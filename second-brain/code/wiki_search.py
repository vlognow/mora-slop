#!/usr/bin/env python3
"""
wiki_search.py — File-level search over a Karpathy-style markdown wiki

Indexes all markdown files in ~/work-brain/, stores metadata + optional
embeddings in SQLite, provides keyword and semantic search.

Design decisions:
  1. File-level indexing, not chunks. Results are whole files. NOT RAG.
  2. SQLite + embedding blobs. No vector DB. sqlite3 ships with Python.
  3. Incremental re-indexing via content hash. Safe to run after every lint.
  4. Embedding provider is swappable. Default: sentence-transformers (local).
     Falls back to keyword-only if no embedding model available.

Usage:
    python3 wiki_search.py index                        # Full index
    python3 wiki_search.py reindex                      # Only changed files
    python3 wiki_search.py search "context engineering"  # Keyword search
    python3 wiki_search.py search "context engineering" --semantic  # Semantic
    python3 wiki_search.py stats                         # Index statistics
    python3 wiki_search.py related concepts/pm-as-builder.md  # Similar files
    python3 wiki_search.py orphans                       # Files with no links
    python3 wiki_search.py broken                        # Broken wikilinks
"""

import argparse
import hashlib
import os
import re
import sqlite3
import struct
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

WIKI_ROOT = Path.home() / "work-brain"
DB_PATH = WIKI_ROOT / ".wiki_search.db"
EXCLUDE_DIRS = {"raw", ".obsidian", ".git", "archive"}

# ============================================================================
# SCHEMA
# ============================================================================

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS wiki_files (
    path TEXT PRIMARY KEY,
    title TEXT,
    summary TEXT,
    content TEXT NOT NULL,
    word_count INTEGER,
    last_modified TIMESTAMP,
    content_hash TEXT,
    embedding BLOB,
    indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_modified ON wiki_files(last_modified DESC);

CREATE TABLE IF NOT EXISTS wiki_links (
    source_file TEXT NOT NULL,
    target_file TEXT NOT NULL,
    link_text TEXT,
    PRIMARY KEY (source_file, target_file)
);

CREATE INDEX IF NOT EXISTS idx_links_source ON wiki_links(source_file);
CREATE INDEX IF NOT EXISTS idx_links_target ON wiki_links(target_file);
"""

# ============================================================================
# EMBEDDINGS — local sentence-transformers (swappable)
# ============================================================================

_model = None

def _load_model():
    """Lazy-load the embedding model. Returns None if unavailable."""
    global _model
    if _model is not None:
        return _model
    try:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")
        return _model
    except ImportError:
        return None


def get_embedding(text: str) -> Optional[bytes]:
    """Generate embedding for text. Returns None if model unavailable."""
    model = _load_model()
    if model is None:
        return None
    try:
        truncated = text[:8000]
        vec = model.encode(truncated, normalize_embeddings=True)
        return struct.pack(f"{len(vec)}f", *vec)
    except Exception as e:
        print(f"WARNING: embedding failed ({e})", file=sys.stderr)
        return None


def unpack_embedding(blob: bytes) -> List[float]:
    if not blob:
        return []
    n = len(blob) // 4
    return list(struct.unpack(f"{n}f", blob))


def cosine_similarity(a: List[float], b: List[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = sum(x * x for x in a) ** 0.5
    mag_b = sum(y * y for y in b) ** 0.5
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


# ============================================================================
# FILE PROCESSING
# ============================================================================

def extract_title(content: str, filename: str) -> str:
    for line in content.split("\n"):
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return Path(filename).stem.replace("-", " ").replace("_", " ").title()


def extract_summary(content: str) -> str:
    """Extract the italic summary line (second non-blank line after title)."""
    lines = content.split("\n")
    for line in lines[1:]:
        stripped = line.strip()
        if stripped and stripped.startswith("*") and stripped.endswith("*"):
            return stripped.strip("*").strip()
    return ""


def extract_wiki_links(content: str) -> List[Tuple[str, str]]:
    links = []
    for match in re.finditer(r'\[\[([^\]]+?)\]\]', content):
        target = match.group(1)
        if "|" in target:
            target, alias = target.split("|", 1)
        else:
            alias = target
        if not target.endswith(".md"):
            target = target + ".md"
        links.append((target.strip(), alias.strip()))
    return links


def compute_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]


def walk_wiki() -> List[Path]:
    files = []
    for root, dirs, filenames in os.walk(WIKI_ROOT):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith(".")]
        for f in filenames:
            if f.endswith(".md") and not f.startswith("."):
                files.append(Path(root) / f)
    return files


# ============================================================================
# DATABASE
# ============================================================================

def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA_SQL)
    return conn


# ============================================================================
# COMMANDS
# ============================================================================

def cmd_index(args):
    conn = get_db()
    files = walk_wiki()
    is_reindex = args.cmd == "reindex"

    model = _load_model()
    if model:
        print(f"Embedding model: all-MiniLM-L6-v2 (local)")
    else:
        print(f"No embedding model available — indexing metadata + keyword search only")
        print(f"  Install: pip3 install sentence-transformers")

    print(f"Found {len(files)} markdown files...")

    indexed = skipped = 0
    for f in files:
        rel = str(f.relative_to(WIKI_ROOT))
        try:
            content = f.read_text(encoding="utf-8")
        except Exception as e:
            print(f"  SKIP: {rel} ({e})", file=sys.stderr)
            continue

        content_hash = compute_hash(content)

        if is_reindex:
            existing = conn.execute(
                "SELECT content_hash FROM wiki_files WHERE path = ?", (rel,)
            ).fetchone()
            if existing and existing["content_hash"] == content_hash:
                skipped += 1
                continue

        title = extract_title(content, rel)
        summary = extract_summary(content)
        word_count = len(content.split())
        mtime = datetime.fromtimestamp(f.stat().st_mtime).isoformat()

        embedding = get_embedding(f"{title}\n\n{content}")

        conn.execute("""
            INSERT INTO wiki_files (path, title, summary, content, word_count,
                                    last_modified, content_hash, embedding)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(path) DO UPDATE SET
                title=excluded.title, summary=excluded.summary,
                content=excluded.content, word_count=excluded.word_count,
                last_modified=excluded.last_modified,
                content_hash=excluded.content_hash,
                embedding=excluded.embedding,
                indexed_at=CURRENT_TIMESTAMP
        """, (rel, title, summary, content, word_count, mtime, content_hash, embedding))

        conn.execute("DELETE FROM wiki_links WHERE source_file = ?", (rel,))
        for target, link_text in extract_wiki_links(content):
            conn.execute("""
                INSERT OR IGNORE INTO wiki_links (source_file, target_file, link_text)
                VALUES (?, ?, ?)
            """, (rel, target, link_text))

        indexed += 1

    # Remove deleted files
    current_paths = {str(f.relative_to(WIKI_ROOT)) for f in files}
    existing_paths = {row["path"] for row in conn.execute("SELECT path FROM wiki_files")}
    deleted = existing_paths - current_paths
    for path in deleted:
        conn.execute("DELETE FROM wiki_files WHERE path = ?", (path,))
        conn.execute("DELETE FROM wiki_links WHERE source_file = ?", (path,))

    conn.commit()
    conn.close()

    print(f"\nDone: {indexed} indexed", end="")
    if skipped:
        print(f", {skipped} unchanged", end="")
    if deleted:
        print(f", {len(deleted)} removed", end="")
    print()


def cmd_search(args):
    conn = get_db()

    if args.semantic:
        query_emb = get_embedding(args.query)
        if not query_emb:
            print("Semantic search unavailable — falling back to keyword.", file=sys.stderr)
            args.semantic = False

    if args.semantic:
        rows = conn.execute("SELECT * FROM wiki_files WHERE embedding IS NOT NULL").fetchall()
        query_vec = unpack_embedding(query_emb)

        scored = []
        for row in rows:
            sim = cosine_similarity(query_vec, unpack_embedding(row["embedding"]))
            scored.append((sim, row))
        scored.sort(key=lambda x: x[0], reverse=True)

        top = scored[:args.limit]
        if not top:
            print("(no results)")
            return

        print(f"Top {len(top)} semantic matches for: {args.query}\n")
        for sim, row in top:
            summary = row['summary'] or row['content'][:150].replace("\n", " ")
            print(f"  [{sim:.3f}] {row['path']}")
            print(f"          {row['title']}")
            print(f"          {summary}")
            print()
    else:
        query = args.query.lower()
        rows = conn.execute(
            "SELECT * FROM wiki_files WHERE LOWER(content) LIKE ? OR LOWER(title) LIKE ? LIMIT ?",
            (f"%{query}%", f"%{query}%", args.limit)
        ).fetchall()

        if not rows:
            print("(no results)")
            return

        print(f"Found {len(rows)} matches for: {args.query}\n")
        for row in rows:
            print(f"  {row['path']}")
            print(f"    {row['title']}")
            for line in row['content'].split("\n"):
                if query in line.lower():
                    print(f"    > {line.strip()[:200]}")
                    break
            print()

    conn.close()


def cmd_stats(args):
    conn = get_db()

    total = conn.execute("SELECT COUNT(*) FROM wiki_files").fetchone()[0]
    if not total:
        print("Index is empty. Run: python3 wiki_search.py index")
        return

    with_emb = conn.execute("SELECT COUNT(*) FROM wiki_files WHERE embedding IS NOT NULL").fetchone()[0]
    total_words = conn.execute("SELECT SUM(word_count) FROM wiki_files").fetchone()[0] or 0
    total_links = conn.execute("SELECT COUNT(*) FROM wiki_links").fetchone()[0]

    print(f"=== Work Brain Search Index ===\n")
    print(f"Files:      {total}")
    print(f"Embeddings: {with_emb} ({100*with_emb//total}%)")
    print(f"Words:      {total_words:,}")
    print(f"Links:      {total_links}")
    print(f"Avg words:  {total_words // total:,}/file")
    print()

    print("By directory:")
    for row in conn.execute("""
        SELECT SUBSTR(path, 1, INSTR(path, '/') - 1) as dir, COUNT(*) as n
        FROM wiki_files WHERE INSTR(path, '/') > 0
        GROUP BY dir ORDER BY n DESC
    """):
        print(f"  {row['dir']:20s} {row['n']:3d}")
    print()

    print("Most linked-to:")
    for row in conn.execute("""
        SELECT target_file, COUNT(*) as n FROM wiki_links
        GROUP BY target_file ORDER BY n DESC LIMIT 10
    """):
        print(f"  [{row['n']:2d}] {row['target_file']}")
    print()

    print("Largest files:")
    for row in conn.execute("SELECT path, word_count FROM wiki_files ORDER BY word_count DESC LIMIT 5"):
        print(f"  {row['word_count']:5d} words  {row['path']}")

    conn.close()


def cmd_related(args):
    conn = get_db()
    row = conn.execute("SELECT * FROM wiki_files WHERE path = ?", (args.file,)).fetchone()
    if not row:
        print(f"File '{args.file}' not in index.", file=sys.stderr)
        sys.exit(1)

    if row["embedding"]:
        source_vec = unpack_embedding(row["embedding"])
        others = conn.execute(
            "SELECT * FROM wiki_files WHERE path != ? AND embedding IS NOT NULL",
            (args.file,)
        ).fetchall()

        scored = [(cosine_similarity(source_vec, unpack_embedding(o["embedding"])), o)
                  for o in others]
        scored.sort(key=lambda x: x[0], reverse=True)

        print(f"Semantically similar to: {row['title']}\n")
        for sim, other in scored[:args.limit]:
            print(f"  [{sim:.3f}] {other['path']} — {other['title']}")
    else:
        print(f"No embedding for {args.file}. Showing link-based relations only.\n")

    outgoing = conn.execute(
        "SELECT target_file FROM wiki_links WHERE source_file = ?", (args.file,)
    ).fetchall()
    incoming = conn.execute(
        "SELECT source_file FROM wiki_links WHERE target_file = ?", (args.file,)
    ).fetchall()

    if outgoing:
        print(f"\nLinks to ({len(outgoing)}):")
        for r in outgoing:
            print(f"  -> {r['target_file']}")
    if incoming:
        print(f"\nLinked from ({len(incoming)}):")
        for r in incoming:
            print(f"  <- {r['source_file']}")

    conn.close()


def cmd_orphans(args):
    conn = get_db()
    orphans = conn.execute("""
        SELECT path, title, word_count FROM wiki_files
        WHERE path NOT IN (SELECT DISTINCT source_file FROM wiki_links)
          AND path NOT IN (SELECT DISTINCT target_file FROM wiki_links)
        ORDER BY path
    """).fetchall()

    if not orphans:
        print("No orphans — every file has at least one link.")
        return

    print(f"Found {len(orphans)} orphan files:\n")
    for row in orphans:
        print(f"  {row['path']} ({row['word_count']} words)")
    conn.close()


def cmd_broken(args):
    conn = get_db()
    existing = {row["path"] for row in conn.execute("SELECT path FROM wiki_files")}
    links = conn.execute("SELECT DISTINCT source_file, target_file FROM wiki_links").fetchall()

    broken = []
    for row in links:
        target = row["target_file"]
        if target in existing:
            continue
        if any(e.endswith(target) or e.endswith(target.lstrip("./")) for e in existing):
            continue
        broken.append((row["source_file"], target))

    if not broken:
        print("No broken links.")
        return

    print(f"Found {len(broken)} broken links:\n")
    by_source = {}
    for source, target in broken:
        by_source.setdefault(source, []).append(target)
    for source, targets in sorted(by_source.items()):
        print(f"  {source}:")
        for t in targets:
            print(f"    -> {t}  (NOT FOUND)")
    conn.close()


# ============================================================================
# CLI
# ============================================================================

def main():
    p = argparse.ArgumentParser(description="Work Brain search")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("index", help="Full index").set_defaults(func=cmd_index)
    sub.add_parser("reindex", help="Index changed files only").set_defaults(func=cmd_index)

    s = sub.add_parser("search", help="Search the wiki")
    s.add_argument("query")
    s.add_argument("--semantic", action="store_true")
    s.add_argument("--limit", type=int, default=10)
    s.set_defaults(func=cmd_search)

    sub.add_parser("stats", help="Index statistics").set_defaults(func=cmd_stats)

    r = sub.add_parser("related", help="Find related files")
    r.add_argument("file", help="relative path")
    r.add_argument("--limit", type=int, default=10)
    r.set_defaults(func=cmd_related)

    sub.add_parser("orphans", help="Find orphan files").set_defaults(func=cmd_orphans)
    sub.add_parser("broken", help="Find broken links").set_defaults(func=cmd_broken)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
