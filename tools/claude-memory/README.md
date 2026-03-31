# claude-memory

Persistent, searchable memory for [Claude Code](https://claude.ai/claude-code) that works across interactive sessions and scheduled tasks.

A single Python file. Zero dependencies. SQLite full-text search with optional Claude-powered semantic re-ranking. Built to solve the problem of Claude Code sessions forgetting everything between conversations.

## The Problem

Claude Code has no memory between sessions. Every new conversation starts from zero. If you're running multiple scheduled tasks (social media automation, monitoring, content pipelines), each one operates in isolation. Learnings from one session never reach another.

The built-in `MEMORY.md` file helps, but it's a flat text file that grows until it hits its line limit. There's no search, no structure, no way for an automated task to write back what it learned.

## What This Does

`memory_tool.py` gives Claude Code a shared brain:

- **Search** across all memories instantly using SQLite FTS5 (BM25 ranking)
- **Semantic search** optionally re-ranks results using Claude Haiku (~$0.001/query)
- **Structured storage** with types (feedback, project, reference, learning) and projects
- **Activity logging** tracks every search, read, and write across all sessions
- **Context generation** produces focused, relevant context instead of dumping everything
- **Daily reflection** uses Claude to synthesize patterns, archive stale memories, and create new insights
- **Markdown mirrors** every memory also exists as a human-readable `.md` file
- **Concurrent-safe** SQLite WAL mode handles multiple tasks hitting the DB simultaneously

## Quick Start

### 1. Install

```bash
# Copy the single file to your Claude Code shared memory directory
mkdir -p ~/.claude/shared-memory
curl -o ~/.claude/shared-memory/memory_tool.py \
  https://raw.githubusercontent.com/philmora/claude-memory/main/memory_tool.py
```

Or clone the repo:

```bash
git clone https://github.com/philmora/claude-memory.git
cp claude-memory/memory_tool.py ~/.claude/shared-memory/
```

### 2. Initialize

The database auto-creates on first use. Just run any command:

```bash
python3 ~/.claude/shared-memory/memory_tool.py stats
```

### 3. Add Your First Memory

```bash
python3 ~/.claude/shared-memory/memory_tool.py add \
  --id "feedback-always-test" \
  --name "Always Run Tests Before Committing" \
  --type feedback \
  --project my-app \
  --content "Never commit without running the test suite. We had a prod incident on March 15 when tests were skipped."
```

### 4. Search It

```bash
python3 ~/.claude/shared-memory/memory_tool.py search "testing before commit"
```

### 5. Tell Claude Code About It

Add this to your project's `CLAUDE.md` or `~/.claude/CLAUDE.md`:

```markdown
## Memory System
Before starting work, load relevant context:
  python3 ~/.claude/shared-memory/memory_tool.py context --project <project-name>

To search for specific knowledge:
  python3 ~/.claude/shared-memory/memory_tool.py search "<query>"

When you learn something that should persist across sessions:
  python3 ~/.claude/shared-memory/memory_tool.py add --id "<slug>" --name "<title>" --type <type> --project <project> --content "<content>"
```

## Commands

### `search` — Find memories

```bash
# Keyword search (instant, free)
memory_tool.py search "deployment process"

# Filter by type or project
memory_tool.py search "API keys" --type reference --project backend

# Semantic search (uses Claude Haiku for re-ranking, ~$0.001)
memory_tool.py search "how do we handle auth" --semantic

# Limit results
memory_tool.py search "database" --limit 5
```

### `read` — Full memory content

```bash
memory_tool.py read feedback-always-test
```

Updates access stats (used by `context` to prioritize frequently-accessed memories).

### `add` — Store a new memory

```bash
memory_tool.py add \
  --id "reference-prod-db" \
  --name "Production Database Credentials Location" \
  --type reference \
  --project backend \
  --description "Where to find prod DB connection strings" \
  --content "Production DB credentials are in AWS Secrets Manager under /prod/db/main. Never hardcode. Use the get-secret.sh helper script." \
  --tags "database,aws,secrets" \
  --source "manual"
```

### `update` — Modify existing memory

```bash
# Update content
memory_tool.py update reference-prod-db --content "Moved to Vault. Path: secret/data/prod/db"

# Change type
memory_tool.py update old-memory --set-type archived
```

### `delete` — Remove or archive

```bash
# Soft delete (recommended — keeps history)
memory_tool.py delete old-memory --archive

# Hard delete
memory_tool.py delete old-memory
```

### `list` — Browse with filters

```bash
# All memories
memory_tool.py list

# By type
memory_tool.py list --type feedback

# By project
memory_tool.py list --project backend

# Recently updated
memory_tool.py list --recent 7

# Stale (not accessed in N days)
memory_tool.py list --stale 30
```

### `context` — Generate focused context

This is the key command for Claude Code integration. Instead of loading a 200-line MEMORY.md, it generates a focused block with only what's relevant:

```bash
memory_tool.py context --project backend
```

Returns:
- All **feedback** rules for the project (these are always included — they're your guard rails)
- **Recent project context** (updated in last 14 days)
- **Top references** (most frequently accessed)
- **Recent learnings** (last 7 days)
- **Latest reflection summary**

Typical output: ~50 focused lines vs hundreds of lines of everything.

### `log` — Record task activity

```bash
memory_tool.py log \
  --actor "deploy-monitor" \
  --action "complete" \
  --details '{"status": "healthy", "version": "2.4.1"}'
```

### `reflect` — AI-powered daily synthesis

```bash
memory_tool.py reflect
```

Uses Claude (Opus by default) to:
1. Review all activity in the last 24 hours
2. Identify patterns across tasks and sessions
3. Create new "learning" memories for discovered patterns
4. Archive stale memories (30+ days untouched, <3 accesses)
5. Identify contradictions and gaps
6. Write a reflection summary to `reflections/YYYY-MM-DD.md`

Use a different model:
```bash
memory_tool.py reflect --model claude-sonnet-4-6
```

### `sync` — Import existing memories

Migrate from Claude Code's built-in markdown memory files:

```bash
# Auto-detect Claude Code memory directory
memory_tool.py sync

# Specify source directory
memory_tool.py sync --source ~/.claude/projects/my-project/memory/
```

### `stats` — Dashboard

```bash
memory_tool.py stats
```

```
## Memory System Stats

Total active memories: 38
Archived: 3

### By Type
  feedback        17
  reference       11
  project          9
  learning         1

### By Project
  backend         15
  frontend        12
  system           8
  ops              3

### Most Accessed
  12x  feedback-test-before-commit: Always Run Tests
   8x  reference-prod-db: Production Database
   5x  feedback-no-force-push: Never Force Push to Main

### Activity
  Today: 47 actions
  Total: 1,203 actions

### Latest Reflection (2026-03-30)
  Three tasks independently discovered that the staging API returns...
```

## Memory Types

| Type | Purpose | When to Use |
|------|---------|-------------|
| `feedback` | Rules, corrections, lessons | User corrects your approach, or confirms a non-obvious one worked |
| `project` | Status, milestones, active work | Track what's in progress, who's doing what, deadlines |
| `reference` | Stable facts, URLs, IDs, accounts | API endpoints, credentials locations, account details |
| `learning` | Patterns discovered by reflection | Created automatically by `reflect`, or manually for insights |
| `session` | Task outputs and summaries | Scheduled tasks logging what they did |
| `user` | User profile, preferences | Role, expertise level, communication preferences |

## Integration with Scheduled Tasks

Add a memory preamble to each scheduled task's `SKILL.md`:

```markdown
## SHARED MEMORY SYSTEM
Before starting, load context:
`python3 ~/.claude/shared-memory/memory_tool.py context --project my-project --actor my-task-name`

After completing, log activity:
`python3 ~/.claude/shared-memory/memory_tool.py log --actor "my-task-name" --action "complete" --details '<JSON>'`

If you discover something new:
`python3 ~/.claude/shared-memory/memory_tool.py add --id "learning-<slug>" --name "<title>" --type learning --project my-project --source "task:my-task-name" --content "<what was learned>"`
```

## Daily Reflection Scheduled Task

Create a nightly task that runs `reflect`:

```bash
# Using Claude Code's scheduled tasks
python3 ~/.claude/shared-memory/memory_tool.py reflect
```

Or with cron:

```bash
# Run reflection at 11:30 PM daily
30 23 * * * cd ~/.claude/shared-memory && python3 memory_tool.py reflect >> reflect.log 2>&1
```

## Architecture

```
~/.claude/shared-memory/
  memory_tool.py        # The tool (single file, ~600 lines)
  memory.db             # SQLite database (auto-created)
  memories/             # Human-readable markdown mirrors
    feedback/
    project/
    reference/
    learning/
    session/
  reflections/          # Daily reflection summaries
    2026-03-30.md
  projects.json         # (Optional) restrict valid project names
```

### Why SQLite FTS5?

- **Zero dependencies** — FTS5 is built into Python's `sqlite3` module
- **BM25 ranking** — same algorithm used by Elasticsearch, but local
- **WAL mode** — safe concurrent access from multiple scheduled tasks
- **Triggers** — FTS index stays in sync automatically
- **Fast** — searches 1000+ memories in <10ms

### Why Not Vector Embeddings?

For a typical Claude Code memory store (50-500 memories, 100KB-5MB of text), vector search adds massive overhead for marginal benefit:

| Approach | Install Size | Latency | Quality |
|----------|-------------|---------|---------|
| SQLite FTS5 | 0 MB | <10ms | Great for keyword matches |
| FTS5 + Haiku re-rank | 0 MB | ~500ms | Excellent — true semantic understanding |
| ChromaDB | ~200 MB | ~100ms | Good — but 200MB for 100KB of data? |
| sentence-transformers | ~2 GB | ~50ms | Good — but PyTorch for a CLI tool? |

FTS5 handles 90% of queries perfectly. For the remaining 10%, the `--semantic` flag calls Haiku to re-rank the top 20 keyword results — giving you true semantic search without any local ML infrastructure.

## Configuration

### Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `CLAUDE_MEMORY_DIR` | `~/.claude/shared-memory` | Base directory for all memory data |
| `ANTHROPIC_API_KEY` | (from shell profile) | Required for `--semantic` and `reflect` |

### Project Restrictions

By default, any project name is accepted. To restrict to a fixed list, create `projects.json`:

```json
["backend", "frontend", "ops", "personal"]
```

## Cost

| Feature | Model | Cost |
|---------|-------|------|
| Keyword search | None | Free |
| Semantic re-ranking | Haiku | ~$0.001/query |
| Daily reflection | Opus | ~$0.05/day |
| **Monthly total** | | **~$2-3** |

## Requirements

- Python 3.8+ (uses only stdlib + optional `anthropic` SDK)
- SQLite with FTS5 support (included in Python 3.8+)
- `anthropic` SDK (only for `--semantic` search and `reflect`)

```bash
pip3 install anthropic  # Optional — only needed for AI features
```

## How It Was Built

This tool was designed and built in a single Claude Code session to solve a real problem: managing memory across 8+ automated scheduled tasks running a political campaign's social media, content pipeline, and monitoring operations. The tasks needed to share learnings without stepping on each other, and the human operator needed a way to search across everything without reading 200+ lines of flat markdown.

The design prioritized:
- **Zero friction** — single file, no dependencies for core features
- **Claude Code native** — works via `Bash` tool calls, outputs markdown
- **Concurrent safety** — WAL mode for multiple scheduled tasks
- **Human readable** — every memory also exists as a markdown file you can browse

## License

MIT
