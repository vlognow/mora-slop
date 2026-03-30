# Department of Vibes

> The CPO said "code more and automate with AI agents." We took it personally.

This is the Product Management team's shared hub for Claude Code skills, prompts, schemas, and automations. Everything here is machine-readable first, human-readable second.

## Quick Start

```bash
# Clone the repo
git clone git@github.com:butchsonik/department-of-vibes.git

# Install all skills into your Claude Code environment
cd department-of-vibes && ./install.sh

# Or just copy one skill manually
cp skills/pm-prd-generator.md ~/.claude/skills/
```

Then open Claude Code anywhere and your new skills are live.

## What's Inside

| Directory | What | For Whom |
|-----------|------|----------|
| `skills/` | Claude Code skills — single-purpose automations | Everyone |
| `schemas/` | YAML schemas for PRDs, one-pagers, briefs | PMs writing structured docs |
| `prompt-library/` | Reusable prompts by function | Anyone using Claude |
| `hooks/` | Claude Code hooks — set-and-forget automation | Power users |
| `scripts/` | Validation and catalog generation | Contributors |
| `examples/` | Real before/after outputs | New users learning the patterns |
| `docs/` | Guides, best practices, metrics | Everyone |

## The Philosophy

1. **Machine-readable first** — YAML frontmatter on everything. If Claude can't parse it, it doesn't ship.
2. **Composable over comprehensive** — Small skills that chain together beat monolithic agents.
3. **Show don't tell** — Every skill has a real example in `examples/`.
4. **No step is optional** — Inspired by CJ Silverio's agent productivity playbook. Contribution checklist is enforced, not suggested.
5. **Track impact** — Every skill declares expected time saved. We measure.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). The fastest path:

1. Run `/new-skill` in Claude Code while in this repo
2. Follow the guided workflow
3. Open a PR

## Starter Skills

- **`pm-prd-generator`** — Structured PRD from bullet points
- **`meeting-to-jira`** — Meeting notes to JIRA stories with acceptance criteria
- **`stakeholder-update`** — Status update calibrated to your audience

## Metrics

We track: skills contributed, hours saved/month, adoption rate. See [docs/METRICS.md](docs/METRICS.md).

**Current goal:** 5 skills in 30 days. Each saving 1-2 hours/week.

---

*Let's make this the most automated product team at the company.*
