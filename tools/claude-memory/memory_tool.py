#!/usr/bin/env python3
"""
claude-memory: Shared semantic search memory for Claude Code sessions and agents.

A single-file CLI tool that gives Claude Code persistent, searchable memory
across interactive sessions and scheduled tasks. Uses SQLite FTS5 for instant
keyword search and optionally calls Claude Haiku for semantic re-ranking.

Zero dependencies beyond Python 3.8+ stdlib. The `anthropic` SDK is only
needed for --semantic search and the `reflect` command.

Usage:
    python3 memory_tool.py search "query" [--semantic] [--type TYPE] [--project PROJECT] [--limit N]
    python3 memory_tool.py read <id>
    python3 memory_tool.py add --id ID --name NAME --type TYPE --project PROJECT --content CONTENT
    python3 memory_tool.py update <id> [--name NAME] [--content CONTENT] [--description DESC] [--tags TAGS]
    python3 memory_tool.py delete <id> [--archive]
    python3 memory_tool.py list [--type TYPE] [--project PROJECT] [--recent DAYS] [--stale DAYS]
    python3 memory_tool.py context --project PROJECT [--actor ACTOR]
    python3 memory_tool.py log --actor ACTOR --action ACTION [--details JSON]
    python3 memory_tool.py reflect [--model MODEL]
    python3 memory_tool.py sync [--source DIR]
    python3 memory_tool.py stats

See README.md for full documentation.
"""

import argparse
import json
import os
import re
import sqlite3
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

# ── Configuration ─────────────────────────────────────────────────────
# Override with CLAUDE_MEMORY_DIR environment variable.
BASE_DIR = Path(os.environ.get("CLAUDE_MEMORY_DIR", Path.home() / ".claude" / "shared-memory"))
DB_PATH = BASE_DIR / "memory.db"
MEMORIES_DIR = BASE_DIR / "memories"
REFLECTIONS_DIR = BASE_DIR / "reflections"

# Default sync source for `sync` command. Override with --source.
DEFAULT_SYNC_SOURCE = Path.home() / ".claude" / "memory"

# Customize these for your setup. Projects are arbitrary labels you define.
VALID_TYPES = ["feedback", "project", "reference", "learning", "session", "user", "archived"]

# Load projects from config file if it exists, otherwise use defaults.
PROJECTS_FILE = BASE_DIR / "projects.json"


def load_projects():
    """Load valid project names from config file or return defaults."""
    if PROJECTS_FILE.exists():
        try:
            return json.loads(PROJECTS_FILE.read_text())
        except (json.JSONDecodeError, IOError):
            pass
    return None  # No restriction — accept any project name


VALID_PROJECTS = load_projects()

# Model configuration
DEFAULT_RERANK_MODEL = "claude-haiku-4-5-20251001"
DEFAULT_REFLECT_MODEL = "claude-opus-4-6"


# ── Utilities ─────────────────────────────────────────────────────────

def ensure_api_key():
    """Ensure ANTHROPIC_API_KEY is in environment, sourcing from shell profile if needed."""
    if os.environ.get("ANTHROPIC_API_KEY"):
        return
    # Try sourcing from common shell profiles
    for profile in ["~/.zshrc", "~/.bashrc", "~/.bash_profile", "~/.profile"]:
        try:
            result = subprocess.run(
                ["sh", "-c", f"source {profile} 2>/dev/null && echo $ANTHROPIC_API_KEY"],
                capture_output=True, text=True, timeout=5
            )
            key = result.stdout.strip()
            if key and key.startswith("sk-ant-"):
                os.environ["ANTHROPIC_API_KEY"] = key
                return
        except Exception:
            continue


def get_db():
    """Get database connection with WAL mode for safe concurrent access."""
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(str(DB_PATH), timeout=10)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA foreign_keys=ON")
    return db


def init_db():
    """Initialize database schema with FTS5 full-text search."""
    db = get_db()
    db.executescript("""
        CREATE TABLE IF NOT EXISTS memories (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT DEFAULT '',
            type TEXT NOT NULL,
            source TEXT DEFAULT 'manual',
            content TEXT NOT NULL,
            project TEXT DEFAULT 'default',
            tags TEXT DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            accessed_at TEXT NOT NULL,
            access_count INTEGER DEFAULT 0
        );

        CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts USING fts5(
            id, name, description, content, tags,
            content=memories,
            content_rowid=rowid
        );

        -- Triggers to keep FTS index in sync with memories table
        CREATE TRIGGER IF NOT EXISTS memories_ai AFTER INSERT ON memories BEGIN
            INSERT INTO memories_fts(rowid, id, name, description, content, tags)
            VALUES (new.rowid, new.id, new.name, new.description, new.content, new.tags);
        END;

        CREATE TRIGGER IF NOT EXISTS memories_ad AFTER DELETE ON memories BEGIN
            INSERT INTO memories_fts(memories_fts, rowid, id, name, description, content, tags)
            VALUES ('delete', old.rowid, old.id, old.name, old.description, old.content, old.tags);
        END;

        CREATE TRIGGER IF NOT EXISTS memories_au AFTER UPDATE ON memories BEGIN
            INSERT INTO memories_fts(memories_fts, rowid, id, name, description, content, tags)
            VALUES ('delete', old.rowid, old.id, old.name, old.description, old.content, old.tags);
            INSERT INTO memories_fts(rowid, id, name, description, content, tags)
            VALUES (new.rowid, new.id, new.name, new.description, new.content, new.tags);
        END;

        CREATE TABLE IF NOT EXISTS activity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            actor TEXT NOT NULL,
            action TEXT NOT NULL,
            memory_id TEXT DEFAULT '',
            query TEXT DEFAULT '',
            details TEXT DEFAULT '{}'
        );

        CREATE TABLE IF NOT EXISTS reflections (
            date TEXT PRIMARY KEY,
            summary TEXT NOT NULL,
            memories_created TEXT DEFAULT '[]',
            memories_archived TEXT DEFAULT '[]',
            metrics TEXT DEFAULT '{}'
        );

        CREATE INDEX IF NOT EXISTS idx_memories_type ON memories(type);
        CREATE INDEX IF NOT EXISTS idx_memories_project ON memories(project);
        CREATE INDEX IF NOT EXISTS idx_memories_updated ON memories(updated_at);
        CREATE INDEX IF NOT EXISTS idx_activity_timestamp ON activity_log(timestamp);
        CREATE INDEX IF NOT EXISTS idx_activity_actor ON activity_log(actor);
    """)
    db.commit()
    db.close()


def now_iso():
    return datetime.now().isoformat()


def write_memory_file(memory_id, name, description, mem_type, content, project, tags="", source="manual"):
    """Write a markdown mirror file for a memory (human-readable backup)."""
    type_dir = MEMORIES_DIR / mem_type
    type_dir.mkdir(parents=True, exist_ok=True)
    filepath = type_dir / f"{memory_id}.md"
    frontmatter = f"""---
name: {name}
description: {description}
type: {mem_type}
project: {project}
tags: {tags}
source: {source}
---

{content}
"""
    filepath.write_text(frontmatter)
    return filepath


def parse_frontmatter(text):
    """Parse YAML-ish frontmatter from a markdown file."""
    result = {}
    if not text.startswith("---"):
        return result, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return result, text
    for line in parts[1].strip().split("\n"):
        if ":" in line:
            key, val = line.split(":", 1)
            result[key.strip()] = val.strip()
    body = parts[2].strip()
    return result, body


# ── Commands ──────────────────────────────────────────────────────────

def cmd_search(args):
    """Search memories using FTS5 with BM25 ranking."""
    db = get_db()
    query = args.query

    # Build FTS5 query — escape special chars, add prefix matching
    fts_query = re.sub(r'[^\w\s]', '', query)
    terms = fts_query.split()
    fts_expr = " OR ".join(f'"{t}"*' for t in terms if t)

    if not fts_expr:
        print("Empty query")
        return

    sql = """
        SELECT m.*, bm25(memories_fts) as rank
        FROM memories_fts fts
        JOIN memories m ON m.id = fts.id
        WHERE memories_fts MATCH ?
    """
    params = [fts_expr]

    if args.type:
        sql += " AND m.type = ?"
        params.append(args.type)
    if args.project:
        sql += " AND m.project = ?"
        params.append(args.project)

    sql += " AND m.type != 'archived'"
    sql += " ORDER BY rank"
    sql += f" LIMIT {args.limit}"

    rows = db.execute(sql, params).fetchall()

    # Log the search
    db.execute(
        "INSERT INTO activity_log (timestamp, actor, action, query, details) VALUES (?, ?, 'search', ?, ?)",
        (now_iso(), args.actor or "interactive", query, json.dumps({"results": len(rows)}))
    )
    db.commit()

    if not rows:
        print(f"No results for: {query}")
        return

    # Optional semantic re-ranking with Claude
    if args.semantic and len(rows) > 1:
        rows = semantic_rerank(query, rows)

    print(f"## Search Results ({len(rows)} matches for \"{query}\")\n")
    for i, row in enumerate(rows, 1):
        print(f"### {i}. [{row['type']}:{row['project']}] {row['name']}")
        print(f"   ID: {row['id']}")
        print(f"   {row['description']}")
        preview = row['content'][:200].replace('\n', ' ')
        if len(row['content']) > 200:
            preview += "..."
        print(f"   > {preview}")
        print(f"   Updated: {row['updated_at'][:10]} | Accessed: {row['access_count']}x")
        print()

    db.close()


def semantic_rerank(query, rows):
    """Use Claude to re-rank search results by semantic relevance."""
    try:
        ensure_api_key()
        import anthropic
        client = anthropic.Anthropic()

        candidates = []
        for i, row in enumerate(rows):
            preview = row['content'][:300]
            candidates.append(f"[{i}] {row['name']}: {row['description']}\n{preview}")

        prompt = f"""Given the search query: "{query}"

Re-rank these memory entries by semantic relevance. Return ONLY a JSON array of indices in order of relevance, e.g. [2, 0, 4, 1, 3].

{chr(10).join(candidates)}"""

        resp = client.messages.create(
            model=DEFAULT_RERANK_MODEL,
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )
        text = resp.content[0].text.strip()
        match = re.search(r'\[[\d,\s]+\]', text)
        if match:
            indices = json.loads(match.group())
            return [rows[i] for i in indices if i < len(rows)]
    except Exception as e:
        print(f"(Semantic re-ranking unavailable: {e} — using keyword ranking)", file=sys.stderr)

    return rows


def cmd_read(args):
    """Read full content of a specific memory."""
    db = get_db()
    row = db.execute("SELECT * FROM memories WHERE id = ?", (args.id,)).fetchone()
    if not row:
        print(f"Memory not found: {args.id}")
        sys.exit(1)

    db.execute(
        "UPDATE memories SET accessed_at = ?, access_count = access_count + 1 WHERE id = ?",
        (now_iso(), args.id)
    )
    db.execute(
        "INSERT INTO activity_log (timestamp, actor, action, memory_id) VALUES (?, ?, 'read', ?)",
        (now_iso(), args.actor or "interactive", args.id)
    )
    db.commit()

    print(f"# {row['name']}")
    print(f"Type: {row['type']} | Project: {row['project']} | Tags: {row['tags']}")
    print(f"Source: {row['source']} | Updated: {row['updated_at'][:10]} | Accessed: {row['access_count']}x")
    print(f"---")
    print(row['content'])
    db.close()


def cmd_add(args):
    """Add a new memory."""
    db = get_db()

    existing = db.execute("SELECT id FROM memories WHERE id = ?", (args.id,)).fetchone()
    if existing:
        print(f"Memory '{args.id}' already exists. Use 'update' instead.")
        sys.exit(1)

    ts = now_iso()
    description = args.description or args.name
    tags = args.tags or ""
    source = args.source or "manual"

    db.execute(
        """INSERT INTO memories (id, name, description, type, source, content, project, tags,
           created_at, updated_at, accessed_at, access_count)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)""",
        (args.id, args.name, description, args.type, source, args.content,
         args.project, tags, ts, ts, ts)
    )

    db.execute(
        "INSERT INTO activity_log (timestamp, actor, action, memory_id, details) VALUES (?, ?, 'add', ?, ?)",
        (ts, args.actor or "interactive", args.id, json.dumps({"type": args.type, "project": args.project}))
    )
    db.commit()

    write_memory_file(args.id, args.name, description, args.type, args.content, args.project, tags, source)

    print(f"Added memory: {args.id} [{args.type}:{args.project}]")
    db.close()


def cmd_update(args):
    """Update an existing memory."""
    db = get_db()
    row = db.execute("SELECT * FROM memories WHERE id = ?", (args.id,)).fetchone()
    if not row:
        print(f"Memory not found: {args.id}")
        sys.exit(1)

    updates = []
    params = []

    if args.name:
        updates.append("name = ?"); params.append(args.name)
    if args.content:
        updates.append("content = ?"); params.append(args.content)
    if args.description:
        updates.append("description = ?"); params.append(args.description)
    if args.tags:
        updates.append("tags = ?"); params.append(args.tags)
    if args.set_type:
        updates.append("type = ?"); params.append(args.set_type)

    if not updates:
        print("Nothing to update")
        return

    updates.append("updated_at = ?")
    params.append(now_iso())
    params.append(args.id)

    db.execute(f"UPDATE memories SET {', '.join(updates)} WHERE id = ?", params)
    db.execute(
        "INSERT INTO activity_log (timestamp, actor, action, memory_id) VALUES (?, ?, 'update', ?)",
        (now_iso(), args.actor or "interactive", args.id)
    )
    db.commit()

    updated = db.execute("SELECT * FROM memories WHERE id = ?", (args.id,)).fetchone()
    write_memory_file(
        updated['id'], updated['name'], updated['description'],
        updated['type'], updated['content'], updated['project'],
        updated['tags'], updated['source']
    )

    print(f"Updated memory: {args.id}")
    db.close()


def cmd_delete(args):
    """Delete a memory (or archive it with --archive)."""
    db = get_db()
    if args.archive:
        db.execute("UPDATE memories SET type = 'archived', updated_at = ? WHERE id = ?", (now_iso(), args.id))
        print(f"Archived memory: {args.id}")
    else:
        db.execute("DELETE FROM memories WHERE id = ?", (args.id,))
        for type_dir in MEMORIES_DIR.iterdir():
            if type_dir.is_dir():
                f = type_dir / f"{args.id}.md"
                if f.exists():
                    f.unlink()
        print(f"Deleted memory: {args.id}")

    db.execute(
        "INSERT INTO activity_log (timestamp, actor, action, memory_id) VALUES (?, ?, ?, ?)",
        (now_iso(), args.actor or "interactive", "archive" if args.archive else "delete", args.id)
    )
    db.commit()
    db.close()


def cmd_list(args):
    """List memories with filters."""
    db = get_db()

    sql = "SELECT id, name, type, project, tags, updated_at, access_count FROM memories WHERE type != 'archived'"
    params = []

    if args.type:
        sql += " AND type = ?"; params.append(args.type)
    if args.project:
        sql += " AND project = ?"; params.append(args.project)
    if args.recent:
        cutoff = (datetime.now() - timedelta(days=args.recent)).isoformat()
        sql += " AND updated_at > ?"; params.append(cutoff)
    if args.stale:
        cutoff = (datetime.now() - timedelta(days=args.stale)).isoformat()
        sql += " AND accessed_at < ?"; params.append(cutoff)

    sql += " ORDER BY updated_at DESC"
    rows = db.execute(sql, params).fetchall()

    if not rows:
        print("No memories found matching filters.")
        return

    print(f"## Memories ({len(rows)} total)\n")
    for row in rows:
        tags = f" [{row['tags']}]" if row['tags'] else ""
        print(f"  {row['id']:40s} {row['type']:10s} {row['project']:12s} {row['updated_at'][:10]} {row['access_count']:3d}x{tags}")

    db.close()


def cmd_context(args):
    """Generate focused context block for a session or task."""
    db = get_db()
    project = args.project
    actor = args.actor or "interactive"
    sections = []

    # 1. All feedback/rules for this project (always include)
    feedbacks = db.execute(
        "SELECT id, name, content FROM memories WHERE type = 'feedback' AND (project = ? OR project = 'default') AND type != 'archived' ORDER BY access_count DESC",
        (project,)
    ).fetchall()
    if feedbacks:
        sections.append("## Rules & Feedback")
        for f in feedbacks:
            compact = f['content'][:150].replace('\n', ' ').strip()
            if len(f['content']) > 150:
                compact += "..."
            sections.append(f"- **{f['name']}**: {compact}")

    # 2. Recent project context (last 14 days)
    recent = db.execute(
        "SELECT id, name, content FROM memories WHERE type = 'project' AND project = ? AND type != 'archived' AND updated_at > ? ORDER BY updated_at DESC LIMIT 10",
        (project, (datetime.now() - timedelta(days=14)).isoformat())
    ).fetchall()
    if recent:
        sections.append("\n## Recent Project Context")
        for r in recent:
            compact = r['content'][:200].replace('\n', ' ').strip()
            if len(r['content']) > 200:
                compact += "..."
            sections.append(f"- **{r['name']}**: {compact}")

    # 3. Most-accessed references (top 5)
    refs = db.execute(
        "SELECT id, name, content FROM memories WHERE type = 'reference' AND project = ? AND type != 'archived' ORDER BY access_count DESC LIMIT 5",
        (project,)
    ).fetchall()
    if refs:
        sections.append("\n## Key References")
        for r in refs:
            compact = r['content'][:200].replace('\n', ' ').strip()
            if len(r['content']) > 200:
                compact += "..."
            sections.append(f"- **{r['name']}**: {compact}")

    # 4. Recent learnings (last 7 days)
    learnings = db.execute(
        "SELECT id, name, content FROM memories WHERE type = 'learning' AND (project = ? OR project = 'default') AND type != 'archived' AND created_at > ? ORDER BY created_at DESC LIMIT 5",
        (project, (datetime.now() - timedelta(days=7)).isoformat())
    ).fetchall()
    if learnings:
        sections.append("\n## Recent Learnings")
        for l in learnings:
            compact = l['content'][:150].replace('\n', ' ').strip()
            sections.append(f"- **{l['name']}**: {compact}")

    # 5. Latest reflection
    reflection = db.execute(
        "SELECT date, summary FROM reflections ORDER BY date DESC LIMIT 1"
    ).fetchone()
    if reflection:
        sections.append(f"\n## Latest Reflection ({reflection['date']})")
        sections.append(reflection['summary'][:300])

    db.execute(
        "INSERT INTO activity_log (timestamp, actor, action, details) VALUES (?, ?, 'context', ?)",
        (now_iso(), actor, json.dumps({"project": project}))
    )
    db.commit()

    output = "\n".join(sections)
    if not output.strip():
        output = f"No memories found for project: {project}"
    print(output)
    db.close()


def cmd_log(args):
    """Log task activity."""
    db = get_db()
    db.execute(
        "INSERT INTO activity_log (timestamp, actor, action, memory_id, query, details) VALUES (?, ?, ?, ?, ?, ?)",
        (now_iso(), args.actor, args.action, args.memory_id or "", args.log_query or "", args.details or "{}")
    )
    db.commit()
    print(f"Logged: {args.actor} -> {args.action}")
    db.close()


def cmd_reflect(args):
    """Run daily reflection cycle using the Claude API."""
    db = get_db()
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).isoformat()

    activities = db.execute("SELECT * FROM activity_log WHERE timestamp > ? ORDER BY timestamp", (yesterday,)).fetchall()
    recent_memories = db.execute("SELECT * FROM memories WHERE updated_at > ? AND type != 'archived' ORDER BY updated_at DESC", (yesterday,)).fetchall()
    hot = db.execute("SELECT id, name, type, project, access_count FROM memories WHERE type != 'archived' ORDER BY access_count DESC LIMIT 10").fetchall()
    cold_cutoff = (datetime.now() - timedelta(days=30)).isoformat()
    cold = db.execute("SELECT id, name, type, project, access_count, accessed_at FROM memories WHERE type != 'archived' AND accessed_at < ? AND access_count < 3", (cold_cutoff,)).fetchall()
    all_memories = db.execute("SELECT id, name, type, project, description FROM memories WHERE type != 'archived' ORDER BY project, type").fetchall()

    actors = {}
    for a in activities:
        actors.setdefault(a['actor'], []).append(f"{a['action']}: {a['memory_id'] or a['query'] or ''}")

    activity_summary = [f"**{actor}**: {', '.join(actions[:10])}" for actor, actions in actors.items()]
    recent_list = [f"- [{m['type']}:{m['project']}] {m['name']}: {m['content'][:100]}" for m in recent_memories]
    hot_list = [f"- {h['id']} ({h['access_count']}x): {h['name']}" for h in hot]
    cold_list = [f"- {c['id']} (last: {c['accessed_at'][:10]}, {c['access_count']}x): {c['name']}" for c in cold]
    all_list = [f"- [{m['type']}:{m['project']}] {m['id']}: {m['description']}" for m in all_memories]

    prompt = f"""You are reflecting on today's activity across all sessions and tasks using a shared memory system.

## Today's Activity ({len(activities)} actions by {len(actors)} actors)
{chr(10).join(activity_summary) if activity_summary else "No activity logged today."}

## Memories Created/Updated Today
{chr(10).join(recent_list) if recent_list else "None."}

## Hot Memories (most accessed)
{chr(10).join(hot_list)}

## Cold Memories (30+ days untouched, <3 accesses)
{chr(10).join(cold_list) if cold_list else "None."}

## All Active Memories ({len(all_memories)} total)
{chr(10).join(all_list)}

## Tasks:
1. Write a 3-5 sentence summary of what was learned today
2. Identify any contradictions between memories
3. Suggest memories to MERGE (similar content)
4. Suggest memories to ARCHIVE (stale, irrelevant)
5. Suggest NEW learning memories (patterns you observe)
6. Note gaps — what should be remembered but isn't?

Respond in JSON:
{{
  "summary": "...",
  "contradictions": ["..."],
  "merge_suggestions": [{{"ids": ["id1", "id2"], "reason": "..."}}],
  "archive_suggestions": [{{"id": "...", "reason": "..."}}],
  "new_memories": [{{"id": "...", "name": "...", "type": "learning", "project": "...", "content": "..."}}],
  "gaps": ["..."]
}}"""

    try:
        ensure_api_key()
        import anthropic
        client = anthropic.Anthropic()
        model = getattr(args, 'model', None) or DEFAULT_REFLECT_MODEL
        resp = client.messages.create(model=model, max_tokens=2000, messages=[{"role": "user", "content": prompt}])
        text = resp.content[0].text.strip()

        match = re.search(r'\{[\s\S]+\}', text)
        if not match:
            print("Reflection failed: could not parse response")
            print(text)
            return

        result = json.loads(match.group())
        created, archived = [], []

        for mem in result.get("new_memories", []):
            mem_id = mem.get("id", f"learning-{today}-{len(created)}")
            try:
                ts = now_iso()
                db.execute(
                    """INSERT INTO memories (id, name, description, type, source, content, project, tags,
                       created_at, updated_at, accessed_at, access_count)
                       VALUES (?, ?, ?, ?, 'reflection', ?, ?, '', ?, ?, ?, 0)""",
                    (mem_id, mem["name"], mem.get("content", "")[:100], mem.get("type", "learning"),
                     mem["content"], mem.get("project", "default"), ts, ts, ts)
                )
                write_memory_file(mem_id, mem["name"], mem.get("content", "")[:100],
                                  mem.get("type", "learning"), mem["content"], mem.get("project", "default"),
                                  source="reflection")
                created.append(mem_id)
            except sqlite3.IntegrityError:
                pass

        for arch in result.get("archive_suggestions", []):
            aid = arch["id"]
            if db.execute("SELECT id FROM memories WHERE id = ?", (aid,)).fetchone():
                db.execute("UPDATE memories SET type = 'archived', updated_at = ? WHERE id = ?", (now_iso(), aid))
                archived.append(aid)

        metrics = {"total_memories": len(all_memories), "activities_today": len(activities),
                   "actors_today": len(actors), "hot_count": len(hot), "cold_count": len(cold)}
        db.execute(
            "INSERT OR REPLACE INTO reflections (date, summary, memories_created, memories_archived, metrics) VALUES (?, ?, ?, ?, ?)",
            (today, result["summary"], json.dumps(created), json.dumps(archived), json.dumps(metrics))
        )
        db.commit()

        reflection_path = REFLECTIONS_DIR / f"{today}.md"
        REFLECTIONS_DIR.mkdir(parents=True, exist_ok=True)
        reflection_md = f"""# Daily Reflection — {today}

## Summary
{result['summary']}

## Contradictions
{chr(10).join('- ' + c for c in result.get('contradictions', [])) or 'None found.'}

## Merge Suggestions
{chr(10).join('- Merge ' + str(m['ids']) + ': ' + m['reason'] for m in result.get('merge_suggestions', [])) or 'None.'}

## Archived
{chr(10).join('- ' + a['id'] + ': ' + a['reason'] for a in result.get('archive_suggestions', [])) or 'None.'}

## New Learnings Created
{chr(10).join('- ' + m.get('id', '?') + ': ' + m['name'] for m in result.get('new_memories', [])) or 'None.'}

## Gaps
{chr(10).join('- ' + g for g in result.get('gaps', [])) or 'None identified.'}

## Metrics
- Total memories: {metrics['total_memories']}
- Activities today: {metrics['activities_today']}
- Actors today: {metrics['actors_today']}
- Created: {len(created)} | Archived: {len(archived)}
"""
        reflection_path.write_text(reflection_md)

        print(f"## Reflection Complete — {today}")
        print(f"\n{result['summary']}")
        print(f"\nCreated: {len(created)} memories | Archived: {len(archived)} memories")
        if result.get("gaps"):
            print(f"\nGaps identified:")
            for g in result["gaps"]:
                print(f"  - {g}")
        print(f"\nFull reflection: {reflection_path}")

    except ImportError:
        print("Error: anthropic SDK required for reflect. Run: pip3 install anthropic")
        sys.exit(1)
    except Exception as e:
        print(f"Reflection error: {e}")
        sys.exit(1)
    finally:
        db.close()


def cmd_sync(args):
    """Migrate existing markdown memory files into the database."""
    source_dir = Path(args.source) if args.source else DEFAULT_SYNC_SOURCE

    # Also check Claude Code's per-project memory directories
    if not source_dir.exists():
        # Try common Claude Code memory locations
        candidates = [
            Path.home() / ".claude" / "memory",
            Path.home() / ".claude" / "projects",
        ]
        for c in candidates:
            if c.exists():
                source_dir = c
                break
        else:
            print(f"No memory directory found. Specify --source DIR.")
            sys.exit(1)

    db = get_db()
    migrated = 0
    skipped = 0

    # Recursively find all .md files
    for f in sorted(source_dir.rglob("*.md")):
        if f.name == "MEMORY.md":
            continue

        text = f.read_text()
        meta, body = parse_frontmatter(text)

        if not body.strip():
            skipped += 1
            continue

        mem_id = f.stem.replace("_", "-")

        # Check for duplicate
        if db.execute("SELECT id FROM memories WHERE id = ?", (mem_id,)).fetchone():
            skipped += 1
            continue

        mem_type = meta.get("type", "project")
        if mem_type not in VALID_TYPES:
            mem_type = "project"

        name = meta.get("name", f.stem.replace("_", " ").replace("-", " ").title())
        description = meta.get("description", name)
        project = meta.get("project", "default")

        ts = now_iso()
        db.execute(
            """INSERT INTO memories (id, name, description, type, source, content, project, tags,
               created_at, updated_at, accessed_at, access_count)
               VALUES (?, ?, ?, ?, 'migrated', ?, ?, '', ?, ?, ?, 0)""",
            (mem_id, name, description, mem_type, body, project, ts, ts, ts)
        )
        write_memory_file(mem_id, name, description, mem_type, body, project, source="migrated")
        migrated += 1

    db.commit()
    print(f"Sync complete: {migrated} migrated, {skipped} skipped (from {source_dir})")
    db.close()


def cmd_stats(args):
    """Show memory system statistics."""
    db = get_db()

    total = db.execute("SELECT COUNT(*) as c FROM memories WHERE type != 'archived'").fetchone()['c']
    archived = db.execute("SELECT COUNT(*) as c FROM memories WHERE type = 'archived'").fetchone()['c']

    print(f"## Memory System Stats\n")
    print(f"Total active memories: {total}")
    print(f"Archived: {archived}")

    print(f"\n### By Type")
    for row in db.execute("SELECT type, COUNT(*) as c FROM memories WHERE type != 'archived' GROUP BY type ORDER BY c DESC"):
        print(f"  {row['type']:15s} {row['c']}")

    print(f"\n### By Project")
    for row in db.execute("SELECT project, COUNT(*) as c FROM memories WHERE type != 'archived' GROUP BY project ORDER BY c DESC"):
        print(f"  {row['project']:15s} {row['c']}")

    print(f"\n### Most Accessed")
    for row in db.execute("SELECT id, name, access_count FROM memories WHERE type != 'archived' ORDER BY access_count DESC LIMIT 5"):
        print(f"  {row['access_count']:3d}x  {row['id']}: {row['name']}")

    today = datetime.now().strftime("%Y-%m-%d")
    today_actions = db.execute("SELECT COUNT(*) as c FROM activity_log WHERE timestamp LIKE ?", (f"{today}%",)).fetchone()['c']
    total_actions = db.execute("SELECT COUNT(*) as c FROM activity_log").fetchone()['c']
    print(f"\n### Activity")
    print(f"  Today: {today_actions} actions")
    print(f"  Total: {total_actions} actions")

    reflection = db.execute("SELECT date, summary FROM reflections ORDER BY date DESC LIMIT 1").fetchone()
    if reflection:
        print(f"\n### Latest Reflection ({reflection['date']})")
        print(f"  {reflection['summary'][:200]}")

    cold_cutoff = (datetime.now() - timedelta(days=14)).isoformat()
    stale = db.execute(
        "SELECT COUNT(*) as c FROM memories WHERE type != 'archived' AND accessed_at < ? AND access_count < 2",
        (cold_cutoff,)
    ).fetchone()['c']
    if stale:
        print(f"\n### Health")
        print(f"  {stale} stale memories (14+ days untouched, <2 accesses)")

    db.close()


# ── Main ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="claude-memory: Shared semantic search memory for Claude Code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="See https://github.com/philmora/claude-memory for full documentation."
    )
    parser.add_argument("--actor", default="interactive", help="Actor identifier (task ID or 'interactive')")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # search
    p = subparsers.add_parser("search", help="Search memories with FTS5 + optional semantic re-ranking")
    p.add_argument("query")
    p.add_argument("--semantic", action="store_true", help="Use Claude Haiku for semantic re-ranking")
    p.add_argument("--type", choices=VALID_TYPES)
    p.add_argument("--project")
    p.add_argument("--limit", type=int, default=10)

    # read
    p = subparsers.add_parser("read", help="Read full content of a memory")
    p.add_argument("id")

    # add
    p = subparsers.add_parser("add", help="Add a new memory")
    p.add_argument("--id", required=True)
    p.add_argument("--name", required=True)
    p.add_argument("--type", required=True, choices=VALID_TYPES)
    p.add_argument("--project", required=True)
    p.add_argument("--content", required=True)
    p.add_argument("--description")
    p.add_argument("--tags")
    p.add_argument("--source")

    # update
    p = subparsers.add_parser("update", help="Update an existing memory")
    p.add_argument("id")
    p.add_argument("--name")
    p.add_argument("--content")
    p.add_argument("--description")
    p.add_argument("--tags")
    p.add_argument("--set-type", choices=VALID_TYPES)

    # delete
    p = subparsers.add_parser("delete", help="Delete or archive a memory")
    p.add_argument("id")
    p.add_argument("--archive", action="store_true", help="Soft-delete: mark as archived instead of removing")

    # list
    p = subparsers.add_parser("list", help="List memories with filters")
    p.add_argument("--type", choices=VALID_TYPES)
    p.add_argument("--project")
    p.add_argument("--recent", type=int, help="Updated in last N days")
    p.add_argument("--stale", type=int, help="Not accessed in N days")

    # context
    p = subparsers.add_parser("context", help="Generate focused context block for a session")
    p.add_argument("--project", required=True)

    # log
    p = subparsers.add_parser("log", help="Log task activity")
    p.add_argument("--actor", required=True)
    p.add_argument("--action", required=True)
    p.add_argument("--memory-id")
    p.add_argument("--log-query")
    p.add_argument("--details")

    # reflect
    p = subparsers.add_parser("reflect", help="Run daily AI reflection cycle")
    p.add_argument("--model", default=DEFAULT_REFLECT_MODEL, help="Model for reflection")

    # sync
    p = subparsers.add_parser("sync", help="Import existing markdown memory files")
    p.add_argument("--source", help="Source directory containing .md files")

    # stats
    subparsers.add_parser("stats", help="Show memory system dashboard")

    args = parser.parse_args()

    if not DB_PATH.exists():
        init_db()

    cmd_map = {
        "search": cmd_search, "read": cmd_read, "add": cmd_add,
        "update": cmd_update, "delete": cmd_delete, "list": cmd_list,
        "context": cmd_context, "log": cmd_log, "reflect": cmd_reflect,
        "sync": cmd_sync, "stats": cmd_stats,
    }

    cmd_map[args.command](args)


if __name__ == "__main__":
    main()
