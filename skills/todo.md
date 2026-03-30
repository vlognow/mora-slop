---
name: todo
version: "2.0"
author: phil-mora
tags: [pm, productivity, todo, persistent]
trigger: "Persistent todo list with add done drop update blocked wip list clean"
inputs: ["subcommand + arguments"]
outputs: ["Updated todo list in memory"]
estimated_time_saved: "15 min per day"
---

# Skill: Todo

## Purpose
Persistent todo list shared between Phil and Claude across all sessions.
Data lives in `~/.claude/projects/-Users-phil-mora/memory/todo.md` so it survives every conversation restart.

---

## Trigger
User invokes `/todo` with an optional subcommand and arguments.

---

## Subcommands

| Command | Description |
|---------|-------------|
| `/todo` | Show the full todo list (grouped by category, sorted by priority) |
| `/todo add <description>` | Add a new item. Optionally include flags (see below) |
| `/todo done <id or description>` | Mark an item as ✅ done |
| `/todo drop <id or description>` | Remove an item entirely |
| `/todo update <id or description>` | Modify fields — priority, status, category, notes, due date |
| `/todo blocked <id or description>` | Mark an item as 🔴 blocked (optionally add reason) |
| `/todo wip <id or description>` | Mark an item as 🟡 in-progress |
| `/todo open <id or description>` | Reset an item back to ⬚ open |
| `/todo list [filter]` | Filter view — e.g. `/todo list build`, `/todo list P0`, `/todo list blocked` |
| `/todo clean` | Archive all done items to the `## Archive` section |
| `/todo help` | Show this command reference |

### Flags for `/todo add`
All optional. If omitted, defaults apply.

| Flag | Values | Default |
|------|--------|---------|
| `-p` | P0, P1, P2, P3 | P2 |
| `-c` | build, product, ops, stakeholder, personal | (inferred or `personal`) |
| `-d` | due date (YYYY-MM-DD or natural language → converted) | none |
| `-n` | note / context | none |

**Examples:**
- `/todo add Ship RPS Bridge isolation spec -p P0 -c product -d 2026-03-22`
- `/todo add Review Ianiv's olapui PR -c build`
- `/todo done RPS Bridge`
- `/todo list build`
- `/todo blocked RPS Bridge -n waiting on CJ capacity`

---

## Data File Format

The todo list is stored at:
`~/.claude/projects/-Users-phil-mora/memory/todo.md`

### Structure

```markdown
# Todo List

## Active Items

| ID | Pri | Status | Category | Description | Due | Notes | Added |
|----|-----|--------|----------|-------------|-----|-------|-------|
| 1  | P0  | ⬚ open | product  | Ship RPS Bridge isolation spec | 2026-03-22 | — | 2026-03-18 |

## Archive
(Completed/dropped items moved here by `/todo clean`)
```

### Rules
- **ID** is an auto-incrementing integer. Never reuse IDs.
- To find the next ID: scan all items (active + archive) and use max + 1.
- **Status values**: `⬚ open`, `🟡 wip`, `🔴 blocked`, `✅ done`
- When matching items by description, use fuzzy substring match (case-insensitive). If ambiguous, show matches and ask Phil to pick.
- Always read the current file before any mutation to avoid stale writes.
- After any mutation, show the updated list (or the relevant subset).
- When showing the list, group by category, sort by priority within each group, and hide the Added column for cleaner display.

---

## Step-by-Step Process

### For any subcommand:
1. **Read** `~/.claude/projects/-Users-phil-mora/memory/todo.md`
2. **Parse** the markdown table into structured data
3. **Execute** the requested operation
4. **Write** the updated file back
5. **Display** the result to Phil — clean, formatted, no fluff

### For `/todo` (no args) or `/todo list`:
1. Read the file
2. Display grouped by category, sorted by priority
3. Show count summary at the bottom (e.g., "12 items: 3 P0, 5 P1, 4 P2 · 2 blocked")

### For `/todo help`:
Display the subcommand table and flag reference from this skill doc. Keep it tight — terminal-friendly formatting.
