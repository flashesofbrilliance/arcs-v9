#!/usr/bin/env python3
"""decision_receipt_to_accountant: bridge outcomes on Zach's decision receipts into the Accountant. Read-only, stdlib.

Why (proposal _PROPOSALS/2026-10-20-shared-intention-before-snap.md, section 4k): ex-ante receipts live in
`decision_receipt`, their outcomes in _STATE/receipt-outcomes.jsonl (scripts/receipt_outcome_queue.py), and the
Accountant read only the compass `Receipt` table, where 0 rows are tagged real. Outcomes on real decisions never
reached calibration. This adapter emits Accountant-shaped rows in one cohort, `decisions`.

Rules (pre-registered 2026-10-20):
  1 Scope = receipt_outcome_queue's default scope (stakes high or critical, or mode COURT, with open lines).
  2 A receipt is CLOSED when every open line has a latest verdict other than `open`.
  3 Dropped lines are excluded. A closed receipt whose lines are all dropped is MOOT, not an outcome.
  4 It SCORES only if every non-dropped line was adjudicated `external`. Any `self` verdict on it: SELF-CLOSED,
    reported and never scored (the ledger's own rule; effort-policy evidence grade).
  5 matched = no non-dropped line is `reeled`.
  6 No NCI and no regret exist on decision receipts: both stay blank, so the cohort reports closure and hit rate
    by stakes and horizon and never claims an NCI calibration.
Reuses receipt_outcome_queue.load_receipts / load_ledger / in_scope; the export comes from
`python3 scripts/universe_receipts_adapter.py --export` (gitignored).

  python3 scripts/decision_receipt_to_accountant.py            # summary of the decisions cohort
  python3 scripts/decision_receipt_to_accountant.py --json     # Accountant report as JSON
  python3 scripts/decision_receipt_to_accountant.py --self-test
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path[:0] = [HERE, os.path.join(REPO, "operators")]
import receipt_outcome_queue as roq  # noqa: E402

COHORT = "decisions"


def adapt(receipts, ledger):
    """Returns {receipts, outcomes, counts} with Accountant-shaped rows."""
    rows, outcomes = [], []
    counts = {"in_scope": 0, "open": 0, "closed_scored": 0, "self_closed": 0, "moot": 0}
    hit = {}
    for rid, r in sorted(receipts.items()):
        if not roq.in_scope(r):
            continue
        counts["in_scope"] += 1
        rows.append({"receipt_id": rid, "cohort": COHORT, "nci_score": None, "horizon": r.get("horizon"),
                     "stakes": r.get("stakes"), "mode": r.get("mode"), "drift_state": None})
        verdicts = [ledger.get((rid, i)) for i in range(len(r["what_unconfirmed"]))]
        if any(v is None or v["verdict"] == "open" for v in verdicts):
            counts["open"] += 1
            continue
        live = [v for v in verdicts if v["verdict"] != "dropped"]
        if not live:
            counts["moot"] += 1
            continue
        if any(v["by"] != "external" for v in live):
            counts["self_closed"] += 1
            continue
        matched = not any(v["verdict"] == "reeled" for v in live)
        counts["closed_scored"] += 1
        outcomes.append({"receipt_id": rid, "matched": matched, "regret_score": None})
        key = (r.get("stakes"), r.get("horizon"))
        h = hit.setdefault(key, [0, 0])
        h[0] += int(matched)
        h[1] += 1
    counts["hit_by_stakes_horizon"] = {f"{s}/{hz}": f"{a}/{b}" for (s, hz), (a, b) in sorted(hit.items(), key=str)}
    return {"receipts": rows, "outcomes": outcomes, "counts": counts}


def report(receipts, ledger):
    from arcs_accountant import AccountantOperator
    a = adapt(receipts, ledger)
    rep = AccountantOperator().run(receipts=a["receipts"], outcomes=a["outcomes"])
    rep["bridge"] = a["counts"]
    return rep


def summary(rep):
    c = rep["bridge"]
    co = rep["cohorts"].get(COHORT, {})
    cal = co.get("calibration", {})
    return (f"  {COHORT:9} receipts={c['in_scope']:4} closed={c['closed_scored']:3} closure={co.get('closure_rate')} "
            f"calibration={cal.get('sufficiency')} (n={cal.get('n')}/{cal.get('threshold')}; no NCI on decision receipts)\n"
            f"            still open={c['open']} self-closed (not scored)={c['self_closed']} moot={c['moot']} "
            f"hit by stakes/horizon={c['hit_by_stakes_horizon'] or 'none'}")


def self_test():
    R = {
        "ext-held--ZH": {"stakes": "high", "mode": "PLAN", "horizon": "this-week", "what_unconfirmed": ["a", "b"]},
        "ext-reeled--ZH": {"stakes": "high", "mode": "PLAN", "horizon": "this-week", "what_unconfirmed": ["a"]},
        "self--ZH": {"stakes": "critical", "mode": "PLAN", "horizon": "today", "what_unconfirmed": ["a"]},
        "mixed--ZH": {"stakes": "high", "mode": "PLAN", "horizon": "today", "what_unconfirmed": ["a", "b"]},
        "half--ZH": {"stakes": "high", "mode": "PLAN", "horizon": "today", "what_unconfirmed": ["a", "b"]},
        "moot--ZH": {"stakes": "high", "mode": "COURT", "horizon": "today", "what_unconfirmed": ["a"]},
        "low--ZH": {"stakes": "low", "mode": "QUICKMOVE", "horizon": "today", "what_unconfirmed": ["a"]},
    }
    E = lambda v: {"verdict": v, "by": "external"}  # noqa: E731
    S = lambda v: {"verdict": v, "by": "self"}  # noqa: E731
    L = {("ext-held--ZH", 0): E("held"), ("ext-held--ZH", 1): S("dropped"),
         ("ext-reeled--ZH", 0): E("reeled"), ("self--ZH", 0): S("held"),
         ("mixed--ZH", 0): E("held"), ("mixed--ZH", 1): S("held"),
         ("half--ZH", 0): E("held"), ("moot--ZH", 0): S("dropped"), ("low--ZH", 0): E("held")}
    a = adapt(R, L)
    c = a["counts"]
    out = {o["receipt_id"]: o["matched"] for o in a["outcomes"]}
    checks = [
        ("low stakes is out of scope", c["in_scope"] == 6),
        ("external held with a dropped line scores as matched", out.get("ext-held--ZH") is True),
        ("external reeled scores as unmatched", out.get("ext-reeled--ZH") is False),
        ("any self verdict keeps a receipt unscored", "self--ZH" not in out and "mixed--ZH" not in out and c["self_closed"] == 2),
        ("a missing line verdict keeps it open", "half--ZH" not in out and c["open"] == 1),
        ("all dropped is moot, not an outcome", c["moot"] == 1 and "moot--ZH" not in out),
        ("only two receipts score", c["closed_scored"] == 2),
        ("hit rate by stakes/horizon", c["hit_by_stakes_horizon"] == {"high/this-week": "1/2"}),
    ]
    try:
        rep = report(R, L)
        checks.append(("Accountant accepts the cohort and blank NCI/regret",
                       rep["cohorts"]["decisions"]["outcomes_logged"] == 2 and rep["cohorts"]["decisions"]["receipts"] == 6))
    except Exception as e:  # noqa: BLE001
        checks.append((f"Accountant run raised {e!r}", False))
    bad = [n for n, ok in checks if not ok]
    for n in bad:
        print(f"FAIL {n}", file=sys.stderr)
    print(f"decision_receipt_to_accountant self-test: {len(checks) - len(bad)}/{len(checks)} passed")
    return 1 if bad else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="Bridge decision-receipt outcomes into the Accountant (read-only).")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    rep = report(roq.load_receipts(), roq.load_ledger())
    print(json.dumps(rep, indent=1, default=str) if a.json else summary(rep))
    return 0


if __name__ == "__main__":
    sys.exit(main())
