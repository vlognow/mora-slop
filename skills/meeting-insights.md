---
name: meeting-insights
version: "2.0"
author: phil-mora
tags: [pm, meetings, transcript, notion, analysis]
trigger: "Analyze a meeting VTT transcript and produce a deep intelligence analysis"
inputs: ["VTT file path, meeting context"]
outputs: ["Notion page with full analysis"]
estimated_time_saved: "1-2 hours per meeting"
---

# Skill: Meeting Insights

## Purpose
Transform any meeting VTT transcript into a deep, well-structured Notion page in Phil's Private Archive.
Produces a single output: a comprehensive analysis document that extracts everything worth knowing and remembering from the meeting.

---

## Trigger
User says something like:
- "analyze this meeting transcript"
- "run meeting insights on [file]"
- "process this VTT file"
- "generate meeting notes from [file]"

---

## Step-by-Step Process

### Step 0 — Always Ask for Context First
Before doing anything else, ask the user:

> "Before I analyze the transcript, give me some context:
> 1. **Meeting name / title** (what should I call this in Notion?)
> 2. **Who was in the meeting?** (names + roles/companies if useful)
> 3. **What was the meeting about?** (1–2 sentences on the purpose/agenda)
> 4. **Any background I should know?** (related projects, ongoing issues, prior decisions, stakes)"

Do not proceed until the user answers. Even brief answers are fine — use what you get.

---

### Step 1 — Read and Pre-process the VTT File
1. Read the VTT file at the path provided
2. Strip all WebVTT formatting noise:
   - Remove `WEBVTT` header
   - Remove numeric cue identifiers
   - Remove timestamp lines (`00:00:00.000 --> 00:00:05.000`)
3. Handle speaker labels:
   - **99% case**: Labels exist as `<v Speaker Name>text</v>` or `Speaker Name: text` → extract and preserve
   - **1% case (no labels)**: Infer speaker changes from conversational context, pronoun shifts, topic ownership. Label as `Speaker A`, `Speaker B`, etc. → **STOP and ask user to confirm names before writing the Notion page**
4. Merge consecutive turns from the same speaker into single paragraphs
5. Produce clean dialogue format:
   ```
   [HH:MM] Speaker Name: text
   ```
6. Note total duration and estimated word count

---

### Step 2 — Auto-Detect Meeting Type
Infer the meeting type from content, title, and context. Types and their output emphasis:

| Type | Emphasis |
|------|----------|
| **1:1** | Relationship dynamics, career/personal notes, commitments made |
| **Standup / Sync** | Blockers, status, who needs what |
| **Strategy / Planning** | Decisions, tradeoffs considered, direction set |
| **Customer Call** | Customer pain points, commitments, sentiment, risk signals |
| **Retrospective** | What broke, what worked, what changes |
| **Interview / Hiring** | Candidate signals, red/green flags, consensus |
| **All-hands / Broadcast** | Key announcements, morale signals, open questions |
| **General** | Balanced across all sections |

State the inferred type at the top of the analysis.

---

### Step 3 — Handle Long Meetings (1 hour+)
For meetings over ~45 minutes or ~8,000 words:

1. **Segment by topic shift** — do NOT cut at arbitrary time intervals. Identify natural topic transitions (a new agenda item starts, conversation pivots, a decision is made and conversation moves on).
2. **Process each segment** independently: extract key moments, quotes, decisions, action items
3. **Synthesize across all segments** into the unified 8-section output
4. Use timestamps to anchor important moments in the document

This approach handles meetings up to 4 hours reliably within context limits.

---

### Step 4 — Run the Full Intelligence Layer
Always run all intelligence analyses — do not skip any section even for short meetings.

**Intelligence analyses to run:**
1. **Subtext & dynamics** — What was said between the lines? Who held power? Any tension or avoidance? What topics were rushed past?
2. **Alignment check** — Where do participants clearly agree? Where are they talking past each other without realizing it?
3. **Risk signals** — Vague commitments, soft "yes" answers, resource/timeline concerns buried in positive language, unresolved ambiguity
4. **Decision quality** — Were decisions made with good information? Were alternatives discussed? Who was missing from the room who should have been?
5. **Relationship reads** (for 1:1s and customer calls) — Energy of the conversation, trust level, anything worth noting about the dynamic
6. **Key quotes** — 2–4 verbatim quotes that capture the essence of the meeting or a critical moment

---

### Step 5 — Generate Notion Page
Create a new page in Phil's Private Archive.

**Parent page ID**: `2be5356b-3971-8026-a9c2-e2e05b8428ec`

**Page title**: `[Meeting Name] — [Date]`
Example: `Product Strategy Sync — Feb 25, 2026`

---

### Notion Page Structure

```
# [Meeting Name]
📅 [Day, Month D, YYYY] | ⏱ [Duration] | 👥 [Attendees list] | 🏷 [Meeting type]

---

## TL;DR
[3–5 bullet points. The absolute minimum someone needs to know if they only read this section.
Lead with decisions, then commitments, then risk. No fluff.]

---

## Summary
[3–5 tight paragraphs. What happened in this meeting, in order. Write it like a smart
colleague recapping the meeting for someone who wasn't there. Cover: what was discussed,
how the conversation evolved, where agreement/tension emerged, and how it ended.
Be specific — name the people, reference what they said.]

---

## Decisions Made
[Each decision as a bullet. Format:]
- **[Decision]**: [context — who proposed it, what alternatives were considered, what was the basis for the call]

[If no clear decisions were made, say so explicitly: "No formal decisions were made in this meeting."]

---

## Action Items
[Table format:]
| # | Action | Owner | Due | Notes |
|---|--------|-------|-----|-------|
| 1 | [what] | [who] | [when or "unspecified"] | [any context] |

[Flag any actions that were verbally agreed but vague or lack an owner.]

---

## Open Questions / Parking Lot
[Things raised but not resolved, deferred, or that need follow-up]
- **[Topic]**: [what the open question is and why it matters]

---

## Intelligence Layer
### What Was Actually Going On
[2–4 paragraphs of honest analysis. Subtext, power dynamics, alignment gaps, what was
left unsaid. Write this for Phil — candid, direct, no corporate euphemism.]

### Risk Signals
[Bullet list of anything that could blow up: vague commitments, soft no's disguised as yes,
timeline risks, resource gaps, misaligned expectations. Flag clearly with ⚠️]

### Decision Quality
[Was this meeting well-run? Were the right people in the room? Were decisions made with
good information? Be blunt.]

### Key Quotes
> "[Verbatim quote]" — Speaker Name
[Brief note on why this quote matters]

---

## Inferred Next Steps
[What SHOULD happen after this meeting, even if not explicitly discussed.
Based on the decisions made, risks identified, and context provided.
Write as recommended actions for Phil.]
1. [Step]
2. [Step]
...

---

*🤖 Generated from VTT transcript by Claude Code Meeting Insights*
*Meeting type: [auto-detected type]*
```

---

## Output
1. Confirm the Notion page was created with its URL
2. Print the TL;DR section to the terminal so Phil gets the quick summary inline

---

## Style Guidelines
- Write for a **single intelligent reader** (Phil) — not a committee
- Be **specific and named**: "Sanjay said he's not confident in the Q3 timeline" not "there was uncertainty around timelines"
- The Intelligence Layer should be **candid and direct** — this is a private document, not a sanitized recap for the team
- Action items should be **complete and ownable** — if something is too vague to act on, flag it as such
- Length scales with meeting complexity: a 30-min sync may produce 600 words, a 4-hour planning session may produce 2,500+ words — that's correct
- Never pad with generic filler ("great discussion was had", "the team aligned on...")
- The TL;DR should stand alone — someone should be able to act from it without reading further

---

## Key IDs & References
- Phil's Private Archive parent page: `2be5356b-3971-8026-a9c2-e2e05b8428ec`
- Slack channel: N/A (this is a private document for Phil only)
- Jira integration: None for now — action items stay in Notion document

---

## Edge Cases

### No Speaker Labels (1% case)
1. Process the transcript with inferred `Speaker A`, `Speaker B`, etc.
2. Show a snippet of the dialogue with your inferred labels
3. Ask: "I couldn't detect speaker names. Here's how I've labeled them — can you confirm? [snippet]"
4. Wait for confirmation before creating the Notion page

### Very Short Meeting (<10 minutes)
Run all sections but keep them brief. TL;DR may be 2 bullets. Summary may be 1 paragraph. Intelligence Layer should still always run.

### Heavily Technical Meeting
In the Summary, don't over-explain technical details — focus on decisions and direction. Capture technical specifics in the Parking Lot or Action Items if they require follow-up.

### Sensitive / Confidential Topics
Write everything candidly — this is Phil's private archive. Do not self-censor.
