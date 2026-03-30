# Best Practices

## Writing Skills

1. **Keep it tiny** — Skills ≤ 150 lines. If it's longer, you're combining two skills.
2. **Test before encoding** — Run the prompt manually first. If the raw output isn't good, the skill won't be either.
3. **Be explicit, not clever** — Claude is brilliant but literal. "Produce a PRD" is vague. "Produce YAML matching schemas/prd.yaml with all required fields" is actionable.
4. **Include failure modes** — What should happen with bad input? Missing fields? Edge cases?
5. **First-person voice** — "You are a Senior PM..." not "The assistant should..."
6. **Structured output first** — Always produce machine-readable output (YAML/JSON) before any human prose.
7. **Version everything** — Bump version on every change.
8. **No fluff** — Human section = max 2 short paragraphs + bullets.

## Writing Prompts

1. **BLUF** — Lead with what you want, then context.
2. **Specify format explicitly** — Don't hope for the right format. Define it.
3. **Include anti-examples** — "Do NOT include pleasantries or hedging language."
4. **One job per prompt** — Composable beats comprehensive.

## Composability Pattern

Skills are most powerful when they chain:

```
meeting notes → [meeting-to-jira] → YAML stories
                                          ↓
                              JIRA API (manual or automated)
                                          ↓
                              sprint data → [stakeholder-update] → exec summary
```

Design skills to consume each other's output. The glue is structured data (YAML).

## What Makes a Skill Worth Sharing

- Saves ≥ 30 min per use
- Used by ≥ 2 people on the team
- Output is send-ready without editing
- Someone else can use it without asking you how
