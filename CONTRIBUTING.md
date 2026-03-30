# Contributing

## Three Rules

1. **It has to work.** You tested it in Claude Code. The output is something you'd actually send — to a stakeholder, to eng, to a customer — without editing.

2. **Your name is on it.** The `author` field in the frontmatter is you. If it breaks or gets stale, that's on you. If you stop maintaining it, it gets archived.

3. **Delete > accumulate.** A skill nobody's used in 60 days gets questioned. If nobody speaks up, it's gone. Dead skills are worse than no skills — they erode trust in the repo.

That's it. No approval committee. No contribution quotas. No mandatory style beyond the YAML frontmatter (which exists for machine discovery, not bureaucracy).

## How to Contribute

**Fastest path:**
1. Open Claude Code in this repo
2. Run `/new-skill` — it walks you through everything
3. Commit and push

**Manual path:**
1. Copy `skills/SKILL-TEMPLATE.md`
2. Fill in the YAML frontmatter
3. Write the skill, test it, commit it

Either way: if it works and your name is on it, ship it.

## What Belongs Here

- Skills that save you real time and produce send-ready output
- Schemas that define how we structure recurring artifacts
- Prompts you find yourself reusing across projects
- Hooks that automate things you'd otherwise forget

## What Doesn't Belong Here

- Stubs and "I'll finish this later" drafts — commit when it works, not before
- Skills that require 10 minutes of context to use
- Anything where the output always needs heavy editing (that's a prompt, not a skill)
- Code projects with their own dependencies — those get their own repos

## Housekeeping

- `catalog.yaml` should reflect what's actually in `skills/`. Run `python3 scripts/generate-catalog.py` if you're not sure.
- `./scripts/validate.sh` catches missing frontmatter and catalog drift. Run it before pushing.
- If you notice a skill is dead or broken, open a one-line PR to archive or remove it. No ceremony required.
