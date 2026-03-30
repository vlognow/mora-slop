---
name: studio-pulse
version: "2.0"
author: phil-mora
tags: [pm, pulse, studio, notion, slack, weekly, github]
trigger: "Generate the weekly Studio Pulse from GitHub releases, Slack, and Jira"
inputs: ["week date range (optional)"]
outputs: ["Notion page + Slack post (review-gated)"]
estimated_time_saved: "2-3 hours per week"
---

# Skill: Studio Pulse

## Purpose
Generate the weekly "⚡ Studio Weekly Pulse" for Machinify Studio (olapui).
Produces two outputs:
1. A Notion page created under Studio Enhancements (parent `2e25356b-3971-8098-8e03-ce8d38fc87b0`)
2. A concise Slack post for **#product-releases** — shown to Phil for review before posting

Optionally also produces a companion **Studio Release Notes** page (detailed/technical).

---

## Trigger
User says something like:
- "generate studio pulse"
- "create this week's studio pulse"
- "write the studio pulse for [week]"

---

## Step-by-Step Process

### Step 1 — Determine the week & version range
The pulse week runs **Tuesday to Tuesday** (inclusive of start Tuesday, up to but not including end Tuesday).
If no date range specified, infer the most recent completed Tuesday-to-Tuesday window.
Example: if today is Tuesday Mar 10, the window is Tue Mar 3 – Tue Mar 10.
Format: `Tue MMM D – Tue MMM D, YYYY`

### Step 2 — Read #eng-studio Slack directly (PRIMARY SIGNAL SOURCE)
Slack MCP is connected. Read the channel directly.
- **Channel ID**: C09UMFL4HSQ
- Use `slack_read_channel` with `response_format: concise` and the week's Unix timestamps
- Extract: shipped work, incidents, cross-team asks, AI tooling discussions, anything not in tickets

### Step 3 — Fetch olapui GitHub Release (PRIMARY CODE SOURCE)
The `olapui` repo has automated versioned releases with full changelogs.
- Search for the release(s) shipped that week using `github-search_issues`:
  `repo:vlognow/olapui is:pr is:merged "chore(main): release" merged:[YYYY-MM-DD]..[YYYY-MM-DD]`
- **IMPORTANT — Deduplication**: Check if a release from that week was already featured in a previous pulse. If so, skip it and focus on:
  - Individual PRs merged to main during the week (bug fixes, feature work that landed)
  - Any newer patch releases (e.g., v0.143.1, v0.143.2) not yet covered
  - Work that was done but not yet released (staged, in PR review)
- Filter for **`studio:`** prefixed entries — Studio-specific changes
- Note exact version numbers and whether they are prod or staging-only releases
- `chore(main): release` = main branch release (prod); `chore(staging): release` = staging only

### Step 4 — Cross-reference Jira
- Path: `/rest/api/3/search/jql`
- JQL: `project = MAC AND updated >= "YYYY-MM-DD" AND updated <= "YYYY-MM-DD" AND (labels = studio OR summary ~ "Studio") AND status changed to Done ORDER BY updated DESC`
- Also look up any MAC tickets referenced in the PR descriptions from Step 3
- Extract: ticket key, summary, assignee

### Step 5 — Read the Daily Development Activity Log (Ianiv's fixes)
- **Page ID**: `2f65356b-3971-81f8-9ebe-dd6309a41614`
- Fetch with `notion-fetch` using `id` param (pass full URL or UUID — NOT `url` param)
- Find the H2 sections matching the target week's days
- Extract commits (hash, Jira, description) for Ianiv Schweber's work
- Cross-reference with GitHub release to avoid duplication

### Step 6 — Check for Studio Ticket Refresh page
- Search Notion for "Studio Ticket Refresh" pages created this week
- These are Ianiv's weekly ticket dashboards — extract any active or newly filed tickets
- Note the page as an artifact in the pulse

### Step 7 — Synthesize
Group all findings into:
- **Highlights**: The 3–6 most impactful changes (features + notable fixes), each with PR# or MAC# and a one-line user impact description
- **By the numbers**: tickets completed, PRs merged, bugs fixed, prod status
- **Team heroes**: Prasanna Ganesan (features/large PRs), Ianiv Schweber (fixes/tooling), and any others with notable contributions this week
- **Production status**: clearly flag what's in prod vs. staged vs. in progress

### Step 8 — Generate Notion Pulse Page
Create as a child page under **Studio Enhancements**:
- Parent page ID: `2e25356b-3971-8098-8e03-ce8d38fc87b0`

**Page title**: `⚡ Studio Weekly Pulse - Week of [DATE RANGE]`

**Structure** (match existing pages exactly):
```
## 📊 This Week By The Numbers
**[N]** Jira tickets completed or advanced to Done
**[N]** PRs merged this week
**[N]** bugs filed and fixed same-day (if applicable)
**[N]** active contributors
**[N]** PRs staged today, prod push pending (if applicable)

---

## 🎯 Major Wins & Impact

### [Win Title]
**What we shipped**: [description]
**Why it matters**: [user/org impact]
**Owner**: [name]

...

---

## 💪 Team Contributions

**🏆 [Name]** 🔥
- [contributions with PR refs]

**[Name]**
- [contributions with PR/commit refs]

---

## 🐛 Production Fixes
- **[MAC-XXXXX]** — [fix description] → [user impact]
...

---

## 🚦 In Progress / Coming Soon
[staged PRs, open PRs in review, ongoing work]

---

## 📋 This Week's Artifacts
**Pull Requests**:
- [#XXXX](url) — description

**GitHub Release**: [vX.X.X](url) [prod or staging]

**Jira Tickets**: list key tickets

**Studio Ticket Refresh**: [link if exists]

---

## 💬 Questions? Feedback?
Want to learn more or see a demo of the new features? Ping Phil in #studio-team 👋

---
*🤖 Generated from GitHub, #eng-studio Slack (C09UMFL4HSQ), and Jira*
```

### Step 9 — Draft Slack Post and Ask for Review
Write the concise version for **#product-releases**.

**CRITICAL — ALWAYS show Phil the draft and wait for approval before posting.**
Never auto-post to Slack. Present the draft and ask: "Ready to post to #product-releases?"

**CRITICAL — Slack mrkdwn formatting rules** (different from markdown):
- Bold: `*text*` (single asterisks) — NOT `**text**`
- Italic: `_text_` (underscores)
- Code: `` `text` `` (backticks)
- No `##` headers — use `*SECTION TITLE*` or emoji prefix instead
- Bullet points work normally

**Slack post format** (follow this exactly):
```
:zap: Studio Weekly Pulse - Week of [DATE RANGE] :zap:

[1–2 sentence intro about the week's theme]

Highlights:

• *[Feature Name]* ([#PR or MAC-XXXXX])
 → [One-line description of user impact]

• *[Feature Name]* ([#PR or MAC-XXXXX])
 → [One-line description of user impact]

• *[Bug Fix Description]* ([MAC-XXXXX])
 → [One-line description of user impact]

:bar_chart: By the numbers: [N] tickets completed | [N] PRs merged | [prod/staging status]

:clap: Team heroes: [Name] + [Name]

:page_facing_up: Full pulse: [notion pulse url]
```

---

## Output
1. Confirm the Notion page was created (include URL)
2. Show the Slack post draft in a code block and ask Phil: "Ready to post to #product-releases?"
3. After Phil approves, post via `slack_send_message` to **#product-releases (C06MZABK7J7)** — return the message link
4. Ask if Phil wants the companion detailed Release Notes page

---

## Style Guidelines
- Slack post is **concise and scannable** — bullet highlights, not paragraphs
- Each highlight: feature/fix name with PR or Jira reference + one-line arrow description of user impact
- Keep intro to 1–2 sentences maximum
- "By the numbers" is a single line with pipe separators
- Tone: energetic and direct — product pride without fluff
- **Don't re-cover releases already featured in the previous week's pulse** — focus on what's new

---

## Key IDs & References
- Daily Activity Log: `2f65356b-3971-81f8-9ebe-dd6309a41614`
- Studio Enhancements parent: `2e25356b-3971-8098-8e03-ce8d38fc87b0`
- GitHub repo: `vlognow/olapui`
- Jira domain: `machinify.atlassian.net`
- Slack channels:
  - `#product-releases`: C06MZABK7J7 (post destination — after Phil review)
  - `#eng-studio`: C09UMFL4HSQ (source — read for weekly signals)
- Primary contributors: `prasannaganesan` (features), `ianiv` (fixes + tooling)

---

## Example Slack Output (Feb 10–14, 2026 — use for style reference)
```
:zap: Studio Weekly Pulse - Week of Feb 10-14, 2026 :zap:

This week Studio shipped three major features that bring enterprise-grade data management capabilities to the platform.

Highlights:

• *Entity Data Editor with Changeset Management* (#7497)
 → Review and approve all entity changes before committing

• *Rulesets CRUD UI with Monaco SQL Editor* (#7484)
 → Create and manage business rules through a modern IDE-like interface with autocomplete and validation

• *Inline UDT Editing with Diff Review* (#7514)
 → Edit User-Defined Types with side-by-side before/after comparison and SQL autocomplete

• *Collection Deletion Bug Fixed* (MAC-27668)
 → Users can now confidently delete collections without false error messages

:bar_chart: By the numbers: 1 ticket completed | 3 major features | 1 bug fix | 3 days active

:clap: Team heroes: Prasanna Ganesan + Ianiv Schweber

:page_facing_up: Full pulse: https://www.notion.so/30a5356b397181cc930ee11d572c95be
```
