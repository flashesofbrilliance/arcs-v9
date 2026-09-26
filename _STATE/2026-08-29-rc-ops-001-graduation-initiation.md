# RC-OPS-001 — Graduation INITIATION receipt (not a promotion)

> **Status transition:** `READY_FOR_PERIOD` → **`GRADUATION_INITIATED`**
> **Date:** 2026-08-29
> **Candidate:** RC-OPS-001 — Orthogonal Echo Detector (`operators/arcs_inchworm_echo.py`)
> **This is NOT a promotion to ROM.** It opens the graduation, banks the evidence so far, and
> pins the criteria that must close before promotion. A primitive *becomes* ROM by surviving its
> gate; it is never *told* it is ROM. See wisdom `rom-graduation-earn-through-gate-never-decree`,
> witness `_STATE/witness/2026-08-28.jsonl` 23:37 EDT ("preach — can I get a witness").

---

## Why initiate (the instinct is right)

The detector keeps producing hindsight-confirmed cross-domain isomorphisms, and the demand to
lower the arbitrary "100 receipts" gate is correct in spirit. But the honest response is not a
lower guessed number — it is to **fix which quantity is measured** and open the promotion against
the corrected gate. This receipt does that.

## Evidence banked (as of 2026-08-29)

**Blind-field echoes (the real gate signal):** count ≈ **1**.
- ✅ 2026-07-13 dual-audit reconciliation — two *blind* methods converged (source-independent).
- ⚪ Tonight's foreshadow echoes (1998→2026 circuit) — **bias-free but NOT source-blind** (one
  searcher, one intent, same session). They strengthen the *no-bias* case, not the *blind-count*.
- ⚪ Perplexity cross-substrate convergence (2026-08-28 serialization + teardown) — a *candidate*
  echo, stronger than same-session priming (separate engine/runtime) but weakened by the
  **shared-corpus common cause**. Confirms gravity-well/sovereignty; not a clean blind echo.

**Detector precision (dogfood 2026-08-29):** **FAILS.**
- Harness `scripts/echo_detector_dogfood.py`; receipt `_STATE/2026-08-29-echo-detector-dogfood.json`.
- Labeled bench (5 genuine isomorphisms, 3 clean negatives, 4 adversarial weak-keyword-collision
  negatives). Default `min_sim=0.20`: recall 1.0, precision 0.56, **adversarial-FP rate 1.0 (4/4)**.
- Sweep: best-F1 at 0.30 (P0.71 R1.0) still adv-FP 0.50; 0.60 zeroes adv-FP but recall → 0.20.
  **No threshold gives high recall AND low adversarial-FP → the limit is architectural** (fixed
  keyword-library token overlap + a `different-domain = 1.0` orthogonality multiplier that rewards
  any cross-domain pair sharing a generic word). Same failure class that got the v8.5.1 variant
  rejected, live at the default threshold.

## Closing criteria (ALL must close before promotion)

1. **Unambiguous ROM to join.** Resolve the ESCALATED ROM-vocabulary canon collision (5/6/7,
   `_DECISIONS/CANON-COLLISION-rom-vocabulary.md`) via `/canon-review`. You cannot graduate a
   primitive into a ROM whose enumeration is itself contested. — **OPEN.**
2. **Detector precision (REPLACES the corpus-count gate).** Rebuild with the injectable
   `signature_fn` (LLM structural extraction) and `orthogonality_fn` (embedding distance); the
   keyword library is a demo, not a detector. Re-run the dogfood; require **adversarial-FP ≤ 0.10
   at recall ≥ 0.80**. Current: **FAIL** (adv-FP 1.0 @ default). — **CLOSED 2026-09-26** (rebuild
   landed; adv-FP 0.0 @ recall 1.0 across the full sweep + a held-out bench — see Update at end).
3. **Blind-field precision.** Accumulate **K** source-independent, hindsight-confirmed echoes with
   **zero** confirmed false-positives in blind operation. K small and stated as a floor for a
   precision estimate (not a corpus proxy); provisionally K = 3. Current blind-count ≈ **1**. — **OPEN.**
4. **Observatory period served.** Findings logged and replayed across *multiple real sessions* with
   severity grading and hindsight confirmation. Needs the unpushed Observatory page (the promotion
   *instrument*; MEMORY records commit `35070a3`) deployed first. — **OPEN.**

## Operational trigger event (defined)

Fire on **new-artifact ingest**, compared against the **prior-session corpus**, logging each
cross-domain candidate with source-independence metadata (`same_session` / `same_domain` /
`same_author_intent`) for later **hindsight grading**. Only source-independent candidates count
toward criterion 3. The dogfood is the *bench* version (ground truth known up front); this is the
*field* version (graded in hindsight).

## Falsifier (for this initiation)

If RC-OPS-001 is promoted to ROM with any criterion above unmet, and it later has to be
un-canonized against real counter-evidence, then decree-over-earn is proven costly and this
initiation discipline was correct to hold. Conversely, if all four close and the detector holds up
in blind field operation, it graduates — earned, not decreed.

## Y-gate

**YELLOW / OBSERVED-AND-OPENED.** The decision to *initiate* is GREEN (named live, evidence banked,
gate corrected). The *candidate* is YELLOW: real accumulating case, three of four criteria open, and
the one measured criterion (precision) currently FAILS. Honest status: opened, not promoted.

**Lineage:** witness 23:37 → wisdom `rom-graduation-earn-through-gate-never-decree` → dogfood
receipt `_STATE/2026-08-29-echo-detector-dogfood.json` → this initiation → RC-REGISTRY transition.

---

## Update — 2026-09-26 · criterion 2 CLOSED (detector precision)

The precision criterion above is now **closed**. The detector was rebuilt on branch
`claude/echo-detector-seaworthy` (golden-inchworm fork off F34):

- **Root cause (Red):** the v8.5.1 matcher scored on lone keyword-token overlap; the four
  adversarial decoys share isolated generic words (`trust`, `shock`, `gradient`, `collapse`)
  without the underlying dynamic, so every low threshold flagged them.
- **Fix (Golden):** flat `PATTERN_LIBRARY` → `CONCEPT_LIBRARY` of named kinematic concepts, each
  detected only by a **relational phrase** (never a lone word); a pattern fires only when
  **≥ 2 concepts are present on both sides**. `signature_fn` + `orthogonality_fn` remain injectable
  (`make_llm_signature_fn` / `make_embedding_orthogonality_fn`); offline defaults are deterministic
  fixtures, labeled honestly as fixtures.
- **Needle (measured):** `scripts/echo_detector_dogfood.py --sweep` → **precision 1.0 / recall 1.0 /
  adv-FP 0.0 across the entire 0.10–0.60 sweep** on the unchanged 12-case bench. A **held-out** bench
  (new domains + a decoy sharing exactly ONE real concept) also passes 1.0/1.0/0.0 — generalization,
  not overfit. Receipt: `_STATE/2026-09-26-echo-detector-dogfood-seaworthy.json`. Pre-registration:
  `_STATE/2026-09-26-echo-detector-seaworthy-prereg.md`. Ledger: F38 (closes F34's loop).

**Still OPEN:** criteria 1 (unambiguous ROM to join), 3 (blind-field precision, K source-independent
echoes), 4 (Observatory period). RC-OPS-001 stays **YELLOW / candidate** — one measured criterion
closed is not graduation. Earned through the gate, not decreed.
