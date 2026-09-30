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


if __name__ == "__main__":
    unittest.main()
