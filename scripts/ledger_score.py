#!/usr/bin/env python3
"""ledger_score.py: score the falsification ledger as probability forecasts (read-only, stdlib only).

Convention: runtime/specs/ledger-forecast-fields.md. A row is scored when it has a numeric
`probability` in [0,1] (fallback: a numeric `prior` in [0,1], labelled 'legacy prior, not
calibrated') AND a verdict of CONFIRMED (outcome 1) or FALSIFIED (outcome 0).
Any other verdict, or a row past `resolve_by` with no verdict, is unresolved: counted, never
dropped. A row with no usable probability is unscoreable: counted, never guessed.
Skill is not claimed below N_MIN scored rows per cohort. Output is deterministic.

Usage:
  python3 scripts/ledger_score.py [--ledger PATH] [--today YYYY-MM-DD]
  python3 scripts/ledger_score.py --self-test
"""
import argparse
import json
import math
import random
import sys
from datetime import date
from pathlib import Path

DEFAULT_LEDGER = Path(__file__).resolve().parent.parent / "_STATE" / "falsification-ledger.jsonl"
N_MIN = 30
CLIP = (0.001, 0.999)
RESAMPLES = 10000
SEED = 20261017
LEGACY_LABEL = "legacy prior, not calibrated"


def _num01(v):
    """A usable probability: a real number (not bool) in [0,1], else None."""
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        return None
    if math.isnan(v) or not (0.0 <= v <= 1.0):
        return None
    return float(v)


def classify(rows, today):
    """Split rows into scored / unresolved / unscoreable. Nothing is dropped."""
    scored, unresolved, unscoreable = [], [], []
    for r in rows:
        p, src = _num01(r.get("probability")), "new"
        if p is None:
            p, src = _num01(r.get("prior")), "legacy"
        if p is None:
            unscoreable.append(r)
            continue
        verdict = r.get("verdict")
        if verdict in ("CONFIRMED", "FALSIFIED"):
            scored.append({"p": p, "o": 1 if verdict == "CONFIRMED" else 0, "src": src,
                           "prov": r.get("provenance"), "id": r.get("id")})
            continue
        rb = r.get("resolve_by")
        overdue = False
        if isinstance(rb, str) and not verdict:
            try:
                overdue = date.fromisoformat(rb) < today
            except ValueError:
                pass
        unresolved.append({"id": r.get("id"), "overdue": overdue})
    return scored, unresolved, unscoreable


def brier(ps, os_):
    return sum((p - o) ** 2 for p, o in zip(ps, os_)) / len(ps)


def logscore(ps, os_):
    """Mean log loss with clipped probabilities (lower is better)."""
    lo, hi = CLIP
    t = 0.0
    for p, o in zip(ps, os_):
        p = min(max(p, lo), hi)
        t += -(o * math.log(p) + (1 - o) * math.log(1 - p))
    return t / len(ps)


def bss(ps, os_):
    """Brier skill score against the base-rate forecast; None if the base forecast is perfect."""
    base = sum(os_) / len(os_)
    bs_base = base * (1 - base)
    if bs_base == 0:
        return None
    return 1 - brier(ps, os_) / bs_base


def bootstrap_bss(ps, os_):
    rng = random.Random(SEED)
    n = len(ps)
    vals, skipped = [], 0
    for _ in range(RESAMPLES):
        idx = [rng.randrange(n) for _ in range(n)]
        v = bss([ps[i] for i in idx], [os_[i] for i in idx])
        if v is None:
            skipped += 1
        else:
            vals.append(v)
    if not vals:
        return None, skipped
    vals.sort()
    lo = vals[int(0.025 * (len(vals) - 1))]
    hi = vals[int(math.ceil(0.975 * (len(vals) - 1)))]
    return (lo, hi), skipped


def calibration(ps, os_):
    bins = [[] for _ in range(5)]
    for p, o in zip(ps, os_):
        bins[min(int(p * 5), 4)].append((p, o))
    out = []
    for i, b in enumerate(bins):
        lo, hi = i / 5, (i + 1) / 5
        label = f"[{lo:.1f},{hi:.1f}{']' if i == 4 else ')'}"
        if b:
            out.append((label, len(b), sum(p for p, _ in b) / len(b), sum(o for _, o in b) / len(b)))
        else:
            out.append((label, 0, None, None))
    return out


def cohort_stats(items):
    ps, os_ = [x["p"] for x in items], [x["o"] for x in items]
    n = len(items)
    s = {"n": n}
    if n == 0:
        return s
    s["base_rate"] = sum(os_) / n
    s["brier"] = brier(ps, os_)
    s["logscore"] = logscore(ps, os_)
    s["calibration"] = calibration(ps, os_)
    if n >= N_MIN:
        s["bss"] = bss(ps, os_)
        s["ci"], s["ci_skipped"] = bootstrap_bss(ps, os_)
    return s


def fmt(v):
    return "n/a" if v is None else f"{v:.4f}"


def render_cohort(name, items, note=""):
    s = cohort_stats(items)
    lines = [f"## cohort: {name}{(' (' + note + ')') if note else ''}", f"n scored: {s['n']}"]
    if s["n"] == 0:
        lines.append("no scored rows")
        return lines, s
    lines += [f"base rate (share CONFIRMED): {fmt(s['base_rate'])}",
              f"Brier score: {fmt(s['brier'])}  (descriptive)",
              f"log score (mean log loss, clipped to [{CLIP[0]}, {CLIP[1]}]): {fmt(s['logscore'])}  (descriptive)"]
    if s["n"] < N_MIN:
        lines.append(f"BSS vs base-rate forecast: insufficient (n={s['n']})")
        lines.append(f"95% bootstrap interval for BSS: insufficient (n={s['n']})")
    else:
        lines.append(f"BSS vs base-rate forecast: {fmt(s['bss'])}")
        if s["ci"] is None:
            lines.append("95% bootstrap interval for BSS: n/a (base-rate forecast is perfect)")
        else:
            lines.append(f"95% bootstrap interval for BSS ({RESAMPLES} resamples, seed {SEED}): "
                         f"[{s['ci'][0]:.4f}, {s['ci'][1]:.4f}]  degenerate resamples skipped: {s['ci_skipped']}")
    lines.append("calibration (5 bins): bin | n | mean forecast | observed freq")
    for label, n, mf, of in s["calibration"]:
        lines.append(f"  {label} | {n} | {fmt(mf)} | {fmt(of)}")
    return lines, s


def report(rows, today, bad_lines=0):
    scored, unresolved, unscoreable = classify(rows, today)
    new = [x for x in scored if x["src"] == "new"]
    leg = [x for x in scored if x["src"] == "legacy"]
    L = ["# ledger_score (read-only)",
         f"rows read: {len(rows)}  unparseable lines: {bad_lines}",
         f"n scored: {len(scored)}  (new-field: {len(new)}, legacy prior: {len(leg)})",
         f"n unresolved: {len(unresolved)}  (past resolve_by with no verdict: "
         f"{sum(1 for u in unresolved if u['overdue'])})",
         f"n unscoreable: {len(unscoreable)}  (no usable probability; none guessed)",
         "caveat: old priors were not written as calibrated probabilities; legacy numbers are rough.", ""]
    for name, items, note in (("new-field", new, ""), ("legacy", leg, LEGACY_LABEL)):
        out, _ = render_cohort(name, items, note)
        L += out + [""]
    provs = sorted({str(x["prov"]) for x in scored if x["prov"] is not None})
    for pv in provs:
        out, _ = render_cohort(f"provenance={pv}", [x for x in scored if str(x["prov"]) == pv])
        L += out + [""]
    return "\n".join(L).rstrip() + "\n"


def load(path):
    rows, bad = [], 0
    for line in Path(path).read_text().splitlines():
        if not line.strip():
            continue
        try:
            v = json.loads(line)
        except ValueError:
            bad += 1
            continue
        if isinstance(v, dict):
            rows.append(v)
        else:
            bad += 1
    return rows, bad


def self_test():
    fails = []

    def check(name, got, want, tol=1e-9):
        ok = (got == want) if not isinstance(want, float) else (got is not None and abs(got - want) <= tol)
        if not ok:
            fails.append(f"{name}: got {got!r} want {want!r}")

    # hand-computed: p=[.8,.6,.2], o=[1,0,0]
    ps, os_ = [0.8, 0.6, 0.2], [1, 0, 0]
    check("hand brier", brier(ps, os_), 0.44 / 3)
    check("hand bss", bss(ps, os_), 1 - (0.44 / 3) / (2 / 9))
    check("hand bss value", bss(ps, os_), 0.34)
    check("hand log", logscore(ps, os_), (-math.log(0.8) - math.log(0.4) - math.log(0.8)) / 3)
    # planted perfect forecast
    pp = [1.0, 0.0] * 20
    po = [1, 0] * 20
    check("perfect brier", brier(pp, po), 0.0)
    check("perfect bss", bss(pp, po), 1.0)
    ci, _ = bootstrap_bss(pp, po)
    check("perfect ci lo", ci[0], 1.0)
    # planted anti-forecast
    ap = [0.0, 1.0] * 20
    check("anti brier", brier(ap, po), 1.0)
    check("anti bss", bss(ap, po), -3.0)
    check("anti log finite", math.isfinite(logscore(ap, po)), True)
    check("anti log clipped", logscore(ap, po), -math.log(0.001))
    # base rate degenerate
    check("degenerate bss", bss([0.5, 0.5], [1, 1]), None)
    # calibration bins: 1.0 lands in the last bin
    check("cal last bin n", calibration([1.0, 0.0], [1, 0])[4][1], 1)
    # classification
    rows = [
        {"id": "a", "probability": 0.7, "verdict": "CONFIRMED"},
        {"id": "b", "prior": 0.4, "verdict": "FALSIFIED"},
        {"id": "c", "probability": 0.5, "verdict": "INCONCLUSIVE"},
        {"id": "d", "probability": 0.5, "resolve_by": "2026-01-01"},
        {"id": "e", "probability": 0.5, "resolve_by": "2099-01-01"},
        {"id": "f", "verdict": "FALSIFIED", "confidence": "high"},
        {"id": "g", "probability": True, "verdict": "CONFIRMED"},
        {"id": "h", "probability": 1.5, "verdict": "CONFIRMED"},
        {"id": "i", "probability": "0.5", "prior": "x", "verdict": "CONFIRMED"},
        {"id": "j", "probability": 0.9, "prior": 0.1, "verdict": "CONFIRMED"},
    ]
    sc, un, us = classify(rows, date(2026, 10, 17))
    check("scored ids", [x["id"] for x in sc], ["a", "b", "j"])
    check("scored src", [x["src"] for x in sc], ["new", "legacy", "new"])
    check("scored p for j prefers probability", sc[2]["p"], 0.9)
    check("unresolved ids", [x["id"] for x in un], ["c", "d", "e"])
    check("overdue flags", [x["overdue"] for x in un], [False, True, False])
    check("unscoreable ids", [x["id"] for x in us], ["f", "g", "h", "i"])
    check("nothing dropped", len(sc) + len(un) + len(us), len(rows))
    # insufficiency wording and determinism
    out1 = report(rows, date(2026, 10, 17))
    check("insufficient text", "insufficient (n=2)" in out1 and "insufficient (n=1)" in out1, True)
    check("legacy label", LEGACY_LABEL in out1, True)
    check("deterministic", report(rows, date(2026, 10, 17)), out1)
    big = [{"id": str(i), "probability": 0.8 if i % 2 else 0.2, "verdict": "CONFIRMED" if i % 2 else "FALSIFIED"}
           for i in range(40)]
    b1, b2 = report(big, date(2026, 10, 17)), report(big, date(2026, 10, 17))
    check("bootstrap deterministic", b1, b2)
    check("n>=30 reports bss", "BSS vs base-rate forecast: 0.8400" in b1, True)
    check("n>=30 reports interval", "95% bootstrap interval for BSS (10000 resamples" in b1, True)
    for f in fails:
        print("FAIL", f)
    print("self-test:", "FAIL" if fails else "OK")
    return 1 if fails else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ledger", default=str(DEFAULT_LEDGER))
    ap.add_argument("--today", default=None, help="YYYY-MM-DD for the resolve_by check (default: today)")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    today = date.fromisoformat(a.today) if a.today else date.today()
    rows, bad = load(a.ledger)
    sys.stdout.write(report(rows, today, bad))
    return 0


if __name__ == "__main__":
    sys.exit(main())
