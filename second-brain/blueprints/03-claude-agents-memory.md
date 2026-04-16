# Blueprint 3 — Claude Agents Memory Management

**The meta-pattern for how Claude Code agents (scheduled tasks, subagents, conversations) manage their own knowledge, context, and memory across runs.**

**Status:** Production-tested (Hughes128 uses every pattern in this blueprint daily)
**Last updated:** 2026-04-09
**Prerequisites:** None — this is the foundation blueprint
**Read this first** if you're new to Claude Code agent memory

---

## Why this blueprint exists

When you build anything with Claude Code that runs more than once, you hit the same problems:

1. **Agents re-derive facts** that were established in earlier conversations. Wasted work, drift between versions.
2. **Context windows fill with low-signal tokens** because prompts try to pre-load "just in case." Performance degrades. Recall suffers ("context rot").
3. **Agents forget learnings** between sessions. Every scheduled task run starts fresh.
4. **Multiple tasks duplicate the same context inline** in their SKILL.md files. Drift accumulates. Updating one rule requires editing N files.
5. **Subagents spawned from a parent conversation either get too much context (bloat) or too little (miss the point).**
6. **The user tries to fix it by dumping everything into `CLAUDE.md`** which then becomes a 2000-line mess that every session reloads.

This blueprint is the playbook for solving those problems. It's based on Andrej Karpathy's "context is RAM not a filing cabinet" framework, Anthropic's official context engineering guidance, and ~6 months of production experience running the Hughes128 campaign on Claude Code.

---

## The core insight

> **An agent's memory should be a graph of files on disk that the agent reads on demand and writes to as it learns. Not inline prompt content. Not system prompts. Not conversation history.**

Memory lives in **files**. Files are **read on demand** based on the current task's needs (just-in-time loading, not pre-loading). Files are **written back to** as the agent discovers new facts. Files are **organized by memory type** so each has a clear lifecycle and purpose.

This is the fundamental pattern. Everything in this blueprint elaborates on it.

---

## The 4 memory types (the Karpathy taxonomy)

Every piece of information an agent might need belongs to exactly one of these categories. The biggest source of rot is mixing them.

### 1. Procedural memory — HOW to do things

**Contents:** Rules, protocols, workflows, hard constraints, how-to procedures.

**Examples:**
- "Every Facebook post must have an image attached"
- "When posting to X, use ClipboardEvent paste not execCommand"
- "Never invent facts; always cite a primary source"
- "Hard time budget: 5 minutes per Facebook post"

**Lifecycle:** Slow-changing. Updates when the user corrects a behavior or when a tool's behavior changes. Revised but rarely deleted.

**Storage:** `wiki/rules/` directory as markdown files.

**Read by:** Every task that performs the relevant workflow. The "always-load" set for most tasks includes `rules/hard-rules.md` at minimum.

### 2. Semantic memory — facts about WHO and WHAT

**Contents:** People, organizations, documents, places, products, opponents, allies. Things with proper names that get referenced repeatedly.

**Examples:**
- "Mark Gillen — incumbent in PA 128th. Bio claims Act 48 Certified Teacher."
- "Docket 25-13317 — Hughes v. Exeter Township et al., Judge Gavin, 10 defendants."
- "Rex Titan — 55yo, 6'4", 285 lbs, lampshade mustache, blue eyes." (Butchsonic)

**Lifecycle:** Updated when new facts are discovered (research, public records, user correction). Rarely deleted, usually expanded.

**Storage:** `wiki/entities/` directory, one file per entity.

**Read by:** Tasks that generate content mentioning the entity. Usually JIT-loaded (only when the entity is referenced), not always-load.

### 3. Episodic memory — what HAPPENED

**Contents:** Log of what the agent did, what was found, what worked, what failed. The diary of the project.

**Examples:**
- "2026-04-09 AM | post-morning | Posted PT-2, GI-1, DC-7 across all 3 platforms. FB timeline verified. Runtime 32 min."
- "Graphics archived: graphic_zero_laws.png (hit 3/3 lifetime cap)"

**Lifecycle:** Append-only short-term (7 days), then compressed weekly, then archived. Never deleted.

**Storage:** `wiki/sessions/current-week.md` + `wiki/sessions/weekly/YYYY-WNN.md` + archives.

**Read by:** Tasks that need recent context (last 5 entries for freshness rules, last week for pattern detection). Never load the full history — that's the archive's job.

### 4. Working memory — the SCRATCHPAD

**Contents:** Per-run, ephemeral notes. Drafts in progress. Intermediate results. Step-by-step work logs during a single task execution.

**Examples:**
- "Post 1 draft: [text]. Graphic: stat_callout.png"
- "Intel scan results: no Gillen content overnight"
- "Chrome crash on post 2 — retrying"

**Lifecycle:** Created at task start, written during the task, sometimes referenced by the next task in the chain (e.g., engage-morning reads what post-morning drafted), then **auto-cleaned after 7 days** by the lint task.

**Storage:** `~/.claude/scratchpads/{task-name}-{YYYY-MM-DD}.md` — **NOT inside the wiki** (ephemeral, not canonical).

**Read by:** The task writing it, and sometimes the next task in a chain. Not read by later tasks.

---

## Why mixing memory types creates rot

**Real example from Hughes128:** Before the wiki migration, every scheduled task SKILL.md had:
- Hard rules inlined (procedural)
- Facts about Ted Gardella inlined (semantic)
- Last session's learnings inlined (episodic)
- Step-by-step workflow notes inlined (working)

When the Gardella threat description needed updating, it had to be edited in 4 different task files. Inevitably they drifted. `morning-social-posts` had a 2-paragraph Gardella description; `facebook-comment-moderation` had a different 3-paragraph version; `social-media-engagement-am` had the old version without the March 28 attack.

**The fix:** Separate files, one canonical source each. `rules/hard-rules.md` is the ONE place hard rules live. `entities/ted-gardella.md` is the ONE place Gardella facts live. `sessions/current-week.md` is the ONE place recent activity lives. Updating one file updates everything that references it.

**This is Karpathy's "compile, don't re-derive" principle.** Compile each fact once into a canonical file; reference from many places.

---

## The wiki as agent memory

The wiki is the agent's long-term memory. It lives on disk as markdown files. Agents read it on demand and write to it as they learn.

```
project-root/
└── wiki/
    ├── README.md                    ← The schema: how the wiki is organized.
    │                                  The first file every agent reads.
    ├── rules/                       ← PROCEDURAL memory
    │   ├── hard-rules.md              (always-load for most tasks)
    │   ├── voice-and-phrases.md
    │   ├── {protocol}-protocol.md     (JIT-load when relevant)
    │   └── {policy}-policy.md
    ├── entities/                    ← SEMANTIC memory
    │   ├── {person-or-org}.md         (JIT-load only when referenced)
    │   ├── {document}.md
    │   └── {entity}.md
    ├── content-strategy/            ← OPTIONAL: structured operational data
    │   ├── {tracker}.json             (machine-readable)
    │   └── {strategy}.md              (human-readable)
    ├── sessions/                    ← EPISODIC memory
    │   ├── current-week.md            (always-load, last 5 entries)
    │   ├── weekly/                    (compressed — never loaded by tasks)
    │   │   └── YYYY-WNN.md
    │   └── ARCHIVE_pre-{date}.md      (frozen history)
    └── scratchpads/                 ← OPTIONAL pointer to ~/.claude/scratchpads/
        └── README.md
```

Plus separately:

```
~/.claude/
├── CLAUDE.md                        ← GLOBAL schema (cross-project rules)
├── scratchpads/                     ← WORKING memory (all projects share)
│   └── {task}-{date}.md
├── shared-memory/                   ← CROSS-SESSION SQLite store
│   ├── memory.db
│   └── memory_tool.py               ← CLI tool for read/write
└── scheduled-tasks/
    └── {task-name}/
        └── SKILL.md                 ← Task prompts (reference the wiki)
```

---

## The scheduled task pattern

This is the production pattern used by Hughes128. Every scheduled task follows this structure:

### Task SKILL.md skeleton

```markdown
---
name: {task-name}
description: {one-line purpose}
---

@@model claude-sonnet-4-6

## GOAL

{What this task does. Focus on OUTPUT, not process. 2-3 sentences.}

**This task is {SCOPE}-ONLY.** Things out of scope:
- ❌ {thing-that-another-task-does}

## WIKI — READ THESE FIRST (PARALLEL — single message)

**IMPORTANT:** Issue all N file reads as parallel Read tool calls in a SINGLE message.
Do NOT read sequentially.

1. `/full/path/to/wiki/README.md`
2. `/full/path/to/wiki/rules/hard-rules.md`
3. ... (other always-load files)

## WIKI — READ JIT (only if relevant to this run)

- `wiki/entities/{entity}.md` — read ONLY if {trigger condition}
- `wiki/rules/{protocol}.md` — read immediately before {step that needs it}

## SCRATCHPAD

Write working notes to: `~/.claude/scratchpads/{task-name}-{YYYY-MM-DD}.md`
Track: {what to include}

## SHARED MEMORY

Before: `python3 ~/.claude/shared-memory/memory_tool.py context --project {slug}`
After: `python3 ~/.claude/shared-memory/memory_tool.py log --actor {task} --action complete --details '<JSON>'`

## WORKFLOW

### Step 1 — {action} (N min)
{concrete instructions}

### Step 2 — {action} (N min)
{concrete instructions}

### Step N — Update session log
Append to `wiki/sessions/current-week.md`:
```
## [YYYY-MM-DD] | {task-name}
{structured fields}
---
```

## ESCALATION

If {failure mode}, fire HIGH PRIORITY shared-memory alert (don't silently skip).

## CONSTRAINT — STAY IN SCOPE

List of things this task MUST NOT do. Anything out-of-scope goes to scratchpad
with a `FLAG FOR {other-task}:` header.

## PRIME DIRECTIVE

One sentence on the most important thing.
```

**Why this structure works:**
- **Always-load list is explicit and bounded** — you can measure the pre-load token count
- **JIT list explains WHEN to read each file** — agents don't over-load
- **Parallel reads instruction** is prominent — saves 10x on startup time
- **Scope constraints are explicit** — prevents scope creep (the biggest source of task bloat)
- **Escalation rule is explicit** — prevents silent failures
- **Session log format is standardized** — enables downstream analysis

---

## When to use subagents

Subagents are Claude sessions spawned from a parent session that execute a specific subtask and return results. They are THE primary mechanism for context isolation.

### Use a subagent when:

1. **The subtask produces a lot of tool-result context the parent doesn't need.** Example: searching the codebase for a specific function. The search might return 50K tokens of file content, but the parent only needs the 200-token answer. Dispatching to a subagent means the parent context only grows by 200 tokens.

2. **The subtask is exploratory and might have false starts.** Example: "research this person". The research might go down 3 dead ends before finding the answer. Those dead ends pollute the parent context. Subagents give you "findings only, no process."

3. **The subtask is genuinely parallelizable.** Example: "for each of these 10 entities, gather current status from 5 websites each." Each entity can be a subagent running in parallel.

4. **The subtask has different tool needs than the parent.** Example: the parent is a posting task that uses Chrome MCP; the subagent is a research task that uses WebSearch + WebFetch. Separating them keeps the parent's approved-tools list minimal.

### DON'T use a subagent when:

1. **The subtask is small and cheap.** A 2-tool-call lookup doesn't need a subagent.
2. **The subagent would need almost all the parent's context to do its job.** Then you're just paying the round-trip cost without isolation benefit.
3. **The user is actively participating.** Subagents can't ask the user questions (no AskUserQuestion tool). Use them for headless work only.

### Subagent dispatch pattern

```
Agent tool call:
subagent_type: general-purpose
description: "Research person X"
prompt: |
  Thorough briefing. Tell the subagent everything it needs:
  - Who you're working for and why
  - What's been tried
  - What format you want the result in
  - What to do when information is missing vs when to fabricate
  - Specific sources to check
  - Length target for the response
```

**The biggest subagent mistake:** under-briefing. A subagent with a 1-sentence prompt produces shallow work. A subagent with a 500-word briefing produces deep work. You can afford a long briefing because the subagent's output is compressed anyway.

---

## The 4 canonical context operations (LangChain framework)

Beyond the memory TYPES, there's a framework for the OPERATIONS an agent performs on context. LangChain's "Context Engineering for Agents" guide (blog.langchain.com/context-engineering-for-agents) distilled four canonical operations that every agent does, explicitly or implicitly:

### 1. WRITE — persist context outside the window

When an agent learns something it'll need later, it WRITES it to an external store so the context window doesn't have to keep carrying it.

**In this blueprint:**
- Writing to `wiki/sessions/current-week.md` at the end of a task
- Writing to `wiki/entities/{name}.md` when discovering a new fact
- Writing to `~/.claude/scratchpads/{task}-{date}.md` during a run
- Writing to `~/.claude/shared-memory/` via `memory_tool.py log`

### 2. SELECT — pull the right pieces into the window

When the agent needs information, it SELECTS the relevant pieces from external stores and loads them into context. This is the opposite of "pre-load everything."

**In this blueprint:**
- JIT reading of entity files (only when the entity is referenced)
- Reading the last 5 entries of current-week.md for freshness rules (not the full log)
- `memory_tool.py context --project {slug}` — returns only the project-relevant subset
- `wiki_search.py` semantic search returns top-5 files, not the whole wiki

### 3. COMPRESS — summarize or prune to fit

When context is filling up or the agent needs to hand off to another step, it COMPRESSES — summarizing old content, pruning stale tool results, keeping only what matters for the next step.

**In this blueprint:**
- Weekly lint task compresses old session entries into weekly summaries
- Session log format is structured (short fields, not prose) to minimize tokens
- Blog-writer drafts are saved to scratchpad, not carried forward in main context
- Subagents return 1,000-2,000 token summaries instead of raw tool results

### 4. ISOLATE — partition context across sub-agents

When a subtask has its own context needs that don't overlap with the parent, it ISOLATES — runs in a separate session with its own context window, returns only the result.

**In this blueprint:**
- Subagents for research, exploration, verbose tool outputs
- Separate scheduled tasks for different responsibilities (posting vs engagement vs moderation)
- Each task SKILL.md has a "STAY IN SCOPE" constraint that enforces isolation
- Cross-task communication via scratchpad `**FLAG FOR {other-task}:**` headers

### The mnemonic: W-S-C-I

Write → Select → Compress → Isolate. Four operations. Every context engineering decision maps to one of them.

When debugging agent memory problems, diagnose which operation is failing:
- Losing information → Write is insufficient (not persisting to disk)
- Over-loading → Select is too broad (pre-loading instead of JIT)
- Running out of space → Compress is too weak (not summarizing old content)
- Parent context polluted → Isolate is missing (should be a subagent)

**Source:** LangChain, "Context Engineering for Agents" — blog.langchain.com/context-engineering-for-agents/

---

## Context engineering: writing prompts that use memory well

This is the craft. Here are the specific patterns.

### Pattern 1: The always-load / JIT split

Every task prompt has two sections:
- **READ THESE FIRST** (always-load, parallel)
- **READ JIT** (on-demand, with explicit trigger conditions)

Move to JIT anything that doesn't meet "every run of this task needs this file."

**Rule of thumb:** If you're not sure, move to JIT. The agent can always load more; it can't unload.

### Pattern 2: Parallel file reads at startup

```markdown
## WIKI — READ THESE FIRST (PARALLEL — single message)

**IMPORTANT:** Issue all N file reads as parallel Read tool calls in a SINGLE
message. Do NOT read sequentially — parallel reads are ~10x faster.
```

This phrasing has been tested and reliably sticks. Without it, agents default to sequential reads and you lose 12-24 seconds on every task startup.

### Pattern 3: Explicit escalation rules

```markdown
## ESCALATION

If you cannot {target}, you MUST:
1. Append a `**⚠️ MISSED TARGET:**` block to the session log
2. Fire a HIGH PRIORITY shared-memory alert:
   python3 ~/.claude/shared-memory/memory_tool.py add \
     --name "HIGH PRIORITY: ..." --type project --project {slug}
3. **NEVER silently skip.** Failure is acceptable; silence is not.
```

Without explicit escalation rules, agents silently skip steps under time pressure. The user only discovers later (or never).

### Pattern 4: Explicit scope constraints (STAY IN SCOPE)

```markdown
## CONSTRAINT — STAY IN SCOPE

This is a POSTING-ONLY task. You MUST NOT:
- ❌ Reply to comments (that's {other-task})
- ❌ Run analytics (that's {other-task})
- ❌ Modify entity files (that's the lint task)

If something out-of-scope needs to happen, save it to scratchpad with a
**FLAG FOR {other-task}:** header. The other task picks it up.
```

Without explicit scope, bundled tasks cascade-fail. When posting hits an issue, engagement gets cut. Separate tasks by responsibility, enforce with explicit constraints.

### Pattern 5: Verification steps, not just action steps

```markdown
### Step 8 — VERIFY ON THE TIMELINE (MANDATORY)

After posting, force-navigate to the profile and confirm the post appears with
the CORRECT text AND the CORRECT image. Never assume "modal closed" = "post
succeeded."
```

LLMs over-trust intermediate success signals (modal closed, button clicked, response was 200). Force verification at the end-state level (the thing you wanted actually exists).

### Pattern 6: Content-type-aware rules

When a rule has exceptions based on context, encode the exceptions in a table:

```markdown
| Content type | Can use X? | Framing |
|---|---|---|
| Long-form article | ✅ | "{long framing}" |
| Short-form social | ❌ | "{alternative framing}" |
| Paid ad | ⚠️ Phil decides | "{safe framing}" |
| Defensive response | ❌ | Pivot to {alternative} |
```

Tables are easier for agents to parse than prose exceptions. When in doubt, table the rule.

### Pattern 7: Source citations for every claim

Entity files should cite primary sources for every fact:

```markdown
- ✅ **{Fact}**. *Source: Docket 25-13317 paragraph 69* (or URL, or document ID)
- ⚠️ **{Fact}**. *Reported by Phil 2026-04-08 — pending verification*
- ❌ **{Fact}**. *INTERNAL ONLY — not for public content*
```

Three-tier verification: ✅ verified, ⚠️ unverified, ❌ do-not-publish. Without tiers, agents treat hearsay as fact and publish it.

---

## Context budget: measuring and optimizing

Every task has a context cost. Measure it.

### The 4 sources of pre-load context

For each task, the pre-load context (what fills the window BEFORE the task does any work) consists of:

1. **System prompt** — fixed by the harness, ~2-3K tokens
2. **SKILL.md body** — the task prompt itself, 1-3K tokens
3. **Always-load wiki files** — the biggest variable, 5-50K tokens
4. **Shared-memory context dump** — 1-3K tokens if using memory_tool.py

Plus what accumulates during the task:

5. **Tool result history** — grows during the run, 10-100K tokens
6. **Reasoning tokens** — depends on model + task complexity

### Measurement script

```bash
#!/bin/bash
# Save as ~/.claude/measure-task-context.sh

TASK_DIR="$1"
SKILL_FILE="$HOME/.claude/scheduled-tasks/$TASK_DIR/SKILL.md"

if [ ! -f "$SKILL_FILE" ]; then
  echo "Task not found: $TASK_DIR"
  exit 1
fi

echo "=== $TASK_DIR pre-load context ==="
echo ""

SKILL_CHARS=$(wc -c < "$SKILL_FILE" | tr -d ' ')
SKILL_TOKENS=$((SKILL_CHARS / 4))
echo "SKILL.md: ${SKILL_CHARS} chars (~${SKILL_TOKENS} tokens)"
echo ""

echo "Always-load wiki files:"
TOTAL=0
grep -oE '/(Users|home)/[^ )"`]+\.(md|json)' "$SKILL_FILE" | sort -u | while read path; do
  if [ -f "$path" ]; then
    chars=$(wc -c < "$path" | tr -d ' ')
    tokens=$((chars / 4))
    rel=$(echo "$path" | sed 's|.*/wiki/||')
    printf "  %-50s %7s chars  ~%6s tokens\n" "$rel" "$chars" "$tokens"
  fi
done
```

Run this after building each task. Compare to budget targets.

### Budget targets

| Task type | Pre-load budget (tokens) |
|---|---|
| Tiny / no-op (warmup, reminders) | <500 |
| Lightweight (moderation, monitoring) | 2-5K |
| Standard (mechanical work + light creative) | 10-25K |
| Heavy (creative + multi-source) | 25-40K |
| Synthesis (combine many sources) | 40-60K |
| Maximum before performance degrades | 60K |

**Beyond 60K, recall suffers measurably.** This is "context rot" in practice.

### The 4 optimization levers (in priority order)

1. **Move files to JIT** (biggest win) — if a file is only needed in some runs, move it out of always-load
2. **Split bloated trackers into active/archive** — see the Hughes128 graphic-usage.json split (9.7K → 1.6K tokens by moving retired+pending to archive)
3. **Compress entity files** — move long histories to a separate `{entity}-history.md` file that's JIT-loaded only when history is needed
4. **Switch from Opus to Sonnet** — doesn't reduce tokens but 2-3x speedup on reasoning steps

**Before optimization (Hughes128 campaign-morning, 2026-04-08):** 40,931 tokens pre-load
**After 4 quick wins:** 24,329 tokens (~41% reduction)
**Estimated runtime savings:** ~5-8 minutes per run

---

## The shared-memory SQLite system

Hughes128 uses a SQLite-backed memory system for cross-session learning. The memory_tool.py CLI provides read/write + semantic search.

### Schema

```sql
CREATE TABLE memories (
    id TEXT PRIMARY KEY,           -- unique slug (e.g., "feedback-no-scalese-2026-04-09")
    name TEXT NOT NULL,            -- human-readable title
    type TEXT NOT NULL,            -- feedback | project | reference | learning | session
    project TEXT,                  -- hughes128 | butchsonic | philmora | system (cross-project)
    content TEXT NOT NULL,         -- the actual memory content (markdown)
    source TEXT,                   -- how this memory was created (task:X, chat, research)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    embedding BLOB                 -- optional: vector embedding for semantic search
);

CREATE INDEX idx_project ON memories(project);
CREATE INDEX idx_type ON memories(type);
CREATE INDEX idx_updated ON memories(updated_at);
```

### Memory types

| Type | Purpose | Lifecycle |
|---|---|---|
| **feedback** | User corrections and rules that apply across sessions. "Never mention X", "Always phrase Y as Z". | Persistent. Rarely deleted. |
| **project** | Status snapshots, milestones, current state of a specific project. | Updated as project evolves. |
| **reference** | Stable facts, URLs, account IDs, external system pointers. | Persistent. Updated if external system changes. |
| **learning** | Patterns the agent or user discovered. "When I did X it had unintended effect Y." | Persistent. Promoted from scratchpad observations. |
| **session** | Task run outputs. What happened in a specific session. | Short-term. Archived or deleted after compression. |

### CLI tool API

```bash
# Context dump (pulled at task start)
python3 ~/.claude/shared-memory/memory_tool.py context --project {slug}

# Full-text search
python3 ~/.claude/shared-memory/memory_tool.py search "keyword" --project {slug}

# Semantic search (uses embeddings)
python3 ~/.claude/shared-memory/memory_tool.py search "keyword" --semantic --project {slug}

# Read a specific memory
python3 ~/.claude/shared-memory/memory_tool.py read {memory-id}

# List all memories (filterable)
python3 ~/.claude/shared-memory/memory_tool.py list --project {slug} --type feedback

# Add a new memory
python3 ~/.claude/shared-memory/memory_tool.py add \
  --id "feedback-slug" \
  --name "Short title" \
  --type feedback \
  --project {slug} \
  --content "content here" \
  --source "chat-2026-04-09"

# Update existing memory
python3 ~/.claude/shared-memory/memory_tool.py update {memory-id} \
  --content "new content"

# Log task activity (quick)
python3 ~/.claude/shared-memory/memory_tool.py log \
  --actor "task-id" \
  --action "complete" \
  --details '{"key":"value"}'

# Dashboard
python3 ~/.claude/shared-memory/memory_tool.py stats
```

**See `code-examples/memory_tool.py` for a complete working implementation.**

### When to use shared-memory vs wiki

| Use shared-memory when... | Use wiki when... |
|---|---|
| The memory is cross-project (applies to all) | The memory is project-specific |
| The memory is small (one fact, one rule) | The memory is structured (multi-section entity) |
| You need semantic search | You need human-readable browsing |
| The memory is ephemeral (task run output) | The memory is canonical |
| You want CLI access without opening files | You want markdown editing / Obsidian |

**Both coexist.** Hughes128 uses both: wiki for the canonical entity files, shared-memory for cross-project feedback and learning.

---

## Cross-project learning

Some memories apply to ALL of Phil's projects, not just one. These are "cross-project" memories and they live with `project=philmora` (the user-level slug) or `project=system` (architectural).

### Examples of cross-project memories

- **User preferences:** "Phil prefers direct language, no corporate-speak, short sentences"
- **Hard rules:** "Never take over the visible computer while Phil is using it"
- **Behavioral feedback:** "When encountering ambiguous user requests, ask 1 clarifying question, not 4"
- **Tool gotchas:** "Facebook requires ClipboardEvent paste not execCommand"
- **Architectural patterns:** "Split active and archive data in trackers to reduce context"

### Where they live

1. `~/.claude/CLAUDE.md` — the most important cross-project rules (hard rules, Phil's working style)
2. `~/.claude/shared-memory/` — feedback memories with `project=philmora` or `project=system`
3. `~/.claude/second-brain-blueprint.md` — the unified theory

### The promotion path

Memories flow UPSTREAM over time:

```
Scratchpad note  →  Project wiki entry  →  Shared-memory entry  →  Global CLAUDE.md rule
(one run)          (one project)           (cross-project)         (universal)
```

A scratchpad observation ("Facebook paste broke") becomes a project wiki rule ("wiki/rules/facebook-posting-protocol.md: use ClipboardEvent"), which when it recurs in multiple projects becomes a shared-memory feedback entry, which when it becomes truly universal graduates to global CLAUDE.md.

**The lint task drives the first two promotions automatically.** Human judgment drives the last two.

---

## The focus bug and mitigations

Claude Code desktop has a known bug (GitHub Issue #40669): scheduled tasks pause when the Schedule view loses focus. This is important to know when designing agent memory systems because:

1. **Tasks don't fire reliably** when the user isn't watching
2. **Stuck sessions accumulate in-flight locks** that block new runs of the same task
3. **Load builds up** as zombie processes accumulate

### Mitigations

1. **Scheduler warmup task** — a tiny no-op task on a 30-min cron that does nothing but dispatch, keeping the scheduler dispatcher warm
2. **Power assertion** — Claude Code itself holds a power assertion preventing system sleep (`pmset -g` shows `sleep 1 (sleep prevented by Claude)`)
3. **App Nap disabled** — `defaults write com.anthropic.claudefordesktop NSAppSleepDisabled -bool YES`
4. **Display sleep is fine** — doesn't affect background tasks
5. **Phil keeps Schedule view focused** when walking away from the machine

### Signs of a stuck task

- `lastRunAt` in the scheduler state file hasn't updated for longer than the task's expected runtime
- Scratchpad for the task hasn't been modified recently but the process is consuming CPU
- Multiple "claude" CLI processes from the task persisting

### Recovery

1. **Cmd+Q and relaunch Claude Code** — kills zombies, scheduler re-reads state from disk
2. **If state file is corrupted:** edit `scheduled-tasks.json` directly to remove the stuck entry, then restart
3. **If a specific run needs to catch up:** the scheduler often catches up missed firings automatically after restart

See `03-claude-agents-memory/code-examples/unstick_task.py` for the recovery script.

---

## Pitfalls (real production failures)

Every one of these actually happened during Hughes128 development. Don't repeat them.

### Pitfall 1: The duplication trap

**What:** Inlining the same content (rules, entity facts, protocols) into multiple task SKILL.md files. They drift over time. Updating requires editing N files.

**Fix:** Canonical wiki file per piece of content. Task SKILL.md files REFERENCE the wiki file; they don't inline the content.

### Pitfall 2: The JSON bloat trap

**What:** A tracker file (graphic-usage.json) accumulated 170 entries where 89% were unusable (retired or pending approval). Tasks loaded all 170 on every run.

**Fix:** Split trackers into active (loaded) and archive (not loaded). Move entries to archive when they become unusable. Periodic cleanup.

### Pitfall 3: The model-too-heavy trap

**What:** Running every task on Opus when most work is mechanical (browser automation, JSON updates, list filtering). Paying 2-3x the latency for no quality gain.

**Fix:** Default to Sonnet. Only use Opus for genuine creative work (long-form writing, analytics synthesis, cross-source reasoning).

### Pitfall 4: The sequential read trap

**What:** Tasks loading 12 wiki files at startup via 12 sequential Read tool calls. 12-24 seconds of wall-clock time doing nothing but waiting.

**Fix:** Explicit "PARALLEL — single message" instruction in the SKILL.md. 10x speedup on startup.

### Pitfall 5: The rule contradiction explosion

**What:** Writing absolute rules ("NEVER use X") that have exceptions ("but X is fine in Y context"). Agents apply the rule literally and break valid use cases. Users work around by editing posts manually.

**Fix:** Context-type-aware rules in tables. Instead of "never use $805K", a table with content-type rows and X/Y columns.

### Pitfall 6: The name discrepancy problem

**What:** Primary source has a typo ("Jessica Savage"), user knows the correct name ("Jennifer Savage"), both versions end up in the wiki, agents alternate between them, content is inconsistent.

**Fix:** Explicit reconciliation whenever a discrepancy is found. Pick one canonical version, document the disagreement, grep-replace everywhere.

### Pitfall 7: The verification gap

**What:** User verbally tells agent a fact ("Chadwick was fired from Tucker Hull"). Agent writes it in the wiki. Future agents treat it as verified fact. It propagates to public content. Legal exposure.

**Fix:** Three-tier verification system (✅/⚠️/❌) in entity files. Every fact flagged. Agents respect the tier when generating public content.

### Pitfall 8: The legal posture problem

**What:** A claim is safe in a long-form article with full context but dangerous in a short-form social post without context. Without content-type-aware rules, agents apply the same rule everywhere.

**Fix:** Tier 1 / Tier 2 system with explicit greenlight requirements. Tier 1 is always safe; Tier 2 requires user approval for the specific run.

### Pitfall 9: DO-NOT-PUBLISH content leak risk

**What:** Internal-only content (rumors, unverified claims, strategic plans) ends up in the wiki for context. Agents read it. It leaks into public output.

**Fix:** Never put content in the wiki that you're NOT okay with appearing in agent output. For context that must be in the wiki for understanding but must NEVER be public: use `❌ DO NOT publish` markers AND add explicit behavioral rules ("agents MUST NOT include this in drafts").

### Pitfall 10: The "task does too much" problem

**What:** A single task bundles posting + engagement + moderation + commenting. When ANY step fails, ALL downstream steps in that task get cut.

**Fix:** Split tasks by responsibility. Posting tasks only post. Engagement tasks only engage. Moderation tasks only moderate. Each has its own schedule and fires independently.

### Pitfall 11: The silent skip

**What:** Task can't hit a target, logs "SKIPPED" in the session log, continues normally. User only discovers days later that it's been failing.

**Fix:** Explicit escalation rule. Missed targets MUST fire a HIGH PRIORITY alert. Failure is acceptable; silence is not.

### Pitfall 12: The zombie task

**What:** A scheduled task gets stuck (in-flight lock never released). The scheduler won't fire a new instance because the old one is "still running." Restart doesn't fix it because the state file persists.

**Fix:** Monitor `lastRunAt` vs expected runtime. Edit scheduler state file manually if necessary. Document the recovery procedure.

### Pitfall 13: The image-text mismatch

**What:** Agent picks angles for posts, picks graphics by "lowest use count" filter, but doesn't semantically match graphics to angles. A Mark Gillen attack post ends up with a David Hughes portrait.

**Fix:** Explicit semantic matching matrix in the SKILL.md. Each angle bucket maps to specific graphic categories. Agent filter by bucket FIRST, then by freshness. Plus a filename sanity check before posting.

### Pitfall 14: The over-engineered wiki

**What:** Building a 50-file wiki for a project that needs 5 files. Every abstraction has a cost. Over-splitting creates navigation overhead without benefit.

**Fix:** Start minimal. Split files when the cost of NOT splitting is concrete (drift, bloat, JIT confusion). Don't split for aesthetic reasons.

---

## Files in this blueprint folder

```
03-claude-agents-memory/
├── README.md                            ← You are here
├── philosophy.md                        ← Deep dive on the theory
├── memory-types-for-agents.md           ← Full reference for the 4 types
├── context-engineering.md               ← Prompt patterns for memory use
├── subagent-patterns.md                 ← When and how to use subagents
├── scheduled-tasks-architecture.md      ← Scheduler state, focus bug, warmup
├── shared-memory-system.md              ← SQLite schema, memory_tool.py
├── cross-project-learning.md            ← Promotion paths, global rules
├── context-budget.md                    ← Measuring + optimizing
├── file-templates/
│   ├── task-skill-template.md           ← The SKILL.md skeleton
│   ├── warmup-task-template.md          ← The scheduler warmup no-op
│   ├── lint-task-template.md            ← Weekly maintenance task
│   └── subagent-briefing-template.md    ← Good subagent prompts
└── code-examples/
    ├── memory_tool.py                    ← Full SQLite memory CLI
    ├── scratchpad_cleanup.py             ← Auto-clean old scratchpads
    ├── context_budget.sh                 ← Measure per-task context
    ├── unstick_task.py                   ← Recover from zombie tasks
    └── session_log_compact.py            ← Compress old episodic memory
```

---

## Bootstrap: using this blueprint for a new project

When starting a new Claude Code project that needs agent memory:

1. **Decide if you need a wiki.** Read `philosophy.md` decision tree. Not every project does.
2. **Set up the global infrastructure first** (if not already present):
   - `~/.claude/CLAUDE.md` — global rules (start minimal)
   - `~/.claude/shared-memory/` — install memory_tool.py from `code-examples/`
   - `~/.claude/scratchpads/` — just create the directory
3. **Create the project wiki directory structure** (see Blueprint 2 for the canonical layout if it's a PKM project, Blueprint 1 if it's a campaign project)
4. **Write `wiki/README.md` first** — the schema, before any content
5. **Identify the 4 memory types for THIS project** — list what belongs to each
6. **Extract inline content** from any existing task SKILL.md files into wiki files
7. **Rewrite task prompts** to use the SKILL.md template pattern (always-load / JIT / scratchpad / session log)
8. **Measure pre-load context** with the budget script
9. **Optimize if over budget** (JIT, split trackers, model choice)
10. **Add the lint task** for weekly maintenance
11. **Add the scheduler-warmup task** to mitigate the focus bug
12. **Test one task end-to-end manually before enabling the schedule**

---

## TL;DR

- **Agent memory = files on disk, organized by memory type**
- **4 memory types:** procedural (rules), semantic (entities), episodic (sessions), working (scratchpads)
- **Mix them = rot. Separate them = canonical source of truth.**
- **Wiki = long-term project memory. Shared-memory = cross-project learning. CLAUDE.md = global universals.**
- **Tasks read wiki files via file paths (no RAG).** Always-load is minimal; JIT-load the rest.
- **Parallel reads at startup.** Explicit escalation rules. Explicit scope constraints. Measure context budget.
- **Subagents for context isolation** when the subtask has noisy output or exploratory research.
- **The lint task promotes learnings** from scratchpad → wiki → shared-memory → CLAUDE.md.
- **Pitfalls are real.** Read the 14 in this file before building. Don't repeat them.

Next: read `philosophy.md` for the deeper theory, `memory-types-for-agents.md` for reference details, and the `code-examples/` for working implementations.
