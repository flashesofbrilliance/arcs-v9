# Basin Distiller — Full-Sweep Epoch (2026-08-11)

**What this is.** Second distiller run (ratchet tooth #2), widened to the full live surface: **arcs-v9 +
arcs-care-local + meridian-cco-repo + perplexity-mcp + arcs-decision-receipts + the design-system layers**
(the stale `arcs` clone excluded). 8 blind readers → condense → 6 adversarial verifies → synth with a
**build_queue** (dense-but-unbuilt). Residue deposit per [[throwaway-context-not-throwaway-learning]];
method [[tool-fit-marker-convention]]; endgame [[prepaid-reflexes-tier-descent]].

**Run stats.** 16 agents, 0 errors, **1,051,437 tokens**, ~16.5m. 106 raw particulates → 6 candidates →
**6 survivors, 0 refuted** (5 CONFIRMED, 1 PARTIAL).

## THE dominant finding (the reason to run this)
**A large, well-built Python operator estate is almost entirely UNWIRED to the user-facing compass.**
The compass route invokes BAR/LAB/Court/Kintsugi/Kairos **only as LLM prompt vocabulary** — the executed
Python pantheon is advisory and never blocks. Unwired: the pantheon runtime, `arcs_lte.py` (1108 LOC),
`operators/core/*` (virtue/Board-of-Advisors/Loki/Detective/Conductor), `arcs_operator_kairos.py` (Phase-7),
`lattice_sim.py`, the Operator20 folksonomy endpoints (gated ≥100 receipts, corpus=0). **The two highest-leverage
moves convert already-built machinery into live surface:** (1) wire the pantheon; (2) close the receipt loop
so the corpus flywheel spins (unblocks lattice/folksonomy/Kairos-detection).

## Basin floor (dense ∩ defensible)
1. **computeYGate / DEWY Y-vector** (97/CONFIRMED) — the deterministic scoring primitive every other converges on; enums byte-identical across arcs-v9 ↔ arcs-decision-receipts. `src/lib/ygate.ts:68`; `runtime/specs/dewy-receipt-schema-v1.json`. *Caveat: no unit tests (observatory risk-6, grade C).*
2. **L0–L5 compass spine** (94/CONFIRMED) — one 613-line POST route: ratelimit→auth→prep→SAGE pre-screen→mode/door→model-routed Claude→parse→computeYGate→persist-if-signed-in→email, with a **deterministic override block** forcing y_state/mode/door over the LLM's echoed values. *L0–L5 are prose in the SYSTEM prompt — one call, not discrete stages.*
3. **Trust-boundary defense family** (91/CONFIRMED) — one recursive never-trust invariant at 3 layers: `sanitize.ts` clamps + zero-width DATA_MARKER wrapping model+user text as DATA; the "no auth = no write" persistence gate; zero-trust ADR-032 + RLS deny-all (ADR-008). *Defense is STRUCTURAL, not content-filtering — the honest bound.*
4. **Python operator pantheon + ballet runtime** (86/CONFIRMED) — `ARCSRuntimeService` composes SAGE→LAB→BAR→Curator with Constitutional Court pre-commit (PERMIT-gated) + Kintsugi repair; thresholds from write-locked Canon ROM; CoherenceReceipt under ARCS Law C=αA−β(S−Smin)²+γW. **HONEST BOUND: NOT wired to compass — advisory only.** `_execute_pipeline` is a fixed Stage 1→8, not the aspirational "dancers declare deps."
5. **Double Helix + Triune Logic kernel** (84/CONFIRMED) — composite = Strand_A×(1−Loki discount, 0–0.75), three-valued OM/UNDEFINED/NULL (refuses false negatives); one `run_gauntlet` + DomainConfig serves calendar/listening/reader. `scripts/arcs_core.py`. *This NCI = resonance scoring, NOT Commit-NCI (ADR-035).*
6. **NOTOMATION supreme axiom** (78/PARTIAL) — write-locked ROM Primitive #1: scaffold/sequence, never compress/replace/overrule revealed preference. Core CONFIRMED; **PARTIAL because the particulate's enforcement composite was fabricated** (see dropped).

## build_queue (dense-but-unbuilt, ranked by build-readiness)
> **These are EX-ANTE predictions — verify-live before pulling any item.** Scored ex-post 2026-08-11:
> item #2 ("outcome PATCH route + Outcome write MISSING") was **refuted** — the loop-close was already
> built (`src/app/api/receipts/[receiptId]/outcome/route.ts`, 116 lines); the only real gap was the
> unfired `receipt_outcome_matched` signal (now emitted server + client). Item #4's auth "stub" was
> likewise refuted (auth.ts is a wired Resend provider; `TOPOLOGY.md` is the stale source). Treat the
> readiness/`built` fields as claims to check, not facts.
1. **Wire the pantheon into compass** (organism/partial, 86) — set `SAGE_URL`, lift SAGE from degrade-to-unset to a live gated pass; needs a Node→Python HTTP bridge. *Highest leverage: converts the whole built estate to live.*
2. **Outcome handler + receipt loop-close** (protocol/named-unbuilt, 80) — `PATCH /api/receipts/[id]` records actual vs ex-ante, fires `receipt_outcome_matched`; + soft save-nudge. *Builds the missing "measure expected vs actual" arm of the canonical loop; biggest PLG gap.*
3. **Recover interactive Observatory** (page/partial, 78) — full Next.js replay page built-but-never-pushed; cherry-pick from stale clone + wire to receipt history. Gated ≥100 receipts.
4. **Auth.js magic-link — resolve stub/live contradiction** (primitive/partial, 76) — **VERIFY-LIVE FIRST** (see below).
5. **ATG mechanization** (operator/partial, 74) — generalize tributaries[3]→2–4 generated; held for instance #2 (ADR-039); fork task_b3dbc0ac.
6. **Shared DEWY-schema package** (protocol, 72) — extract `dewy-receipt-schema-v1.json` into an imported lib so cross-repo "cannot drift" rests on a dependency, not discipline.
7. **Design-system formalization** (ui-kit/partial, 70) — promote convention-only ui/→molecules/→organisms/ into a documented atomic system: an `atoms/` layer, a DS ADR, and a `@dsCard` generator making React counterparts for the 14 annotated Recoil-Report HTML primitives (nothing consumes `@dsCard` today).
8. **Token SSOT** (atom/partial, 66) — collapse `tokens.ts` vs `recoil-report/_tokens.css` duplication into one generated source + SSOT ADR (ADR-009 acknowledged).
9. **compass-atoms-v1 live wiring** (molecule, 64) — atoms 9–11 (Drift Sentinel, persistence indicator, NCI display) — BLOCKED on a session model not built.
10. **Full Kairos operator wiring** (operator/partial, 62) — replace inline `_compute_kairos()` with `arcs_operator_kairos.py` gyroscope.
11. **Fold pre-kernel scanners onto DomainConfig** (protocol, 58) — network/forensic/archetype scanners don't import arcs_core; unify.
12. **LTE trajectory operator integration** (operator, 56) — wire `arcs_lte.py` (1108 LOC) into a running surface (zero importers today).
13. **Superionic lattice / Kairos-detection go-live** (calibration, 54) — real-corpus Zipf baseline (100+ receipts) → lattice constants + goal_edges table. *Downstream of #2/#4 (the flywheel).*
14. **Stripe billing gate** (workflow, 48) — middleware gating COURT/DEEP (PRO $29 / TEAM $299).
15. **MCP veil** (protocol/named-unbuilt, 46) — the named successor to the interim `statusgate.ts`, + durable gateway rate-limiter + spend caps (ledger GW-002) replacing the instance-local limiter.

## Adversarial drops (must not be re-bought)
- **`effort_score` is fabricated** — zero grep hits across .py/.ts/.md; only `nci_self_grade` exists.
- **SIGNAL_PROMOTE_GATE is a CI/CD prod-deploy circuit breaker (ADR-014), NOT a grading-field enforcer** — the NOTOMATION particulate conflated two mechanisms.
- **`colors_and_type.css` does not exist** (sources: `tokens.ts` + `globals.css` + `recoil-report/_tokens.css`).
- NOTOMATION is paraphrased differently per repo, not stated identically. "ballet/dancers declare own deps" is aspirational — `_execute_pipeline` is fixed Stage 1→8.
- ADR-034 "live CI-gated law" was stranded on an unmerged branch for a period (later merged via PR #63) — the earlier "live" claim was premature.

## ⚠️ Contradiction flagged for VERIFY-LIVE
**`src/lib/auth.ts`: reader/TOPOLOGY.md report a null Auth.js stub ("non-functional until ADR-016"); global CLAUDE.md memory claims a fully-wired live Resend provider.** Do not trust either without a live check — receipt persistence AND the trust gate's Postgres arm depend on it. (Note: the status.arcs.care gate reuses `AUTH_SECRET`, not the provider, so it's unaffected either way.)

## Key negatives (liveness truths — don't re-derive)
- No `kinematics` lib module — gradient/flowTopology/manifoldCurvature are **inline in `ygate.ts`**.
- `ReceiptPreviewWidget.tsx` (16KB, largest molecule) has **zero importers** — orphaned.
- `public/templates` holds **only** call-brief-template.html despite the "template registry" commit.
- Supabase `compass_receipts` table (arcs.care persistence target, ADR-017) **does not exist** — arcs.care receipts returned but not persisted; the cross-repo schema lock is aspirational on the arcs.care side.
- `create_skill` MCP tool returns in-memory only (no Supabase write wired). `mcp.arcs.care` unwired (ADR-003).
- Duplicate ADR numbers (two each of 024/025/031/032); `index.json` stale vs per-file Status headers (SoT).
- No `atoms/` dir, no DS ADR — the design system is code-only, self-documented via the design-test gallery + `@dsCard` comments.

---
*Calibration: bars held again — 6/6 survivors code-anchored, adversarial pass caught a fabricated field + a mechanism-conflation without false-refuting the core. The build_queue is the actionable output: rank #1 (wire pantheon) + the receipt flywheel (#2→#13) convert the most already-built machinery into live surface. Next deposit appends here or a dated sibling.*
