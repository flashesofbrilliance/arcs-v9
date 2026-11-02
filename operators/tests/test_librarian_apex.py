"""Unit tests for the Apex Spine source and the quorum gaps in operators/arcs_librarian.py (Operator 21).

Synthetic corpus only: no dependence on gitignored universe files. Pre-registration:
_PATTERNS/2026-11-02-card-catalog-sweep-prereg.md.

Run: python3 -m unittest discover -s operators/tests
Stdlib only.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import arcs_librarian as lib  # noqa: E402

SPINE = """# Apex Spine test page

Thesis: one non-orientable surface, 2026-10-01.

## The spine (witness to ADR)

witness quartzline feeds the ADR chain.

## Honesty air-gaps

the spine is its own gate, no silent patching.
"""


def _root(with_spine=True):
    root = Path(tempfile.mkdtemp())
    if with_spine:
        (root / "_CANON").mkdir()
        (root / lib.APEX_SPINE_REL).write_text(SPINE)
    return root


class ApexSpineLoader(unittest.TestCase):
    def test_one_candidate_per_section_plus_preamble(self):
        c = lib.load_apex_spine(_root())
        self.assertEqual([x.id for x in c], ["apex-spine:preamble", "apex-spine:the-spine-witness-to-adr", "apex-spine:honesty-air-gaps"])
        self.assertTrue(all(x.cls == "apex-spine" and x.date == "2026-10-01" for x in c))
        self.assertTrue(c[1].path.endswith("#the-spine-witness-to-adr"))

    def test_missing_page_degrades_to_empty(self):
        self.assertEqual(lib.load_apex_spine(_root(with_spine=False)), [])


class SweepBesideReceiptsAndAdrs(unittest.TestCase):
    def setUp(self):
        root = _root()
        extra = [lib.Candidate(id="ADR-900", cls="adr", path="_DECISIONS/ADR-900.md", text="quartzline witness decision record"),
                 lib.Candidate(id="2026-10-01--quartzline--ZH", cls="personal-receipt", path="decision_receipt:test", text="Ship quartzline? Confirmed: merged. Unconfirmed: tone")]
        self.lib = lib.Librarian(root=root, git_root=lib.DEFAULT_ROOT, memory_dir=None, load_corpus=False,
                                 extra_candidates=lib.load_apex_spine(root) + extra)
        self.res = self.lib.recommend("quartzline witness", budget=20000, stakes="high")

    def test_apex_spine_hit_returned_beside_adr_and_receipt(self):
        classes = {i["class"] for i in self.res["items"]}
        self.assertTrue({"apex-spine", "adr", "personal-receipt"} <= classes, classes)

    def test_every_item_has_graded_source_and_provenance(self):
        for i in self.res["items"]:
            self.assertTrue(i["source"]["tier"])
            self.assertTrue(i["path"] and i["why_load_bearing"])
            self.assertIn("verified", i["freshness"])

    def test_unbacked_apex_hit_is_unconfirmed_never_confirmed(self):
        self.assertIn("apex-spine:the-spine-witness-to-adr", self.res["what_unconfirmed"])
        self.assertFalse(set(self.res["what_confirmed"]) & set(self.res["what_unconfirmed"]))

    def test_class_borrows_a_tier_row_when_the_tiers_file_lacks_it(self):
        self.assertNotIn("apex-spine", self.lib.tiers["classes"])
        item = next(i for i in self.res["items"] if i["class"] == "apex-spine")
        self.assertEqual(item["read_friction"]["tier"], self.lib.tiers["classes"]["essay"]["tier"])

    def test_negative_control_returns_nothing_from_the_spine(self):
        r = self.lib.recommend("zebra metronome tuning", budget=20000, stakes="medium")
        self.assertFalse([i for i in r["items"] if i["class"] == "apex-spine"])


class QuorumGaps(unittest.TestCase):
    def test_gaps_named_and_never_consulted(self):
        gaps = lib.Librarian(load_corpus=False, memory_dir=None).recommend("anything")["gaps"]
        self.assertEqual([g["member"] for g in gaps], ["Op 25 Sage", "auditor", "scholar"])
        self.assertFalse(any(g["consulted"] for g in gaps))
        self.assertIn("UNBUILT", gaps[0]["evidence"])

    def test_gap_reads_registry_not_assumption(self):
        root = Path(tempfile.mkdtemp())
        (root / "operators").mkdir()
        (root / "operators" / "OPERATOR-REGISTRY.json").write_text(json.dumps({"operators": [{"op": 25, "name": "X", "status": "READY"}]}))
        g = lib.Librarian(root=root, git_root=lib.DEFAULT_ROOT, load_corpus=False, memory_dir=None).quorum_gaps()
        self.assertIn("[READY]", g[0]["evidence"])


if __name__ == "__main__":
    unittest.main()
