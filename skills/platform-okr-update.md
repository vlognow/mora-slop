---
name: platform-okr-update
version: "2.0"
author: phil-mora
tags: [pm, okr, platform, notion, weekly, review-gated]
trigger: "Update Platform team OKR rows from the latest weekend update post"
inputs: ["latest weekend update (auto-fetched)"]
outputs: ["Updated KR rows in OKR dashboard"]
estimated_time_saved: "1-2 hours per week"
---

# Skill: Platform OKR Update

## Purpose
Every Friday evening, read the latest Core Platform weekend update post and use it to
update the `Status`, `Health`, and `Status update (optional)` fields for all Platform team
KR rows in the Machinify OKR dashboard.

**This is a review-gated skill.** Always show Phil the full proposed diff before writing
a single row to Notion. Never write without explicit approval.

---

## Trigger
User says something like:
- "update platform OKRs"
- "run platform OKR update"
- "weekly platform OKR update"
- "friday OKR update"
- "update the OKR dashboard from the weekend update"

---

## Step-by-Step Process

### Step 1 — Determine the week ending date
Use today's date to find the most recently completed Friday.
Format: `MM/DD` (e.g., `02/27`) — this prefix goes at the start of every Status update.
Also note the full date for display: `Fri MMM D, YYYY`.

---

### Step 2 — Pull the latest Platform weekend update (PRIMARY SOURCE)
Query the weekend update database for the most recent entry:

```
notion-query-data-sources:
  data_source_urls: ["collection://1b65356b-3971-809f-a313-000bffda8b57"]
  query: SELECT url, Name, Created FROM "collection://1b65356b-3971-809f-a313-000bffda8b57"
         ORDER BY createdTime DESC LIMIT 1
```

Then fetch the full page content:
```
notion-fetch: id = <url from query result>
```

Extract the full "Status/Progress" section — every engineer's bullet points.
This is your only source of truth for this skill. Do not cross-reference GitHub or Jira
(that's platform-pulse's job). Keep the scope clean.

---

### Step 3 — Pull the Platform team OKR rows
Query the correct OKR database for all Platform team rows in the current quarter:

```
notion-query-data-sources:
  data_source_urls: ["collection://1515356b-3971-81d4-824b-000b20ca20c2"]
  query: SELECT url, "Key result", "Status", "Health", "Status update (optional)"
         FROM "collection://1515356b-3971-81d4-824b-000b20ca20c2"
         WHERE "Owner team" = 'Platform team'
         AND "Quarter" = 'Q1 2026'
         ORDER BY url
```

**Update the quarter value** ("Q1 2026", "Q2 2026", etc.) based on the current date:
- Q1 2026: Jan 6 – Mar 28, 2026
- Q2 2026: Apr 1 – Jun 30, 2026

---

### Step 4 — Map weekend update content to each KR

For each KR row, scan the weekend update for relevant signal using this mapping.
If a KR has **no signal** in the weekend update, mark it explicitly as "no update — carry forward."

#### KR Signal Mapping

| KR | Look For In Weekend Update |
|----|---------------------------|
| KR 1.1 – Data Inventory [Shared] | Usually a cross-team note; if already stamped with the correct date, skip |
| KR 1.2 – Evolent Data Split & MIAB Support | James (Evolent data split, PR stack, Spark version), Fernanda (MIAB, cluster launch, EC2, SSH) |
| KR 2.1 – Proactive Alerting & Monitoring | Ashish (dashboards, Grafana, alerts, LunchNLearn), Ceej (on-call, FireHydrant, Nagios, incidents, Tailscale, DB instability) |
| KR 2.2 – Cloud Cost Optimization | Ashish (Spark jobs, costTrackingId, MAC-2766x, MAC-2755x, CPU/memory ratio, EBS), Ananth (cluster overprovisioning) |
| KR 3.1 – MacUI Framework Productization | Revin (mac-ui npm, AI steering rules, Developer Guide, PR #4xx, adoption), Phil (mac-ui AI coding docs) |
| KR 3.2 – NexTurn Finance Document Automation | Danny (subro deployments, NexTurn), Project Sovereignty, Hartford, IDP pipeline |
| KR 4.1 – Enhanced Machinify Studio | Regression mentions, release notes, Chris (CI, GHA, continuous tests, JDK), Danny (mac-ui deployments, QA deploys) |
| KR 4.2 – Backend Development Platform | Ceej (machined-rs, scaffolding, templates, Backend Dev Platform), Jake's team |
| KR 4.3 – DeltaLake/Iceberg Data Resource | Mitch (Iceberg, DeltaLake, DataResource, read/write, runbook, Spark version skew) |
| KR 4.5 – Improved ODA Testing | Charlie (E2E tests, triage, test failures), Chris (GHA, continuous tests, CI fixes), Fernanda (MIAB local testing) |

---

### Step 5 — Draft proposed updates

For each KR, produce:

**`Status`** — one of:
- `On track` (green, progressing)
- `At Risk` (yellow, slowing or blocked)
- `BLOCKED` (red, hard blocker with no path forward)
- `Not started` (if nothing has started yet)

**`Health`** — one of: `🟢`, `🟡`, `🔴`

**`Status update (optional)`** — text, always starting with `MM/DD — `:
- Lead with the engineer's name: "Ashish:", "Ceej:", "Mitch:", etc.
- 1–3 sentences. Specific: name the work, the PR if mentioned, the blocker if any.
- If multiple engineers contribute to one KR, combine: "Ashish: [x]. Ceej: [y]."
- If there is no signal this week: `MM/DD — No update this week.`
- **Never fabricate detail** — only write what is directly stated in the weekend update.

#### Status/Health decision rules:
- Signal present + progress made → `On track` / 🟢
- Signal present + work blocked, stalled, or no progress → `At Risk` / 🟡
- Hard blocker explicitly stated with no workaround → `BLOCKED` / 🔴
- No signal in update for this KR → carry forward existing status/health unchanged
- KR already stamped with the correct date → skip, no change

---

### Step 6 — Present the full diff for approval

**STOP HERE. Do not write to Notion yet.**

Display every KR as a table showing current vs. proposed:

```
## Proposed Platform OKR Updates — Week ending [Fri MMM D, YYYY]

### KR [X.X] – [Key Result Name]
| Field | Current | Proposed |
|-------|---------|----------|
| Status | [current] | [proposed] *(changed / no change)* |
| Health | [current] | [proposed] *(changed / no change)* |
| Status update | [current text] | [proposed text] |

---
[repeat for each KR]

### Skipped (no change)
- KR X.X – [name]: [reason — already current / no signal]
```

Then say:
> "X rows to write, Y skipped. Approve and I'll fire them all in parallel."

**Wait for Phil's explicit approval ("yes", "approved", "go", "do it") before proceeding.**
If Phil asks to modify a specific row, update your draft and re-show the affected row before writing.

---

### Step 7 — Write to Notion (all approved rows in parallel)

Use `notion-update-page` with `command: update_properties` for each approved row.

Fields to write per row:
```json
{
  "Status": "<value>",
  "Health": "<🟢|🟡|🔴>",
  "Status update (optional)": "<MM/DD — text>"
}
```

Run all writes in a single parallel batch. Do not write rows one at a time.

---

### Step 8 — Confirm to terminal

```
✅ Platform OKR Update — [Fri MMM D, YYYY] — COMPLETE

Rows updated: X
Rows skipped: Y (no change / no signal)

Summary:
  🟢 KR 2.1 – Proactive Alerting & Monitoring
  🟢 KR 2.2 – Cloud Cost Optimization
  [etc.]

Dashboard: https://www.notion.so/machinify/Platform-and-Data-product-line-OKR-dashboard-29d5356b397180f2875becf3af5da112
```

---

## Key IDs & References

| Resource | ID / URL |
|----------|----------|
| OKR Dashboard (target page) | `29d5356b-3971-80f2-875b-ecf3af5da112` |
| OKR data source (write target) | `collection://1515356b-3971-81d4-824b-000b20ca20c2` |
| Weekend update data source (read source) | `collection://1b65356b-3971-809f-a313-000bffda8b57` |
| Weekend update DB view | `view://1b65356b-3971-8091-9930-000cfa67c5f7` |

---

## Guardrails

- **Never write without Phil's approval** — always show the diff first
- **Never fabricate** — only write what is in the weekend update
- **Never update Data team rows** — filter strictly to `Owner team = "Platform team"`
- **Never overwrite a row already stamped with today's date** unless Phil explicitly asks
- **Always use parallel writes** — never sequential row-by-row
- If the weekend update hasn't been posted yet (most recent entry is more than 8 days old),
  say: "No weekend update found for this week yet — check back after the team posts."

---

## Status Field Valid Values (exact strings required by Notion)

```
"On track"
"At Risk"
"BLOCKED"
"Not started"
"Paused"
"Achieved"
"Partially achieved"
"Did not achieve"
"Abandoned"
"Started (deprecated)"
```

Health field valid values: `"🟢"`, `"🟡"`, `"🔴"`
