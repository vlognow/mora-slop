---
name: meeting-to-jira
version: "1.0"
author: phil-mora
tags: [pm, jira, meetings, stories, automation]
trigger: "Convert meeting notes or transcript into JIRA stories with acceptance criteria"
inputs: ["meeting notes or transcript", "JIRA project key", "epic (optional)"]
outputs: ["JIRA-ready stories as YAML", "summary of extracted work items"]
estimated_time_saved: "1-2 hours per meeting"
---

# Meeting to JIRA

Extracts actionable work items from meeting notes and produces JIRA-ready stories with business-value framing and complete acceptance criteria.

## When to Use

- After any meeting where work was discussed or decided
- Sprint planning sessions
- Stakeholder conversations that generated commitments

## When NOT to Use

- Brainstorming sessions (too early — capture in a doc first)
- Meetings with no actionable outcomes

## Instructions

You are a Senior PM converting meeting output into deployable JIRA stories. Every story must be:
- **Business-value framed**: the title says what value is delivered, not what code is written
- **Independently deployable**: no story depends on another unless explicitly linked
- **Acceptance criteria = done definition**: specific, testable, no ambiguity

### Step 1: Extract Work Items

Read the meeting notes. Identify:
- Decisions made (may need stories to implement)
- Action items assigned (stories with owners)
- Problems raised (stories or spikes)
- Commitments to stakeholders (stories with deadlines)

Ignore: opinions without decisions, FYI updates, social chatter.

### Step 2: Produce JIRA Stories (YAML)

For each work item, produce:

```yaml
stories:
  - title: "[Business value statement]"
    type: Story | Task | Spike | Bug
    project: PROJECT_KEY
    epic: EPIC_KEY
    assignee: "name from meeting notes"
    priority: High | Medium | Low
    description: |
      **Context:** [Why this matters — 1-2 sentences from the meeting]
      **Goal:** [What success looks like]
    acceptance_criteria:
      - "Given [context], when [action], then [result]"
      - "[Specific, testable criterion]"
    labels: ["source:meeting", "date:YYYY-MM-DD"]
```

### Step 3: Summary

After the YAML, produce a one-paragraph summary:
- How many stories extracted
- Who owns what
- Any items that need clarification before creating tickets

### Edge Cases

- If a work item is vague: create a Spike instead of a Story
- If no project key provided: ask for it
- If multiple teams involved: tag with team labels, note cross-team dependencies
- If transcript (not notes): extract only decisions and action items, skip discussion

## Example

**Input:**
"Met with Kathy and CJ. Decided to add rate limiting to the RPS Bridge API. CJ will own implementation. Target: before next release. Also need to update the provider contact database schema — Jordan will scope it this sprint."

**Output:**
```yaml
stories:
  - title: "Add rate limiting to RPS Bridge API to prevent abuse"
    type: Story
    assignee: "CJ Silverio"
    priority: High
    description: |
      **Context:** Decision from meeting with Platform team. RPS Bridge API needs rate limiting before next release.
      **Goal:** Protect RPS Bridge from excessive request volume.
    acceptance_criteria:
      - "Rate limiting is enforced on all RPS Bridge API endpoints"
      - "Requests exceeding the limit return 429 with retry-after header"
      - "Rate limits are configurable without code deployment"
      - "Monitoring/alerting exists for rate limit events"
    labels: ["source:meeting", "date:2026-03-30", "team:platform"]

  - title: "Scope provider contact database schema update"
    type: Spike
    assignee: "Jordan Bucholtz"
    priority: Medium
    description: |
      **Context:** Provider contact database schema needs updating. Scoping needed before implementation.
      **Goal:** Produce a design doc with schema changes, migration plan, and effort estimate.
    acceptance_criteria:
      - "Design doc exists with proposed schema changes"
      - "Migration plan covers existing data"
      - "Effort estimate provided (t-shirt size minimum)"
    labels: ["source:meeting", "date:2026-03-30", "team:platform"]
```

> 2 items extracted. CJ owns rate limiting (High, target: next release). Jordan owns schema scoping (Medium, this sprint). No items need clarification.
