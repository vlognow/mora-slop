# Blueprint 2 — Personal Knowledge Management (PKM)

**The classic Karpathy-style "second brain": a markdown wiki you build and maintain over time for personal research, learning, and reference. The LLM reads it directly (no RAG) and writes to it as it learns.**

**Status:** Theory production-proven in Hughes128. PKM-specific adaptation is Phil's first implementation.
**Last updated:** 2026-04-09
**Prerequisite:** Read `03-claude-agents-memory/README.md` first for the memory foundation

---

## What this blueprint is for

You have 10+ years of accumulated learning scattered across Notion pages, Apple Notes, browser bookmarks, research papers in `~/Downloads`, notes-to-self in text files, and your own memory. You want:

- **One place** where everything important lives
- **Claude-native** — the LLM can read it, search it, update it, and help you think with it
- **Searchable** — both keyword and semantic
- **Browsable** — you can explore it visually, not just query it
- **Compounding** — it gets better over time, not bloated
- **Self-improving** — Claude catches contradictions and fills gaps

This blueprint is how you build that. It's based on Andrej Karpathy's "LLM Wiki" pattern + classical PKM methodologies (Zettelkasten, Building a Second Brain, Evergreen Notes) + production experience from the Hughes128 campaign wiki.

## What this blueprint is NOT for

- **Operational campaign management** — that's Blueprint 1
- **Agent-internal memory architecture** — that's Blueprint 3
- **A specific creative project's knowledge base** — that's Blueprint 4 (Butchsonic)

PKM is specifically for **personal learning and reference**. Research papers you've read. Books you're digesting. Concepts you want to understand. People/ideas/projects you're tracking for your own use, not for production output.

---

## The Karpathy insight

From Karpathy's LLM Wiki gist and his 2025-2026 writing:

> **"The context window is RAM, not a filing cabinet. Every additional token degrades recall on every other token. Find the smallest set of high-signal tokens that maximize the likelihood of the desired outcome."**

> **"RAG retrieves and forgets. A wiki accumulates and compounds."**

> **"Context engineering is the delicate art and science of filling the context window with just the right information for the next step."**

And the radical move that makes his system different from every RAG-based "chat with your docs" approach:

> **"No RAG — the LLM reads its own index."**

Karpathy's wiki is ~100 articles, ~400K words total, pure markdown. When he asks a question, the LLM loads the whole wiki (or the relevant subset) directly into its context window. No embeddings. No vector DB. No similarity search. Just markdown files and long context.

**Why this works:**
- Modern LLMs have 200K-1M context windows. ~400K words fits comfortably in 1M context.
- The LLM is BETTER at synthesizing across documents when it has them all in context than when it gets "top-5 chunks by cosine similarity."
- The wiki structure (explicit cross-references between files, consistent formatting, clear section headers) makes navigation effortless for the LLM.
- Maintaining the wiki is a FEATURE not a bug — the act of curating keeps knowledge fresh.

**Why most "AI knowledge base" products get it wrong:**
- They index everything with embeddings and rely on retrieval
- Retrieval returns disconnected chunks with no structural context
- Users can't read/edit/browse the knowledge directly (everything is opaque vectors)
- The system gets worse over time as stale content accumulates in the vector store

**The LLM Wiki inverts this:** the wiki is PRIMARY and HUMAN-READABLE. The LLM is a tool that helps you maintain it and query it. When you query, the LLM reads the wiki directly.

---

## How PKM methodologies translate to LLM wikis

### Zettelkasten (Niklas Luhmann)

Luhmann's "slip box" method: atomic notes with unique IDs, linked densely, written in your own words.

**What transfers:**
- **Atomic notes** — one idea per file. Keeps files composable.
- **Dense linking** — every file cross-references related files. Creates a graph.
- **Your own words** — don't copy-paste source material; paraphrase in notes.
- **Permanent notes vs fleeting notes** — maps to our "wiki" vs "scratchpads" distinction.

**What doesn't:**
- Unique numerical IDs (Luhmann needed them pre-digital; we use file paths)
- Paper-based sequencing

**Apply to LLM wikis:** each `entities/{name}.md` and `concepts/{topic}.md` is a zettel. Cross-references via file paths. Scratchpads are fleeting notes.

### Building a Second Brain (Tiago Forte) — PARA method

Forte's framework: organize by actionability, not by topic.
- **P**rojects — things with a deadline and outcome
- **A**reas — ongoing responsibilities (health, finances, relationships)
- **R**esources — topics of interest (reference material)
- **A**rchive — inactive items from the above

**What transfers:**
- **Actionability hierarchy** — Projects are hottest; Resources are coldest
- **CODE workflow** — Capture, Organize, Distill, Express
- **Progressive summarization** — highlight the best parts of what you capture

**What doesn't cleanly:**
- The PARA categories don't match LLM wiki memory types 1:1 (PARA is about outcome-orientation; memory types are about lifecycle and purpose)

**Apply to LLM wikis:** you CAN use PARA as a top-level `wiki/` organization:
```
wiki/
├── projects/      ← active projects with deadlines
├── areas/         ← ongoing areas of responsibility
├── resources/     ← reference material (Karpathy-style entities + concepts)
├── archive/       ← retired items
```
But most LLM wikis use memory-type organization instead (rules/entities/sessions) because agents find it easier to navigate. **Hybrid is fine** — PARA at the top level, memory-type organization within each PARA folder.

### Evergreen Notes (Andy Matuschak)

Matuschak's principles for notes that get better over time:
- **Notes should be atomic** — one concept per note
- **Notes should be concept-oriented** — named by the idea, not by the source
- **Notes should be densely linked** — explicit connections to related notes
- **Prefer associative ontologies to hierarchical** — tags over folders
- **Write notes for yourself by default** — clarity over formality

**What transfers:** nearly everything. Matuschak's principles are the gold standard for LLM-ready PKM. An "evergreen note" is exactly what you want in a wiki: atomic, concept-named, densely linked, durable.

**Apply to LLM wikis:** every file in `wiki/` should be an evergreen note. No "notes about chapter 3 of book X" — that's source-oriented. Instead, "the idea-that-chapter-3-is-about.md" — that's concept-oriented.

### Digital Gardens (Maggie Appleton)

Appleton's concept: a personal knowledge garden that's messy in public. Notes at different stages of maturity (seedling → budding → evergreen). Linked together. Published as a website but always "under construction."

**What transfers:**
- **Growth stages** — notes can be rough drafts (seedlings) that mature over time (evergreens)
- **Non-linear** — no table of contents, just entry points and links
- **Public-facing version** — the wiki can ALSO be a public website via MkDocs/Obsidian Publish/Quartz

**Apply to LLM wikis:** if you ever want to publish your wiki as a public digital garden, use a static site generator like Quartz (built specifically for Obsidian vaults) to transform the markdown into a browsable website.

### Progressive summarization (Forte's technique)

When you capture a piece of content (article, paper, book), you summarize it in layers:
- **Layer 1:** Save the raw content
- **Layer 2:** Bold the important parts
- **Layer 3:** Highlight the most important parts of what's bolded
- **Layer 4:** Write an executive summary in your own words
- **Layer 5:** Express/apply the insight

**Apply to LLM wikis:** this is a great workflow for ingest. The raw content lives in `raw/` (Layer 1). The LLM's paraphrased note lives in `notes/{topic}.md` (Layer 2-3). The distilled insight lives in `concepts/{idea}.md` (Layer 4). The application lives in your projects/writing (Layer 5).

---

## The architecture: 3 layers + Obsidian frontend

### Layer 1 — Raw sources (immutable, read-only)

Web articles, research papers, PDFs, book excerpts, conversation transcripts, clipped content. These are IMPORTS from outside the system. You don't edit them in place. The wiki references them but doesn't replace them.

**Where they live:** `wiki/raw/` or `wiki/sources/` — a single folder for all imports, organized by date or topic.

**How they get there:**
1. **Manual drop** — you copy a PDF/markdown/text file into `wiki/raw/`
2. **Browser clipper** — Obsidian Web Clipper or MarkDownload Chrome extension saves a webpage as markdown into `wiki/raw/`
3. **Automated ingest** — a scheduled task (`pkm-ingest`) watches `wiki/raw/` and processes new arrivals

### Layer 2 — The wiki (curated, editable by Claude + you)

The Karpathy layer. Markdown files organized by memory type. Atomic, densely linked, concept-oriented.

**Core subfolders:**
```
wiki/
├── README.md       ← Schema + navigation (the constitution)
├── index.md        ← 🆕 Content catalog (auto-maintained by lint task) [Karpathy-mandated]
├── log.md          ← 🆕 Append-only operation log (ingest/query/lint/edit) [Karpathy-mandated]
├── concepts/       ← atomic notes on ideas (evergreen notes)
│   ├── context-engineering.md
│   ├── progressive-summarization.md
│   └── {one concept per file}.md
├── entities/       ← notes on specific people, organizations, products, places
│   ├── karpathy.md
│   ├── anthropic.md
│   └── {one entity per file}.md
├── projects/       ← active projects you're working on
│   ├── learn-transformers.md
│   └── {project}.md
├── areas/          ← ongoing areas of responsibility (PARA-style)
│   ├── ml-research.md
│   ├── health.md
│   └── {area}.md
├── sources/        ← notes ABOUT specific sources (books, papers, articles)
│   ├── building-a-second-brain.md
│   ├── attention-is-all-you-need.md
│   └── {source}.md
├── MOCs/           ← Maps of Content (hub pages linking related notes)
│   ├── ml-research-MOC.md
│   └── {topic}-MOC.md
├── sessions/       ← episodic log of what you've been doing/learning
│   ├── current-week.md
│   ├── weekly/
│   └── ARCHIVE_pre-{date}.md
└── raw/            ← Layer 1 (imports, not edited in place)
    └── processed/{date}/   ← Items already ingested
```

**⚠️ `index.md` and `log.md` are Karpathy-mandated, not optional.** They live at the ROOT of the wiki. The lint task maintains index.md; all tasks (ingest/query/lint/edit) append to log.md.

### Alternative structure: numbered top-level folders (converged pattern from research)

From the research agent's synthesis of PKM methodologies, there's a converged vault structure pattern worth considering as an alternative:

```
wiki/
├── 00 Meta/              ← README.md, index.md, log.md, schema, templates
├── 10 Projects/          ← active work (PARA — hot)
├── 20 Areas/             ← ongoing responsibilities (PARA — warm)
├── 30 Resources/         ← reference material (PARA — cold)
├── 40 Archive/           ← historical (PARA — frozen)
└── 50 Notes/             ← atomic evergreen notes (Zettelkasten layer)
```

The numbered prefixes give consistent ordering and explicit hot-to-cold structure. This is equivalent to the flat structure above but more PARA-aligned. Pick whichever matches how you think. The blueprints default to the flat concept/entity/project structure because it's simpler and more agent-navigable, but the numbered structure is equally valid.

### Layer 3 — Schema (constitution)

`wiki/README.md` + `~/.claude/CLAUDE.md` — the rules that govern how the wiki is organized, how agents read/write it, and how you interact with it.

---

## 🆕 Two REQUIRED navigation files (from Karpathy's gist)

**Research update 2026-04-09:** Reading Karpathy's actual LLM Wiki gist at `gist.github.com/karpathy/442a6bf555914893e9891c11519de94f` revealed TWO navigation files that are **mandatory** in his pattern but that I initially missed. Add these to every PKM wiki:

### `wiki/index.md` — the content catalog

An auto-maintained index of every page in the wiki, with one-line summaries and metadata. This is how agents (and humans) navigate content-first.

**Structure:**
```markdown
# {Wiki Name} — Index

*Auto-maintained by ingest and lint tasks. Last updated: YYYY-MM-DD*

## Concepts

- [[concepts/context-engineering]] — The discipline of filling the context window
- [[concepts/evergreen-notes]] — Notes that get better over time (Matuschak)
- [[concepts/progressive-summarization]] — Layered distillation technique (Forte)
- ...

## Entities

- [[entities/andrej-karpathy]] — AI researcher, creator of the LLM Wiki pattern
- [[entities/anthropic]] — Creator of Claude, context engineering guide
- [[entities/obsidian]] — Recommended PKM frontend
- ...

## Sources

- [[sources/effective-context-engineering-anthropic]] — Sept 2025, foundational guide
- [[sources/building-a-second-brain]] — Forte, 2022, PARA method
- [[sources/evergreen-notes-matuschak]] — Living document, 5 principles
- ...

## Projects

- [[projects/learn-rust]] — Active, deadline 2026-05
- [[projects/blueprint-library]] — Complete 2026-04-09
- ...
```

The index is regenerated by the lint task (weekly) using Obsidian's Dataview plugin or the `wiki_lint.py` script. Humans rarely edit it by hand.

### `wiki/log.md` — the append-only chronological log

Every operation (ingest, query, lint) that touches the wiki gets a timestamped entry here. Parseable prefixes let agents search the log by operation type.

**Structure:**
```markdown
# {Wiki Name} — Operation Log

*Append-only. Newest entries at the top. Never edit past entries.*

---

## [2026-04-09 14:32] lint | Weekly maintenance
- Compressed 12 session entries into sessions/weekly/2026-W14.md
- Flagged 3 orphan files for review
- Regenerated index.md
- Found 2 broken links (documented in scratchpad for Phil review)

## [2026-04-09 09:15] ingest | Paper: Attention Is All You Need
- Read raw/attention-is-all-you-need.pdf
- Created concepts/attention-mechanism.md (new atomic note)
- Extended concepts/transformer-architecture.md with decoder section
- Created entities/vaswani-et-al.md
- Moved raw file to raw/processed/2026-04-09/

## [2026-04-08 17:42] query | "How does progressive summarization work?"
- Read concepts/progressive-summarization.md
- Read sources/building-a-second-brain.md
- Answered in conversation
- Promoted answer to concepts/progressive-summarization.md "Practical workflow" section

---
```

**Why this matters:** The log is the wiki's audit trail. When you're trying to remember "when did I add that idea?" or "what was the last research I ingested?", the log answers instantly. It's also how the lint task detects patterns (e.g., "concepts/X has been queried 5 times this month but hasn't been extended — consider deepening it").

**Parseable prefixes:** `## [YYYY-MM-DD HH:MM] operation | short-description`

Operations: `ingest` | `query` | `lint` | `edit` | `create` | `retire`

**Automation:** The ingest, lint, and query tasks should all APPEND to `log.md` automatically. Manual edits from you also get logged. The lint task checks weekly that the log is being maintained.

### Obsidian as the frontend

Obsidian is the universal best-in-class frontend for markdown-based PKM. Install it from obsidian.md, point it at your wiki folder as a "vault," and you get:

- **Graph view** — visual map of how notes connect
- **Backlinks pane** — "what references this note"
- **Full-text search** — instant
- **Markdown editing** with live preview
- **Plugins** — Dataview (queries over your notes), Templater (snippets), Omnisearch (semantic search), Canvas (spatial layouts)
- **Link autocompletion** — type `[[` and get suggestions from your vault
- **Tags** — hierarchical, browsable
- **Daily notes** — auto-created templates for journaling

**It's free.** Zero code. Zero cost (there's a paid Sync service but you don't need it).

**Setup is ~5 minutes.** See `obsidian-setup.md` in this blueprint for the exact plugin recommendations.

---

## The 4 memory types, PKM edition

Adapting Blueprint 3's memory types to the PKM use case:

### Procedural memory — HOW TO (for YOU, not for agents)

**Contents:** Workflows, decision frameworks, personal methodologies, "the way I do X." Things you've figured out about how to work, learn, or make decisions.

**Examples:**
- "My decision framework for whether to start a new project"
- "How I process research papers" (a reading workflow)
- "The questions I ask when evaluating a job offer"
- "My weekly review checklist"

**Where:** `wiki/concepts/workflows/` or `wiki/rules/` (personal rules)

### Semantic memory — WHAT I KNOW ABOUT

**Contents:** Atomic notes on concepts, people, organizations, products. The evergreen notes. One file per concept.

**Examples:**
- `wiki/concepts/context-engineering.md`
- `wiki/concepts/emergent-abilities.md`
- `wiki/entities/andrej-karpathy.md`
- `wiki/entities/obsidian.md`

This is the biggest layer. 80% of your wiki will be here.

### Episodic memory — WHAT I'VE DONE / LEARNED

**Contents:** Activity log, what you read, what you built, what you figured out. Chronological.

**Examples:**
- `wiki/sessions/current-week.md` (append-only, compressed weekly)
- Daily notes (if you use Obsidian's Daily Notes plugin)

### Working memory — CURRENT DRAFTS AND EXPLORATIONS

**Contents:** In-progress thinking, half-formed ideas, exploratory writing. The scratchpad.

**Where:** `~/.claude/scratchpads/` (outside the wiki, ephemeral) OR `wiki/sandbox/` if you want a persistent "this isn't ready yet" folder.

**Lifecycle:** Move to canonical wiki files when mature, or delete if not worth keeping.

---

## The ingest pipeline (replacing Karpathy's Clipper)

This is Stage 1+2 of the Karpathy whiteboard diagram. The goal: capture content effortlessly, process it into structured wiki notes automatically.

### The user-facing pattern

```
You drop a PDF/URL/text into wiki/raw/     ← Manual or via Clipper extension
             ↓
The pkm-ingest scheduled task runs         ← Daily at 8 AM (or on demand)
             ↓
Task reads new items in wiki/raw/          ← Classifies each one
             ↓
Task creates/updates wiki notes            ← With source citations back to raw/
             ↓
Task moves processed items                 ← wiki/raw/processed/{date}/
             ↓
Task appends a session log entry            ← "Ingested 3 items: X, Y, Z"
             ↓
You review the new/updated notes            ← Accept or refine
```

### Key design decisions

1. **Nothing gets published to the canonical wiki without your review** — the task CREATES notes but you're expected to review them during your weekly PKM session. This is different from the campaign management blueprint (Blueprint 1) where tasks can publish autonomously.

2. **Classification is LLM-based, not regex** — the task reads each raw item and asks "is this a paper? a book excerpt? a tweet? a blog post?" and routes accordingly. The classification is Claude's judgment call, not a hardcoded taxonomy.

3. **Existing notes get extended, not replaced** — if the task ingests content about "context engineering" and `wiki/concepts/context-engineering.md` already exists, the task APPENDS to it with a new section, citing the new source. It never overwrites existing content.

4. **Raw items are moved, not deleted** — after processing, `wiki/raw/paper-X.pdf` → `wiki/raw/processed/2026-04-09/paper-X.pdf`. You can always trace a wiki note back to its raw source.

### The ingest task SKILL.md

See `file-templates/pkm-ingest-task.md` for the full SKILL.md. Key sections:

```markdown
## GOAL
Process new items in wiki/raw/. For each one:
1. Classify (paper / article / book / tweet / other)
2. Extract key concepts and entities
3. Check if related wiki notes already exist
4. Create new notes or extend existing ones
5. Cite the raw source in every note
6. Move the raw item to wiki/raw/processed/{date}/

## WORKFLOW
### Step 1 — Scan raw/ for new items
ls -la wiki/raw/ (excluding processed/)

### Step 2 — For each item: classify
Read the first ~1000 words. Determine type.

### Step 3 — Extract concepts and entities
For each key idea: is there an existing concept note? If yes, extend it.
If no, create a new atomic note.

### Step 4 — Create/update wiki files
Write notes in the project's evergreen-note style.
Cite the raw source: "*Source: wiki/raw/{filename}*"

### Step 5 — Move raw item
mv wiki/raw/{item} wiki/raw/processed/{date}/

### Step 6 — Append session log
Log which items were processed, which concepts were created/extended.

### Step 7 — Phil-review flag
If any classification was uncertain, add a FLAG FOR PHIL marker.
```

### The manual ingest pattern

If you don't want to set up a scheduled task, the same workflow works manually in a fresh Claude conversation:

```
I just dropped a paper in wiki/raw/attention-is-all-you-need.pdf. Process it:
- Read it
- Extract key concepts
- Create or extend wiki/concepts/ files
- Create or extend wiki/entities/ files
- Cite the source everywhere
- Move the raw file to wiki/raw/processed/2026-04-09/
- Show me what you did
```

Claude will follow the same workflow as the scheduled version.

---

## Semantic search over the wiki

Karpathy's vision is "no RAG — LLM reads directly" and for most queries, that's right. But for large wikis (>200 notes) or for quick lookups, you want semantic search as a complement.

### The pattern

Use SQLite with vector embeddings (via sqlite-vss or LanceDB) to index every wiki file. When you ask a question, the search returns the top 5-10 most relevant files. Then the LLM reads THOSE files (not chunks) directly.

**This is NOT RAG.** It's search-then-read. The retrieval surface is at the FILE level, not the chunk level. The LLM still sees whole files in context. Karpathy would be okay with this pattern — it's just navigation.

### Implementation

See `code-examples/wiki_search.py` for a full working script. Usage:

```bash
# Index all wiki files
python3 wiki_search.py index /path/to/wiki

# Search (keyword)
python3 wiki_search.py search "context engineering"

# Semantic search (embeddings)
python3 wiki_search.py search "context engineering" --semantic

# Re-index after changes (run nightly via cron)
python3 wiki_search.py reindex /path/to/wiki
```

### Embedding providers

You need a vector embedding model. Options:
- **OpenAI** (text-embedding-3-small, ~$0.02/1M tokens) — high quality, low cost, cloud
- **Voyage AI** (voyage-3, ~$0.06/1M tokens) — specialized for retrieval
- **Local via llama-cpp** (e.g., nomic-embed-text) — free, private, requires local inference setup
- **Cohere** (embed-v3, ~$0.10/1M tokens) — good quality, cloud

For a personal wiki of <1000 notes, the cost is negligible regardless of provider — probably <$1/month.

**Recommendation:** start with OpenAI (easiest setup, lowest cost). Switch to local if privacy matters.

---

## The lint pattern (Stage 6 from Karpathy's diagram)

Every wiki rots without maintenance. The lint task is how you fight back.

### What the PKM lint task does

Weekly (e.g., Sunday morning), the `pkm-lint` scheduled task runs and:

1. **Finds inconsistencies** — cross-references notes that reference each other and flags discrepancies
2. **Fills gaps** — identifies concepts mentioned in many notes but without their own dedicated file; proposes creating one
3. **Finds connections** — notices when two notes are semantically related but not linked; proposes adding cross-references
4. **Suggests new topics** — based on what you've been writing about, suggests related concepts you haven't explored
5. **Compresses episodic memory** — moves old session entries to weekly archives
6. **Trims deprecated notes** — flags notes not touched in 90+ days for review (not automatic deletion)
7. **Updates MOCs (Maps of Content)** — refreshes hub pages based on current wiki state
8. **Generates a maintenance report** — summary of changes with Phil-review items

### The lint task SKILL.md

See `file-templates/pkm-lint-task.md` for the full version. Key design:

- **Propose, don't act** for anything that modifies canonical content
- **Act directly** only for mechanical tasks (compressing sessions, updating timestamps, fixing obvious broken links)
- **Always generate a maintenance report** so you can review what happened
- **Run weekly, not daily** — leave enough time between runs to see patterns

### The self-improving loop

Karpathy's diagram has an orange arrow from "Output Formats" back to "Wiki" labeled "self-improving loop." Here's what that means in practice:

1. You generate output from the wiki (an essay, a Marp deck, a chart)
2. During generation, Claude notices gaps: "I want to reference X but there's no note on X"
3. Claude proposes creating the missing note: "Should I create `concepts/X.md`?"
4. You approve (or edit the proposed note)
5. The wiki now has one more note — next time you need X, it's there

The self-improving loop is HUMAN-IN-THE-LOOP. Claude proposes, you approve. Over months, the wiki fills in gaps you didn't know existed.

---

## Output formats: what to do with the wiki

The wiki is the source; outputs are derivatives. Common output patterns:

### 1. Markdown (the native format)

Most of the time, you read the wiki directly in Obsidian. No conversion needed.

### 2. Marp presentations

Marp is a markdown-based slide deck tool. You can convert wiki notes into slide decks with minimal effort.

**Pattern:** in a fresh Claude conversation, say "Generate a Marp slide deck summarizing `wiki/concepts/X.md` and related notes." Claude drafts the Marp markdown; you render it via `marp your-deck.md -o deck.pdf`.

See `file-templates/marp-deck-template.md`.

### 3. Matplotlib charts

For data-oriented notes (stats, timelines, comparisons), Claude can generate matplotlib Python scripts that render charts based on data in the wiki.

### 4. Blog posts / essays

One of the highest-value uses. You've accumulated knowledge in atomic notes; you want to synthesize them into long-form writing. Claude reads the relevant atomic notes and drafts an essay. You refine.

**Pattern:** "Write a 2000-word essay on X, drawing from wiki/concepts/X.md, wiki/concepts/Y.md, wiki/entities/karpathy.md. Use my voice (casual but precise). Cite the wiki notes inline."

### 5. Q&A / conversation

The simplest output. In any Claude conversation, say "Read my wiki at wiki/ and help me think about X." Claude reads the relevant files (via JIT loading) and engages as a thinking partner who has context.

### 6. Public digital garden

If you want to publish parts of your wiki as a public website:
- **Quartz** (quartz.jzhao.xyz) — built specifically for Obsidian vaults, generates a static site
- **Obsidian Publish** (paid, $8/mo) — one-click publishing, handled by Obsidian
- **MkDocs Material** — more developer-oriented, highly customizable

Both Quartz and Publish handle backlinks, graph view, and search for free.

---

## Bootstrap workflow: building a PKM wiki from scratch

### Phase 1 — Pre-flight (10 min)

- Install Obsidian from obsidian.md
- Pick a location for your wiki (recommended: `~/Documents/Brain/` or `~/wiki/`)
- Read Blueprint 3 if you haven't — you need the memory types foundation

### Phase 2 — Directory scaffold (5 min)

```bash
WIKI=~/Documents/Brain
mkdir -p $WIKI/{concepts,entities,projects,areas,sources,MOCs,sessions/weekly,raw/processed,sandbox}
```

### Phase 3 — Write `wiki/README.md` (15 min)

Use the template in `file-templates/pkm-readme-template.md`. Customize the schema description, reading protocol, and directory map.

### Phase 4 — Obsidian setup (10 min)

Open Obsidian → "Open folder as vault" → select your wiki folder.

Install recommended plugins (all free):
- **Dataview** — query over your notes (find all concepts tagged #ml, for example)
- **Templater** — snippets for quickly creating templated notes
- **Omnisearch** — full-text search
- **Graph Analysis** — advanced graph view

Configure:
- Files & Links → "New link format" → "Relative path to file" (so Obsidian links match file paths)
- Editor → "Strict line breaks" → on
- Appearance → pick a theme you like

### Phase 5 — Seed content (1-2 hours)

**Don't try to migrate everything at once.** Instead, seed with 5-10 notes that cover things you're actively thinking about.

Good seeds:
- A concept you want to understand deeply → `concepts/{concept}.md`
- A person whose work you follow → `entities/{person}.md`
- A project you're currently working on → `projects/{project}.md`
- A book you're reading → `sources/{book}.md`
- A workflow you've been refining → `concepts/workflows/{workflow}.md`

Each note should follow the atomic principle: one idea per note, dense cross-references, your own words.

### Phase 6 — Set up the ingest pipeline (30 min)

Option A — Manual ingest (simplest):
- Just drop files into `wiki/raw/` and process them in a Claude conversation when you feel like it

Option B — Scheduled ingest:
- Create `~/.claude/scheduled-tasks/pkm-ingest/SKILL.md` from `file-templates/pkm-ingest-task.md`
- Set a schedule (e.g., daily 8:00 AM)
- Test it manually once to verify

### Phase 7 — Set up the lint task (20 min)

- Create `~/.claude/scheduled-tasks/pkm-lint/SKILL.md` from `file-templates/pkm-lint-task.md`
- Set a schedule (e.g., Sundays 10:00 AM)
- Test it manually once

### Phase 8 — Set up semantic search (1 hour — optional but recommended)

- Install `code-examples/wiki_search.py` to `~/bin/wiki_search.py` or similar
- Configure an embedding provider (OpenAI API key recommended)
- Run initial index: `wiki_search.py index ~/Documents/Brain`
- Add a nightly re-index cron or include it in the lint task

### Phase 9 — Daily/weekly routines

**Daily (5-10 min):**
- When you read something interesting, drop it in `wiki/raw/` or note the URL in a daily note
- When a new concept clicks, write a fresh atomic note
- When you discuss something with Claude, ask Claude to propose wiki updates based on the conversation

**Weekly (20-30 min):**
- Review the lint task's maintenance report
- Review new notes created by the ingest task
- Accept/refine/delete
- Look at the Obsidian graph — what clusters are forming? What notes have no connections (orphans)?
- Write one longer-form synthesis (essay, blog post, draft) that uses the wiki

---

## The two things most people get wrong with PKM

### Mistake 1: Over-organizing before there's content

Spending 2 weeks designing the perfect folder structure before you have any notes. Don't. Start with 5 folders (`concepts/`, `entities/`, `projects/`, `sources/`, `sessions/`) and let organic use reveal what's needed.

### Mistake 2: Copy-pasting source material instead of writing in your own words

The single biggest PKM anti-pattern. You read an article, copy-paste the summary into a note, move on. Six months later you have 500 notes that are just quotations from other people. You can't remember what any of them mean.

**The fix:** every time you capture something, WRITE IT IN YOUR OWN WORDS. Even if it's just "This paper argues that X because Y. I think this is interesting because Z." The act of rephrasing is where learning happens.

This is Luhmann's core insight with Zettelkasten: the notes are valuable because YOU wrote them, not because you captured what someone else wrote.

**LLM implication:** when the ingest pipeline runs, it SHOULD paraphrase and synthesize, not transcribe. The prompt for the ingest task explicitly says "rewrite in your own words, never quote more than one sentence at a time from the raw source."

---

## Files in this blueprint folder

```
02-personal-knowledge-management/
├── README.md                            ← You are here
├── karpathy-framework.md                ← The theory (Karpathy quotes + analysis)
├── architecture.md                      ← 3-layer model + memory types + directory structure
├── obsidian-setup.md                    ← Install + configure + plugins
├── ingest-pipeline.md                   ← Stage 1+2 automation (Clipper replacement)
├── semantic-search.md                   ← wiki_search.py design + embedding providers
├── maintenance.md                       ← Lint task, compaction, evolution
├── pkm-methodologies.md                 ← Zettelkasten, BASB, Evergreen Notes, Digital Gardens
├── output-formats.md                    ← Marp, matplotlib, essays, Q&A, digital garden
├── bootstrap-workflow.md                ← Phase-by-phase from empty folder to working PKM
├── file-templates/
│   ├── pkm-readme-template.md           ← The wiki/README.md starter
│   ├── atomic-note-template.md          ← An evergreen note skeleton
│   ├── entity-note-template.md          ← A note about a specific entity
│   ├── source-note-template.md          ← A note about a book/paper/article
│   ├── MOC-template.md                  ← A Map of Content (hub page)
│   ├── project-note-template.md         ← An active project note
│   ├── daily-note-template.md           ← Daily log template
│   ├── pkm-ingest-task.md               ← The ingest scheduled task SKILL.md
│   ├── pkm-lint-task.md                 ← The lint scheduled task SKILL.md
│   └── marp-deck-template.md            ← Marp slide deck starter
└── code-examples/
    ├── wiki_search.py                    ← Semantic search with SQLite + embeddings
    ├── wiki_lint.py                      ← Standalone lint script
    ├── pkm_ingest.py                     ← Ingest helper (can be called from SKILL.md)
    └── marp_export.py                    ← Convert wiki notes to Marp deck
```

---

## TL;DR

- **PKM = personal learning and reference wiki** (not operational content generation)
- **Karpathy's insight:** no RAG, LLM reads the wiki directly, wiki is primary and human-readable
- **Obsidian is the best frontend** — free, markdown-native, graph view, backlinks, instant search
- **3 layers:** raw sources (imports) / wiki (curated) / schema (constitution)
- **Write in your own words** — the #1 rule of PKM, enforced by the ingest task's paraphrasing requirement
- **Atomic notes + dense cross-references** — Zettelkasten / Evergreen Notes principles
- **Lint weekly** for inconsistencies, gaps, new connections, stale notes
- **Semantic search is file-level, not chunk-level** — search returns files, LLM reads them in full
- **The self-improving loop:** you write, Claude proposes additions, you approve, wiki compounds

Read `karpathy-framework.md` next for the full theoretical foundation, then `architecture.md` for the concrete directory structure, then `bootstrap-workflow.md` when you're ready to build.
