#!/usr/bin/env python3
"""
echo_detector_dogfood.py — falsifiable seaworthiness test for the Orthogonal Echo
Detector (RC-OPS-001, operators/arcs_inchworm_echo.py).

WHY THIS EXISTS
---------------
The detector's graduation gate is *blind precision*, not corpus size (see memory
`rom-graduation-earn-through-gate-never-decree`). Blind field echoes accrue slowly
(count ~1). This harness produces the OTHER half of the evidence the gate needs and
can produce NOW, deterministically: the detector's precision/recall on a LABELED
benchmark, including the known adversarial failure mode (weak generic keyword
collisions that are NOT genuine kinematic isomorphisms).

It does not replace the blind-field-echo count. It answers a narrower, mechanically
scorable question: given pairs where we KNOW the ground truth, does the detector flag
the real isomorphisms and reject the fakes — and at what threshold does it stop being
fooled? That is what "seaworthy" means for the instrument itself.

THE OPERATIONAL TRIGGER EVENT (spec, emitted with the receipt)
--------------------------------------------------------------
In normal operation the detector should fire on NEW-ARTIFACT INGEST, compared against
the prior-session corpus, logging cross-domain candidates with source-independence
metadata (same_session / same_domain / same_author_intent) for later HINDSIGHT grading.
Only candidates whose two sides are source-independent (different session, different
domain) count toward the blind gate. This harness is the *bench* version of that
trigger: ground truth is known up front instead of graded in hindsight.

Run:  python3 scripts/echo_detector_dogfood.py [--min-sim 0.20] [--sweep]
Exit: 0 always (it is a measurement, not a gate that blocks). Emits a JSON receipt.
"""
import sys, os, json, argparse, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REPO, "operators"))

from arcs_inchworm_echo import OrthogonalEchoDetector  # noqa: E402

# ── LABELED BENCHMARK ─────────────────────────────────────────────────────────
# Each case: two domain-texts + ground truth. expect=True means a genuine
# cross-domain kinematic isomorphism SHOULD be flagged (optionally on `pattern`).
# expect=False means NO real isomorphism; the detector should stay quiet.
# `adversarial=True` marks negatives engineered to trip weak generic keywords
# (the documented False==False / keyword-collision failure class).

BENCH = [
    # ---- POSITIVES (genuine isomorphisms) ----
    dict(id="pos_autocatalytic", expect=True, pattern="autocatalytic_loop",
         a=("compound_interest", "Money reinvested compounds; each period's output "
            "becomes next period's input, driving exponential growth. Self-reinforcing, "
            "amplifying, a positive feedback loop."),
         b=("viral_content", "A share triggers more shares; the output becomes input, "
            "compounding into exponential growth. Self-reinforcing and amplifying via "
            "positive feedback.")),
    dict(id="pos_immune_memory", expect=True, pattern="adaptive_immune_memory",
         a=("vaccination", "The first encounter is costly; the second is cheap. The body "
            "learns from exposure, memory improves response, acquired resistance builds."),
         b=("relationship_trust", "First betrayal is costly, later recovery cheaper as "
            "trust erodes then rebuilding learns from exposure; recovery is memory of the "
            "encounter.")),
    dict(id="pos_ratchet", expect=True, pattern="ratchet_irreversibility",
         a=("career_specialization", "Deep specialization locks in; it is path dependent, "
            "one-way, with no rollback once you commit."),
         b=("schema_migration", "A destructive migration is irreversible; you cannot undo "
            "it, it locks in, there is no return.")),
    dict(id="pos_threshold", expect=True, pattern="threshold_cascade",
         a=("snow_avalanche", "Near critical mass a tiny input past the tipping point sets "
            "off a chain reaction; the avalanche happens suddenly."),
         b=("bank_run", "Past a threshold, contagion cascades; a small trigger causes "
            "collapse suddenly as the panic spreads.")),
    dict(id="pos_punctuated", expect=True, pattern="punctuated_equilibrium",
         a=("evolution", "Long stasis, then a sudden shift; stable until disrupted, then a "
            "rapid change as populations speciate."),
         b=("startup_growth", "A long plateau then a leap; a phase transition, rapid change "
            "after stasis.")),
    # ---- CLEAN NEGATIVES (no shared dynamic, no pattern keywords) ----
    dict(id="neg_mundane", expect=False,
         a=("grocery_list", "Buy milk, eggs, bread, apples, and coffee at the store today."),
         b=("weather_note", "It is mild and clear this afternoon with a light breeze.")),
    dict(id="neg_procedural", expect=False,
         a=("bread_recipe", "Mix flour and water, knead the dough, let it rest, then bake."),
         b=("furniture_assembly", "Attach the legs to the tabletop with the provided screws "
            "and tighten each corner.")),
    dict(id="neg_disjoint_dynamics", expect=False,
         a=("compound_interest2", "Reinvested money compounds into exponential growth, a "
            "self-reinforcing amplifying loop."),
         b=("bread_recipe2", "Knead the dough and let it rest before baking at high heat.")),
    # ---- ADVERSARIAL NEGATIVES (weak generic keyword collisions; must NOT match) ----
    dict(id="adv_trust_collision", expect=False, adversarial=True,
         a=("wine_review", "I trust this vintage; the recovery of the cork was clean."),
         b=("backup_restore", "We restore from a trusted source; recovery completed.")),
    dict(id="adv_stability_shock", expect=False, adversarial=True,
         a=("yoga_class", "Find stability in the pose; absorb the shock through your legs."),
         b=("suspension_bridge", "The design has stability; it must absorb a shock load.")),
    dict(id="adv_gradient_generic", expect=False, adversarial=True,
         a=("art_critique", "The gradient of color spreads across the canvas."),
         b=("hiking_trail", "The gradient of the slope; the crowd spreads out along it.")),
    dict(id="adv_collapse_generic", expect=False, adversarial=True,
         a=("tired_evening", "I collapse onto the couch; a sudden wave of sleep."),
         b=("tent_teardown", "The poles collapse; suddenly the tent folds flat.")),
]


def evaluate(min_sim: float):
    det = OrthogonalEchoDetector(min_similarity=min_sim)
    rows, tp = [], 0
    fp = fn = tn = 0
    adv_fp = adv_total = 0
    for c in BENCH:
        rec = det.run({c["a"][0]: c["a"][1], c["b"][0]: c["b"][1]})
        matched = len(rec.matches) > 0
        top = rec.matches[0].pattern_name if rec.matches else None
        top_sim = rec.matches[0].similarity if rec.matches else 0.0
        # correctness: for positives, matched AND (pattern right if specified)
        if c["expect"]:
            pat_ok = (c.get("pattern") is None) or any(
                m.pattern_name == c["pattern"] for m in rec.matches)
            correct = matched and pat_ok
            tp += int(correct); fn += int(not correct)
        else:
            correct = not matched
            tn += int(correct); fp += int(not correct)
            if c.get("adversarial"):
                adv_total += 1; adv_fp += int(matched)
        rows.append(dict(id=c["id"], expect=c["expect"], adversarial=c.get("adversarial", False),
                         matched=matched, top_pattern=top, top_sim=round(top_sim, 3),
                         expected_pattern=c.get("pattern"), correct=correct))
    P = len([c for c in BENCH if c["expect"]])
    N = len([c for c in BENCH if not c["expect"]])
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall    = tp / (tp + fn) if (tp + fn) else 0.0
    f1        = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    return dict(
        min_sim=min_sim, positives=P, negatives=N,
        tp=tp, fp=fp, fn=fn, tn=tn,
        precision=round(precision, 3), recall=round(recall, 3), f1=round(f1, 3),
        adversarial_fp=adv_fp, adversarial_total=adv_total,
        adversarial_fp_rate=round(adv_fp / adv_total, 3) if adv_total else 0.0,
        rows=rows,
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-sim", type=float, default=0.20)
    ap.add_argument("--sweep", action="store_true", help="sweep thresholds 0.10..0.60")
    ap.add_argument("--emit", default=None, help="write JSON receipt to this path")
    args = ap.parse_args()

    if args.sweep:
        sweep = [evaluate(round(s, 2)) for s in [0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50, 0.60]]
        print("min_sim  precision  recall  f1    adv_fp_rate")
        for r in sweep:
            print(f"  {r['min_sim']:.2f}      {r['precision']:.2f}     "
                  f"{r['recall']:.2f}   {r['f1']:.2f}    {r['adversarial_fp_rate']:.2f}")
        best = max(sweep, key=lambda r: (r["f1"], -r["adversarial_fp_rate"]))
        print(f"\nbest-F1 threshold: min_sim={best['min_sim']} "
              f"(P={best['precision']} R={best['recall']} F1={best['f1']} "
              f"adv_fp_rate={best['adversarial_fp_rate']})")
        out = dict(kind="echo-detector-dogfood-sweep", sweep=sweep, best=best)
    else:
        out = dict(kind="echo-detector-dogfood", result=evaluate(args.min_sim))
        r = out["result"]
        print(f"min_sim={r['min_sim']}  P={r['precision']}  R={r['recall']}  F1={r['f1']}  "
              f"adv_fp_rate={r['adversarial_fp_rate']} ({r['adversarial_fp']}/{r['adversarial_total']})")
        for row in r["rows"]:
            flag = "OK " if row["correct"] else "XX "
            print(f"  {flag}{row['id']:24s} matched={row['matched']!s:5s} "
                  f"top={row['top_pattern']} sim={row['top_sim']}")

    if args.emit:
        with open(args.emit, "w") as f:
            json.dump(out, f, indent=2)
        print(f"\nreceipt -> {args.emit}")


if __name__ == "__main__":
    main()
