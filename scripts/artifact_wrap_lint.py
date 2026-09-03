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
  MODE 5  container/measure mismatch — the prose is capped at a reading measure (`max-width:
          var(--measure)`), but the layout container (`.wrap`/`.container`/`main`/…) is set MUCH
          wider than that measure, while sibling boxes/tables/notes reset to `max-width:none` and
          fill the container. On desktop the prose then wraps short in a narrow sub-column with a
          fat right gutter, ragged against the full-width boxes beside it. This is INVISIBLE to an
          overflow check (the page does not pan), so it slips every horizontal-scroll test and has
          to be caught by eye — until now. The fix is to make the container's inner width equal the
          measure (set container max-width ≈ measure + horizontal padding), so prose and full-width
          siblings share one column. (Root cause of the 2026-09-03 dossier desktop wrap bug: .wrap
          940px vs --maxw 660px.) Threshold: container more than 120px wider than the measure.

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

# MODE 5 — container/measure mismatch.
# How much wider than the reading measure a layout container may be before the prose
# column reads as a ragged narrow sub-column beside full-width siblings. 120px leaves
# room for horizontal padding + slack (a container whose INNER width equals the measure
# is the goal), while still catching egregious cases like .wrap:940 vs --maxw:660 (Δ280).
MISMATCH_THRESHOLD_PX = 120
# CSS custom-property px/rem definitions: `--maxw: 660px;` / `--measure: 41rem;`
VAR_DEF_RE = re.compile(r"--([\w-]+)\s*:\s*(\d+(?:\.\d+)?)(px|rem)\b", re.IGNORECASE)
# prose caps that reference a measure var: `max-width: var(--maxw)`
VAR_MAXW_RE = re.compile(r"max-width\s*:\s*var\(\s*--([\w-]+)\s*\)", re.IGNORECASE)
# unambiguously-text selectors — a LITERAL max-width here is a prose measure, not a box.
# (Catches the blacksmith `.lede{max-width:660px}` variant the var matcher misses.)
TEXT_SELECTOR_RE = re.compile(
    r"(?:^|[\s,>+~])(?:p|li|blockquote|"
    r"\.(?:lede|lead|subhead|standfirst|dek|deck|prose|copy|sec-sub|subtitle|intro|body-?copy|para)s?)"
    r"(?:[\s.:,>+~\[]|$)",
    re.IGNORECASE,
)
# a prose measure lives in this px band; outside it, a literal cap is a box/rail, not a reading column.
PROSE_BAND_PX = (380, 800)
# a CSS rule block: `selector { body }` (no nested braces in these hand-written files)
CSS_BLOCK_RE = re.compile(r"([^{}]+)\{([^{}]*)\}")
# selectors that name the outer layout container (its max-width is the page column width)
CONTAINER_SELECTOR_RE = re.compile(
    r"(?:^|[\s,>])(?:\.(?:wrap|wrapper|container|page|shell|doc|content|layout|main|inner)\b|main\b|article\b|body\b)",
    re.IGNORECASE,
)
MAXW_LITERAL_RE = re.compile(r"max-width\s*:\s*(\d+(?:\.\d+)?)(px|rem)\b", re.IGNORECASE)


def _to_px(value, unit):
    return float(value) * (16.0 if unit.lower() == "rem" else 1.0)


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


def _line_of(html, offset):
    """1-based line number of a character offset (for clickable findings)."""
    return html.count("\n", 0, offset) + 1


STYLE_BLOCK_RE = re.compile(r"<style\b[^>]*>(.*?)</style\s*>", re.IGNORECASE | re.DOTALL)
CSS_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)


def _strip_css_comments(css):
    """Blank out /* ... */ comments, preserving length+newlines so offsets/lines stay accurate.
    Without this a comment sitting before a rule gets captured as part of the selector."""
    return CSS_COMMENT_RE.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), css)


def _measure_container_mismatch(html):
    """MODE 5 — flag when the layout container is much wider than the prose measure.

    Returns a list of (line_no, mode, message). Only fires when the file BOTH caps prose
    at a measure var (`max-width: var(--x)`) AND defines a container whose max-width is
    more than MISMATCH_THRESHOLD_PX wider than that measure. Units are normalized (rem*16).

    Scans ONLY <style> contents — never inline <script>/JSON, whose `{...}` object braces
    are not CSS and would both mislead the block parser and risk pathological backtracking.
    Offsets are mapped back to the original file so findings stay clickable.
    """
    findings = []

    # Concatenate <style> bodies, remembering each block's start offset in the original file
    # so a match offset can be translated back to a real line number.
    styles = [(m.start(1), _strip_css_comments(m.group(1))) for m in STYLE_BLOCK_RE.finditer(html)]
    if not styles:
        return findings

    var_defs = {}
    prose_measures = {}
    widest = None  # (px, selector, original_offset)

    for base, css in styles:
        for m in VAR_DEF_RE.finditer(css):
            var_defs[m.group(1).lower()] = _to_px(m.group(2), m.group(3))

    used = set()
    for base, css in styles:
        for m in VAR_MAXW_RE.finditer(css):
            used.add(m.group(1).lower())
    prose_measures = {("--" + n): var_defs[n] for n in used if n in var_defs}

    for base, css in styles:
        for m in CSS_BLOCK_RE.finditer(css):
            selector, body = m.group(1), m.group(2)
            lit = MAXW_LITERAL_RE.search(body)
            if not lit:
                continue
            px = _to_px(lit.group(1), lit.group(2))
            # 1b. literal cap on an unambiguous text selector → a prose measure.
            if TEXT_SELECTOR_RE.search(selector) and PROSE_BAND_PX[0] <= px <= PROSE_BAND_PX[1]:
                label = "`%s`" % " ".join(selector.split())[:24]
                if label not in prose_measures or px < prose_measures[label]:
                    prose_measures[label] = px
            # 2. widest layout-container cap.
            if CONTAINER_SELECTOR_RE.search(selector) and (widest is None or px > widest[0]):
                widest = (px, " ".join(selector.split())[:40], base + m.start(2) + lit.start())

    if not prose_measures:
        return findings  # no measure-capped prose → this mode does not apply
    tightest_name = min(prose_measures, key=prose_measures.get)
    measure_px = prose_measures[tightest_name]

    if widest is None:
        return findings  # container has no literal max-width (e.g. fluid) → skip

    container_px, sel, off = widest
    if container_px - measure_px > MISMATCH_THRESHOLD_PX:
        findings.append((
            _line_of(html, off), "measure-mismatch",
            "container `%s` max-width %dpx is %dpx wider than prose measure %s (%dpx); "
            "prose wraps ragged in a narrow sub-column beside full-width siblings on desktop. "
            "Set the container inner width to the measure (max-width ~= %dpx incl. padding)."
            % (sel, int(container_px), int(container_px - measure_px), tightest_name,
               int(measure_px), int(measure_px) + 40),
        ))
    return findings


def lint_file(path):
    """Return a list of (line_no, mode, message) findings for one file."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            html = fh.read()
    except (OSError, UnicodeDecodeError) as e:
        return [(0, "read", "could not read file: %s" % e)]

    findings = []

    # MODE 5 — container/measure mismatch (structural; scans raw CSS)
    findings.extend(_measure_container_mismatch(html))

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
        print("  rule); replace every `max-width:NNch` on text with one shared px --measure; for a", file=sys.stderr)
        print("  measure-mismatch, set the container's inner width to the measure so prose and", file=sys.stderr)
        print("  full-width boxes share one column (see _PATTERNS/arcs-artifact-css-base.css).", file=sys.stderr)
        print("  Then re-sweep 375/790/desktop before publishing.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
