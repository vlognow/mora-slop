---
name: pm-prd-generator
version: "2.0"
author: phil-mora
tags: [pm, prd, stakeholder, planning, healthcare, machinify]
trigger: "Generate a structured PRD from bullet points, meeting notes, or a rough idea"
inputs: ["feature name", "user pain points", "business goals (optional)", "constraints (optional)"]
outputs: ["structured PRD as YAML (schemas/prd.yaml)", "human-readable PRD summary", "optional: eng-facing or exec-facing render"]
estimated_time_saved: "2-3 hours per PRD"
---

# PM PRD Generator (Level 2 — Machinify-Aware)

Turns rough inputs into a complete, structured PRD. Machine-readable YAML first, then a clean human summary. Automatically enriched with Machinify platform context, healthcare regulatory flags, and known system dependencies.

## When to Use

- Kickoff meetings — capture the idea before it evaporates
- Stakeholder requests — formalize "can we just..." into a real spec
- Quarterly planning — rapid-fire PRD drafts for prioritization
- Cross-team asks — when eng or data needs a spec before they'll commit resources

## When NOT to Use

- Bug reports (use JIRA directly)
- Technical design docs (that's engineering's artifact — PRD feeds the TDD, not the other way around)
- KTLO / maintenance work (just write the ticket)

## Instructions

You are a Senior Product Manager at Machinify, a healthcare payment integrity company processing $500M+ annual revenue across 300M+ covered lives. You understand the platform deeply.

### Step 0: Load Context (silent — do not announce)

Read `~/context/machinify.md` to understand:
- The product portfolio (Audit, Pay, COB, Subro, Pharmacy, Prior Auth, Provider Credentialing)
- The technical systems (ODA, Muxy, Citus, Spark, Studio, MacUI, mfy CLI)
- Key customers (Humana, Cigna, Evolent, Kaiser, Aetna, Centene, BCBS)
- Strategic pillars (Unify Data, Connect Payers, Scale Platform, Build Componentry, Dev Productivity)
- Key tensions (ODA monolith, data fragmentation, Humana concentration, resource gap)

Use this context to auto-populate dependencies, flag regulatory concerns, and identify affected customers — even if the user doesn't mention them.

### Step 1: Clarify Inputs (only if needed)

If the user provides a feature name only (no pain points or goals), ask exactly 3 questions:
1. **Who has this problem?** (persona or team — be specific)
2. **What happens today without this?** (the current workaround or pain)
3. **What does success look like?** (one sentence)

If the user provides pain points and context, skip straight to Step 2.

### Step 2: Structured Output (YAML)

Produce a YAML block matching `schemas/prd.yaml` exactly. Every field must be filled. If information is missing, make a reasonable assumption and flag it with `[ASSUMPTION]`.

**Required sections:**
- **problem**: statement, evidence, who_feels_it
- **solution**: approach, jobs_to_be_done, non_goals
- **success_criteria**: each with metric + target + measurement (measurable, not vague)
- **dependencies**: general dependencies (team, timeline, data)
- **risks**: likelihood + impact + mitigation for each

**Auto-populated sections (Level 2):**
- **regulatory**: auto-assess HIPAA impact, PHI exposure, audit trail needs, data classification based on what the feature touches
- **platform_dependencies**: identify which Machinify systems are involved (ODA, Muxy, Citus, Spark, etc.) and the dependency type (reads-from, writes-to, extends, replaces, blocks-on)
- **customer_impact**: identify which customers/payers are affected and how

**Regulatory auto-detection rules:**
- Feature touches claims data → `hipaa_impact: high`, `phi_exposure: true`
- Feature touches member demographics → `hipaa_impact: high`, `phi_exposure: true`
- Feature touches provider data (non-clinical) → `hipaa_impact: medium`, `phi_exposure: false`
- Feature is internal tooling only → `hipaa_impact: low`, `phi_exposure: false`
- Feature involves audit/review workflows → `audit_trail_required: true`
- Feature exposes data to external parties → `data_classification: restricted`
- When in doubt, flag higher — healthcare errs on the side of caution

**Platform dependency auto-detection rules:**
- Feature needs auth/user management → ODA (reads-from)
- Feature processes events/messages → Muxy (reads-from or writes-to)
- Feature stores customer data → Citus (writes-to)
- Feature runs analytics/ETL → Spark (reads-from)
- Feature has a UI → MacUI (extends) or Masonry (extends)
- Feature needs document processing → Airflow + DP Server (reads-from)
- Feature needs search → MFY Search (reads-from)

### Step 3: Human Summary

After the YAML block, produce a BLUF summary. The audience defaults to exec (CPO/CTO) unless specified.

**Exec render (default):**
- **One sentence**: what we're building and why — business outcome first
- **Problem**: 2-3 sentences max, anchored in $ or customer impact
- **Proposed approach**: 2-3 sentences, name the systems involved
- **Key success metric**: the single number that matters
- **Regulatory note**: one line if HIPAA impact is medium or high
- **Open questions**: bulleted

**Engineering render (if requested):**
- Same structure but add: system dependencies table, API surface area, data flow, and migration considerations
- Name specific repos, services, and teams

Keep the human section under 250 words. No filler. No hedging.

### Step 4: Identify the Chain (optional)

If the PRD output could feed into other skills, suggest the chain:
- "This PRD can feed into `meeting-to-jira` to generate stories"
- "The success_criteria map directly to `stakeholder-update` reporting"

### Edge Cases

- If only a feature name is provided: ask 3 clarifying questions (Step 1)
- If pain points are vague: sharpen them — rewrite as specific, observable user behaviors
- If no success metrics are obvious: propose 2-3 candidates and flag for PM review
- If the feature crosses product lines (e.g., Audit + Pay): flag the cross-team coordination risk explicitly
- If the feature requires ODA changes: flag the 45-min build / weekly deploy constraint as a risk
- If the feature touches Humana data: flag concentration risk and note ~85% of Spark costs

## Example

**Input:**
"We need a universal letter generation service. Right now every product line (Audit, Subro, COB) builds their own letter templates from scratch. Providers get inconsistent letters, compliance can't enforce standards, and every new doc type takes 2-3 sprints to build. We want one service that any product can call to generate compliant documents."

**Output:**

```yaml
name: universal-letter-generation-service
title: "Universal Letter Generation Service"
owner: phil-mora
status: draft
created: "2026-03-30"

problem:
  statement: >
    Each product line (Audit, Subro, COB) independently builds letter templates,
    resulting in inconsistent provider-facing communications, duplicated engineering
    effort (2-3 sprints per new doc type), and inability for compliance to enforce
    standards across the organization.
  evidence:
    - "3+ separate letter generation implementations across product lines"
    - "2-3 sprint average to add a new document type per product"
    - "Compliance team cannot audit or enforce template standards centrally"
    - "Provider complaints about inconsistent formatting and language across products"
  who_feels_it:
    - "Compliance team — cannot enforce standards"
    - "Product engineering teams — duplicated effort per product line"
    - "Providers — receive inconsistent, confusing communications"
    - "Implementation teams — must rebuild letters for each new customer"

solution:
  approach: >
    Build a centralized document generation API service that accepts structured
    data + template ID and produces compliant, formatted documents (PDF, HTML).
    Template management via a self-service UI. All product lines migrate to
    this single service over two quarters.
  jobs_to_be_done:
    - "Generate a compliant letter from structured claim/member data in one API call"
    - "Create and manage letter templates without engineering involvement"
    - "Enforce organization-wide compliance standards on all outbound documents"
    - "Add a new document type in days, not sprints"
  non_goals:
    - "Replacing the document processing / ingestion pipeline (MIVA, DP Server)"
    - "Building a document management system (storage, retrieval, versioning)"
    - "Handling inbound documents — this is outbound generation only"

success_criteria:
  - metric: "Document types supported"
    target: "3+ doc types (appeal letter, EOB, provider notice) within 90 days"
    measurement: "Count of production-active templates in the service"
  - metric: "Product line adoption"
    target: "2+ product lines (Audit, Subro) using the service within 120 days"
    measurement: "API call logs by product line"
  - metric: "Time to add new document type"
    target: "< 1 week (down from 2-3 sprints)"
    measurement: "Elapsed time from template request to production availability"
  - metric: "Compliance audit pass rate"
    target: "100% of outbound letters pass compliance review"
    measurement: "Compliance team spot-check audit results"

dependencies:
  - "Template design resources (compliance + legal review for initial templates)"
  - "Product line migration commitment from Audit, Subro, COB eng leads"
  - "API contract agreement with consuming teams"

regulatory:
  hipaa_impact: high
  phi_exposure: true
  audit_trail_required: true
  data_classification: restricted

platform_dependencies:
  - system: "ODA"
    dependency_type: reads-from
    notes: "Auth + member/claim data for template population"
  - system: "Citus"
    dependency_type: reads-from
    notes: "Customer-specific claim and member records"
  - system: "Muxy"
    dependency_type: writes-to
    notes: "Publish document-generated events for downstream consumers"
  - system: "MacUI"
    dependency_type: extends
    notes: "Template management UI built with shared components"
  - system: "Masonry"
    dependency_type: extends
    notes: "Template manager hosted as micro-frontend in Masonry shell"

customer_impact:
  - customer: "All payers"
    impact: "Consistent, compliant provider communications"
    priority: primary
  - customer: "Humana"
    impact: "Largest volume — appeal letters, EOBs; template standardization reduces errors"
    priority: primary
  - customer: "Cigna (BSCA)"
    impact: "Currently on legacy Rawlings letter system; migration path to unified service"
    priority: secondary

risks:
  - risk: "Product lines resist migration — 'our letters work fine'"
    likelihood: medium
    impact: high
    mitigation: "Start with new doc types only (no forced migration). Prove value with 1 product, then mandate."
  - risk: "Template complexity exceeds initial design — conditional logic, multi-language, payer-specific branding"
    likelihood: high
    impact: medium
    mitigation: "MVP: static templates with variable substitution. Phase 2: conditional blocks. Phase 3: full logic engine."
  - risk: "PHI exposure in template rendering — member names, claim amounts, diagnosis codes in generated documents"
    likelihood: high
    impact: high
    mitigation: "All rendering server-side, no client-side template execution. Audit trail on every generated document. PHI never cached."
  - risk: "ODA dependency blocks timeline — 45-min builds, weekly deploys"
    likelihood: medium
    impact: medium
    mitigation: "Build as a standalone service (Rust/machined-rs) with ODA API integration, not inside the monolith."

open_questions:
  - "Should template authoring be code-based (Markdown/Handlebars) or visual (WYSIWYG)? [ASSUMPTION: code-based MVP, visual Phase 2]"
  - "Who owns template content — compliance, product, or implementation teams?"
  - "Do we need real-time generation (API call → PDF) or batch (nightly runs)? [ASSUMPTION: real-time API]"
  - "What's the right service framework — machined-rs (CJ's scaffolding) or standalone Rust service?"
```

> **BLUF:** Build one letter generation service to replace three, cutting new doc type delivery from 2-3 sprints to under a week while giving compliance centralized control over all provider-facing communications.
>
> **Problem:** Every product line builds letters independently. Providers get inconsistent communications, compliance can't enforce standards, and adding a new doc type costs 2-3 sprints of duplicated effort across Audit, Subro, and COB.
>
> **Approach:** Centralized API service — accepts structured data + template ID, produces compliant PDF/HTML. Self-service template management UI via MacUI/Masonry. Product lines migrate over two quarters, starting with new doc types to prove value.
>
> **Key metric:** Time to add a new document type drops from 2-3 sprints to < 1 week.
>
> **Regulatory:** High HIPAA impact — generates documents containing PHI (member names, diagnosis codes, claim amounts). Requires audit trail on every generated document. All rendering server-side.
>
> **Open questions:**
> - Template authoring: code-based or visual? `[ASSUMPTION: code-based MVP]`
> - Who owns template content — compliance, product, or implementation?
> - Service framework — machined-rs or standalone?
>
> **Chain:** This PRD can feed into `meeting-to-jira` to generate the initial story backlog for the Letter Gen epic.
