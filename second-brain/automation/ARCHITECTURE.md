# Automation Architecture

How the second brain stays alive without manual discipline.

---

## The problem automation solves

Every personal knowledge system dies when the user forgets to maintain it. The wiki's automation layer eliminates "forgetting" as a failure mode by weaving wiki awareness into existing daily workflows and scheduling maintenance that runs without human initiation.

## Three layers of automation

### Layer 1 — Every session reads the wiki (durable)

**Mechanism:** Global `~/.claude/CLAUDE.md` contains instructions to read `~/work-brain/index.md` at session start.

**Effect:** Every Claude session — regardless of what Phil is working on — knows what the wiki contains. When a work knowledge question comes up, Claude checks the wiki before answering. When a concept emerges in conversation, Claude can propose a wiki note because it knows what already exists.

**Durability:** File on disk. Survives reboots, session restarts, everything.

### Layer 2 — End-of-session wiki proposals (durable)

**Mechanism:** Global `~/.claude/CLAUDE.md` instructs Claude to check at the end of substantive work sessions:
- Did a concept come up that has no wiki note?
- Did we learn something new about an existing concept/entity?
- Did a significant decision get made?
- Did something go wrong or right worth capturing?

**Effect:** The wiki grows organically from normal work conversations, not from dedicated "wiki time."

**Durability:** File on disk.

### Layer 3 — Daily digest includes wiki status (durable)

**Mechanism:** The daily-digest skill (`~/.claude/skills/daily-digest/SKILL.md`) includes:
- **Wiki status:** items in raw/, days since last lint, total note count
- **Wiki capture candidates:** decisions, concepts, entities, sources, and "Clone Phil gaps" surfaced from the day's Slack and GitHub activity

**Effect:** Every morning's digest shows wiki health and flags content worth capturing. Phil doesn't need to remember to check — it's in the briefing.

**Durability:** Skill file on disk.

## Three scheduled jobs (launchd)

All three run via macOS launchd — they survive reboots and don't require an active Claude session.

### Daily Digest — weekdays at 5:03am EDT

**Plist:** `com.philmora.work-brain.daily-digest.plist`

**What it does:** Reads 14 Slack channels + 4 GitHub repos + DMs. Produces a comprehensive morning briefing including wiki status and capture candidates. Posts to #claude-phil.

**Why 5:03am:** Ready before Phil starts his day. Off-minute to avoid API congestion.

### Daily Ingest Check — weekdays at 9:42am EDT

**Plist:** `com.philmora.work-brain.daily-ingest.plist`

**What it does:** Checks `~/work-brain/raw/` for unprocessed items. If empty, exits silently. If items exist, runs the ingest skill: reads each item, creates source notes, proposes concept/entity notes, moves processed files, updates index and log, posts summary to #claude-phil.

**Why 9:42am:** After Phil has had time to drop morning captures into raw/.

### Friday Lint — Fridays at 4:07pm EDT

**Plist:** `com.philmora.work-brain.friday-lint.plist`

**What it does:** Full maintenance cycle:
1. Ingest any remaining raw/ items
2. Scan all wiki files for orphans, broken links, gaps, contradictions, stale notes
3. Compress `sessions/current-week.md` into `sessions/weekly/YYYY-W##.md`
4. Regenerate `index.md`
5. Reindex semantic search embeddings
6. Post lint report to #claude-phil
7. Update `log.md`

**Why Friday 4:07pm:** End-of-week ritual. Pairs with Phil's existing Friday chain (platform-pulse → okr-update → weekly-update-entry → wiki lint).

## The wrapper script

`run-claude-task.sh` exists because launchd doesn't set up a shell environment. It:
1. Sets `HOME`, `PATH` with the correct node/Claude binary locations
2. Creates a log directory (`~/work-brain/scripts/logs/`)
3. Runs `claude -p "<prompt>"` (print mode, non-interactive)
4. Logs stdout to a dated file per task

Each launchd plist calls this script with the task prompt and a task name.

## The propose-don't-act safety model

All automation follows one rule: **propose, don't act** on canonical wiki content.

- **Canonical content** = concepts, entities, sources, projects, decisions. These represent Phil's compiled knowledge. Only Phil approves changes.
- **Mechanical content** = index.md, session compression, broken link fixes. These are bookkeeping. Automation handles them directly.

This means the daily ingest creates source notes (mechanical) but only *proposes* concept notes (canonical). The Friday lint regenerates the index (mechanical) but only *flags* contradictions (canonical). The human review gate is preserved even when automation runs headlessly.

## Installation

### Prerequisites
- macOS with launchd
- Claude Code CLI installed (`claude` binary accessible)
- Node.js (via fnm or nvm)

### Install the launchd jobs
```bash
cp automation/launchd/*.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.philmora.work-brain.daily-digest.plist
launchctl load ~/Library/LaunchAgents/com.philmora.work-brain.daily-ingest.plist
launchctl load ~/Library/LaunchAgents/com.philmora.work-brain.friday-lint.plist
```

### Verify
```bash
launchctl list | grep philmora
```

### Check logs
```bash
ls ~/work-brain/scripts/logs/
cat ~/work-brain/scripts/logs/daily-digest-$(date +%Y-%m-%d).log
```

### Uninstall
```bash
launchctl unload ~/Library/LaunchAgents/com.philmora.work-brain.*.plist
rm ~/Library/LaunchAgents/com.philmora.work-brain.*.plist
```

## Adapting for your own setup

If you're not Phil Mora on this specific machine, you'll need to change:
1. **Paths in `run-claude-task.sh`:** `HOME`, `PATH`, and the Claude binary location
2. **Paths in the plist files:** `ProgramArguments`, `StandardOutPath`, `StandardErrorPath`
3. **Slack channel IDs in the skill files:** your #claude-phil equivalent
4. **Wiki root in `wiki_search.py`:** the `WIKI_ROOT` constant
5. **Timing:** adjust the schedule to your timezone and work rhythm
