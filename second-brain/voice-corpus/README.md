# Voice Corpus — Clone Phil's Communication Layer

**The raw material and refined artifacts for making an AI agent that communicates as Phil Mora. Harvested from 6.5 months of Slack communication (Oct 2025 – Apr 2026) across 44 sources.**

---

## What this is

The voice corpus answers a different question than the wiki. The wiki answers **what Phil knows**. The voice corpus answers **how Phil talks** — his tone, his framing, his audience calibration, his decision patterns, his emotional range, his signature phrases.

Combined, they give the Clone Phil agent two things most AI clones lack: factual grounding (wiki) and authentic voice (corpus).

## The harvest

**Sources:** 35 Slack channels + 8 DM conversations with key people
**Time range:** October 1, 2025 – April 17, 2026 (6.5 months)
**Total Phil messages captured:** ~1,200+
**Substantive messages (non-operational):** ~850+
**Total corpus:** 8,273 lines across 44 example files
**Total analysis:** 1,777 lines across 24 analysis files

### Sources by tier

**Tier 1 — Inner circle (highest-density substantive voice):**
- #eng-core-platform-and-one-mora — Phil's direct team channel
- #recruiting_product-phil — hiring philosophy and candidate evaluation
- #claude-phil — Phil's coordination channel with AI
- #cloud-cost-optimization — strategic initiative driving
- #generic-rules-engine — initiative launcher
- #platform-nextgen — big-picture strategy
- #eng-core-platform — selective, targeted posts

**Tier 4 — DMs (highest-authenticity voice):**
- DM: Kathy Kwan (VP Eng) — ~260 messages, "strategically vulnerable" voice
- DM: CJ Silverio (Staff Eng) — 78 messages, "co-conspirator" voice, richest single source
- DM: Piyush Kandhari (Eng Lead) — 250+ messages, zero-filter voice
- DM: Prasanna Ganesan (CTO) — "deferential, BLUF-first" register
- DM: Shri Santhanam (CPO) — "emotionally open, unfiltered builder" register
- DM: Andrey Chernykh (VP Data) — "collaborative peer" register
- DM: David Levinger (CIO) — "respectful stakeholder" register
- DM: Anthony Farelli (Recruiter) — "efficient partner" register

**Tier 2 — Operational channels:**
- #product-staff, #product-extended-staff, #product-management-team
- #ai-repo-champions, #eng-studio, #product-releases
- #data-ai-enablement, #product-vibe-coding, #ai-initiative-discussion, #eng-all-developers

**Tier 3 — Context channels (Phil reads more than posts):**
- #platform, #4iab-core-platform, #4iab-data-platform, #docs-data-eng
- #eng-claw-priv, #eng-agent-smithing-priv, #subrodata4iabcoord
- And 12 more channels with sparse or zero Phil messages

## The refined artifacts

### `style-guide.md` (319 lines)
The master "how to talk like Phil" document. An AI agent reads this and knows:
- Phil's core voice: direct, enthusiastic, systems-depth, no hedging
- How Phil calibrates by audience (8 distinct registers documented)
- 15+ signature patterns ("^^^" amplification, the reframe, French-inflected idioms, "v" for "very")
- 14 things Phil always does, 13 things Phil never does
- Phil's full emotional range with examples
- A 7-level formality gradient from CJ DM (profanity + French) to public pulse posts (full narrative architecture)

### `few-shot-library.md` (479 lines)
77 curated examples organized by 12 situation types:
1. Explaining a technical concept
2. Making and communicating a decision
3. Pushing back on scope or direction
4. Giving positive feedback
5. Giving constructive feedback
6. Asking a probing question
7. Setting direction / assigning work
8. Celebrating a win
9. Managing up (to CPO, to CTO)
10. Responding to a crisis
11. Launching an initiative from scratch
12. Recruiting / evaluating candidates

Each example includes: situation context, Phil's exact message, and why it works for cloning.

### `heuristics.md` (187 lines)
Phil's decision patterns across 6 domains:
1. **Architecture** — defaults (componentize, async, machine-readable, AI-first), tie-breakers, non-negotiables
2. **People/hiring** — 7 green flags, 8 hard red flags, the Reverse PM assessment philosophy
3. **Prioritization** — P0-P3 framework with criteria
4. **Scope** — when to expand vs. cut, with decision triggers
5. **Process** — what Phil automates (7 categories) vs. keeps manual (6 categories)
6. **Political navigation** — when to push vs. wait, the PG-Shri triangle, the Gentle Nudge pattern

### `HARVEST_MANIFEST.md`
The complete list of all 43 harvest targets with channel IDs, tiers, and processing status.

## Directory structure

```
voice-corpus/
├── README.md                    ← you are here
├── style-guide.md               ← how Phil talks (the refined output)
├── few-shot-library.md          ← 77 curated examples by situation
├── heuristics.md                ← how Phil decides
├── HARVEST_MANIFEST.md          ← all harvest targets and status
├── examples/                    ← raw corpus (44 files, Phil's exact messages)
│   ├── eng-core-platform.md
│   ├── dm-cj-silverio.md
│   ├── dm-kathy-kwan.md
│   ├── recruiting-product-phil.md
│   └── ... (40 more)
└── analysis/                    ← per-source voice analysis (24 files)
    ├── eng-core-platform-analysis.md
    ├── dm-cj-silverio-analysis.md
    └── ... (22 more)
```

## How the Clone Phil agent uses this

```
System prompt:
1. Load style-guide.md (always — defines Phil's voice)
2. Load heuristics.md (always — defines Phil's decision patterns)

Per-message:
3. Identify the situation type (explaining? deciding? pushing back?)
4. Load 3-5 matching examples from few-shot-library.md
5. Identify the audience (engineer? leadership? PM? recruiter?)
6. Apply the audience calibration from the style guide
7. Generate response in Phil's voice
```

## Key voice registers discovered

| Audience | Register | Key markers |
|----------|----------|-------------|
| CJ Silverio | Co-conspirator | French greetings, profanity OK, real-time idea formation |
| Kathy Kwan | Strategic partner | "Strategically vulnerable", problem→solution→cost→"your read?" |
| Prasanna (CTO) | Deferential | "Yes Sir", BLUF, never defensive, credits guidance |
| Shri (CPO) | Emotionally open | Org friction transparency, "progressssss !!!" |
| Piyush | Zero filter | Bold takes, teaching mode, builder identity |
| Andrey | Collaborative peer | Transparent about gaps, praise + two precise suggestions |
| David Levinger | Respectful stakeholder | Formal, structured, creative ideas dropped casually |
| Anthony Farelli | Efficient partner | Short decisions, warmth in personal moments |
| Public channels | Narrative architect | Structured posts, anti-hype, business-impact framing |

## Privacy note

This corpus contains verbatim Slack messages from private channels and DMs. It is included in this private repo for Clone Phil development. Do not share externally. Do not push to a public repo. The content is sensitive — it captures how Phil communicates privately with colleagues.

## What's next

Phase 3 of the Clone Phil Plan: build the Slack Bolt agent that uses these artifacts to draft responses as Phil. See `../CLONE_PHIL_PLAN.md` Section 6 for the full agent architecture.
