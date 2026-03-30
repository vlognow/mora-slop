---
name: daily-digest
version: "2.0"
author: phil-mora
tags: [pm, slack, daily, digest, automation]
trigger: "Generate a daily digest of key Slack channels and post to claude-phil"
inputs: ["time window (auto last 24 hours)"]
outputs: ["Categorized digest posted to Slack"]
estimated_time_saved: "30-45 min per day"
---

# Skill: Daily Digest

## Purpose
Generate a daily digest of Phil's key Slack channels and post it to **#claude-phil**.
Surfaces decisions, action items, things needing Phil's attention, and notable updates — so Phil can start the day informed without reading every channel.

---

## Trigger
User says something like:
- "daily digest"
- "run the daily digest"
- "what did I miss"
- "catch me up on slack"
- Automatically via cron (when session is active)

---

## Channel List

### Core (full read, all threads with replies)
| Channel | ID | Focus |
|---------|----|-------|
| #eng-core-platform | C07F7K8N5CY | Platform eng activity |
| #eng-core-platform-and-one-mora | C0A9QVBDRQT | Platform + Phil |
| #ai-repo-champions | C0APCFFP9J4 | AI Enablement Program |
| #cloud-cost-optimization | C0AB8018UK0 | Cloud cost project |
| #product-releases | C06MZABK7J7 | Pulse posts, releases |
| #eng-studio | C09UMFL4HSQ | Studio eng activity |

### Professional (read messages, follow up on threads mentioning Phil or decisions)
| Channel | ID | Focus |
|---------|----|-------|
| #product-management-team | C06KSTV59HU | PM team |
| #product-staff | C09E5SNMMJT | PM leadership |
| #product-extended-staff | C0AE8P0JLJW | Broader PM group |
| #recruiting_product-phil | C0A9XNFESTD | Phil's recruiting |
| #product-vibe-coding | C09F21NRBEW | Vibe coding initiative |
| #product-factory | C09K11V3FAS | Product Factory |
| #ai-initiative-discussion | C0ALGGKMNG6 | AI initiative (David Levinger) |
| #data-ai-enablement | C0AJN0E16VA | Data AI enablement (Andrey) |
| #generic-rules-engine | C0AKJUASV7V | Rules engine project |

---

## Step-by-Step Process

### Step 1 — Determine the time window
Calculate Unix timestamps for the last 24 hours (or since previous business day if Monday).
Use these as `oldest` and `latest` parameters for `slack_read_channel`.

### Step 2 — Read all Core channels
For each Core channel:
1. Call `slack_read_channel` with the channel ID, `oldest`, and `latest` params, limit 100
2. For any message with thread replies, call `slack_read_thread` to get the full discussion
3. Note: use `response_format: "concise"` for efficiency

### Step 3 — Read all Professional channels
For each Professional channel:
1. Call `slack_read_channel` with the channel ID, `oldest`, and `latest` params, limit 50
2. Only follow threads that mention Phil (`<@U099L4N8GAX>`) or contain decisions/action items

### Step 4 — Analyze and categorize
Sort everything into four buckets:

1. **Needs Your Attention** — direct mentions of Phil, questions awaiting Phil's response, items assigned to Phil, PRs needing review
2. **Decisions Made** — any decision or resolution that affects Phil's work or teams
3. **Notable Updates** — significant progress, blockers, wins, new information
4. **FYI / Low Priority** — interesting but not actionable today

### Step 5 — Format the digest
Write the digest in Slack mrkdwn format:

```
*Daily Digest — [Day, Month Date]*
_Covering [X] channels from the last 24 hours_

*Needs Your Attention*
- [item with channel link]

*Decisions Made*
- [item with channel link]

*Notable Updates*
- [item with channel link]

*FYI*
- [item with channel link]

_[N] channels were quiet (no messages in the last 24 hours)_
```

### Step 6 — Post to #claude-phil
Use `slack_send_message` with:
- `channel_id`: `C0AP3B1EQK0`
- The formatted digest as the message

If the digest exceeds 4000 characters, split into two messages: first with Needs Attention + Decisions, second with Updates + FYI.

### Step 7 — Surface follow-ups
If there are items needing Phil's attention, ask Phil directly in the Claude Code session whether he wants to act on any of them right now.

---

## Important Notes
- Do NOT include DM or group DM content in the digest — those are private
- Do NOT summarize messages Phil himself sent — he knows what he said
- DO include messages that mention Phil or reply to Phil's messages
- DO link to specific messages using Slack permalinks where relevant
- Keep each bullet to 1-2 lines max — this is a scan, not a novel
- If a channel had zero messages in the window, don't list it individually — just count quiet channels at the bottom
