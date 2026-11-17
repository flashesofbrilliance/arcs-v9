#!/usr/bin/env python3
"""resume_claim_gate: block resume claims Zach has corrected from coming back into forge resume bundles.

Why (2026-11-17): the forge resume bundles (_ARTIFACTS/forge-*/resume-*.html and the ATS .txt next to
them) carried three corrected claims across ~120 bundles:
  1. Squat New York "$350M ARR": the client's figure is annual revenue, not ARR (Zach, 2026-11-16).
  2. Unvetted Twill Health wording ("KPI and evaluation frameworks", "killed the third before it
     consumed further engineering time", "API instrumentation ... developer-facing"). The vetted line,
     from the private master, is "Strategy and validation for 3 AI-enabled digital-therapeutics product
     lines; drove go-forward on two of them."
  3. Grayscale $7B as assets under management: a launch figure, never that (scripts/aum_claim_gate.py covers it repo-wide;
     it is repeated here so this gate is the one list for resume claims).
Tags are stripped before matching, so a phrase split across <b> or <span> still hits. Staged PDFs are
read with pdftotext when it is installed: a PDF that missed a re-render after its HTML was fixed is how
13 stale claims survived (2026-11-17).

  python3 scripts/resume_claim_gate.py --staged      # pre-commit: staged forge resume files
  python3 scripts/resume_claim_gate.py --all         # every tracked forge resume html/txt (--pdfs adds PDFs)
  python3 scripts/resume_claim_gate.py --self-test   # proves it fails on a bad fixture and passes a good one
  python3 scripts/resume_claim_gate.py FILE...       # explicit files

Exit 0 clean, 1 on a hit. Stdlib only.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys

SCOPE = re.compile(r"^_ARTIFACTS/forge-[^/]+/resume-[^/]*\.(?:html|txt|pdf)$")
PDFTOTEXT = shutil.which("pdftotext")

# (pattern, fix). Built from parts where needed so this file does not match the AUM gate.
RULES: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\$\s?350\s?M[\s-]+ARR\b", re.I),
     'Squat is "$350M annual revenue" or "a company with $350M in annual revenue", never ARR'),
    (re.compile(r"KPI and evaluation frameworks", re.I),
     'Twill: "strategy and validation for 3 AI-enabled digital-therapeutics product lines; drove go-forward on two of them"'),
    (re.compile(r"kill(?:ed|ing)?\s+(?:the third|1 of 3|one product|ideas before)", re.I),
     "Twill: drop the kill claim; say it drove go-forward on two of three"),
    (re.compile(r"API instrumentation", re.I),
     "Twill: unvetted; use the vetted master line"),
    (re.compile(r"developer-facing\s+(?:product lines|integrations)", re.I),
     "Twill: unvetted; use the vetted master line"),
    # Round 2 (Zach, 2026-11-17): the unflagged Twill variants are normalized too. Clause-scoped
    # ([^.;:]) so a fit-row label that echoes the posting ("SQL-driven data foundation and
    # instrumentation:") does not trip it; only the claim after the colon is judged.
    (re.compile(r"KPI frameworks informed", re.I),
     'Twill: "strategy and validation for 3 AI-enabled digital-therapeutics product lines; drove go-forward on two of them"'),
    (re.compile(r"(?:evaluation frameworks|quality loops|KPI frameworks|HIPAA-compliant)[^.;:]{0,90}\bat Twill\b", re.I),
     "Twill: unvetted build claim; say \"ran strategy and validation for 3 AI-enabled digital-therapeutics product lines at Twill Health\""),
    (re.compile(r"Twill Health\s*\([^)]*\):[^.;]{0,160}(?:KPI|instrumentation|framework|stopped the third|no-go on the third)", re.I),
     "Twill: the experience bullet is the vetted master line only"),
    (re.compile(r"7\s?(?:B|billion)\s+(?:in\s+)?" + "A" + "UM", re.I),
     'Grayscale: "$7B, 10-product regulated launch", never AUM'),
]


def git(*args: str) -> bytes:
    return subprocess.run(["git", *args], capture_output=True, check=False).stdout


def flat(text: str) -> str:
    """Strip tags and entities, collapse whitespace, so split phrases still match."""
    text = re.sub(r"<style[\s\S]*?</style>", " ", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"&[a-z]+;|&#\d+;", " ", text)
    return re.sub(r"\s+", " ", text)


def hits_in(text: str) -> list[tuple[str, str]]:
    t = flat(text)
    out = []
    for pat, fix in RULES:
        for m in pat.finditer(t):
            out.append((t[max(0, m.start() - 50):m.end() + 30].strip(), fix))
    return out


def scan(paths: list[str], read, pdfs: bool = False) -> int:
    bad = 0
    for p in paths:
        if not SCOPE.match(p):
            continue
        raw = read(p)
        if p.endswith(".pdf"):
            if not pdfs or not PDFTOTEXT:
                continue
            raw = subprocess.run([PDFTOTEXT, "-", "-"], input=raw, capture_output=True, check=False).stdout
        for snippet, fix in hits_in(raw.decode("utf-8", "replace")):
            print(f"✖ resume-claim: {p}: ...{snippet}...\n    fix: {fix}", file=sys.stderr)
            bad += 1
    if bad:
        print(f"  {bad} corrected resume claim(s). Fix the HTML, then re-render the PDF and ATS text.", file=sys.stderr)
    return 1 if bad else 0


def self_test() -> int:
    bad = [
        '<li>Squat New York (behavioral health, <span class="metric">$350M ARR</span>, post-PE)</li>',
        "inside a $350M-ARR behavioral health company",
        "<li>Twill Health (HIPAA): designed the <b>KPI and evaluation</b> frameworks that drove go/no-go</li>",
        "drove go-forward on 2 of 3 and killed the third before it consumed further engineering time",
        "defined API instrumentation and success metrics for developer-facing integrations",
        "Grayscale ($7B " + "AUM)",
        "Twill Health (HIPAA digital health, 2021 to 2023): market-viability testing for 3 product lines; the KPI frameworks informed go-forward decisions on 2 of 3.",
        "built evaluation frameworks and quality loops for 3 AI-enabled product lines at Twill Health",
        "Twill Health (HIPAA): researched three lines, recommended two, and stopped the third before it consumed engineering time.",
    ]
    good = [
        '<li>Squat New York (behavioral health, <span class="metric">$350M annual revenue</span>, post-PE)</li>',
        "inside a behavioral health company with $350M in annual revenue",
        "<li>Twill Health (HIPAA digital health, 2021 to 2023): strategy and validation for 3 AI-enabled "
        "digital-therapeutics product lines; drove go-forward on two of them.</li>",
        "the same motion as building APIs and developer-facing interfaces",
        "SQL-driven data foundation and instrumentation: ran strategy and validation for 3 AI-enabled digital-therapeutics product lines at Twill Health",
        "built evaluation frameworks and outcome-capture loops for AI-enabled product lines at ARCS",
        "Grayscale ($7B launched); $7B, 10-product regulated launch",
    ]
    misses = [b for b in bad if not hits_in(b)]
    false_hits = [g for g in good if hits_in(g)]
    scoped = bool(SCOPE.match("_ARTIFACTS/forge-x/resume-x.html")) and not SCOPE.match("_ARTIFACTS/forge-x/page.html")
    ok = not misses and not false_hits and scoped
    for m in misses:
        print("  missed bad:", m)
    for g in false_hits:
        print("  flagged good:", g)
    print("resume_claim_gate self-test:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return self_test()
    if "--staged" in argv:
        paths = git("diff", "--cached", "--name-only", "--diff-filter=ACMR").decode().splitlines()
        return scan(paths, lambda p: git("show", f":{p}"), pdfs=True)
    if "--all" in argv:
        paths = git("ls-files", "_ARTIFACTS").decode().splitlines()
        return scan(paths, lambda p: open(p, "rb").read(), pdfs="--pdfs" in argv)
    files = [a for a in argv if not a.startswith("--")]
    if files:
        return scan(files, lambda p: open(p, "rb").read(), pdfs=True)
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
