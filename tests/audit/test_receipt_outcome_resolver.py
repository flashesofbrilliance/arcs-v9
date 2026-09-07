"""Unit tests for scripts/receipt_outcome_resolver.py pure functions.

Covers resolve() — external-verdict scoring, self-graded NOT scored, pending,
NCI>100 excluded, no-stake excluded, held=1.0 / reeled=0.0, ruin weighting — and
load_export() file handling.
"""
import os
import tempfile
import unittest

from _loader import load_receipt_outcome_resolver

RO = load_receipt_outcome_resolver()


class TestResolveScoring(unittest.TestCase):
    def test_external_held_scored_outcome_one(self):
        rows = [{"receipt_id": "r1", "nci_score": 80, "external_verdict": "held",
                 "ruin": "high"}]
        scorable, diag = RO.resolve(rows)
        self.assertEqual(len(scorable), 1)
        s = scorable[0]
        self.assertEqual(s["claim_id"], "r1")
        self.assertEqual(s["confidence"], 0.8)
        self.assertEqual(s["outcome"], 1.0)
        self.assertEqual(s["weight"], 3)              # high
        self.assertEqual(s["meta"]["resolution_source"], "external-adjudication")
        self.assertEqual(diag["externally_adjudicated_scored"], 1)

    def test_external_reeled_scored_outcome_zero(self):
        rows = [{"receipt_id": "r2", "nci_score": 40, "external_verdict": "reeled",
                 "ruin": "low"}]
        scorable, _ = RO.resolve(rows)
        self.assertEqual(scorable[0]["outcome"], 0.0)
        self.assertEqual(scorable[0]["weight"], 1)     # low

    def test_default_ruin_is_med_weight_two(self):
        rows = [{"receipt_id": "r", "nci_score": 50, "external_verdict": "held"}]
        scorable, _ = RO.resolve(rows)
        self.assertEqual(scorable[0]["weight"], 2)

    def test_unknown_ruin_falls_back_to_two(self):
        rows = [{"receipt_id": "r", "nci_score": 50, "external_verdict": "held",
                 "ruin": "bogus"}]
        scorable, _ = RO.resolve(rows)
        self.assertEqual(scorable[0]["weight"], 2)

    def test_self_graded_only_not_scored(self):
        rows = [{"receipt_id": "r", "nci_score": 70, "external_verdict": None,
                 "self_matched": True}]
        scorable, diag = RO.resolve(rows)
        self.assertEqual(scorable, [])
        self.assertEqual(diag["self_graded_only_seen_not_scored"], 1)
        self.assertEqual(diag["pending_no_signal"], 0)

    def test_pending_when_no_signal_at_all(self):
        rows = [{"receipt_id": "r", "nci_score": 70, "external_verdict": None,
                 "self_matched": None}]
        scorable, diag = RO.resolve(rows)
        self.assertEqual(scorable, [])
        self.assertEqual(diag["pending_no_signal"], 1)
        self.assertEqual(diag["self_graded_only_seen_not_scored"], 0)

    def test_nci_over_100_excluded(self):
        rows = [{"receipt_id": "r", "nci_score": 150, "external_verdict": "held"}]
        scorable, diag = RO.resolve(rows)
        self.assertEqual(scorable, [])
        self.assertEqual(diag["excluded_nci_over_100"], 1)

    def test_non_int_nci_is_no_stake(self):
        rows = [
            {"receipt_id": "a", "nci_score": None, "external_verdict": "held"},
            {"receipt_id": "b", "external_verdict": "held"},           # missing nci
            {"receipt_id": "c", "nci_score": "80", "external_verdict": "held"},  # string
        ]
        scorable, diag = RO.resolve(rows)
        self.assertEqual(scorable, [])
        self.assertEqual(diag["excluded_no_stake"], 3)

    def test_bool_nci_is_not_a_stake(self):
        # bool is an int subclass in Python; nci_score=True must NOT be scored as p=0.01.
        # Regression for the bool-guard fix.
        rows = [{"receipt_id": "r", "nci_score": True, "external_verdict": "held"}]
        scorable, diag = RO.resolve(rows)
        self.assertEqual(len(scorable), 0)
        self.assertEqual(diag["excluded_no_stake"], 1)

    def test_mixed_batch_diagnostics(self):
        rows = [
            {"receipt_id": "1", "nci_score": 90, "external_verdict": "held"},
            {"receipt_id": "2", "nci_score": 20, "external_verdict": "reeled"},
            {"receipt_id": "3", "nci_score": 50, "external_verdict": None, "self_matched": False},
            {"receipt_id": "4", "nci_score": 50, "external_verdict": None},
            {"receipt_id": "5", "nci_score": 200, "external_verdict": "held"},
            {"receipt_id": "6", "nci_score": None},
        ]
        scorable, diag = RO.resolve(rows)
        self.assertEqual(diag["export_rows"], 6)
        self.assertEqual(diag["externally_adjudicated_scored"], 2)
        self.assertEqual(diag["self_graded_only_seen_not_scored"], 1)
        self.assertEqual(diag["pending_no_signal"], 1)
        self.assertEqual(diag["excluded_nci_over_100"], 1)
        self.assertEqual(diag["excluded_no_stake"], 1)


class TestLoadExport(unittest.TestCase):
    def test_none_path_returns_empty(self):
        self.assertEqual(RO.load_export(None), [])

    def test_missing_file_returns_empty(self):
        self.assertEqual(RO.load_export("/nonexistent/path/xyz.jsonl"), [])

    def test_parses_jsonl_skipping_blank_lines(self):
        fd, path = tempfile.mkstemp(suffix=".jsonl")
        try:
            with os.fdopen(fd, "w") as fh:
                fh.write('{"receipt_id": "a", "nci_score": 80}\n')
                fh.write("\n")
                fh.write('{"receipt_id": "b", "nci_score": 40}\n')
            rows = RO.load_export(path)
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]["receipt_id"], "a")
            self.assertEqual(rows[1]["nci_score"], 40)
        finally:
            os.remove(path)

    def test_malformed_line_raises_with_line_number(self):
        # Regression for review #6: a bad JSONL line fails loud with its line number,
        # not a bare traceback and not a silent skip.
        fd, path = tempfile.mkstemp(suffix=".jsonl")
        try:
            with os.fdopen(fd, "w") as fh:
                fh.write('{"receipt_id": "a", "nci_score": 80}\n')
                fh.write('{not valid json\n')
            with self.assertRaises(ValueError) as ctx:
                RO.load_export(path)
            self.assertIn("line 2", str(ctx.exception))
        finally:
            os.remove(path)


if __name__ == "__main__":
    unittest.main()
