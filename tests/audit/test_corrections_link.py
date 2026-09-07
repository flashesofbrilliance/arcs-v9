"""Unit tests for scripts/corrections_link.py pure functions.

Covers numeric_nci() parsing, Candidate.strength / Candidate.self_link, and the
diff-parsing logic of removed_lines_by_file() (git is stubbed with a canned diff so
the parser is tested deterministically — no real repo access).
"""
import unittest

from _loader import load_corrections_link

CL = load_corrections_link()
Candidate = CL.Candidate


class TestNumericNci(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(CL.numeric_nci("feat(x): thing [NCI:52]"), 52)

    def test_skip_is_none(self):
        self.assertIsNone(CL.numeric_nci("chore: x [NCI:SKIP]"))

    def test_skip_docs_is_none(self):
        self.assertIsNone(CL.numeric_nci("docs: x [NCI:SKIP docs]"))

    def test_nci_with_trailing_word_is_none(self):
        self.assertIsNone(CL.numeric_nci("x [NCI:52 docs]"))

    def test_non_numeric_is_none(self):
        self.assertIsNone(CL.numeric_nci("x [NCI:high]"))

    def test_no_tag_is_none(self):
        self.assertIsNone(CL.numeric_nci("plain subject no tag"))

    def test_over_100_is_returned_uncapped(self):
        # NOTE: numeric_nci does NOT cap at 100 — unlike believability_ledger, which
        # excludes NCI>100 as uninterpretable. corrections_link.build() likewise does
        # not exclude >100. Documented divergence, flagged in the test report.
        self.assertEqual(CL.numeric_nci("x [NCI:150]"), 150)


class TestCandidateStrength(unittest.TestCase):
    def _cand(self, linked, total, corr="aaaaaaaaaaaa", claim="bbbbbbbbbbbb"):
        return Candidate(corr, "corr subj", claim, 50, "claim subj", linked, total, ["f.py"])

    def test_strength_fraction(self):
        self.assertEqual(self._cand(3, 4).strength, 0.75)

    def test_strength_rounds_to_3(self):
        self.assertEqual(self._cand(1, 3).strength, 0.333)

    def test_strength_zero_when_total_removed_zero(self):
        self.assertEqual(self._cand(0, 0).strength, 0.0)

    def test_full_attribution(self):
        self.assertEqual(self._cand(5, 5).strength, 1.0)


class TestCandidateSelfLink(unittest.TestCase):
    def test_self_link_when_prefixes_match(self):
        # short sha (claim) is a prefix of the correction sha
        c = Candidate("abcdef123456", "s", "abcdef", 50, "s", 1, 1, [])
        self.assertTrue(c.self_link)

    def test_self_link_symmetric(self):
        c = Candidate("abcdef", "s", "abcdef123456", 50, "s", 1, 1, [])
        self.assertTrue(c.self_link)

    def test_cross_session_not_self_link(self):
        c = Candidate("abcdef123456", "s", "999999999999", 50, "s", 1, 1, [])
        self.assertFalse(c.self_link)


class TestRemovedLinesByFile(unittest.TestCase):
    def setUp(self):
        self._orig = CL._git

    def tearDown(self):
        CL._git = self._orig

    def _stub(self, diff):
        CL._git = lambda *a, **k: diff

    def test_parses_removed_old_line_numbers(self):
        diff = (
            "diff --git a/foo.py b/foo.py\n"
            "--- a/foo.py\n"
            "+++ b/foo.py\n"
            "@@ -10,2 +10,1 @@\n"
            "-old line 10\n"
            "-old line 11\n"
            "+replacement line\n"
        )
        self._stub(diff)
        self.assertEqual(CL.removed_lines_by_file("deadbeef"), {"foo.py": [10, 11]})

    def test_additions_do_not_advance_old_counter(self):
        diff = (
            "diff --git a/bar.py b/bar.py\n"
            "--- a/bar.py\n"
            "+++ b/bar.py\n"
            "@@ -5,1 +5,3 @@\n"
            "-only removed line 5\n"
            "+added a\n"
            "+added b\n"
        )
        self._stub(diff)
        self.assertEqual(CL.removed_lines_by_file("deadbeef"), {"bar.py": [5]})

    def test_multiple_hunks_reset_old_line(self):
        diff = (
            "diff --git a/baz.py b/baz.py\n"
            "--- a/baz.py\n"
            "+++ b/baz.py\n"
            "@@ -3,1 +3,0 @@\n"
            "-line 3\n"
            "@@ -20,2 +19,0 @@\n"
            "-line 20\n"
            "-line 21\n"
        )
        self._stub(diff)
        self.assertEqual(CL.removed_lines_by_file("deadbeef"), {"baz.py": [3, 20, 21]})

    def test_whole_file_deletion_attributes_to_old_path(self):
        # Regression for review #4: a whole-file deletion header is `--- a/gone.py` /
        # `+++ /dev/null`. Removed lines must attribute to gone.py (the OLD path we blame),
        # never to a previous file and never dropped.
        diff = (
            "diff --git a/gone.py b/gone.py\n"
            "deleted file mode 100644\n"
            "--- a/gone.py\n"
            "+++ /dev/null\n"
            "@@ -1,2 +0,0 @@\n"
            "-claim line 1\n"
            "-claim line 2\n"
        )
        self._stub(diff)
        self.assertEqual(CL.removed_lines_by_file("deadbeef"), {"gone.py": [1, 2]})

    def test_new_file_has_no_removed_lines(self):
        # `--- /dev/null` (file added) → no old lines to attribute.
        diff = (
            "diff --git a/new.py b/new.py\n"
            "new file mode 100644\n"
            "--- /dev/null\n"
            "+++ b/new.py\n"
            "@@ -0,0 +1,2 @@\n"
            "+brand new 1\n"
            "+brand new 2\n"
        )
        self._stub(diff)
        self.assertEqual(CL.removed_lines_by_file("deadbeef"), {})

    def test_pure_addition_file_excluded(self):
        # a file with no removed lines is dropped from the result
        diff = (
            "diff --git a/new.py b/new.py\n"
            "--- a/new.py\n"
            "+++ b/new.py\n"
            "@@ -0,0 +1,2 @@\n"
            "+added a\n"
            "+added b\n"
        )
        self._stub(diff)
        self.assertEqual(CL.removed_lines_by_file("deadbeef"), {})


if __name__ == "__main__":
    unittest.main()
