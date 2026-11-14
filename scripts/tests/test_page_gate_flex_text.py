#!/usr/bin/env python3
"""page_gate.py flex-text check: a flex row with loose words next to a span is flagged; a one-span row and a block row are not.

    python3 scripts/tests/test_page_gate_flex_text.py      # stdlib unittest; skips without node + Chrome (page_gate's own requirements)
Fail-on-bad AND pass-on-good (AGENTS.md gotcha 15): the bad fixture is the 2026-11-12 status page era line.
"""
import os, shutil, subprocess, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
GATE = os.path.join(os.path.dirname(HERE), "page_gate.py")
PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Fixture page</title></head>
<body><main><h1>Fixture</h1>%s</main></body></html>"""
BAD = '<div style="display:flex;gap:8px"><i></i>BUILD TELEMETRY DAY 0 TO DAY <span>217</span> SINCE APR 2026 AS OF <span>Nov 12</span></div>'
GOOD_SPAN = '<div style="display:flex;gap:8px"><i></i><span>BUILD TELEMETRY DAY 0 TO DAY <b>217</b> SINCE APR 2026 AS OF <b>Nov 12</b></span></div>'
GOOD_BLOCK = '<div style="display:block"><i></i>BUILD TELEMETRY DAY 0 TO DAY <span>217</span> SINCE APR 2026 AS OF <span>Nov 12</span></div>'
ONE_RUN = '<div style="display:flex;gap:8px"><i></i>BUILD TELEMETRY DAY 0 TO DAY 217 SINCE APR 2026</div>'
OPT_OUT = BAD.replace("<div ", '<div data-flex-text="ok" ', 1)


def gate(body):
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, "fixture.html")
        open(f, "w", encoding="utf-8").write(PAGE % body)
        r = subprocess.run([sys.executable, GATE, f], capture_output=True, text=True, timeout=300)
        return r.returncode, r.stdout + r.stderr


@unittest.skipUnless(shutil.which("node"), "needs node and playwright")
class FlexText(unittest.TestCase):
    def test_bad_is_flagged(self):
        rc, out = gate(BAD)
        if rc == 2 and "SKIPPED" in out:
            self.skipTest("render checks unavailable here")
        self.assertIn("flex-text", out)

    def test_good_passes(self):
        for body in (GOOD_SPAN, GOOD_BLOCK, OPT_OUT, ONE_RUN):
            rc, out = gate(body)
            if rc == 2 and "SKIPPED" in out:
                self.skipTest("render checks unavailable here")
            self.assertNotIn("flex-text", out, body)


if __name__ == "__main__":
    unittest.main()
