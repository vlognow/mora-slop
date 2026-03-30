---
name: cloud-cost-pulse
version: "2.0"
author: phil-mora
tags: [pm, pulse, cloud-cost, notion, slack, jira, weekly]
trigger: "Generate the weekly Cloud Cost Pulse from JIRA, GitHub, Slack, and Notion"
inputs: ["week date range (optional)"]
outputs: ["Notion page + Slack post"]
estimated_time_saved: "2-3 hours per week"
---

# Skill: Cloud Cost Pulse

## Purpose
Generate the weekly "💰 Cloud Cost Pulse" for the Cloud Cost Optimization initiative at Machinify.
Produces two outputs:
1. A Notion page created as a child of the Cloud Cost Optimization page
2. A concise Slack post posted directly to **#product-releases**

---

## Trigger
User says something like:
- "generate cloud cost pulse"
- "create this week's cloud cost pulse"
- "write the cloud cost pulse for [week]"
- "run cloud cost pulse"

---

## Step-by-Step Process

### Step 1 — Determine the week
The pulse week runs **Tuesday to Tuesday** (inclusive of start Tuesday, up to but not including end Tuesday).
If no date range specified, infer the most recent completed Tuesday-to-Tuesday window.
Example: if today is Tuesday Mar 10, the window is Tue Mar 3 – Tue Mar 10.
Format: `Tue MMM D – Tue MMM D, YYYY`

### Step 2 — Read #cloud-cost-optimization Slack directly
Slack MCP is connected. Read the channel directly — no need to ask Phil for a summary.
- **Channel ID**: C0AB8018UK0
- Use `slack_read_channel` with `response_format: concise` and the week's Unix timestamps
- Extract: findings, blockers, decisions, cross-team coordination, anything not in tickets

---

### Step 3 — Query JIRA (PRIMARY SOURCE for progress)
Pull the status of all stories under the Cloud Cost Optimization epic.

- **Epic**: `MAC-26975`
- **JQL**: `parent = MAC-26975 ORDER BY updated DESC`
- Use `jira_get` with `/rest/api/3/search/jql`
- For each story, extract: key, summary, assignee, status, and any status change in the target week
- Identify:
  - **Stories that moved to Done/Verification In Progress this week** → wins
  - **Stories currently In Progress** → active work
  - **Stories still in New with no activity** → potential blockers or stalled items
  - **Stories that had comments added this week** → signals of activity even without status change

Key stories to track:
| Ticket | Topic | Assignee |
|--------|-------|----------|
| MAC-26976 | Spark job costs dashboard | Ashish Gupta |
| MAC-27492 | Useless snapshot detection | Ananth Rao |
| MAC-27550 | Dev/staging spend reduction | Chris Pounds |
| MAC-27555 | Snapshot cost by user/automation | Ananth Rao |
| MAC-27556 | Incomplete snapshot jobs report | Ananth Rao |
| MAC-27557 | Cluster overprovisioning manual assessment | Ashish Gupta |
| MAC-27591 | Failing doc-proc criterion metrics | Akshay More |
| MAC-27660 | Cluster overprovisioning UI — server | Ananth Rao |
| MAC-27661 | Cluster overprovisioning UI — UI part | Unassigned |

---

### Step 4 — Cross-reference GitHub (VERIFY & ENRICH)
Search for merged PRs and commits from the week related to cost optimization work.

Key repos to check:
- `vlognow/onlineDataAnalysis` — Spark job events, cluster metrics, snapshot logic, tableaccesstime
- `vlognow/infrastructure` — AWS infra changes, ECR lifecycle, dev/staging cleanup, S3 policies
- `vlognow/k8s-machinify-apps` — k8s app deployments related to cost work
- `vlognow/airflow-dags` — data pipeline changes, snapshot automation

Search query pattern:
`org:vlognow is:pr is:merged merged:[YYYY-MM-DD]..[YYYY-MM-DD]`

Then filter by relevance — look for PRs with keywords: `cost`, `spark`, `snapshot`, `cluster`, `staging`, `ECR`, `S3`, `lifecycle`, `overprovisioning`, `utilization`, `dashboard`

For each relevant PR: title, author, repo, brief description of change.

---

### Step 5 — Read the Cloud Cost Optimization Notion page (CONTEXT & DECISIONS)
- **Page ID**: `2f65356b-3971-804c-93c3-efabe1a72cf7`
- Fetch with `notion-fetch`
- Look for any new content added during the target week (meeting notes, findings, decisions, updated priorities)
- Extract: any new cost numbers, priority changes, findings from analysis, decisions made

---

### Step 6 — Synthesize
Combine all sources. Build the week's picture around these dimensions:

- **Wins shipped**: stories completed, PRs merged, findings published (with $ impact if known)
- **Active work**: what's in flight right now, who owns it
- **Cost signals**: any actual savings realized or quantified this week
- **Blockers / at-risk**: stories with no movement, missing owners, stalled analysis
- **By the numbers**: JIRA tickets closed, PRs merged, $ impact quantified
- **Coming next week**: what should be landing based on current in-progress work

---

### Step 7 — Generate Notion Pulse Page
Create as a child page under **Cloud Cost Optimization**:
- **Parent page ID**: `2f65356b-3971-804c-93c3-efabe1a72cf7`

**Page title**: `💰 Cloud Cost Pulse - Week of [DATE RANGE]`

**Structure**:
```
## 📊 This Week By The Numbers
**[N]** Jira tickets completed or advanced to verification
**[N]** PRs merged related to cost optimization
**$[X]K** savings realized or quantified (if known)
**[N]** active stories in progress
**[N]** stories still in New / not started

---

## ✅ Wins & Progress

### [Win Title] ([MAC-XXXXX])
**What happened**: [description]
**Why it matters**: [$ impact or downstream value]
**Owner**: [name]

...

---

## 🔄 In Progress This Week

- **[MAC-XXXXX] [Story title]** (Owner: [Name]) — [1-line status update]
...

---

## ⚠️ At Risk / Stalled

- **[MAC-XXXXX] [Story title]** — [why it's flagged: no movement, missing owner, blocked on dependency]
...

[If nothing at risk: "No stories currently flagged as at risk."]

---

## 💰 Cost Impact Tracker

| Category | Baseline | Current | Delta | Source |
|----------|----------|---------|-------|--------|
| Spark clusters | ~$200K/mo | [current if known] | [delta] | [dashboard/ticket] |
| Dev/staging | ~$110K/mo | [current if known] | [delta] | CloudHealth |
| S3 storage | ~$67K/mo | [current if known] | [delta] | CloudHealth |
| **Total** | **~$400K/mo** | [total if known] | [delta] | |

[If no new cost data: "No updated cost figures this week. Baseline numbers shown for reference."]

---

## 🔮 Expected Next Week

- **[Story/initiative]**: [what should land, who owns it]
...

---

## 📋 This Week's Artifacts

**Jira tickets advanced**:
- [MAC-XXXXX](url) — [status change]

**Pull Requests merged**:
- [#XXXX](url) in [repo] — [description]

**Notion updates**:
- [page title](url) — [what changed]

---

*🤖 Generated from JIRA MAC-26975, GitHub, and Notion Cloud Cost Optimization page*
```

---

### Step 8 — Generate Slack Post
Write the concise version for **#cloud-cost-optimization**.

**Slack post format**:
```
:moneybag: Cloud Cost Pulse - Week of [DATE RANGE]

[1–2 sentence intro on the week's theme or momentum]

:white_check_mark: SHIPPED / COMPLETED
• [Win] ([MAC-XXXXX]) — [one-line impact]
• [Win] — [one-line impact]

:arrows_counterclockwise: IN PROGRESS
• [MAC-XXXXX] [Story] (Owner: [Name]) — [status]
• ...

:trophy: HEROES OF THE WEEK
• [Name] — [what they shipped and why it mattered, one line]
• [Name] — [contribution]

:bar_chart: By the numbers: [N] tickets advanced | [N] PRs merged | $[X]K savings quantified (or "baseline $400K/mo, no new actuals this week")

:page_facing_up: Full pulse: [notion page url]
```

**Important**: No WATCH LIST in the Slack post — this is a public channel. Blockers, at-risk items, and missing owners go in the Notion page only (At Risk / Stalled section).

**Emoji guide**:
- `:moneybag:` — cost savings / financial impact
- `:bar_chart:` — dashboards / metrics
- `:hammer_and_wrench:` — infra changes (ECR, S3, dev/staging cleanup)
- `:mag:` — analysis / investigation work
- `:white_check_mark:` — completed
- `:arrows_counterclockwise:` — in progress
- `:trophy:` — heroes of the week
- `:fire:` — high-impact win

---

## Output
1. Confirm the Notion page was created (include URL)
2. Post the Slack message directly to **#product-releases (C06MZABK7J7)** via `slack_send_message` — return the message link
3. Show Phil both links so he can verify

---

## Style Guidelines
- Lead every win with **what actually changed** (code shipped, analysis published, savings confirmed) — not intent or planning
- Be **specific with numbers**: "$10K/month saved on ECR" not "ECR costs reduced"
- For stalled stories, be **direct but not political** — flag the gap, not the person
- The Cost Impact Tracker should always show even when there's no new data — it anchors the initiative to real dollars
- If Phil provided Slack channel context, weave it in naturally — don't just append it as a separate section
- Slack post should be **scannable in 30 seconds** — bullets, not paragraphs

---

## Key IDs & References
- Cloud Cost Optimization parent page: `2f65356b-3971-804c-93c3-efabe1a72cf7`
- JIRA epic: `MAC-26975`
- JIRA domain: `machinify.atlassian.net`
- GitHub org: `vlognow`
- Slack channels:
  - `#product-releases`: C06MZABK7J7 (post destination)
  - `#cloud-cost-optimization`: C0AB8018UK0 (source — read for weekly signals)
- Key contributors: Ashish Gupta, Ananth Rao, Chris Pounds, Akshay More, David Levinger

---

## Cost Baseline (as of Jan 2026 — update as actuals come in)
- Spark clusters + EBS: ~$200K/month
- Dev/staging (net of CastAI): ~$110K/month
- S3 storage: ~$67K/month
- **Total: ~$400K/month**
- Target: 25–30% reduction (~$100–120K/month, ~$360–420K annually)
- Primary cost driver: Humana (~80–85% of Spark costs)
