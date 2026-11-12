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
  review  optional (--review-md/--review-pdf): a markdown review copy rendered as a
          double-spaced PDF with numbered paragraphs and a wide notes margin, for readers
          who mark it up by hand. The same markdown seeds the editable Google Doc.

USAGE
  python3 scripts/proposal_build.py --source S --hosted public/X.html --pdf public/X.pdf \\
      [--send OUT.html] [--pdf-href /proposal/outside-read.pdf]
  python3 scripts/proposal_build.py --source S --hosted public/X.html --check
  python3 scripts/proposal_build.py --louisville            # the Louisville proposal preset
  python3 scripts/proposal_build.py --louisville --check
  python3 scripts/proposal_build.py --louisville --tune OUT.html     internal copy with the live editor (refuses public/)
  python3 scripts/proposal_build.py --louisville --apply EXPORT [...] the editor's exports back to the source, then rebuild
                                    (text to the source page; tokens and wrapping to a tuned block in its <style>)
Before a multi-part copy edit to the source: run the sanity-check agent (.claude/agents/sanity-check.md).
Then gate the outputs: python3 scripts/page_gate.py --counterpart --matrix full public/X.html public/X.pdf
EXIT 0 ok · 1 --check drift or a build error
"""
import argparse, os, re, shutil, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import page_tune as pt  # the shared --tune / --apply mechanics

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SENTINEL = "/* ARCS Recoil Report — Design Tokens */"
ANALYTICS = '<script defer src="/_vercel/insights/script.js"></script>'
PRESETS = {
    "louisville": dict(source="_ARTIFACTS/louisville-proposal/source.html",
                       hosted="public/louisville-proposal.html",
                       pdf="public/louisville-proposal.pdf",
                       pdf_href="/proposal/outside-read.pdf",
                       review_md="_ARTIFACTS/louisville-proposal/review-copy.md",
                       review_pdf="public/louisville-proposal-review.pdf",
                       # the same text as plain Markdown, for AI tools and agents (served gated at /proposal/proposal.md)
                       review_txt="public/louisville-proposal.md"),
}

# Review copy: the proposal as plain, numbered text for a reader who marks it up by hand
# (Zach, 2026-11-09: "printable copy to redline with a pen ... for old school legal teams").
# Double-spaced body, a wide right margin for notes, ruled answer cells, page numbers.
REVIEW_CSS = """
@page{size:Letter;margin:0.9in 2.1in 0.9in 1in;
  @bottom-left{content:"Review copy  \\00B7  Confidential";font:8pt Georgia,serif;color:#555;}
  @bottom-right{content:"Page " counter(page) " of " counter(pages);font:8pt Georgia,serif;color:#555;}}
html{font:11.5pt/2 Georgia,"Times New Roman",serif;color:#111;}
body{margin:0;}
h1{font-size:20pt;line-height:1.25;margin:0 0 6pt;}
h2{font-size:13pt;line-height:1.3;margin:18pt 0 4pt;break-after:avoid;}
p{margin:0 0 8pt;}
ol{margin:0 0 8pt;padding-left:22pt;}
table{width:100%;border-collapse:collapse;margin:6pt 0 12pt;font-size:10.5pt;line-height:1.6;break-inside:auto;}
th,td{border:0.75pt solid #444;padding:6pt 7pt;vertical-align:top;text-align:left;}
th{background:#eee;}
tr{break-inside:avoid;}
td:empty{height:46pt;}
"""
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


def render_review(md_path, pdf_out):
    pandoc = shutil.which("pandoc")
    if not pandoc:
        raise SystemExit("proposal_build: pandoc not found (needed for the review copy)")
    body = subprocess.run([pandoc, "-f", "gfm", "-t", "html5", md_path], capture_output=True,
                          check=True, text=True).stdout
    page = ('<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Review copy</title><style>'
            + REVIEW_CSS + "</style></head><body>" + body + "</body></html>")
    render_pdf(page, pdf_out)


def main():
    ap = argparse.ArgumentParser(description="Build a proposal page's hosted copy, send copy and PDF from one source.")
    ap.add_argument("--louisville", action="store_true", help="use the Louisville proposal paths")
    ap.add_argument("--source"); ap.add_argument("--hosted"); ap.add_argument("--pdf"); ap.add_argument("--send")
    ap.add_argument("--pdf-href", default="/proposal/outside-read.pdf")
    ap.add_argument("--review-md"); ap.add_argument("--review-pdf"); ap.add_argument("--review-txt")
    ap.add_argument("--check", action="store_true", help="fail if the hosted copy differs from a fresh build")
    pt.add_args(ap)
    a = ap.parse_args()
    if a.louisville:
        for k, v in PRESETS["louisville"].items():
            if getattr(a, k) is None or k == "pdf_href":
                setattr(a, k, v)
    if not (a.source and a.hosted):
        ap.error("--source and --hosted are required (or --louisville)")
    rel = lambda p: p if os.path.isabs(p) else os.path.join(ROOT, p)
    if a.apply:  # the source is hand HTML: text pairs and the tuned style block both land in it; then build as usual
        pt.apply(a.apply, [("html", rel(a.source))], style=("block", rel(a.source)), version=a.version)
    with open(rel(a.source), encoding="utf-8") as f:
        src = f.read()
    send = send_copy(src)
    # Guard (2026-11-09): a scripted copy edit once shipped "I\'m" to the counterpart. Refuse an
    # escaped quote in the page's visible text (scripts and styles are skipped).
    visible = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", "", send, flags=re.S)
    if re.search(r"\\['\"]", re.sub(r"<[^>]+>", "", visible)):
        print("✖ proposal-build: escaped quote (\\' or \\\") in visible text; fix the source")
        return 1
    hosted = hosted_copy(send, a.pdf_href)
    if a.tune:
        pt.tune_write(hosted, a.tune)
        return 0

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
    if a.review_md and a.review_pdf:
        render_review(rel(a.review_md), rel(a.review_pdf))
        print(f"wrote {a.review_pdf}")
    if a.review_md and a.review_txt:
        shutil.copyfile(rel(a.review_md), rel(a.review_txt))
        print(f"wrote {a.review_txt}")
    print(f"next: python3 scripts/page_gate.py --counterpart --matrix full {a.hosted}" + (f" {a.pdf}" if a.pdf else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
