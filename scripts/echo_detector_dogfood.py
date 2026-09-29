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

# ── HELD-OUT BENCH ──────────────────────────────────────────────────────────────
# Added by the F34 seaworthiness rebuild (2026-09-26) and reported SEPARATELY from
# the canonical 12 above (which are left byte-identical for a like-for-like F34
# comparison). These are NEW domains/wording the concept library was NOT tuned
# against — the generalization check. The critical case is `ho_adv_single_concept`:
# both sides genuinely share ONE real concept ("locks in"), so it probes the
# MIN_SHARED_CONCEPTS>=2 rule directly — a single coincident structural feature must
# still be rejected, or the fix is just a narrower keyword filter.
HOLDOUT_BENCH = [
    # ---- HELD-OUT POSITIVES (genuine isomorphisms, unseen wording) ----
    dict(id="ho_pos_autocatalytic", expect=True, pattern="autocatalytic_loop",
         a=("bacterial_culture", "Each division yields two cells that themselves divide; the "
            "output becomes input and the population compounds toward exponential growth, a "
            "self-reinforcing rise."),
         b=("open_source_adoption", "Every new contributor recruits more contributors; output "
            "becomes input, a positive feedback that compounds into exponential growth.")),
    dict(id="ho_pos_ratchet", expect=True, pattern="ratchet_irreversibility",
         a=("getting_a_tattoo", "Once inked it locks in; the choice is one-way and effectively "
            "irreversible, you cannot undo it."),
         b=("constitutional_amendment", "A ratified amendment locks in; repeal is a one-way "
            "cost, path dependent with no return.")),
    dict(id="ho_pos_threshold", expect=True, pattern="threshold_cascade",
         a=("forest_fire", "Below critical mass nothing spreads; past a threshold one spark "
            "sets off a chain reaction and the fire cascades."),
         b=("online_pileon", "A single quote past the tipping point triggers contagion; the "
            "cascade is a chain reaction of outrage.")),
    # ---- HELD-OUT NEGATIVES ----
    # Shares EXACTLY ONE real concept (locks_in) and nothing else -> must be rejected
    # (an isomorphism is a shared multi-feature structure, not one coincident feature).
    dict(id="ho_adv_single_concept", expect=False, adversarial=True,
         a=("door_deadbolt", "Turn the deadbolt and it locks in place; the door is secure."),
         b=("salary_offer", "Once you accept, the number locks in for the year.")),
    # Lone generic-word collisions in fresh wording (the F34 failure class, unseen).
    dict(id="ho_adv_generic_words", expect=False, adversarial=True,
         a=("plating_a_dish", "The sauce spreads across the plate in a gradient of flavor."),
         b=("traffic_report", "Cars spread out; the gradient of the on-ramp eases.")),
    # Clean unrelated pair, no dynamics on either side.
    dict(id="ho_neg_clean", expect=False,
         a=("dentist_visit", "The hygienist cleaned my teeth and booked a follow-up in six months."),
         b=("library_return", "I returned three books and paid a small late fee at the desk.")),
]


def evaluate(min_sim: float, bench: list = BENCH):
    det = OrthogonalEchoDetector(min_similarity=min_sim)
    rows, tp = [], 0
    fp = fn = tn = 0
    adv_fp = adv_total = 0
    for c in bench:
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
    P = len([c for c in bench if c["expect"]])
    N = len([c for c in bench if not c["expect"]])
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


# The pre-registered kill-condition for F34 (seaworthiness of RC-OPS-001).
TARGET_ADV_FP_MAX = 0.10
TARGET_RECALL_MIN = 0.80
GATE_MIN_SIM      = 0.35   # the detector's shipped operating default


def _print_rows(r, label):
    print(f"[{label}] min_sim={r['min_sim']}  P={r['precision']}  R={r['recall']}  "
          f"F1={r['f1']}  adv_fp_rate={r['adversarial_fp_rate']} "
          f"({r['adversarial_fp']}/{r['adversarial_total']})")
    for row in r["rows"]:
        flag = "OK " if row["correct"] else "XX "
        print(f"  {flag}{row['id']:24s} matched={row['matched']!s:5s} "
              f"top={row['top_pattern']} sim={row['top_sim']}")


def _meets_target(r) -> bool:
    return r["adversarial_fp_rate"] <= TARGET_ADV_FP_MAX and r["recall"] >= TARGET_RECALL_MIN


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-sim", type=float, default=0.20)
    ap.add_argument("--sweep", action="store_true", help="sweep thresholds 0.10..0.60")
    ap.add_argument("--emit", default=None, help="write JSON receipt to this path")
    ap.add_argument("--gate", action="store_true",
                    help=f"exit 1 unless BENCH and HOLDOUT both meet the F34 target "
                         f"(adv-FP<={TARGET_ADV_FP_MAX} @ recall>={TARGET_RECALL_MIN}) at "
                         f"min_sim={GATE_MIN_SIM}")
    args = ap.parse_args()

    # Always also measure the held-out bench, reported separately (never merged
    # into the canonical 12 — they stay F34-comparable).
    holdout = evaluate(GATE_MIN_SIM, bench=HOLDOUT_BENCH)

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
        out = dict(kind="echo-detector-dogfood-sweep", sweep=sweep, best=best, holdout=holdout)
    else:
        result = evaluate(args.min_sim)
        out = dict(kind="echo-detector-dogfood", result=result, holdout=holdout)
        _print_rows(result, "BENCH")

    print()
    _print_rows(holdout, "HOLDOUT")

    if args.emit:
        with open(args.emit, "w") as f:
            json.dump(out, f, indent=2)
        print(f"\nreceipt -> {args.emit}")

    if args.gate:
        bench_at_gate = evaluate(GATE_MIN_SIM)
        ok = _meets_target(bench_at_gate) and _meets_target(holdout)
        print(f"\nGATE @ min_sim={GATE_MIN_SIM}: "
              f"BENCH(adv_fp={bench_at_gate['adversarial_fp_rate']} R={bench_at_gate['recall']}) "
              f"HOLDOUT(adv_fp={holdout['adversarial_fp_rate']} R={holdout['recall']}) "
              f"-> {'PASS' if ok else 'FAIL'} "
              f"(target adv-FP<={TARGET_ADV_FP_MAX} @ recall>={TARGET_RECALL_MIN})")
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
