import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import arcs_verb_eval as core  # noqa: E402
import arcs_verb_eval_io as vio  # noqa: E402


class SelfTests(unittest.TestCase):
    def test_core_gates_fail_on_bad_and_pass_on_good(self):
        self.assertEqual(core.self_test(), 0)

    def test_io_ingest_and_export(self):
        self.assertEqual(vio.self_test(), 0)

    def test_example_notebook_ingests(self):
        import tempfile
        out = tempfile.mkdtemp()
        man = vio.ingest(str(Path(__file__).parent.parent / "examples/training-run.ipynb"), out)
        self.assertGreater(man["claims"], 0)
        rep = core.evaluate("analysis", (Path(out) / "analysis.html").read_text())
        self.assertTrue(rep["ok"], rep["failed"])


class WebParity(unittest.TestCase):
    """The page's JavaScript must fail the same gates as the Python engine on every self-test case."""

    CLI_ONLY = {"ex-ante-receipt", "pre-send-gauntlet", "slop-lint"}

    def test_js_engine_matches_python(self):
        import json, shutil, subprocess, tempfile
        node = shutil.which("node")
        if not node:
            self.skipTest("node not installed")
        tmp = Path(tempfile.mkdtemp())
        (tmp / "ex-ante.json").write_text("{}")
        (tmp / "gauntlet.json").write_text("{}")
        opts = {"slop": False, "base": tmp}
        cases, expected, good_idx, prints = [], [], {}, {}
        up = None
        for v in core.VERBS:
            r = core.evaluate(v, core.GOOD[v], upstream=up, **opts)
            good_idx[v] = len(cases)
            cases.append({"verb": v, "text": core.GOOD[v], "up": good_idx.get(core.VERBS[core.VERBS.index(v) - 1]) if v != "analysis" else None})
            expected.append(r["failed"])
            prints[v] = up = r
        for v, mut, _gate in core.BAD:
            prev = core.VERBS[core.VERBS.index(v) - 1] if v != "analysis" else None
            r = core.evaluate(v, mut(core.GOOD[v]), upstream=prints[prev] if prev else None, **opts)
            cases.append({"verb": v, "text": mut(core.GOOD[v]), "up": good_idx[prev] if prev else None})
            expected.append(r["failed"])
        js = Path(__file__).parent / "parity.js"
        out = subprocess.run([node, str(js)], input=json.dumps(cases), capture_output=True, text=True, check=True)
        got = json.loads(out.stdout)
        for i, (c, want, have) in enumerate(zip(cases, expected, got)):
            w = sorted(set(want) - self.CLI_ONLY)
            h = sorted(set(have) - self.CLI_ONLY)
            self.assertEqual(w, h, f"case {i} ({c['verb']}): python failed {w}, js failed {h}")
        self.assertEqual(len(got), 23)


if __name__ == "__main__":
    unittest.main()
