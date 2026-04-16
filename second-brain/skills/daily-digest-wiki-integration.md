# Daily Digest — Wiki Integration (Excerpt)

*This is an excerpt from the full daily-digest skill at `~/.claude/skills/daily-digest/SKILL.md`. It contains only the wiki-specific steps (7 and 8) that were added to accelerate the Clone Phil project.*

*The full daily-digest skill covers: 14 Slack channels, 4 GitHub repos, DMs, Follow-Up Radar, cross-channel synthesis, wiki status, and wiki capture candidates.*

---

## Design Principle

> Every digest run is an opportunity to accelerate the Clone Phil project. Surface knowledge that belongs in the wiki. Flag decisions worth capturing. Identify concepts that keep recurring but have no wiki note. The digest feeds the wiki; the wiki feeds the agents; the agents clone Phil.

---

## Step 7 — Cross-Channel Synthesis

Read `~/work-brain/index.md` to load active projects and concepts.

Look for connections the channel-by-channel view would miss:
- Activity in one channel that directly relates to activity in another
- Slack discussion that maps to a specific OKR or KR Phil owns
- A person mentioned in two different contexts
- A recurring concept or topic that keeps appearing across channels

Format:
```
*Connections*
- [Connection 1: what links to what, and why it matters]
- [Connection 2]
```

If no meaningful connections exist today, omit this section. Do not force connections.

## Step 8 — Wiki Status + Capture Candidates

### Status check
1. Count new (unprocessed) files in `~/work-brain/raw/` (exclude `processed/`)
2. Read the last entry in `~/work-brain/log.md` to find days since last lint
3. Count total wiki files: `find ~/work-brain -name "*.md" -not -path "*/raw/*" -not -path "*/.git/*" -not -path "*/.obsidian/*" | wc -l`

### Capture candidates (Clone Phil accelerator)

Review today's Slack and GitHub activity for content that belongs in the wiki. Flag anything that matches:

- A **decision** was made → suggest `decisions/YYYY-MM-DD-slug.md`
- A **concept** was discussed that has no wiki note (check index.md) → suggest `concepts/slug.md`
- An **entity** appeared that Phil interacts with regularly but has no entity note → suggest `entities/slug.md`
- A **source** was shared (article, doc, design doc link) → suggest dropping in `~/work-brain/raw/`
- A **recurring question** was asked that the wiki should be able to answer → flag as **Clone Phil gap**

The Clone Phil test: "if an agent saw this question in Slack, could it answer from the wiki?" If not, that's a gap worth flagging.

### Format
```
*Work Brain*
- raw/: [N] items waiting [or "empty"]
- Last lint: [date] ([N] days ago) [flag if >7 days]
- Size: [N] notes
- Captures: [N] flagged

*Wiki Capture Candidates*
- Decision: [what] → `decisions/slug.md`
- Concept: [name] discussed in [channel] → `concepts/slug.md`
- Entity: [name] in [N] channels → `entities/slug.md`
- Source: [link] → drop in raw/
- Clone Phil gap: "[question]" — wiki can't answer this yet
```
