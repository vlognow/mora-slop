#!/usr/bin/env python3
"""
pkm_ingest.py — PKM ingest helper (Stage 1+2 automation)

Watches a `raw/` folder for new content (PDFs, markdown, text, URLs) and
helps process them into the wiki. This is a HELPER script — the actual
intelligent classification and note creation happens in a Claude conversation
(the scheduled task calls Claude with the raw content).

What this script does:
1. Scan `wiki/raw/` for new files (not yet in `wiki/raw/processed/`)
2. For each file: extract text content, word count, timestamps
3. Output a structured report the Claude task uses to make decisions
4. Optionally: fetch URL content (if the raw file is a .url or .txt containing a URL)
5. Optionally: move processed files to `wiki/raw/processed/{date}/` after the task completes

Usage:

    # List pending items (what needs processing)
    python3 pkm_ingest.py list ~/Documents/Brain

    # Get structured data about a specific item
    python3 pkm_ingest.py inspect ~/Documents/Brain raw/paper-attention.pdf

    # Get a processing report for Claude (task uses this as input)
    python3 pkm_ingest.py report ~/Documents/Brain

    # Mark items as processed (move to processed/ folder)
    python3 pkm_ingest.py archive ~/Documents/Brain raw/paper-attention.pdf

    # Fetch a URL and save as markdown in raw/
    python3 pkm_ingest.py fetch ~/Documents/Brain "https://example.com/article"

Dependencies:
    - Standard library only for basic operations
    - Optional: requests + beautifulsoup4 for URL fetching
    - Optional: pypdf for PDF text extraction
"""

import argparse
import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional


def get_pending_items(wiki_root: Path) -> List[Path]:
    """List files in wiki/raw/ that haven't been processed yet."""
    raw_dir = wiki_root / "raw"
    if not raw_dir.is_dir():
        return []

    pending = []
    for item in raw_dir.iterdir():
        # Skip processed/ subdirectory
        if item.name == "processed":
            continue
        # Skip hidden files
        if item.name.startswith("."):
            continue
        if item.is_file():
            pending.append(item)
    return sorted(pending)


def extract_text(file_path: Path, max_chars: int = 50000) -> str:
    """Extract text content from a file. Supports .md, .txt, .pdf."""
    suffix = file_path.suffix.lower()

    if suffix in [".md", ".txt", ".markdown"]:
        try:
            return file_path.read_text(encoding="utf-8")[:max_chars]
        except Exception as e:
            return f"[ERROR reading: {e}]"

    if suffix == ".pdf":
        try:
            import pypdf
            reader = pypdf.PdfReader(str(file_path))
            text = ""
            for page in reader.pages[:50]:  # first 50 pages max
                text += page.extract_text() + "\n"
                if len(text) > max_chars:
                    break
            return text[:max_chars]
        except ImportError:
            return "[pypdf not installed — run: pip install pypdf]"
        except Exception as e:
            return f"[ERROR reading PDF: {e}]"

    if suffix == ".url":
        # Windows URL file — contains URL in INI format
        try:
            content = file_path.read_text(encoding="utf-8")
            for line in content.split("\n"):
                if line.startswith("URL="):
                    return f"URL reference: {line[4:].strip()}"
        except:
            pass
        return "[unknown URL file format]"

    return f"[unsupported file type: {suffix}]"


def inspect_item(wiki_root: Path, file_path: Path) -> Dict:
    """Get structured data about a raw item."""
    rel = file_path.relative_to(wiki_root) if file_path.is_absolute() else file_path
    full = file_path if file_path.is_absolute() else wiki_root / file_path

    if not full.exists():
        return {"error": f"not found: {rel}"}

    content = extract_text(full)
    stat = full.stat()

    # Try to extract a title from the first line / heading
    title = None
    first_lines = content.split("\n")[:5]
    for line in first_lines:
        stripped = line.strip()
        if stripped.startswith("# "):
            title = stripped[2:].strip()
            break
    if not title:
        for line in first_lines:
            if line.strip():
                title = line.strip()[:80]
                break

    return {
        "path": str(rel),
        "full_path": str(full),
        "size_bytes": stat.st_size,
        "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        "suffix": full.suffix,
        "title": title or full.stem,
        "word_count": len(content.split()),
        "char_count": len(content),
        "content_preview": content[:2000],
        "full_content": content,  # for the Claude task to process
    }


def cmd_list(args):
    wiki_root = Path(args.wiki_root).resolve()
    pending = get_pending_items(wiki_root)

    if not pending:
        print("(no pending items in raw/)")
        return

    print(f"Pending items in {wiki_root}/raw/ ({len(pending)}):")
    print()
    for item in pending:
        size = item.stat().st_size
        mtime = datetime.fromtimestamp(item.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
        print(f"  [{size:>8} bytes]  [{mtime}]  {item.name}")


def cmd_inspect(args):
    wiki_root = Path(args.wiki_root).resolve()
    file_path = Path(args.file)
    result = inspect_item(wiki_root, file_path)
    print(json.dumps(result, indent=2, default=str))


def cmd_report(args):
    """
    Generate a structured report for Claude to use as input to the ingest task.
    """
    wiki_root = Path(args.wiki_root).resolve()
    pending = get_pending_items(wiki_root)

    report = {
        "wiki_root": str(wiki_root),
        "generated_at": datetime.now().isoformat(),
        "pending_count": len(pending),
        "items": [],
    }

    for item in pending:
        data = inspect_item(wiki_root, item)
        report["items"].append({
            "path": data["path"],
            "title": data["title"],
            "size_bytes": data["size_bytes"],
            "word_count": data["word_count"],
            "suffix": data["suffix"],
            "content_preview": data["content_preview"][:1000],
        })

    print(json.dumps(report, indent=2, default=str))


def cmd_archive(args):
    """Move a processed file to raw/processed/{date}/"""
    wiki_root = Path(args.wiki_root).resolve()
    file_path = Path(args.file)
    if not file_path.is_absolute():
        file_path = wiki_root / file_path

    if not file_path.exists():
        print(f"ERROR: {file_path} not found", file=sys.stderr)
        sys.exit(1)

    today = datetime.now().strftime("%Y-%m-%d")
    archive_dir = wiki_root / "raw" / "processed" / today
    archive_dir.mkdir(parents=True, exist_ok=True)

    dest = archive_dir / file_path.name
    if dest.exists():
        # Add a suffix to avoid overwriting
        i = 1
        while (archive_dir / f"{file_path.stem}_{i}{file_path.suffix}").exists():
            i += 1
        dest = archive_dir / f"{file_path.stem}_{i}{file_path.suffix}"

    shutil.move(str(file_path), str(dest))
    print(f"✓ Archived: {file_path.name} → {dest.relative_to(wiki_root)}")


def cmd_fetch(args):
    """Fetch a URL and save the text content to raw/."""
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        print("ERROR: url fetching requires: pip install requests beautifulsoup4", file=sys.stderr)
        sys.exit(1)

    wiki_root = Path(args.wiki_root).resolve()
    url = args.url

    print(f"Fetching {url}...")
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0 pkm-ingest"})
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Remove scripts, styles, nav
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    title = soup.find("title")
    title_text = title.get_text().strip() if title else "untitled"

    # Extract main content (try common selectors)
    main = (soup.find("article") or
            soup.find("main") or
            soup.find("div", {"class": "content"}) or
            soup.body)
    text = main.get_text(separator="\n\n", strip=True) if main else soup.get_text()

    # Slug for filename
    slug = "".join(c if c.isalnum() or c in "-_" else "-" for c in title_text.lower())[:60]
    date = datetime.now().strftime("%Y-%m-%d")
    filename = f"{date}-{slug}.md"

    raw_dir = wiki_root / "raw"
    raw_dir.mkdir(exist_ok=True)
    dest = raw_dir / filename

    content = f"""# {title_text}

**Source:** {url}
**Fetched:** {datetime.now().isoformat()}

---

{text}
"""
    dest.write_text(content, encoding="utf-8")
    print(f"✓ Saved: {dest.relative_to(wiki_root)}")
    print(f"  {len(text.split())} words")


def main():
    parser = argparse.ArgumentParser(description="PKM ingest helper")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("list", help="List pending items in raw/")
    p.add_argument("wiki_root")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("inspect", help="Inspect a specific item")
    p.add_argument("wiki_root")
    p.add_argument("file", help="path relative to wiki root")
    p.set_defaults(func=cmd_inspect)

    p = sub.add_parser("report", help="Generate structured report for Claude")
    p.add_argument("wiki_root")
    p.set_defaults(func=cmd_report)

    p = sub.add_parser("archive", help="Move processed item to raw/processed/")
    p.add_argument("wiki_root")
    p.add_argument("file", help="path relative to wiki root or absolute")
    p.set_defaults(func=cmd_archive)

    p = sub.add_parser("fetch", help="Fetch a URL and save to raw/")
    p.add_argument("wiki_root")
    p.add_argument("url")
    p.set_defaults(func=cmd_fetch)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
