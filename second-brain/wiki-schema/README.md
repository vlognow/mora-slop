# Phil Mora — Work Brain

**A Karpathy-style LLM wiki for professional knowledge — personal research, learning, and reference for work at Machinify.**

*Maintained by Phil Mora + Claude*
*Bootstrapped: 2026-04-14*

---

## What this wiki is for

Phil's professional knowledge: concepts, entities, sources, projects, decisions, and lessons learned as Sr. Director of Product Management for Core Platform and Data at Machinify. A compounding second brain that accumulates learning over time.

This wiki has a downstream consumer beyond Phil: a future swarm of AI agents that answer questions on Phil's behalf in Slack. The quality bar for every note is: **could an agent synthesize a good answer from this content?**

## What this wiki is NOT for

- Team-shared source of truth (that's Notion)
- Task management (that's Jira)
- Operational state and session memory (that's `~/dev/shared-memory/` and `~/.claude/` memory)
- Weekly context snapshots (that's `~/dev/context/machinify.md` and `active-projects.md`)
- Skill definitions (that's `~/.claude/skills/`)
- Credentials, PII, client-confidential data (see Privacy Rules below)
- Work email or Slack search
- Performance review content about colleagues
- Emotional journaling — sessions are behavioral ("what I did, what I learned"), not personal

## Navigation

- **[[index]]** — content catalog of every page, auto-maintained
- **[[log]]** — append-only operation log, newest first

## Directory structure

- `concepts/` — atomic notes on ideas. One concept per file. Evergreen notes. Named by the idea, not by the source.
- `entities/` — notes on people, teams, orgs, products, vendors. One per file.
- `sources/` — notes about specific papers, books, articles, talks, meeting insights.
- `projects/` — active work projects with status, goals, decisions, and log.
- `areas/` — ongoing areas of responsibility (platform strategy, data strategy, AI enablement, cloud cost).
- `decisions/` — Architectural Decision Records (ADRs). Major decisions with context, alternatives, consequences.
- `retros/` — retrospectives and lessons learned.
- `MOCs/` — Maps of Content. Hub pages linking related notes when a topic grows past 10+ related files.
- `sessions/` — episodic log of what Phil did and learned. `current-week.md` is append-only; compressed to `weekly/YYYY-W##.md` by the lint task.
- `sandbox/` — in-progress drafts, working memory, quarantined content. Can be deleted freely.
- `raw/` — imported sources awaiting ingestion. Moved to `raw/processed/{YYYY-MM-DD}/` after processing. Immutable — never edit raw sources in place.

## Writing rules (for Claude when maintaining this wiki)

1. **Paraphrase, never transcribe.** Write in Phil's voice. Never quote more than one sentence at a time from a source. The whole value of PKM comes from rephrasing in your own words.
2. **Atomic notes.** One concept per file. If a note is trying to cover two ideas, split it.
3. **Dense cross-references.** Use `[[wikilinks]]` liberally. Every concept note should link to 2-5 related notes. Isolated notes are worthless.
4. **Cite everywhere.** Every new fact needs `*Source: [[sources/{source-slug}]]*`.
5. **Extend, don't overwrite.** If a concept note exists, add a new section. Never rewrite existing content without Phil's approval.
6. **Concept-oriented naming.** File names describe the idea, not the source. `concepts/agentic-readiness.md` — not `concepts/ai-enablement-program-summary.md`.
7. **Update index.md and log.md after every operation.** No exceptions.
8. **Propose, don't act** for anything modifying canonical concept/entity/source/project content. Mechanical work (compressing sessions, fixing broken links, regenerating the index) can be done directly. Everything else is a proposal that waits for Phil's approval.

## Privacy rules

These are **hard rules**. No exceptions.

- NO credentials, API keys, passwords, tokens, certificates
- NO PII (SSNs, DOBs for identification, financial account details)
- NO client-confidential material or anything under NDA
- NO data regulated under HIPAA, GDPR special categories, PCI, or export controls
- NO performance review content about colleagues
- NO anything Phil's manager, legal, or HR would object to in a personal knowledge system
- Material with ambiguous classification goes in `sandbox/` with a `FLAG FOR REVIEW` marker, not in canonical folders. Ask Phil in the next ingest report.

## Privacy tier

**Standard:** Anthropic API (Claude) usage is fine. Local embeddings when the time comes. No other external APIs for wiki content.

## Tasks that operate on this wiki

- **Ingest** (manual): process `raw/` into atomic notes. Phil triggers by saying "run the ingest task." Natural moments: end of a Claude session with new raw content, start of Friday ritual, ad hoc.
- **Query** (session protocol): read index, read relevant files, answer, propose promotion of synthesis back to wiki.
- **Lint** (weekly, Friday PM): find orphans, broken links, gaps, contradictions; compress sessions; regenerate index. Pairs with existing Friday ritual chain.

## Relationship to other systems

This wiki is a **new layer** that complements Phil's existing infrastructure:

| System | Purpose | Relationship to wiki |
|--------|---------|---------------------|
| `~/dev/shared-memory/` | Operational cross-session memory (SQLite) | Separate. Wiki is knowledge, shared-memory is operational state. |
| `~/.claude/` memory | Auto-memory for Claude Code sessions | Separate. May reference wiki content but doesn't duplicate it. |
| `~/dev/context/` files | Weekly-refreshed company and project snapshots | Separate. Context files are summaries; wiki is the deep knowledge. |
| `~/.claude/skills/` | Operational skills (pulse, digest, etc.) | Skills may query the wiki in the future. Wiki doesn't contain skill definitions. |
| Notion | Team-shared docs, OKRs, strategy, meeting insights | Wiki ingests from Notion (via raw/) but doesn't replace it. Notion is the team source of truth; wiki is Phil's personal synthesis. |
| Slack | Conversations, decisions, threads | Wiki may ingest notable threads (via raw/). Future: agent swarm reads wiki to answer on Phil's behalf. |

## Downstream consumer: Clone Phil

The aspirational project is a swarm of AI agents that answer questions on Phil's behalf in Slack, backed by this wiki. This means:

- Every note should be self-contained enough for an agent to use without reading 10 other files
- Cross-references should be explicit about *why* two concepts relate, not just that they do
- Entity notes should capture Phil's perspective and relationship, not just facts
- The quality bar is: **if an agent read only this note and the index, could it give a useful answer?**
