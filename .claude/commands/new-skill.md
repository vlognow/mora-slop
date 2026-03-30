# /new-skill — Guided Skill Creation

You are helping a PM create a new skill for the Department of Vibes repo.
Follow these phases exactly. **No step is optional.**

## Phase 1: Discovery (before writing anything)

Ask the user:
1. **What task does this automate?** (one sentence)
2. **How often do you do this?** (daily / weekly / monthly)
3. **What inputs do you start with?** (meeting notes, bullet points, data, etc.)
4. **What output do you need?** (JIRA stories, a doc, a Slack message, YAML, etc.)
5. **What makes a good vs. bad output?** (the quality bar)

Do NOT proceed until you have clear answers to all 5.

## Phase 2: Test the Prompt Manually

**Critical: Do this before encoding as a skill.**

Using the user's answers, draft a raw prompt and test it right now:
1. Ask the user for a real example input
2. Run the prompt against that input
3. Show the output to the user
4. Ask: "Is this output good enough to send without editing?"

If no: iterate on the prompt until the output passes the quality bar.
If yes: proceed to Phase 3.

## Phase 3: Encode as a Skill

1. Copy `skills/SKILL-TEMPLATE.md`
2. Fill in all YAML frontmatter fields:
   - `name`: kebab-case, descriptive
   - `version`: "1.0"
   - `author`: user's Slack handle
   - `tags`: relevant categories
   - `trigger`: one sentence — when to use this
   - `inputs`: what the user provides
   - `outputs`: what the skill produces
   - `estimated_time_saved`: be realistic, not aspirational
3. Write the skill body following the template structure
4. Include the real example from Phase 2

**Checkpoint:** The skill must be ≤ 150 lines. If longer, split it.

## Phase 4: Validate

1. Run `./scripts/validate.sh` — must pass clean
2. Verify the skill works by running it in Claude Code
3. Update `catalog.yaml` with the new entry

## Phase 5: Ship

1. Create a branch: `skill/[skill-name]`
2. Commit with message: `feat: add [skill-name] skill v1.0`
3. Open a PR titled `[Skill] [skill-name] v1.0`
4. Tag @phil-mora for review

Tell the user: "Your skill is ready for review. Once merged, anyone on the team can install it with `./install.sh`."
