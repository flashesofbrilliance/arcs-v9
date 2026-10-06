"""Unit tests for operators/arcs_accountant.py (Operator 19) and its prod adapter
operators/prod_receipt_to_accountant.py.

Covers the sufficiency gate at CALIBRATION_MIN_N, empty input, non-numeric nci_score,
unknown cohorts landing in `unattributed`, per-cohort counts and closure rate, and the
adapter's row mapping (cohort rule, horizon fallback, outcome join).

Run: python3 -m unittest discover -s operators/tests
Stdlib only.
"""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import arcs_accountant as acc  # noqa: E402
import prod_receipt_to_accountant as adapter  # noqa: E402


def _closed(n, cohort, nci=lambda i: 20 + (i * 7) % 70):
    """n receipts, all closed, alternating matched so both outcome classes exist."""
    receipts, outcomes = [], []
    for i in range(n):
        rid = f"{cohort}-{i}"
        receipts.append({"receipt_id": rid, "cohort": cohort, "nci_score": nci(i),
                         "horizon": "WEEK", "mode": "QUICKMOVE", "drift_state": "ON_TRACK"})
        outcomes.append({"receipt_id": rid, "matched": i % 2 == 0, "regret_score": i % 10})
    return receipts, outcomes


class TestSufficiency(unittest.TestCase):
    def setUp(self):
        self.op = acc.AccountantOperator()

    def test_threshold_is_30(self):
        self.assertEqual(acc.CALIBRATION_MIN_N, 30)

    def test_at_threshold_is_sufficient(self):
        rep = self.op.run(*_closed(acc.CALIBRATION_MIN_N, "external"))
        self.assertEqual(rep["sufficiency"], "sufficient")
        cal = rep["cohorts"]["external"]["calibration"]
        self.assertEqual(cal["sufficiency"], "sufficient")
        self.assertEqual(cal["n"], 30)
        self.assertIsNotNone(cal["spearman_nci_vs_regret"])

    def test_below_threshold_is_insufficient(self):
        rep = self.op.run(*_closed(acc.CALIBRATION_MIN_N - 1, "external"))
        self.assertEqual(rep["sufficiency"], "insufficient")
        cal = rep["cohorts"]["external"]["calibration"]
        self.assertEqual(cal["n"], 29)
        self.assertIsNone(cal["spearman_nci_vs_regret"])
        self.assertIsNone(cal["mean_nci_matched"])

    def test_threshold_is_per_cohort_not_pooled(self):
        r1, o1 = _closed(20, "founder")
        r2, o2 = _closed(20, "external")
        rep = self.op.run(r1 + r2, o1 + o2)
        self.assertEqual(rep["sufficiency"], "insufficient")

    def test_empty_input(self):
        for args in (([], []), (None, None)):
            rep = self.op.run(*args)
            self.assertEqual(rep["sufficiency"], "insufficient")
            self.assertEqual(rep["cohorts"], {})
            self.assertEqual(rep["totals"]["receipts"], 0)
            json.dumps(rep)

    def test_non_numeric_nci_does_not_crash(self):
        rep = self.op.run(*_closed(40, "external", nci=lambda i: "high"))
        ex = rep["cohorts"]["external"]
        self.assertEqual(rep["sufficiency"], "insufficient")
        self.assertEqual(ex["calibration"]["n"], 0)
        self.assertEqual(ex["missing_fields"]["nci_score"], 40)
        self.assertEqual(ex["nci_scored"], 0)
        self.assertIsNone(ex["mean_nci_all"])
        json.dumps(rep)

    def test_mixed_junk_nci_values(self):
        junk = [None, "70", True, float("nan"), {"x": 1}]
        receipts = [{"receipt_id": str(i), "cohort": "founder", "nci_score": v}
                    for i, v in enumerate(junk)]
        rep = self.op.run(receipts, [])
        fo = rep["cohorts"]["founder"]
        self.assertEqual(fo["missing_fields"]["nci_score"], len(junk))
        self.assertEqual(rep["sufficiency"], "insufficient")


class TestCohorts(unittest.TestCase):
    def test_unknown_cohort_is_unattributed(self):
        receipts = [{"receipt_id": "a", "cohort": "partner", "nci_score": 50},
                    {"receipt_id": "b", "cohort": "founder", "nci_score": 60},
                    {"receipt_id": "c", "nci_score": 70}]
        rep = acc.AccountantOperator().run(receipts, [])
        self.assertEqual(rep["cohorts"]["unattributed"]["receipts"], 2)
        self.assertEqual(rep["cohorts"]["founder"]["receipts"], 1)
        self.assertNotIn("partner", rep["cohorts"])
        self.assertNotIn("external", rep["cohorts"])
        self.assertNotIn("anonymous", rep["cohorts"])

    def test_counts_and_closure_rate(self):
        receipts = [
            {"receipt_id": "f1", "cohort": "founder", "nci_score": 80, "horizon": "WEEK",
             "mode": "PLAN", "drift_state": "LANDED"},
            {"receipt_id": "f2", "cohort": "founder", "nci_score": 40, "horizon": "TODAY",
             "mode": "PLAN", "drift_state": "DRIFTING"},
            {"receipt_id": "f3", "cohort": "founder", "nci_score": 60},
            {"receipt_id": "f4", "cohort": "founder", "nci_score": 20, "horizon": "WEEK"},
            {"receipt_id": "e1", "cohort": "external", "nci_score": 90, "mode": "COURT"},
            {"receipt_id": "x1", "cohort": "anonymous"},
        ]
        outcomes = [
            {"receipt_id": "f1", "matched": True, "regret_score": 1},
            {"receipt_id": "f2", "matched": False, "regret_score": 7},
            {"receipt_id": "e1", "matched": True, "regret_score": 2},
        ]
        rep = acc.AccountantOperator().run(receipts, outcomes)
        fo, ex, an = (rep["cohorts"][c] for c in ("founder", "external", "anonymous"))

        self.assertEqual((fo["receipts"], fo["outcomes_logged"], fo["matched"], fo["unmatched"]),
                         (4, 2, 1, 1))
        self.assertEqual(fo["closure_rate"], 0.5)
        self.assertEqual(fo["fate"], {"OPEN": 2, "LOGGED": 2, "EXPIRED": "not_computed"})
        self.assertEqual(fo["by_horizon"], {"WEEK": 2, "TODAY": 1})
        self.assertEqual(fo["by_mode"], {"PLAN": 2})
        self.assertEqual(fo["drift"]["LANDED"], 1)
        self.assertEqual(fo["drift"]["DRIFTING"], 1)
        self.assertEqual(fo["regret_scores"], [1, 7])
        self.assertEqual(fo["mean_regret"], 4.0)
        self.assertEqual(fo["mean_nci_all"], 50.0)

        self.assertEqual((ex["receipts"], ex["outcomes_logged"], ex["closure_rate"]), (1, 1, 1.0))
        self.assertEqual((an["receipts"], an["outcomes_logged"], an["closure_rate"]), (1, 0, 0.0))

        self.assertEqual(rep["totals"]["receipts"], 6)
        self.assertEqual(rep["totals"]["outcomes_joined"], 3)
        self.assertEqual(rep["totals"]["closed_by_cohort"],
                         {"founder": 2, "external": 1, "anonymous": 0})


class TestProdAdapter(unittest.TestCase):
    ROW = {
        "id": "ckreceipt1", "receiptId": "ARCS-ORIENT-001", "userId": "u1",
        "user_email_sha256": "0" * 64, "created_epoch": 1_760_000_000,
        "nciScore": 72, "horizon": None, "window": "this-week", "stakes": "high",
        "mode": "PLAN", "driftState": "LANDED", "yState": "GREEN",
        "outcome_id": "o1", "outcome_matched": True, "outcome_regret_score": 3,
        "outcome_logged_at": "2026-10-01T00:00:00Z", "outcome_what_len": 12,
        "outcome_learning_len": 0,
    }

    def test_receipt_mapping(self):
        r = adapter.adapt_receipt(self.ROW)
        self.assertEqual(r["receipt_id"], "ckreceipt1")
        self.assertEqual(r["dewy_receipt_id"], "ARCS-ORIENT-001")
        self.assertEqual(r["cohort"], "external")
        self.assertEqual(r["nci_score"], 72)
        self.assertEqual(r["horizon"], "this-week")
        self.assertEqual(r["horizon_source"], "window(legacy)")
        self.assertEqual((r["stakes"], r["mode"], r["drift_state"], r["y_state"]),
                         ("high", "PLAN", "LANDED", "GREEN"))
        self.assertEqual(r["created_epoch"], 1_760_000_000)

    def test_horizon_preferred_over_window(self):
        r = adapter.adapt_receipt({**self.ROW, "horizon": "today"})
        self.assertEqual((r["horizon"], r["horizon_source"]), ("today", "horizon"))

    def test_cohort_rule(self):
        founder_sha = next(iter(adapter.FOUNDER_SHA256))
        self.assertEqual(adapter.cohort_of({**self.ROW, "user_email_sha256": founder_sha}), "founder")
        self.assertEqual(adapter.cohort_of({**self.ROW, "userId": None}), "anonymous")
        self.assertEqual(adapter.cohort_of(self.ROW), "external")

    def test_outcome_mapping_and_absence(self):
        o = adapter.adapt_outcome(self.ROW)
        self.assertEqual(o["receipt_id"], "ckreceipt1")
        self.assertEqual((o["matched"], o["regret_score"]), (True, 3))
        self.assertIsNone(adapter.adapt_outcome({**self.ROW, "outcome_id": None}))

    def test_adapt_feeds_operator(self):
        rows = [self.ROW, {**self.ROW, "id": "ckreceipt2", "outcome_id": None}]
        payload = adapter.adapt(rows)
        self.assertEqual((len(payload["receipts"]), len(payload["outcomes"])), (2, 1))
        rep = acc.AccountantOperator().run(**payload)
        self.assertEqual(rep["cohorts"]["external"]["closure_rate"], 0.5)
        self.assertEqual(rep["sufficiency"], "insufficient")


if __name__ == "__main__":
    unittest.main()
