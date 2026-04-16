# Work Second Brain — Phase 0 Discovery

**Date:** 2026-04-14
**Participant:** Phil Mora + Claude Opus 4.6

---

## 10 Decisions

### 1. Wiki location
**Decision:** `~/work-brain/`

### 2. Frontend
**Decision:** Obsidian

### 3. Version control
**Decision:** Git + private remote repo (vlognow org on GitHub)

### 4. Embedding provider
**Decision:** Local embeddings (when needed). Skip for now — wiki will be <100 files initially. Revisit at the 100-file mark. When the time comes, use `nomic-embed-text` or `sentence-transformers` to keep content off external APIs.

### 5. Ingest task mode
**Decision:** Manual to start. Trigger points:
- End of a Claude session where raw/ has new content
- Start of Friday ritual (before lint)
- Ad hoc when you remember
- Future: daily-digest skill could remind "N unprocessed items in raw/"

### 6. Lint cadence
**Decision:** Weekly Friday afternoon. Pairs with existing Friday ritual chain (platform-pulse -> okr-update -> weekly-update-entry -> wiki lint).

### 7. Privacy tier
**Decision:** Standard. Anthropic API (Claude) is fine. Local embeddings when the time comes. No other external APIs for wiki content.

### 8. Scope of content
**Decision:** All work knowledge. Meeting notes go into `raw/` and get distilled into atomic concept/entity notes — transcripts don't live in the wiki proper. No HR/compensation/performance review content.

### 9. Sharing posture
**Decision:** Shareable read-only. Build for personal use but design so select pages can be exported for onboarding, handoffs, or team reference.

### 10. Seeding strategy
**Decision:** Fresh notes only. 5-10 new atomic notes based on active thinking. No migration of existing knowledge infrastructure (shared memory, context files, Notion, CLAUDE.md memory system stay as-is). The wiki is a new layer, not a replacement.

---

## Discovery Questions

### Where does existing work knowledge live?
- **Notion** — primary: OKRs, strategy docs, project pages, meeting insights, weekly updates, pulse reports
- **Slack** — conversations, decisions, context in threads across ~15 channels
- **GitHub** (vlognow org) — code, PRs, technical decisions
- **JIRA** (machinify.atlassian.net) — stories, epics, sprint tracking
- **`~/dev/context/`** — machinify.md (company context) and active-projects.md (current state)
- **`~/.claude/` memory system** — auto-memory + shared-memory SQLite for cross-session persistence
- **`~/.claude/skills/`** — operational skills (platform-pulse, studio-pulse, etc.)
- **Phil's head** — mental models, frameworks, industry patterns, relationship context

### Tooling constraints
- Can install apps freely (Obsidian OK)
- Python 3 available
- Git available
- brew available
- No restrictive IT policies on this machine

### Top 3 active work projects
1. **Q2 Platform & Data OKRs** — 6 product themes, 15+ KRs spanning rules engine, cross-project APIs, mac-ui, machined-rs, cloud cost, Evolent, Lazarus, SQL language server, KTLO. Phil owns or co-owns KRs across all themes.
2. **Platform & Data Strategy** — the strategic narrative: "We are a technology company. The platform work IS the business strategy." 300M lives canonicalization, cloud migration, AI-native componentry, contributor velocity.
3. **AI Enablement Program** — "Repo AI Enablement": prepare the codebase, not the developer. Top 20 repos, champions model, 8-16hr autonomous agent runtime target. Executive sponsor: Prasanna (CTO). Engineering lead: CJ Silverio. PM: Phil + Piyush.

### Concepts (selected by Phil)
1. **Agentic readiness** — "Prepare the codebase, not the developer." Autonomous agent capability is a property of the repository, not the person.
2. **Vibe-driven product development** — PMs and domain experts build functional prototypes that validate ideas before engineering commits. Prototyping separated from production.
3. **Context engineering** — The Karpathy/Anthropic discipline of filling the context window with the right information for the next step. Phil actively practices this.
4. **Cloud cost as product problem** — Separating variable costs (customer-driven, expected) from fixed costs (waste). 99% of spend is one customer (Humana).
5. **PM-as-builder** — Phil's thesis: reinventing the Sr. Director PM role by pairing deep technical product leadership with AI-native building.
6. **Change agency for AI adoption** — The organizational change management dimension of getting PMs and engineers to actually adopt AI tooling. Not the tech — the people side.

### Aspirational project: Clone Phil
A swarm of AI agents backed by the second brain that can answer questions on Phil's behalf in Slack. The wiki becomes the knowledge source agents query to synthesize Phil-like answers. This creates a quality feedback loop: bad agent answers reveal wiki gaps.

This project shapes wiki design — density and cross-referencing quality bar should be "could an agent synthesize a good answer from this content?"

---

## What's NOT migrating
- Shared memory SQLite (`~/dev/shared-memory/`) — stays as-is, separate system
- CLAUDE.md auto-memory — stays as-is
- Context files (`~/dev/context/`) — stays as-is, updated weekly
- Skills (`~/.claude/skills/`) — stays as-is

The wiki is a NEW layer for accumulated knowledge. The existing infrastructure handles operational state and session memory. Different purposes, complementary systems.
