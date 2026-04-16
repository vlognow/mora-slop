# Second Brain — Karpathy-Style LLM Wiki

**A complete reference implementation of the Karpathy LLM Wiki pattern: a personal knowledge wiki maintained by Claude, structured as human-readable markdown, designed to compound in value over time. Built for work. Built to clone its owner.**

---

## What this is

An externalized cognitive system. Plain markdown files in a folder. Claude reads them directly (no RAG), writes to them as it learns, and proposes maintenance. Obsidian provides the human frontend. Semantic search provides navigation at scale. Automation keeps it alive without manual discipline.

The system was bootstrapped in a single afternoon and is designed to grow organically through use — not through migration.

## The Karpathy LLM Wiki pattern in 5 sentences

1. Your knowledge lives as atomic markdown notes on disk — one concept per file, densely cross-referenced.
2. The LLM reads its own index to navigate, then loads full files into context — no RAG, no chunks, no vector retrieval as the primary path.
3. Three operations keep the wiki alive: **ingest** (raw sources become wiki notes), **query** (questions answered from the wiki, synthesis promoted back), and **lint** (weekly maintenance finds orphans, gaps, contradictions).
4. The human does the creative labor (reading, thinking, paraphrasing). The LLM does the clerical labor (indexing, cross-referencing, gap detection). Neither gets bored doing the other's job.
5. The wiki compounds: each new note makes every existing note more valuable because the LLM has more context to synthesize across.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  LAYER 3: SCHEMA                                            │
│  wiki/README.md + CLAUDE.md                                 │
│  The "constitution" — rules for how the wiki is organized,  │
│  how content is cited, how ingest/query/lint tasks behave.  │
│  Edited by the human, read by Claude on every operation.    │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│  LAYER 2: WIKI (the second brain itself)                    │
│  concepts/ entities/ sources/ projects/ areas/ decisions/   │
│  index.md (content catalog) + log.md (operation log)        │
│  Atomic notes, dense cross-references, your voice.          │
│  Written and maintained by Claude; reviewed by you.         │
└─────────────────────────────────────────────────────────────┘
                            ↑
┌─────────────────────────────────────────────────────────────┐
│  LAYER 1: RAW SOURCES (immutable)                           │
│  raw/ — papers, articles, meeting notes, Slack threads      │
│  Imported from outside. Claude reads but never modifies.    │
│  Moved to raw/processed/{date}/ after ingestion.            │
└─────────────────────────────────────────────────────────────┘
```

Two navigation files are **mandatory** (Karpathy's rule):
- `index.md` — content catalog with one-line summaries. The LLM reads this first to decide which files to load.
- `log.md` — append-only chronological log of every operation. The wiki's audit trail.

## Directory map

```
second-brain/
├── README.md                          ← you are here
├── DISCOVERY.md                       ← Phase 0 decisions (10 choices + discovery Q&A)
│
├── proposal/                          ← the documents that drove the bootstrap
│   ├── Work_Karpathy_LLM_Wiki_Second_Brain_Proposal.md   (the 15K-word implementation spec)
│   ├── Second_Brain_Philosophy_and_Technology.pdf          (41-page philosophy + history)
│   └── START_HERE_CLAUDE_PROMPT.txt                        (bootstrap prompt for a fresh session)
│
├── blueprints/                        ← theoretical foundation from the Claude-Blueprints library
│   ├── 02-personal-knowledge-management.md    (PKM deep-dive: Karpathy + Zettelkasten + BASB)
│   ├── 03-claude-agents-memory.md             (memory foundation: 4 types, task patterns)
│   └── reference/
│       ├── karpathy-sources.md                (verified Karpathy quotes + URLs)
│       └── anthropic-context-engineering.md   (Anthropic Sept 2025 guide summary)
│
├── wiki-schema/                       ← the wiki's constitution + session hook + templates
│   ├── README.md                      (the rules: directory structure, writing rules, privacy)
│   ├── CLAUDE.md                      (what Claude reads at session start)
│   └── templates/                     (copy-paste-ready templates for every note type)
│       ├── atomic-note.md
│       ├── entity-note.md
│       ├── source-note.md
│       ├── project-note.md
│       ├── decision-record.md
│       ├── session-entry.md
│       └── map-of-content.md
│
├── code/                              ← working Python scripts
│   ├── wiki_search.py                 (file-level semantic search, SQLite + local embeddings)
│   ├── pkm_ingest.py                  (raw/ folder scanner + processing helper)
│   └── wiki_lint.py                   (orphan/broken-link/stale-note detection)
│
├── skills/                            ← Claude Code skill definitions
│   ├── work-brain-ingest.md           (ingest task: raw/ → atomic notes)
│   ├── work-brain-lint.md             (weekly lint: find issues, compress sessions, regen index)
│   └── daily-digest-wiki-integration.md (wiki status + capture candidates in daily digest)
│
└── automation/                        ← launchd jobs + wrapper script
    ├── ARCHITECTURE.md                (how the automation layer works)
    ├── run-claude-task.sh             (headless Claude execution wrapper)
    └── launchd/
        ├── com.philmora.work-brain.daily-digest.plist    (weekdays 5:03am)
        ├── com.philmora.work-brain.daily-ingest.plist    (weekdays 9:42am)
        └── com.philmora.work-brain.friday-lint.plist     (Fridays 4:07pm)
```

## How the system works day-to-day

### Ingest (when raw/ has content)
You drop a file into `~/work-brain/raw/`. Say "run the ingest task." Claude reads the file, classifies it, extracts concepts and entities, writes source notes, proposes concept/entity notes for your review, moves the raw file to `processed/{date}/`, and updates the index and log.

**Critical rule:** paraphrase, never transcribe. Every note is in your voice. Never quote more than one sentence from a source.

### Query (every Claude session)
Claude reads `index.md` at session start. When you ask a work knowledge question, Claude identifies relevant files from the index, reads them in full (not chunks), synthesizes an answer citing specific files, and proposes promoting the synthesis back into the wiki if it added new connections.

### Lint (Fridays)
Automated via launchd at 4:07pm. Scans all files, finds orphans/broken links/gaps/contradictions/stale notes, compresses the weekly session log, regenerates the index, reindexes embeddings, and posts a report to #claude-phil on Slack.

**Hard rule:** propose, don't act on canonical content. The lint task can regenerate mechanical things (index, session compression). Everything else is a suggestion for your Friday review.

## How to bootstrap your own

1. Read `proposal/Work_Karpathy_LLM_Wiki_Second_Brain_Proposal.md` — the full spec
2. Copy `proposal/START_HERE_CLAUDE_PROMPT.txt` into a fresh Claude Code session
3. Claude walks you through 10 decisions, then scaffolds the wiki
4. Or read `DISCOVERY.md` to see the decisions Phil made and adapt them

The bootstrap takes ~3 hours end-to-end: reading the proposal, making decisions, scaffolding, writing 5-10 seed notes, configuring Obsidian, setting up search and automation.

## Tooling stack

| Component | Choice | Why |
|-----------|--------|-----|
| Wiki location | `~/work-brain/` | Clean path, no cloud sync risk |
| Frontend | Obsidian | Free, markdown-native, graph view, backlinks, no data sent anywhere |
| Version control | Git + private vlognow repo | Full history, backup, team-accessible |
| Semantic search | Local embeddings (all-MiniLM-L6-v2) | File-level, not chunk-level. Zero external API calls. SQLite backend. |
| LLM | Claude Opus 4.6 (1M context) | Reads full files directly. No RAG pipeline. |
| Privacy | Standard tier | Claude API fine, local embeddings, no other external APIs |
| Automation | macOS launchd | Survives reboots, no active session needed |

## The four memory types

Every piece of information in the wiki belongs to exactly one type. Mixing them is how wikis rot.

| Type | What | Where | Lifecycle |
|------|------|-------|-----------|
| **Procedural** | HOW — workflows, decision frameworks, checklists | `concepts/workflows/` | Slow-changing |
| **Semantic** | WHAT — concepts, entities, sources (~80% of wiki) | `concepts/`, `entities/`, `sources/` | Expanding |
| **Episodic** | WHAT HAPPENED — activity log, decisions, retros | `sessions/`, `decisions/`, `retros/` | Append → compress → archive |
| **Working** | CURRENT DRAFTS — half-formed ideas, explorations | `sandbox/` | Transient, freely deleted |

## Relationship to other systems

This wiki is a **new layer** that complements existing infrastructure:

| System | Purpose | Relationship |
|--------|---------|-------------|
| `~/dev/shared-memory/` | Operational cross-session memory (SQLite) | Separate — wiki is knowledge, shared-memory is state |
| `~/.claude/` memory | Auto-memory for Claude Code sessions | May reference wiki, doesn't duplicate it |
| `~/dev/context/` files | Weekly company/project snapshots | Context files are summaries; wiki is deep knowledge |
| `~/.claude/skills/` | Operational skills (pulse, digest, etc.) | Skills may query the wiki. Wiki doesn't contain skill defs. |
| Notion | Team-shared docs, OKRs, strategy | Wiki ingests from Notion via raw/. Notion is team truth; wiki is personal synthesis. |
| Slack | Conversations, decisions | Wiki may ingest threads. Future: agent swarm reads wiki to answer on Phil's behalf. |

## The Clone Phil aspiration

The downstream consumer that shapes every design decision: a swarm of AI agents that answer questions on Phil's behalf in Slack, backed by this wiki.

This means:
- Every note must be self-contained enough for an agent to use without reading 10 other files
- Cross-references must explain *why* two concepts relate, not just that they do
- Entity notes must capture Phil's perspective, not just facts
- The quality bar: **if an agent read only this note and the index, could it give a useful answer?**

Every daily digest flags "Clone Phil gaps" — questions asked in Slack that the wiki can't answer yet. The wiki feeds the agents; bad agent answers reveal wiki gaps; the wiki improves. Compounding.

## Hard rules

1. **Paraphrase, never transcribe.** Write in your voice. Never quote more than one sentence.
2. **Propose, don't act** on canonical content. Mechanical work (index, sessions) is direct.
3. **Privacy is absolute.** No credentials, PII, client-confidential, HIPAA, or colleague performance content.
4. **index.md and log.md are mandatory.** Every operation updates both.
5. **Start small, grow with use.** 5-10 seed notes, not 500.

## Sources and further reading

- **Karpathy's LLM Wiki gist** — gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- **Karpathy on context engineering** — x.com/karpathy/status/1937902205765607626
- **Anthropic: Effective context engineering** — anthropic.com/engineering/effective-context-engineering-for-ai-agents
- **Andy Matuschak's evergreen notes** — notes.andymatuschak.org
- **Obsidian** — obsidian.md

---

*Built April 2026. Phil Mora + Claude Opus 4.6.*
