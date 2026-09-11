"""Unit tests for scripts/believability_ledger.py pure functions.

Covers score_ledger() Brier math (unweighted vs weighted, base-rate baseline,
always-0.5 hedge, seaworthiness threshold), the empty/null-honest path, unresolved
exclusion, ruin_weight() file classification, high_conf_reel_ins(), and the
ReceiptOutcomeResolver honest-stub.

No git shell-outs — the resolvers that touch git (GitRevertResolver.resolve) are
integration surface and deliberately not exercised here.
"""
import unittest

from _loader import load_believability

BL = load_believability()
ClaimRow = BL.ClaimRow


def row(conf, outcome, weight=1, cid="c", meta=None):
    return ClaimRow(cid, conf, outcome, weight, meta or {})


class TestScoreLedgerEmpty(unittest.TestCase):
    def test_no_rows_is_null_honest_not_zero(self):
        s = BL.score_ledger([])
        self.assertEqual(s["resolved"], 0)
        self.assertIsNone(s["brier_unweighted"])
        self.assertIsNone(s["brier_weighted"])
        self.assertIsNone(s["base_rate_hold"])
        self.assertIsNone(s["model_skill_vs_base_rate"])
        self.assertIn("Brier undefined", s["note"])

    def test_only_unresolved_rows_is_still_null_honest(self):
        s = BL.score_ledger([row(0.9, None), row(0.5, None)])
        self.assertEqual(s["resolved"], 0)
        self.assertEqual(s["unresolved"], 2)
        self.assertIsNone(s["brier_weighted"])


class TestScoreLedgerBrierMath(unittest.TestCase):
    def setUp(self):
        # r1: p=0.9 held  weight 1 -> err 0.01
        # r2: p=0.2 reeled weight 3 -> err 0.04
        self.rows = [row(0.9, 1.0, 1, "held1"), row(0.2, 0.0, 3, "reel1")]
        self.s = BL.score_ledger(self.rows)

    def test_resolved_and_unresolved_counts(self):
        s = BL.score_ledger(self.rows + [row(0.5, None)])
        self.assertEqual(s["resolved"], 2)
        self.assertEqual(s["unresolved"], 1)

    def test_unweighted_brier(self):
        # (0.01 + 0.04) / 2
        self.assertEqual(self.s["brier_unweighted"], 0.025)

    def test_weighted_brier_differs_from_unweighted(self):
        # (1*0.01 + 3*0.04) / (1+3) = 0.13/4
        self.assertEqual(self.s["brier_weighted"], 0.0325)
        self.assertNotEqual(self.s["brier_weighted"], self.s["brier_unweighted"])

    def test_base_rate_hold(self):
        self.assertEqual(self.s["base_rate_hold"], 0.5)

    def test_base_rate_brier_baseline(self):
        # ((0.5-1)^2 + (0.5-0)^2)/2 = 0.25
        self.assertEqual(self.s["brier_base_rate"], 0.25)

    def test_always_half_hedge_baseline(self):
        # identical to base rate here because hold_rate happens to be 0.5
        self.assertEqual(self.s["brier_always_0.5_hedge"], 0.25)

    def test_model_skill_vs_base_rate(self):
        # weighted base-rate (review #3): w_hold=(1*1+3*0)/4=0.25 →
        # brier_base_w = (1*(0.25-1)^2 + 3*(0.25-0)^2)/4 = 0.1875; minus weighted(0.0325) = 0.155
        self.assertEqual(self.s["brier_base_rate_weighted"], 0.1875)
        self.assertEqual(self.s["model_skill_vs_base_rate"], 0.155)

    def test_reel_in_count(self):
        self.assertEqual(self.s["reel_ins"], 1)


class TestWeightedBaseRate(unittest.TestCase):
    # Regression for review #3: model_skill must compare a WEIGHTED model Brier against a
    # WEIGHTED base-rate Brier. With mixed weights whose outcome correlates with weight,
    # the weighted and unweighted base-rate Briers diverge, and model_skill uses the weighted one.
    def setUp(self):
        # w=1 held, w=3 reeled → unweighted hold 0.5, weighted hold 0.25
        self.s = BL.score_ledger([row(0.9, 1.0, weight=1), row(0.9, 0.0, weight=3)])

    def test_weighted_and_unweighted_base_rate_differ(self):
        self.assertEqual(self.s["brier_base_rate"], 0.25)
        self.assertEqual(self.s["brier_base_rate_weighted"], 0.1875)

    def test_model_skill_uses_weighted_baseline(self):
        # brier_base_w (0.1875) - brier_w (0.61) = -0.4225
        self.assertEqual(self.s["brier_weighted"], 0.61)
        self.assertEqual(self.s["model_skill_vs_base_rate"], -0.4225)

    def test_top_reliability_bucket_clamped(self):
        # p=1.0 lands in "90-100%", never a nonsensical "100-109%" (review #8)
        s = BL.score_ledger([row(1.0, 1.0, weight=1), row(0.95, 0.0, weight=1)])
        self.assertIn("90-100%", s["reliability_buckets"])
        self.assertNotIn("100-109%", s["reliability_buckets"])


class TestSeaworthiness(unittest.TestCase):
    def test_sparse_reel_ins_not_seaworthy(self):
        # only 1 reel-in -> below the >=3 threshold
        s = BL.score_ledger([row(0.2, 0.0, 1), row(0.9, 1.0, 1)])
        self.assertFalse(s["seaworthy"])
        self.assertIn("NON-DISCRIMINATING", s["verdict"])

    def test_all_held_high_hold_rate_not_seaworthy(self):
        # hold_rate == 1.0 >= 0.99 -> degenerate even if many rows
        s = BL.score_ledger([row(0.9, 1.0, 1) for _ in range(10)])
        self.assertFalse(s["seaworthy"])
        self.assertEqual(s["reel_ins"], 0)

    def test_three_reel_ins_and_holds_is_seaworthy(self):
        rows = [row(0.2, 0.0, 1, f"r{i}") for i in range(3)] + \
               [row(0.9, 1.0, 1, f"h{i}") for i in range(5)]
        s = BL.score_ledger(rows)
        self.assertTrue(s["seaworthy"])
        self.assertEqual(s["reel_ins"], 3)
        self.assertLess(s["base_rate_hold"], 0.99)
        self.assertIn("discriminating", s["verdict"])

    def test_boundary_exactly_three_reelins_but_hold_rate_ge_099(self):
        # 3 reel-ins but hold_rate >= 0.99 still fails (OR condition)
        rows = [row(0.2, 0.0, 1, f"r{i}") for i in range(3)] + \
               [row(0.99, 1.0, 1, f"h{i}") for i in range(400)]
        s = BL.score_ledger(rows)
        self.assertGreaterEqual(s["base_rate_hold"], 0.99)
        self.assertFalse(s["seaworthy"])


class TestRuinWeight(unittest.TestCase):
    def test_prisma_is_high(self):
        self.assertEqual(BL.ruin_weight(["prisma/schema.prisma"]), (3, "high"))

    def test_auth_lib_is_high(self):
        self.assertEqual(BL.ruin_weight(["src/lib/auth.ts"]), (3, "high"))

    def test_api_route_is_high(self):
        self.assertEqual(BL.ruin_weight(["src/app/api/compass/route.ts"]), (3, "high"))

    def test_migration_substring_is_high(self):
        self.assertEqual(BL.ruin_weight(["db/somemigration.sql"]), (3, "high"))

    def test_other_src_is_med(self):
        self.assertEqual(BL.ruin_weight(["src/components/Foo.tsx"]), (2, "med"))

    def test_docs_is_low(self):
        self.assertEqual(BL.ruin_weight(["docs/readme.md"]), (1, "low"))

    def test_empty_is_low(self):
        self.assertEqual(BL.ruin_weight([]), (1, "low"))

    def test_high_wins_over_med_when_mixed(self):
        self.assertEqual(BL.ruin_weight(["src/components/Foo.tsx", "prisma/x"]), (3, "high"))


class TestHighConfReelIns(unittest.TestCase):
    def test_flags_only_confident_reeled(self):
        rows = [
            row(0.9, 0.0, 3, "a", {"reeled_by": "z", "ruin": "high", "subject": "big claim"}),
            row(0.5, 0.0, 1, "b", {"subject": "low conf reel"}),   # below 0.85
            row(0.95, 1.0, 1, "c", {"subject": "held"}),           # held, not a reel-in
        ]
        out = BL.high_conf_reel_ins(rows)
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["claim"], "a")
        self.assertEqual(out[0]["confidence"], 0.9)

    def test_sorted_descending_by_confidence(self):
        rows = [
            row(0.86, 0.0, 1, "a", {"subject": "s"}),
            row(0.99, 0.0, 1, "b", {"subject": "s"}),
        ]
        out = BL.high_conf_reel_ins(rows)
        self.assertEqual([o["claim"] for o in out], ["b", "a"])


class TestReceiptOutcomeResolverStub(unittest.TestCase):
    def test_returns_empty_and_not_wired(self):
        rows, diag = BL.ReceiptOutcomeResolver().resolve()
        self.assertEqual(rows, [])
        self.assertEqual(diag["status"], "NOT_WIRED")


if __name__ == "__main__":
    unittest.main()
