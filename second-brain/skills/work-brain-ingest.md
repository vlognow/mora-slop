# Skill: Work Brain Ingest

## Purpose
Process new items in `~/work-brain/raw/` into atomic notes, entity notes, and source notes in Phil's Karpathy-style LLM wiki. Non-destructive, always paraphrasing, always citing.

---

## Trigger
User says something like:
- "run the ingest task"
- "process raw"
- "ingest new material"
- "process the work brain"

---

## Pre-Flight

Read these files in parallel (single message):
1. `~/work-brain/README.md` — the schema (rules, structure, privacy)
2. `~/work-brain/index.md` — what files already exist
3. List `~/work-brain/raw/` (excluding `processed/`) for new items

If `raw/` has no new items, report "Nothing to ingest" and stop.

---

## Workflow

### Step 1 — For each new item in raw/

1. Read the item. For PDFs, extract text. For HTML, convert to markdown.
2. Classify the content type: paper | article | meeting notes | book excerpt | email thread | Slack thread | other.
3. Read enough to understand the main arguments and key terms.

### Step 2 — Extract concepts and entities

1. List every concept (abstract idea) mentioned in the source.
2. List every entity (person, organization, product, vendor, team, technology) mentioned.
3. For each, determine if it's significant enough to warrant a wiki note. Rule of thumb: if it appears more than twice in the source OR is central to the argument, it warrants a note.

### Step 3 — For each significant concept

1. Check if `concepts/{slug}.md` exists (consult `index.md`).
2. If YES:
   - Read the existing file
   - **PROPOSE** the extension to Phil (show the new section you'd add)
   - Only write after approval
3. If NO:
   - **PROPOSE** the new atomic note to Phil (show the draft)
   - Write in Phil's voice (paraphrased, direct, systems-depth)
   - Include cross-references to related existing concepts
   - Only create after approval

### Step 4 — For each significant entity

1. Check if `entities/{slug}.md` exists.
2. If YES: **propose** extending with new facts from this source.
3. If NO: **propose** creating a new entity note.

### Step 5 — Create the source note

1. Create `sources/{source-slug}.md` for this specific source.
2. Include: bibliographic metadata (author, date, URL/path), one-paragraph summary in Phil's voice, 3-5 key claims, "Phil's take" placeholder, list of concept/entity notes this source contributed to.

### Step 6 — Move the raw file

1. `mv ~/work-brain/raw/{file} ~/work-brain/raw/processed/{YYYY-MM-DD}/{file}`
2. Create the date folder if needed.

### Step 7 — Update index.md

1. Add entries for any new files created.
2. Keep entries alphabetical within each section.

### Step 8 — Append to log.md

Add an entry at the TOP (newest first):
```
## [YYYY-MM-DD HH:MM] ingest | {short description of source}
- Read raw/{file}
- Created {N} new notes: {list}
- Extended {N} existing notes: {list}
- Created sources/{source-slug}.md
- Moved raw file to raw/processed/{YYYY-MM-DD}/
```

### Step 9 — Generate ingest report

Produce a summary for Phil:
- What was ingested
- What was created (with links)
- What was extended
- Any FLAG FOR REVIEW items
- Suggested next action

---

## Hard Rules

- **PARAPHRASE in Phil's voice, always.** Never quote more than one sentence at a time from a source.
- **PROPOSE, don't act** for new concept/entity notes and extensions to existing ones. Show Phil the draft. Wait for approval.
- **ACT DIRECTLY** only for: source notes, moving raw files to processed/, updating index.md and log.md.
- **NEVER overwrite** existing concept/entity content — always extend.
- **NEVER delete** a raw source — always move to `processed/{date}/`.
- **NEVER skip** the log.md and index.md updates.
- **NEVER create** a note without a source citation.
- **Privacy:** No credentials, PII, client-confidential material, HIPAA data. Quarantine ambiguous content to `sandbox/` with FLAG FOR REVIEW.

---

## Output
The final message to Phil should be a concise report:
- N sources processed
- N new notes created (proposed or written)
- N existing notes extended (proposed or written)
- List of anything flagged for review
- Next suggested action
