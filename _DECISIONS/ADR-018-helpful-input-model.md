# ADR-018 — /helpful Input Model: Structured Form vs. Raw-Paste Navigator

> **Status:** DRAFT — HELD pending Architect packet from Perplexity Space session
> **Date:** 2026-05-28
> **Commit:** (set at merge)

## D — The Decision

**Sharp question:** Should `arcs.care/helpful` replace its 5-field structured input form with a single raw-context paste field, delegating structure extraction to the engine?

## E — Entity / System

- `arcs-care-local/app/helpful/page.tsx` — input form (5 fields today)
- `arcs-care-local/app/api/helpful/route.ts` — engine route (accepts structured fields, runs HCP operators)
- `supabase: helpful_receipts` table — persists all 6 user-input fields + 9 engine-output fields
- Human Connection Physics system prompt (PRONOIA SPARK PLUG / STATED vs. REVEALED / OPPORTUNITY-COST GUARDRAIL)

## W — Window

**Horizon:** QUARTER  
**Revisit trigger:** First 10 receipts logged — compare raw-paste receipt quality to structured-form receipts. If extraction accuracy < 90% on person_name + tier, fall back to hybrid mode.

## Context

The Dan Pascone loop-close email (sent 2026-05-28) was the highest-fidelity "how can I be most helpful" output produced by ARCS to date. It was generated in Perplexity Space — not through arcs.care/helpful — because the context was an email thread + LinkedIn profile + job post + relationship history. The form's pre-compression requirement was the failure point.

**Core finding:** The instrument is an instrument panel (user pre-assembles data, instrument processes it). The demonstrated use case requires a navigator (user pastes raw signal, system extracts and acts). The cases where pronoia physics matters most — high-context, high-stakes relationship moments — are exactly the cases that resist form-field compression.

**The form IS the cognitive tax it claims to eliminate.** The PRONOIA SPARK PLUG principle is: eliminate the other person's cognitive load. The form transfers that load onto the user before the engine runs, which inverts the value proposition at the hardest cases.

## Options Considered

### Option A — Keep 5-field structured form
- What it is: no change; user pre-compresses context into structured fields
- Pros: simple API contract; no extraction failure mode; fields are always explicit
- Cons: fails at high-context cases (the ones with most value); cognitive tax is the problem we're solving; Perplexity Space remains the better tool for real use

### Option B — Single raw-paste field (replace form)
- What it is: one large textarea ("Paste everything you know — email threads, context, notes"); engine extracts person_name, relationship_stage, context, output_goal, prior_stated, prior_revealed internally before running HCP operators
- Pros: zero pre-compression burden; handles email threads, LinkedIn profiles, meeting notes natively; matches demonstrated Perplexity Space UX; extraction can be shown in UI as a "parsed: [name]" confirmation step
- Cons: extraction can fail or hallucinate (need HOLD gate for low-context input); Supabase schema changes needed (raw_context column; 6 fields become nullable engine-output, not user-input); system prompt needs extraction step before operators

### Option C — Hybrid: raw paste + optional structured fields
- What it is: raw paste is primary; structured fields are shown as an optional "override" if extraction is wrong
- Pros: handles both cases; recoverable from extraction errors without full re-submit
- Cons: more complex UI; "optional fields" often ignored; adds cognitive surface area

## Decision

**Chosen:** Option B (pending Architect ratification) — **DO NOT IMPLEMENT until Architect packet returns from Perplexity Space.**  
**Rationale:** The high-context cases are the valuable ones. Optimizing the form for easy-but-low-value inputs (where the user already knows what to write) misidentifies the job to be done. The extraction failure mode is manageable with a HOLD gate on low-context input (< ~150 chars with no clear person reference).  
**Trade-offs accepted:** Extraction can fail; need explicit fallback copy ("Couldn't extract a person name — can you add more context?"); Supabase schema migration needed; system prompt grows by ~200 tokens for extraction step.

**Architect questions to resolve before implementation:**
1. Exact system prompt addition for reliable extraction step
2. HOLD gate condition for low-context input
3. Whether raw_context becomes the primary stored field (yes) or derived fields are the canonical receipt (decision: raw_context is first-class; extracted fields are engine metadata)
4. Hybrid mode: needed or rejected (lean toward rejected — complexity cost > coverage gain)

## Y — Conviction

**Polarity:** YELLOW  
**Conviction:** MEDIUM  
**Stability:** SHIFTING — pending Architect packet from Perplexity Space session

**Loki test:** The 5-field form forces the user to think through the situation before submitting — which may produce *better* context compression than a raw paste that gets lazily extracted. High-volume users might prefer the structured form because it makes them be precise. Counter: the people who need this instrument most are the ones mid-relationship-crisis who don't have time to compose 5 fields. The form's friction is highest for them.

## Consequences

- `app/helpful/page.tsx` — replace form grid with single textarea + extraction preview chip
- `app/api/helpful/route.ts` — add extraction step to system prompt; accept `raw_context` field; log extracted fields to Supabase
- `helpful_receipts` table — add `raw_context TEXT` column; make 5 input fields nullable
- System prompt addition: extraction step must run BEFORE PRONOIA SPARK PLUG operators; must produce structured JSON block that operators then consume
- UI addition: show extracted fields as confirmation chips ("Detected: Dan Pascone · Warm acquaintance · Goal: loop-close email") before generating → allow one-tap correction

**Implementation pointer:** `arcs-care-local/app/helpful/page.tsx` + `app/api/helpful/route.ts` + Supabase migration (new column `raw_context TEXT`, make 5 fields nullable)
