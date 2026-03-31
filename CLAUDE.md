# mora-slop — Project Instructions

> It's slop, but it's my slop.

Phil Mora's PM automation lab. Skills, prompts, schemas, and automations built with Claude Code.
Everything here is designed to be discovered and used by Claude Code automatically.

## Core Principle

**Machine-readable first, human-readable second.**

Every skill, schema, and template starts with structured YAML frontmatter.
The human prose exists to explain — the YAML exists to execute.
If it can't be parsed, it can't be automated. If the output isn't send-ready, it's actual slop and gets deleted.

## Repo Layout

```
skills/              # Claude Code skills (.md) — drop into ~/.claude/skills/
schemas/             # YAML schemas for structured PM artifacts
prompt-library/      # Reusable prompts organized by function
  pm/                # Product management prompts
  engineering/       # Engineering collaboration prompts
  shared/            # Cross-functional prompts
hooks/               # Claude Code hooks for automation
scripts/             # Utility scripts (validation, catalog generation)
examples/            # Real before/after outputs — proof it's not just slop
docs/                # Human-readable guides (kept minimal)
.claude/commands/    # Slash commands for this repo
.github/             # PR template, CI
catalog.yaml         # Machine-readable index of all skills
```

## How to Use a Skill

1. Browse `catalog.yaml` or `skills/` directory
2. Copy the skill file to `~/.claude/skills/` (or run `./install.sh`)
3. The skill auto-loads in your next Claude Code session

Or just ask Claude: "What skills are available in this repo for [task]?"

## Fork-in-the-Road Decisions

| Situation | Use This | Not This |
|-----------|----------|----------|
| Repeatable task with structured I/O | **Skill** (`.md` in `skills/`) | Raw prompt in a chat |
| One-off question or exploration | **Prompt** (from `prompt-library/`) | A full skill |
| Multi-step workflow with checkpoints | **Slash command** (`.claude/commands/`) | A mega-skill |
| Data structure definition | **Schema** (`.yaml` in `schemas/`) | Inline in a skill |
| Automated action on every commit/session | **Hook** (`hooks/`) | Manual reminder |

## Skill Frontmatter Standard

Every skill MUST start with this YAML frontmatter:

```yaml
---
name: short-kebab-case-name
version: "1.0"
author: your-slack-handle
tags: [pm, prd, jira]           # used for discovery
trigger: "when to invoke this"   # one line, plain English
inputs: ["what the user provides"]
outputs: ["what the skill produces"]
---
```

The `trigger` field is critical — it's how Claude (and humans) decide when to use the skill.

## Writing Standards

- **BLUF** (Bottom Line Up Front) — lead with the answer, not the reasoning
- Human sections: max 2 short paragraphs + bullets. No fluff.
- No hedging. No filler. No "it's worth noting that."
- Length scales with complexity. Never padded. Never truncated when depth matters.

## What We Decided Not to Automate

See `docs/REJECTED-AUTOMATIONS.md` — before building something new, check if we already evaluated and rejected it (and why).

## Validation

Run `./scripts/validate.sh` before pushing. It checks:
- All skills have valid YAML frontmatter
- All skills are listed in `catalog.yaml`

## Contributing

See `CONTRIBUTING.md` or run `/new-skill` in Claude Code while in this repo.
Three rules: it works, your name is on it, delete > accumulate.
