#!/usr/bin/env python3
"""receipt_efficacy_probe: plumbing proof for predictions -> closes -> Accountant scoring.

DRY-RUN ONLY, zero DB access. Takes an export of rows in the adapter shape (EXPORT_SQL, or a
fixture), picks a seeded random sample of rows tagged provenance="test", fabricates synthetic
outcomes for them (outcome_synthetic=true, same column shape the real Outcome path writes), and
checks the whole flow through the real adapter + Accountant:
  1. every sampled test receipt flips OPEN -> LOGGED inside the `test` cohort
  2. synthetic outcomes are excluded from every cohort (real/founder/external/anonymous unchanged)
  3. non-test receipts are never sampled or touched
Writing the same synthetic outcomes to a real DB goes through POST /api/receipts/[id]/outcome with
`synthetic: true` (route only accepts it on provenance="test"); cleanup is
`DELETE FROM "Outcome" WHERE synthetic = true`. That needs Zach's explicit yes against prod.

Usage: receipt_efficacy_probe.py EXPORT.json [--n 30] [--seed 7]    | --self-test
Stdlib only.
"""
from __future__ import annotations

import argparse
import copy
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "operators"))
from prod_receipt_to_accountant import adapt, load_rows  # noqa: E402
from arcs_accountant import AccountantOperator  # noqa: E402


def probe(rows: list, n: int = 30, seed: int = 7) -> dict:
    rnd = random.Random(seed)
    test_open = [r for r in rows if r.get("provenance") == "test" and r.get("outcome_id") is None]
    sample = rnd.sample(test_open, min(n, len(test_open)))
    ids = {r["id"] for r in sample}
    after = copy.deepcopy(rows)
    for r in after:
        if r["id"] in ids:
            m = rnd.random() < 0.5
            r.update(outcome_id=f"synthetic-{r['id']}", outcome_matched=m,
                     outcome_regret_score=rnd.randint(0, 10), outcome_logged_at="1970-01-01T00:00:00Z",
                     outcome_what_len=0, outcome_learning_len=0, outcome_synthetic=True)
    before_rep = AccountantOperator().run(**adapt(rows))
    p_after = adapt(after)
    rep = AccountantOperator().run(**p_after)
    checks = {}
    checks["sampled_only_test"] = all(r["provenance"] == "test" for r in sample)
    checks["synthetic_excluded_from_scoring"] = (p_after["synthetic_excluded"] == len(sample)
        and rep["totals"]["closed_by_cohort"] == before_rep["totals"]["closed_by_cohort"])
    checks["non_test_cohorts_unchanged"] = all(
        rep["cohorts"].get(c) == before_rep["cohorts"].get(c) for c in ("real", "founder", "external", "anonymous"))
    # flow check with synthetics INCLUDED (what the Accountant would see if they leaked): closes land in `test`
    leak = copy.deepcopy(after)
    for r in leak:
        r["outcome_synthetic"] = False
    leak_rep = AccountantOperator().run(**adapt(leak))
    checks["closes_flow_to_test_cohort"] = (
        leak_rep["totals"]["closed_by_cohort"].get("test", 0)
        == before_rep["totals"]["closed_by_cohort"].get("test", 0) + len(sample))
    return {"sampled": len(sample), "seed": seed, "checks": checks, "ok": all(checks.values()),
            "test_cohort_if_leaked": leak_rep["cohorts"].get("test", {}).get("calibration", {}).get("sufficiency")}


def _fixture() -> list:
    rows = []
    for i in range(60):
        rows.append({"id": f"t{i}", "userId": "u1", "provenance": "test", "nciScore": 40 + i % 50, "horizon": "WEEK"})
    for i in range(5):
        rows.append({"id": f"r{i}", "userId": "u1", "provenance": "real", "nciScore": 70, "horizon": "WEEK"})
    rows.append({"id": "x0", "userId": "u2", "nciScore": 55, "horizon": "WEEK"})
    rows.append({"id": "a0", "userId": None, "nciScore": 55, "horizon": "WEEK"})
    return rows


def main(argv: list) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("export", nargs="?")
    ap.add_argument("--n", type=int, default=30)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    rows = _fixture() if a.self_test else load_rows(a.export)
    res = probe(rows, a.n, a.seed)
    print(res)
    if a.self_test:
        assert res["ok"] and res["sampled"] == 30, res
        print("receipt_efficacy_probe self-test OK")
    return 0 if res["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
