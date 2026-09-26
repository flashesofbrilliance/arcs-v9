#!/usr/bin/env python3
"""case_evidence_lint: every number in a playable case must trace to a published source, verbatim.

Why a second gate: provenance_lint strips <script> and only matches money/percent/latency/"N+"
shapes, so on a case page it sees none of the facts (they live in the game's data as decimals
and counts). Measured 2026-09-26: it found only the HUD label "Over 0" on both cases. A ledger
that merely satisfied it would read as verified while checking nothing (control described, not
wired).

Corpus scanned per page:
  1. visible text (tags stripped; the shared case-world runtime excluded)
  2. the game's data region: from "(function () {" to the first "var over" line
  3. every double-quoted string literal in the rest of the page script
Every digit run in that corpus must sit inside a matched ledger entry, by POSITION, so a fact
cannot hide behind a mechanic that happens to share a digit ("2 of 247" vs "Chair 2 of 3").

Ledger: sibling <page-stem>.evidence.jsonl (the same file provenance_lint reads). Each line:
  {"pattern": <regex for provenance_lint>, "kind": "fact"|"mechanic", "page": <exact text on page>,
   "source": <repo path of the published post>, "quote": <verbatim text in that post>, "note": ...}
  fact     -> "page" must occur in the corpus AND "quote" must occur in the source's text
              (whitespace/quote-normalized). A missing quote fails: the source changed or the
              fact was never there.
  mechanic -> "page" must occur; "why" says what game rule it is. No source needed.

Usage: python3 scripts/case_evidence_lint.py [page.html ...]   (default: case-world pages + any page with a ledger)
       exit 1 on any uncovered number, missing page string, or unverifiable quote. Stdlib only.
"""
import glob, html, json, os, re, sys

NUM = re.compile(r"(?<![A-Za-z0-9.])\d+(?:\.\d+)?(?![A-Za-z0-9])")


def norm(s):
    s = html.unescape(s)
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", s).strip()


def text_of(markup):
    markup = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", markup)
    return norm(re.sub(r"<[^>]+>", " ", markup))


def corpus(page_html):
    body = page_html.split("</style>", 1)[1]
    body = re.sub(r"(?s)<!-- case-world:runtime:begin -->.*?<!-- case-world:runtime:end -->", " ", body)
    scripts = re.findall(r"(?s)<script>(.*?)</script>", body)
    parts = [text_of(body)]
    for s in scripts:
        a = s.find("(function () {")
        b = s.find("var over")
        if a >= 0 and b > a:
            parts.append(norm(s[a:b]))
            rest = s[b:]
        else:
            rest = s
        parts += [norm(x) for x in re.findall(r'"((?:[^"\\]|\\.)*)"', rest)]
    return "\n".join(parts)


def ledger_for(page):
    return os.path.splitext(page)[0] + ".evidence.jsonl"


def lint(page):
    errs = []
    lp = ledger_for(page)
    if not os.path.exists(lp):
        return [f"no ledger at {lp}"]
    text = corpus(open(page, encoding="utf-8").read())
    covered = [False] * len(text)
    sources = {}
    for n, ln in enumerate(open(lp, encoding="utf-8"), 1):
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        e = json.loads(ln)
        want = norm(e["page"])
        hits = [m.start() for m in re.finditer(re.escape(want), text)]
        if not hits:
            errs.append(f"ledger line {n}: page text {want!r} not found on the page (stale entry)")
            continue
        for h in hits:
            for k in range(h, h + len(want)):
                covered[k] = True
        if e.get("kind") == "fact":
            src = e.get("source", "")
            if not os.path.exists(src):
                errs.append(f"ledger line {n}: source {src!r} does not exist")
                continue
            if src not in sources:
                sources[src] = text_of(open(src, encoding="utf-8").read())
            if norm(e.get("quote", "")) not in sources[src]:
                errs.append(f"ledger line {n}: quote {e.get('quote')!r} not found in {src}")
        elif e.get("kind") != "mechanic":
            errs.append(f"ledger line {n}: kind must be 'fact' or 'mechanic'")
    for m in NUM.finditer(text):
        if not all(covered[m.start():m.end()]):
            lo = max(0, m.start() - 30)
            errs.append(f"uncovered number {m.group(0)!r} in: ...{text[lo:m.end() + 30]}...")
    return errs


def main(argv):
    pages = argv or sorted(p for p in glob.glob("public/*.html")
                           if "case-world:" in open(p, encoding="utf-8").read()
                           or os.path.exists(ledger_for(p)))
    bad = 0
    for p in pages:
        errs = lint(p)
        if errs:
            bad += 1
            print(f"✖ case-evidence: {p}")
            for e in errs:
                print(f"   {e}")
        else:
            print(f"✓ case-evidence: {p} every number traces to a ledger entry; every quote verified in its source")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
