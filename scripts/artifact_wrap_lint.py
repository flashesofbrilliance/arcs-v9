#!/usr/bin/env python3
"""artifact_wrap_lint.py — pre-publish gate for the intermediate-width wrap-regression class.

WHY: the "text wrapping bug" keeps recurring on self-contained ARCS artifacts because each one
re-authors CSS from scratch and re-introduces the same root causes. Prose in memory and a copy-in
template (_PATTERNS/arcs-artifact-css-base.css) did not stop it — a memory only STOPS being tuition
when it can stop YOU. This is that stop: a mechanical gate that fails the two modes you can grep.

It checks the two failure modes named in the taxonomy (memories:
text-wrapping-bug-four-failure-modes-rca, intermediate-width-wrap-regression-class):

  MODE 1  em-dash in rendered copy  — a space-padded U+2014 lands at a line break and reads as a
          broken wrap (also Zach's standing no-em-dash writing rule). Checked against VISIBLE text
          only: <style>, <script>, and HTML comments are excluded.
  MODE 4  per-role `max-width: NNch` on text — a literal ch cap. `ch` computed against mixed font
          sizes gives every text role a different right edge; the misaligned rag reads as broken
          wrapping. The fix is ONE shared px measure. `max-width: var(--measure-narrow)` and a
          `--measure-narrow: 34ch` VAR DEFINITION are both allowed (only literal caps on max-width
          are flagged).

Modes 2 (split accent clause) and 3 (split bold fragment) need rendered-line-break inspection, not
a grep — they stay a manual pass (screenshot-sweep at ~790px). This gate covers what is mechanical.

USAGE
  python3 scripts/artifact_wrap_lint.py <file.html> [<file2.html> ...]
  exit 0 = clean · exit 1 = at least one violation (per-file findings printed to stderr)

Stdlib only. Safe to run in a git hook.
"""
import re
import sys

MDASH_CHARS = ("—",)                    # — literal
MDASH_ENTITIES = ("&mdash;", "&#8212;", "&#x2014;", "&#X2014;")
CH_CAP_RE = re.compile(r"max-width\s*:\s*\d+(?:\.\d+)?ch", re.IGNORECASE)
COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
TAG_RE = re.compile(r"<[^>]+>")


def _visible_text_lines(html):
    """Yield (line_no, visible_text) with <style>/<script>/comments removed.

    Block state is tracked across lines so multi-line style/script bodies are fully excluded.
    Line numbers refer to the ORIGINAL file so findings are clickable.
    """
    # strip HTML comments globally first (they can span lines), keeping newline count stable
    def _blank(m):
        return re.sub(r"[^\n]", " ", m.group(0))
    html = COMMENT_RE.sub(_blank, html)

    in_block = None  # 'style' | 'script' | None
    for i, raw in enumerate(html.split("\n"), start=1):
        line = raw
        out = []
        while line:
            if in_block:
                close = re.search(r"</\s*%s\s*>" % in_block, line, re.IGNORECASE)
                if not close:
                    line = ""
                    break
                line = line[close.end():]
                in_block = None
            else:
                opn = re.search(r"<\s*(style|script)\b[^>]*>", line, re.IGNORECASE)
                if not opn:
                    out.append(line)
                    line = ""
                    break
                out.append(line[:opn.start()])
                in_block = opn.group(1).lower()
                line = line[opn.end():]
        text = TAG_RE.sub("", "".join(out))
        yield i, text


def lint_file(path):
    """Return a list of (line_no, mode, message) findings for one file."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            html = fh.read()
    except (OSError, UnicodeDecodeError) as e:
        return [(0, "read", "could not read file: %s" % e)]

    findings = []

    # MODE 4 — literal ch caps on max-width (scan raw lines; these live in <style>)
    for i, raw in enumerate(html.split("\n"), start=1):
        for m in CH_CAP_RE.finditer(raw):
            findings.append((i, "ch-cap", "per-role ch cap `%s` — use one shared px --measure instead" % m.group(0)))

    # MODE 1 — em-dash in rendered copy only
    for line_no, text in _visible_text_lines(html):
        hay = text
        for ent in MDASH_ENTITIES:
            hay = hay.replace(ent, "—")
        if any(c in hay for c in MDASH_CHARS):
            snippet = re.sub(r"\s+", " ", text).strip()
            if len(snippet) > 90:
                idx = snippet.find("—")
                snippet = "..." + snippet[max(0, idx - 40):idx + 45] + "..."
            findings.append((line_no, "em-dash", "em-dash in rendered copy: “%s”" % snippet))

    findings.sort(key=lambda f: (f[0], f[1]))
    return findings


def main(argv):
    paths = argv[1:]
    if not paths or paths[0] in ("-h", "--help"):
        print(__doc__)
        return 0 if paths else 2

    total = 0
    for path in paths:
        if not path.lower().endswith((".html", ".htm")):
            print("· wrap-lint: %s skipped (not an .html artifact)" % path)
            continue
        findings = lint_file(path)
        if not findings:
            print("✓ wrap-lint: %s clean" % path)
            continue
        total += len(findings)
        print("✗ wrap-lint: %s — %d issue(s)" % (path, len(findings)), file=sys.stderr)
        for line_no, mode, msg in findings:
            loc = "%s:%d" % (path, line_no) if line_no else path
            print("    [%s] %s  %s" % (mode, loc, msg), file=sys.stderr)

    if total:
        print("", file=sys.stderr)
        print("✗ %d wrap-class violation(s). Fixes: remove em-dashes (also the no-em-dash writing" % total, file=sys.stderr)
        print("  rule); replace every `max-width:NNch` on text with one shared px --measure (see", file=sys.stderr)
        print("  _PATTERNS/arcs-artifact-css-base.css). Then re-sweep 375/790/desktop before publishing.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
