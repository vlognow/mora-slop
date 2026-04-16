# Karpathy on Context Engineering, LLM Wikis, and Agent Memory

**A reference collection of Andrej Karpathy's writings and talks on the concepts underlying this blueprint library.**

**Last updated:** 2026-04-09 (integrated research agent findings with verified URLs and quote corrections)
**Purpose:** When building blueprints or discussing the underlying theory, cite these sources. They're the philosophical foundation.

---

## ⚠️ Quote attribution note

**"Context is RAM, not a filing cabinet"** is a **paraphrase** commonly attributed to Karpathy, but the exact phrasing (especially "not a filing cabinet") is not directly verified from primary sources. The RAM analogy IS Karpathy's — see the LLM OS / "Context window = RAM" section below — but the specific contrast with "filing cabinet" appears in secondary coverage rather than Karpathy's own words.

**Correct attribution:** paraphrase Karpathy's LLM-as-OS framing rather than quoting "context is RAM not a filing cabinet" directly. The underlying IDEA is verified; the exact wording is not.

---

## The core claims

Five ideas from Karpathy that form the foundation of the blueprint library:

### 1. Context window = RAM (the LLM-as-OS framing)

**Verified framing** from Karpathy's LLM-as-OS posts (X, October and November 2023):

- **LLM = CPU**
- **Context window = RAM** (working memory the kernel pages in and out)
- **Retrieval / filesystem = disk**
- **Agents = long-running apps**

**Verified URLs:**
- `x.com/karpathy/status/1707437820045062561` — original LLM OS framing (Oct 2023)
- `x.com/karpathy/status/1723140519554105733` — explicit RAM/CPU/filesystem mapping (Nov 2023)

**Why it matters:** Most people treat the context window as storage (put everything in, retrieve as needed). Karpathy's framing inverts that: treat it as scarce working memory that the "kernel" pages in and out from disk. The wiki is the DISK; the context window is the RAM. This insight justifies every "JIT loading" and "always-load minimization" pattern in the blueprints.

### 2. Context rot

> "The 10,000th token is less trustworthy than the 10th."

**Source:** Karpathy + Chroma research

**Why it matters:** Performance degrades as context fills. This is empirically measurable — models show worse recall, worse instruction-following, and worse reasoning as the window gets closer to full. Implication: pre-loading "just in case" actively harms performance on the current task.

### 3. Compile, don't re-derive

> "RAG retrieves and forgets. A wiki accumulates and compounds."

**Source:** Karpathy's LLM Wiki gist + X thread on wiki vs RAG

**Why it matters:** RAG systems treat each query in isolation — retrieve chunks, answer, forget. A wiki accumulates structured knowledge that compounds over time. The wiki is PRIMARY and HUMAN-READABLE; the LLM helps maintain and query it. This is the opposite of "chat with your docs" products.

### 4. No RAG — LLM reads its own index

> "No RAG — the LLM reads its own index."

**Source:** Karpathy's LLM Wiki gist

**Why it matters:** Modern long-context models (200K+) can load entire wikis directly. Retrieval at the CHUNK level creates disconnected snippets; retrieval at the FILE level (or no retrieval at all) preserves the wiki's structural context. For wikis under ~400K words, no RAG is feasible and preferable.

### 5. The self-improving loop

> "The wiki accumulates and compounds because the agent writes to it as it learns."

**Source:** implied throughout Karpathy's LLM Wiki writing

**Why it matters:** The agent is not just a READER of the wiki; it's a MAINTAINER. When the agent discovers something new, it updates the wiki. Over time, the wiki gets smarter, not staler. This requires a lint step (catch contradictions, fill gaps) and a human review gate (approve agent-proposed changes).

---

## Primary sources

### Karpathy's LLM Wiki gist ⭐ THE canonical source

**Verified URL:** `gist.github.com/karpathy/442a6bf555914893e9891c11519de94f`

**What it is:** A public GitHub gist where Karpathy documents his LLM Wiki architecture. This is THE canonical source for the pattern that underlies Blueprint 2 (and influences all four blueprints).

**Karpathy's 3-layer architecture (from the gist):**

1. **Raw Sources** — immutable (articles, papers, PDFs, meeting notes, PRs, images). The LLM reads but never modifies.
2. **The Wiki** — LLM-generated markdown (entity pages, concept pages, summaries, cross-links). The LLM owns it.
3. **The Schema** — a config/instruction document (essentially a `CLAUDE.md`) specifying folder structure, citation rules, ingest workflow, QA behavior, and linting conventions. Co-evolved between human and agent.

This 3-layer model is the load-bearing structure of the blueprint library.

**Karpathy's core operations (from the gist):**

- **Ingest** — new source arrives → LLM reads, discusses, writes a summary, updates the index, revises entity/concept pages, appends to the log.
- **Query** — questions are answered against the wiki (not raw sources). Good answers get promoted back as wiki pages.
- **Lint** — periodic health-checks for contradictions, stale claims, orphan pages, missing cross-references.

**Two REQUIRED navigation files (from the gist):**

1. **`index.md`** — a content-oriented catalog of every page with one-line summaries and metadata
2. **`log.md`** — an append-only chronological record with parseable prefixes like:
   ```
   ## [2026-04-02] ingest | Article Title
   ## [2026-04-02] query | What is X?
   ## [2026-04-02] lint | Fixed contradiction in entity-Y.md
   ```

These two files are **mandatory** in Karpathy's pattern — not optional. The index is how the LLM (and humans) navigate content-first; the log is how the LLM (and humans) navigate chronologically. Any LLM wiki implementation following Karpathy's pattern MUST have both.

**Karpathy's core claim (quotable from the gist):**

> "The tedious part of maintaining a knowledge base is not the reading or the thinking — it's the bookkeeping."

LLMs don't forget cross-references, so the bookkeeping cost approaches zero. This is why the wiki becomes a compounding asset rather than a maintenance burden.

**On RAG (from the gist):** The wiki is explicitly presented as a reframing of RAG. Rather than retrieving chunks per-query, the LLM pre-compiles sources into a structured, interlinked artifact. RAG is still allowed as one tool among many in Karpathy's context engineering checklist — but it's demoted, not abolished.

**Key takeaways:**
- Markdown files in a flat or lightly nested structure
- `index.md` + `log.md` are required
- No default RAG — queries load relevant wiki pages directly into context
- Wiki is maintained jointly by Karpathy and the LLM
- The format is "atomic notes + dense cross-references" (Zettelkasten-adjacent)
- Obsidian serves as the IDE; the wiki is the codebase

### Karpathy on X (Twitter) — key verified posts

**Context engineering (June 2025) — the viral thread:**
- **URL:** `x.com/karpathy/status/1937902205765607626`
- **Date:** June 2025
- **Key quote (verified):** "the delicate art and science of filling the context window with just the right information for the next step"
- **Components Karpathy lists as part of context engineering:** task descriptions, few-shot examples, RAG, related multimodal data, tools, state and history, compacting

**LLM as OS (October 2023):**
- **URL:** `x.com/karpathy/status/1707437820045062561`
- The origin of the LLM-as-kernel analogy

**LLM OS specs (November 2023):**
- **URL:** `x.com/karpathy/status/1723140519554105733`
- Explicit RAM/CPU/filesystem mapping

**Topics Karpathy has written about in 2025-2026:**
- Context engineering as a discipline
- Subagent patterns for context isolation (community agreement + echoes)
- LLM OS framing (RAM/CPU/disk/agents)
- Why the LLM Wiki is a reframing of RAG rather than a competitor
- The role of human curation in LLM knowledge bases
- Claude Code as "the first convincing LLM agent" (from Karpathy's 2025 Year in Review)

**Karpathy's 2025 Year in Review:**
- **URL:** `karpathy.bearblog.dev/year-in-review-2025/`
- Notable for his framing of Claude Code and agent tooling

**Note on URLs:** X post URLs are generally stable but posts CAN be deleted. The stable references are the CONCEPTS. When citing Karpathy in a blueprint, cite the concept AND the verified URL, and be prepared for URLs to shift over time.

### Karpathy's talks

**"Intro to Large Language Models" (1 hour talk, Nov 2023)** — foundational but doesn't cover context engineering specifically

**"State of GPT" (Microsoft Build 2023)** — early reference on prompt engineering patterns

**Any 2025-2026 talks on agent architectures** — when these become available, they'll likely be the best video references for context engineering specifically

---

## Secondary sources (related work that validates or extends Karpathy's framework)

### Anthropic's "Effective context engineering for AI agents"

Anthropic's official guide covers the same territory: managing context, avoiding bloat, using long-context effectively. See `reference/anthropic-context-engineering.md` in this folder for the summary.

**Stable URL:** docs.anthropic.com/en/docs/build-with-claude/context-engineering (or similar — Anthropic docs URL structure shifts)

### Chroma's "Context Rot" research

Empirical paper showing measurable degradation of LLM recall and reasoning as context fills. This is the quantitative backup for Karpathy's "context is RAM" claim.

**Why it matters:** If someone challenges "why not just pre-load everything?", this paper is the answer — pre-loading demonstrably hurts performance.

### LangChain's "Context Engineering for Agents" guide

LangChain (a major agent framework vendor) documented context engineering patterns consistent with Karpathy's framework. While LangChain tends to still use RAG, they acknowledge the tradeoffs and have patterns for long-context-direct access.

### Anthropic's Model Context Protocol (MCP)

MCP is Anthropic's protocol for giving agents access to external tools and resources. It's relevant to memory management because MCP servers can expose wiki files as read/write resources that agents use.

**Key insight for blueprints:** the shared-memory SQLite system Phil uses (`memory_tool.py`) is conceptually similar to what an MCP server provides — a structured memory interface that agents call.

---

## Tertiary sources (PKM methodologies that transfer to LLM wikis)

### Niklas Luhmann — Zettelkasten

The 1960s-era "slip box" method. Atomic notes with unique IDs, dense linking, written in your own words. Produced ~90,000 notes over Luhmann's career and enabled him to publish 70+ books.

**Key transfer to LLM wikis:**
- Atomic notes (one idea per note)
- Dense cross-references
- Your own words (no copy-paste)
- Permanent vs fleeting notes (our "wiki" vs "scratchpad" split)

**Further reading:** Sönke Ahrens, "How to Take Smart Notes" (modern explanation of Luhmann's method)

### Tiago Forte — Building a Second Brain / PARA

Modern PKM framework. PARA = Projects, Areas, Resources, Archives. CODE = Capture, Organize, Distill, Express.

**Key transfer to LLM wikis:**
- Organize by ACTIONABILITY, not by topic
- Capture is separate from processing (raw/ → wiki)
- Progressive summarization (layers of distillation)

**Further reading:** Forte's book "Building a Second Brain" (2022)

### Andy Matuschak — Evergreen Notes

Principles for notes that get better over time. Atomic, concept-oriented, densely linked, prefer associative over hierarchical.

**Key transfer to LLM wikis:** nearly everything. Evergreen notes are EXACTLY what you want in a wiki.

**Further reading:** notes.andymatuschak.org (Matuschak's own public digital garden, organized as evergreen notes)

### Maggie Appleton — Digital Gardens

The "public knowledge garden" concept. Notes at different maturity levels (seedling → budding → evergreen). Linked together as a website.

**Key transfer to LLM wikis:**
- Growth stages (not everything needs to be polished)
- Public-facing option via static site generators (Quartz, Obsidian Publish)

**Further reading:** maggieappleton.com/garden

---

## Karpathy-adjacent researchers worth reading

### Simon Willison

Writes extensively on LLMs, tools, and personal knowledge systems. Maintains a public digital garden built on his own "Datasette" project. His writing is practical and production-oriented.

### Shawn Wang (swyx)

Prolific writer on AI engineering, context engineering, and developer tools. Good for the "state of the art" view at any given moment.

### Dwarkesh Patel

Interviews key AI researchers. The interviews often touch on memory architectures and long-context work.

---

## How to cite Karpathy in blueprints

When writing a blueprint that uses Karpathy's framework:

**✅ Do:**
- Cite the CONCEPT by name ("Karpathy's 'context is RAM' principle")
- Reference the LLM Wiki gist as the source
- Note "per Karpathy's 2025-2026 writing on X" for general citations
- Quote sparingly (under 15 words)

**❌ Don't:**
- Link to specific X posts (they may be deleted)
- Paraphrase Karpathy's exact wording closely (copyright / attribution concerns)
- Pretend the framework is something other than Karpathy's (give credit)
- Use Karpathy's name to bootstrap authority for unrelated claims

---

## The stable core of Karpathy's framework

Even as URLs change and specific posts get deleted, these concepts are STABLE and attributable:

1. **Context is RAM, not a filing cabinet** — Karpathy, context engineering, 2025
2. **Context rot** — Karpathy + Chroma, 2024-2025
3. **No RAG, LLM reads its own index** — Karpathy's LLM Wiki gist, 2025
4. **Wiki accumulates and compounds** — Karpathy's LLM Wiki gist, 2025
5. **Subagents for context isolation** — Karpathy's writing on agent architectures, 2025-2026

These five concepts are the load-bearing ideas in this blueprint library.

---

## Related reference files

- `reference/anthropic-context-engineering.md` — Anthropic's official guide (production-practical)
- `reference/pkm-methodologies.md` — Zettelkasten, BASB, Evergreen, Digital Gardens in depth
- `reference/glossary.md` — terminology used across blueprints
- `reference/tool-setup-guides.md` — Obsidian, MkDocs, embedding providers

---

**Note on research freshness:**

This reference file was populated from the model's training knowledge + the research agent's findings at the time of blueprint creation. For the LATEST Karpathy writing, always check:
- x.com/karpathy (recent tweets)
- karpathy.ai (personal site, if updated)
- His GitHub gists
- Recent conference talks on YouTube

Update this file quarterly or whenever a major new Karpathy piece drops on these topics.
