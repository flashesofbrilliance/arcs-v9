"""Unit tests for scripts/reel_in_scan.py pure functions.

Covers verdict() classification (GENUINE-AUTO / NEEDS-RATIFY / WEAK) and archetypes()
tagging. Git-touching functions (gather, patch_id, main) are integration surface and
not exercised here.
"""
import unittest

from _loader import load_reel_in_scan

RS = load_reel_in_scan()
Cand = RS.Cand


class TestVerdict(unittest.TestCase):
    def test_trailer_is_genuine_auto(self):
        c = Cand("abc", "anything at all", True)
        self.assertEqual(RS.verdict(c), "GENUINE-AUTO")

    def test_trailer_wins_even_with_plain_subject(self):
        # body trailer trumps subject regardless of reversal language
        c = Cand("abc", "chore: bump deps", True)
        self.assertEqual(RS.verdict(c), "GENUINE-AUTO")

    def test_subject_revert_prefix_is_needs_ratify(self):
        for subj in ("revert(scope): x", "revert: x", "Revert x"):
            self.assertEqual(RS.verdict(Cand("s", subj, False)), "NEEDS-RATIFY", subj)

    def test_reversal_language_is_needs_ratify(self):
        # whole-word reversal tokens the regex matches correctly
        for subj in (
            "fix: this was a false-claim",
            "chore: mark stale ADR, wrong number",
            "fix: not proven at scale",
            "docs: walk-back the phantom metric",
        ):
            self.assertEqual(RS.verdict(Cand("s", subj, False)), "NEEDS-RATIFY", subj)

    def test_inflected_stems_are_needs_ratify(self):
        # Regression for the _REVERSAL stem fix: inflected forms of the intended stems
        # ("overstated", "confabulated", "overclaimed") must classify NEEDS-RATIFY, not
        # fall through to WEAK. Was a defect (stems closed with a bare \b that could not
        # match past the stem); fixed by carrying \w* on each stem.
        for subj in (
            "fix: overstated the coverage number",
            "docs: was confabulated, correcting",
            "fix: overclaimed the throughput",
        ):
            self.assertEqual(RS.verdict(Cand("s", subj, False)), "NEEDS-RATIFY", subj)

    def test_correction_vocab_without_reversal_is_weak(self):
        for subj in (
            "correct 5 verification failures",
            "reconcile lockfile drift",
            "fix: catch-up territory number",
        ):
            self.assertEqual(RS.verdict(Cand("s", subj, False)), "WEAK", subj)


class TestArchetypes(unittest.TestCase):
    def test_loki(self):
        self.assertIn("loki", RS.archetypes("loki adversarial pre-commit test"))

    def test_kintsugi(self):
        self.assertIn("kintsugi", RS.archetypes("kintsugi repair to the record"))

    def test_drift_sentinel(self):
        self.assertIn("drift-sentinel", RS.archetypes("drift sentinel caught a spin cycle"))

    def test_claims_skeptic(self):
        self.assertIn("claims-skeptic", RS.archetypes("re-audit verification failures for provenance"))

    def test_multiple_tags_possible(self):
        tags = RS.archetypes("kintsugi repair after drift sentinel fired")
        self.assertIn("kintsugi", tags)
        self.assertIn("drift-sentinel", tags)

    def test_no_match_is_empty(self):
        self.assertEqual(RS.archetypes("bump dependency versions"), [])


if __name__ == "__main__":
    unittest.main()
