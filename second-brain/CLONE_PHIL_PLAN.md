# The Clone Phil Plan

**A technical blueprint for building an AI agent that communicates as Phil Mora — at work via Slack, at home via email/iMessage — backed by a Karpathy-style LLM wiki and a voice corpus harvested from real conversations.**

*Version: 1.0 | Date: April 2026 | Authors: Phil Mora + Claude Opus 4.6*

---

## Table of contents

1. [The thesis](#1-the-thesis)
2. [Architecture overview](#2-architecture-overview)
3. [The three layers](#3-the-three-layers)
4. [Phase 1: The backfill — harvesting Phil's communication history](#4-phase-1-the-backfill)
5. [Phase 2: The style engine — learning how Phil talks](#5-phase-2-the-style-engine)
6. [Phase 3: The agent — Clone Phil goes live](#6-phase-3-the-agent)
7. [The autonomy graduation model](#7-the-autonomy-graduation-model)
8. [Safety, boundaries, and hard rules](#8-safety-boundaries-and-hard-rules)
9. [Work implementation (Slack)](#9-work-implementation-slack)
10. [Home implementation (email, iMessage, personal)](#10-home-implementation)
11. [Data schemas](#11-data-schemas)
12. [Technical stack](#12-technical-stack)
13. [Metrics and evaluation](#13-metrics-and-evaluation)
14. [Research foundations](#14-research-foundations)
15. [Risks and mitigations](#15-risks-and-mitigations)
16. [Implementation timeline](#16-implementation-timeline)

---

## 1. The thesis

The most valuable thing Phil Mora produces at work is not documents, slides, or code. It is **decisions, explanations, and direction delivered through conversation** — in Slack threads, meeting discussions, email chains, and hallway exchanges. This conversational output is ephemeral: it helps the person who received it, but it doesn't compound. The same question asked by a different person three months later gets answered from scratch.

Clone Phil is an AI agent that:
1. **Knows what Phil knows** — via the work-brain wiki (concepts, entities, decisions, projects)
2. **Talks like Phil talks** — via a voice corpus harvested from real conversations
3. **Decides like Phil decides** — via decision heuristics extracted from Phil's communication patterns
4. **Knows when to shut up** — via a confidence model and hard boundary list

The goal is not to replace Phil. The goal is to handle the **repeatable 60%** of Phil's communication — the questions that have been answered before, the status updates, the context-sharing, the "who owns this?" lookups — so Phil can focus on the **irreplaceable 40%** that requires genuine judgment, creativity, empathy, and authority.

### The Stanford validation

Stanford HAI's 2025 study is the key evidence. They created digital twins of 1,052 individuals using 2-hour interview transcripts injected into LLM prompts. The agents replicated responses **85% as accurately as the individuals replicated their own answers** two weeks later. The method was simple: rich personal context in the system prompt. No fine-tuning. No complex architectures. Just the right context.

Phil's work-brain wiki + voice corpus is a far richer context source than a 2-hour interview transcript. If 2 hours of transcript produces 85% accuracy, 6 months of Slack messages + a structured wiki should produce something substantially better.

---

## 2. Architecture overview

```
┌──────────────────────────────────────────────────────────────────────┐
│                        CLONE PHIL AGENT                              │
│                                                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │
│  │  KNOWLEDGE   │  │    VOICE    │  │  DECISION   │  │ CONFIDENCE │ │
│  │    LAYER     │  │    LAYER    │  │  HEURISTICS │  │   MODEL    │ │
│  │             │  │             │  │             │  │            │ │
│  │ work-brain/ │  │   voice/    │  │  voice/     │  │ Tiered     │ │
│  │ wiki notes  │  │  examples/  │  │  heuristics │  │ autonomy + │ │
│  │ index.md    │  │  style-     │  │  .md        │  │ hard       │ │
│  │             │  │  guide.md   │  │             │  │ boundaries │ │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └─────┬──────┘ │
│         │                │                │               │         │
│         └────────────────┴────────────────┴───────────────┘         │
│                              │                                       │
│                    ┌─────────┴─────────┐                            │
│                    │  RESPONSE ENGINE   │                            │
│                    │  (Claude API)      │                            │
│                    └─────────┬─────────┘                            │
│                              │                                       │
│              ┌───────────────┼───────────────┐                      │
│              ▼               ▼               ▼                      │
│     ┌──────────────┐ ┌────────────┐ ┌──────────────┐              │
│     │ AUTO-RESPOND  │ │   DRAFT    │ │    SKIP      │              │
│     │ (high conf,  │ │ (to review │ │ (not for     │              │
│     │  routine)    │ │  channel)  │ │  Phil)       │              │
│     └──────────────┘ └────────────┘ └──────────────┘              │
└──────────────────────────────────────────────────────────────────────┘
                              │
            ┌─────────────────┼─────────────────┐
            ▼                 ▼                 ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │    SLACK      │  │    EMAIL     │  │   iMESSAGE   │
    │  (Bolt SDK)  │  │ (Gmail API)  │  │ (Shortcuts   │
    │              │  │              │  │  + bridge)   │
    └──────────────┘  └──────────────┘  └──────────────┘
         WORK              HOME              HOME
```

---

## 3. The three layers

### Layer 1: Knowledge (what Phil knows)

**Source:** `~/work-brain/` — the Karpathy-style LLM wiki.

**Contains:** Concepts (agentic readiness, context engineering, vibe-driven product dev, etc.), entities (people, teams, vendors), projects (Q2 OKRs, AI enablement, platform strategy), decisions (ADRs), sources (papers, articles, meeting notes).

**How the agent uses it:** When a question comes in, the agent reads `index.md`, identifies relevant files, reads them in full, and draws on them for factual grounding. "What did we decide about the rules engine?" → reads `concepts/rules-engine-unification.md` + `projects/q2-platform-and-data-okrs.md` + any relevant `decisions/` files.

**Growth mechanism:** The wiki grows through ingest (raw/ → atomic notes), query promotion (good answers written back), and the Slack backfill (historical decisions/explanations mined from conversation history).

### Layer 2: Voice (how Phil talks)

**Source:** `~/work-brain/voice/` — harvested from Slack, email, and other communication channels.

**Contains:**
- `voice/examples/` — Phil's actual messages, organized by channel and categorized by type (decision, explanation, position, feedback, question, direction, celebration)
- `voice/style-guide.md` — synthesized analysis of Phil's communication patterns, recurring phrases, tone variations by audience
- `voice/few-shot-library.md` — 50-100 curated examples for few-shot prompting, organized by situation type
- `voice/heuristics.md` — decision patterns: "when asked about X, Phil's position is Y because Z"

**How the agent uses it:** The style guide loads into the system prompt. When generating a response, the agent finds the 3-5 most relevant few-shot examples (by situation type and topic similarity) and includes them as demonstrations. The response matches Phil's tone, length, framing, and vocabulary.

**Growth mechanism:** The daily digest flags new substantive Phil messages for corpus inclusion. The weekly lint reviews and recategorizes the voice corpus. Over time, the style guide gets refined as patterns sharpen.

### Layer 3: Confidence (when to act vs. escalate)

**Source:** `voice/confidence-policy.md` — explicit rules for what the agent can and cannot do.

**Contains:**
- Autonomy level definition (currently at Level N)
- Hard boundary list (topics never handled autonomously)
- Confidence threshold by message type
- Escalation protocol (how to present drafts for review)
- Reversibility assessment (can this action be undone?)

**How the agent uses it:** Before responding, the agent evaluates:
1. Is this message for Phil? (triage)
2. Is this topic on the hard boundary list? (if yes → draft only)
3. Does the wiki have sufficient context to answer? (if no → draft or skip)
4. What's the confidence score? (below threshold → draft)
5. Is the response reversible? (if no → draft regardless of confidence)
6. Current autonomy level allows auto-send? (if no → draft)

---

## 4. Phase 1: The backfill

### 4.1 Objective

Harvest Phil's Slack messages from October 1, 2025 through the present. Produce two outputs:
1. **Wiki notes** — substantive content paraphrased into the wiki
2. **Voice corpus** — Phil's actual messages stored verbatim with metadata

### 4.2 Source channels

**Core (full harvest — every Phil message):**

| Channel | ID | Expected density |
|---------|----|-----------------|
| #eng-core-platform | C07F7K8N5CY | High — technical decisions, architecture |
| #eng-core-platform-and-one-mora | C0A9QVBDRQT | High — direct team communication |
| #ai-repo-champions | C0APCFFP9J4 | Medium — AI enablement direction |
| #cloud-cost-optimization | C0AB8018UK0 | Medium — cost analysis, decisions |
| #product-releases | C06MZABK7J7 | Low — pulse posts (already in wiki) |
| #eng-studio | C09UMFL4HSQ | Medium — Studio direction |

**Professional (selective harvest — substantive Phil messages only):**

| Channel | ID | Expected density |
|---------|----|-----------------|
| #product-management-team | C06KSTV59HU | Medium — PM strategy |
| #product-staff | C09E5SNMMJT | Low — leadership coordination |
| #product-extended-staff | C0AE8P0JLJW | Medium — announcements, onboarding |
| #recruiting_product-phil | C0A9XNFESTD | Medium — hiring philosophy |
| #product-vibe-coding | C09F21NRBEW | Low — vibecoding initiative |
| #ai-initiative-discussion | C0ALGGKMNG6 | Low — AI initiative |
| #data-ai-enablement | C0AJN0E16VA | Medium — data team AI adoption |
| #generic-rules-engine | C0AKJUASV7V | Low — rules engine project |

**DMs (selective — substantive conversations only):**
- Harvest Phil's DM threads with key people: Kathy Kwan, CJ Silverio, Prasanna Ganesan, Shri Santhanam, Andrey Chernykh, Piyush Kandhari

### 4.3 Message classification taxonomy

Every Phil message gets one of these labels:

| Category | Description | Wiki action | Voice corpus |
|----------|-------------|-------------|-------------|
| DECISION | Making or announcing a decision | → `decisions/` | Yes |
| EXPLANATION | Explaining architecture, strategy, how something works | → `concepts/` | Yes |
| POSITION | Stating a stance or opinion | → `concepts/` | Yes |
| FEEDBACK | Giving feedback to someone | None | Yes |
| QUESTION | Asking a probing or strategic question | None | Yes |
| DIRECTION | Assigning work, setting priorities | → `projects/` | Yes |
| CELEBRATION | Acknowledging good work, wins | None | Yes |
| OPERATIONAL | Scheduling, "sounds good", logistics | None | No |
| SOCIAL | Humor, casual, relationship-building | None | No (but track for voice warmth) |

### 4.4 Execution plan

**Rate limits:** Slack allows ~50 reads/minute. Each channel read returns up to 100 messages.

**Estimated volume:**
- ~6.5 months × ~20 working days × ~14 channels
- Assumption: Phil posts ~10-30 messages/day across all channels
- Estimated total Phil messages: 1,500-4,000
- Substantive (non-operational/social): ~40% = 600-1,600 messages

**Batch strategy:**
- Process 2-3 channels per day
- Each batch: read channel → filter Phil messages → classify → write to voice corpus → propose wiki notes
- Day 1-2: 6 core channels (highest value)
- Day 3-4: 8 professional channels
- Day 5: DMs with key people
- Day 6-7: Review, recategorize, quality-check

**Storage format:** See [Section 11: Data schemas](#11-data-schemas).

### 4.5 Home computer backfill (personal)

On the home machine, the same process runs against different sources:

| Source | Method | Expected content |
|--------|--------|-----------------|
| Gmail (personal) | Gmail API or Google Takeout export | Personal communication style, non-work topics |
| Apple Mail (work overflow) | `mdfind` + Mail.app export | Cross-over work communication |
| iMessage | `chat.db` SQLite (~/Library/Messages/) | Most authentic personal voice — casual, family, friends |
| WhatsApp (if used) | Export chat → markdown | International contacts, personal |
| Notes (Apple Notes) | Shortcuts export or direct DB read | Personal thinking, ideas, lists |
| Voice memos | Whisper transcription → markdown | Fleeting thoughts, ideas on walks |

**iMessage is the gold mine for personal voice.** The `chat.db` SQLite database is locally accessible at `~/Library/Messages/chat.db` on macOS. It contains every iMessage/SMS with timestamps, read receipts, and thread structure. No API needed — just SQL queries against the local database.

---

## 5. Phase 2: The style engine

### 5.1 Objective

Analyze the voice corpus to produce three artifacts:
1. Style guide
2. Few-shot library
3. Decision heuristics

### 5.2 The style guide (`voice/style-guide.md`)

Produced by having Claude read the entire voice corpus and synthesize Phil's communication patterns:

```markdown
# Phil Mora — Communication Style Guide

## Voice characteristics
- [Tone: direct, enthusiastic, systems-thinking depth]
- [Sentence structure: short declarative, then elaboration]
- [Vocabulary: technical but accessible, specific not abstract]
- [Humor: dry, self-deprecating, pop culture references]

## Audience calibration
### With engineers (CJ, Lina, James, Chris)
- [peer-level technical depth, specific architecture references]
- [asks questions before stating positions]
- [respects autonomy — suggests, doesn't dictate]

### With leadership (Shri, Prasanna, David)
- [BLUF first, then supporting context]
- [quantifies wherever possible]
- [frames in business impact, not technical detail]

### With PMs (Piyush, Sarah, product team)
- [collaborative, builds on their framing]
- [connects tactical to strategic]
- [energetic about AI enablement]

### With recruiters/candidates
- [welcoming, high-energy]
- [balances enthusiasm with directness about expectations]

## Recurring phrases and patterns
- [list of Phil-isms extracted from corpus]

## What Phil NEVER does
- [hedge without taking a position]
- [use corporate jargon without substance]
- [dismiss someone's idea without engaging with it]
```

### 5.3 The few-shot library (`voice/few-shot-library.md`)

50-100 curated examples, organized by situation:

```markdown
## Explaining a technical concept to leadership
### Example 1: Cloud cost framing for David Levinger
Situation: David asked about AWS cost trends
Phil said: [exact quote]
Why this works: [Phil simplified without losing precision, led with the business frame]

## Pushing back on scope
### Example 1: Rules engine scope boundary
Situation: Team wanted to include workflows in Q2
Phil said: [exact quote]
Why this works: [Phil acknowledged the value, drew the line, gave a timeline for the deferred scope]
```

### 5.4 Decision heuristics (`voice/heuristics.md`)

Extracted from DECISION-type messages:

```markdown
## Phil's decision patterns

### Architecture decisions
- Default: start simple, add complexity when proven necessary
- Tie-breaker: which option is more reversible?
- Non-negotiable: HIPAA compliance, data privacy, human-in-the-loop for AI

### People decisions
- Hire for taste + technical depth, not credentials
- Give ownership, not tasks
- Default to trust, course-correct fast

### Prioritization
- P0: anything blocking revenue or compliance
- P1: platform capabilities that unblock multiple teams
- P2: developer experience improvements
- P3: nice-to-haves that can wait a quarter
```

---

## 6. Phase 3: The agent

### 6.1 Work agent (Slack)

**Framework:** Slack Bolt for Python

**Event loop:**
```python
# Pseudocode — the core agent loop
@app.event("message")
def handle_message(event, say):
    # 1. Triage: is this for Phil?
    if not is_for_phil(event):
        return
    
    # 2. Check hard boundaries
    if is_hard_boundary(event):
        draft_to_approval_channel(event, reason="hard boundary topic")
        return
    
    # 3. Load context
    wiki_context = load_relevant_wiki_files(event)
    voice_context = load_matching_few_shot_examples(event)
    thread_context = load_thread_history(event)
    style_guide = load_style_guide()
    
    # 4. Generate response
    response = generate_phil_response(
        message=event,
        wiki=wiki_context,
        voice=voice_context,
        thread=thread_context,
        style=style_guide,
    )
    
    # 5. Evaluate confidence
    confidence = evaluate_confidence(event, response, wiki_context)
    
    # 6. Act based on autonomy level and confidence
    if autonomy_level >= 2 and confidence > 0.85 and is_reversible(event):
        say(response)  # auto-send
        log_to_audit_trail(event, response, confidence, auto=True)
    else:
        draft_to_approval_channel(event, response, confidence)
```

**The `is_for_phil()` function:**
```python
def is_for_phil(event):
    """Determine if this message needs Phil's attention."""
    text = event.get("text", "")
    # Direct @mention
    if "<@U099L4N8GAX>" in text:
        return True
    # Question in a channel Phil monitors, on a topic Phil owns
    if is_question(text) and topic_matches_phil_domain(text):
        return True
    # Reply in a thread Phil is participating in
    if event.get("thread_ts") and phil_in_thread(event["thread_ts"]):
        return True
    return False
```

### 6.2 Home agent (email + iMessage)

**Email (Gmail):**
- Use Gmail API with OAuth2
- Watch for incoming emails that need responses
- Same triage → context → generate → confidence → act/draft pipeline
- Draft responses appear in Gmail Drafts folder for Phil to review and send
- Uses personal wiki + personal voice corpus (different from work)

**iMessage:**
- macOS Shortcuts can trigger on incoming messages
- A Shortcut calls a local script that:
  1. Reads the incoming message
  2. Queries the personal wiki
  3. Generates a suggested reply
  4. Displays it as a notification or writes it to a "suggested replies" note
- Full automation is possible via AppleScript `tell application "Messages"` but risky — start with suggestions only

**Architecture difference from work:**
- Work uses Slack Bolt (event-driven, always-on)
- Home uses polling (Gmail API check every N minutes) + Shortcuts triggers (iMessage)
- Work posts drafts to #claude-phil
- Home posts drafts to a local "Clone Phil Drafts" note in Apple Notes or a dedicated app

---

## 7. The autonomy graduation model

| Level | Name | Behavior | Graduation criteria |
|-------|------|----------|-------------------|
| **0** | Observer | Reads everything, reports in daily digest. No responses. | Default starting level |
| **1** | Drafter | Drafts all responses to approval channel. Phil approves/edits/sends. | Manual activation |
| **2** | Collaborator | Auto-sends routine responses (factual lookups, status, scheduling). Drafts everything else. | >90% approval rate over 2 weeks at Level 1 |
| **3** | Delegate | Auto-handles all defined categories. Escalates novel situations. | >95% approval rate over 1 month at Level 2 |
| **4** | Twin | Fully autonomous for all internal communication. Drafts-only for external. | >98% approval rate over 2 months at Level 3 |

**Demotion:** Any single response that Phil marks as "wrong" or "should not have sent" drops the agent one level for that message category. Trust is earned slowly and lost quickly.

**Per-category leveling:** The agent can be Level 3 for "status update" messages but Level 1 for "architecture decisions." Categories graduate independently.

---

## 8. Safety, boundaries, and hard rules

### 8.1 Hard boundaries (never autonomous, any level)

| Category | Why |
|----------|-----|
| Compensation, performance, personnel | Legal and HR implications |
| Legal commitments, contracts, NDAs | Binding authority |
| Anything requiring genuine empathy | Bad empathy is worse than silence |
| External stakeholders (customers, vendors, board) | Reputational risk |
| Anything Phil has never expressed a position on | No basis for the clone to act |
| Irreversible actions (approve deploy, merge PR, close ticket) | Can't undo |
| Confidential strategy not yet in the wiki | Risk of premature disclosure |

### 8.2 Transparency policy

**Internal Slack (work):**
- Level 1-2: no disclosure needed (Phil is reviewing everything)
- Level 3-4: messages include a subtle footer: `via Phil's AI assistant`
- Anyone can ask "is this Phil or the bot?" and get an honest answer

**External (email, clients, vendors):**
- Always draft-only. Phil always sends personally.
- If Phil forwards a draft, he takes ownership of the content.

**Personal (home):**
- Close contacts know about the clone
- Suggestions only, never auto-send to personal contacts
- iMessage auto-send only for logistics ("running 5 min late", "on my way")

### 8.3 The audit trail

Every agent action is logged:
```json
{
  "timestamp": "2026-05-01T14:32:00Z",
  "channel": "C07F7K8N5CY",
  "message_id": "1776351577.445809",
  "action": "auto_respond | draft | skip",
  "confidence": 0.87,
  "autonomy_level": 2,
  "wiki_files_used": ["concepts/agentic-readiness.md", "projects/ai-enablement-program.md"],
  "few_shot_examples_used": ["explanation_03", "direction_12"],
  "response_text": "...",
  "phil_review": "approved | edited | rejected | pending",
  "phil_edit_distance": 0.12
}
```

The edit distance (how much Phil changes drafts before sending) is the core metric for graduation. If Phil sends drafts unedited >90% of the time, the agent is ready to level up.

---

## 9. Work implementation (Slack)

### 9.1 Technical components

```
~/projects/clone-phil/
├── agent/
│   ├── app.py                    # Slack Bolt event loop
│   ├── triage.py                 # Is this for Phil?
│   ├── context_loader.py         # Wiki + voice + thread context
│   ├── response_engine.py        # Generate Phil-voice response
│   ├── confidence.py             # Confidence scoring
│   ├── autonomy.py               # Level management + graduation
│   └── audit.py                  # Logging every action
├── config/
│   ├── boundaries.yaml           # Hard boundary list
│   ├── autonomy_levels.yaml      # Per-category autonomy state
│   └── channel_config.yaml       # Which channels to monitor
├── scripts/
│   ├── backfill.py               # Slack history harvester
│   ├── analyze_voice.py          # Voice corpus → style guide
│   └── evaluate.py               # Compute approval rate, edit distance
├── tests/
│   ├── test_triage.py
│   ├── test_response_quality.py  # Compare agent response to Phil's actual
│   └── test_boundaries.py
├── CLAUDE.md                     # Agent context for Claude Code sessions
└── README.md
```

### 9.2 Dependencies

```
slack-bolt>=1.18.0       # Slack event framework
anthropic>=0.45.0        # Claude API
pyyaml>=6.0              # Config files
sqlite3                  # Audit trail (stdlib)
```

### 9.3 Deployment

- Runs on Phil's work Mac as a launchd daemon (same pattern as existing wiki automation)
- Socket Mode connection to Slack (no public URL needed)
- Logs to `~/projects/clone-phil/logs/`
- Audit trail in SQLite at `~/projects/clone-phil/audit.db`

---

## 10. Home implementation

### 10.1 Differences from work

| Aspect | Work | Home |
|--------|------|------|
| Primary channel | Slack | Gmail + iMessage |
| Wiki location | `~/work-brain/` | `~/personal-brain/` |
| Voice corpus | Slack messages | Email + iMessage + voice memos |
| Autonomy | Graduated auto-send | Suggestions only (except logistics) |
| Privacy tier | Standard (Anthropic API OK) | Strict (consider local LLM for personal content) |
| Topics | Professional knowledge | Personal knowledge, family, hobbies, health, finance |

### 10.2 Personal wiki bootstrap

Same Karpathy pattern, different content:

```
~/personal-brain/
├── README.md                    # Schema
├── index.md                     # Content catalog
├── log.md                       # Operation log
├── concepts/                    # Ideas, frameworks, interests
│   ├── music-production.md
│   ├── parenting-philosophy.md
│   └── health-fitness.md
├── entities/                    # People, places, things
│   ├── family/
│   ├── friends/
│   └── doctors-services/
├── projects/                    # Active personal projects
├── sources/                     # Books, articles, podcasts
├── voice/                       # Personal communication corpus
│   ├── examples/
│   ├── style-guide.md
│   └── few-shot-library.md
└── raw/
```

### 10.3 iMessage harvesting

The local `chat.db` is a SQLite database:

```sql
-- Find all Phil's sent messages with recipients
SELECT
    m.ROWID,
    m.date / 1000000000 + 978307200 as unix_timestamp,
    m.text,
    m.is_from_me,
    h.id as contact,
    c.display_name as chat_name
FROM message m
JOIN chat_message_join cmj ON m.ROWID = cmj.message_id
JOIN chat c ON cmj.chat_id = c.ROWID
LEFT JOIN handle h ON m.handle_id = h.ROWID
WHERE m.is_from_me = 1
  AND m.text IS NOT NULL
  AND m.date / 1000000000 + 978307200 > 1727740800  -- Oct 1, 2025
ORDER BY m.date DESC;
```

**Privacy note:** iMessage content is deeply personal. The personal brain should use:
- Local embeddings (sentence-transformers, not cloud)
- Consider local LLM (Ollama + Llama 3) instead of Claude API for personal content
- Or use Claude with a zero-retention agreement if available
- Separate privacy tier from work wiki

### 10.4 Gmail harvesting

```python
# Using Gmail API
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

service = build('gmail', 'v1', credentials=creds)
# Fetch sent messages
results = service.users().messages().list(
    userId='me',
    q='from:me after:2025/10/01',
    maxResults=500
).execute()
```

### 10.5 Home agent architecture

```python
# Home agent — poll-based, not event-driven
import schedule

def check_gmail():
    """Poll Gmail every 5 minutes for messages needing response."""
    unread = get_unread_needing_response()
    for email in unread:
        context = load_personal_wiki_context(email)
        voice = load_personal_few_shot(email)
        draft = generate_phil_response(email, context, voice)
        save_as_gmail_draft(email, draft)
        notify_phil(f"Draft ready for: {email.subject}")

def check_imessage():
    """Poll chat.db for new messages needing response."""
    # Read from ~/Library/Messages/chat.db
    new_messages = get_new_imessage_messages()
    for msg in new_messages:
        if needs_response(msg):
            suggestion = generate_phil_response(msg)
            display_notification(f"Suggested reply to {msg.sender}: {suggestion}")

schedule.every(5).minutes.do(check_gmail)
schedule.every(1).minute.do(check_imessage)
```

---

## 11. Data schemas

### 11.1 Voice corpus entry

```markdown
## [YYYY-MM-DD HH:MM] CATEGORY | topic-slug

**Channel:** #channel-name (or DM: Person Name)
**Thread:** [top-level | reply to: brief description of parent]
**Audience:** [engineer | leadership | PM | recruiter | personal]
**Tone:** [direct | collaborative | celebratory | firm | casual]

> Phil's exact message text here.
> Can be multi-line.

**Context:** Brief description of what prompted this message.
**Entities mentioned:** [[entities/cj-silverio]], [[concepts/agentic-readiness]]
**Decision (if any):** [What was decided, or N/A]
```

### 11.2 Audit trail record

```sql
CREATE TABLE audit_trail (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    channel_id TEXT,
    channel_name TEXT,
    message_ts TEXT,
    trigger_type TEXT,  -- mention, question, thread_reply, direct
    action TEXT,        -- auto_respond, draft, skip, escalate
    confidence REAL,
    autonomy_level INTEGER,
    wiki_files_used TEXT,  -- JSON array
    few_shot_ids TEXT,     -- JSON array
    response_text TEXT,
    phil_review TEXT,    -- approved, edited, rejected, pending, N/A
    edit_distance REAL, -- 0.0 = no changes, 1.0 = complete rewrite
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_timestamp ON audit_trail(timestamp);
CREATE INDEX idx_audit_action ON audit_trail(action);
CREATE INDEX idx_audit_review ON audit_trail(phil_review);
```

### 11.3 Confidence model inputs

```yaml
confidence_factors:
  wiki_coverage: 0.3      # Weight: does the wiki have relevant content?
  few_shot_match: 0.2     # Weight: do we have similar few-shot examples?
  topic_familiarity: 0.2  # Weight: has Phil discussed this topic before?
  question_clarity: 0.15  # Weight: is the question unambiguous?
  audience_match: 0.15    # Weight: have we seen Phil talk to this person?

thresholds:
  auto_respond: 0.85
  draft: 0.40
  skip: 0.0  # Below 0.40, the agent skips (not for Phil or too uncertain)
```

---

## 12. Technical stack

### 12.1 Work (Slack agent)

| Component | Choice | Why |
|-----------|--------|-----|
| Event framework | Slack Bolt for Python | Official, well-maintained, Socket Mode |
| LLM | Claude Opus 4.6 (1M context) via Anthropic API | Best synthesis, long context for wiki loading |
| LLM (fast path) | Claude Sonnet 4.6 | Triage + confidence scoring (cheaper, faster) |
| Knowledge store | `~/work-brain/` (markdown files) | Karpathy pattern, already built |
| Voice store | `~/work-brain/voice/` (markdown files) | Same pattern, same search infrastructure |
| Semantic search | wiki_search.py (sentence-transformers, SQLite) | Already built, extend to voice corpus |
| Audit trail | SQLite | Simple, local, queryable |
| Deployment | macOS launchd | Same pattern as existing automation |
| Approval channel | #claude-phil (Slack) | Already exists, private |

### 12.2 Home (email + iMessage agent)

| Component | Choice | Why |
|-----------|--------|-----|
| Email | Gmail API + OAuth2 | Standard, well-documented |
| iMessage | Direct SQLite read of chat.db | No API needed, fully local |
| LLM | Claude API or Ollama (local) | Privacy-dependent decision |
| Knowledge store | `~/personal-brain/` | Separate from work, same pattern |
| Voice store | `~/personal-brain/voice/` | Separate corpus, personal voice |
| Deployment | launchd (polling daemon) | Same macOS pattern |
| Approval | Apple Notes or dedicated app | Drafts appear for review |

---

## 13. Metrics and evaluation

### 13.1 Core metrics

| Metric | How measured | Target |
|--------|-------------|--------|
| **Approval rate** | % of drafts Phil sends unedited | >90% for Level 2 graduation |
| **Edit distance** | Levenshtein ratio between draft and sent version | <0.15 average |
| **Response time** | Time from message to draft available | <30 seconds |
| **Coverage** | % of Phil-directed messages the agent can draft for | >70% |
| **False positive rate** | Messages the agent tried to answer that weren't for Phil | <5% |
| **Hard boundary compliance** | % of boundary-list topics correctly escalated | 100% (non-negotiable) |
| **Wiki growth from agent** | Notes/extensions proposed from agent activity | 5+/week |

### 13.2 The Phil Test

A weekly qualitative check: Phil reads 10 agent-drafted responses blind (without knowing which are drafts and which are real Phil messages from the corpus). Can he tell which are his?

**Target:** Phil cannot reliably distinguish agent drafts from his own messages >70% of the time.

### 13.3 The Colleague Test

After Level 2 graduation: show 5 colleagues 10 messages (mix of Phil and agent). Can they tell which are Phil?

**Target:** Colleagues cannot reliably distinguish >60% of the time.

---

## 14. Research foundations

| Source | Key finding | How we use it |
|--------|-------------|---------------|
| Stanford HAI 2025 — Digital Twin study | 2-hour interview transcripts → 85% replication accuracy | Rich context in system prompt beats fine-tuning |
| EMNLP 2025 — "Catch Me If You Can?" | LLMs struggle with implicit writing style via ICL alone | Need explicit style guide, not just examples |
| Karpathy LLM Wiki gist | Wiki as knowledge substrate, no RAG, file-level retrieval | The work-brain architecture |
| Anthropic context engineering guide | Structure context deliberately, budget attention | JIT wiki loading, minimal always-load set |
| Microsoft Agent Governance Toolkit | Reversibility as the key heuristic for autonomy | Confidence model design |
| Delphi.ai | Production digital clone platform | Validation that the pattern works commercially |
| OpenClaw framework | Open-source multi-channel personal agent | Reference implementation for Slack/email/iMessage |
| Slack Bolt starter agent | Official Slack agent template with Claude | Starting point for the Slack bot |

---

## 15. Risks and mitigations

| Risk | Severity | Mitigation |
|------|----------|-----------|
| Clone says something factually wrong about a project | High | RAG against wiki (not parametric memory). If wiki doesn't have it, the agent says "I'm not sure, let me check with Phil." |
| Clone commits Phil to something he wouldn't agree to | High | Hard boundary list + autonomy levels + irreversibility check |
| Voice drift — clone gradually stops sounding like Phil | Medium | Weekly Phil Test. Style guide refreshed monthly. Corpus grows continuously. |
| Colleagues lose trust if they discover responses are AI | Medium | Transparency policy. Internal Slack = lower stakes. Graduated disclosure. |
| Privacy breach — personal wiki content leaks | High | Separate work/personal wikis. Local embeddings for personal. Consider local LLM. |
| Over-reliance — Phil stops thinking because the clone handles it | Medium | The clone handles the repeatable 60%, not the creative 40%. Phil still does the hard thinking. |
| Regulatory — EU AI Act requires disclosure | Low (internal) | Footer on auto-sent messages at Level 3+. External always manual. |

---

## 16. Implementation timeline

### Work (this machine)

| Week | Phase | Deliverable |
|------|-------|-------------|
| 1-2 | Backfill | Slack messages Oct 2025 → present harvested. Voice corpus populated. |
| 3 | Style engine | Style guide, few-shot library, decision heuristics produced. |
| 4 | Agent scaffold | Slack Bolt app running, Level 0 (observer), triage working. |
| 5 | Level 1 | Drafts appearing in #claude-phil for Phil's review. Audit trail logging. |
| 6 | Evaluation | Approval rate computed. Phil Test run. Adjust style guide. |
| 7-8 | Level 2 attempt | If >90% approval: auto-send routine, draft complex. |

### Home (home machine — separate Claude session)

| Week | Phase | Deliverable |
|------|-------|-------------|
| 1 | Bootstrap personal wiki | `~/personal-brain/` scaffolded, same Karpathy pattern |
| 2-3 | Backfill | iMessage + Gmail harvested. Personal voice corpus populated. |
| 4 | Style engine | Personal style guide (different from work voice). |
| 5 | Agent scaffold | Gmail polling + iMessage monitoring running. Suggestions only. |
| 6+ | Iteration | Refine suggestions. Evaluate whether auto-draft-to-Gmail is useful. |

---

## Appendix A: Starting the home implementation

To bootstrap Clone Phil on the home computer, start a fresh Claude Code session and say:

> "I want to build a personal Clone Phil agent. Read ~/projects/mora-slop/second-brain/CLONE_PHIL_PLAN.md — specifically Section 10 (Home implementation). Bootstrap a personal wiki at ~/personal-brain/ following the same Karpathy pattern as the work wiki. Then harvest my iMessage history from chat.db and my Gmail sent messages. Build the personal voice corpus. I want suggestions for replies, not auto-send. Start with Section 10.3 (iMessage harvesting) — that's where my most authentic personal voice is."

The home session doesn't need access to any work systems. It builds a separate wiki, separate voice corpus, separate agent — connected only by the fact that they're both cloning the same person.

---

*End of document. This plan is alive — it evolves as we build. The wiki feeds the voice corpus; the voice corpus feeds the agent; the agent reveals wiki gaps; the gaps feed the wiki. Compounding.*
