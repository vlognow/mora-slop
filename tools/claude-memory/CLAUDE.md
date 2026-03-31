# claude-memory — Agent Integration Guide

This file tells Claude Code (and any AI agent) how to use the memory system.

## Setup

The memory tool lives at `~/.claude/shared-memory/memory_tool.py`. All commands are invoked via:

```bash
python3 ~/.claude/shared-memory/memory_tool.py <command> [args]
```

## When Starting a Session

Load context for the project you're working on:

```bash
python3 ~/.claude/shared-memory/memory_tool.py context --project <project-name>
```

This returns a focused block of rules, recent context, references, and learnings — much more relevant than reading a raw MEMORY.md file.

## When You Need Specific Knowledge

Search for it:

```bash
# Fast keyword search
python3 ~/.claude/shared-memory/memory_tool.py search "deployment process"

# Semantic search (understands meaning, not just keywords)
python3 ~/.claude/shared-memory/memory_tool.py search "how do we handle authentication" --semantic
```

## When You Learn Something New

Save it so future sessions benefit:

```bash
python3 ~/.claude/shared-memory/memory_tool.py add \
  --id "learning-<descriptive-slug>" \
  --name "<Short Title>" \
  --type learning \
  --project <project-name> \
  --content "<What you learned and why it matters>"
```

### What to Save

- **feedback**: Rules, corrections, things the user told you to do or not do
- **learning**: Patterns you discovered (a workaround, a platform behavior, a gotcha)
- **project**: Status updates, milestone completions, blockers
- **reference**: Stable facts like URLs, account IDs, file paths

### What NOT to Save

- Things derivable from reading the code or git history
- Temporary task state (use todo lists instead)
- Anything already in CLAUDE.md files

## When Completing a Scheduled Task

Log what you did:

```bash
python3 ~/.claude/shared-memory/memory_tool.py log \
  --actor "<task-id>" \
  --action "complete" \
  --details '{"summary": "what was accomplished"}'
```

## Memory Types at a Glance

| Type | Always loaded in context? | Example |
|------|--------------------------|---------|
| feedback | Yes | "Never force-push to main" |
| project | If recent (14 days) | "Sprint 12 started March 28" |
| reference | Top 5 by access count | "Prod DB is in AWS us-east-1" |
| learning | If recent (7 days) | "The staging API caches for 5 min" |
