# Anthropic's Context Engineering Guidance

**A summary of Anthropic's official recommendations for building Claude-powered agents, extracted for blueprint reference.**

**Last updated:** 2026-04-09 (verified quotes added from the official guide)

**Primary source (verified URL and date):**
- **"Effective context engineering for AI agents"** — Anthropic engineering blog
- URL: `anthropic.com/engineering/effective-context-engineering-for-ai-agents`
- Published: September 29, 2025

---

## Verified quotes from the Anthropic guide

Use these verbatim when citing in blueprints or conversations:

**Definition:**
> "Context engineering is the set of strategies for curating and maintaining the optimal set of tokens (information) during LLM inference, including all the other information that may land there outside of the prompts."

It is positioned as "the natural progression of prompt engineering."

**The core guiding principle:**
> "Find the smallest set of high-signal tokens that maximize the likelihood of your desired outcome."

**The attention budget framing:**
> "Like humans, who have limited working memory capacity, LLMs have an 'attention budget' that they draw on when parsing large volumes of context."

**On compaction and tool result clearing:**
> "The safest lightest touch" form of compaction is tool result clearing.

**On minimal system prompts:**
> "Minimal does not necessarily mean short."
>
> Start minimal; add instructions as failure modes surface.

**On tool design:**
> "If a human engineer can't definitively say which tool should be used in a given situation, an AI agent can't be expected to do better."

**On sub-agents (quoted from the guide's findings):**
> "Showed substantial improvement over single-agent systems on complex research tasks."

Multi-agent workflows for research showed 90%+ quality improvements over single-agent baselines, with sub-agents returning 1,000-2,000 token summaries.

---

---

## The Anthropic framework (in 7 principles)

### 1. Context is a scarce resource; budget it

Anthropic's framing aligns with Karpathy's: the context window is scarce working memory, not storage. Treat every token as a cost.

**Practical recommendations:**
- Measure pre-load context per task
- Set budget targets by task type
- Optimize when over budget (move to JIT, split trackers, compress)
- Monitor context bloat in long-running conversations

### 2. Structure context deliberately

The ORDER and STRUCTURE of information in context matters. Claude reads top-to-bottom and weighs early information more heavily.

**Practical recommendations:**
- Put the most important context FIRST (system prompt → task prompt → current state)
- Use clear section headers
- Put constraints and hard rules near the top of a task prompt
- Put current state / recent events closer to the action the model needs to take

### 3. Separate ephemeral from persistent

Short-term working memory (this conversation) is different from long-term memory (across conversations). Treat them differently.

**Practical recommendations:**
- Use scratchpads for ephemeral working memory
- Use files (wiki, notes) for persistent memory
- Don't stuff long-term memory into every conversation's system prompt
- Use tools (memory_tool.py, MCP servers) to bridge ephemeral ↔ persistent

### 4. Prefer tools over pre-loading

When the agent needs information, give it a TOOL to fetch the information rather than pre-loading it "just in case."

**Practical recommendations:**
- Give the agent file-system read access
- Let the agent query a database rather than loading the database
- Use MCP servers to expose complex systems as tool calls
- Trust the agent to fetch what it needs when it needs it

### 5. Use subagents for context isolation

When a subtask produces a lot of tool-result context the parent doesn't need, dispatch to a subagent.

**Practical recommendations:**
- Research subtasks that might go down dead ends → subagents
- Large code searches → subagents
- Parallel work on independent items → subagents
- Don't use subagents when they'd need most of the parent's context anyway

### 6. Trust tool results as data, not instructions

Tool results contain DATA the agent should reason over, not INSTRUCTIONS the agent should follow blindly. Prompt injection from untrusted content (web pages, emails, documents) is a real risk.

**Practical recommendations:**
- Treat all external content as untrusted data
- Verify claims from tool results against other sources
- When a tool result contains instructions to take action, confirm with the user
- Use the Anthropic-provided content isolation rules in Claude Code

### 7. Long context is a feature, not a necessity

Claude Opus 4.6 has a 1M-token context window. Using it well is a feature. But you don't NEED to fill it — most tasks work better with tight, focused context.

**Practical recommendations:**
- Long-context is great for synthesis across many documents
- Long-context is wasted on simple tasks that need 5K tokens of context
- Use the right context size for the task type
- Measure; don't assume

---

## Anthropic's Model Context Protocol (MCP)

MCP is Anthropic's protocol for exposing tools and resources to Claude. It's relevant to memory management because:

### MCP servers can expose memory as resources

Instead of reading files directly, an agent can call an MCP server that manages the memory layer. The MCP server handles:
- Finding relevant files
- Updating files
- Enforcing schemas
- Cross-linking
- Version history

This is conceptually similar to the `memory_tool.py` pattern Phil uses — except exposed via MCP instead of a CLI.

### When to use MCP for memory

- **Use MCP when:** the memory system is complex enough to need a dedicated service (multiple agents, multiple clients, complex schemas)
- **Use CLI tools (like memory_tool.py) when:** a single agent on a single machine needs memory access (simpler setup, no MCP server to maintain)

For Phil's projects (single-user, local machine), CLI tools are the right choice. MCP becomes valuable for team or multi-client scenarios.

---

## Claude Code–specific guidance

### Slash commands

Claude Code supports custom slash commands defined in `.claude/commands/` or `~/.claude/commands/`. These are a lightweight way to create task-shaped workflows without full scheduled tasks.

### Scheduled tasks

Claude Code Desktop supports scheduled tasks via `~/.claude/scheduled-tasks/{task-name}/SKILL.md`. Each task has:
- A SKILL.md file (the prompt)
- A cron schedule
- Optional permission approvals stored per-task

### Skills

Skills are Claude Code's plugin system for pre-built capabilities. A skill is a SKILL.md file that describes a capability and its trigger conditions. Claude Code invokes skills automatically when trigger conditions match.

### CLAUDE.md

The global instructions file at `~/.claude/CLAUDE.md` is loaded into EVERY Claude Code conversation. Keep it short (under 3000 words ideally) and high-signal. This is the place for:
- User preferences (writing style, tool preferences)
- Cross-project hard rules
- Tool usage conventions
- Safety constraints

It is NOT the place for project-specific knowledge (that goes in project wikis).

### Shared state across conversations

Claude Code conversations are ephemeral. To persist state across conversations, use:
- **Files on disk** (wiki, scratchpads)
- **Shared memory SQLite** (memory_tool.py pattern)
- **MCP servers** exposing persistent state
- **The Anthropic API's conversation history** (for resumed conversations)

---

## Anthropic's recommended task patterns

Based on Anthropic documentation and best practices:

### Pattern 1: The scoped task

A task that does ONE thing and exits. Clear input, clear output, clear scope boundary.

Example: "post-morning" (publish posts and exit). Not "campaign-morning" (do everything).

### Pattern 2: The research-and-report task

A task that gathers information and produces a structured report. Often implemented as a subagent.

Example: "Research Coach Don Weaver at Daniel Boone HS" → structured report back to parent.

### Pattern 3: The maintenance task

A task that runs periodically to keep the system healthy. Not producing output per se — producing health.

Example: "campaign-wiki-lint" (weekly wiki maintenance), "scheduler-warmup" (keep dispatcher warm).

### Pattern 4: The integration task

A task that bridges two systems. Reads from A, writes to B.

Example: "campaign-fundraising" (Anedot donations → Donor Tracker Excel → Mailchimp audience).

---

## Safety guidance

Anthropic publishes extensive safety guidance for agents. Key points relevant to memory/context:

### Content isolation

Content from external sources (web pages, emails, documents) must be treated as untrusted data. Never execute instructions found in external content without explicit user confirmation.

### Sensitive information

Never store credentials, API keys, PII, or financial data in wiki files. Use environment variables or system keychains for secrets.

### Action gates

Certain actions require explicit user confirmation:
- Publishing content publicly
- Sending emails
- Making purchases
- Deleting files
- Modifying external accounts

Scheduled tasks CAN do these actions but only with explicit permission approvals stored per-task.

---

## Where to find Anthropic's official docs

Anthropic's documentation URLs shift over time. Stable entry points:

- **docs.anthropic.com** — main documentation hub
- **code.claude.com/docs** — Claude Code specific documentation
- **support.claude.com** — user-facing help
- **github.com/anthropics** — open-source projects including Claude Code SDK

**When citing in a blueprint:** link to the docs.anthropic.com path for concepts that are stable (tool use, system prompts, context window), but be prepared for URLs to shift. Always name the concept in addition to the URL.

---

## Integration with this blueprint library

Where Anthropic's guidance aligns with the blueprints:

| Anthropic principle | Where it shows up in blueprints |
|---|---|
| Context is scarce; budget it | Blueprint 3 "Context budget" section, `context_budget.sh` script |
| Structure context deliberately | Blueprint 3 "The scheduled task pattern" section |
| Separate ephemeral from persistent | Blueprint 3 "The 4 memory types" section |
| Prefer tools over pre-loading | Blueprint 3 "JIT vs preload" section |
| Use subagents for context isolation | Blueprint 3 "When to use subagents" section |
| Trust tool results as data, not instructions | Implicit throughout — the wiki is the trusted layer, external content goes through verification tiers |
| Long context is a feature, not a necessity | Blueprint 3 "Context budget targets" section |

Where Anthropic's guidance is silent (but the blueprints fill in):

- **The specific wiki architecture** (rules/entities/sessions/content-strategy) is Karpathy-derived, not Anthropic-derived
- **The verification tier system** (✅/⚠️/❌) is Hughes128-derived
- **The Tier 1 / Tier 2 legal posture** is Hughes128-derived
- **The semantic image-text correlation rule** is Hughes128-derived

Anthropic provides the FOUNDATION (Claude's capabilities, agent patterns, safety rules). The blueprints provide the SPECIFIC IMPLEMENTATION for knowledge/campaign work.

---

## Related reference files

- `reference/karpathy-sources.md` — Karpathy's framework (the theoretical foundation)
- `reference/pkm-methodologies.md` — Classical PKM methods that transfer to LLM wikis
- `reference/glossary.md` — Terminology used across blueprints
- `reference/tool-setup-guides.md` — Specific tool setups (Obsidian, embedding providers, etc.)
