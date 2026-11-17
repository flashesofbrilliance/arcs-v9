#!/usr/bin/env python3
"""
mc.py - Monte Carlo for the Gravity page Call and Put (stdlib only).

Claim (gravity.json, overview "bull-bear" ledger):
  Call: 1 in 3 that a card network or issuer requires an intent record by 2027-06-30.
  Put:  if the rule is late, the loss is small: ARCS already writes the record for human decisions.

A simulation shows only what its assumptions imply. Every prior below is JUDGMENT unless a
source is named next to it; none of the ranges was fitted to data, and none was tuned to land
near 1/3 (the ranges were written before the first run).

Forward (anterior): sample parameters, then drivers, then the event. 30,000 runs.
Reverse (posterior): rejection-sample from the same model until 15,000 "happened" and 15,000
"did not happen" runs are held (30,000 total), then read which driver paths dominate each.

Three readings of "requires an intent record" (the claim does not pre-register one):
  network_only : Visa, Mastercard, Amex or Discover PUBLISHES a rule requiring it for agent-initiated payments
  as_written   : network_only OR a top-20 issuer requires it in its own program terms
  loose        : as_written OR an existing agent program (Mastercard Agent Pay, Visa Intelligent Commerce,
                 AP2 mandates inside a network program) is judged to already count
"""
import json, math, random, sys
from pathlib import Path

SEED = 20261110
N_FWD = 30_000
N_REV_EACH = 15_000
OUT = Path(__file__).with_name("mc_results.json")

# name: (low, high, basis). Uniform on [low, high].
PRIORS = {
    # Drivers (each: does it happen by 2027-06-30, about 7.6 months from 2026-11-10)
    "p_standard": (0.35, 0.70, "judgment: AP2 (Google, Sept 2025) or Verifiable Intent in production in at least one network program; announcements recalled, not re-verified this session"),
    "p_fraud":    (0.25, 0.55, "judgment: a widely reported agent-payment fraud or mandate-overrun incident"),
    "p_regulator":(0.05, 0.25, "judgment: US/EU/UK guidance that names an authorization or mandate record for agent payments; OCC stablecoin rule effective 2027-01-18 (occ.gov nr-2026-92) is about stablecoin issuers, not card intent records, so it does not count"),
    # Base hazards with no driver present
    "base_network": (0.04, 0.15, "judgment: networks publish rule changes on a release cadence; 7.6 months is one or two cycles"),
    "base_issuer":  (0.02, 0.08, "judgment: a top-20 issuer rarely sets its own rule ahead of its network"),
    # Multiplicative lifts when a driver is present
    "lift_standard_network": (1.5, 3.0, "judgment"),
    "lift_fraud":            (1.3, 2.5, "judgment: applies to network and issuer"),
    "lift_regulator":        (1.5, 3.0, "judgment: applies to network and issuer"),
    # Loose reading only
    "p_existing_counts": (0.30, 0.60, "judgment: chance a resolver counts an existing agent program as 'requires an intent record'"),
    # Put
    "build_weeks_lo":   (2.0, 2.0, "judgment: triangular(2, 4, 10) weeks to extend ARCS receipts into a signed, transaction-bound intent record"),
    "salvage":          (0.30, 0.70, "judgment: share of that work still useful if the rule is late (human-decision receipts, portfolio)"),
    "rep_weeks":        (0.0, 0.5, "judgment: reputation cost of a public miss, in week-equivalents; a calibrated 1-in-3 call that misses is the expected outcome"),
    "p_nonconform":     (0.50, 0.90, "judgment: chance the ARCS record does not meet the format a network names (AP2 / Verifiable Intent style signed mandate); repo check: decision_receipt is append-only by trigger but has no signature, mandate or transaction-binding field"),
    "rework_weeks_lo":  (1.0, 1.0, "judgment: triangular(1, 3, 6) weeks of rework if non-conforming"),
}
BUILD_TRI = (2.0, 4.0, 10.0)
REWORK_TRI = (1.0, 3.0, 6.0)
DRIVERS = ["p_standard", "p_fraud", "p_regulator", "base_network", "base_issuer",
           "lift_standard_network", "lift_fraud", "lift_regulator", "p_existing_counts"]


def u(r, k):
    lo, hi, _ = PRIORS[k]
    return lo if lo == hi else r.uniform(lo, hi)


def sample_params(r):
    return {k: u(r, k) for k in DRIVERS}


def cond_probs(p, S, F, R):
    lift_n = (p["lift_standard_network"] if S else 1) * (p["lift_fraud"] if F else 1) * (p["lift_regulator"] if R else 1)
    lift_i = (p["lift_fraud"] if F else 1) * (p["lift_regulator"] if R else 1)
    return min(0.95, p["base_network"] * lift_n), min(0.95, p["base_issuer"] * lift_i)


def analytic(p):
    """P(event | params) for each reading, summing over the 8 driver states."""
    out = {"network_only": 0.0, "as_written": 0.0, "loose": 0.0}
    for S in (0, 1):
        for F in (0, 1):
            for R in (0, 1):
                w = (p["p_standard"] if S else 1 - p["p_standard"]) * (p["p_fraud"] if F else 1 - p["p_fraud"]) * (p["p_regulator"] if R else 1 - p["p_regulator"])
                pn, pi = cond_probs(p, S, F, R)
                aw = 1 - (1 - pn) * (1 - pi)
                out["network_only"] += w * pn
                out["as_written"] += w * aw
                out["loose"] += w * (1 - (1 - aw) * (1 - p["p_existing_counts"]))
    return out


def draw_world(r, p):
    S, F, R = r.random() < p["p_standard"], r.random() < p["p_fraud"], r.random() < p["p_regulator"]
    pn, pi = cond_probs(p, S, F, R)
    N, I = r.random() < pn, r.random() < pi
    return {"S": S, "F": F, "R": R, "N": N, "I": I, "E": N or I}


def pct(xs, q):
    xs = sorted(xs)
    k = (len(xs) - 1) * q
    f, c = math.floor(k), math.ceil(k)
    return xs[f] if f == c else xs[f] + (xs[c] - xs[f]) * (k - f)


def summary(xs):
    return {"mean": round(sum(xs) / len(xs), 4), "p05": round(pct(xs, .05), 4), "p25": round(pct(xs, .25), 4),
            "p50": round(pct(xs, .5), 4), "p75": round(pct(xs, .75), 4), "p95": round(pct(xs, .95), 4),
            "share_ge_1in3": round(sum(x >= 1 / 3 for x in xs) / len(xs), 4)}


def tri(r, a, m, b):
    return r.triangular(a, b, m)


def main():
    r = random.Random(SEED)
    # ---- forward
    Ps = {"network_only": [], "as_written": [], "loose": []}
    realized = 0
    params_log = []
    for _ in range(N_FWD):
        p = sample_params(r)
        a = analytic(p)
        for k in Ps:
            Ps[k].append(a[k])
        params_log.append(p)
        realized += draw_world(r, p)["E"]
    fwd = {k: summary(v) for k, v in Ps.items()}
    fwd["as_written_realized_frequency"] = round(realized / N_FWD, 4)

    # ---- tornado: one prior at a time to its low/high end, others at midpoint (as_written reading)
    mid = {k: (PRIORS[k][0] + PRIORS[k][1]) / 2 for k in DRIVERS}
    base = analytic(mid)["as_written"]
    tornado = []
    for k in DRIVERS:
        if k == "p_existing_counts":
            continue
        lo, hi = dict(mid), dict(mid)
        lo[k], hi[k] = PRIORS[k][0], PRIORS[k][1]
        a, b = analytic(lo)["as_written"], analytic(hi)["as_written"]
        tornado.append({"prior": k, "at_low": round(a, 4), "at_high": round(b, 4), "swing": round(abs(b - a), 4)})
    tornado.sort(key=lambda t: -t["swing"])
    # rank correlation of each prior with P(as_written) across the forward runs
    def ranks(v):
        order = sorted(range(len(v)), key=lambda i: v[i]); rk = [0] * len(v)
        for j, i in enumerate(order): rk[i] = j
        return rk
    ry = ranks(Ps["as_written"]); n = len(ry)
    spearman = {}
    for k in DRIVERS:
        if k == "p_existing_counts":
            continue
        rx = ranks([pl[k] for pl in params_log])
        d2 = sum((a - b) ** 2 for a, b in zip(rx, ry))
        spearman[k] = round(1 - 6 * d2 / (n * (n * n - 1)), 3)
    reading_swing = {"network_only_mid": round(analytic(mid)["network_only"], 4), "as_written_mid": round(base, 4),
                     "loose_mid": round(analytic(mid)["loose"], 4)}

    # ---- reverse: condition on the outcome (as_written reading)
    hap, nothap, tries = [], [], 0
    while len(hap) < N_REV_EACH or len(nothap) < N_REV_EACH:
        tries += 1
        w = draw_world(r, sample_params(r))
        if w["E"] and len(hap) < N_REV_EACH:
            hap.append(w)
        elif not w["E"] and len(nothap) < N_REV_EACH:
            nothap.append(w)

    def path(w):
        return "+".join(n for n, on in (("standard", w["S"]), ("fraud", w["F"]), ("regulator", w["R"])) if on) or "no driver"

    def paths(ws):
        c = {}
        for w in ws:
            c[path(w)] = c.get(path(w), 0) + 1
        return {k: round(v / len(ws), 4) for k, v in sorted(c.items(), key=lambda kv: -kv[1])}

    def share(ws, key):
        return round(sum(w[key] for w in ws) / len(ws), 4)

    rev = {"accepted_happened": len(hap), "accepted_not": len(nothap), "draws_needed": tries,
           "happened": {"paths": paths(hap), "P(standard)": share(hap, "S"), "P(fraud)": share(hap, "F"),
                        "P(regulator)": share(hap, "R"), "fired_network": share(hap, "N"), "fired_issuer": share(hap, "I"),
                        "issuer_only": round(sum(w["I"] and not w["N"] for w in hap) / len(hap), 4)},
           "not_happened": {"paths": paths(nothap), "P(standard)": share(nothap, "S"), "P(fraud)": share(nothap, "F"),
                            "P(regulator)": share(nothap, "R")}}
    # likelihood ratio per driver: P(driver | happened) / P(driver | not)
    rev["likelihood_ratio"] = {d: round(rev["happened"][f"P({d})"] / max(1e-9, rev["not_happened"][f"P({d})"]), 3)
                               for d in ("standard", "fraud", "regulator")}

    # ---- Put: expected loss in week-equivalents
    late_loss, conform_loss, total = [], [], []
    for i in range(N_FWD):
        pE = Ps["as_written"][i]
        build = tri(r, *BUILD_TRI)
        salv = u(r, "salvage"); rep = u(r, "rep_weeks"); pnc = u(r, "p_nonconform"); rw = tri(r, *REWORK_TRI)
        a = (1 - pE) * (build * (1 - salv) + rep)
        b = pE * pnc * rw
        late_loss.append(a); conform_loss.append(b); total.append(a + b)
    put = {"units": "week-equivalents of Zach's time (judgment)",
           "EL_if_late_branch": summary(late_loss), "EL_win_branch_nonconformance": summary(conform_loss),
           "EL_total": summary(total),
           "share_of_EL_from_branch_the_Put_ignores": round(sum(conform_loss) / sum(total), 4)}

    res = {"seed": SEED, "n_forward": N_FWD, "n_reverse": 2 * N_REV_EACH,
           "priors": {k: {"low": v[0], "high": v[1], "basis": v[2]} for k, v in PRIORS.items()},
           "forward_P_event": fwd, "midpoint_by_reading": reading_swing,
           "tornado_as_written": tornado, "spearman_vs_P_as_written": spearman,
           "reverse": rev, "put": put,
           "caveat": "These numbers restate the judgment priors above through a fixed structure. They are not evidence about the world."}
    OUT.write_text(json.dumps(res, indent=1))
    json.dump(res, sys.stdout, indent=1)


if __name__ == "__main__":
    main()
