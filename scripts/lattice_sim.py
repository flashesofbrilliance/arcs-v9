#!/usr/bin/env python3
"""
lattice_sim.py — Structural load test for the superionic goal lattice (ADR-023).

This is the ANTERIOR/POSTERIOR simulation harness for the Conductor loop. It does NOT
set production constants — per the ADR-023 PR gate, those are BLOCKED until a real-corpus
Zipf baseline (100+ receipts) can be measured. This harness certifies only:
  (1) the machinery runs and each counter-force has its predicted directional effect,
  (2) a non-empty stable (SUPERIONIC) envelope exists on parametrized synthetic load,
  (3) the FMEA failure modes F1-F6 are reproducible and detected.

Everything it emits is stamped PROVISIONAL / SYNTHETIC.

The Conductor steps a ballet of operators each tick:
    folksonomist (grow edges) -> reinforce -> decay -> contrarian -> calc-guard -> sentinel

Goal lattice is modelled at the goal-CONCEPT level (what the Folksonomist actually grows);
the goal_edges (receipt,receipt) table in ADR-023 is the persistence projection of this.

Modes:
    anterior  — forward-simulate under load, classify final phase, detect failure modes
    posterior — replay an anterior trajectory log, recoil analysis (when did it calcify?)
    sweep     — grid over (lambda, c, g); report the stable SUPERIONIC envelope
    test      — assert F1-F6 reproduce and the envelope is non-empty; exit 0/1 (the gate)

Usage:
    python3 scripts/lattice_sim.py test
    python3 scripts/lattice_sim.py anterior --ticks 200 --inflow 8 --decay 0.1 --cadence 10 --cap 0.55
    python3 scripts/lattice_sim.py sweep
    python3 scripts/lattice_sim.py posterior   # replays the last anterior run
"""
from __future__ import annotations

import argparse
import json
import math
import os
import random
from dataclasses import dataclass, asdict
from datetime import date
from itertools import combinations
from typing import Dict, List, Optional, Tuple

SEED = 42
EDGE_FLOOR = 0.05          # edges below this are pruned (the lattice floor)
VOCAB = 40                 # number of goal-concepts
PERSIST_WINDOW = 12        # ticks an argmax node must hold to count as a stable attractor
N_MIN_HOLD = 50            # F4: below this many receipts, the lattice HOLDs (no inference)

Edge = Tuple[int, int]


# ─────────────────────────────────────────────────────────────────────────────
# Load model — synthetic receipt stream
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class Load:
    """The thrust. Reinforcement inflow + the rich-get-richer feedback that drives
    preferential attachment — the force the buttresses must carry. Without pref_attach
    there is no self-reinforcing regime and the lattice cannot calcify (F1 needs it)."""
    inflow: float = 8.0       # R: receipts per tick (mean)
    burstiness: float = 0.0   # 0 = steady; >0 multiplies per-tick variance
    skew: float = 1.0         # Zipf exponent over concepts (>1 = more concentrated)
    pref_attach: float = 6.0  # preferential-attachment coefficient (the cyclic feedback)
    k_min: int = 2
    k_max: int = 4


def zipf_weights(n: int, skew: float) -> List[float]:
    raw = [1.0 / ((i + 1) ** skew) for i in range(n)]
    s = sum(raw)
    return [r / s for r in raw]


def draw_receipt(rng: random.Random, probs: List[float], k_min: int, k_max: int) -> List[int]:
    k = rng.randint(k_min, k_max)
    chosen: List[int] = []
    idx = list(range(len(probs)))
    # weighted sampling without replacement
    pool_p = probs[:]
    for _ in range(min(k, len(idx))):
        total = sum(pool_p)
        r = rng.random() * total
        acc = 0.0
        for j in idx:
            acc += pool_p[j]
            if acc >= r:
                chosen.append(j)
                pool_p[j] = 0.0
                break
    return chosen


# ─────────────────────────────────────────────────────────────────────────────
# Constants under test (the L7-governed pressure constants — swept here, not set)
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class Pressure:
    decay: float = 0.10       # lambda: fraction of edge weight shed per tick (LP-DECAY-01)
    cadence: int = 10         # c: contrarian injection every c ticks (0 = off) (LP-CONTRA-01)
    cap: float = 0.55         # g: hub weight-share ceiling; guard acts above it (LP-CALC-01)
    gain: float = 1.0


# ─────────────────────────────────────────────────────────────────────────────
# Phase readings — TWO proxies on purpose (F5: cheap proxies can diverge from the
# true minimal-DFA complexity; we compute two and report disagreement as a caveat).
# ─────────────────────────────────────────────────────────────────────────────
def node_strengths(edges: Dict[Edge, float]) -> Dict[int, float]:
    s: Dict[int, float] = {}
    for (a, b), w in edges.items():
        s[a] = s.get(a, 0.0) + w
        s[b] = s.get(b, 0.0) + w
    return s


def top_share(edges: Dict[Edge, float]) -> float:
    s = node_strengths(edges)
    tot = sum(s.values())
    if tot <= 0:
        return 0.0
    return max(s.values()) / tot


def gini(edges: Dict[Edge, float]) -> float:
    ws = sorted(w for w in edges.values() if w > 0)
    n = len(ws)
    if n == 0:
        return 0.0
    cum = sum((i + 1) * w for i, w in enumerate(ws))
    return (2 * cum) / (n * sum(ws)) - (n + 1) / n


def eff_attractors(edges: Dict[Edge, float]) -> float:
    """Hill number: exp(Shannon entropy of node-strength distribution)."""
    s = node_strengths(edges)
    tot = sum(s.values())
    if tot <= 0:
        return 0.0
    h = -sum((v / tot) * math.log(v / tot) for v in s.values() if v > 0)
    return math.exp(h)


def classify(g_val: float, stable: bool, n_receipts: int) -> str:
    """PRIMARY phase reading. Gini of edge weights tracks core-concentration — the real
    calcification signature in a co-occurrence lattice (weight freezes into a dense core,
    not a single star node), so it is the structural gauge."""
    if n_receipts < N_MIN_HOLD:
        return "HOLD"                       # F4 guard
    if g_val >= 0.78:
        return "SOLID"                      # F1 — weight frozen into a dense core
    if g_val < 0.30 or not stable:
        return "GAS"                        # F2 — no structure holds / no settled attractor
    return "SUPERIONIC"


def classify_secondary(share: float, n_receipts: int) -> str:
    """SECOND, deliberately-divergent proxy (F5). Node-strength share misses core
    concentration — it stays mid-band even when gini says SOLID. The disagreement IS the
    demonstration that a cheap proxy can read SUPERIONIC while the structure calcifies."""
    if n_receipts < N_MIN_HOLD:
        return "HOLD"
    if share >= 0.55:
        return "SOLID"
    if share < 0.15:
        return "GAS"
    return "SUPERIONIC"


# ─────────────────────────────────────────────────────────────────────────────
# The Conductor — one tick of the operator ballet
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class TickLog:
    tick: int
    n_receipts: int
    top_share: float
    gini: float
    eff_attractors: float
    active_edges: int
    phase: str
    phase_alt: str
    guard_fired: bool
    argmax_node: Optional[int]


def conductor_tick(rng, edges, probs, load, pres, tick, argmax_history) -> TickLog:
    # 1. inflow this tick (burstiness perturbs R)
    r = load.inflow
    if load.burstiness > 0:
        r = max(0.0, rng.gauss(load.inflow, load.inflow * load.burstiness))
    n_new = int(round(r))

    # 2. folksonomist: grow/reinforce co-occurrence edges.
    #    Preferential attachment: draw probability blends static Zipf with CURRENT node
    #    strength (the rich-get-richer feedback). This is the cyclic regime where
    #    calcification is possible; with pref_attach=0 it collapses to static Zipf.
    n_receipts_delta = 0
    strengths = node_strengths(edges)
    tot_s = sum(strengths.values())
    if tot_s > 0 and load.pref_attach > 0:
        eff_probs = [probs[i] * (1.0 + load.pref_attach * strengths.get(i, 0.0) / tot_s)
                     for i in range(len(probs))]
        es = sum(eff_probs)
        eff_probs = [p / es for p in eff_probs]
    else:
        eff_probs = probs
    for _ in range(n_new):
        concepts = draw_receipt(rng, eff_probs, load.k_min, load.k_max)
        n_receipts_delta += 1
        for a, b in combinations(sorted(set(concepts)), 2):
            edges[(a, b)] = edges.get((a, b), 0.0) + pres.gain

    # 3. decay (LP-DECAY-01) + prune below floor
    for e in list(edges.keys()):
        edges[e] *= (1.0 - pres.decay)
        if edges[e] < EDGE_FLOOR:
            del edges[e]

    # 4. contrarian injection (LP-CONTRA-01): challenge the current top attractor
    if pres.cadence and tick % pres.cadence == 0 and edges:
        s = node_strengths(edges)
        hub = max(s, key=s.get)
        # pick an orthogonal node not currently linked to the hub
        candidates = [n for n in range(VOCAB)
                      if n != hub and (min(n, hub), max(n, hub)) not in edges]
        if candidates:
            other = rng.choice(candidates)
            e = (min(other, hub), max(other, hub))
            edges[e] = edges.get(e, 0.0) + pres.gain * 1.5  # a fair challenge

    # 5. calcification guard (LP-CALC-01): if hub share > cap, fire an extra challenge
    guard_fired = False
    share = top_share(edges)
    if edges and share > pres.cap:
        guard_fired = True
        s = node_strengths(edges)
        hub = max(s, key=s.get)
        candidates = [n for n in range(VOCAB)
                      if n != hub and (min(n, hub), max(n, hub)) not in edges]
        if candidates:
            other = rng.choice(candidates)
            e = (min(other, hub), max(other, hub))
            edges[e] = edges.get(e, 0.0) + pres.gain * 2.0

    # 6. sentinel: read the phase
    s = node_strengths(edges)
    argmax_node = max(s, key=s.get) if s else None
    argmax_history.append(argmax_node)
    stable = (len(argmax_history) >= PERSIST_WINDOW
              and len(set(argmax_history[-PERSIST_WINDOW:])) == 1
              and argmax_node is not None)

    return TickLog(
        tick=tick, n_receipts=n_receipts_delta,
        top_share=round(share, 4), gini=round(gini(edges), 4),
        eff_attractors=round(eff_attractors(edges), 3),
        active_edges=len(edges), phase="", phase_alt="",
        guard_fired=guard_fired, argmax_node=argmax_node,
    ), stable


# ─────────────────────────────────────────────────────────────────────────────
# Anterior — forward simulation under load
# ─────────────────────────────────────────────────────────────────────────────
def run_anterior(load: Load, pres: Pressure, ticks: int, seed: int = SEED) -> Dict:
    rng = random.Random(seed)
    probs = zipf_weights(VOCAB, load.skew)
    edges: Dict[Edge, float] = {}
    argmax_history: List[Optional[int]] = []
    cum_receipts = 0
    logs: List[TickLog] = []

    for t in range(1, ticks + 1):
        log, stable = conductor_tick(rng, edges, probs, load, pres, t, argmax_history)
        cum_receipts += log.n_receipts
        log.phase = classify(log.gini, stable, cum_receipts)          # primary: gini
        log.phase_alt = classify_secondary(log.top_share, cum_receipts)  # divergent proxy
        logs.append(log)

    final = logs[-1]
    # failure-mode detection over the trajectory
    phases = [l.phase for l in logs]
    flips = sum(1 for i in range(1, len(phases)) if phases[i] != phases[i - 1])
    sensor_disagreements = sum(1 for l in logs if l.phase != l.phase_alt and l.phase != "HOLD")

    return {
        "load": asdict(load),
        "pressure": asdict(pres),
        "ticks": ticks,
        "cum_receipts": cum_receipts,
        "final_phase": final.phase,
        "final_top_share": final.top_share,
        "final_gini": final.gini,
        "final_eff_attractors": final.eff_attractors,
        "phase_flips": flips,                         # F3 proxy
        "sensor_disagreements": sensor_disagreements, # F5 proxy
        "trajectory": [asdict(l) for l in logs],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Posterior — recoil analysis over a trajectory
# ─────────────────────────────────────────────────────────────────────────────
def run_posterior(run: Dict) -> Dict:
    traj = run["trajectory"]
    first_solid = next((l["tick"] for l in traj if l["phase"] == "SOLID"), None)
    first_stable = next((l["tick"] for l in traj
                         if l["phase"] == "SUPERIONIC"), None)
    lock_tick = None
    # when did an argmax node lock for good?
    for i in range(len(traj) - PERSIST_WINDOW):
        window = {traj[j]["argmax_node"] for j in range(i, i + PERSIST_WINDOW)}
        if len(window) == 1 and None not in window:
            lock_tick = traj[i]["tick"]
            break
    guard_fires = sum(1 for l in traj if l["guard_fired"])
    return {
        "first_superionic_tick": first_stable,
        "first_solid_tick": first_solid,
        "attractor_lock_tick": lock_tick,
        "guard_fires": guard_fires,
        "recoil": (
            "calcified — buttresses did not carry the thrust" if first_solid
            else "held in band" if run["final_phase"] == "SUPERIONIC"
            else f"ended {run['final_phase']}"
        ),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Sweep — map the stable envelope over (lambda, c, g)
# ─────────────────────────────────────────────────────────────────────────────
def run_sweep(load: Load, ticks: int = 150) -> Dict:
    lambdas = [0.0, 0.05, 0.10, 0.20, 0.40, 0.80]
    cadences = [0, 5, 10, 20]
    caps = [0.40, 0.55, 0.70, 1.0]
    envelope: List[Dict] = []
    grid: List[Dict] = []
    for lam in lambdas:
        for c in cadences:
            for g in caps:
                pres = Pressure(decay=lam, cadence=c, cap=g)
                res = run_anterior(load, pres, ticks)
                cell = {"decay": lam, "cadence": c, "cap": g, "phase": res["final_phase"]}
                grid.append(cell)
                if res["final_phase"] == "SUPERIONIC":
                    envelope.append(cell)
    return {
        "load": asdict(load),
        "ticks": ticks,
        "envelope_size": len(envelope),
        "grid_size": len(grid),
        "envelope": envelope,
        "envelope_nonempty": len(envelope) > 0,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Test — the pre-PR machinery gate (asserts F1-F6 reproduce). Exit 0/1.
# ─────────────────────────────────────────────────────────────────────────────
def run_test() -> int:
    results: List[Tuple[str, bool, str]] = []

    # F1: no decay + skewed high load -> SOLID (compression / calcification)
    r = run_anterior(Load(inflow=10, skew=1.3), Pressure(decay=0.0, cadence=0, cap=1.0), 150)
    results.append(("F1 SOLID collapse reproduces (decay off)",
                    r["final_phase"] == "SOLID", r["final_phase"]))

    # F2: very high decay -> no settled structure -> GAS (tension)
    r = run_anterior(Load(inflow=8, skew=1.0), Pressure(decay=0.85, cadence=0, cap=1.0), 150)
    results.append(("F2 GAS blowout reproduces (decay maxed)",
                    r["final_phase"] in ("GAS", "HOLD"), r["final_phase"]))

    # F3: oscillation observable (phase flips > 0 somewhere in the regime)
    r = run_anterior(Load(inflow=8, skew=1.1, burstiness=0.6),
                     Pressure(decay=0.45, cadence=3, cap=0.5), 150)
    results.append(("F3 oscillation observable (flips>0)",
                    r["phase_flips"] > 0, f"flips={r['phase_flips']}"))

    # F4: small N holds, does NOT prematurely lock
    r = run_anterior(Load(inflow=2, skew=1.4), Pressure(decay=0.05, cadence=10, cap=0.55), 8)
    results.append(("F4 premature lock prevented by HOLD (<N_min)",
                    r["final_phase"] == "HOLD", r["final_phase"]))

    # F5: the two phase proxies disagree somewhere (sensor caveat is real)
    r = run_anterior(Load(inflow=8, skew=1.2), Pressure(decay=0.1, cadence=10, cap=0.55), 150)
    results.append(("F5 sensor proxies diverge (disagreements>0)",
                    r["sensor_disagreements"] > 0, f"disagreements={r['sensor_disagreements']}"))

    # Envelope: a non-empty SUPERIONIC region exists at moderate load (F6 — constants matter)
    sw = run_sweep(Load(inflow=8, skew=1.1), ticks=120)
    results.append(("Stable SUPERIONIC envelope is non-empty",
                    sw["envelope_nonempty"], f"size={sw['envelope_size']}/{sw['grid_size']}"))

    print("\nLATTICE STRUCTURAL LOAD TEST (ADR-023) — synthetic, PROVISIONAL\n" + "-" * 64)
    ok = True
    for name, passed, detail in results:
        ok = ok and passed
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}  ({detail})")
    print("-" * 64)
    print(f"  RESULT: {'GREEN — machinery sound' if ok else 'FAIL'}")
    print("  NOTE: certifies machinery + failure-mode reproduction ONLY.")
    print("  PR remains BLOCKED until real-corpus Zipf baseline (100+ receipts) — ADR-023.\n")
    return 0 if ok else 1


# ─────────────────────────────────────────────────────────────────────────────
def out_dir() -> str:
    d = os.path.join("exports", "lattice", date.today().isoformat())
    os.makedirs(d, exist_ok=True)
    return d


def write_receipt(name: str, payload: Dict) -> str:
    payload = {
        "_stamp": "PROVISIONAL / SYNTHETIC",
        "_pr_gate": "BLOCKED until real-corpus Zipf baseline (100+ receipts) — ADR-023",
        "_governing_adr": "_DECISIONS/ADR-023-observability-goal-lattice.md",
        "_rom": "runtime/specs/lattice-pressure-rom.json",
        **payload,
    }
    path = os.path.join(out_dir(), f"{name}.json")
    with open(path, "w") as f:
        json.dump(payload, f, indent=2)
    return path


def main() -> int:
    ap = argparse.ArgumentParser(description="Superionic goal-lattice structural load test")
    ap.add_argument("mode", choices=["anterior", "posterior", "sweep", "test"])
    ap.add_argument("--ticks", type=int, default=200)
    ap.add_argument("--inflow", type=float, default=8.0)
    ap.add_argument("--burstiness", type=float, default=0.0)
    ap.add_argument("--skew", type=float, default=1.1)
    ap.add_argument("--decay", type=float, default=0.10)
    ap.add_argument("--cadence", type=int, default=10)
    ap.add_argument("--cap", type=float, default=0.55)
    args = ap.parse_args()

    if args.mode == "test":
        return run_test()

    load = Load(inflow=args.inflow, burstiness=args.burstiness, skew=args.skew)
    pres = Pressure(decay=args.decay, cadence=args.cadence, cap=args.cap)

    if args.mode == "anterior":
        res = run_anterior(load, pres, args.ticks)
        p = write_receipt("anterior", res)
        print(f"anterior: final_phase={res['final_phase']} "
              f"top_share={res['final_top_share']} flips={res['phase_flips']} -> {p}")
    elif args.mode == "posterior":
        path = os.path.join(out_dir(), "anterior.json")
        if not os.path.exists(path):
            print("no anterior.json to replay — run `anterior` first")
            return 1
        with open(path) as f:
            run = json.load(f)
        rec = run_posterior(run)
        p = write_receipt("posterior", rec)
        print(f"posterior recoil: {rec['recoil']} "
              f"(lock@{rec['attractor_lock_tick']}, solid@{rec['first_solid_tick']}) -> {p}")
    elif args.mode == "sweep":
        res = run_sweep(load, ticks=args.ticks)
        p = write_receipt("sweep", res)
        print(f"sweep: SUPERIONIC envelope {res['envelope_size']}/{res['grid_size']} cells -> {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
