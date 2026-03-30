---
name: weekly-briefing
version: "2.0"
author: phil-mora
tags: [pm, okr, weekly, notion, accountability, ritual]
trigger: "Run the Friday weekly OKR briefing — interview, health status, write to Notion"
inputs: ["Phil answers to OKR questions"]
outputs: ["OKR database updates + field report"]
estimated_time_saved: "3-4 hours per week"
---

# Skill: Weekly Briefing

## Purpose
Phil's Friday afternoon OKR accountability ritual. Codename: **SITREP**.

Ask Phil one sharp question per OKR mission, call the battle status on each,
then write everything to Notion — Command Center, OKR database rows, mission
intel pages, and Weekly Field Report — all in one pass.

This is **Phil-facing and OKR-centric**. Not a JIRA report. Not a team update.
A private weekly reckoning with what actually moved and what didn't.

---

## Trigger
User says something like:
- "run weekly briefing"
- "weekly briefing"
- "Friday briefing"
- "let's do the weekly OKR check-in"

---

## The 9 OKR Initiatives (Know These Cold)

### Focus Area A: Platform Execution & Reliability
| # | Initiative | RICE | KR Summary |
|---|-----------|------|------------|
| 1 | Cloud Cost Optimization | 80 | Documented $XM annual savings; top 20 expensive jobs; David Levinger as exec owner |
| 2 | MacUI Framework Productization | 72 | >80% adoption across 4 MFY properties; Legos of Legos pattern; 2-day onboarding |
| 3 | Enhanced Machinify Studio | 60 | Zero new regressions; top 10 critical bugs fixed; MacUI Phase 1 migration |
| 4 | NextTurn Finance Doc Automation | 30 | Oversee Project Sovereignty — lightweight; NexTurn offshore handles execution |
| 5 | Payer Connectivity Strategy | — | Business case + ROI + 60+ payer inventory; Humana conversations; ~15 hrs PM work |

### Focus Area B: Architecture & Discovery
| # | Initiative | RICE | KR Summary |
|---|-----------|------|------------|
| 6 | Letter Generation Service | 40 | Requirements + architecture + API spec for universal doc gen; 3+ doc types, 2+ teams |
| 7 | Mailroom Integration Requirements | 16 | Requirements only (not implementation); enables Q2 execution |
| 8 | RPA Strategy & Prioritization | 12 | Governance + backlog; "last resort" policy; strategy not implementation |

### Focus Area C: Strategic Planning
| # | Initiative | RICE | KR Summary |
|---|-----------|------|------------|
| 9 | Streamlined Q2 Planning Process | 48 | 60% time reduction vs Q4; documented playbook; repeatable rhythm |
| 10 | Product Factory Operating Model Reset | 96* | Rebuild trust with engineering; 70%+ buy-in signal by Q1 end; *relationship value, not delivery pressure |

---

## Step-by-Step Process

### Step 1 — Determine the week
Calculate from today's date:
- Q1 = Jan 6 – Mar 28, 2026 (12 weeks)
- Week 1 = Jan 6–9, Week 2 = Jan 12–16, Week 3 = Jan 19–23, Week 4 = Jan 26–30,
  Week 5 = Feb 2–6, Week 6 = Feb 9–13, Week 7 = Feb 16–20, Week 8 = Feb 23–27,
  Week 9 = Mar 2–6, Week 10 = Mar 9–13, Week 11 = Mar 16–20, Week 12 = Mar 23–28
- Format date range: `Mon MMM D – Fri MMM D, YYYY`

---

### Step 2 — Pre-load context (do this silently, don't announce it)
Read `~/context/active-projects.md` to know current state of each OKR before asking.
This lets you ask informed questions, not generic ones.

If any OKR has a known blocker or recent development from context, reference it
in the question ("Last I knew X was the blocker — did that move?").

---

### Step 3 — Run the OKR interview

Open with one line setting the tone, then go Focus Area by Focus Area.
Ask all questions in a single message — Phil answers in one pass.
Be direct. Be specific. Reference what you know.

**Opening line** (pick one based on the week's energy):
- "Week [N] of 12. SITREP time. One question per mission — answer what you know, skip what you don't."
- "Friday. Week [N]. Command Center needs updating. Let's see where we actually are."
- "Q1 has [N] weeks left. Week [N] field report. Go."
- "🪖 SITREP Week [N]. Report in, Commander."

**Then ask all 10 questions in this format:**

```
--- FOCUS AREA A: PLATFORM EXECUTION ---

1. CLOUD COST OPTIMIZATION (RICE 80 — your highest-stakes delivery OKR)
[One sharp, specific question about what happened. Reference known context.
Examples: "MAC-27492 and MAC-26976 were in Verification — did they close?"
or "Any actual dollar numbers from Levinger's team yet?"
or "What's the biggest thing that moved on cost this week?"]

2. MACUI FRAMEWORK (RICE 72)
[Question about adoption momentum or migration progress.
Example: "Where is >80% adoption tracking — closer or further than last week?"]

3. ENHANCED MACHINIFY STUDIO (RICE 60)
[Question about regression count or quality trajectory.
Example: "Any new regressions this week, or is the zero-regression goal holding?"]

4. NEXTURN FINANCE / PROJECT SOVEREIGNTY (RICE 30 — managed)
[Quick pulse — this is lightweight oversight.
Example: "Any blockers to remove for the NextTurn team, or is this running itself?"]

5. PAYER CONNECTIVITY STRATEGY
[Question about strategic PM work — conversations, doc progress.
Example: "Any progress on the Humana conversations or the 60-payer inventory this week?"]

--- FOCUS AREA B: ARCHITECTURE & DISCOVERY ---

6. LETTER GENERATION SERVICE (RICE 40)
[Requirements and architecture movement.
Example: "Did Letter Gen requirements or API spec move this week?"]

7. MAILROOM INTEGRATION REQUIREMENTS (RICE 16)
[Quick pulse — requirements only.
Example: "Any movement on Mailroom requirements, or is this on hold?"]

8. RPA STRATEGY (RICE 12)
[Lowest priority — quick yes/no.
Example: "RPA — anything to note, or quietly tracking?"]

--- FOCUS AREA C: STRATEGIC PLANNING ---

9. Q2 PLANNING PROCESS (RICE 48)
[Planning machinery and timeline.
Example: "How did the Fit/Not Fit review go? Is Q2 planning taking shape?"]

10. PRODUCT FACTORY OPERATING MODEL (RICE 96 relationship value)
[Trust signals with engineering — subtle and qualitative.
Example: "Any conversations with Kathy's org or engineering this week that felt like progress on trust?"]

---

11. ANYTHING ELSE?
Surprises, decisions made, things that cut across multiple OKRs, or anything
I should know about that doesn't fit neatly into a single initiative.
```

**Wait for Phil's response. Be persistent — if he says "let's do it later" or deflects, push back once:**
> "It's Friday. Takes 5 minutes to answer. We can write the Notion updates in parallel. Go."

---

### Step 4 — Ask follow-up questions if needed
If Phil's answer on any OKR is vague ("good", "moving", "on track"), probe once:
> "[OKR name] — specifically what happened? Even one concrete thing."

If an OKR has no update ("nothing this week"), accept it but flag it in the health status.
Two consecutive weeks of "nothing" = 🟡 minimum.

---

### Step 5 — Call health status for each OKR

**After receiving Phil's answers**, assign health status. This is your call, not Phil's.

**Health status rubric:**
- 🟢 On Track: Phil describes concrete progress; no blockers; pacing right for Q1 end
- 🟡 Needs Attention: Progress slower than expected, OR a dependency is pending,
  OR Phil's answer is vague/uncertain, OR no movement for 1+ week on a high-RICE item
- 🔴 At Risk: No meaningful progress for 2+ weeks, OR hard blocker with no path forward,
  OR Phil explicitly flags concern, OR Q1 delivery is mathematically unlikely at current pace

**For RICE ≥60 (Cloud Cost, MacUI, Studio): hold to a higher standard.**
Vague progress = 🟡. Concrete progress with momentum = 🟢.

**For RICE ≤30 (NextTurn, Mailroom, RPA): lower bar.**
These are lightweight; "quietly tracking" = 🟢.

**Overall health for the week:**
- Any 🔴 present → overall 🔴
- 2+ 🟡 or 1 🔴 + multiple 🟡 → overall 🟡
- Otherwise → 🟢

Tell Phil your battle status calls briefly before writing to Notion:
> "Battle status: Cloud Cost 🟡 (no actuals yet, two missions stalled), MacUI 🟢, Studio 🟢, [etc.]. Any pushback before I file the field report?"

Wait for override, then write.

---

### Step 6 — Write to Notion (run all in parallel)

#### A. Update the OKR database rows (all 9-10 in parallel)
- **Database**: collection `158b2524-aba3-4002-971c-14bac611d0c6`
- For each initiative row, update:
  - `Status` — 🟢 On Track / 🟡 Needs Attention / 🔴 At Risk
  - `This Week` — 1-2 sentences: what happened this week (based on Phil's answer)
  - `Progress` — cumulative progress narrative (append this week to prior weeks, keep it to 3-4 sentences max total)

#### B. Update each mission's intel page (child pages)
Fetch each child page first (rows in the OKR database).
Prepend a **weekly field report block** at the top (before existing content):

```
---
### 📡 Week [N] Field Report — [Fri MMM D, 2026] | [battle status emoji]
**🎯 Mission status**: [🟢 Green / 🟡 Caution / 🔴 Red Alert] — [one-line rationale]
**⚔️ Action this week**: [Phil's answer, synthesized]
**🚀 Next deployment**: [what should move next week]
[**💣 Active blocker**: [if any]]
---
```

#### C. Create new Weekly Field Report database entry
- **Database**: collection `54b9b283-fd0c-4a5e-aa28-899d608d9bda`
- Properties:
  - `Name`: `🪖 Week [N] — [punchy one-line that captures the week's character]`
    Examples: "🪖 Week 8 — Cost missions stall, Studio fires on all cylinders"
              "🪖 Week 9 — Q2 theater secured, MacUI momentum building"
              "🪖 Week 8 — Quiet week, holding the line"
  - `Health Status`: overall 🟢/🟡/🔴
  - `Week Ending`: Friday's date (ISO format)
  - `Week Number`: N (as number)
  - `Key Highlights`: field report across all 9 missions

**Key Highlights format:**
```
✅ [Mission] — [what moved, one line]
✅ [Mission] — [what moved]
⚠️ [Mission] — [caution flag]
🔴 [Mission] — [red alert, if any]
📌 [Cross-cutting intel if any]
```

#### D. Update the Q1 Dashboard page (Command Center) header + SITREP callout
The dashboard page (`2e35356b-3971-81f3-8767-ec1b4ac2df87`) has two static text blocks that must be updated every week.

Use `replace_content_range` to replace from the `📡 **LAST SITREP**` line through the end of the old callout block in a single operation.

**1. Header lines** (top of page):
```
📡 **LAST SITREP**: Week [N] filed — [Mon MMM D, YYYY] | [🟢/🟡/🔴] [color]
🗓️ **Q1 2026** | Week [N] of 12 | [12-N] weeks to close
```

**2. SITREP callout** (under `⚡ WEEKLY SITREP`):
```
> [🟢/🟡/🔴] **WEEK [N] TL;DR**
> ✅ [Mission] — [one-line win]
> ✅ [Mission] — [one-line win]
> ⚠️ [Mission] — [one-line flag]
> ⚠️ [Mission] — [one-line flag]
> 📌 [Cross-cutting note if any]
```

**Rule**: Only list missions with concrete movement (✅) or active flags (⚠️). Skip quietly-tracking green missions. Max 6-7 lines — this is the 30-second Monday morning read.

---

### Step 7 — Confirm and summarize to terminal

Print a clean close-out:

```
🪖 SITREP Week [N] — FILED.
Command Center: https://www.notion.so/2e35356b397181f38767ec1b4ac2df87
Field Report: [weekly field report entry url]

Overall battle status: [emoji] — [one-line summary]

Mission status board:
  [emoji] Cloud Cost Optimization
  [emoji] MacUI Framework
  [emoji] Enhanced Studio
  [emoji] NextTurn Finance
  [emoji] Payer Connectivity
  [emoji] Letter Generation Service
  [emoji] Mailroom Integration
  [emoji] RPA Strategy
  [emoji] Q2 Planning Process
  [emoji] Product Factory Reset

Week [N] of 12 complete. [12-N] weeks to victory. 🎖️
```

---

## Persistence Protocol
If Phil doesn't respond to the questions, or says "later":
1. Push back once (see Step 3)
2. If still no response, hold position — don't abandon
3. When Phil returns: "Still need your Week [N] SITREP. 5 minutes. Report in."
4. Never write to Notion with incomplete answers — partial intel is worse than no intel

---

## Style Guidelines
- Questions are short and sharp — 1 sentence max each
- Reference specific context (ticket names, last known status) to make it easy to answer
- Health status calls are Phil's accountability mirror — if something is 🟡, say why plainly
- The weekly update names should have personality: capture the actual character of the week
- The child page updates should feel like a running log, not a fresh document — they accumulate week over week
- Never skip the health status conversation — that's the core value of the ritual

---

## Key IDs & References
- Q1 Dashboard: `2e35356b-3971-81f3-8767-ec1b4ac2df87`
- OKR database (data source): `collection://158b2524-aba3-4002-971c-14bac611d0c6`
- Weekly Updates database (data source): `collection://54b9b283-fd0c-4a5e-aa28-899d608d9bda`
- Phil's Personal OKRs page: `2e15356b-3971-81fe-ba5b-f94324df87ad`
- Phil's Private Archive: `2be5356b-3971-8026-a9c2-e2e05b8428ec`
- Context file: `~/context/active-projects.md`

## Q1 Calendar
- Q1 = Jan 6 – Mar 28, 2026 (12 weeks)
- Week 1: Jan 6–9 | Week 2: Jan 12–16 | Week 3: Jan 19–23 | Week 4: Jan 26–30
- Week 5: Feb 2–6 | Week 6: Feb 9–13 | Week 7: Feb 16–20 | Week 8: Feb 23–27
- Week 9: Mar 2–6 | Week 10: Mar 9–13 | Week 11: Mar 16–20 | Week 12: Mar 23–28
