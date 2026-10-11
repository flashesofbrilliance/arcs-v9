#!/usr/bin/env python3
"""Monte Carlo pre-mortem for the monday.com take-home. Stdlib only. Deterministic (seeded).

HONESTY: the priors below are SUBJECTIVE estimates from the blind pre-mortem, not measured data.
The output is a structured way to expose assumptions and rank pre-work, NOT a prediction.
Edit the table, rerun, and compare. Nothing here touches the real assignment.

Model
- Anterior (prior): each failure mode (FM) has a probability of occurring, scaled by latent factors
  (time pressure T, brief difficulty B) and a rejection-given-occurrence probability scaled by
  reviewer strictness S.
- Posterior: evidence events (brief read, rehearsal done, dry run, gates passed) multiply specific
  FM probabilities down; we report the readiness curve as evidence accumulates.
- Blue team: choose mitigations under an hours budget (greedy by marginal gain per hour, common random numbers).
- Red team: stress each FM (x1.8) and each pair to find the plan's weakest joint.
- Inverse reasoning: start from a target P(pass) and report the cheapest mitigation set that reaches it.
- Dual bar raiser: two audience bars (A customer-outcome, B builder-defense) must both clear, plus a KILL bar
  (pathogen / hardening / kintsugi failures). Pass = no kill event AND bar A AND bar B clear.
"""
import random, json, sys

L = {"High": 0.35, "Medium": 0.20, "Low": 0.08}
R = {"VeryHigh": 0.85, "High": 0.60, "Medium": 0.30}
# id, name, likelihood, rejection-if-occurs, bar, hours-to-mitigate, mitigation effectiveness, latent drivers
FMS = [
 (1, "wrong question / sprawl", "High", "High", "A", 3.0, 0.60, ("B", "T")),
 (2, "engineering demo, not customer outcome", "High", "High", "A", 2.0, 0.65, ("B",)),
 (3, "cannot defend own work in walkthrough", "Medium", "VeryHigh", "B", 4.0, 0.60, ("T",)),
 (4, "monday platform fluency gap", "Medium", "High", "B", 4.0, 0.50, ("B",)),
 (5, "unsupported or inconsistent claims (pathogen)", "Medium", "High", "K", 2.0, 0.70, ("T",)),
 (6, "one-time-link process failure (hardening)", "Medium", "VeryHigh", "K", 1.5, 0.75, ("T",)),
 (7, "ARCS wrapper reads off-brief or thirsty", "Medium", "Medium", "A", 1.0, 0.50, ()),
 (8, "IP / confidentiality slip (pathogen)", "Low", "High", "K", 0.5, 0.70, ()),
 (9, "overpromised local-model claim", "Medium", "Medium", "B", 1.5, 0.60, ()),
 (10, "ambiguity handled silently", "Medium", "Medium", "A", 1.0, 0.50, ("B",)),
 (11, "fatigue / rushed last third", "Medium", "Medium", "B", 2.0, 0.50, ("T",)),
 (12, "governance mismatch (missing or overdone)", "Low", "Medium", "A", 1.0, 0.40, ("B",)),
 (13, "silent repair, no kintsugi record", "Medium", "High", "K", 0.5, 0.80, ()),
]
# evidence events (posterior updates): event -> {fm_id: multiplier}
EVENTS = [
 ("E1 brief read, rubric reconciled", {1: .7, 2: .7, 10: .6, 12: .6, 7: .8}),
 ("E2 walkthrough rehearsed aloud", {3: .6, 9: .7, 11: .9}),
 ("E3 packaging + environment dry run passed", {6: .5, 11: .9}),
 ("E4 provenance / consistency / slop gates passed", {5: .5, 8: .6, 13: .6}),
 ("E5 independent bar-raiser CONDITIONAL CLEAR", {1: .8, 2: .8, 3: .8, 5: .7, 7: .7}),
]

def clip(x): return max(0.0, min(0.99, x))

def simulate(mitigated, mult, n, seed):
    rng = random.Random(seed)
    ok = a_fail = b_fail = k_fail = 0
    for _ in range(n):
        T = rng.betavariate(2, 3); Bd = rng.betavariate(2, 2); S = rng.betavariate(2, 2)
        fa = fb = fk = False
        for (i, nm, lk, rj, bar, hrs, eff, drv) in FMS:
            p = L[lk] * mult.get(i, 1.0)
            if "T" in drv: p *= (0.6 + 0.8 * T)
            if "B" in drv: p *= (0.7 + 0.6 * Bd)
            if i in mitigated: p *= (1 - eff)
            if rng.random() < clip(p):
                if rng.random() < clip(R[rj] * (0.8 + 0.4 * S)):
                    if bar == "A": fa = True
                    elif bar == "B": fb = True
                    else: fk = True
        a_fail += fa; b_fail += fb; k_fail += fk
        ok += not (fa or fb or fk)
    return ok / n, a_fail / n, b_fail / n, k_fail / n

def greedy(budget, mult, n=12000, seed=7):
    chosen, spent, curve = set(), 0.0, []
    base = simulate(chosen, mult, n, seed)[0]
    while True:
        best = None
        for fm in FMS:
            i, hrs = fm[0], fm[5]
            if i in chosen or spent + hrs > budget: continue
            gain = simulate(chosen | {i}, mult, n, seed)[0] - base
            if best is None or gain / hrs > best[0]: best = (gain / hrs, i, gain, hrs)
        if not best or best[2] <= 0: break
        _, i, gain, hrs = best
        chosen.add(i); spent += hrs; base += gain; curve.append((i, round(gain, 4), hrs, round(base, 4)))
    return chosen, spent, curve

def main():
    N = 40000; BUDGET = 16.0
    name = {fm[0]: fm[1] for fm in FMS}
    out = []
    p0 = simulate(set(), {}, N, 1)
    out.append("## Anterior (prior), no pre-work\nP(pass all bars) = %.3f | A fail %.3f | B fail %.3f | KILL fail %.3f" % p0)
    chosen, spent, curve = greedy(BUDGET, {})
    p1 = simulate(chosen, {}, N, 1)
    out.append("\n## Blue team plan (budget %.0f h): mitigations in order of value per hour" % BUDGET)
    for (i, gain, hrs, cum) in curve: out.append("- FM%d %s: +%.3f for %.1f h (cumulative %.3f)" % (i, name[i], gain, hrs, cum))
    out.append("Spent %.1f h. P(pass) = %.3f | A %.3f | B %.3f | KILL %.3f" % ((spent,) + p1))
    out.append("\n## Posterior readiness curve (plan applied, evidence accumulates)")
    mult = {}
    out.append("- start: %.3f" % simulate(chosen, mult, N, 1)[0])
    for ev, eff in EVENTS:
        for k, v in eff.items(): mult[k] = mult.get(k, 1.0) * v
        out.append("- after %s: %.3f" % (ev, simulate(chosen, dict(mult), N, 1)[0]))
    final_mult = dict(mult)
    out.append("\n## Red team: single-FM stress (x1.8) against the blue plan")
    base = simulate(chosen, {}, 20000, 3)[0]; rows = []
    for fm in FMS:
        m = {fm[0]: 1.8}; rows.append((simulate(chosen, m, 20000, 3)[0] - base, fm[0]))
    for d, i in sorted(rows)[:5]: out.append("- FM%d %s: P(pass) %+.3f" % (i, name[i], d))
    worst = None
    for a in range(len(FMS)):
        for b in range(a + 1, len(FMS)):
            m = {FMS[a][0]: 1.8, FMS[b][0]: 1.8}; v = simulate(chosen, m, 5000, 5)[0]
            if worst is None or v < worst[0]: worst = (v, FMS[a][0], FMS[b][0])
    out.append("Worst pair: FM%d + FM%d -> P(pass) %.3f" % (worst[1], worst[2], worst[0]))
    out.append("\n## Inverse reasoning: cheapest path to a target P(pass) (mitigations only, then with evidence events)")
    path_chosen, path_spent, path_curve = greedy(24.0, {}, n=8000, seed=11)
    cum, picked, targets = 0.0, set(), [0.45, 0.55, 0.65]
    hit = {}
    for (i, gain, hrs, _) in path_curve:
        cum += hrs; picked.add(i)
        pv = simulate(picked, {}, 40000, 2)[0]
        for t in targets:
            if t not in hit and pv >= t: hit[t] = (cum, sorted(picked), pv)
    for t in targets:
        if t in hit: out.append("- target %.2f: reached at %.1f h of mitigation (P=%.3f) with FMs %s" % (t, hit[t][0], hit[t][2], hit[t][1]))
        else:
            pe = simulate(path_chosen, dict(final_mult), 40000, 2)[0]
            out.append("- target %.2f: NOT reached by mitigations alone within 24 h (max %.3f); with all evidence events: %.3f" % (t, simulate(path_chosen, {}, 40000, 2)[0], pe))
    out.append("\n## Pathogen and kill-bar view (KILL fail rate by mitigation)")
    out.append("No mitigation %.3f -> plan %.3f -> plan + all evidence events %.3f" % (p0[3], p1[3], simulate(chosen, final_mult, N, 1)[3]))
    print("\n".join(out))

if __name__ == "__main__": main()
