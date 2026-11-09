#!/usr/bin/env python3
"""Format a plain-language agreement (markdown) into a counsel-ready Word file and PDF.

Input is the markdown export of the agreement doc (Claude Docs export, or any .md).
Output, in --out (default: the input's folder):
  <stem>.docx           Word, for counsel's redlines: serif body, headings as written,
                        footer "<title> | <version> | Page X of Y"
  <stem>.pdf            the same, print-ready on US Letter
  <stem>.manifest.json  sha256 of the source and both outputs, for the decision receipt

Before it builds, it lints the text and refuses on anything that must not reach a signer:
open choices or blanks in [square brackets], TBD/TODO, doc chips (@mentions), em or en
dashes, "your business name" style placeholders, and a signature table with an empty Name
cell. --draft builds anyway and stamps "DRAFT, not for signature" in the footer.
--check lints only (exit 1 on any finding).

Substance is not checked here: the paralegal and best-practices-clerk agents
(.claude/agents/) review the text; this script only makes it presentable and refuses blanks.

Tools: pandoc (system binary) and Google Chrome (headless print). No Python dependencies.
Usage:
  python3 scripts/contract_format.py agreement.md --version "rev 28" [--draft] [--out DIR]
  python3 scripts/contract_format.py agreement.md --check
  python3 scripts/contract_format.py --self-test
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# A markdown link "[text](url)" and a ticked box "[x]" are not blanks.
BLANK = re.compile(r"\\?\[(?!\s*[xX ]?\s*\\?\])([^\]\n]{1,200}?)\\?\](?!\()")
LINT_RULES = [
    ("open choice or blank in [brackets]", BLANK),
    ("TBD or TODO", re.compile(r"\bTBD\b|\bTODO\b")),
    ("doc chip (@mention)", re.compile(r"(?<![\w.])@[A-Z]\w+")),
    ("em or en dash", re.compile("[\u2014\u2013]")),
    ("placeholder", re.compile(r"your (business|company|legal) name", re.I)),
]


def clean(md: str) -> tuple[str, list[str]]:
    """Undo export artifacts. Returns (text, notes of what was changed)."""
    notes = []
    md = md.replace("&#91;", "[").replace("&#93;", "]")
    out = []
    for line in md.splitlines():
        # Claude Docs header chips, e.g. "Nov 6, 2026 · @Zach Harris"
        if re.fullmatch(r"\s*[A-Z][a-z]{2} \d{1,2}, \d{4}\s*·\s*@.+", line):
            notes.append(f"dropped doc chip line: {line.strip()}")
            continue
        out.append(line)
    return "\n".join(out).strip() + "\n", notes


def lint(md: str) -> list[str]:
    problems = []
    for n, line in enumerate(md.splitlines(), 1):
        for name, rx in LINT_RULES:
            m = rx.search(line)
            if m:
                problems.append(f"line {n}: {name}: {m.group(0)[:80]!r}")
        if re.match(r"\|\s*Name\s*\|", line):
            cells = [c.strip() for c in line.strip().strip("|").split("|")][1:]
            if any(c == "" for c in cells):
                problems.append(f"line {n}: signature block: a Name cell is empty")
    return problems


FOOTER_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:ftr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
<w:p><w:pPr><w:jc w:val="center"/></w:pPr>
<w:r><w:rPr><w:sz w:val="16"/></w:rPr><w:t xml:space="preserve">{label} | Page </w:t></w:r>
<w:r><w:rPr><w:sz w:val="16"/></w:rPr><w:fldChar w:fldCharType="begin"/></w:r>
<w:r><w:rPr><w:sz w:val="16"/></w:rPr><w:instrText xml:space="preserve"> PAGE </w:instrText></w:r>
<w:r><w:rPr><w:sz w:val="16"/></w:rPr><w:fldChar w:fldCharType="end"/></w:r>
<w:r><w:rPr><w:sz w:val="16"/></w:rPr><w:t xml:space="preserve"> of </w:t></w:r>
<w:r><w:rPr><w:sz w:val="16"/></w:rPr><w:fldChar w:fldCharType="begin"/></w:r>
<w:r><w:rPr><w:sz w:val="16"/></w:rPr><w:instrText xml:space="preserve"> NUMPAGES </w:instrText></w:r>
<w:r><w:rPr><w:sz w:val="16"/></w:rPr><w:fldChar w:fldCharType="end"/></w:r>
</w:p></w:ftr>"""
REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"


def build_reference_docx(dst: Path, label: str) -> None:
    """Pandoc's default reference.docx, restyled (Georgia, black headings) with a page-number footer."""
    src = dst.with_suffix(".src.docx")
    subprocess.run(["pandoc", "-o", str(src), "--print-default-data-file", "reference.docx"], check=True)
    with zipfile.ZipFile(src) as zin, zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            name = item.filename
            if name == "word/styles.xml":
                s = data.decode()
                s = re.sub(r'w:(ascii|hAnsi|cs|eastAsia)Theme="[^"]*"', "", s)
                s = re.sub(r'w:ascii="[^"]*"', 'w:ascii="Georgia"', s)
                s = re.sub(r'w:hAnsi="[^"]*"', 'w:hAnsi="Georgia"', s)
                s = re.sub(r'<w:color w:val="[0-9A-Fa-f]{6}"[^/]*/>', '<w:color w:val="000000"/>', s)
                data = s.encode()
            elif name == "word/document.xml":
                s = data.decode()
                ref = '<w:footerReference w:type="default" r:id="rIdFtr1"/>'
                s, k = re.subn(r"(<w:sectPr\b[^>]*>)", r"\1" + ref, s, count=1)
                if not k:
                    raise SystemExit("reference.docx has no sectPr; cannot attach the footer")
                if "xmlns:r=" not in s:
                    s = s.replace("<w:document ", f'<w:document xmlns:r="{REL_NS}" ', 1)
                data = s.encode()
            elif name == "word/_rels/document.xml.rels":
                data = data.decode().replace("</Relationships>",
                    f'<Relationship Id="rIdFtr1" Type="{REL_NS}/footer" Target="footer1.xml"/></Relationships>').encode()
            elif name == "[Content_Types].xml":
                data = data.decode().replace("</Types>",
                    '<Override PartName="/word/footer1.xml" ContentType="application/'
                    'vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/></Types>').encode()
            zout.writestr(item, data)
        zout.writestr("word/footer1.xml", FOOTER_XML.format(label=html.escape(label)))
    src.unlink()


PRINT_CSS = """
@page { size: letter; margin: 1in 1in 0.9in 1in;
  @bottom-center { content: "%(label)s | Page " counter(page) " of " counter(pages);
    font: 8pt Georgia, serif; color: #000; } }
html { background: #fff; }
body { font: 11pt/1.45 Georgia, "Times New Roman", serif; color: #000; max-width: none; margin: 0; padding: 0; }
header#title-block-header { display: none; }
h1 { font-size: 16pt; margin: 0 0 14pt; }
h2 { font-size: 12pt; margin: 16pt 0 6pt; break-after: avoid; }
h3 { font-size: 11pt; margin: 12pt 0 4pt; break-after: avoid; }
p, li { orphans: 3; widows: 3; }
table { border-collapse: collapse; width: 100%%; margin: 8pt 0; break-inside: avoid; }
th, td { border: 0.5pt solid #000; padding: 5pt 7pt; vertical-align: top; text-align: left; }
h2#signatures + table td { height: 26pt; }
"""


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def build(md_path: Path, version: str, out_dir: Path, draft: bool) -> dict:
    md, notes = clean(md_path.read_text())
    problems = lint(md)
    if problems and not draft:
        raise SystemExit("REFUSED: fix these before formatting for signature (or pass --draft):\n  "
                         + "\n  ".join(problems))
    title = next((l[2:].strip() for l in md.splitlines() if l.startswith("# ")), md_path.stem)
    label = f"{title} | {version}" + (" | DRAFT, not for signature" if draft else "")
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = re.sub(r"[^A-Za-z0-9]+", "-", f"{title} {version}").strip("-").lower()
    docx, pdf = out_dir / f"{stem}.docx", out_dir / f"{stem}.pdf"
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        clean_md = td / "agreement.md"
        clean_md.write_text(md)
        ref = td / "reference.docx"
        build_reference_docx(ref, label)
        subprocess.run(["pandoc", str(clean_md), "-f", "gfm", "-o", str(docx),
                        f"--reference-doc={ref}"], check=True)
        css = td / "print.css"
        css.write_text(PRINT_CSS % {"label": label.replace('"', "'")})
        page = td / "agreement.html"
        subprocess.run(["pandoc", str(clean_md), "-f", "gfm", "-s", "--embed-resources",
                        f"--css={css}", "--metadata", f"pagetitle={title}", "-o", str(page)], check=True)
        if not Path(CHROME).exists():
            raise SystemExit(f"Chrome not found at {CHROME}; the .docx is built, the PDF is not")
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                        f"--print-to-pdf={pdf}", page.as_uri()], check=True, capture_output=True, timeout=90)
    manifest = {"source": str(md_path), "source_sha256": sha(md_path), "version": version,
                "draft": draft, "lint": problems, "notes": notes,
                "docx": str(docx), "docx_sha256": sha(docx), "pdf": str(pdf), "pdf_sha256": sha(pdf)}
    (out_dir / f"{stem}.manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def self_test() -> None:
    bad = ("# A\n\nBetween X and \\[your business name\\]. Pay TBD.\n\n"
           "| | X | Y |\n| --- | --- | --- |\n| Name | | Zach |\n")
    good = ("# A\n\nBetween X, LLC and Zach Harris. Pay $1,500. See [the NDA](https://example.com).\n\n"
            "- [x] done\n\n| | X | Y |\n| --- | --- | --- |\n| Name | Leah | Zach |\n")
    assert len(lint(clean(bad)[0])) >= 3, lint(clean(bad)[0])
    assert lint(clean(good)[0]) == [], lint(clean(good)[0])
    assert "chip" in clean("# A\n\nNov 6, 2026 · @Zach Harris\n")[1][0]
    assert lint("&#91;Choose one: a / b\\]".replace("&#91;", "[")), "export-escaped choice must lint"
    assert lint("x \u2014 y"), "em dash must lint"
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "a.md"
        p.write_text(good + "\n## 1. Work\n\nSome text.\n")
        m = build(p, "test", Path(td) / "out", draft=False)
        for k in ("docx", "pdf"):
            assert Path(m[k]).stat().st_size > 1000, k
        assert Path(m["pdf"]).read_bytes()[:4] == b"%PDF"
        with zipfile.ZipFile(m["docx"]) as z:
            assert "NUMPAGES" in z.read("word/footer1.xml").decode()
            assert "rIdFtr1" in z.read("word/document.xml").decode()
        p.write_text(bad)
        try:
            build(p, "test", Path(td) / "out2", draft=False)
            raise AssertionError("bad input was not refused")
        except SystemExit as e:
            assert "REFUSED" in str(e)
    print("contract_format self-test: OK (lint fails on bad, passes on good; footer in docx; PDF built; refusal)")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("md", nargs="?")
    ap.add_argument("--version", default="draft")
    ap.add_argument("--out")
    ap.add_argument("--draft", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if not shutil.which("pandoc"):
        raise SystemExit("pandoc not found (brew install pandoc)")
    if a.self_test:
        return self_test()
    if not a.md:
        ap.error("markdown file required")
    p = Path(a.md)
    if a.check:
        probs = lint(clean(p.read_text())[0])
        print("\n".join(probs) if probs else "clean")
        sys.exit(1 if probs else 0)
    m = build(p, a.version, Path(a.out) if a.out else p.parent, a.draft)
    print(json.dumps({k: m[k] for k in ("docx", "pdf", "lint", "notes")}, indent=2))


if __name__ == "__main__":
    main()
