# Skill: Work Brain Lint

## Purpose
Weekly maintenance of Phil's Karpathy-style LLM wiki. Finds orphans, broken links, gaps, contradictions, stale notes. Compresses session entries. Regenerates index. Propose-don't-act for canonical content.

---

## Trigger
User says something like:
- "run the lint task"
- "lint the wiki"
- "wiki maintenance"
- "run work brain lint"

---

## Schedule
Once per week, Friday afternoon. Pairs with Phil's existing Friday ritual chain (platform-pulse -> okr-update -> weekly-update-entry -> wiki lint).

---

## Pre-Flight

Read these files in parallel (single message):
1. `~/work-brain/README.md` — the schema
2. `~/work-brain/index.md` — current content catalog
3. `~/work-brain/log.md` — last 2 weeks of entries

---

## Workflow

### Step 1 — Inventory
- List every `.md` file in the wiki (excluding .obsidian/, .git/)
- Count by category: concepts, entities, sources, projects, areas, decisions, retros, sessions, MOCs, sandbox
- Compare against index.md — flag any files missing from the index

### Step 2 — Find orphans
- For each concept/entity/source file: check if anything else links to it (grep for its wikilink)
- For each concept/entity/source file: check if it links to anything
- Files with neither inbound nor outbound links are orphans — FLAG FOR REVIEW

### Step 3 — Find broken wikilinks
- For each `[[wikilink]]` in every file: check the target file exists
- If clearly a rename/move: auto-fix
- Otherwise: FLAG FOR REVIEW

### Step 4 — Find gap candidates
- Identify terms or names mentioned by name in 3+ files that don't have their own note
- PROPOSE creating them (don't create automatically)

### Step 5 — Find contradictions
- For each entity: check that different files agree on stable facts (title, role, team)
- For each concept: check that different source citations don't contradict
- FLAG any contradictions found

### Step 6 — Find stale notes
- List files untouched for 90+ days
- FLAG for "still relevant?" review (never delete automatically)

### Step 7 — Compress sessions
- Read `sessions/current-week.md` (if it exists)
- If the week has ended: summarize into `sessions/weekly/YYYY-W##.md`
- Clear `current-week.md` for the new week (keep the header)
- If no current-week.md exists yet, skip

### Step 8 — Regenerate index.md
- Scan all files in concepts/, entities/, sources/, projects/, areas/, decisions/, MOCs/, sandbox/
- Read the first line of each file (the `# Title`) and the italic summary line below it
- Rebuild index.md with one-line summaries per file
- Alphabetize within each section
- Overwrite index.md with the new version

### Step 9 — Generate the maintenance report
Save to `~/work-brain/sandbox/lint-report-{YYYY-MM-DD}.md`:
- **Stats:** total files, count by category, new since last lint
- **Auto-fixed:** compressed sessions, regenerated index, fixed broken links
- **Flagged for Phil:** orphans, gap candidates, contradictions, stale notes
- **Suggested actions:** prioritized list of what Phil should review

### Step 10 — Reindex semantic search
Run:
```bash
source ~/work-brain/.venv/bin/activate && cd ~/work-brain && python3 wiki_search.py reindex
```
This re-embeds any files that changed since last index. Incremental — only processes changed files.

### Step 11 — Append to log.md
```
## [YYYY-MM-DD HH:MM] lint | Weekly maintenance
- Total files: {N} ({breakdown by category})
- Compressed {N} session entries
- Found {N} orphans: {list}
- Found {N} broken links: {fixed N, flagged N}
- Proposed {N} new notes: {list}
- Found {N} contradictions: {list}
- Found {N} stale notes (90+ days): {list}
- Regenerated index.md
```

---

## Hard Rules

- **PROPOSE, don't act** for anything modifying canonical concept/entity/source/project content.
- **ACT DIRECTLY** only for: index.md regeneration, session compression, obvious broken-link fixes.
- **ALWAYS generate a report** — never run silently.
- **ALWAYS append to log.md.**
- **NEVER delete** any file without Phil's explicit approval.

---

## Output
Two things:
1. The lint report saved to `sandbox/lint-report-{YYYY-MM-DD}.md`
2. A concise summary message to Phil with the top 3-5 items needing his attention
