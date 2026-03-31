# mora-slop

> It's slop, but it's *my* slop.

PM automation skills, prompts, and schemas built with Claude Code. Machine-readable first, human-readable second. Quality bar: would I send this output without editing? If yes, it ships. If no, it's actual slop and gets deleted.

## Quick Start

```bash
git clone git@github.com:butchsonik/mora-slop.git
cd mora-slop && ./install.sh
```

Then open Claude Code anywhere and your new skills are live.

## What's Inside

| Directory | What |
|-----------|------|
| `skills/` | Claude Code skills — the slop factory |
| `schemas/` | YAML schemas for PRDs, one-pagers, briefs |
| `prompt-library/` | Reusable prompts by function |
| `hooks/` | Set-and-forget automation |
| `scripts/` | Validation and catalog generation |
| `examples/` | Real before/after outputs — proof it's not just slop |
| `docs/` | Guides, best practices |

## The Philosophy

1. **Machine-readable first** — YAML frontmatter on everything. If Claude can't parse it, it doesn't ship.
2. **Composable over comprehensive** — Small skills that chain together beat monolithic agents.
3. **It works or it's gone** — No stubs, no "I'll finish this later," no aspirational code.
4. **Delete > accumulate** — Dead skills get archived. The repo should get smaller over time.
5. **It's slop, but it's my slop** — Self-deprecating about the process, serious about the output.

## Skills (12 in catalog)

**Starter skills** — generic, anyone can use:
- `pm-prd-generator` — Structured PRD from bullet points (Level 2: Machinify-aware)
- `meeting-to-jira` — Meeting notes to JIRA stories with acceptance criteria
- `stakeholder-update` — Status update calibrated to your audience

**Production skills** — battle-tested, running weekly:
- `platform-pulse` — Weekly platform highlights from Notion + GitHub + Jira + Slack
- `studio-pulse` — Weekly Studio highlights from GitHub releases + Slack
- `cloud-cost-pulse` — Weekly cloud cost progress from JIRA + GitHub + Slack
- `meeting-insights` — Deep analysis of meeting transcripts with intelligence layer
- `weekly-briefing` — Friday OKR accountability ritual
- `platform-okr-update` — Update OKR dashboard from weekend updates
- `weekly-update-entry` — Cross-team weekly product line update
- `daily-digest` — Daily Slack channel digest
- `todo` — Persistent todo list across sessions

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Three rules: it works, your name is on it, delete > accumulate.

---

*It's slop, but it's my slop.*
