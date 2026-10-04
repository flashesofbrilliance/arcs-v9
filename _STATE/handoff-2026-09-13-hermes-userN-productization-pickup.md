# Cross-Harness Handoff Pickup — Hermes

- **Doc:** handoff-2026-09-13-hermes-userN-productization-pickup
- **Re:** PROP-2026-09-12-USERN-EXTENSIBILITY-001 (Triune Productization, User0 -> UserN)
- **For:** Hermes Agent (Operator / Actuator, profile `arcs`)
- **From:** Claude Code (Architect / Compiler)
- **Branch:** `fresh-starts` (NOT on main; the convergence anchor lives here). main_head = 19e2bc7b
- **Beat:** global_beat 6
- **Prepared:** 2026-09-13
- **Parent anchors:** `_STATE/convergence.json`, `_SPECS/self-serve-atlas-scan-v1.md`, `_STATE/handoff-2026-09-11-cross-harness-pickup.md`

> **STATUS CORRECTION — supersedes Hermes's 2026-09-11 snapshot.** Hermes local memory (and its last pre-limit message) records JTBD-006 as `AWAITING_REVIEW` with no architect/scout responses and fresh-starts unpushed. That is STALE. Git ground truth (`_STATE/convergence.json`, updated 2026-09-12T01:46:21Z, read 2026-09-13) shows the review is COMPLETE: architect `CREDIBLE_NOT_VAPOR`, scout `APPROVED`, compiler verdict recorded, compiler commit 9f6beb9a cherry-picked onto fresh-starts as 9ef11c52. **Do NOT re-run the review round or spawn review agents — it is done.** Open work = the 5 gates + 3 flags below. (Classic `verify-in-git-not-ram`: trust convergence.json over any harness's memory, including this file.)

## 0. Read this first (30-second orientation)
The productization proposal has cleared architect + scout review (JTBD-006 = `APPROVED_BY_ARCHITECT_AND_SCOUT`). It is NOT yet convergence-landed: 5 gates are required and 3 compiler flags are open. Two of the three open flags and at least two of the five gates fall in YOUR sovereign domain (local runtime, PII air-gap, headless rendering). This file names exactly which, grounded in `_STATE/convergence.json`.

Ground truth is git, not this file and not any harness's word (mine included). Confirmed vs unconfirmed is marked in section 7. Verify on pickup.

## 1. Where the work lives (CONFIRMED this session, from git)
- Proposal: `_PROPOSALS/2026-09-12-triune-productization-user0-to-userN.md`
- Convergence anchor: `_STATE/convergence.json` (global_beat 6, updated 2026-09-12)
- Invariant / architecture specs: `_SPECS/job-search-invariant-shape.md`, `_SPECS/self-serve-atlas-scan-v1.md`, `_SPECS/profile-scan-spec-v1.md`
- Canonical intake schema: `_INBOX/evidence/role-dossier-schema.json` (commit 673e4b8d, Perplexity-owned, supersedes Hermes draft 99f4a68d)
- Scout dossiers present: `SCOUT-blacksmith-...` (valid), `SCOUT-trueseek-...` (valid), `SCOUT-parloa-fde-us-...` (INVALID: missing `extraction_risk`)
- Compiler artifacts: `_STATE/job-search/architect-review-triune-productization.md`; compiler commit 9f6beb9a (cherry-picked onto fresh-starts as 9ef11c52)
- Branch reality: fresh-starts carries ~53 patch-id-unmerged commits and is dirty. Do your work on fresh-starts (or a branch off it), never straight on main.

## 2. Your mandate this pickup (JTBD-006 gates you own)
Architect required 5 gates before convergence-land:
- **Gate 2 (YOURS):** Mechanical PII air-gap test script, fail-closed (`exit != 0` on any leak). This is your air-gapped-runtime sovereignty. See flag #1: the current `pii_leak_gate.py` is redaction-QC, which is NOT a network air-gap guarantee.
- **Gate 4 (YOURS):** Dual-manifest `resume-tailor-skill` (keep `.claude-plugin/plugin.json` AND add Hermes `skill.yaml` + `SKILL.md` frontmatter); register into `~/.hermes/profiles/arcs/skills/resume-tailor`; prove both CLIs invoke the same skill.
- **Gate 3 (SHARED):** Supabase RLS tenant isolation test (prove UserN cannot read UserM). You execute/verify locally; Claude owns the schema + RLS policy.
- Gate 1 (Claude): normalized opportunity-record schema contract (shared intake join).
- Gate 5 (Claude/Perplexity): falsification/conversion hypothesis loop (H1-H4 ledger).

## 3. Open compiler flags to correct (all OPEN)
1. **PII banner OVERCLAIMS.** redaction-QC (`pii_leak_gate.py`) is not the same guarantee as a network air-gap. Correct the language, and/or make Gate 2 real. (Your domain.)
2. **PWA surface `resume-tailor-pwa.html` is grep-confirmed only, NOT browser-verified.** Render it headless and verify. (Your rendering domain; ties to Phase 2.)
3. **Supabase RLS tenant isolation UNTESTED** (no passing isolation test yet). (Gate 3.)

## 4. Adjacent JTBDs
- **JTBD-004 `READY_FOR_HERMES`:** extract `Complete_LinkedInDataExport_09-11-2026.zip.zip` locally (PII stays on host), run `scripts/network_scan_full.py`, cross-reference `jobs.arcs.care` for warm-referral matches.
- **JTBD-007 `GATE_LANDED_PARLOA_REEMIT_OPEN` (owner = Perplexity, NOT you):** validator `scripts/scout_dossier_ingest.py {validate|map|post}` is live. Parloa dossier is INVALID pending a Perplexity re-emit with `extraction_risk`. Flagged so you do not duplicate Perplexity's work.

## 5. Proposal phases mapped to your actuator role
- **Phase 1 Engine Portability (`resume-tailor-skill`):** audit for zero User0 hardcoded strings; dual-manifest; register into the `~/.hermes` profile; verify both CLIs. == Gate 4.
- **Phase 2 Presentation (`arcs-v9`):** local smoke-test `public/resume-tailor-pwa.html` (branch `feat/resume-pwa-theming`); strip legacy service-worker hooks from `public/resume.html`; then promote `resume-tailor.arcs.care` routing. == closes flag #2.
- **Phase 3 Triune Feedback:** wire `role-dossier-schema.json` into `target-role-scan.json` + `resume-tailor-skill`; every build logs a `decision_receipt` (claims confirmed vs unconfirmed).

## 6. Boundaries / invariants (do not cross)
- **Local-first:** raw PII (LinkedIn ZIP/CSV) never leaves the localhost sandbox.
- **Writes:** outputs land locally; git is the write-lock; untracked = the gap.
- **Receipts:** every merge/deploy/publish logs ONE `decision_receipt` row (Supabase `xbbpiryokswwvcrcutge`, ARCS_v9): `question, horizon{today|this-week|this-quarter|1-3y}, stakes{low|medium|high|critical}, mode{QUICKMOVE|PLAN|COURT}, what_confirmed[], what_unconfirmed[], operator, event_at, source_repo, refs[]`. Anything not git-verifiable goes in `what_unconfirmed`.
- **Numbering:** allocate ADR/seed/receipt numbers via the oracle (`_SEEDS/_oracle.json`), never guess.
- **Heartbeat:** pulse/oracle beat is yours (`_STATE/pulse.json`).
- **Evidentiary weight:** attestations from any harness (mine included) are not proof. Confirm in git / real state before writing CONFIRMED.

## 7. Confirmed vs Unconfirmed (honesty grade)
**CONFIRMED (git + convergence.json, 2026-09-13):** proposal doc, convergence beat 6, JTBD-006 architect+scout approvals, the 5 gates, the 3 open flags, `role-dossier-schema.json` canonical, the 3 scout dossiers and their validation states, fresh-starts unmerged/dirty.

**UNCONFIRMED (verify on pickup, NOT checked this session):**
- `resume-tailor-skill` User0-hardcoding state and dual-manifest status (Gate 4 not started/verified).
- `public/resume-tailor-pwa.html` actual render (flag #2).
- `pii_leak_gate.py` existence/behavior vs a true air-gap (Gate 2).
- Supabase RLS isolation (Gate 3, no passing test).
- `resume-tailor.arcs.care` domain routing state.
- Presence of the LinkedIn export zip on the local host (JTBD-004 precondition).

## 8. First three moves (suggested)
1. `git fetch`; confirm you are on `fresh-starts`; read `_STATE/convergence.json` JTBD-006 verbatim.
2. **Gate 2:** stand up the fail-closed PII air-gap test; correct the overclaiming PII banner (flag #1).
3. **Gate 4:** dual-manifest + register `resume-tailor-skill`; prove both CLIs invoke it. Log a `decision_receipt` for each.
