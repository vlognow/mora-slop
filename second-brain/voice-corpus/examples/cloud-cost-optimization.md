# Voice Corpus: #cloud-cost-optimization

Source: Slack channel #cloud-cost-optimization (C0AB8018UK0)
Time range: 2025-10-01 to 2026-04-17
Subject: Phil Mora (U099L4N8GAX)
Total messages extracted: 13
Extraction date: 2026-04-14

---

## Messages

### MSG-CCO-001
- **Date:** 2026-02-05 07:44:02 EST
- **Type:** Thread reply
- **Category:** DIRECTION
- **Topic:** Setting up recurring cadence for cloud cost initiative
- **Context:** Replying in thread to Kathy Kwan's meeting notes post; David Levinger and Kathy tagged for action
- **Text:**
> ^^ @kathy.kwan @david.levinger we discussed a weekly i'll set that up today.

---

### MSG-CCO-002
- **Date:** 2026-02-05 13:13:34 EST
- **Type:** Thread reply
- **Category:** DIRECTION
- **Topic:** Establishing recurring meeting cadence to maintain initiative priority
- **Context:** Replying after David Levinger shared detailed dev/staging cost breakdown ($110K/month); Phil reinforcing urgency
- **Text:**
> ^^^ I want to have a weekly so that we keep this on top of the pile

---

### MSG-CCO-003
- **Date:** 2026-03-02 15:12:02 EST
- **Type:** Top-level
- **Category:** EXPLANATION
- **Topic:** Weekly cloud cost pulse update -- progress report to channel
- **Context:** Structured status update covering ticket progress, verification pipeline, new scope, and team recognition
- **Text:**
> :moneybag: Cloud Cost Pulse - Week of Feb 23-27, 2026
> Steady progress week -- three tickets sitting in Verification In Progress and the cluster metrics pipeline hitting staging. The big unlock comes Monday when Ananth's changes land in prod.
> :white_check_mark: SHIPPED / IN VERIFICATION
> - MAC-27660 (Ananth) -- Cluster memory/CPU/disk metrics to staging Feb 26, prod target Mar 2. This is the data foundation for everything overprovisioning-related.
> - MAC-27492 (Ananth) -- Useless snapshot detection dashboard live since Feb 16; 30-day window fills ~March 18.
> - MAC-26976 (Ashish) -- Spark job cost dashboard in verification; re-run queued once MAC-27660 hits prod.
> :arrows_counterclockwise: IN PROGRESS
> - MAC-27550 (Chris Pounds) -- S3 lifecycle fixes and dev/staging cleanup ongoing. Chris also requested prod CastAI access for full cost visibility.
> - MAC-27557 (Ashish) -- Manual cluster overprovisioning assessment in Code Review; unblocks once MAC-27660 in prod Mar 2.
> - System job cost attribution (Ashish) -- Started investigation; reached out to DE to set costTrackingId on service account pipelines.
> :mag: SNAPSHOT SCOPE EXPANDED
> Two new tickets filed this week scoping the next phase of snapshot analysis: who's spending most (MAC-27555) and which jobs never finish (MAC-27556). Data from the live snapshot dashboard starts getting actionable ~March 18.
> :trophy: HEROES OF THE WEEK
> - Ananth Rao -- Cluster metrics pipeline to staging; two new snapshot analysis tickets scoped and filed
> - Ashish Gupta -- System job attribution investigation kicked off; cross-team coordination on metrics
> :bar_chart: By the numbers: 3 tickets in verification | 2 new tickets scoped | $10,600/mo cumulative savings (ECR confirmed + S3 in-flight) | Spark cost data arrives with prod deploy Mar 2

---

### MSG-CCO-004
- **Date:** 2026-03-03 15:35:31 EST
- **Type:** Top-level
- **Category:** DIRECTION
- **Topic:** Pulling JX Bell into the channel for cost documentation work
- **Context:** Prasanna noted that Joshua Caudill couldn't find docs on how to discover costs of SQL jobs; Phil tagging JX Bell to join
- **Text:**
> ^^^ @JX Bell ^^^^

---

### MSG-CCO-005
- **Date:** 2026-03-03 15:36:09 EST
- **Type:** Thread reply
- **Category:** CELEBRATION
- **Topic:** Reacting to Prasanna's PR showing costs in the UI
- **Context:** Prasanna Ganesan announced he pushed a PR to show costs in the UI -- a key visibility feature for the initiative
- **Text:**
> OOOH THIS IS HUGE - thank you @Prasanna Ganesan

---

### MSG-CCO-006
- **Date:** 2026-03-17 21:48:42 EDT
- **Type:** Top-level
- **Category:** EXPLANATION
- **Topic:** Weekly cloud cost pulse update -- quiet week, awaiting data maturity
- **Context:** Structured status update noting no progress but flagging that the 30-day snapshot data window is about to become actionable
- **Text:**
> :moneybag: Cloud Cost Pulse - Week of Mar 10-17, 2026
> Quiet week across the board -- no tickets closed, no cost-related PRs merged, no Slack activity in this channel. The good news: our snapshot 30-day data window hits maturity tomorrow (Mar 18), which should unlock action on the highest-priority cost lever.
> :white_check_mark: SHIPPED / COMPLETED
> - No tickets moved to Done this week
> :arrows_counterclockwise: IN PROGRESS
> - MAC-27492 Useless snapshot detection (Ananth Rao) -- 30-day data window actionable Mar 18 :eyes:
> - MAC-27660 Cluster overprovisioning server (Ananth Rao) -- Verification, in prod since Mar 2
> - MAC-26976 Spark job costs dashboard (Ashish Gupta) -- Verification, dashboard live since Mar 4
> - MAC-27557 Manual cluster assessment (Ashish Gupta) -- Code Review, 5th week :warning:
> - MAC-27550 Dev/staging spend reduction (Chris Pounds) -- In Progress, no update in 3 weeks
> :trophy: HEROES OF THE WEEK
> - Quiet week -- looking forward to celebrating snapshot analysis results next week :rocket:
> :bar_chart: By the numbers: 0 tickets completed | 0 PRs merged | $10.6K/mo savings (unchanged for 3 weeks) | Baseline $400K/mo

---

### MSG-CCO-007
- **Date:** 2026-03-23 13:09:18 EDT
- **Type:** Top-level (thread parent)
- **Category:** QUESTION
- **Topic:** Requesting confirmed savings data for Q1 reporting
- **Context:** Phil asking David Levinger for official cost savings number after Q1 review -- he could only report $11K/month confirmed
- **Text:**
> @david.levinger good morning :wave: do you have a good estimate of the cost savings we've achieved this quarter? During Q1 review last week, I could only report the savings that I knew were confirmed with is about $11K/month --- I suspect the number is higher but I didn't have a more "official" source of accurate data.

---

### MSG-CCO-008
- **Date:** 2026-03-23 13:25:59 EDT
- **Type:** Thread reply
- **Category:** SOCIAL
- **Topic:** Acknowledging David Levinger's commitment to share data while traveling
- **Context:** Levinger said he'd share his cost savings tracking sheet but was boarding a flight
- **Text:**
> okay super and thank you, safe travels!

---

### MSG-CCO-009
- **Date:** 2026-03-24 13:12:22 EDT
- **Type:** Top-level
- **Category:** DIRECTION
- **Topic:** Following up on prod access for Chris Pounds to unlock CastAI savings analysis
- **Context:** CJ Silverio had just posted about CastAI being in read-only mode across clusters; Phil pushing to get Chris access agreed in February
- **Text:**
> ^^^ @Chris Pounds do you have access to prod ? I think that was an agree action item from one of our discussions in february -- I am eager to see the savings (and potential) from that angle.

---

### MSG-CCO-010
- **Date:** 2026-03-30 16:51:26 EDT
- **Type:** Top-level
- **Category:** DIRECTION
- **Topic:** Nudging David Levinger for cost savings data promised earlier
- **Context:** Phil following up on the March 23 request for official savings numbers; polite but persistent
- **Text:**
> also @david.levinger good afternoon :wave:
> Gentle nudge on this: https://machinify.slack.com/archives/C0AB8018UK0/p1774285758904809

---

### MSG-CCO-011
- **Date:** 2026-04-01 15:45:10 EDT
- **Type:** Top-level (thread parent)
- **Category:** QUESTION
- **Topic:** Probing whether reported savings are recurring or one-time, and how they compare to cost growth rate
- **Context:** David Levinger had shared savings data; Phil immediately challenging the framing to understand if it's meaningful relative to growth
- **Text:**
> @David Levinger thank you -- is that a recurring charge or fixed savings, and how does it compare against the rate of growth of cost for "cloud" --

---

### MSG-CCO-012
- **Date:** 2026-04-01 16:20:33 EDT
- **Type:** Thread reply
- **Category:** POSITION
- **Topic:** Arguing for measuring savings relative to cost growth rate rather than absolute reduction
- **Context:** After Levinger confirmed cloud spend grows faster than savings; Phil articulating his analytical framework for how to measure the initiative
- **Text:**
> yes. my thinking is to understand the rate of growth of the spending and prove that by removing all the potential for "abuse" (we discussed that this quarter) we are slowing the organic rate of growth. It fells to me more accurate than "we're reducing the expense by x%" which in absolute would be right but relative to the "ever" increasing expense might not be a good metric to look at?

---

### MSG-CCO-013
- **Date:** 2026-04-01 16:22:19 EDT
- **Type:** Thread reply
- **Category:** QUESTION
- **Topic:** Confirming total savings figure and attributing it to specific work
- **Context:** Continuing the thread on savings measurement; Phil pinning down the exact number and its source
- **Text:**
> So basically rn we are at approx $245K fixed savings for 2026 and this feels like this was only coming from the "scrub" that Chris Pounds did in February correct?
