# Sampling Engine Spec — the cost-governed hypercube gauntlet (v1)

**Status:** PROVISIONAL · 2026-08-13 · implements ADR-060 §8 (the two-gate architecture)
**Grounding:** two real runs, not estimates — `wf_719c5843-ff0` (Opus gauntlet, self-audit) and
`wf_90b0b237-fe2` (Haiku coarse-ripple, cost probe). Where a claim is measured it is tagged **[E]**
(empirical); where it is design that has not been run it is tagged **[H]** (hypothesis).
**Provenance note:** this spec was written *after* the cost probe falsified the author's ~25K estimate
(actual: 325K). It is built from the falsification, on the tape — see [[arcs-magnetic-best-fit-simulated-annealing]].

> The job: turn "a dial" (spend ~20K coarse … ~1M fine, set by hand) into "a dial that tunes itself" —
> a cost-governor that decides *where* to spend the next token from value-of-information, not a budget
> guessed up front.

---

## 0. The empirical cost model — the correction that governs everything **[E]**

The naive model ("tight prompts + exclusions = cheap; cost scales with input data size") is **wrong**.
Measured, per spawned subagent:

| run | model | agents | total tokens | per-agent |
|---|---|---|---|---|
| gauntlet (self-audit) | Opus | 7 | 567,370 | ~81,050 |
| ripple (cost probe) | Haiku | 6 | 325,445 | **~54,140 (uniform)** |
| single-pass (threshold probe) | Haiku | **1** | **54,429** | 54,429 — **25 cells, ONE floor** |

The ripple's per-agent tokens were **near-identical (~54,140) across all six**, independent of task or
wall-time (19s–54s). That uniformity is the finding: there is a **fixed floor per spawned subagent**
(harness system prompt + tool schemas loaded on spawn), and it *dominates* the task tokens (a ~400-token
digest + ~5-cell output). Model tier sets the floor height (**Haiku ≈ 54K, Opus ≈ 81K [E]**) and the
$/token, not whether the floor exists.

**Amortization confirmed [E]:** the single-pass agent graded **all 25 cells for 54,429** — the same ~54K
a ripple agent spent on **5**. Cells-per-agent is nearly free; *agents* are the cost. The 6-fan ripple
(325K) → 1 amortized agent (54K) = **6× cheaper, identical coverage.** Amortize to the floor.

**The cost law:**

```
Total ≈ Σ_spawned_agents ( FLOOR_model + task_tokens_agent )     FLOOR ≈ 54K (Haiku) / 81K (Opus)  [E]
Inline work (main context, no spawn) pays task_tokens only — NO floor.                             [E]
```

**Re-ranked levers (was → is):**

| lever | naive rank | true rank | why |
|---|---|---|---|
| **Inline the coarse gate** (no subagent) | — | **#1** | the floor is a *spawn* cost; the main context doesn't pay it |
| **Minimize agent count / amortize** | secondary | **#2** | 1 walker × 25 cells ≈ 1 floor; 6 walkers = 6 floors (the ripple left ~6× on the table) |
| **Model tier (Haiku vs Opus)** | — | **#3** | ~54K vs ~81K floor + cheaper $/token; never for ruin-exposed cells ([[model-tier-routing-locked-principle]]) |
| **Tight prompts / exclusions** | **#1** | **#4 (marginal)** | trims task tokens only — a few K on top of a 54K floor |

---

## 1. Architecture — corrected two-gate, floor-aware

1. **Gate 1 (coarse) runs INLINE** in the main context by default — no spawn, no floor. It sweeps a
   sparse anchor set over the penteract slice, mechanically/cheaply, and produces a coarse surrogate.
   Spawn a *single* amortized cheap walker only if independence from the main context is needed for the
   coarse read (one floor, not N). **[H — the inline path is unmeasured; next run validates it.]**
2. **A severity threshold on Gate 1 is mandatory — but use top-K, not an absolute cutoff.** The binary
   ripple flagged **25/25 [E]** (zero routing signal). Re-run with **graded severity 0–3** produced a
   real spread — **8/7/10/0 [E]** — and thresholding dropped 15 of 25 below the fine-gate, so grading
   *localizes*. **But the absolute scale mis-calibrates [E]:** the model clustered at 2 (10 cells) and
   used *nothing* at 3, so an absolute cutoff (≥2) still escalates 40% and won't use the top of its own
   scale. **The raw model score is ordinal, not absolute** → the coarse gate must rank and take **top-K**
   (or calibrate the scale via §2's loop), never a fixed numeric threshold.
3. **Gate 2 (fine) spawns independent subagents ONLY on cells that clear the governor's threshold** —
   you pay the ~54K floor exactly where independent verification (the oboe's-A property) earns it, and
   nowhere else.

---

## 2. The cost-governor — value-of-information, not a hand-set budget

Escalate a cell coarse→fine iff:

```
escalate(cell) = irreversible(cell)                    // hard override — COURT / free-solo topology
              OR  uncertainty(cell) × stakes(cell) > τ  // value-of-information gate
              OR  rand() < ε                            // exploration floor (non-negotiable)
```

- **uncertainty(cell)** — the surrogate's posterior variance there; *how much a fine probe could move
  the estimate.* The YELLOW axis. Confident (GREEN) coarse read ⇒ a fine probe buys nothing. **[H]**
- **stakes(cell)** — BAR ruin/consequence × reversibility penalty. The *why-you'd-care* axis. **[H]**
- **τ** — cost-indexed threshold, `τ ∝ FLOOR_model / decision_value`. Because the fine-probe cost is now
  known (~54K), τ is computable, not vibes: escalating is worth it iff the expected decision-regret it
  retires exceeds ~54K tokens' worth of value. **[E-anchored]**
- **ε floor — mandatory.** `stakes` and `uncertainty` are the surrogate's *own* estimates, so the gate
  inherits the surrogate's blindspots (the self observing has the blindspots of the self observed). A
  fixed random fraction of fine-probes fires *regardless* of the surrogate — importance-sampling the
  cells it is confidently-wrong about (ruin in plain sight, ADR-060 §1.7). Without ε the engine is
  efficient *and* self-blinding.

**Marginal-stop (when to stop refining a region):** keep probing until Δuncertainty per token drops
below a floor — the ratcheting fan→condense→verify→**floor** pattern
([[../_PATTERNS/2026-08-11-distiller-proof-epoch.md]]). N probes that don't move the estimate = stop; the
Drift Sentinel applied to spend.

**The tape** = `_STATE/gauntlet-runs.jsonl` (append-only, one row per run; the 3 reps that ground this
spec are its first entries). Every future gauntlet run appends here; τ-calibration reads it.

**τ-calibration (the self-tuning dial):** after each run, score from the tape —
- did fine-gate probes *flip* the coarse verdict? If they rarely do → over-spending → raise τ.
- did a coarse verdict that *skipped* the fine gate later get falsified? → under-spending → lower τ (and
  check ε wasn't too small).
τ is a **floating** parameter — declared, tuned, never a magic constant (ADR-060 §1.5 float-not-drift:
its ladder is the calibration record). Become-your-own-bookie, made mechanical. **[H — needs a tape of
≥ a few runs to calibrate.]**

---

## 3. Sampling strategy — the ripple (exploit the field) **[H]**

The penteract is a *continuous field* (ADR-060 §2), so cells are correlated — never enumerate 3,125.
- **Amortized walker**, not parallel fan: one context evaluates many cells sequentially (one floor).
- **Latin-hypercube anchors** across the 5 axes (~coarse mesh), then a cheap **surrogate/interpolation**
  fills between them; refine only where surrogate uncertainty or gradient is high (active learning).
- **Importance-sample the ruin** (BAR): least-resistance flow avoids high-resistance/ruin cells, so they
  must be probed deliberately (ADR-060 §1.7).

---

## 4. The factorial pass IS the orthogonality falsifier **[H → cheap to run]**

The main-effects design (5 axes × 5 values ≈ 25 probes) both approximates the space cheaply *and* tests
ADR-060 finding #4 (axis orthogonality UNPROVEN): run main-effects-only, then predict a few held-out
*joint* cells. Prediction holds ⇒ axes ~independent, penteract stands, proved for ~25 probes. Prediction
fails ⇒ axes dependent, penteract (and the 3,125 count) collapses — learned cheaply. **The cost-
optimization and the falsification are the same move.**

---

## 5. Worked budget (the self-tuning dial, in real numbers) **[E-anchored]**

- **Coarse, one amortized Haiku agent: 54,429 [E]** — 25 cells for one floor, ~10× cheaper than the full
  Opus gauntlet, and it **re-found the same core faults** the 567K gauntlet confirmed (see below). Inline
  (no spawn) would drop even the one floor — unmeasured [H], but the floor is a *spawn* cost.
- ~~Coarse-only target: measure it~~ → done; the 6-fan ripple proved the *wrong* way costs 6 floors (325K).
- **Coarse + a few fine probes:** inline gate 1 + K spawned fine probes ≈ K × 54K (Haiku) / 81K (Opus).
  K is set by τ and the critical-path size — typically single digits, not 3,125.
- **Full independent gauntlet (max):** ~7 Opus floors ≈ 567K [E] — reserved for the highest-ruin,
  most-irreversible artifacts only.

The dial is now priced: every notch is `± one FLOOR`. You set it by how much the decision's ruin
justifies, and τ re-prices it from whether the last notch paid off.

---

## Implementation status — `scripts/hypercube_sampler.py` (2026-08-13)

The `[H]` machinery of this spec is now **built and runs deterministically without an LLM**
(`scripts/hypercube_sampler.py`, stdlib-only). What moved `[H] → built`:

- **penteract model** (ADR-060 §1 axes), **LHS anchor sampler** (§3, balanced per-axis),
  **categorical surrogate** with the exactness gate `u = (1−max_w)(√var + β)` (§2 uncertainty),
  **cost-governor** (`irreversible OR uncertainty×stakes>τ OR rand<ε`, plus coarse top-K, §1.2/§2),
  **amortized walker** + **two-gate run** (inline coarse, one spawned fine floor, §1/§5),
  **empirical cost model** (54K Haiku / 81K Opus floors, §0), **tape I/O + τ-calibration** (§2),
  and the **factorial orthogonality falsifier** (§4).
- **Falsification-first `--selftest`** (11 checks that try to *break* the claims: surrogate
  exactness at anchors, factorial detecting a *planted* interaction, ε-floor + irreversible
  override firing, cost-floor arithmetic) — all pass.
- **In-silico reproduction of the §5 validation:** a 25-cell inline coarse pass + one amortized
  Haiku fine spawn (~98K tokens, ~6× under the 567K Opus gauntlet) **re-localizes all three
  confirmed faults** — C-lens hot, NOTOMATION×COURT contradiction, BAR orthogonality-ruin —
  on a synthetic ground-truth field built to carry exactly those faults.
- **Honest result, not rigged:** the built orthogonality falsifier reports **INTERACTION /
  penteract-collapses** on that field (mae 0.423 > 0.35 tol) — because the faults *are* lens×
  operator interactions. That is ADR-060's own unresolved MED finding #4 surfacing mechanically,
  not a pass manufactured by choosing an additive field.

## Live run — the real cheap→fine cycle on ADR-060 (2026-08-13, `engine-live-11`)

The fine-gate seam was wired to real models (Agent tool) and the full cycle run on ADR-060 itself.
One Haiku coarse spawn (20 LHS anchors) → governor → one Sonnet fine spawn (24 escalated cells) →
close. It **re-localized all three confirmed faults** (C-lens hot · NOTOMATION×COURT · BAR ruin) for
**177,002 measured tokens vs the 567K Opus gauntlet (~3.2× cheaper)** — and the run **falsified two of
its own designs, which then propagated to the code** (falsification-not-confirmation, on the tape):

1. **Governor absolute-threshold flood → FIXED.** The first escalate used an *unbounded* `voi > τ` OR
   and escalated **380/400** — the binary ripple's "25/25, zero discrimination" (§1.2) reappearing at
   the VoI layer. Fix: the escalation set is a **union of two BOUNDED top-Ks** (severity localizes the
   biggest faults; VoI spends where a probe cuts regret) + irreversible-override + ε. 380 → **24**.
   Confirms §1.2 with live data: *no absolute cutoff survives contact — on severity OR on VoI.*
2. **Cost model under-counted ~2× → FIXED.** Modeled 85.6K vs measured **177K**. The gap: each spawned
   agent **re-reads the full subject** (~22K Haiku / ~32K Sonnet), which `TASK_TOKENS_PER_CELL` omitted.
   `CostModel` now carries a `subject_read_tokens` term — and it is the **prompt-caching lever**: the
   subject-read is the identical cacheable prefix (`grading_prefix()`) across every spawn, so
   `cache_subject=True` models paying it once. Caching would pull this run from ~177K toward ~145K.
3. **Flip data is now on the tape.** flip_rate **0.50** (12/24): up-flips confirmed the two existential
   faults *harder* (COURT/FUNHOUSE 1.8→3.0); down-flips killed ε-floor false positives (→0.0). This is
   the predictor-scoreboard (§2 τ-calibration) with its first real rep.

## Second live run — ADR-053 (2026-08-14, `engine-live-23`), and the calibration finding

A contrasting subject (ADR-053, the Tao of ARCS — GREEN/canonical, vs ADR-060 YELLOW/contested) run
through the identical cycle: Haiku coarse (20 anchors) → governor (20 escalated) → Sonnet fine → close.
**156,942 measured tokens.** The fine gate did what BAR importance-sampling is *for*: it surfaced **two
irreversible ruin cells the coarse pass rated ordinary** — `D.Operational.BAR.synthesize.L3` (doctrine-
leak into the public MIT repo is a *human* discipline, not a technical control; one slip is irreversible)
and `R.Operational.BAR.synthesize.L2` (never-GC ⇒ unbounded dormant-seed accumulation, no mitigation).
Ruin hiding in plain sight — exactly §1.7.

**The calibration finding (two reps, honest):** *both* runs landed at flip_rate **exactly 0.50** (12/24
and 10/20). The loop mechanically works — it reads the tape, computes per-run + aggregate flip rate,
and would move τ if the rate left the [0.15, 0.5] band — but two reps pinned at 0.50 is a signal about
the *metric*, not a tuned τ: with only 20 anchors interpolating over 3,125 cells through a cheap Haiku
read, **the flip rate is dominated by surrogate NOISE, not by escalation productivity.** Before τ-tuning
is trustworthy the coarse mesh must be denser (more anchors → less interpolation variance) or the flip
threshold de-noised. Two honest reps buy *this*, not a dial that's ready. **[E, N=2]**

**Also honest:** the `localized_faults` field is meaningful only for the SyntheticField (where the fault
coordinates are known); on a real subject it degrades to label-pattern matching (did we escalate any
cell labelled C-lens / COURT / BAR) and is ~always true — it is NOT a live-run signal. Use flip data and
the fine-gate notes, not `localized_faults`, to judge a real run.

## Open questions / what is NOT built (honest)

- The **fine-gate judgment is still a seam**, not wired: `LLMGrader` renders the coarse/fine
  prompt but has no `judge_fn` — the workflow/skill layer must supply the real Claude call. The
  engine counts the spawn so the cost model stays honest either way. Until that seam is wired to
  a live model, the only *judged* field is the deterministic `SyntheticField`.
- **τ-calibration has no tape of engine-runs yet** — the loop is built and tested against a
  scratch tape, but the real `_STATE/gauntlet-runs.jsonl` needs ≥ a few live reps before τ tunes
  from anything but its seed. (The 3 grounding rows on the real tape are manual, not engine-runs.)
- The **surrogate, walker, and τ-calibration loop are built** — superseding the line below.
- The **~54K floor is harness-specific** and may change with the runtime; re-measure, don't assume.
- **Field-smoothness is assumed, not verified** — if the field is discontinuous, interpolation
  under-covers; the surrogate's own error must flag where.
- **RESOLVED [E] 2026-08-13 (run `wf_56c743ca-18e`):** the one-amortized-Haiku-pass ran. Floor confirmed
  **54,429** (25 cells, one floor). Grading **localizes** (8/7/10/0, not 25/25) but the *absolute* scale
  mis-calibrates → coarse gate uses **top-K/relative**, not absolute τ (§1.2). **Validation:** the ~54K
  coarse pass re-found the **same core faults** the 567K Opus gauntlet confirmed — the **C(oherence) lens
  hot across nearly every operator**, the **NOTOMATION-vs-annealing contradiction** (COURT.D/C), and the
  **orthogonality ruin** (BAR.D/R). The cheap→fine division of labor is empirically supported: coarse
  localizes correctly (~10× cheaper) → fine confirms the few hot cells.
- **New open question [H]:** severity-scale calibration — model scores are ordinal, cluster mid-scale;
  needs top-K, a calibrated rubric, or the §2 τ-loop tuned over a tape of runs.
