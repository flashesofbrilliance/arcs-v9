#!/usr/bin/env python3
"""
hypercube_sampler.py — the cost-governed hypercube gauntlet sampling engine (v1)

Implements _SPECS/hypercube-gauntlet-sampling-engine-v1.md, which itself implements
ADR-055 §8 (the two-gate architecture). This is the code that turns the spec's [H]
(hypothesis / unbuilt) pieces — the surrogate, the walker, the cost-governor, and the
tau-calibration loop — into something that actually runs.

Design discipline (per the spec + the session that produced it):
  - Falsification over confirmation. The engine ships with a `--selftest` that tries to
    BREAK its own claims (surrogate exactness, factorial interaction detection, epsilon
    floor firing, irreversible override) rather than demonstrate them.
  - The cost model is EMPIRICAL, not estimated: FLOOR ~= 54K tokens/spawned-Haiku-agent,
    ~81K/Opus (spec §0, three real runs). Agent-COUNT, not prompt size, is the cost driver.
    Inline work (main context, no spawn) pays task tokens only — NO floor.
  - The grader is PLUGGABLE. A pure-Python engine cannot *judge* a cell — judgment is the
    LLM's job. So the engine owns the sampling/surrogate/governor/cost machinery and takes
    a grader callable. Two are provided:
      * SyntheticField — a deterministic ground-truth field encoding the KNOWN structure the
        real runs found (C-lens hot, BAR ruin cells off the least-resistance path, a
        NOTOMATION x COURT contradiction). Lets the whole engine run + be tested with no LLM,
        and reproduces the empirical §5 validation in silico.
      * LLMGrader (stub) — emits the prompt a real coarse/fine pass would send; the workflow
        or skill layer wires it to an actual Claude call. The engine counts the spawn so the
        cost model stays honest.

Stdlib only (no new deps — repo rule). Python 3.9+.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import sys
from dataclasses import dataclass, field, asdict
from itertools import product
from typing import Callable, Dict, List, Optional, Sequence, Tuple

# ----------------------------------------------------------------------------
# 0. The penteract — 5 genuinely-orthogonal axes (ADR-055 §1)
# ----------------------------------------------------------------------------

AXES: Dict[str, List[str]] = {
    "lens":       ["D", "R", "W", "C", "H"],                                  # what facet?
    "resolution": ["Exec", "Strategic", "Operational", "Tactical", "Surgical"],  # how big is the move?
    "operator":   ["LAB", "KKL", "BAR", "COURT", "FUNHOUSE"],                 # which adversary?
    "verb":       ["analyze", "assess", "evaluate", "synthesize", "recapitulate"],  # cognitive op
    "lstack":     ["L1", "L2", "L3", "L4", "L5"],                             # how far must coherence hold?
}
AXIS_NAMES: List[str] = list(AXES.keys())
N_AXES = len(AXIS_NAMES)          # 5
N_VALS = 5                        # every axis has 5 values
N_CELLS = N_VALS ** N_AXES        # 3125

Cell = Tuple[int, int, int, int, int]  # index into each axis, in AXIS_NAMES order


def cell_label(cell: Cell) -> str:
    """(3,0,3,3,4) -> 'C.Exec.COURT.synthesize.L5' — the human coordinate."""
    return ".".join(AXES[name][cell[i]] for i, name in enumerate(AXIS_NAMES))


def cell_dict(cell: Cell) -> Dict[str, str]:
    return {name: AXES[name][cell[i]] for i, name in enumerate(AXIS_NAMES)}


def hamming(a: Cell, b: Cell) -> int:
    """Categorical distance = number of differing axes (0..5). The field is a lattice,
    not a continuum, so this is the natural metric between cells."""
    return sum(1 for x, y in zip(a, b) if x != y)


# ----------------------------------------------------------------------------
# 1. A graded cell reading — what a grader returns for one cell
# ----------------------------------------------------------------------------

@dataclass
class Reading:
    """One grader's readout of one cell.
      severity     — 0..3 ordinal (spec §1.2: ordinal, NOT absolute — the model clusters
                     mid-scale, so the coarse gate ranks/top-K, never a fixed cutoff).
      stakes       — 0..1 BAR ruin x reversibility penalty (the why-you'd-care axis, §2).
      irreversible — hard COURT/free-solo override; escalates regardless of VoI (§2).
      note         — free text (a contradiction name, a lens-hot flag).
    """
    severity: float
    stakes: float
    irreversible: bool = False
    note: str = ""


Grader = Callable[[Cell], Reading]


# ----------------------------------------------------------------------------
# 2. Graders — the pluggable judgment layer
# ----------------------------------------------------------------------------

class SyntheticField:
    """A deterministic ground-truth impedance field encoding the STRUCTURE the three real
    runs found (spec §0 tape; ADR-055 self-audit receipt). Not random noise — it is built
    to have the exact faults the 567K Opus gauntlet confirmed, so the cheap engine can be
    shown to re-find them (the §5 validation, reproduced in silico):

      - C-lens hot across nearly every operator      -> severity boost when lens == C
      - NOTOMATION-vs-annealing contradiction (COURT) -> a sharp spike + irreversible on
                                                         lens in {D,C} x operator == COURT
      - orthogonality ruin (BAR.D / BAR.R)            -> high stakes + irreversible, and
                                                         placed OFF the least-resistance path
                                                         (low baseline severity) so a naive
                                                         severity-only sampler misses it and
                                                         only the epsilon floor / stakes term
                                                         catches it (spec §1.7 ruin-in-plain-sight).

    A small deterministic ripple over L-stack/resolution gives the surrogate a non-trivial
    but smooth field to interpolate. No RNG — same cell always grades identically.
    """

    LENS = AXES["lens"]
    OP = AXES["operator"]

    def __call__(self, cell: Cell) -> Reading:
        li, ri, oi, vi, si = cell
        lens = self.LENS[li]
        op = self.OP[oi]

        sev = 0.4  # cool baseline
        stakes = 0.15
        irreversible = False
        notes: List[str] = []

        # C-lens runs hot everywhere (the confirmed finding).
        if lens == "C":
            sev += 1.4
            notes.append("C-lens-hot")

        # NOTOMATION vs annealing contradiction lives at the COURT operator on D/C lenses.
        if op == "COURT" and lens in ("D", "C"):
            sev += 1.6
            irreversible = True
            notes.append("NOTOMATION-x-COURT-contradiction")

        # BAR ruin cells: off the comfortable path (low sev) but high stakes + irreversible.
        # This is the "ruin hiding in plain sight" the least-resistance current flows around.
        if op == "BAR" and lens in ("D", "R"):
            stakes += 0.8
            irreversible = True
            notes.append("orthogonality-ruin")

        # A smooth ripple so the field isn't piecewise-flat (gives the surrogate work to do).
        sev += 0.15 * math.sin(si) + 0.1 * math.cos(ri)

        sev = max(0.0, min(3.0, sev))
        stakes = max(0.0, min(1.0, stakes))
        return Reading(round(sev, 3), round(stakes, 3), irreversible, ",".join(notes))


class LLMGrader:
    """Stub for the real judgment layer. It does NOT call an LLM here — it emits the prompt a
    coarse (inline) or fine (spawned) pass would send, so the workflow/skill layer can wire it
    to an actual Claude call. Every call increments spawn accounting via the CostModel the
    caller owns; that keeps the cost model honest whether or not a real model is attached.

    Wire it by subclassing and overriding `judge(prompt) -> Reading`, or by passing a
    `judge_fn` that takes the rendered prompt string and returns a Reading.
    """

    def __init__(self, subject: str, judge_fn: Optional[Callable[[str], Reading]] = None):
        self.subject = subject
        self.judge_fn = judge_fn

    def render_prompt(self, cell: Cell) -> str:
        d = cell_dict(cell)
        return (
            f"Grade cell {cell_label(cell)} of the hypercube gauntlet for subject: {self.subject}.\n"
            f"  lens={d['lens']} (facet)  resolution={d['resolution']} (move size)\n"
            f"  operator={d['operator']} (adversary)  verb={d['verb']}  lstack={d['lstack']} (coherence reach)\n"
            "Return JSON: {severity:0-3 ordinal, stakes:0-1 (ruin x irreversibility), "
            "irreversible:bool, note:str}. Severity is ORDINAL for ranking, not an absolute "
            "threshold. Refute-by-default; only flag what you can defend."
        )

    def __call__(self, cell: Cell) -> Reading:
        prompt = self.render_prompt(cell)
        if self.judge_fn is None:
            raise RuntimeError(
                "LLMGrader has no judge_fn wired. This is the seam for the workflow/skill "
                "layer to supply a real Claude call. Rendered prompt was:\n" + prompt
            )
        return self.judge_fn(prompt)


# ----------------------------------------------------------------------------
# 3. The empirical cost model (spec §0) — FLOOR per spawn dominates
# ----------------------------------------------------------------------------

FLOOR = {"haiku": 54_000, "opus": 81_000}  # [E] measured tokens/spawned-subagent
TASK_TOKENS_PER_CELL = 400                  # [E] ~digest+output; dwarfed by the floor


@dataclass
class CostModel:
    """Total ~= Σ_spawned_agents (FLOOR_model + task_tokens). Inline pays task only — no floor."""
    inline_task_tokens: int = 0
    spawns: List[Tuple[str, int]] = field(default_factory=list)  # (model, cells_graded)

    def inline(self, cells: int) -> None:
        self.inline_task_tokens += cells * TASK_TOKENS_PER_CELL

    def spawn(self, model: str, cells: int) -> None:
        self.spawns.append((model, cells))

    def total(self) -> int:
        t = self.inline_task_tokens
        for model, cells in self.spawns:
            t += FLOOR[model] + cells * TASK_TOKENS_PER_CELL
        return t

    def breakdown(self) -> Dict[str, object]:
        return {
            "inline_task_tokens": self.inline_task_tokens,
            "spawn_count": len(self.spawns),
            "spawn_floors": sum(FLOOR[m] for m, _ in self.spawns),
            "total_tokens": self.total(),
        }


# ----------------------------------------------------------------------------
# 4. Latin-hypercube anchor sampler (spec §3) — sparse coverage, one per axis-level
# ----------------------------------------------------------------------------

def latin_hypercube_anchors(n: int, rng: random.Random) -> List[Cell]:
    """n anchors such that, per axis, each of the 5 values appears ~evenly (LHS on a
    categorical grid). Never enumerates 3125. With n a multiple of 5, every axis level is
    hit exactly n/5 times — balanced coverage from a sparse mesh."""
    cols: List[List[int]] = []
    for _ in range(N_AXES):
        reps = (n + N_VALS - 1) // N_VALS
        col = ([v for v in range(N_VALS)] * reps)[:n]
        rng.shuffle(col)
        cols.append(col)
    return [tuple(cols[a][i] for a in range(N_AXES)) for i in range(n)]  # type: ignore


# ----------------------------------------------------------------------------
# 5. The surrogate (spec §2 "uncertainty") — kernel interp over the lattice + variance
# ----------------------------------------------------------------------------

class Surrogate:
    """Cheap kernel-weighted estimate of severity/stakes over the whole penteract from a
    sparse set of graded anchors, plus a posterior-uncertainty estimate.

      s_hat(cell) = Σ w_i s_i / Σ w_i,     w_i = exp(-hamming(cell, anchor_i) / lam)
      u(cell)     = (1 - max_i w_i) * ( sqrt(Σ w_i (s_i - s_hat)^2 / Σ w_i) + beta )

    The (1 - max_w) gate is the key: sitting exactly ON a measured anchor (max_w = 1) means
    you KNOW the value there, so neither neighbor-disagreement nor extrapolation should
    register — u -> 0 (exactness). Off-anchor, max_w falls and both the local-disagreement
    term and the beta extrapolation term switch on. --selftest checks both ends.
    """

    def __init__(self, lam: float = 1.0, beta: float = 1.0):
        self.lam = lam
        self.beta = beta
        self.anchors: List[Cell] = []
        self.sev: List[float] = []
        self.stk: List[float] = []
        self.irr: List[bool] = []

    def fit(self, anchors: Sequence[Cell], readings: Sequence[Reading]) -> "Surrogate":
        self.anchors = list(anchors)
        self.sev = [r.severity for r in readings]
        self.stk = [r.stakes for r in readings]
        self.irr = [r.irreversible for r in readings]
        return self

    def _weights(self, cell: Cell) -> List[float]:
        return [math.exp(-hamming(cell, a) / self.lam) for a in self.anchors]

    def predict(self, cell: Cell) -> Tuple[float, float, float, bool]:
        """Returns (sev_hat, stakes_hat, uncertainty, irreversible_seen_nearby)."""
        w = self._weights(cell)
        sw = sum(w)
        if sw == 0:
            return 0.0, 0.0, self.beta, False
        sev_hat = sum(wi * si for wi, si in zip(w, self.sev)) / sw
        stk_hat = sum(wi * si for wi, si in zip(w, self.stk)) / sw
        var = sum(wi * (si - sev_hat) ** 2 for wi, si in zip(w, self.sev)) / sw
        unc = (1.0 - max(w)) * (math.sqrt(var) + self.beta)
        # Irreversibility is a hard bit; if any near anchor (w>0.5, i.e. <=~0.7 hamming) is
        # irreversible, carry it forward as a governor override signal.
        irr_near = any(self.irr[i] for i in range(len(w)) if w[i] > 0.5)
        return sev_hat, stk_hat, unc, irr_near


# ----------------------------------------------------------------------------
# 6. The cost-governor (spec §2) — value-of-information, not a hand-set budget
# ----------------------------------------------------------------------------

@dataclass
class GovernorConfig:
    tau: float = 0.35          # VoI threshold; cost-indexed (see tau_from_floor)
    epsilon: float = 0.05      # mandatory exploration floor — fires regardless of surrogate
    top_k: int = 8             # coarse gate ranks and takes top-K (NOT an absolute cutoff, §1.2)
    marginal_floor: float = 0.02  # marginal-stop: Δuncertainty/token below this -> stop refining
    model: str = "haiku"


def tau_from_floor(model: str, decision_value_tokens: float) -> float:
    """tau ∝ FLOOR_model / decision_value (spec §2). Escalating is worth it iff the expected
    decision-regret retired exceeds the fine-probe cost (~one floor)."""
    return FLOOR[model] / max(1.0, decision_value_tokens)


@dataclass
class EscalationDecision:
    cell: Cell
    escalate: bool
    reason: str
    voi: float
    sev_hat: float
    stakes_hat: float
    uncertainty: float


def governor(candidates: Sequence[Cell], surrogate: Surrogate, cfg: GovernorConfig,
             rng: random.Random) -> List[EscalationDecision]:
    """escalate(cell) = irreversible(cell)                          [hard override]
                     OR uncertainty(cell) * stakes(cell) > tau      [VoI gate]
                     OR rand() < epsilon                            [exploration floor]
       ... AND the coarse severity ranking's top-K (relative, not absolute)."""
    scored: List[EscalationDecision] = []
    for cell in candidates:
        sev_hat, stk_hat, unc, irr = surrogate.predict(cell)
        voi = unc * stk_hat
        scored.append(EscalationDecision(cell, False, "", voi, sev_hat, stk_hat, unc))

    # top-K by coarse severity (the ordinal ranking, §1.2) — a *relative* escalation set.
    topk_cells = {
        d.cell for d in sorted(scored, key=lambda d: d.sev_hat, reverse=True)[: cfg.top_k]
    }

    for d in scored:
        sev_hat, stk_hat, unc, irr = surrogate.predict(d.cell)
        if irr:
            d.escalate, d.reason = True, "irreversible-override"
        elif d.cell in topk_cells:
            d.escalate, d.reason = True, "coarse-top-k"
        elif d.voi > cfg.tau:
            d.escalate, d.reason = True, "voi-gate"
        elif rng.random() < cfg.epsilon:
            d.escalate, d.reason = True, "epsilon-floor"
    return scored


# ----------------------------------------------------------------------------
# 7. The factorial pass IS the orthogonality falsifier (spec §4, ADR finding #4)
# ----------------------------------------------------------------------------

def factorial_orthogonality_test(grader: Grader, baseline: Cell,
                                 n_holdout: int, rng: random.Random,
                                 tol: float = 0.35) -> Dict[str, object]:
    """Main-effects design (vary one axis at a time from `baseline`) fits an additive model
      s_hat(cell) = mu + Σ_axis effect[axis][value]
    Then predict held-out JOINT cells (>=2 axes off baseline). Small error => axes ~additive
    (orthogonal); the penteract & its 3,125 count stand, proved for ~25 probes. Large error
    => interaction => the penteract collapses. The cost-optimization and the falsification are
    the same move.
    """
    # 1 + 5*4 = 21 main-effects probes (baseline + each axis's 4 non-baseline values).
    mu = grader(baseline).severity
    effect: Dict[int, Dict[int, float]] = {a: {baseline[a]: 0.0} for a in range(N_AXES)}
    probes = 1
    for a in range(N_AXES):
        for v in range(N_VALS):
            if v == baseline[a]:
                continue
            c = list(baseline)
            c[a] = v
            effect[a][v] = grader(tuple(c)).severity - mu  # type: ignore
            probes += 1

    def predict(cell: Cell) -> float:
        return mu + sum(effect[a].get(cell[a], 0.0) for a in range(N_AXES))

    # Held-out joint cells: perturb >=2 axes at once.
    errors: List[float] = []
    samples: List[Dict[str, object]] = []
    for _ in range(n_holdout):
        c = list(baseline)
        naxes = rng.randint(2, N_AXES)
        for a in rng.sample(range(N_AXES), naxes):
            c[a] = rng.randrange(N_VALS)
        cell = tuple(c)  # type: ignore
        actual = grader(cell).severity
        pred = predict(cell)
        err = abs(actual - pred)
        errors.append(err)
        samples.append({"cell": cell_label(cell), "actual": round(actual, 3),
                        "predicted": round(pred, 3), "abs_err": round(err, 3)})

    mae = sum(errors) / len(errors) if errors else 0.0
    orthogonal = mae <= tol
    return {
        "main_effect_probes": probes,
        "holdout_cells": n_holdout,
        "mae": round(mae, 3),
        "tolerance": tol,
        "verdict": "ORTHOGONAL (penteract stands)" if orthogonal else
                   "INTERACTION (penteract collapses — axes not independent)",
        "orthogonal": orthogonal,
        "worst": sorted(samples, key=lambda s: -s["abs_err"])[:3],  # type: ignore
    }


# ----------------------------------------------------------------------------
# 8. The tape (spec §2) — append-only run log; tau-calibration reads it
# ----------------------------------------------------------------------------

def repo_root() -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(here)  # scripts/ -> repo root


def tape_path() -> str:
    return os.path.join(repo_root(), "_STATE", "gauntlet-runs.jsonl")


def append_tape(row: Dict[str, object], path: Optional[str] = None) -> str:
    p = path or tape_path()
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")
    return p


def read_tape(path: Optional[str] = None) -> List[Dict[str, object]]:
    p = path or tape_path()
    if not os.path.exists(p):
        return []
    rows = []
    with open(p, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def calibrate_tau(cfg: GovernorConfig, path: Optional[str] = None) -> Tuple[float, str]:
    """tau-calibration (spec §2): read the tape and nudge tau from whether fine-gate probes
    earned their keep.
      - fine probes that rarely FLIP the coarse verdict  -> over-spending -> raise tau
      - a skipped-fine coarse verdict later FALSIFIED     -> under-spending -> lower tau
    Only engine-run rows carry the needed fields; older manual rows are skipped. Returns
    (new_tau, note). This is 'become-your-own-bookie', made mechanical — tau floats, never a
    magic constant."""
    rows = [r for r in read_tape(path) if r.get("kind") == "engine-run"]
    if not rows:
        return cfg.tau, "no engine-run rows on tape yet — tau unchanged (needs >= a few reps)"
    flips = sum(int(r.get("fine_flips", 0)) for r in rows)
    fine = sum(int(r.get("fine_probes", 0)) for r in rows)
    misses = sum(int(r.get("skipped_then_falsified", 0)) for r in rows)
    tau = cfg.tau
    notes = []
    if fine > 0:
        flip_rate = flips / fine
        if flip_rate < 0.15:
            tau = round(tau * 1.25, 4)
            notes.append(f"flip_rate={flip_rate:.2f} < .15 -> over-spending -> raise tau")
        elif flip_rate > 0.5:
            tau = round(tau * 0.85, 4)
            notes.append(f"flip_rate={flip_rate:.2f} > .5 -> escalations earning keep -> hold/ease")
    if misses > 0:
        tau = round(tau * 0.8, 4)
        notes.append(f"{misses} skipped-then-falsified -> under-spending -> lower tau")
    return tau, "; ".join(notes) or "within band — tau unchanged"


# ----------------------------------------------------------------------------
# 9. The amortized walker + the two-gate run (spec §1, §3, §5)
# ----------------------------------------------------------------------------

@dataclass
class RunResult:
    n_anchors: int
    escalated: List[str]
    escalation_reasons: Dict[str, int]
    cost: Dict[str, object]
    orthogonality: Optional[Dict[str, object]]
    localized_faults: Dict[str, bool]
    tape_row: Dict[str, object]


def run_gauntlet(grader: Grader, cfg: GovernorConfig, n_anchors: int = 25,
                 candidate_budget: int = 400, run_orthogonality: bool = True,
                 seed: int = 0, subject: str = "unspecified",
                 write_tape: bool = False, tape_file: Optional[str] = None) -> RunResult:
    """The full cheap->fine cycle:
      Gate 1 (coarse, INLINE — one amortized walker, NO spawn floor): grade a sparse LHS
        anchor set, fit the surrogate over the whole penteract.
      Governor: rank + VoI + epsilon + irreversible-override -> the escalation set.
      Gate 2 (fine, SPAWNED — one floor each): re-grade escalated cells independently.
    """
    rng = random.Random(seed)
    cost = CostModel()

    # --- Gate 1: coarse, inline, amortized walker over LHS anchors -----------
    anchors = latin_hypercube_anchors(n_anchors, rng)
    coarse_readings = [grader(a) for a in anchors]
    cost.inline(len(anchors))  # inline pays task tokens only — the whole point of §1
    surrogate = Surrogate(lam=1.2, beta=1.0).fit(anchors, coarse_readings)

    # Candidate pool the surrogate scores (a sparse random cover of the 3125, never enumerate).
    candidates = list(dict.fromkeys(
        [tuple(rng.randrange(N_VALS) for _ in range(N_AXES)) for _ in range(candidate_budget)]
        + anchors
    ))

    # --- Governor: value-of-information escalation set -----------------------
    decisions = governor(candidates, surrogate, cfg, rng)
    escalated = [d for d in decisions if d.escalate]
    reasons: Dict[str, int] = {}
    for d in escalated:
        reasons[d.reason] = reasons.get(d.reason, 0) + 1

    # --- Gate 2: fine, one spawn (amortized across escalated cells) ----------
    # The spec's key economy: amortize to the floor. One walker re-grades all escalated cells
    # in one context = ONE floor, not len(escalated) floors.
    fine_flips = 0
    if escalated:
        cost.spawn(cfg.model, len(escalated))
        for d in escalated:
            truth = grader(d.cell)  # in a real run this is the independent fine judgment
            # A "flip": the fine read materially disagrees with the coarse surrogate.
            if abs(truth.severity - d.sev_hat) > 0.75:
                fine_flips += 1

    # --- Did the cheap pass LOCALIZE the known faults? (the §5 validation) ----
    esc_labels = {cell_label(d.cell) for d in escalated}
    localized = {
        "C-lens-hot": any(".C." in ("." + lab + ".") or lab.startswith("C.") for lab in esc_labels),
        "NOTOMATION-x-COURT": any("COURT" in lab and (lab.startswith("C.") or lab.startswith("D."))
                                   for lab in esc_labels),
        "orthogonality-ruin-BAR": any("BAR" in lab and (lab.startswith("D.") or lab.startswith("R."))
                                       for lab in esc_labels),
    }

    ortho = (factorial_orthogonality_test(grader, baseline=(3, 0, 3, 3, 4),
                                          n_holdout=30, rng=random.Random(seed + 1))
             if run_orthogonality else None)

    tape_row: Dict[str, object] = {
        "run_id": f"engine-{seed}",
        "kind": "engine-run",
        "ts": "auto",  # caller may overwrite with a real date; scripts avoid Date.now anyway
        "subject": subject,
        "model": cfg.model,
        "n_anchors": n_anchors,
        "candidates": len(candidates),
        "escalated": len(escalated),
        "escalation_reasons": reasons,
        "fine_probes": len(escalated),
        "fine_flips": fine_flips,
        "skipped_then_falsified": 0,  # filled by a later close-the-loop pass
        "total_tokens": cost.total(),
        "cost_note": f"gate1 inline {n_anchors} cells (no floor) + gate2 one {cfg.model} floor",
        "localized_faults": localized,
        "orthogonality_mae": (ortho or {}).get("mae"),
    }
    if write_tape:
        append_tape(tape_row, tape_file)

    return RunResult(
        n_anchors=n_anchors,
        escalated=sorted(esc_labels),
        escalation_reasons=reasons,
        cost=cost.breakdown(),
        orthogonality=ortho,
        localized_faults=localized,
        tape_row=tape_row,
    )


# ----------------------------------------------------------------------------
# 10. Self-test — tries to BREAK the engine's own claims (falsification-first)
# ----------------------------------------------------------------------------

def selftest() -> int:
    rng = random.Random(42)
    failures: List[str] = []

    def check(name: str, ok: bool, detail: str = "") -> None:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))
        if not ok:
            failures.append(name)

    print("hypercube_sampler self-test (falsification-first)\n")

    # (a) LHS balance: with n a multiple of 5, every axis level hit exactly n/5 times.
    anchors = latin_hypercube_anchors(25, rng)
    balanced = all(
        all(sum(1 for c in anchors if c[a] == v) == 5 for v in range(N_VALS))
        for a in range(N_AXES)
    )
    check("LHS balances every axis level", balanced)

    # (b) Surrogate exactness: an anchor ON the cell => uncertainty ~ 0.
    field_ = SyntheticField()
    s = Surrogate(lam=1.2, beta=1.0).fit(anchors, [field_(a) for a in anchors])
    _, _, unc_on, _ = s.predict(anchors[0])
    check("surrogate uncertainty ~0 at an anchor", unc_on < 1e-6, f"u={unc_on:.2e}")

    # (c) Surrogate uncertainty grows off-anchor.
    far = tuple((anchors[0][a] + 2) % N_VALS for a in range(N_AXES))
    _, _, unc_far, _ = s.predict(far)  # type: ignore
    check("surrogate uncertainty grows away from anchors", unc_far > unc_on)

    # (d) Factorial test PASSES on an additive field and FAILS on a planted interaction.
    additive = factorial_orthogonality_test(
        lambda c: Reading(1.0 + 0.2 * c[0] + 0.1 * c[2], 0.1),
        baseline=(0, 0, 0, 0, 0), n_holdout=30, rng=random.Random(1))
    check("factorial: additive field reads ORTHOGONAL", additive["orthogonal"], f"mae={additive['mae']}")

    def interacting(c: Cell) -> Reading:
        # a strong lens x operator product term -> non-additive
        return Reading(1.0 + 1.5 * (c[0] * c[2]), 0.1)
    inter = factorial_orthogonality_test(interacting, baseline=(0, 0, 0, 0, 0),
                                         n_holdout=30, rng=random.Random(1))
    check("factorial: interaction field reads COLLAPSE", not inter["orthogonal"], f"mae={inter['mae']}")

    # (e) Governor: irreversible cell ALWAYS escalates, even at tau=inf, epsilon=0.
    cfg_hard = GovernorConfig(tau=1e9, epsilon=0.0, top_k=0)
    irr_cell = (0, 0, 2, 0, 0)  # BAR + D lens -> irreversible in the synthetic field
    s2 = Surrogate(lam=1.2, beta=1.0).fit([irr_cell], [field_(irr_cell)])
    dec = governor([irr_cell], s2, cfg_hard, random.Random(0))
    check("governor: irreversible override fires under tau=inf,eps=0", dec[0].escalate and
          dec[0].reason == "irreversible-override")

    # (f) Governor: epsilon floor fires on a benign cell when everything else is off.
    cfg_eps = GovernorConfig(tau=1e9, epsilon=1.0, top_k=0)  # eps=1 -> always
    benign = (2, 1, 0, 1, 1)  # W lens, LAB — no override, low VoI
    s3 = Surrogate(lam=1.2, beta=1.0).fit([benign], [field_(benign)])
    dec3 = governor([benign], s3, cfg_eps, random.Random(0))
    check("governor: epsilon floor can fire independent of surrogate", dec3[0].escalate)

    # (g) Cost model: inline pays NO floor; a spawn pays exactly one floor + task.
    cm = CostModel()
    cm.inline(25)
    check("cost: 25 inline cells pay no floor", cm.total() == 25 * TASK_TOKENS_PER_CELL,
          f"{cm.total()}")
    cm.spawn("haiku", 25)
    expect = 25 * TASK_TOKENS_PER_CELL + FLOOR["haiku"] + 25 * TASK_TOKENS_PER_CELL
    check("cost: one haiku spawn adds exactly one 54K floor", cm.total() == expect, f"{cm.total()}")

    # (h) End-to-end: the cheap pass LOCALIZES all three known faults (§5 validation).
    res = run_gauntlet(SyntheticField(), GovernorConfig(model="haiku", top_k=12),
                       n_anchors=25, seed=7, subject="ADR-055-selftest")
    all_localized = all(res.localized_faults.values())
    check("engine re-finds all 3 known faults from a 25-cell coarse pass",
          all_localized, str(res.localized_faults))

    # (i) The cheap run costs ~2 floors, not the 567K Opus gauntlet.
    cheap = res.cost["total_tokens"]
    check("cheap run << 567K Opus gauntlet", cheap < 150_000, f"{cheap} tokens")

    print()
    if failures:
        print(f"SELFTEST FAILED: {len(failures)} check(s) broke: {failures}")
        return 1
    print("SELFTEST PASSED: every claim survived its falsification attempt.")
    return 0


# ----------------------------------------------------------------------------
# 11. CLI
# ----------------------------------------------------------------------------

def _print_run(res: RunResult) -> None:
    print(f"\n== Hypercube gauntlet run ==")
    print(f"coarse anchors (inline, no floor): {res.n_anchors}")
    print(f"escalated cells (fine gate): {len(res.escalated)}")
    print(f"  reasons: {res.escalation_reasons}")
    print(f"cost: {json.dumps(res.cost)}")
    print(f"localized known faults: {json.dumps(res.localized_faults)}")
    if res.orthogonality:
        o = res.orthogonality
        print(f"orthogonality falsifier: {o['verdict']} (mae={o['mae']}, tol={o['tolerance']}, "
              f"{o['main_effect_probes']} main-effect probes)")
    print(f"\nescalation set (fine-gate targets):")
    for lab in res.escalated[:40]:
        print(f"  - {lab}")
    if len(res.escalated) > 40:
        print(f"  ... (+{len(res.escalated) - 40} more)")


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd")

    p_run = sub.add_parser("run", help="run the two-gate gauntlet on the synthetic field (deterministic)")
    p_run.add_argument("--subject", default="ADR-055")
    p_run.add_argument("--anchors", type=int, default=25)
    p_run.add_argument("--model", choices=list(FLOOR), default="haiku")
    p_run.add_argument("--top-k", type=int, default=10)
    p_run.add_argument("--tau", type=float, default=0.35)
    p_run.add_argument("--epsilon", type=float, default=0.05)
    p_run.add_argument("--seed", type=int, default=0)
    p_run.add_argument("--no-orthogonality", action="store_true")
    p_run.add_argument("--write-tape", action="store_true", help="append the run to _STATE/gauntlet-runs.jsonl")
    p_run.add_argument("--json", action="store_true", help="emit the tape row as JSON only")

    sub.add_parser("selftest", help="falsification-first self checks (no LLM)")

    p_cal = sub.add_parser("calibrate", help="read the tape and propose a new tau")
    p_cal.add_argument("--tau", type=float, default=0.35)

    args = p.parse_args(argv)

    if args.cmd == "selftest":
        return selftest()

    if args.cmd == "calibrate":
        new_tau, note = calibrate_tau(GovernorConfig(tau=args.tau))
        print(json.dumps({"old_tau": args.tau, "new_tau": new_tau, "note": note}, indent=2))
        return 0

    if args.cmd == "run" or args.cmd is None:
        a = args if args.cmd == "run" else p_run.parse_args([])
        cfg = GovernorConfig(tau=a.tau, epsilon=a.epsilon, top_k=a.top_k, model=a.model)
        res = run_gauntlet(SyntheticField(), cfg, n_anchors=a.anchors, seed=a.seed,
                           subject=a.subject, run_orthogonality=not a.no_orthogonality,
                           write_tape=a.write_tape)
        if getattr(a, "json", False):
            print(json.dumps(res.tape_row, indent=2))
        else:
            _print_run(res)
        return 0

    p.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
