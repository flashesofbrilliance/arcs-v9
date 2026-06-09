# ADR-024 — resume.arcs.care Architecture Gates

> **Status:** DECIDED
> **Date:** 2026-06-09
> **Governs:** New `resume.arcs.care` surface — all build decisions downstream reference this ADR

---

## D — The Decision

Two architecture gates resolved before any build begins on `resume.arcs.care`:

1. **Scan Layer UX** — what does the user experience between "paste resume + JD" and landing at `/compass`?
2. **Instance Isolation** — how is each job opportunity quarantined at the web layer?

---

## E — Entity / System

- `resume.arcs.care` — new standalone Next.js app (new Vercel project, new repo)
- Supabase `arcs_app` — shared DB instance; opportunity isolation enforced via RLS
- `arcs-claude-project-scaffold` — Layer 1 Claude Project template (per-opportunity thinking layer)
- `arcs-intel-protocol/instances/` — live opportunity instances following the scaffold
- `arcs-v9` (app.arcs.care) — existing compass/brief/prep machinery; **not forked**, referenced

---

## W — Window

**Horizon:** SPRINT (build begins immediately after this ADR)
**Revisit trigger:** First 10 real opportunities processed; or if scan latency exceeds 8 seconds (triggers reconsideration of background vs. blocking pattern)

---

## Gate 1 — Scan Layer UX

**Decision: Option B with twist — input/routing page, scan output pre-injected into compass**

The scan is upstream fuel, not a destination. User flow:

```
resume.arcs.care/
  ↓ user pastes resume + JD + optional alternatives → hits "Scan"
  ↓ Claude scan runs (~3–6s, blocking with progress indicator)
  ↓ scan output written to Supabase (opportunityId scoped)
  ↓ auto-route to /compass/[opportunityId]

/compass/[opportunityId]
  ↓ loads scan output on mount
  ↓ pre-filled question: "Given [role] at [company] vs [alternatives], is this worth pursuing?"
  ↓ collapsible "Signal Brief" panel at top (fit score + recruiter altitude + resonance + north star)
  ↓ user reviews pre-fill, edits if needed, runs compass → DEWY receipt

/brief/[receiptId]
  ↓ full Profile Scan document layout lives here (UIKit sidebar-nav pattern)
  ↓ scan cartography + compass output combined into rich artifact
```

**Why not Option A (document view as primary surface):**
The scan is calibration infrastructure. Making it a destination adds a navigation step between the user's question ("is this worth it?") and the compass that answers it. The full artifact belongs at `/brief` where deep cartography is expected and earned.

**The Signal Brief panel** at `/compass`:
- Collapsible accordion, collapsed by default
- Shows: Fit Score (0–100) · Recruiter Altitude · Rhetorical Resonance · North Star
- Renders in DEGRADED resolution until compass runs (scan confidence ≠ compass receipt confidence)

---

## Gate 2 — Instance Isolation

**Decision: Option B — single Vercel deployment, `opportunityId`-scoped RLS**

```
resume.arcs.care (one Vercel project)
  /[opportunityId]/...    ← all routes scoped by opportunityId in URL + DB
  
Supabase RLS: policy on all tables = (userId, opportunityId) composite key
  - No row readable unless session userId + opportunityId match
  - opportunityId is a UUID generated at scan creation time
  - Never guessable; no sequential IDs in URLs
```

**Why not Option A (separate deployments per opportunity):**
The Claude Project instances (Layer 1) achieve quarantine via directory structure — not separate Claude accounts. The web layer mirrors that mental model. Isolation is a data concern, not an infrastructure concern. Separate deployments would create ops overhead (separate env configs, separate Vercel projects, separate DB connections) with no security benefit that RLS doesn't already provide.

**Layer 1 / Layer 2 relationship:**
Each opportunity has both:
- A **Claude Project instance** (`arcs-intel-protocol/instances/[company]-[date]/`) — the thinking layer, following the scaffold, quarantined by directory
- A **web record** in Supabase (`opportunities` table, scoped by `opportunityId`) — the persistence layer, quarantined by RLS

These are parallel, not hierarchical. The Claude Project writes artifacts (recoil reports, briefs, receipts) as markdown files. The web app reads/writes structured data. They share the `opportunityId` as the common key.

---

## Tributary Resolutions (three pre-answered sub-decisions)

### T1 — Scan Trigger

**Decision: Auto-run on page load when `opportunityId` is present in the URL**

If the JD is not yet stored, the page shows a single-field paste input before triggering the scan. No manual "Scan" button on the happy path — the URL param is the trigger. If the user arrives at `/scan/[opportunityId]` with a pre-registered opportunity, the scan starts immediately on mount (streaming status). This matches the Layer 1 mental model: creating an opportunity instance and arriving at the scan page are the same atomic action.

**Edge case:** First visit with no URL param → input surface (paste resume + JD + alternatives). On submit, `opportunityId` is minted, written to URL, and scan auto-fires.

### T2 — RLS Policy Shape

**Decision: `(userId, opportunityId)` composite key**

Single `opportunityId` alone is insufficient — a UUID is not a secret, and a logged-in user should never be able to read another user's opportunity even if they somehow obtain the ID. Composite key: `auth.uid() = userId AND opportunity_id = [param]`. This is consistent with ADR-008 (RLS deny-all baseline) and ADR-001 (auth at app layer, not Supabase auth).

**Implementation note:** Since Prisma connects as postgres superuser (bypasses RLS per ADR-008), the composite-key enforcement is at the **API route layer** — every `/api/` handler for resume.arcs.care must filter by `(session.userId, opportunityId)`. RLS is a backup, not the primary gate.

### T3 — Compass Pre-fill Contract

The scan layer writes one `opportunities` row to Supabase. The `/compass/[opportunityId]` route reads it on mount and injects into the compass form + API call context.

**Fields the scan writes (table: `opportunity_scans`):**

```typescript
interface OpportunityScanOutput {
  opportunity_id:       uuid       // generated at scan creation
  user_id:              uuid       // session userId
  created_at:           timestamp

  // Injected into DEWY compass
  fit_score:            number     // 0–100, vector collision score
  recruiter_altitude:   "low" | "mid" | "high"   // inferred from JD signal density
  rhetorical_resonance: "analytical" | "relational" | "executional" | "visionary"
  north_star_signal:    string     // 1–2 sentence synthesis of what they're really hiring for

  // Surfaced in Signal Brief accordion (not injected into form)
  fit_breakdown:        jsonb      // per-dimension scores
  silence_map:          jsonb      // JD sections with low signal (what they didn't say)
  raw_jd_text:          text

  // Compass pre-fill
  prefilled_question:   string     // e.g. "Given the Figma Code org role vs. Deloitte FDE and JPMorgan DeFi, is this worth the investment of time and effort?"

  // Render metadata
  scan_confidence:      number     // 0–100; drives Signal Brief render resolution
}
```

**What the compass receives from pre-fill:**
- `question` field pre-populated with `prefilledQuestion` (user-editable before submission)
- `prep` context pre-populated with: stakes inferred from `fitScore`, window inferred from `alternatives[].stage`
- Signal Brief panel populated from `fitScore` + `recruiterAltitude` + `rhetoricalResonance` + `northStar`

The compass route POST to `/api/compass` includes the `opportunityId` — every receipt created from this opportunity is linked back to the scan record.

---

## FMEA

| Failure mode | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Scan latency > 8s causes user drop-off | MEDIUM | HIGH | Show streaming progress ("Analyzing fit… mapping altitude… generating north star…"); 8s hard timeout → partial output + manual override |
| Pre-filled question is wrong/generic | MEDIUM | MEDIUM | Question is fully editable before compass runs; user always has override |
| opportunityId collision | VERY LOW | HIGH | UUID v4; statistically impossible but add uniqueness constraint at DB level |
| RLS bypass at API layer | LOW | HIGH | Each API handler must validate `(session.userId, opportunityId)` before any DB read/write |
| Claude Project instance and web record diverge (different opportunityId) | MEDIUM | LOW | Convention only for v1: same opportunityId used as folder name in Layer 1 instances |

---

## Build Sequence (from this ADR)

```
1. New repo: arcs-resume (or resume-arcs-care)
   └─ Next.js 16 · Prisma 7 · Supabase · Auth.js v5 (same stack as arcs-v9)
   └─ resume.arcs.care Vercel project

2. Supabase migration: `opportunity_scans` table (T3 schema above) — ADR-025

3. Input surface: resume.arcs.care/ (paste resume + JD + alternatives → Scan)

4. Scan API: POST /api/scan → Claude call → write OpportunityScanOutput → redirect

5. Compass surface: /compass/[opportunityId] (pre-fill contract T3)
   └─ Signal Brief collapsible panel
   └─ Pre-populated question (editable)
   └─ Calls existing compass pipeline logic (port from arcs-v9 or call API)

6. Brief surface: /brief/[receiptId] (UIKit sidebar-nav Profile Scan layout)

7. Prep surface: /prep/[receiptId] (port from arcs-v9)

8. Receipt surface: /receipt/[receiptId] (ex-ante bet)

9. Recoil surface: /recoil/[receiptId] (port static page → dynamic from DB)

10. ADR-025: resume.arcs.care Supabase schema (opportunities table migration)
    ADR-026: resume.arcs.care scan Claude prompt spec
```

---

---

## Open Questions (Pre-Build — resolved in principle, implementation TBD)

1. **Scan streaming UX:** Does `/scan` show a progress bar, streaming text, or a spinner? → Recommendation: streaming status messages ("Scoring fit vectors… Mapping recruiter altitude… Building signal brief…") to reduce perceived latency.
2. **Compass pre-fill animation:** Fields populate sequentially (80ms stagger) or render fully populated? → Recommendation: sequential 80ms stagger — signals the AI read the JD, not that it guessed.
3. **Signal Brief accordion placement:** Top of compass page (above the receipt form) or sidebar drawer? → Recommendation: collapsible top accordion for mobile-first; sidebar drawer at ≥1024px breakpoint.

---

## Y — Gate

**Y: GREEN / HIGH / STABLE**

Both decisions are unambiguous. No FORK. No competing considerations of equal weight. Build can begin immediately.

---

## Cross-repo notes

- `arcs-v9`: No changes required. Compass/Brief/Prep logic may be ported or called via API.
- `arcs-intel-protocol`: Layer 1 instances adopt `opportunityId` as directory name convention (e.g. `instances/figma-[opportunityId]/`)
- `arcs-care`: No changes required.
- `MEMORY.md` in arcs-v9: Update with this ADR at session close.
