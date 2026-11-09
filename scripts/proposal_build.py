#!/usr/bin/env python3
"""proposal_build.py: one source page -> the hosted page, a send copy and the PDF.

WHY: the Louisville proposal (louisville.arcs.care/proposal) was built on 2026-11-05 by ten
one-off scripts in a temp folder, with its source untracked. The next edit would have had to
rebuild that pipeline from memory, and a hand edit to the hosted copy would be clobbered by the
next regeneration (memory regen-from-generator-can-clobber-postpublish-handfix). This is the
pipeline, committed, with a --check that fails when the hosted copy drifts from its source.

THE SOURCE is a single-file page with comments, the inlined _tokens.css sentinel, and a PDF
download link `<a class="pdfbtn" href="...">`. Edit only the source.

OUTPUTS
  send    comments stripped (HTML and CSS), the _tokens.css sentinel line kept. Safe to attach.
  hosted  the send copy, with the PDF link pointed at --pdf-href and the Vercel analytics
          snippet added. This is the file in public/.
  pdf     rendered by headless Chrome from the send copy with every <details> forced open,
          US Letter (the page's own @page rule).

USAGE
  python3 scripts/proposal_build.py --source S --hosted public/X.html --pdf public/X.pdf \\
      [--send OUT.html] [--pdf-href /proposal/outside-read.pdf]
  python3 scripts/proposal_build.py --source S --hosted public/X.html --check
  python3 scripts/proposal_build.py --louisville            # the Louisville proposal preset
  python3 scripts/proposal_build.py --louisville --check
Before a multi-part copy edit to the source: run the sanity-check agent (.claude/agents/sanity-check.md).
Then gate the outputs: python3 scripts/page_gate.py --counterpart --matrix full public/X.html public/X.pdf
EXIT 0 ok · 1 --check drift or a build error
"""
import argparse, os, re, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SENTINEL = "/* ARCS Recoil Report — Design Tokens */"
ANALYTICS = '<script defer src="/_vercel/insights/script.js"></script>'
PRESETS = {
    "louisville": dict(source="_ARTIFACTS/louisville-proposal/source.html",
                       hosted="public/louisville-proposal.html",
                       pdf="public/louisville-proposal.pdf",
                       pdf_href="/proposal/outside-read.pdf"),
}
CHROMES = ("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "google-chrome", "chromium")


def send_copy(src):
    out = re.sub(r"<!--.*?-->\n?", "", src, flags=re.S)
    def strip_css(m):
        body = m.group(2).replace(SENTINEL, "\0S\0")
        body = re.sub(r"/\*.*?\*/", "", body, flags=re.S)
        return m.group(1) + body.replace("\0S\0", SENTINEL) + m.group(3)
    out = re.sub(r"(?s)(<style>)(.*?)(</style>)", strip_css, out)
    if SENTINEL in src and SENTINEL not in out:
        raise SystemExit("proposal_build: the _tokens.css sentinel was lost")
    return out


def hosted_copy(send, pdf_href):
    out, n = re.subn(r'(<a class="pdfbtn" href=")[^"]*(")', lambda m: m.group(1) + pdf_href + m.group(2), send)
    if n != 1:
        raise SystemExit(f"proposal_build: expected one a.pdfbtn link, found {n}")
    if ANALYTICS not in out:
        out = out.replace("</head>", ANALYTICS + "\n</head>", 1)
    return out


def render_pdf(send, pdf_out):
    chrome = next((c for c in (shutil.which(x) or x for x in CHROMES) if os.path.exists(c)), None)
    if not chrome:
        raise SystemExit("proposal_build: headless Chrome not found")
    d = tempfile.mkdtemp()
    page = os.path.join(d, "print.html")
    with open(page, "w", encoding="utf-8") as f:
        f.write(re.sub(r"<details(?![^>]*\bopen\b)", "<details open", send))
    subprocess.run([chrome, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={os.path.abspath(pdf_out)}", "file://" + page],
                   capture_output=True, check=True, timeout=180)
    shutil.rmtree(d, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser(description="Build a proposal page's hosted copy, send copy and PDF from one source.")
    ap.add_argument("--louisville", action="store_true", help="use the Louisville proposal paths")
    ap.add_argument("--source"); ap.add_argument("--hosted"); ap.add_argument("--pdf"); ap.add_argument("--send")
    ap.add_argument("--pdf-href", default="/proposal/outside-read.pdf")
    ap.add_argument("--check", action="store_true", help="fail if the hosted copy differs from a fresh build")
    a = ap.parse_args()
    if a.louisville:
        for k, v in PRESETS["louisville"].items():
            if getattr(a, k) is None or k == "pdf_href":
                setattr(a, k, v)
    if not (a.source and a.hosted):
        ap.error("--source and --hosted are required (or --louisville)")
    rel = lambda p: p if os.path.isabs(p) else os.path.join(ROOT, p)
    with open(rel(a.source), encoding="utf-8") as f:
        src = f.read()
    send = send_copy(src)
    hosted = hosted_copy(send, a.pdf_href)

    if a.check:
        try:
            with open(rel(a.hosted), encoding="utf-8") as f:
                live = f.read()
        except FileNotFoundError:
            print(f"✖ proposal-build: {a.hosted} does not exist; build it from {a.source}")
            return 1
        if live != hosted:
            print(f"✖ proposal-build: {a.hosted} differs from a fresh build of {a.source}. "
                  f"Edit the source, then run: python3 scripts/proposal_build.py --source {a.source} --hosted {a.hosted} --pdf <pdf>")
            return 1
        print(f"✓ proposal-build: {a.hosted} matches {a.source}")
        return 0

    with open(rel(a.hosted), "w", encoding="utf-8") as f:
        f.write(hosted)
    print(f"wrote {a.hosted}")
    if a.send:
        with open(rel(a.send), "w", encoding="utf-8") as f:
            f.write(send)
        print(f"wrote {a.send}")
    if a.pdf:
        render_pdf(send, rel(a.pdf))
        print(f"wrote {a.pdf}")
    print(f"next: python3 scripts/page_gate.py --counterpart --matrix full {a.hosted}" + (f" {a.pdf}" if a.pdf else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
