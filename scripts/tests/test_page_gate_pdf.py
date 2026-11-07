#!/usr/bin/env python3
"""page_gate.py PDF checks: a good PDF passes, a bad one fails on each defect class.

Builds both PDFs at test time from tiny HTML with headless Chrome, so no binary fixtures live in git.
    python3 scripts/tests/test_page_gate_pdf.py      # stdlib unittest; skips without Chrome or poppler
"""
import os, shutil, subprocess, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
GATE = os.path.join(os.path.dirname(HERE), "page_gate.py")
CHROME = next((p for p in (
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    shutil.which("google-chrome") or "", shutil.which("chromium") or "") if p and os.path.exists(p)), None)
POPPLER = all(shutil.which(t) for t in ("pdfinfo", "pdffonts", "pdftotext"))

GOOD = """<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Outside Read</title></head>
<body><h1>An outside read</h1><p>The decision: Adobo. See <a href="https://good.arcs.care/rfp-engine">the engine</a>
or <a href="mailto:someone@example.com">write</a>.</p></body></html>"""
BAD = """<!doctype html><html lang="en"><head><meta charset="utf-8"></head>
<body><h1>An outside read — draft</h1><p>Open <a href="file:///Users/someone/page.pdf">the local file</a>.</p></body></html>"""


def render(html, out):
    src = out + ".html"
    with open(src, "w", encoding="utf-8") as f:
        f.write(html)
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={out}", "file://" + src], capture_output=True, check=True, timeout=120)


def gate(path):
    return subprocess.run([sys.executable, GATE, path], capture_output=True, text=True)


@unittest.skipUnless(CHROME and POPPLER, "needs headless Chrome and poppler (brew install poppler)")
class PdfGate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = tempfile.mkdtemp()
        cls.good, cls.bad = os.path.join(cls.d, "good.pdf"), os.path.join(cls.d, "bad.pdf")
        render(GOOD, cls.good)
        render(BAD, cls.bad)

    def test_good_pdf_passes(self):
        r = gate(self.good)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("pdf", r.stdout)

    def test_bad_pdf_fails_on_each_defect(self):
        r = gate(self.bad)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        for key in ("pdf-emdash", "pdf-title", "pdf-link"):
            self.assertIn(key, r.stdout, f"{key} not reported:\n{r.stdout}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
