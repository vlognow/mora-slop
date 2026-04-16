# Work Second Brain — Karpathy-Style LLM Wiki Proposal

**Document purpose:** A deep, self-contained proposal for building Phil Mora a Karpathy-style personal knowledge wiki ("second brain") at work, on a different computer than this document was written on. Intended audience: a fresh Claude Code (or Claude Desktop) session running on Phil's work machine, with no access to any of Phil's other files or conversations. Everything required to understand and execute the proposal is inside this single document.

**Date:** 2026-04-09
**Author:** Claude Opus 4.6 (1M context), personal-machine session
**For:** Phil Mora, to share with the work-machine Claude session
**Reading time:** ~45–60 minutes full; ~15 minutes if skimming sections 1, 3, 7, and 10

---

## Document map

1. Executive summary and what Phil wants
2. The Karpathy LLM Wiki pattern — full theoretical foundation
3. Why this pattern is specifically ideal for work knowledge
4. Architecture for the work wiki (three layers + four memory types)
5. Tooling stack — options and recommendations
6. Source ingestion pipeline
7. The three core tasks: ingest, query, lint (with full SKILL.md templates)
8. Bootstrap workflow — phase-by-phase from empty folder
9. File templates (copy-paste ready, inline)
10. Principles, hard rules, and anti-patterns
11. Privacy, compliance, and data-handling for work use
12. Maintenance cadence
13. Options and open decisions Phil must make
14. What the work Claude should do first
15. Sources and references

---

## 1. Executive summary and what Phil wants

Phil has accumulated a decade-plus of professional knowledge that currently lives scattered across: work email, Slack/Teams archives, Notion pages, Google Docs, browser bookmarks, research papers downloaded and then forgotten, meeting notes in various apps, technical documents, his own memory, and the tacit "I'll know it when I see it" knowledge he uses every day to do his job.

He wants a single system where:

- **Everything work-relevant lives in one place** — searchable, browsable, persistent
- **Claude is a first-class citizen** — reads it, writes to it, updates it, helps him think with it
- **The LLM reads the wiki directly** — no vector database, no retrieval pipeline for the primary query path, no "chat with your docs" opacity
- **The wiki compounds over time** — gets better and denser as Phil adds material, instead of rotting the way traditional docs-and-notes systems do
- **Maintenance is near-zero** — the LLM handles the bookkeeping (cross-references, index updates, contradiction detection, gap identification) so Phil's only maintenance job is approving LLM-proposed changes and writing new atomic notes in his own words
- **It works on his work computer with work constraints** — not dependent on his personal infrastructure, compatible with whatever IT policies apply, respecting work data handling requirements

This is the pattern Andrej Karpathy described publicly in his "LLM Wiki" gist and X posts in late 2025 / early 2026. It has been validated by Phil's own Hughes128 campaign implementation. This proposal adapts the pattern for Phil's work context with full implementation detail.

**Outcome:** a working, populated wiki at `~/work-brain/` (or equivalent location) within 1–2 weeks, with automated ingest, weekly lint, and semantic file-level search. Ongoing cost: under $10/month for embeddings. Ongoing time commitment from Phil: ~30 min/week for weekly review plus ad-hoc atomic note writing during normal work.

---

## 2. The Karpathy LLM Wiki pattern — full theoretical foundation

This section exists so the work Claude has the complete theoretical framework in one place. Skip if you already know it, but most Claude instances reading this for the first time benefit from reading it fully.

### 2.1 The core insight: context is working memory, not storage

Karpathy's framing (from his LLM-as-OS posts in late 2023, formalized in his context-engineering writings from June 2025, and most fully expressed in his LLM Wiki gist):

- **LLM = CPU**
- **Context window = RAM** (scarce, fast, paged in on demand)
- **Filesystem = disk** (abundant, slow, the place where things persist)
- **Agents = long-running applications**

The implication: **do not treat the context window as a place to store everything just in case.** The context window is the LLM's working memory for the current task. Fill it with everything only relevant to the current step. The knowledge base lives on disk as markdown files. The LLM loads pages from disk into the context window as needed.

This inverts how most "AI knowledge base" products work. Most products assume the LLM has a small context and needs retrieval augmentation (RAG) — chunk everything, embed everything, cosine-similarity search, dump top-k chunks into the prompt. Karpathy's framing says: long context is here, load whole files instead, and invest in structuring the files so the LLM can navigate them efficiently.

### 2.2 Context rot

Empirically, model performance degrades as the context window fills. The 10,000th token is less trustworthy than the 10th — recall drops, instruction-following weakens, reasoning gets sloppier. This is measurable, and Anthropic, Chroma, and several other groups have published benchmarks confirming it.

**Implication for wiki design:** do not pre-load content "just in case." Load the minimum set of files that maximizes the likelihood of a correct answer on the current query. This is why the Karpathy wiki prefers **just-in-time loading** (read the specific files the query needs) over **pre-loading** (dump the entire wiki into context every time).

### 2.3 No RAG — LLM reads its own index

The radical move that distinguishes the Karpathy pattern from every mainstream "chat with your docs" product:

> "No RAG. The LLM reads its own index."

Modern long-context models can load 200K to 1M tokens. A typical personal wiki — 100 to 500 atomic notes, each a few hundred words — totals 50K to 400K words. This fits comfortably in a 1M-token context window, and fits the top subset in a 200K window.

**Instead of:** embed every chunk, retrieve top-k per query, dump chunks into prompt, hope the model synthesizes across them.

**The Karpathy pattern does:** load the index file (one-line summaries of everything in the wiki), let the LLM decide which full files to read based on the query, load those full files, answer from them. Retrieval happens at the **file level**, not the chunk level, and the LLM does the "retrieval" itself by reading the index and deciding which files are relevant.

This preserves structural context. It keeps the human-readable markdown primary. It makes the whole system debuggable (you can read any file in a text editor and see exactly what the LLM saw).

### 2.4 Compile, don't re-derive

> "RAG retrieves and forgets. A wiki accumulates and compounds."

RAG-based systems treat each query in isolation. Every query re-embeds, re-retrieves, re-synthesizes. Nothing persists. The effort spent on one query doesn't help the next.

A wiki accumulates. When you ingest a source, you don't just store it — you **compile** it into the wiki's existing structure. New concepts get atomic notes. Existing concepts get extended. Cross-references get added. The index updates. The next query benefits from all this structural work.

Over months and years, a wiki becomes a compounding asset: the more material you ingest, the more valuable every future query becomes, because the structural work from past ingestion makes future synthesis faster and more accurate.

### 2.5 The self-improving loop

The wiki is not a static artifact. It is co-maintained between Phil and Claude. The loop:

1. Phil captures a source (paper, article, meeting notes, research doc) into `raw/`
2. Claude reads the source, identifies concepts and entities, and writes or extends wiki pages
3. Phil reviews what Claude wrote and approves, refines, or rejects
4. Over time, Claude notices patterns: gaps where a frequently-referenced concept has no dedicated page, contradictions between old and new notes, orphaned pages that should be linked
5. Claude proposes maintenance actions; Phil approves
6. The wiki becomes better structured, not staler, as it grows

This is the **"lint" step** in Karpathy's pattern. Without linting, wikis rot. With LLM-driven linting, they self-improve.

### 2.6 The three-layer architecture (Karpathy's gist, canonical)

```
┌─────────────────────────────────────────────────────────────┐
│  LAYER 3: SCHEMA                                            │
│  wiki/README.md + CLAUDE.md                                 │
│  The "constitution" — rules for how the wiki is organized,  │
│  how content is cited, how ingest/query/lint tasks behave.  │
│  Edited by Phil, read by Claude on every operation.         │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│  LAYER 2: WIKI (the second brain itself)                    │
│  wiki/concepts/ wiki/entities/ wiki/sources/ wiki/projects/ │
│  wiki/index.md wiki/log.md                                  │
│  Markdown files, atomic notes, dense cross-references.      │
│  Written and maintained by Claude; reviewed by Phil.        │
└─────────────────────────────────────────────────────────────┘
                            ↑
┌─────────────────────────────────────────────────────────────┐
│  LAYER 1: RAW SOURCES (immutable)                           │
│  wiki/raw/                                                  │
│  Papers, articles, meeting notes, clipped web pages, PDFs.  │
│  Imported from outside. Claude reads but never modifies.    │
│  Moved to wiki/raw/processed/{date}/ after ingestion.       │
└─────────────────────────────────────────────────────────────┘
```

**Layer 1 (Raw Sources)** is everything that comes from outside: papers, articles, PDFs, meeting transcripts, clipped webpages, forwarded emails, Slack export JSON. Immutable. The wiki references them but does not modify them.

**Layer 2 (Wiki)** is the curated, LLM-maintained knowledge base. Markdown files. Atomic notes. Dense cross-references. Written in Phil's voice (via Claude paraphrasing the raw sources). One concept per file. One entity per file. Dense cross-linking via `[[wikilinks]]`.

**Layer 3 (Schema)** is the rules. `wiki/README.md` at the root of the wiki describes the directory structure, the citation conventions, the folder purposes, the write rules, and the task instructions. `CLAUDE.md` at the project root hooks this into Claude Code's automatic loading so every session starts with the schema in context.

### 2.7 The two mandatory navigation files

Karpathy's gist makes these two files **non-optional**. They live at the root of the wiki and exist to make the wiki navigable by both humans and LLMs.

#### `wiki/index.md` — the content catalog

A flat, auto-maintained list of every page in the wiki, with one-line summaries. The LLM reads this first when starting to answer a query. Based on the one-line summaries, the LLM decides which full files to read.

Example structure:

```markdown
# Work Brain — Index

*Auto-maintained by lint task. Last updated: 2026-04-09*

## Concepts
- [[concepts/distributed-tracing]] — Observability pattern for microservices
- [[concepts/context-engineering]] — Discipline of filling the LLM context window
- [[concepts/progressive-summarization]] — Layered distillation technique (Forte)
- ...

## Entities
- [[entities/team-observability]] — Internal team owning monitoring tooling
- [[entities/vendor-datadog]] — APM vendor, current contract expires 2027Q1
- ...

## Sources
- [[sources/effective-context-engineering-anthropic]] — Sept 2025 guide
- [[sources/dapper-tracing-paper]] — Google's 2010 tracing paper
- ...

## Projects
- [[projects/q2-platform-migration]] — Active, target 2026-06-30
- [[projects/observability-vendor-evaluation]] — Complete 2026-03-15
- ...
```

The index is the LLM's navigation aid. Queries start by reading the index, not by reading every file.

#### `wiki/log.md` — the append-only chronological log

Every operation that modifies the wiki — ingest, query (if the answer is promoted into the wiki), lint, manual edit, retire — gets a timestamped entry appended to `log.md`. Newest at the top. Never edit past entries. Parseable prefixes so the LLM can search the log by operation type.

Example structure:

```markdown
# Work Brain — Operation Log

*Append-only. Newest entries at the top. Never edit past entries.*

---

## [2026-04-09 14:32] lint | Weekly maintenance
- Compressed 14 session entries into sessions/weekly/2026-W14.md
- Flagged 3 orphan files for review: ...
- Regenerated index.md
- Found 2 broken [[wikilinks]] (listed in scratchpad for review)

## [2026-04-09 09:15] ingest | Paper: Dapper, a Large-Scale Distributed Systems Tracing Infrastructure
- Read raw/dapper-paper.pdf
- Created concepts/distributed-tracing.md (new atomic note)
- Extended concepts/observability.md with tracing subsection
- Created entities/google-research.md
- Created sources/dapper-tracing-paper.md
- Moved raw file to raw/processed/2026-04-09/

## [2026-04-08 17:42] query | "How does context rot affect long agent conversations?"
- Read concepts/context-engineering.md
- Read concepts/context-rot.md
- Read sources/effective-context-engineering-anthropic.md
- Promoted synthesized answer to concepts/context-rot.md "Practical implications" section

---
```

**Why the log matters:** it is the wiki's audit trail. It answers "when did I first learn about X?" instantly. It lets the lint task detect patterns (a concept queried 5 times but never extended is a candidate for deepening). It is also how the next Claude session understands what happened in previous sessions without reading every file.

**Parseable prefix format:** `## [YYYY-MM-DD HH:MM] operation | short-description`

**Operations:** `ingest` | `query` | `lint` | `edit` | `create` | `retire`

### 2.8 Summary of the pattern

- Markdown files on disk, one concept/entity/source per file
- Three layers: raw sources / wiki / schema
- Two mandatory navigation files: `index.md` (content catalog) and `log.md` (operation log)
- Long-context LLM reads files directly (no RAG as the primary path; semantic file-level search as a navigation aid only)
- Atomic notes, dense cross-references, written in your own words
- Co-maintained: Phil writes, Claude extends, Claude proposes, Phil approves
- Self-improving via the weekly lint task
- Obsidian as the visual frontend (free, markdown-native)

---

## 3. Why this pattern is specifically ideal for work knowledge

Work knowledge has five properties that make the Karpathy pattern a near-perfect fit:

### 3.1 It's messy and scattered by default

Work generates knowledge in many formats: meeting notes, Slack threads, email chains, Google/Word docs, research papers, codebases, technical designs, stakeholder conversations, competitive analyses, internal wikis. No single tool holds all of it. A second brain that ingests from all sources and normalizes into one markdown structure fights this entropy.

### 3.2 It's high-churn but high-reuse

The same concepts keep coming back: the same clients, the same technical decisions, the same stakeholders, the same recurring questions. A compounding wiki lets past effort benefit future effort. Every time Phil encounters a topic for the second or third time, the wiki already has a starting point.

### 3.3 It rewards cross-referencing across domains

Work problems span multiple domains — the technical meets the political meets the financial meets the interpersonal. A wiki with dense cross-references surfaces unexpected connections that a flat notes app or a search-based system misses.

### 3.4 It gets evaluated on specific, recurring questions

"What did we decide about X?" "Who owns Y?" "What was the context on Z?" "Has anyone looked at P before?" These are questions the LLM can answer instantly from a well-maintained wiki — and questions Phil currently answers slowly by searching email, asking colleagues, or rediscovering forgotten context.

### 3.5 It has audit and continuity requirements

When Phil changes roles, onboards someone new, or picks up a project after months away, the wiki is the handoff. Traditional note-taking systems are write-only; nobody reads them later. The Karpathy pattern is read-first: the structure is designed for an LLM to navigate, and an LLM is a much better reader than a human skimming folders.

### 3.6 What the pattern is NOT ideal for

Being honest about limits:

- **Not a replacement for shared team wikis** (Notion, Confluence) — those are for collaboration and for content that needs broad review. The Karpathy pattern is for Phil's personal second brain, not a team source of truth.
- **Not a replacement for task management** — this is knowledge, not tasks. Use whatever Phil's team uses for tasks (Jira, Linear, Asana, etc.).
- **Not a dumping ground for sensitive material** — PII, credentials, client confidential information, and regulated data need extra care (see section 11).
- **Not a search engine for work email or Slack** — the wiki ingests relevant material from those sources, but isn't a replacement for full-text email search.

---

## 4. Architecture for the work wiki

### 4.1 Directory structure

Recommended layout for a work brain:

```
~/work-brain/                          ← the wiki root
├── README.md                          ← SCHEMA (the constitution)
├── CLAUDE.md                          ← Claude Code session hook (links to README.md)
├── index.md                           ← MANDATORY content catalog
├── log.md                             ← MANDATORY operation log
│
├── concepts/                          ← atomic notes on ideas (evergreen notes)
│   ├── context-engineering.md
│   ├── distributed-tracing.md
│   └── {one concept per file}.md
│
├── entities/                          ← notes on people, teams, orgs, products, vendors
│   ├── team-{name}.md
│   ├── vendor-{name}.md
│   ├── person-{name}.md
│   └── {one entity per file}.md
│
├── projects/                          ← active work projects
│   ├── q2-platform-migration.md
│   └── {project-slug}.md
│
├── areas/                             ← ongoing areas of responsibility (PARA-style)
│   ├── observability.md
│   ├── team-growth.md
│   └── {area-slug}.md
│
├── sources/                           ← notes about specific sources (papers, books, articles, talks)
│   ├── effective-context-engineering-anthropic.md
│   ├── dapper-tracing-paper.md
│   └── {source-slug}.md
│
├── MOCs/                              ← Maps of Content (hub pages linking related notes)
│   ├── observability-MOC.md
│   ├── team-processes-MOC.md
│   └── {topic}-MOC.md
│
├── sessions/                          ← episodic log of work done/learned
│   ├── current-week.md                ← append-only for the current week
│   ├── weekly/                        ← compressed weekly archives
│   │   ├── 2026-W14.md
│   │   └── 2026-W15.md
│   └── ARCHIVE_pre-{YYYY-MM}.md       ← quarterly consolidation
│
├── decisions/                         ← architectural and major decisions (ADR-style)
│   ├── 2026-03-15-chose-datadog-over-new-relic.md
│   └── {YYYY-MM-DD-slug}.md
│
├── retros/                            ← retrospectives, lessons learned
│   └── {YYYY-MM-DD-project}.md
│
├── sandbox/                           ← in-progress drafts, half-formed ideas
│   └── {anything-in-progress}.md
│
└── raw/                               ← Layer 1 imports, not edited
    ├── {new-drop}.pdf
    ├── {new-drop}.md
    └── processed/
        └── {YYYY-MM-DD}/
            └── {already-ingested}.pdf
```

### 4.2 Why this layout specifically

- **`concepts/`, `entities/`, `sources/`, `projects/`, `areas/`** — directly from the Karpathy/PKM tradition. Each holds a different memory type (see 4.3 below).
- **`decisions/`** — work-specific. Architectural Decision Records (ADRs) are a proven pattern for capturing "why we decided X" with context, alternatives considered, and status. Critical for work continuity.
- **`retros/`** — work-specific. Post-project reflection captures high-density learning that would otherwise be forgotten.
- **`sessions/`** — episodic memory. What Phil actually did this week. Compressed weekly.
- **`sandbox/`** — working memory. Things that aren't ready to be atomic notes yet. Can be deleted freely.
- **`MOCs/`** — Maps of Content. Hub pages that link related atomic notes. Useful for topics big enough to need a landing page.
- **`raw/`** and **`raw/processed/`** — Layer 1 staging. Imports land here; ingestion moves them to `processed/{date}/`.

### 4.3 The four memory types, mapped to work

Every piece of information the wiki holds belongs to exactly one of four memory types. Mixing them is the biggest source of wiki rot.

**Procedural memory — HOW Phil does things at work**
- Workflows, decision frameworks, personal methodologies
- Lives in: `concepts/workflows/` or inline in `concepts/`
- Examples: "My decision framework for accepting a new project," "How I run a retrospective," "My meeting prep checklist"

**Semantic memory — WHAT Phil knows about**
- Atomic concept notes, entity notes, source notes. The biggest bucket.
- Lives in: `concepts/`, `entities/`, `sources/`
- Examples: `concepts/observability.md`, `entities/team-platform.md`, `sources/dapper-paper.md`
- ~80% of the wiki will be here

**Episodic memory — WHAT Phil has done and learned**
- Activity log. What Phil did this week. What he figured out. What went wrong.
- Lives in: `sessions/`, `decisions/`, `retros/`
- Examples: `sessions/current-week.md`, `decisions/2026-03-15-chose-datadog.md`, `retros/2026-Q1-platform-rollout.md`

**Working memory — CURRENT drafts and explorations**
- Half-formed ideas, exploratory writing, in-progress thinking
- Lives in: `sandbox/`
- Deleted freely, moved to canonical files when mature

### 4.4 Always-load vs JIT-load

A working pattern for the wiki is to distinguish files that are **always loaded** at the start of every operation from files that are **just-in-time loaded** when the current task needs them.

**Always-load** (in every Claude Code session via `CLAUDE.md`):
- `wiki/README.md` (the schema)
- `wiki/index.md` (the content catalog — tells Claude what files exist)
- A small set of "hard rules" files if Phil has any

**JIT-load** (the agent reads these when the query implies they're relevant):
- Specific concept files
- Specific entity files
- Specific source files
- Specific project files
- Specific session entries

**Why this matters for context engineering:** the always-load set is the cost Phil pays on every operation. Keep it small (~2-4K tokens max). The JIT-load files are the "paged in from disk" content — loaded only when needed. This keeps the context window efficient.

---

## 5. Tooling stack — options and recommendations

### 5.1 The editor / frontend

**Recommended: Obsidian** (free, obsidian.md)

Why:
- Markdown-native. Zero vendor lock-in. Files are just files in a folder.
- Graph view (visualizes cross-references as a network)
- Backlinks pane (shows what references the current note)
- Full-text search, instant
- Link autocomplete (`[[` triggers suggestions)
- Tags, hierarchical
- Plugin ecosystem (Dataview, Templater, Omnisearch) — all free
- Works on Mac, Windows, Linux, iOS, Android
- No account required; no data sent anywhere

Setup (10 minutes):
1. Download from obsidian.md
2. "Open folder as vault" → point at `~/work-brain/`
3. Install plugins: Dataview, Templater, Omnisearch, Graph Analysis
4. Configure Files & Links → "New link format" → "Relative path to file"

**Alternative 1: Logseq** — block-based instead of file-based, outline-first. Better for journaling and daily notes. Less compatible with the Karpathy "one file per concept" model. Skip unless Phil specifically prefers outlines.

**Alternative 2: Dendron** — VS Code plugin, hierarchy-first. Good if Phil lives in VS Code. More rigid than Obsidian. Worth considering only if the work machine is a VS Code-heavy developer setup and Phil doesn't want a separate app.

**Alternative 3: Plain editor (VS Code, Sublime, Vim)** — works fine. No graph view, no backlinks. Choose this if Phil's work environment prohibits installing new apps.

### 5.2 Where the wiki lives on disk

**Critical decision — depends on what Phil's work IT allows:**

**Option A: Local only** — `~/work-brain/` on the work machine's local disk. Zero cloud. Simplest. No compliance concerns. Downside: no backup unless Phil manually backs up. No sync to phone.

**Option B: Local + Git** — `~/work-brain/` as a Git repository, pushed to a private repo on an approved Git host (GitHub Enterprise, GitLab, etc.). Gives version history, backup, and optional collaboration. Recommended if Phil's work already uses Git and has a private repo option.

**Option C: iCloud / OneDrive / Google Drive sync folder** — `~/Documents/work-brain/` inside a cloud-sync folder. Automatic backup, cross-device sync. Check whether IT policy allows work content in personal cloud.

**Option D: Work-provided cloud storage** — if work provides an approved cloud storage mount, the wiki lives there.

**Recommendation:** Option B (Local + private Git) if possible. Best combination of backup, version history, no cloud data concerns (Git repo can be private and self-hosted), and the ability to work offline.

### 5.3 Semantic file-level search

This is a **navigation aid**, not a replacement for Claude reading files directly. The LLM still reads whole files; semantic search helps identify which files to read for a query against a large wiki.

**Approach:** embed every wiki file (not chunks — whole files). Store embeddings in SQLite or a small local vector DB. When querying, compute a query embedding, find the top-k closest files by cosine similarity, return file paths (not chunks). The LLM then reads those files.

**Embedding provider options:**

| Provider | Cost | Privacy | Quality |
|---|---|---|---|
| OpenAI `text-embedding-3-small` | ~$0.02 per 1M tokens | Cloud | High |
| Voyage AI `voyage-3` | ~$0.06 per 1M tokens | Cloud | Very high (retrieval-specialized) |
| Cohere `embed-v3` | ~$0.10 per 1M tokens | Cloud | High |
| Local via `nomic-embed-text` (llama.cpp) | $0 | Fully local | Medium-high |
| Local via `sentence-transformers` | $0 | Fully local | Medium |

**Recommendation for work:** **local embeddings** via `nomic-embed-text` or `sentence-transformers`. Even though cloud is cheaper, local keeps work content off external APIs. A personal wiki of <1000 notes is small enough that local inference is fast.

**If local is too complex to set up:** OpenAI `text-embedding-3-small` costs pennies per month for this scale, and most work content in a personal wiki is not sensitive enough to rule out external embeddings. But verify with Phil's IT policy.

**Skip semantic search entirely if:** the wiki is under ~100 notes. The index file alone is navigable at that size.

### 5.4 The LLM runtime

Phil will be using Claude Code (or Claude Desktop) on the work machine. The wiki is consumed by whatever Claude instance Phil starts a session with. There is no separate "wiki server" — the wiki is just markdown files, and Claude reads them with the Read tool.

**Model recommendation:** Claude Opus 4.6 with 1M context for heavy synthesis (ingest, weekly lint, long essays). Claude Sonnet 4.6 for lightweight query work (looking up a specific fact). Haiku 4.5 for tasks that don't need model strength.

---

## 6. Source ingestion pipeline

The wiki grows because material flows into it. Ingestion is how that flow happens.

### 6.1 Capture patterns (how content reaches `raw/`)

**Pattern 1 — Manual drop** (simplest, start here)

Phil drops a file into `~/work-brain/raw/`. Any format: PDF, markdown, plain text, HTML export, DOCX, TXT. The file sits there until the next ingest run.

**Pattern 2 — Browser clipper**

Install Obsidian Web Clipper (official) or MarkDownload (Chrome extension). Configure to save clipped articles into `~/work-brain/raw/`. Phil browses, hits Clip, content lands in raw/ as markdown.

**Pattern 3 — Email forwarding**

Set up a filter in work email: forwarded emails from a specific alias (e.g., `brain+save@me.com`) get saved to a mailbox Claude can read. The ingest task processes that mailbox and saves content to `raw/`. Only if work email policy allows.

**Pattern 4 — Meeting notes import**

If Phil uses a meeting notes tool (Granola, Fathom, Otter, Notion AI, etc.), export meeting notes as markdown weekly and drop into `raw/`. The ingest task will process them.

**Pattern 5 — Slack/Teams export**

Work Slack has an export feature (admin controlled). If allowed, periodic exports of starred messages or specific channels can flow into `raw/`. Or lighter-weight: when Phil reads an interesting Slack thread, he copies it into a markdown file and drops it into `raw/`.

**Pattern 6 — Research paper workflow**

When Phil downloads a paper from arXiv, a work reading list, or a vendor blog, he drops the PDF into `raw/`. The ingest task extracts concepts and creates atomic notes + a source note.

**Pattern 7 — Quick voice capture**

For fleeting ideas: voice memo → transcription → markdown file in `raw/`. On macOS, the built-in dictation or a tool like Wispr Flow works. Again, verify work data handling.

### 6.2 The ingest task — what it does with raw/ content

Pseudocode / workflow for the ingest task:

```
1. List new files in ~/work-brain/raw/ (exclude processed/)
2. For each new file:
   a. Read the file (PDF, markdown, text — use appropriate parser)
   b. Classify the content type (paper, article, meeting notes, book excerpt,
      email thread, Slack thread, other)
   c. Extract key concepts and entities mentioned
   d. For each concept:
      - Check if concepts/{concept}.md exists
      - If yes: read it and extend with a new section citing the source
      - If no: create a new atomic note in Phil's voice (paraphrasing, not quoting)
   e. For each entity:
      - Check if entities/{entity}.md exists
      - If yes: read it and add any new facts, citing the source
      - If no: create a new entity note
   f. Create sources/{source-slug}.md — a notes page ABOUT the source itself
      (bibliographic details, one-paragraph summary, key claims, Phil's take)
   g. Move the raw file to raw/processed/{YYYY-MM-DD}/
   h. Append an ingest entry to log.md
   i. Update index.md with any new pages created
3. Generate a summary of what was ingested and flag anything uncertain for
   Phil to review in the next weekly session
```

**Critical rules the ingest task MUST follow:**

1. **Paraphrase, never transcribe.** Write in Phil's voice. Never quote more than one sentence from a raw source. The whole value of PKM comes from rephrasing; transcription is anti-PKM.
2. **Cite everywhere.** Every new fact in a concept note must have a source citation: `*Source: [[sources/{source-slug}]]*`
3. **Extend, don't overwrite.** If a concept note exists, add a new section; do not rewrite existing content.
4. **Flag uncertainty.** If classification is ambiguous, add a `FLAG FOR REVIEW` marker.
5. **Never delete raw sources.** Always move to `processed/{date}/`.
6. **Update the log and index.** Every ingest run updates both files.

### 6.3 The query task — what happens when Phil asks a question

Phil starts a Claude session on the work machine and asks: "What do we know about distributed tracing for the Q2 platform migration?"

Workflow:

```
1. Read wiki/README.md (already in context via CLAUDE.md)
2. Read wiki/index.md to see what concept/entity/project files exist
3. Identify relevant files:
   - concepts/distributed-tracing.md
   - projects/q2-platform-migration.md
   - sources/dapper-tracing-paper.md (mentioned in index)
4. Read those full files into context
5. Synthesize answer
6. Answer Phil's question
7. Ask: "This answer contained synthesis beyond what's currently in the wiki.
   Should I promote it to concepts/distributed-tracing.md as a new section?"
8. If Phil says yes: update the file, append to log.md, update index.md
```

The query task is the self-improving loop in action. Every good answer is a candidate for being written back into the wiki.

### 6.4 The lint task — weekly maintenance

Runs weekly (e.g., Sunday morning, or Friday afternoon as a "close the week" ritual):

```
1. Scan all files in the wiki
2. Find orphan files (not linked from anything, not linking to anything) and flag for review
3. Find broken wikilinks (links to files that no longer exist) and fix or flag
4. Find concepts mentioned many times across files but without their own atomic note — propose creating
5. Find contradictions (two files claiming different facts about the same entity or concept) — flag
6. Find notes untouched for 90+ days — flag for "still relevant?" review
7. Compress sessions/current-week.md into sessions/weekly/YYYY-W##.md and start a fresh current-week
8. Regenerate index.md from current file state
9. Generate a maintenance report: what was done automatically, what needs Phil's review
10. Append a lint entry to log.md
```

**Critical rules the lint task MUST follow:**

1. **Propose, don't act** for anything touching canonical content (concepts, entities, sources, projects). Flag for Phil review.
2. **Act directly** only for mechanical work (compressing sessions, regenerating index.md, fixing obvious broken links).
3. **Always generate a maintenance report** — never run silently.
4. **Weekly, not daily.** Give enough time for patterns to emerge.

---

## 7. Three core tasks — full SKILL.md templates

These are copy-paste-ready task descriptions. If Phil's work setup supports scheduled tasks (e.g., Claude Code's scheduled-tasks feature, cron + CLI, or equivalent), these are the templates. If not, they work as **manual prompts** — Phil starts a Claude session and says "run the ingest task" with the SKILL.md as context.

### 7.1 Ingest task SKILL.md

```markdown
---
name: work-brain-ingest
description: Process new items in ~/work-brain/raw/ into atomic notes, entity notes, and source notes in the work wiki. Non-destructive, always paraphrasing, always citing.
---

# Work Brain — Ingest Task

## GOAL
Process new items in `~/work-brain/raw/`. For each item:
1. Classify the content type (paper / article / meeting notes / book excerpt / email thread / Slack thread / other)
2. Extract key concepts and entities
3. Create or extend wiki notes in Phil's voice, paraphrasing (never transcribing)
4. Cite every new fact with `*Source: [[sources/{source-slug}]]*`
5. Move the raw item to `raw/processed/{YYYY-MM-DD}/`
6. Update `index.md` and `log.md`

## PRE-FLIGHT
- Read `~/work-brain/README.md` (the schema)
- Read `~/work-brain/index.md` to know what files already exist
- List `~/work-brain/raw/` (excluding `processed/`) for new items

## WORKFLOW

### Step 1 — For each new item in raw/

1. Read the item. For PDFs, extract text. For HTML, convert to markdown.
2. Classify the content type. Write the classification in your work notes.
3. Read the first ~2000 words to understand the main arguments and key terms.

### Step 2 — Extract concepts and entities

1. List every concept (abstract idea) mentioned in the source.
2. List every entity (person, organization, product, vendor, team, technology) mentioned.
3. For each, determine if it's significant enough to warrant a wiki note. Rule of thumb: if the concept or entity appears more than twice in the source OR is central to the source's argument, it warrants a note.

### Step 3 — For each significant concept

1. Check if `concepts/{slug}.md` exists (consult `index.md`).
2. If YES:
   - Read the existing file
   - Add a new section (with a `## From [[sources/{source-slug}]]` heading) containing the new content
   - Paraphrase in Phil's voice; do not quote more than one sentence
3. If NO:
   - Create `concepts/{slug}.md` using the atomic note template (see section 9.2)
   - Write in Phil's voice (paraphrased, first-person-plural "we" or impersonal)
   - Include cross-references to related existing concepts

### Step 4 — For each significant entity

1. Check if `entities/{slug}.md` exists.
2. If YES: extend with new facts from this source, citing.
3. If NO: create a new entity note from the template.

### Step 5 — Create the source note

1. Create `sources/{source-slug}.md` for this specific source.
2. Include: bibliographic metadata (author, date, URL/path), one-paragraph summary in Phil's voice, the 3-5 key claims the source makes, Phil's take (or a placeholder for Phil to fill in during review), list of concept and entity notes this source contributed to.

### Step 6 — Move the raw file

1. `mv ~/work-brain/raw/{file} ~/work-brain/raw/processed/{YYYY-MM-DD}/{file}`
2. If the date folder does not exist, create it.

### Step 7 — Update index.md

1. Read `index.md`
2. Add entries for any new concept, entity, source files created
3. Keep entries alphabetical within each section

### Step 8 — Append to log.md

1. Add an entry at the TOP (newest first):
```
## [YYYY-MM-DD HH:MM] ingest | {short description of source}
- Read {raw/{file}}
- Created {N} new atomic notes: {list}
- Extended {N} existing notes: {list}
- Created sources/{source-slug}.md
- Moved raw file to raw/processed/{YYYY-MM-DD}/
```

### Step 9 — Generate ingest report

Produce a summary for Phil:
- What was ingested
- What was created
- What was extended
- Any uncertainty flags (FLAG FOR REVIEW markers)

## HARD RULES
- NEVER quote more than one sentence at a time from a raw source
- NEVER overwrite existing concept/entity content; always extend
- NEVER delete a raw source; always move to processed/
- NEVER create a concept or entity note without a source citation
- NEVER skip the log.md and index.md updates
- PARAPHRASE in Phil's voice, always

## OUTPUT
The final message to Phil should be a concise report:
- N sources processed
- N new concept notes created
- N existing notes extended
- List of anything flagged for review
- Next suggested action (usually "review new notes in next weekly session")
```

### 7.2 Query task (not a scheduled task — a session pattern)

This runs whenever Phil asks a question in a Claude session. It's more of a session protocol than a scheduled task.

```markdown
---
name: work-brain-query
description: How to answer a question using the work wiki: read index first, read relevant files, answer, propose promotion of synthesis back into the wiki.
---

# Work Brain — Query Protocol

## When to use
Whenever Phil asks a question that relates to work knowledge the wiki might contain. The protocol is always the same regardless of whether Phil explicitly says "check the wiki" or not.

## WORKFLOW

### Step 1 — Read the schema and index
- `~/work-brain/README.md` (usually already in context via CLAUDE.md)
- `~/work-brain/index.md`

### Step 2 — Identify relevant files
Based on the query, list the concept/entity/source/project/session files that are most likely relevant. Include files you're only moderately confident about — it's cheap to read a file that turns out not to help.

### Step 3 — Read the files

Read the full files (not chunks). Read as many as the context budget allows. Prioritize concept and source files over session entries.

### Step 4 — Synthesize and answer

Answer Phil's question from the wiki content. Cite the specific files you drew from (`[[concepts/X]]`, `[[sources/Y]]`).

### Step 5 — Propose promotion (if applicable)

If the answer contains synthesis that goes beyond what's in the wiki today — you connected ideas across files, or you filled in context from your own knowledge — ask Phil:

> "My answer connected ideas from [[concepts/X]] and [[sources/Y]] in a way that's not currently captured in either file. Should I promote the connection to [[concepts/X]] as a new section?"

If Phil says yes:
1. Update the relevant file
2. Add the new section with a `## Connection to [[concepts/Y]]` heading
3. Append a `query` entry to log.md

### Step 6 — If the query revealed a gap

If the query revealed that the wiki has no file for a concept that should exist, propose creating one:

> "There's no file for [concept] but it's referenced in [[sources/X]]. Should I create `concepts/{concept}.md`?"

If Phil says yes, create it following the atomic note template.

## HARD RULES
- ALWAYS read index.md first
- ALWAYS cite source files in the answer
- NEVER fabricate facts — if the wiki doesn't have it, say so
- NEVER modify the wiki without Phil's explicit approval
- Promotion of synthesis is a QUESTION, not an action
```

### 7.3 Lint task SKILL.md

```markdown
---
name: work-brain-lint
description: Weekly maintenance of the work wiki. Finds orphans, broken links, gaps, contradictions. Compresses session entries. Regenerates index. Propose-don't-act for canonical content.
---

# Work Brain — Weekly Lint Task

## GOAL
Keep the wiki healthy. Find problems the human wouldn't notice. Propose fixes. Compress volatile content. Regenerate navigation aids.

## SCHEDULE
Once per week. Suggested: Friday afternoon (end of work week) or Sunday morning.

## PRE-FLIGHT
- Read `~/work-brain/README.md`
- Read `~/work-brain/index.md`
- Read `~/work-brain/log.md` (last 2 weeks of entries)

## WORKFLOW

### Step 1 — Inventory
- List every file in the wiki
- Count by category (concepts, entities, sources, projects, areas, sessions, decisions, retros)

### Step 2 — Find orphans
- For each concept/entity file: check if anything links to it (use `grep` or Obsidian's backlink data)
- For each concept/entity file: check if it links to anything
- Files with neither inbound nor outbound links are orphans — FLAG FOR REVIEW

### Step 3 — Find broken wikilinks
- For each `[[wikilink]]` in every file: check the target exists
- If not: either (a) auto-fix if the target clearly moved, or (b) FLAG FOR REVIEW

### Step 4 — Find gap candidates
- Identify concepts mentioned by name in 3+ files that don't have their own concept note
- PROPOSE creating them (don't create automatically)

### Step 5 — Find contradictions
- For each entity, check that different files agree on stable facts
- For each concept, check that different source citations don't contradict each other
- FLAG any contradictions

### Step 6 — Find stale notes
- List files untouched for 90+ days
- FLAG for "still relevant?" review (do not delete automatically)

### Step 7 — Compress sessions
- Read `sessions/current-week.md`
- If the week has ended: summarize into `sessions/weekly/YYYY-W##.md`
- Clear `current-week.md` for the new week (keep the header)

### Step 8 — Regenerate index.md
- Scan all files
- Rebuild the index with one-line summaries per file
- Alphabetize within each section
- Overwrite `index.md` with the new version

### Step 9 — Generate the maintenance report
- What was auto-fixed (compressed sessions, regenerated index, fixed broken links)
- What is FLAGGED for Phil's review (orphans, gap candidates, contradictions, stale notes)
- Suggested actions for Phil's weekly review session

### Step 10 — Append to log.md
```
## [YYYY-MM-DD HH:MM] lint | Weekly maintenance
- Compressed {N} session entries
- Found {N} orphans: {list}
- Found {N} broken links: {fixed N, flagged N}
- Proposed {N} new concept notes: {list}
- Found {N} stale notes: {list}
- Regenerated index.md
```

## HARD RULES
- PROPOSE, don't act, for anything modifying canonical concept/entity/source/project content
- AUTO-ACT only for mechanical tasks: index regen, session compression, obvious broken-link fixes
- ALWAYS generate a report — never silent
- ALWAYS append to log.md

## OUTPUT
A maintenance report saved to `~/work-brain/sandbox/lint-report-{YYYY-MM-DD}.md` that Phil reads during his weekly review session.
```

---

## 8. Bootstrap workflow — phase by phase

This is the step-by-step plan the work Claude should follow to set up the wiki from scratch. It assumes an empty starting state.

### Phase 0 — Discovery (30 minutes)

Before creating anything, the work Claude should understand:

1. **Where does Phil want the wiki to live?** Ask him. Default suggestion: `~/work-brain/`. Alternative: `~/Documents/work-brain/` if cloud sync is desired.
2. **What does Phil's existing work knowledge look like?** Ask him to point to: existing notes app, meeting notes location, research paper downloads folder, any docs he references frequently, any wikis/Notion/Confluence pages he owns.
3. **What tooling constraints exist?** Ask: can he install Obsidian? Can he install Python packages for semantic search? Is external API usage allowed? Is Git usage allowed (for version control)?
4. **What are his top 3 active projects?** Those become the first `projects/` files.
5. **What are 5-10 concepts he thinks about weekly?** Those become the first `concepts/` files.

Record the answers in a `DISCOVERY.md` file in the wiki root. This becomes reference during implementation.

### Phase 1 — Scaffold (10 minutes)

Create the directory structure:

```bash
WIKI=~/work-brain
mkdir -p $WIKI/{concepts,entities,projects,areas,sources,MOCs,decisions,retros,sandbox}
mkdir -p $WIKI/sessions/weekly
mkdir -p $WIKI/raw/processed
```

### Phase 2 — Write the schema (`README.md`) (20 minutes)

Copy the template from section 9.1 of this document. Customize:
- The wiki name
- Phil's role / context (1-2 sentences)
- Any work-specific constraints (data handling, confidentiality)

### Phase 3 — Create the two mandatory navigation files (5 minutes)

**`index.md`:**
```markdown
# Work Brain — Index

*Auto-maintained by lint task. Last updated: {YYYY-MM-DD}*

## Concepts
- (none yet)

## Entities
- (none yet)

## Sources
- (none yet)

## Projects
- (none yet)

## Areas
- (none yet)
```

**`log.md`:**
```markdown
# Work Brain — Operation Log

*Append-only. Newest entries at the top. Never edit past entries.*

---

## [{YYYY-MM-DD HH:MM}] create | Wiki bootstrapped
- Created directory structure
- Wrote README.md (schema)
- Created empty index.md and log.md
- Ready for first ingest / first atomic notes

---
```

### Phase 4 — Seed with 5-10 real notes (1-2 hours)

**Do NOT try to migrate everything at once.** Migration is an anti-pattern for PKM bootstrapping. Instead, seed with material Phil is actively thinking about:

- 3 concept notes (things Phil thinks about weekly)
- 2 entity notes (a key team and a key vendor/product)
- 2 project notes (active projects)
- 1 source note (a recent paper or article Phil found valuable)

Use the templates in section 9 of this document. Write in Phil's voice, paraphrased, with cross-references.

**Why only 5-10 at the start:** the wiki is a tool that only works if Phil uses it. Using it creates a feedback loop where Phil notices what's missing and adds it. Pre-populating 500 notes that Phil never touches creates dead weight.

### Phase 5 — Install and configure Obsidian (10 minutes)

1. Download from obsidian.md
2. "Open folder as vault" → select `~/work-brain/`
3. Install plugins: Dataview, Templater, Omnisearch
4. Configure: Files & Links → relative paths; Editor → strict line breaks on; theme to Phil's preference
5. Verify graph view renders the cross-references

### Phase 6 — Set up the ingest task (30 minutes)

Two options:

**Option A — Manual ingest (start here):**
- Phil drops files into `~/work-brain/raw/`
- Phil starts a Claude session and says "run the ingest task"
- The work Claude reads the SKILL.md in section 7.1 and executes
- Simplest possible setup, no automation

**Option B — Scheduled ingest (after Option A is proven):**
- If Claude Code on the work machine supports scheduled tasks, create a task with the SKILL.md from section 7.1
- Set it to run daily at a Phil-convenient time (e.g., 7 AM)
- Test manually first

Start with Option A. Only upgrade to Option B after Phil has run a manual ingest successfully at least 3 times.

### Phase 7 — Set up the lint task (20 minutes)

Same pattern as ingest: start manual, upgrade to scheduled later.

Manual flow: Friday afternoon, Phil says "run the lint task." Claude reads SKILL.md from section 7.3 and executes.

Scheduled flow: weekly task runs Sunday morning; Phil reads the report on Monday.

### Phase 8 — Optional: semantic search (1 hour)

Only set this up if the wiki grows past ~100 files. Below that, the index alone is enough navigation.

Setup:
1. Write (or copy from Phil's Claude-Blueprints reference if available) a `wiki_search.py` script
2. Configure embedding provider (local recommended for work content)
3. Initial index: `python3 wiki_search.py index ~/work-brain`
4. Wire into the lint task to re-index after every lint run

### Phase 9 — Daily and weekly routines

**Daily (5 minutes):**
- When Phil reads something good, drop it in `raw/` or make a note in `sessions/current-week.md`
- When a concept clicks, write a new atomic note (take 3 minutes to do it right)
- In Claude conversations about work, ask "should any of this become a wiki note?" at the end

**Weekly (20-30 minutes, Friday afternoon or Monday morning):**
- Run the lint task
- Read the maintenance report
- Accept/refine flagged items
- Look at the Obsidian graph — which clusters are forming, what orphans exist
- Consider writing one longer-form synthesis (a short essay, a decision record, a retro) that uses the wiki

### Phase 10 — Stabilize and evaluate (end of week 4)

At the 4-week mark, Phil and the work Claude should evaluate:

- **Is the wiki growing?** Target: 30-50 files by end of week 4.
- **Is Phil actually using it?** If he's not querying it, the setup failed and needs rethinking.
- **Does the ingest task produce notes Phil approves of?** If not, refine the SKILL.md in section 7.1 based on what Phil wishes it did differently.
- **Does the lint report surface useful flags?** If it's noise, tune the thresholds.
- **Is the Obsidian graph showing structure?** If everything is disconnected, the cross-linking discipline needs tightening.

Adjust based on findings. The wiki is a living system, not a finished artifact.

---

## 9. File templates (copy-paste-ready)

These templates are designed so the work Claude can use them directly during bootstrap without needing to fetch anything from this proposal.

### 9.1 `wiki/README.md` — the schema (constitution)

```markdown
# {Phil's Name} Work Brain

**A Karpathy-style LLM wiki for professional knowledge — personal research, learning, and reference for work.**

*Maintained by Phil Mora + Claude*
*Bootstrapped: {YYYY-MM-DD}*

---

## What this wiki is for

Phil's professional knowledge: concepts, entities, sources, projects, decisions, and lessons. A compounding second brain that accumulates learning over time.

## What this wiki is NOT for

- Team-shared source of truth (that's Notion/Confluence/etc.)
- Task management (that's Jira/Linear/etc.)
- Credentials, PII, client confidential data (see Privacy Rules below)
- Work email search (that's the email client)

## Navigation

- **[[index]]** — content catalog of every page, auto-maintained
- **[[log]]** — append-only operation log, newest first

## Directory structure

- `concepts/` — atomic notes on ideas. One concept per file. Evergreen notes.
- `entities/` — notes on people, teams, orgs, products, vendors. One per file.
- `sources/` — notes about specific papers, books, articles, talks.
- `projects/` — active work projects.
- `areas/` — ongoing areas of responsibility.
- `decisions/` — Architectural Decision Records (ADRs) — major decisions with context.
- `retros/` — retrospectives and lessons learned.
- `MOCs/` — Maps of Content (hub pages linking related notes).
- `sessions/` — episodic log of what Phil did and learned, compressed weekly.
- `sandbox/` — in-progress drafts, working memory. Can be deleted freely.
- `raw/` — imported sources awaiting ingestion. Moved to `raw/processed/{date}/` after processing.

## Writing rules (for Claude when maintaining this wiki)

1. **Paraphrase, never transcribe.** Write in Phil's voice. Never quote more than one sentence at a time from a source.
2. **Atomic notes.** One concept per file. If a note is trying to cover two ideas, split it.
3. **Dense cross-references.** Use `[[wikilinks]]` liberally. Every concept note should link to 2-5 related notes.
4. **Cite everywhere.** Every new fact needs `*Source: [[sources/{source-slug}]]*`.
5. **Extend, don't overwrite.** If a concept note exists, add a new section. Never rewrite existing content.
6. **Concept-oriented naming.** File names are the idea, not the source. `concepts/distributed-tracing.md` not `concepts/dapper-paper-summary.md`.
7. **Update index.md and log.md after every operation.**

## Privacy rules

- NO credentials, API keys, passwords, tokens
- NO PII of colleagues, clients, or third parties
- NO client-confidential material
- NO data regulated under HIPAA, GDPR restricted categories, or similar
- Material with ambiguous classification goes in `sandbox/` with a FLAG, not in canonical folders

## Tasks that operate on this wiki

- **Ingest** (manual or scheduled): process `raw/` into atomic notes. See task SKILL.md.
- **Query** (session protocol): read index, read relevant files, answer, propose promotion of synthesis back to wiki.
- **Lint** (weekly): find orphans, broken links, gaps, contradictions; regenerate index.
```

### 9.2 Atomic note template

```markdown
# {Concept Title}

*{One-line summary of the concept in Phil's voice, suitable for the index.}*

---

## What it is

{One or two paragraphs in Phil's own words explaining the concept.}

## Why it matters

{One paragraph on why this concept is worth knowing — what it unlocks, what it prevents, what it connects.}

## Key points

- {Atomic claim #1}  *Source: [[sources/{source-slug}]]*
- {Atomic claim #2}  *Source: [[sources/{source-slug}]]*
- ...

## Related

- [[concepts/{related-concept-1}]] — {brief reason for the link}
- [[concepts/{related-concept-2}]] — {brief reason}
- [[entities/{relevant-entity}]] — {brief reason}

## Sources

- [[sources/{source-slug-1}]]
- [[sources/{source-slug-2}]]

---

*Created: {YYYY-MM-DD}. Last updated: {YYYY-MM-DD}.*
```

### 9.3 Entity note template

```markdown
# {Entity Name}

*{One-line description — who/what they are, suitable for the index.}*

---

## Overview

{One paragraph. What is this entity, what do they do, why does Phil care.}

## Facts

- **Type:** person | team | organization | vendor | product | team-internal | ...
- **Primary contact / reference:** ...
- **Status:** active | inactive | retired | ...
- **Phil's relationship:** ...

## History

{Chronological notes on interactions, decisions, events involving this entity.}

- **{YYYY-MM-DD}** — {event}  *Source: [[sources/{slug}]]*
- **{YYYY-MM-DD}** — {event}

## Related

- [[concepts/{concept}]] — {why}
- [[projects/{project}]] — {why}
- [[entities/{other-entity}]] — {relationship}

## Sources

- [[sources/{slug}]]

---

*Created: {YYYY-MM-DD}. Last updated: {YYYY-MM-DD}.*
```

### 9.4 Source note template

```markdown
# {Source Title}

*{One-line summary of the source in Phil's voice, suitable for the index.}*

---

## Bibliographic

- **Type:** paper | article | book | talk | blog post | meeting notes | ...
- **Author(s):** ...
- **Published:** ...
- **URL / location:** ... *(link to raw/processed/{date}/{filename} if imported)*
- **Ingested:** {YYYY-MM-DD}

## One-paragraph summary (in Phil's voice)

{Paraphrase the source's main argument in 3-5 sentences. Do not quote.}

## Key claims

1. {Claim #1 from the source}
2. {Claim #2}
3. {Claim #3}
4. ...

## Phil's take

{Phil fills this in during weekly review. Can start empty.}

## Wiki notes this source contributed to

- [[concepts/{concept-1}]]
- [[concepts/{concept-2}]]
- [[entities/{entity}]]

## Related sources

- [[sources/{related-source}]] — {why}

---

*Created: {YYYY-MM-DD}.*
```

### 9.5 Project note template

```markdown
# {Project Name}

*{One-line status — what it is, current state, suitable for the index.}*

---

## Status

- **Phase:** discovery | planning | in-progress | wrapping-up | done | archived
- **Target date:** {YYYY-MM-DD} or "ongoing"
- **Stakeholders:** [[entities/{name}]], [[entities/{name}]]
- **Last update:** {YYYY-MM-DD}

## Goal

{One paragraph on what success looks like for this project.}

## Current state

{What's happening right now. What's blocked. What's next.}

## Decisions

- [[decisions/{YYYY-MM-DD-slug}]] — {one-line summary}
- [[decisions/{YYYY-MM-DD-slug}]] — {one-line summary}

## Key concepts

- [[concepts/{concept}]] — {why relevant to this project}

## Related sources

- [[sources/{source}]] — {why}

## Log

- **{YYYY-MM-DD}** — {event}
- **{YYYY-MM-DD}** — {event}

---

*Created: {YYYY-MM-DD}. Last updated: {YYYY-MM-DD}.*
```

### 9.6 Decision record template (ADR-style)

```markdown
# {YYYY-MM-DD} — {Decision Title}

*{One-line: what was decided.}*

---

## Status

Proposed | Accepted | Superseded by [[decisions/{other}]] | Deprecated

## Context

{What was the situation that required a decision? What were the forces at play? What did we know, and what didn't we know?}

## Decision

{What did we decide to do? State it in one or two sentences.}

## Alternatives considered

1. **{Alternative A}** — {brief description, why rejected}
2. **{Alternative B}** — {brief description, why rejected}
3. **{Alternative C}** — {brief description, why rejected}

## Consequences

- **Positive:** {what this unlocks}
- **Negative:** {what this costs, what it closes off}
- **Neutral:** {what changes but isn't strictly better or worse}

## Related

- [[concepts/{concept}]]
- [[projects/{project}]]
- [[sources/{source}]] — {if a source influenced the decision}

---

*Recorded: {YYYY-MM-DD}.*
```

### 9.7 Daily session entry (append to `sessions/current-week.md`)

```markdown
## {YYYY-MM-DD} ({day of week})

### What I did
- ...
- ...

### What I learned
- ...

### What I'm thinking about
- ...

### Notes to add to the wiki later
- {concept/entity/source to capture}

---
```

### 9.8 MOC (Map of Content) template

```markdown
# {Topic} — Map of Content

*{One-line: what this MOC covers, suitable for the index.}*

---

## What this MOC covers

{One paragraph on the topic and why it deserves a hub page.}

## Core concepts

- [[concepts/{concept-1}]] — {one-line relevance}
- [[concepts/{concept-2}]] — {one-line relevance}
- [[concepts/{concept-3}]] — {one-line relevance}

## Key entities

- [[entities/{entity-1}]] — {one-line relevance}

## Key sources

- [[sources/{source-1}]] — {one-line relevance}

## Active projects in this area

- [[projects/{project-1}]] — {one-line status}

## Decisions affecting this area

- [[decisions/{decision}]]

## Open questions

- {questions Phil wants to explore in this area}

---

*Created: {YYYY-MM-DD}. Last updated: {YYYY-MM-DD}.*
```

---

## 10. Principles, hard rules, and anti-patterns

### 10.1 Principles

1. **Atomic notes, one idea per file.** If a note is about two things, split it.
2. **Concept-oriented naming.** File names describe the idea, not the source. `concepts/distributed-tracing.md` — not `concepts/dapper-paper.md`.
3. **Dense cross-references.** Every note should link to 2-5 others. Isolated notes are worthless.
4. **Write in Phil's own words.** The whole value of PKM is paraphrasing. Copy-paste is the enemy.
5. **Cite everything.** Every fact has a source. Sources live in `sources/`.
6. **Progressive elaboration.** Start a concept note small; extend it every time new material touches the concept.
7. **Promote synthesis.** When a query produces a good connection, promote the connection back into the wiki.
8. **The wiki evolves with use.** Don't over-design the structure upfront. Start with 5 folders and let patterns emerge.

### 10.2 Hard rules

1. **`index.md` and `log.md` are mandatory.** Every operation updates both.
2. **`raw/` is immutable.** Never edit a raw source in place. Always move to `raw/processed/{date}/` after ingestion.
3. **`concepts/`, `entities/`, `sources/`, `projects/` are sacred.** Only the ingest task or explicit Phil-approved updates modify them.
4. **Never quote more than one sentence at a time** from a raw source.
5. **Never delete anything canonical without Phil's explicit approval.** The lint task can flag stale notes, but only Phil retires them.
6. **Privacy rules are hard rules.** No credentials, PII, or client-confidential material in the wiki (see section 11).

### 10.3 Anti-patterns (things to NOT do)

**Anti-pattern 1: Over-organizing before there's content.** Spending a week designing the perfect folder structure before any notes exist. Start with the structure in section 4.1 and let use reveal what else is needed.

**Anti-pattern 2: Copy-pasting source material.** You read an article, paste the summary into a note, move on. Six months later you have 500 notes that are quotes from other people. You've learned nothing. The fix: every capture gets rewritten in your own words. Even if it's just "This paper argues X because Y. I think this matters because Z."

**Anti-pattern 3: Source-oriented note naming.** `concepts/dapper-paper.md` is a source note, not a concept note. It belongs in `sources/`. The concept in the paper is `concepts/distributed-tracing.md`.

**Anti-pattern 4: Giant uber-notes.** A single `concepts/observability.md` that tries to cover everything about observability. Split it into `concepts/distributed-tracing.md`, `concepts/metrics-vs-logs.md`, `concepts/sampling-strategies.md`, etc. Keep `concepts/observability.md` as a MOC that links them.

**Anti-pattern 5: Letting the wiki become a personal journal.** The wiki is for knowledge, not for venting or emotion-processing. Keep those in a separate journal (not the wiki). The wiki's "session" entries are behavioral ("what I did, what I learned"), not emotional.

**Anti-pattern 6: Ignoring the lint task reports.** The lint task only creates value if Phil actually reads its flags and acts on them. Schedule the weekly review. Don't skip it.

**Anti-pattern 7: Treating `index.md` as a manually-edited file.** The index is auto-generated by the lint task. Don't hand-edit it except in emergencies.

**Anti-pattern 8: RAG-ifying the wiki.** Some implementations chunk every file, embed every chunk, and do RAG over the wiki. This defeats the entire Karpathy pattern. Use file-level semantic search (whole files returned, not chunks) or no retrieval at all (LLM reads the index).

---

## 11. Privacy, compliance, and data-handling for work use

This section is specifically important because the wiki is going on a work machine with work content. Phil should review this section carefully and the work Claude should honor it as constraints.

### 11.1 What the wiki MUST NOT contain

- **Credentials:** passwords, API keys, SSH keys, tokens, certificates, service account keys
- **Personal identifiers:** Social Security numbers, passport numbers, driver's license numbers, dates of birth for identification purposes
- **Financial account details:** account numbers, routing numbers, credit card numbers (even redacted — don't keep them)
- **Health data:** anything that would be PHI under HIPAA for anyone, including Phil
- **Client confidential material:** anything under NDA, anything customer-specific the customer has not agreed to be used this way
- **Regulated data:** anything under GDPR special categories, PCI data, export-controlled material
- **Performance review content about colleagues**
- **Anything Phil's manager, legal, or HR would object to being in a personal knowledge system**

### 11.2 Handling rules for ambiguous content

When the work Claude is ingesting content and encounters something that might be sensitive:

1. **Default to caution.** If in doubt, do not ingest into canonical folders.
2. **Use `sandbox/` as a quarantine.** Put uncertain material in `sandbox/` with a `FLAG FOR REVIEW` marker.
3. **Ask Phil.** In the ingest report, explicitly list anything ambiguous and ask Phil whether it belongs in the wiki.
4. **When ingesting, redact.** If a source contains one sensitive item mixed with otherwise fine content, the note can still be created but the sensitive item is redacted or referenced only as "{redacted}" with a note of where the full context exists.

### 11.3 Where the wiki lives matters

- **On the work machine's local disk only:** safest. No cloud, no sync, nothing external.
- **On a private Git repo:** acceptable if the Git host is work-approved (GitHub Enterprise, internal GitLab, etc.).
- **On personal cloud storage (iCloud, Dropbox, Google Drive personal):** check IT policy. Many work data policies prohibit this.
- **On work-approved cloud storage:** best if the work already provides a compliant cloud mount.

### 11.4 External API usage

The wiki itself is just files. But operations on it may call external APIs:

- **Claude model calls** — these send context to Anthropic's API. Fine for non-sensitive content under Anthropic's standard data handling; verify whether Phil's work has a zero-retention agreement with Anthropic or uses a Claude deployment that keeps data in a specific region.
- **Embedding API calls** — sends wiki content to an external embedding provider. Avoid for sensitive content. Prefer local embeddings.
- **Web search** — fine; outbound only.

### 11.5 Backup strategy

- **If the wiki is on Git:** the Git repo is the backup. Push regularly.
- **If the wiki is local-only:** set up Time Machine (Mac) or equivalent backup.
- **Never skip backup.** A year of PKM work lost is a genuine loss.

### 11.6 Exit strategy

Because the wiki is plain markdown in a folder, there is no lock-in. If Phil leaves this employer, the wiki is portable. But: if any content would be considered employer property (e.g., material derived from confidential sources), Phil should consult HR/legal before taking the wiki. A safer default: at job exit, archive the work wiki separately and start a new one at the new job. Knowledge that is portable (concepts Phil learned, entities that aren't employer-proprietary) can be manually migrated.

---

## 12. Maintenance cadence

### 12.1 Daily (5-10 min)

- Drop new sources into `raw/` as they come in
- Add brief entries to `sessions/current-week.md` at end of day: "what I did, what I learned, what I'm thinking about"
- When a concept clicks, write a new atomic note (3-5 min to do it right)

### 12.2 Weekly (20-30 min, Friday afternoon or Monday morning)

- Run the ingest task (if manual) to process whatever landed in `raw/` during the week
- Run the lint task
- Read the lint report
- Act on flagged items: approve or refine proposed concept notes, resolve contradictions, review stale notes, fix broken links
- Browse the Obsidian graph view for 5 minutes — look for unexpected connections
- Write one longer-form synthesis if inspired (short essay, retro, decision record)

### 12.3 Monthly (30-45 min)

- Review `projects/` files — are any done and ready to move to `archive/`?
- Review `areas/` files — are they reflecting current responsibilities or stale?
- Look at `log.md` — what have the last 4 weeks of operations looked like? Patterns?
- Consider whether to create new MOCs for topics that have grown past 10-15 related notes

### 12.4 Quarterly (1-2 hours)

- Review the wiki structure — is it still serving Phil's workflow, or has the structure diverged from his actual use?
- Prune or archive projects that are done
- Consider writing a longer-form quarterly synthesis (themes Phil explored, big decisions, what he learned)
- Make sure backups are working

---

## 13. Options and open decisions Phil must make

The work Claude should walk through these with Phil at the start of the bootstrap workflow. No defaults — these are Phil's calls.

1. **Wiki location:** `~/work-brain/` (recommended) vs another path vs a sync folder
2. **Frontend:** Obsidian (recommended) vs Logseq vs Dendron vs plain editor
3. **Version control:** Git (recommended) vs local-only vs cloud sync
4. **Embedding provider:** Local (recommended for work content) vs OpenAI vs Voyage vs Cohere vs none
5. **Ingest task mode:** Manual (recommended to start) vs scheduled
6. **Lint cadence:** Weekly Friday (recommended) vs weekly Sunday vs biweekly
7. **Privacy tier:** Strict (no external APIs at all) vs standard (Anthropic API + local embeddings) vs permissive (external APIs allowed)
8. **Scope of what belongs in the wiki:** all work knowledge vs specific domains only vs excluding meeting notes vs including
9. **Sharing:** personal only (recommended) vs shareable with team members via read-only export
10. **Seeding strategy:** bootstrap with 5-10 fresh notes (recommended) vs migrate existing notes from elsewhere vs both

---

## 14. What the work Claude should do first

If you are the Claude session running on Phil's work machine reading this document:

### Step 1 — Confirm scope with Phil
Do not start building without explicit go-ahead. Ask:
- "Have you read this proposal end to end?"
- "Which options in section 13 do you want me to default to?"
- "Where should the wiki live on this machine?"
- "What are the 3 concepts and 2 entities you want me to seed it with?"

### Step 2 — Verify tooling availability
Check:
- Is Python 3 available? (`python3 --version`)
- Is Git available? (`git --version`)
- Is Obsidian installable on this machine? (or is there an alternative Phil prefers)
- What file system access does Claude have? (read/write to `~/`, or restricted)

### Step 3 — Read the full document once more
Re-read sections 2, 4, 7, 9, 11 carefully. Section 2 for the philosophy. Section 4 for the architecture. Section 7 for the tasks. Section 9 for the templates. Section 11 for the privacy rules.

### Step 4 — Follow the bootstrap workflow from section 8
Phase 0 through Phase 4 in order. Do not skip Phase 0 (discovery). Do not skip Phase 3 (the two mandatory navigation files — if you skip these, the wiki is not Karpathy-pattern compliant).

### Step 5 — Seed with Phil's input, not your own choices
The 5-10 seed notes should reflect what Phil actually thinks about, not what you think would be good examples. Ask him directly.

### Step 6 — Do the first ingest and lint runs manually
Before setting up any scheduled tasks, run the ingest and lint workflows manually end-to-end at least twice. Verify the output matches what Phil expects. Tune the SKILL.md templates in section 7 based on what you learn.

### Step 7 — Report back
At the end of Phase 4, write a short summary for Phil:
- What was created
- What is in the wiki now
- What the open questions are
- What Phil should do first in his weekly routine

### Step 8 — Set up the maintenance cadence
Once Phil has confirmed the wiki works for him, set up (or schedule) the weekly lint and daily session routines.

### Step 9 — Save progress
Log everything to `~/work-brain/log.md` as you go. Future Claude sessions will read this log to understand what happened.

---

## 15. Sources and further reading

### Karpathy's primary writings
- [Karpathy's LLM Wiki gist (the canonical source)](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) — the architecture, the 3-layer model, the index/log requirements
- [Karpathy on X — LLM-as-OS framing (October 2023)](https://x.com/karpathy/status/1707437820045062561) — origin of the RAM/CPU/filesystem analogy
- [Karpathy on X — context engineering (June 2025)](https://x.com/karpathy/status/1937902205765607626) — "the delicate art and science of filling the context window with just the right information for the next step"
- [Karpathy's 2025 Year in Review](https://karpathy.bearblog.dev/year-in-review-2025/) — broader context on his LLM usage shift

### Independent coverage of Karpathy's LLM Wiki
- [VentureBeat: Karpathy shares LLM Knowledge Base architecture that bypasses RAG](https://venturebeat.com/data/karpathy-shares-llm-knowledge-base-architecture-that-bypasses-rag-with-an)
- [MindStudio: What Is Andrej Karpathy's LLM Wiki? How to Build a Personal Knowledge Base With Claude Code](https://www.mindstudio.ai/blog/andrej-karpathy-llm-wiki-knowledge-base-claude-code)
- [Medium (Neural Notions): Karpathy is using AI to build a second brain instead of writing code](https://medium.com/neuralnotions/andrej-karpathy-stopped-using-ai-to-write-code-hes-using-it-to-build-a-second-brain-instead-cddceadc5df5)
- [Analytics Vidhya: LLM Wiki Revolution](https://www.analyticsvidhya.com/blog/2026/04/llm-wiki-by-andrej-karpathy/)
- [Codersera: Karpathy's LLM Knowledge Base — Build an AI Second Brain](https://ghost.codersera.com/blog/karpathy-llm-knowledge-base-second-brain/)
- [DAIR.AI: LLM Knowledge Bases](https://academy.dair.ai/blog/llm-knowledge-bases-karpathy)

### Anthropic context engineering (foundational for any Claude-backed wiki)
- [Anthropic: Effective context engineering for AI agents (Sept 2025)](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) — the practical guide to filling the context window well
- [Anthropic Engineering Hub](https://www.anthropic.com/engineering) — collection of Anthropic engineering writeups including context engineering, managed agents, and more

### Reference implementations
- [GitHub: kfchou/wiki-skills](https://github.com/kfchou/wiki-skills) — LLM-maintained personal wiki skills for Claude Code, implements Karpathy's pattern
- [GitHub: Astro-Han/karpathy-llm-wiki](https://github.com/Astro-Han/karpathy-llm-wiki) — a single skill for building a Karpathy-style LLM wiki
- [GitHub: ussumant/llm-wiki-compiler](https://github.com/ussumant/llm-wiki-compiler) — Claude Code plugin that compiles markdown knowledge files into a topic-based wiki

### PKM methodology sources
- **Niklas Luhmann — Zettelkasten** — the foundational personal knowledge system. Atomic notes, unique IDs, dense linking. Translates cleanly to markdown+wikilinks.
- **Tiago Forte — Building a Second Brain / PARA method** — organization by actionability (Projects / Areas / Resources / Archive). PARA top-level categories are a valid alternative organization scheme.
- **Andy Matuschak — Evergreen Notes** — the principles: atomic, concept-oriented, densely linked, written for yourself, associative over hierarchical. These principles ARE the Karpathy wiki's quality bar. See andymatuschak.org.
- **Maggie Appleton — Digital Gardens** — notes at different maturity stages (seedling/budding/evergreen), non-linear, always-under-construction. Optional extension if Phil ever wants to publish parts of the wiki.

### Tooling
- [Obsidian](https://obsidian.md) — the recommended frontend, free, markdown-native
- [Quartz](https://quartz.jzhao.xyz) — static site generator built specifically for Obsidian vaults (if Phil ever wants to publish)
- [nomic-embed-text](https://github.com/nomic-ai/contrastors) — local embedding model for semantic search

---

## Final note to the work Claude session reading this

This proposal is long because it is meant to be complete on its own. You do not need to search for anything, fetch anything, or guess at anything. Everything you need to bootstrap a working Karpathy-style LLM wiki for Phil's work knowledge is in this document.

The three most important things to remember:

1. **The wiki is primary; the LLM is the maintainer.** You write to it, Phil reviews. You do not replace Phil's judgment. You propose; he approves.

2. **Paraphrase, don't transcribe.** This is the rule that separates a PKM wiki from a notes dump. Enforce it strictly during ingestion.

3. **Start small, grow with use.** Bootstrap with 5-10 real notes. Do not migrate everything at once. Let the wiki grow at the speed of Phil's actual use.

Ask Phil the questions in section 13. Do Phase 0 discovery. Then follow the bootstrap workflow. Report back at the end of Phase 4.

Good luck. A strong second brain compounds over years. The Karpathy pattern is the best current design for making that compounding actually happen with LLM help.

---

*End of document. Last updated 2026-04-09.*
