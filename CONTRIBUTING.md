# Contributing to Department of Vibes

## The Fastest Path

1. Open Claude Code in this repo
2. Run `/new-skill`
3. Follow the guided workflow — it handles frontmatter, structure, and catalog entry
4. Open a PR

## Manual Contribution Flow

1. Branch from `main`
2. Copy `skills/SKILL-TEMPLATE.md` to `skills/your-skill-name.md`
3. Fill in the YAML frontmatter (all fields required)
4. Write the skill body (≤ 150 lines total)
5. Add an example to `examples/your-skill-name/`
6. Run `./scripts/validate.sh` — must pass clean
7. Update `catalog.yaml` (or run `python3 scripts/generate-catalog.py`)
8. Open a PR titled `[Skill] your-skill-name v1.0`

## PR Checklist (enforced)

- [ ] YAML frontmatter present and valid (name, version, author, tags, trigger, inputs, outputs)
- [ ] Tested in Claude Code — actually ran it, not just wrote it
- [ ] Human section ≤ 2 paragraphs
- [ ] Total skill ≤ 150 lines
- [ ] Example output in `examples/`
- [ ] `catalog.yaml` updated
- [ ] `./scripts/validate.sh` passes

## Skill Quality Bar

**Ship it if:**
- It saves ≥ 30 minutes per use
- Someone else on the team would actually use it
- The output is good enough to send without editing

**Don't ship it if:**
- It's a prompt you use once a quarter
- It requires 10 minutes of setup/context to use
- The output always needs heavy editing

## Naming Conventions

- Skill files: `kebab-case.md` (e.g., `pm-prd-generator.md`)
- Tags: lowercase, no spaces (e.g., `pm`, `jira`, `stakeholder`)
- Versions: semver-ish — bump minor for improvements, major for breaking changes

## Review Process

- Tag `@phil-mora` for review (≤24h turnaround)
- Low ceremony — if it works and follows the template, it ships
