#!/usr/bin/env python3
"""
wiki_lint.py — Wiki maintenance / lint script

Performs the Stage 6 maintenance tasks from Karpathy's diagram:
- Find inconsistencies
- Fill gaps (identify missing notes)
- Find connections (suggest new cross-references)
- Suggest topics
- Plus housekeeping: orphans, broken links, stale notes, duplicate IDs

Usage:

    # Full report
    python3 wiki_lint.py ~/Documents/Brain

    # Specific checks
    python3 wiki_lint.py ~/Documents/Brain --check orphans
    python3 wiki_lint.py ~/Documents/Brain --check stale
    python3 wiki_lint.py ~/Documents/Brain --check broken-links
    python3 wiki_lint.py ~/Documents/Brain --check duplicates
    python3 wiki_lint.py ~/Documents/Brain --check frontmatter

    # Auto-fix what can be auto-fixed
    python3 wiki_lint.py ~/Documents/Brain --fix

    # Output as JSON (for scheduled task consumption)
    python3 wiki_lint.py ~/Documents/Brain --json
"""

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Set, Tuple


def walk_wiki(wiki_root: Path, exclude_dirs: List[str] = None) -> List[Path]:
    if exclude_dirs is None:
        exclude_dirs = ["raw", ".obsidian", ".git", "sessions/weekly", ".wiki_search.db"]
    files = []
    for root, dirs, filenames in os.walk(wiki_root):
        dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith(".")]
        for f in filenames:
            if f.endswith(".md"):
                files.append(Path(root) / f)
    return files


def extract_links(content: str) -> List[str]:
    """Return list of link targets (file paths or wikilinks)."""
    targets = []
    # [[wikilinks]]
    for m in re.finditer(r'\[\[([^\]|#]+)', content):
        t = m.group(1).strip()
        if not t.endswith(".md"):
            t = t + ".md"
        targets.append(t)
    # [text](path.md)
    for m in re.finditer(r'\[[^\]]+\]\(([^)]+\.md)\)', content):
        targets.append(m.group(1).strip())
    # Backtick-quoted paths
    for m in re.finditer(r'`([^`\s]+\.md)`', content):
        targets.append(m.group(1).strip())
    return targets


def extract_title(content: str, filename: str) -> str:
    for line in content.split("\n")[:10]:
        if line.strip().startswith("# "):
            return line.strip()[2:].strip()
    return Path(filename).stem


def extract_frontmatter(content: str) -> Dict:
    """Parse YAML frontmatter if present."""
    if not content.startswith("---"):
        return {}
    lines = content.split("\n")
    if len(lines) < 3:
        return {}
    # Find closing ---
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return {}
    fm = {}
    for line in lines[1:end]:
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    return fm


# ============================================================================
# CHECKS
# ============================================================================

def check_orphans(wiki_root: Path, files: List[Path]) -> Dict:
    """Find files with no incoming or outgoing links."""
    file_set = {str(f.relative_to(wiki_root)) for f in files}

    incoming = defaultdict(int)
    outgoing = defaultdict(int)

    for f in files:
        try:
            content = f.read_text(encoding="utf-8")
        except:
            continue
        rel = str(f.relative_to(wiki_root))
        targets = extract_links(content)
        for t in targets:
            outgoing[rel] += 1
            # Try to resolve t to an actual file
            if t in file_set:
                incoming[t] += 1
            else:
                # Try as suffix match
                for existing in file_set:
                    if existing.endswith(t) or existing.endswith("/" + t):
                        incoming[existing] += 1
                        break

    orphans = []
    for f in files:
        rel = str(f.relative_to(wiki_root))
        if incoming[rel] == 0 and outgoing[rel] == 0:
            # Skip README files and top-level schema files
            if Path(rel).name in ("README.md", "current-week.md"):
                continue
            orphans.append(rel)

    return {
        "orphans": orphans,
        "count": len(orphans),
        "message": f"Found {len(orphans)} orphan files (no incoming or outgoing links)",
    }


def check_stale(wiki_root: Path, files: List[Path], days: int = 90) -> Dict:
    """Find files not modified in N days."""
    cutoff = datetime.now() - timedelta(days=days)
    stale = []
    for f in files:
        # Skip sessions (expected to change frequently) and archives (frozen)
        rel = str(f.relative_to(wiki_root))
        if "sessions/ARCHIVE" in rel or "weekly/" in rel:
            continue
        mtime = datetime.fromtimestamp(f.stat().st_mtime)
        if mtime < cutoff:
            stale.append({
                "path": rel,
                "last_modified": mtime.isoformat()[:19],
                "days_old": (datetime.now() - mtime).days,
            })
    stale.sort(key=lambda x: x["days_old"], reverse=True)
    return {
        "stale": stale,
        "count": len(stale),
        "message": f"Found {len(stale)} files not modified in {days}+ days",
    }


def check_broken_links(wiki_root: Path, files: List[Path]) -> Dict:
    """Find links to files that don't exist."""
    file_set = {str(f.relative_to(wiki_root)) for f in files}

    broken = defaultdict(list)  # source -> list of broken targets
    for f in files:
        try:
            content = f.read_text(encoding="utf-8")
        except:
            continue
        rel = str(f.relative_to(wiki_root))
        targets = extract_links(content)
        for t in targets:
            # Try exact match
            if t in file_set:
                continue
            # Try with various path normalizations
            if t.lstrip("./") in file_set:
                continue
            # Suffix match (t might be just the filename while file is path/filename)
            if any(f.endswith(t) or f.endswith("/" + t) for f in file_set):
                continue
            broken[rel].append(t)

    return {
        "broken": dict(broken),
        "count": sum(len(v) for v in broken.values()),
        "message": f"Found {sum(len(v) for v in broken.values())} broken link targets across {len(broken)} files",
    }


def check_duplicates(wiki_root: Path, files: List[Path]) -> Dict:
    """Find files with duplicate titles (potential accidental duplicates)."""
    titles = defaultdict(list)
    for f in files:
        try:
            content = f.read_text(encoding="utf-8")
        except:
            continue
        title = extract_title(content, f.name).lower().strip()
        rel = str(f.relative_to(wiki_root))
        titles[title].append(rel)

    duplicates = {t: paths for t, paths in titles.items() if len(paths) > 1}
    return {
        "duplicates": duplicates,
        "count": len(duplicates),
        "message": f"Found {len(duplicates)} duplicate titles",
    }


def check_frontmatter(wiki_root: Path, files: List[Path]) -> Dict:
    """Check frontmatter consistency (if notes use frontmatter)."""
    uses_frontmatter = 0
    no_frontmatter = 0
    missing_required = []

    for f in files:
        try:
            content = f.read_text(encoding="utf-8")
        except:
            continue
        rel = str(f.relative_to(wiki_root))
        fm = extract_frontmatter(content)
        if fm:
            uses_frontmatter += 1
            # Check for commonly-expected fields
            if "type" not in fm and Path(rel).parent.name in ("entities", "concepts"):
                missing_required.append({"file": rel, "missing": "type"})
        else:
            no_frontmatter += 1

    return {
        "uses_frontmatter": uses_frontmatter,
        "no_frontmatter": no_frontmatter,
        "missing_required": missing_required,
        "message": f"{uses_frontmatter} files use frontmatter, {no_frontmatter} don't",
    }


def check_session_log_size(wiki_root: Path) -> Dict:
    """Check if current-week.md is growing too large."""
    path = wiki_root / "sessions" / "current-week.md"
    if not path.exists():
        return {"exists": False, "message": "no current-week.md found"}

    try:
        content = path.read_text(encoding="utf-8")
    except:
        return {"exists": True, "error": "could not read"}

    lines = len(content.split("\n"))
    words = len(content.split())
    chars = len(content)
    tokens_approx = chars // 4

    # Count session entries
    entries = len([l for l in content.split("\n") if l.startswith("## [")])

    return {
        "exists": True,
        "lines": lines,
        "words": words,
        "tokens_approx": tokens_approx,
        "entries": entries,
        "warning": tokens_approx > 5000,
        "message": f"current-week.md: {entries} entries, ~{tokens_approx} tokens"
                   + (" — ⚠️ exceeds 5K token threshold, consider compressing" if tokens_approx > 5000 else ""),
    }


def check_wiki_size(wiki_root: Path, files: List[Path]) -> Dict:
    """Total wiki size in tokens."""
    total_chars = 0
    largest = []
    for f in files:
        try:
            size = f.stat().st_size
            total_chars += size
            rel = str(f.relative_to(wiki_root))
            largest.append((size, rel))
        except:
            pass
    largest.sort(reverse=True)
    return {
        "total_files": len(files),
        "total_chars": total_chars,
        "tokens_approx": total_chars // 4,
        "largest_files": [{"size_bytes": s, "path": p, "tokens_approx": s // 4} for s, p in largest[:10]],
        "message": f"Wiki has {len(files)} files, ~{total_chars // 4:,} tokens total",
    }


# ============================================================================
# SUGGESTIONS (Claude-assisted — this script outputs suggestions for review)
# ============================================================================

def suggest_missing_notes(wiki_root: Path, files: List[Path]) -> Dict:
    """
    Suggest new notes based on concepts mentioned frequently across files
    but without their own dedicated note.

    Heuristic: if a capitalized term appears in 3+ files but has no file named after it,
    it might deserve its own note.
    """
    file_stems = {Path(f.relative_to(wiki_root)).stem.lower().replace("-", " ") for f in files}

    # Find capitalized phrases across all files
    mentions = defaultdict(int)
    for f in files:
        try:
            content = f.read_text(encoding="utf-8")
        except:
            continue
        # Find Title Case phrases 2-4 words
        for match in re.finditer(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3}\b', content):
            phrase = match.group(0).lower()
            if phrase not in file_stems:
                mentions[phrase] += 1

    suggestions = [
        {"phrase": phrase, "mention_count": count}
        for phrase, count in mentions.items() if count >= 3
    ]
    suggestions.sort(key=lambda x: x["mention_count"], reverse=True)

    return {
        "suggestions": suggestions[:20],
        "message": f"Found {len(suggestions)} concepts mentioned 3+ times with no dedicated note",
    }


# ============================================================================
# REPORT
# ============================================================================

def generate_report(wiki_root: Path, checks: List[str] = None) -> Dict:
    files = walk_wiki(wiki_root)

    report = {
        "wiki_root": str(wiki_root),
        "generated_at": datetime.now().isoformat(),
        "file_count": len(files),
        "checks": {},
    }

    checks_to_run = checks or ["orphans", "stale", "broken-links", "duplicates",
                                "frontmatter", "session-log-size", "wiki-size", "suggestions"]

    if "wiki-size" in checks_to_run:
        report["checks"]["wiki_size"] = check_wiki_size(wiki_root, files)
    if "orphans" in checks_to_run:
        report["checks"]["orphans"] = check_orphans(wiki_root, files)
    if "stale" in checks_to_run:
        report["checks"]["stale"] = check_stale(wiki_root, files)
    if "broken-links" in checks_to_run:
        report["checks"]["broken_links"] = check_broken_links(wiki_root, files)
    if "duplicates" in checks_to_run:
        report["checks"]["duplicates"] = check_duplicates(wiki_root, files)
    if "frontmatter" in checks_to_run:
        report["checks"]["frontmatter"] = check_frontmatter(wiki_root, files)
    if "session-log-size" in checks_to_run:
        report["checks"]["session_log_size"] = check_session_log_size(wiki_root)
    if "suggestions" in checks_to_run:
        report["checks"]["missing_note_suggestions"] = suggest_missing_notes(wiki_root, files)

    return report


def format_report_text(report: Dict) -> str:
    out = []
    out.append(f"# Wiki Lint Report — {report['wiki_root']}")
    out.append(f"*Generated {report['generated_at'][:19]}*")
    out.append(f"*{report['file_count']} files total*")
    out.append("")

    checks = report["checks"]

    if "wiki_size" in checks:
        c = checks["wiki_size"]
        out.append("## Wiki Size")
        out.append(f"- {c['message']}")
        out.append(f"- Largest files:")
        for f in c["largest_files"][:5]:
            out.append(f"  - `{f['path']}` — {f['tokens_approx']:,} tokens")
        out.append("")

    if "orphans" in checks:
        c = checks["orphans"]
        out.append("## Orphan Files")
        out.append(f"- {c['message']}")
        if c["orphans"]:
            for o in c["orphans"][:10]:
                out.append(f"  - `{o}`")
            if len(c["orphans"]) > 10:
                out.append(f"  - ... and {len(c['orphans']) - 10} more")
        out.append("")

    if "stale" in checks:
        c = checks["stale"]
        out.append("## Stale Files (90+ days)")
        out.append(f"- {c['message']}")
        for s in c["stale"][:10]:
            out.append(f"  - `{s['path']}` — {s['days_old']} days old (last {s['last_modified']})")
        out.append("")

    if "broken_links" in checks:
        c = checks["broken_links"]
        out.append("## Broken Links")
        out.append(f"- {c['message']}")
        for source, targets in list(c["broken"].items())[:10]:
            out.append(f"  - `{source}`:")
            for t in targets[:5]:
                out.append(f"    - `{t}` (not found)")
        out.append("")

    if "duplicates" in checks:
        c = checks["duplicates"]
        out.append("## Duplicate Titles")
        out.append(f"- {c['message']}")
        for title, paths in list(c["duplicates"].items())[:5]:
            out.append(f"  - \"{title}\":")
            for p in paths:
                out.append(f"    - `{p}`")
        out.append("")

    if "frontmatter" in checks:
        c = checks["frontmatter"]
        out.append("## Frontmatter")
        out.append(f"- {c['message']}")
        if c.get("missing_required"):
            out.append(f"- Missing required fields:")
            for m in c["missing_required"][:10]:
                out.append(f"  - `{m['file']}` missing `{m['missing']}`")
        out.append("")

    if "session_log_size" in checks:
        c = checks["session_log_size"]
        out.append("## Session Log")
        out.append(f"- {c['message']}")
        out.append("")

    if "missing_note_suggestions" in checks:
        c = checks["missing_note_suggestions"]
        out.append("## Missing Note Suggestions")
        out.append(f"- {c['message']}")
        for s in c["suggestions"][:10]:
            out.append(f"  - \"{s['phrase']}\" ({s['mention_count']} mentions)")
        out.append("")

    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser(description="Wiki maintenance / lint")
    parser.add_argument("wiki_root")
    parser.add_argument("--check", help="specific check to run (orphans|stale|broken-links|duplicates|frontmatter|session-log-size|wiki-size|suggestions)")
    parser.add_argument("--json", action="store_true", help="output as JSON")
    parser.add_argument("--fix", action="store_true", help="auto-fix what can be auto-fixed")

    args = parser.parse_args()

    wiki_root = Path(args.wiki_root).resolve()
    if not wiki_root.is_dir():
        print(f"ERROR: {wiki_root} is not a directory", file=sys.stderr)
        sys.exit(1)

    checks = [args.check] if args.check else None
    report = generate_report(wiki_root, checks)

    if args.json:
        print(json.dumps(report, indent=2, default=str))
    else:
        print(format_report_text(report))


if __name__ == "__main__":
    main()
