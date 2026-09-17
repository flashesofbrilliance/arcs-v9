# ADR-CANDIDATE (proposed, unnumbered) — Defeasible context codec + kinematic-adaptive freshness

_Status: CANDIDATE. Not a decided ADR. Promote to `ADR-NN` via `python3 scripts/oracle.py next adr` only when we commit to build. Planted 2026-09-17 from the PRL defeasibility thread (worktree arcs-e2e-benchmarks-cicd-0369bd). Raw material: witness stubs `_STATE/witness/2026-09-17.jsonl`; memories [[defeasible-warrant-freshness-horizon-and-defeater-triggers]], [[claim-exit-lattice-falsification-truth-axis-vs-mootness-liveness-axis]], [[context-compression-taxonomy-redactive-referential]]._

## Context
Two problems surfaced as one shape. (1) Session compaction is **abstractive** (lossy + distortion); important context is lost when summarized without a durable pointer. (2) A warranted conclusion (esp. a null / absence claim) is **defeasible** — true as-of-T, retractable by a later defeater — so any "we don't have X" or "it works" that a plan rests on decays, and a one-shot gate can't catch that.

## Decision (proposed)
Build **nothing from scratch**; compose two things and add the ARCS-specific glue.

### Part A — Redactive-referential context codec (compose, don't rebuild)
A pre-pass BEFORE abstractive compaction:
1. **Extract** the task/commitment-salient spans verbatim — decisions, receipts, IDs, open threads, defeaters — (mp3 principle: protect what's above the salience threshold).
2. **Address** them into a pointer store so they're bit-exact recoverable (FLAC principle: lossless-by-reference).
3. Let abstractive compaction handle only the low-salience remainder.
- **Reuse:** LLMLingua / LLMLingua-2 (perceptual token codec) for the remainder; Letta (MemGPT) / Mem0 / LlamaIndex for the addressable memory-paging layer; append-only JSONL logs (witness / induced-backlog / progressive-handoff) for capture. See memory [[context-compression-taxonomy-redactive-referential]].
- **Net-new = the salience model is task/commitment-aware (not perplexity-only)** — receipts/decisions/defeaters are the "above-threshold" signal — plus wiring it to Part B.

### Part B — Kinematic-adaptive freshness gate (generalize the PRL P-1 gate)
Every warranted null/conclusion carries (a) a **freshness horizon** and (b) named **defeater-triggers**. On trigger, RE-exhaust — don't re-assume.
- **Pacing is kinematic, not a fixed clock:** re-check frequency scales to the belief's rate-of-change on the manifold (the recoil `kinematic_series`). Trigger = a **knot** in the spline (Operator21 anterior/posterior inference; Kairos = the right moment, not periodic). Floor = **Nyquist**: sample > 2x the truth's bandwidth or a fast-moving null aliases into stale-reads-as-fresh.
- Working instance already shipped: `_ARTIFACTS/prl-1-2-close-loop/prl_depmap_check.py` (`--baseline` status-diff -> anterior->posterior belief re-score) + the `investigation_prework` P-1 gate.

## The epistemic frame this enforces (the "why")
A claim exits by **falsification** (truth axis: null-flip ¬X->X, or its inverse **exoneration** X->¬X) or by **mootness** (liveness axis: superseded/vacated). Falsification you correct; mootness you vacate-and-mark. `think->know` = acquiring **citable** justification (not confidence); "know" is itself defeasible (JTB + no genuine defeaters = the exhaustion gate + a valid freshness horizon); receipts' `what_confirmed`/`what_unconfirmed` IS the know/think line. Overclaiming "know" queues a self-inflicted exoneration.

## Germination conditions
- **Soil:** any long-running harness where context compaction drops load-bearing commitments, or any plan/gate resting on absence-claims that decay.
- **Next (Part A):** prototype the redactive pre-pass over LLMLingua-2 + Letta on this repo's own session logs; measure commitment-retention vs plain abstractive compaction.
- **Next (Part B):** add `freshness_horizon` + `defeater_triggers` fields to the depmap schema; a scheduled/triggered re-exhaustion runner; wire Operator21 knot-detection as the trigger source.
- **Promote:** when either part is decided-to-build, mint `ADR-NN` via the oracle and move the relevant seed from `candidate` -> lab.
