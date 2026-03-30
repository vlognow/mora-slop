---
name: weekly-update-entry
version: "2.0"
author: phil-mora
tags: [pm, weekly, stakeholder, notion, review-gated]
trigger: "Fill in the Data and Platform row in cross-team weekly product line updates"
inputs: ["platform-pulse wins + at-risk KRs (auto-fetched)"]
outputs: ["Updated row in weekly updates page"]
estimated_time_saved: "30-60 min per week"
---

# Skill: Weekly Update Entry

## Purpose
Populate the **Data & Platform** row in the cross-team "Weekly product line updates"
Notion page. This is the leadership roll-up that Shri and other PMs review.

**Inputs come from upstream skills — not raw sources:**
- **Wins** column: Summarized from the most recent **platform-pulse** Notion page
- **OKRs at Risk** column: Pulled from the OKR dashboard (Platform team KRs with Health 🟡 or 🔴)
- **Help Needed** column: Any KR at 🔴 or with an explicit blocker

This skill does NOT re-read the weekend update or GitHub. It consumes what
platform-pulse and platform-okr-update already produced.

**Review-gated.** Always show Phil the proposed cell content before writing.

---

## Trigger
User says something like:
- "update the weekly product line entry"
- "fill in the weekly update entry"
- "write the platform row in the weekly updates"
- "weekly update entry"

---

## Step-by-Step Process

### Step 1 — Determine the week
Use today's date to find the most recently completed Friday.
The toggle heading format is: `## Weekly Update M/D/YYYY {toggle="true"}`
Example: `## Weekly Update 3/20/2026 {toggle="true"}`

---

### Step 2 — Find the most recent Platform Pulse page
Query the Platform Pulse parent page for the most recent child page:

```
notion-fetch: id = "2775356b-3971-80e2-874f-c5aa2f135ba5"
```

Find the most recent "Platform Pulse - Week of ..." child page. Fetch its full content.
Extract the **Major Wins & Impact** section — these are the wins to summarize.

---

### Step 3 — Pull at-risk KRs from the OKR dashboard
Query the OKR database for Platform team KRs with Health 🟡 or 🔴:

```
notion-query-data-sources:
  data_source_urls: ["collection://1515356b-3971-81d4-824b-000b20ca20c2"]
  query: SELECT url, "Key result", "Status", "Health", "Status update (optional)"
         FROM "collection://1515356b-3971-81d4-824b-000b20ca20c2"
         WHERE "Owner team" = 'Platform team'
         AND "Quarter" = '<current quarter>'
         AND "Health" IN ('🟡', '🔴')
         ORDER BY url
```

Update the quarter value based on the current date:
- Q1 2026: Jan 6 – Mar 28, 2026
- Q2 2026: Apr 1 – Jun 30, 2026

---

### Step 4 — Fetch the current weekly updates page
Fetch the page to find the current week's table and the existing Data & Platform row:

```
notion-fetch: id = "2e15356b-3971-8079-a60f-e8d19906ebae"
```

Locate the toggle heading for the target week (e.g., `## Weekly Update 3/20/2026`).
Inside it, find the `<tr>` containing `**Data & Platform **`.

**IMPORTANT**: The Data team may have already filled in part of the Wins column.
Never overwrite their content — always **prepend** Core Platform wins before the
existing Data team content, separated by `<br><br>`.

---

### Step 5 — Draft the three cell contents

#### OKRs at Risk column
Format matching the existing style (see Audit row for reference):

```
**🟡 KR X.X – [KR Name]**<br>  • [1-2 sentence status from the Status update field]<br><br>**🔴 KR Y.Y – [KR Name]**<br>  • [1-2 sentence status]
```

- Use the emoji prefix matching the Health field (🟡 or 🔴)
- Bold the KR name line
- Indent the status note with `  •`
- If no KRs are at risk, write: `All KRs on track 🟢`

#### Wins column
Summarize the top wins from the platform-pulse into bullet-style entries.
**Prepend** before any existing Data team content.

Format:
```
**Core Platform**<br>✅ [Win 1 — 1 sentence, name the owner]<br>✅ [Win 2]<br>✅ [Win 3]<br>...<br><br>[existing Data team content unchanged]
```

- 4–7 wins max, one line each
- Lead with the most impactful
- Name the engineer
- Keep each win to ~15 words

#### Help Needed column
- If any KR is 🔴: briefly state what's needed
- If no 🔴 KRs: leave empty

---

### Step 6 — Present the draft for approval

**STOP HERE. Do not write to Notion yet.**

Show Phil the proposed content:

```
## Weekly Update Entry — Data & Platform — [date]

### ⚠️ OKRs at Risk
[proposed content]

### ✅ Wins / Key Accomplishments
[proposed Core Platform wins]
[note: Data team content preserved below]

### 🆘 Help Needed
[proposed content or "empty"]
```

Wait for Phil's explicit approval before writing.

---

### Step 7 — Write to Notion

Use `notion-update-page` with `command: update_content` on the weekly updates page.

The `old_str` must match the exact existing `<tr>` for the Data & Platform row.
The `new_str` replaces it with the updated row containing all three columns.

**CRITICAL**: Preserve the exact `<td>` structure, user mentions, and any existing
Data team content in the Wins column.

---

### Step 8 — Confirm

```
✅ Weekly Update Entry — Data & Platform — [date] — COMPLETE

OKRs at Risk: X flagged (Y 🟡, Z 🔴)
Wins: N Core Platform wins added (Data team content preserved)
Help Needed: [filled / empty]

Page: https://www.notion.so/machinify/Weekly-product-line-updates-2e15356b39718079a60fe8d19906ebae
```

---

## Key IDs & References

| Resource | ID / URL |
|----------|----------|
| Weekly product line updates page | `2e15356b-3971-8079-a60f-e8d19906ebae` |
| Platform Pulse parent page | `2775356b-3971-80e2-874f-c5aa2f135ba5` |
| OKR data source | `collection://1515356b-3971-81d4-824b-000b20ca20c2` |
| OKR Dashboard | `29d5356b-3971-80f2-875b-ecf3af5da112` |

---

## Guardrails

- **Never write without Phil's approval**
- **Never overwrite Data team content** — always prepend Core Platform wins
- **Never re-source from raw data** — consume platform-pulse and OKR dashboard only
- **Match the existing table style exactly** — bold KR names, emoji prefixes, `<br>` separators
- If the platform-pulse for this week hasn't been generated yet, say:
  "No platform pulse found for this week — run `/platform-pulse` first."
- If the weekly update toggle for this week doesn't exist yet, say:
  "No weekly update entry found for [date] — the template may need to be duplicated first."
