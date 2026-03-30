---
name: platform-pulse
version: "2.0"
author: phil-mora
tags: [pm, pulse, platform, notion, slack, weekly]
trigger: "Generate the weekly Platform Pulse from weekend updates, GitHub, Jira, and Slack"
inputs: ["week date range (optional)"]
outputs: ["Notion page + Slack post to #product-releases"]
estimated_time_saved: "2-3 hours per week"
---

# Skill: Platform Pulse

## Purpose
Generate the weekly "⚡ Platform Pulse" for the Core Platform team at Machinify.
Produces two outputs:
1. A full Notion page (added under the Platform Weekly Wins section)
2. A condensed Slack post — posted directly to **#product-releases** via Slack MCP

---

## Trigger
User says something like:
- "generate platform pulse"
- "create this week's platform pulse"
- "write the platform pulse for [week]"

---

## Step-by-Step Process

### Step 1 — Determine the week
If the user doesn't specify a date range, use the current date to infer the Monday–Friday range for the most recently completed work week.
Format: `Mon MMM D – Fri MMM D, YYYY` (e.g., `Feb 17–21, 2026`)

### Step 2 — Read the Core Platform Weekend Update (PRIMARY SOURCE)
Query the weekend update database to find the most recent entry:
- **Database view**: `view://1b65356b-3971-8091-9930-000cfa67c5f7`
- Use `notion-query-data-sources` with `mode: view` and `view_url` above
- Take the entry with the most recent `Created` date
- Fetch the full page content using `notion-fetch` with `id: <full notion URL>` (pass the URL as the `id` param — e.g., `id: "https://www.notion.so/3145356b..."`)
- This is your primary source of truth — extract: wins, owners, PRs, incidents, blockers

### Step 3 — Cross-reference GitHub (VERIFY & ENRICH)
Search the `vlognow` org for merged PRs and releases from the week.
Key repos to check (use `github-search_code` or `github-list_commits`):
- `vlognow/onlineDataAnalysis` — core platform (ODA)
- `vlognow/infrastructure` — AWS, k8s infra
- `vlognow/k8s-machinify-apps` — app deployments
- `vlognow/k8s-app-machinify-monitoring` — Grafana/observability
- `vlognow/mac-ui` — frontend
- `vlognow/subro-assistant-bff` — subro backend
- `vlognow/airflow-dags` — data pipelines

Search query pattern: `org:vlognow is:pr is:merged merged:[YYYY-MM-DD]..[YYYY-MM-DD]`

Look for: new dashboards, CLI releases, bug fixes, infra changes, cost savings PRs.

### Step 4 — Cross-reference Jira (VERIFY & ENRICH)
Query Jira for recently updated/closed tickets from the Core Platform team:
- Domain: `machinify.atlassian.net`
- Use `jira_get` with path `/rest/api/3/search/jql` (NOT `/rest/api/3/search` — deprecated)
- **NOTE**: The `labels = "core-platform"` filter often returns zero results — the team does not tag consistently. Try these fallbacks in order:
  1. `project = MAC AND updated >= "YYYY-MM-DD" AND updated <= "YYYY-MM-DD" AND labels = "core-platform"`
  2. `project = MAC AND updated >= "YYYY-MM-DD" AND updated <= "YYYY-MM-DD" AND component = "Core Platform"`
  3. `project = MAC AND updated >= "YYYY-MM-DD" AND updated <= "YYYY-MM-DD" AND assignee in ("charlie.thomas", "chris.pounds", "ashish.gupta", "lina.butler", "revin.guillen")`
- Always use `jq` to filter: `issues[*].{key: key, summary: fields.summary, status: fields.status.name, assignee: fields.assignee.displayName}`
- Extract ticket numbers, summaries, and status changes to validate and add to artifacts

### Step 5 — Read Slack channels directly (ENRICHMENT — Slack MCP is live)
Slack MCP is connected. Read the Core Platform Slack channels directly for the week's date range.
Convert date range to Unix timestamps for `oldest` / `latest` params.

Key channels:
- **#eng-core-platform** (C07F7K8N5CY) — main engineering channel
- **#eng-core-platform-and-one-mora** (C0A9QVBDRQT) — Phil + team, AI tooling & strategy discussions

Use `slack_read_channel` with `response_format: concise` and the week's timestamps.
Extract: incidents mentioned, cross-team asks, AI tooling discussions, anything not in the weekend update.

### Step 6 — Synthesize & Draft Content
Combine all sources. Prioritize:
1. Weekend update page content (source of truth)
2. Slack channel signals (incidents, discussions, tone, anything missed in the update)
3. GitHub PRs that corroborate or add detail
4. Jira tickets as validation

Identify:
- **Major wins** (3–6 items): what shipped + why it matters to the broader org
- **By the numbers**: count of dashboards, PRs, tickets, incidents, etc.
- **Team powerhouses**: who drove what — be specific and generous with credit
- **Production saves**: incidents caught/fixed, cost savings
- **Coming next week**: from "next week" section of weekend update
- **Artifacts**: key PR links, Jira tickets, Notion docs

### Step 7 — Generate Notion Page
Create a new Notion page as a child of the Platform page (`2775356b-3971-80e2-874f-c5aa2f135ba5`), inserting it after the block `30a5356b-3971-8017-8fdc-f0eaac038a6a` (the "Weekly Wins" section heading).

**Page title**: `⚡ Platform Pulse - Week of [DATE RANGE]`

**Notion page structure**:
```
# 📊 By The Numbers
**[N]** [metric description]
**[N]** [metric description]
...

---

# 🚀 Major Wins & Impact

## 1. [Win Title]
**What we shipped**: [concise description]
**Why it matters**: [business/engineering impact for the broader org]
**Owner**: [name]

## 2. [Win Title]
...

---

# 👏 Team Powerhouses
**🏆 [Name]** - [Hero of the week - specific contributions]
**[Name]** - [contributions]
...

---

# 💰 Production Saves
[Incidents resolved, cost savings, etc.]

---

# 🔮 Coming Next Week
- **[Initiative]**: [who, what]
...

---

# 📚 This Week's Artifacts
**Key PRs**:
- [PR Title](url) - brief description

**Jira Tickets**:
- [MAC-XXXX](url)

**Documentation**:
- [Doc title](url)
```

### Step 8 — Generate Slack Post & Post Directly
Write a condensed version for Slack. Match the style and energy of the example below exactly.
Then **post it directly to #product-releases (C06MZABK7J7)** using `slack_send_message` — do not ask Phil to copy-paste.

**CRITICAL — Slack mrkdwn formatting rules** (different from markdown):
- Bold: `*text*` (single asterisks) — NOT `**text**`
- Italic: `_text_` (underscores)
- Code: `` `text` `` (backticks)
- No `##` headers — use `*SECTION TITLE*` with emoji prefix instead
- Bullet points work normally

**Slack post format**:
```
:rocket: Core Platform Weekly Highlights - [DATE RANGE]

[1–2 sentence intro that celebrates the team and any context (short week, big milestone, etc.)]

:[emoji]: *SECTION TITLE IN CAPS*
[2–3 sentence description. Lead with what shipped. Follow with why it matters to engineers across the org.]

:[emoji]: *SECTION TITLE IN CAPS*
[2–3 sentences]

... (3–6 sections total, use relevant Slack emoji)

Huge shoutout to [Hero] (hero of the week!), [Name], [Name], and the entire Core Platform team for [accomplishment].

:page_facing_up: Full Platform Pulse: [notion page url]
```

**Emoji guide** (match to content):
- `:hammer_and_wrench:` — new tools/CLIs
- `:bar_chart:` — dashboards/observability
- `:zap:` — TypeScript/API/SDK work
- `:moneybag:` — cost savings/AWS
- `:whale:` — Docker/containers/devcontainers
- `:shield:` — security/incidents/fixes
- `:rocket:` — major launches
- `:fire:` — performance improvements
- `:broom:` — cleanup/tech debt

---

## Output

1. Create the Notion page — confirm with URL
2. Post the Slack message directly to **#product-releases (C06MZABK7J7)** — return the message link
3. Show Phil both links so he can verify

---

## Style Guidelines
- Write for a **mixed technical audience** — engineers + leadership
- Lead every win with **what shipped**, follow with **why it matters to other teams**
- Be **specific**: name the engineers, link the PRs, cite the numbers
- Tone: energetic, proud, direct — like a great engineering manager who loves their team
- Never use vague phrases like "various improvements" or "ongoing work"
- The Slack post should be ~400–600 words, punchy paragraphs, no bullet overload

---

## Key IDs & References
- Weekend update database view: `view://1b65356b-3971-8091-9930-000cfa67c5f7`
- Platform Pulse parent page: `2775356b-3971-80e2-874f-c5aa2f135ba5`
- Jira domain: `machinify.atlassian.net`
- GitHub org: `vlognow`
- Slack channels:
  - `#product-releases`: C06MZABK7J7 (post destination)
  - `#eng-core-platform`: C07F7K8N5CY (source)
  - `#eng-core-platform-and-one-mora`: C0A9QVBDRQT (source — Phil + team, AI tooling discussions)

---

## Example Slack Output (for style reference)
```
:rocket: Core Platform Weekly Highlights - Feb 17-21, 2026

Despite a short week with mandatory training, Core Platform shipped some game-changing improvements for the entire engineering org:

:hammer_and_wrench: NEW: Machinify Studio CLI
The team launched the `mfy` CLI - now installable via Homebrew (`brew install vlognow/tap/mfy`). This brings Studio functionality directly to your terminal, streamlining developer workflows across all teams. Multiple releases shipping daily as the tool evolves.

:bar_chart: Production Observability Upgrade
6 new Grafana dashboards went live covering critical system metrics. These dashboards enable teams to diagnose production issues in minutes instead of hours - a massive win for incident response and uptime.

:zap: TypeScript Client for ODA
Fixed critical Ploidy bugs that were blocking TypeScript client generation. Frontend teams now have proper type safety when working with ODA - fewer runtime errors, faster feature development.

:moneybag: AWS Cost Savings in Action
Cleaned up unused S3 backups and implemented ECR lifecycle management across dev/staging environments. Real cost savings happening right now, freeing up budget for production infrastructure.

:whale: Devcontainer Implementation
New local development workflow using devcontainers means consistent environments for everyone and faster onboarding for new engineers.

Huge shoutout to Chris (hero of the week!), Ceej, Ashish, Lina, and the entire Core Platform team for making this happen while juggling 7 hours of compliance training.

:page_facing_up: Full Platform Pulse: https://www.notion.so/3105356b39718124b46cd61957dfd9da
```
