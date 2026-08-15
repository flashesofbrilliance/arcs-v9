#!/usr/bin/env python3
"""
hypercube_sampler.py — the cost-governed hypercube gauntlet sampling engine (v1)

Implements _SPECS/hypercube-gauntlet-sampling-engine-v1.md, which itself implements
ADR-060 §8 (the two-gate architecture). This is the code that turns the spec's [H]
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
# 0. The penteract — 5 genuinely-orthogonal axes (ADR-060 §1)
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


def label_to_cell(label: str) -> Cell:
    """'C.Exec.COURT.synthesize.L5' -> (3,0,3,3,4). Inverse of cell_label."""
    parts = label.split(".")
    if len(parts) != N_AXES:
        raise ValueError(f"bad cell label {label!r}: expected {N_AXES} dotted parts")
    return tuple(AXES[name].index(parts[i]) for i, name in enumerate(AXIS_NAMES))  # type: ignore


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
    runs found (spec §0 tape; ADR-060 self-audit receipt). Not random noise — it is built
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

FLOOR = {
    "haiku": 54_000,   # [E] measured (spec §0, wf_56c743ca-18e)
    "sonnet": 68_000,  # [H] interpolated between haiku/opus — NOT independently measured
    "opus": 81_000,    # [E] measured (spec §0, wf_719c5843-ff0)
}
TASK_TOKENS_PER_CELL = 400  # [E] ~digest+output; dwarfed by the floor (bare cells; +subject-read is extra)

# Real capital cost — Anthropic list price, USD per 1M tokens (input, output).
# Source: claude-api skill pricing table (cached 2026-06-24). The gauntlet's spend is
# input-dominated: the ~54-81K floor is system-prompt + tool schemas + subject-read, all INPUT;
# the graded JSON is the only OUTPUT and is a few K. So the input rate governs the bill — and
# because the engine tier-routes (cheap Haiku coarse + Sonnet fine) against a 7x-Opus baseline,
# the DOLLAR compression exceeds the TOKEN compression.
PRICE_PER_MTOK = {           # (input $/1M, output $/1M)
    "haiku": (1.00, 5.00),
    "sonnet": (3.00, 15.00),  # standard; intro $2/$10 through 2026-08-31 — use standard to not under-state
    "opus": (5.00, 25.00),
}
OUTPUT_FRACTION = 0.05  # [H] the graded-JSON output is a small, ~flat share of a run's tokens;
                        # measured runs land 3-4%. 5% is a slight over-estimate so the $ figure
                        # is conservative (output is the pricier direction).


def dollars_exact(model: str, input_tokens: float, output_tokens: float,
                  cache_read_input_tokens: float = 0.0) -> float:
    """Precise capital cost when the real input/output split is known (e.g. the Anthropic API
    `usage` block). `cache_read_input_tokens` of the input bills at the ~0.1x cache-read rate."""
    pin, pout = PRICE_PER_MTOK[model]
    fresh_in = max(0.0, input_tokens - cache_read_input_tokens)
    return (fresh_in * pin + cache_read_input_tokens * pin * 0.1 + output_tokens * pout) / 1_000_000


def dollars(model: str, total_tokens: int, output_fraction: float = OUTPUT_FRACTION,
            cache_read_fraction: float = 0.0) -> float:
    """ESTIMATE — capital cost of `total_tokens` on `model` when only the TOTAL is known (the
    Agent-tool `subagent_tokens` metric gives a single aggregate, not an input/output split).
    Splits by `output_fraction`; input is the dominant, cheaper leg. When the real split IS known,
    use `dollars_exact` instead — that is what the tape's per-spawn cost_breakdown enables."""
    out_tok = total_tokens * output_fraction
    in_tok = total_tokens - out_tok
    return dollars_exact(model, in_tok, out_tok, in_tok * cache_read_fraction)


def price_spawn(spawn: Dict[str, object]) -> float:
    """Price one spawn from a cost_breakdown entry. Exact when input_tokens/output_tokens are
    present; falls back to the output_fraction estimate on total_tokens otherwise."""
    model = str(spawn["model"])
    if spawn.get("input_tokens") is not None and spawn.get("output_tokens") is not None:
        return dollars_exact(model, float(spawn["input_tokens"]), float(spawn["output_tokens"]),
                             float(spawn.get("cache_read_input_tokens") or 0.0))
    return dollars(model, int(spawn.get("total_tokens") or 0))


def parse_spawn(s: str) -> Dict[str, object]:
    """Parse a --spawn arg: 'model:total' | 'model:input:output' | 'model:input:output:cacheread'.
    A 2-field form records the aggregate (priced by estimate); 3+ fields record the exact split."""
    parts = s.split(":")
    model = parts[0]
    if model not in PRICE_PER_MTOK:
        raise ValueError(f"unknown model {model!r}; known: {list(PRICE_PER_MTOK)}")
    nums = [int(p) for p in parts[1:]]
    if len(nums) == 1:
        return {"model": model, "total_tokens": nums[0], "input_tokens": None, "output_tokens": None}
    if len(nums) >= 2:
        d = {"model": model, "input_tokens": nums[0], "output_tokens": nums[1],
             "total_tokens": nums[0] + nums[1]}
        if len(nums) >= 3:
            d["cache_read_input_tokens"] = nums[2]
        return d
    raise ValueError(f"--spawn needs at least model:total, got {s!r}")


@dataclass
class CostModel:
    """Total ~= Σ_spawned_agents (FLOOR_model + subject_read + task_tokens). Inline pays task
    only — no floor. `subject_read_tokens` is the cost of a spawned agent RE-READING the subject
    each spawn — a real term the live ADR-060 run exposed (2026-08-13): the modeled cost that
    omitted it under-counted by ~2x (85.6K modeled vs 177K measured). It is the SAME cacheable
    prefix across every spawn (grading_prefix()), so with prompt-caching only the first spawn
    pays it — set cache_subject=True to model that."""
    inline_task_tokens: int = 0
    subject_read_tokens: int = 0        # per-spawn re-read of the subject text
    cache_subject: bool = False         # prompt-caching: only the first spawn pays the read
    spawns: List[Tuple[str, int]] = field(default_factory=list)  # (model, cells_graded)

    def inline(self, cells: int) -> None:
        self.inline_task_tokens += cells * TASK_TOKENS_PER_CELL

    def spawn(self, model: str, cells: int) -> None:
        self.spawns.append((model, cells))

    def total(self) -> int:
        t = self.inline_task_tokens
        for i, (model, cells) in enumerate(self.spawns):
            t += FLOOR[model] + cells * TASK_TOKENS_PER_CELL
            if self.subject_read_tokens and not (self.cache_subject and i > 0):
                t += self.subject_read_tokens
        return t

    def breakdown(self) -> Dict[str, object]:
        return {
            "inline_task_tokens": self.inline_task_tokens,
            "spawn_count": len(self.spawns),
            "spawn_floors": sum(FLOOR[m] for m, _ in self.spawns),
            "subject_read_tokens": self.subject_read_tokens,
            "cache_subject": self.cache_subject,
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
    """The escalation set is BOUNDED — a union of bounded selectors, never unbounded predicates:

        escalate(cell) = irreversible(cell)            [hard override — COURT/free-solo]
                      OR cell in top-K by severity     [localize the biggest faults, §1.2]
                      OR cell in top-K by VoI          [spend where a probe cuts regret, §2]
                      OR rand() < epsilon              [mandatory exploration floor]

    Both top-Ks are RELATIVE (rank + take K), never an absolute cutoff. Spec §1.2, confirmed
    live 2026-08-13: an absolute threshold — on severity (the binary ripple's 25/25) OR on VoI
    (a real ADR-060 coarse pass escalated 380/400 under `voi > 0.35`) — floods. Severity and
    stakes are DIFFERENT axes (a huge fault at low ruin vs a small fault at existential ruin),
    so the gate needs both selectors; bounding each at K keeps the fine gate at ~2K + overrides.
    `tau` is retained only for the marginal-stop / calibration bookkeeping, not as a gate."""
    scored: List[EscalationDecision] = []
    for cell in candidates:
        sev_hat, stk_hat, unc, irr = surrogate.predict(cell)
        voi = unc * stk_hat
        scored.append(EscalationDecision(cell, False, "", voi, sev_hat, stk_hat, unc))

    topk_sev = {d.cell for d in sorted(scored, key=lambda d: d.sev_hat, reverse=True)[: cfg.top_k]}
    topk_voi = {d.cell for d in sorted(scored, key=lambda d: d.voi, reverse=True)[: cfg.top_k]}

    for d in scored:
        _, _, _, irr = surrogate.predict(d.cell)
        if irr:
            d.escalate, d.reason = True, "irreversible-override"
        elif d.cell in topk_sev:
            d.escalate, d.reason = True, "severity-top-k"
        elif d.cell in topk_voi:
            d.escalate, d.reason = True, "voi-top-k"
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
    """tau-calibration (spec §2) — DIRECTION-SPLIT (corrected by the 60-anchor falsification,
    2026-08-15). A raw flip rate conflates two opposite signals; splitting fine_flips by
    direction (from the tape's `flip_detail`, which stores coarse vs fine per flipped cell) is
    what makes tau move on the RIGHT signal:

      - UP-flip   (fine > coarse): the coarse pass UNDER-rated — it nearly missed a fault the
                  fine gate found. A recall hole = the dangerous one → lower tau / raise recall.
      - DOWN-flip (fine < coarse): the coarse pass OVER-rated; the fine gate zeroed a false
                  positive. This is the two-gate precision filter WORKING — healthy, not a
                  miscalibration. High down-flip rate does NOT move tau (if anything it argues
                  for a tighter top-K, handled separately).
      - near-zero total flips: the fine gate rarely changes anything → over-spending → raise tau.
      - skipped-fine coarse verdict later FALSIFIED (belief-log) → under-spending → lower tau.

    Only engine-run rows are read; rows without flip_detail fall back to undirected fine_flips
    (treated conservatively as recall signal). 'Become-your-own-bookie', made mechanical."""
    rows = [r for r in read_tape(path) if r.get("kind") == "engine-run"]
    if not rows:
        return cfg.tau, "no engine-run rows on tape yet — tau unchanged (needs >= a few reps)"
    up = down = undirected = fine = 0
    THRESH = 0.75  # same materiality bar bridge_close uses to count a flip
    for r in rows:
        fine += int(r.get("fine_probes", 0))
        detail = r.get("flip_detail")
        if isinstance(detail, list) and detail:
            for f in detail:
                try:
                    d = float(f["fine"]) - float(f["coarse"])
                except (KeyError, TypeError, ValueError):
                    undirected += 1
                    continue
                if d >= THRESH:
                    up += 1
                elif d <= -THRESH:
                    down += 1
        else:
            undirected += int(r.get("fine_flips", 0))  # no direction available
    misses = sum(int(r.get("skipped_then_falsified", 0)) for r in rows)
    tau = cfg.tau
    notes = []
    if fine > 0:
        up_rate = (up + undirected) / fine   # undirected counted as possible recall holes
        down_rate = down / fine
        total_rate = (up + down + undirected) / fine
        if up_rate > 0.15:
            tau = round(tau * 0.85, 4)
            notes.append(f"up-flip_rate={up_rate:.2f} > .15 (coarse missed faults) -> lower tau (raise recall)")
        elif total_rate < 0.10:
            tau = round(tau * 1.25, 4)
            notes.append(f"total_flip_rate={total_rate:.2f} < .10 (fine gate rarely changes verdict) -> raise tau")
        if down_rate >= 0.30:
            notes.append(f"down-flip_rate={down_rate:.2f} high but HEALTHY (fine gate killing coarse false-positives); "
                         f"tau unmoved — consider tighter top-K to shrink the coarse net")
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
# 9.5 The agent bridge — wire the fine-gate to a REAL model via stateless JSON
# ----------------------------------------------------------------------------
#
# The judgment seam. A pure-Python engine can't judge a cell; a live model can. This bridge
# lets the orchestrator (the main Claude loop, a Workflow, or a human) act as the amortized
# walker: three stateless JSON steps, real gradings supplied in between.
#
#   1. `anchors`  -> emits the LHS anchor cells + one grading prompt (one amortized spawn
#                    grades all of them = ONE floor, per spec §0 amortize-to-the-floor).
#   2. <grade>    -> the model returns [{label, severity, stakes, irreversible, note}, ...].
#   3. `escalate` -> fits the surrogate on those gradings, runs the governor, emits the
#                    fine-gate escalation set + its grading prompt (a second amortized spawn).
#   4. <grade>    -> the model grades the escalated cells (the independent fine judgment).
#   5. `close`    -> computes flips (coarse-vs-fine disagreement), cost, localized faults,
#                    and appends the run to the tape. THIS is where prompt/predictor quality
#                    gets scored by confirmed outcome.

_GRADE_SCHEMA_HINT = (
    'Return ONLY a JSON array, one object per cell, each: '
    '{"label": "<the cell label verbatim>", "severity": <0-3 float, ordinal>, '
    '"stakes": <0-1 float: ruin x irreversibility>, "irreversible": <bool>, '
    '"note": "<short: name the fault or say clean>"}. '
    'Severity is ORDINAL for ranking, not an absolute threshold. Refute-by-default: only a '
    'nonzero severity for a fault you can defend against the subject text.'
)


def grading_prefix(subject: str) -> str:
    """The CACHE-STABLE prefix: subject + axis key + schema. Identical across coarse and fine
    gates and every cell batch, so an AnthropicGrader marks it `cache_control` and pays the
    floor's re-read cost ONCE (the prompt-caching lever on the ~54K floor, spec §0). Ordered
    stable-first, variable-last on purpose."""
    axis_key = "; ".join(f"{name}={'/'.join(vals)}" for name, vals in AXES.items())
    return (
        f"You grade cells of the hypercube gauntlet for subject: {subject}.\n"
        f"Read the subject, then grade each cell for how severe a FAULT the subject has at that "
        f"coordinate. Axes — {axis_key}.\n"
        f"A cell = (lens.resolution.operator.verb.lstack): lens is the facet, operator the "
        f"adversary applying pressure, verb the cognitive move, lstack the coherence reach.\n"
        + _GRADE_SCHEMA_HINT
    )


def _grading_prompt(subject: str, cells: List[Cell], gate: str) -> str:
    """Cache-stable prefix first, then the variable suffix (gate label + cell list)."""
    lines = [f"  {i+1}. {cell_label(c)}" for i, c in enumerate(cells)]
    return (
        grading_prefix(subject)
        + f"\n\n--- this batch: {gate} gate ---\nGrade exactly these cells:\n"
        + "\n".join(lines)
    )


def bridge_anchors(n: int, seed: int, subject: str) -> Dict[str, object]:
    rng = random.Random(seed)
    anchors = latin_hypercube_anchors(n, rng)
    return {
        "step": "anchors",
        "subject": subject,
        "seed": seed,
        "gate": "coarse",
        "cells": [cell_label(c) for c in anchors],
        "grading_prompt": _grading_prompt(subject, anchors, "COARSE (cheap, amortized)"),
    }


def _readings_from_gradings(gradings: List[Dict[str, object]]) -> Tuple[List[Cell], List[Reading]]:
    cells, readings = [], []
    for g in gradings:
        cell = label_to_cell(str(g["label"]))
        cells.append(cell)
        readings.append(Reading(
            severity=float(g.get("severity", 0.0)),
            stakes=float(g.get("stakes", 0.0)),
            irreversible=bool(g.get("irreversible", False)),
            note=str(g.get("note", "")),
        ))
    return cells, readings


def bridge_escalate(anchor_gradings: List[Dict[str, object]], cfg: GovernorConfig,
                    subject: str, seed: int, candidate_budget: int = 400) -> Dict[str, object]:
    rng = random.Random(seed + 100)
    anchors, readings = _readings_from_gradings(anchor_gradings)
    surrogate = Surrogate(lam=1.2, beta=1.0).fit(anchors, readings)
    candidates = list(dict.fromkeys(
        [tuple(rng.randrange(N_VALS) for _ in range(N_AXES)) for _ in range(candidate_budget)]
        + anchors
    ))
    decisions = governor(candidates, surrogate, cfg, rng)
    escalated = [d for d in decisions if d.escalate]
    esc_cells = [d.cell for d in escalated]
    reasons: Dict[str, int] = {}
    for d in escalated:
        reasons[d.reason] = reasons.get(d.reason, 0) + 1
    return {
        "step": "escalate",
        "subject": subject,
        "gate": "fine",
        "escalated_count": len(escalated),
        "escalation_reasons": reasons,
        # carry the coarse surrogate estimate so `close` can measure flips.
        "coarse_estimate": {cell_label(d.cell): round(d.sev_hat, 3) for d in escalated},
        "cells": [cell_label(c) for c in esc_cells],
        "grading_prompt": _grading_prompt(subject, esc_cells, "FINE (independent verify)"),
    }


def bridge_close(fine_gradings: List[Dict[str, object]], coarse_estimate: Dict[str, float],
                 cfg: GovernorConfig, subject: str, seed: int, n_anchors: int,
                 write_tape: bool = False, tape_file: Optional[str] = None,
                 ts: str = "auto", measured_tokens: Optional[int] = None,
                 cost_breakdown: Optional[List[Dict[str, object]]] = None) -> Dict[str, object]:
    cost = CostModel()
    cost.inline(n_anchors)               # gate 1: one amortized coarse spawn's cells, inline-modeled
    fine_cells, fine_readings = _readings_from_gradings(fine_gradings)
    if fine_cells:
        cost.spawn(cfg.model, len(fine_cells))  # gate 2: one amortized fine floor

    # Flips: the confirmed-outcome score. Coarse predicted sev_hat; fine measured severity.
    flips, flip_detail = 0, []
    for cell, r in zip(fine_cells, fine_readings):
        lab = cell_label(cell)
        pred = coarse_estimate.get(lab)
        if pred is not None and abs(r.severity - pred) > 0.75:
            flips += 1
            flip_detail.append({"cell": lab, "coarse": pred, "fine": round(r.severity, 3)})

    esc_labels = {cell_label(c) for c in fine_cells}
    localized = {
        "C-lens-hot": any(lab.startswith("C.") for lab in esc_labels),
        "NOTOMATION-x-COURT": any("COURT" in lab and (lab.startswith("C.") or lab.startswith("D."))
                                   for lab in esc_labels),
        "orthogonality-ruin-BAR": any("BAR" in lab and (lab.startswith("D.") or lab.startswith("R."))
                                       for lab in esc_labels),
    }
    row = {
        "run_id": f"engine-live-{seed}",
        "kind": "engine-run",
        "ts": ts,
        "subject": subject,
        "model": cfg.model,
        "n_anchors": n_anchors,
        "escalated": len(fine_cells),
        "fine_probes": len(fine_cells),
        "fine_flips": flips,
        "flip_detail": flip_detail,
        "skipped_then_falsified": 0,
        "total_tokens_modeled": cost.total(),
        "total_tokens_measured": measured_tokens,  # actual harness usage when a live run supplies it
        "cost_note": f"gate1 {n_anchors} coarse cells (1 amortized spawn) + gate2 {len(fine_cells)} "
                     f"fine cells (1 amortized {cfg.model} spawn)",
        "localized_faults": localized,
    }
    # Precise capital: per-spawn cost breakdown so the run prices ITSELF on the tape instead of
    # being estimated downstream. Exact when the spawn carried an input/output split.
    if cost_breakdown:
        priced = []
        for sp in cost_breakdown:
            usd = price_spawn(sp)
            exact = sp.get("input_tokens") is not None
            priced.append({**sp, "usd": round(usd, 6), "priced": "exact" if exact else "estimate"})
        row["cost_breakdown"] = priced
        row["total_usd"] = round(sum(p["usd"] for p in priced), 6)
        if measured_tokens is None:
            row["total_tokens_measured"] = sum(int(p.get("total_tokens") or 0) for p in priced)
    if write_tape:
        append_tape(row, tape_file)
    return {"step": "close", "tape_row": row, "cost": cost.breakdown(),
            "total_usd": row.get("total_usd"),
            "flip_rate": round(flips / len(fine_cells), 3) if fine_cells else None}


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
                       n_anchors=25, seed=7, subject="ADR-060-selftest")
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
    p_run.add_argument("--subject", default="ADR-060")
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

    # --- agent bridge: wire the fine-gate to a real model via stateless JSON ---
    p_anc = sub.add_parser("anchors", help="bridge step 1: emit LHS anchor cells + coarse grading prompt")
    p_anc.add_argument("--subject", default="ADR-060")
    p_anc.add_argument("--anchors", type=int, default=25)
    p_anc.add_argument("--seed", type=int, default=0)

    p_esc = sub.add_parser("escalate", help="bridge step 3: coarse gradings JSON -> fine escalation set")
    p_esc.add_argument("gradings", help="path to JSON array of coarse gradings")
    p_esc.add_argument("--subject", default="ADR-060")
    p_esc.add_argument("--seed", type=int, default=0)
    p_esc.add_argument("--top-k", type=int, default=10)
    p_esc.add_argument("--tau", type=float, default=0.35)
    p_esc.add_argument("--epsilon", type=float, default=0.05)
    p_esc.add_argument("--model", choices=list(FLOOR), default="haiku")

    p_cls = sub.add_parser("close", help="bridge step 5: fine gradings JSON -> flips, cost, tape row")
    p_cls.add_argument("gradings", help="path to JSON array of fine gradings")
    p_cls.add_argument("escalation", help="path to the escalate-step JSON (carries coarse_estimate)")
    p_cls.add_argument("--subject", default="ADR-060")
    p_cls.add_argument("--seed", type=int, default=0)
    p_cls.add_argument("--anchors", type=int, default=25)
    p_cls.add_argument("--model", choices=list(FLOOR), default="haiku")
    p_cls.add_argument("--ts", default="auto")
    p_cls.add_argument("--measured", type=int, default=None, help="actual harness tokens spent (live run)")
    p_cls.add_argument("--spawn", action="append", default=None, metavar="model:total|model:in:out[:cacheread]",
                       help="per-spawn cost (repeatable) — records an exact/estimated cost_breakdown on the tape")
    p_cls.add_argument("--write-tape", action="store_true")

    args = p.parse_args(argv)

    if args.cmd == "selftest":
        return selftest()

    if args.cmd == "calibrate":
        new_tau, note = calibrate_tau(GovernorConfig(tau=args.tau))
        print(json.dumps({"old_tau": args.tau, "new_tau": new_tau, "note": note}, indent=2))
        return 0

    if args.cmd == "anchors":
        print(json.dumps(bridge_anchors(args.anchors, args.seed, args.subject), indent=2))
        return 0

    if args.cmd == "escalate":
        with open(args.gradings, encoding="utf-8") as f:
            gradings = json.load(f)
        cfg = GovernorConfig(tau=args.tau, epsilon=args.epsilon, top_k=args.top_k, model=args.model)
        print(json.dumps(bridge_escalate(gradings, cfg, args.subject, args.seed), indent=2))
        return 0

    if args.cmd == "close":
        with open(args.gradings, encoding="utf-8") as f:
            fine = json.load(f)
        with open(args.escalation, encoding="utf-8") as f:
            esc = json.load(f)
        cfg = GovernorConfig(model=args.model)
        breakdown = [parse_spawn(s) for s in args.spawn] if args.spawn else None
        out = bridge_close(fine, esc.get("coarse_estimate", {}), cfg, args.subject, args.seed,
                           args.anchors, write_tape=args.write_tape, ts=args.ts,
                           measured_tokens=args.measured, cost_breakdown=breakdown)
        print(json.dumps(out, indent=2))
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
