#!/usr/bin/env python3
"""aum_claim_gate: block the Grayscale "$7B as assets under management" phrasing from coming back.

Why (2026-11-16): Zach confirmed the Grayscale $7B is capital taken to private and public markets
across 10 regulated products (a launch figure), never assets under management. The AUM wording
had spread to 391 files (forge resume bundles, public resume pages, specs). The canonical line is
"$7B, 10-product regulated launch". The private resume master already bans the phrase; this gate
does the same for every staged file outside _ARCHIVE/.

  python3 scripts/aum_claim_gate.py --staged      # pre-commit: staged text vs the pattern
  python3 scripts/aum_claim_gate.py --all         # every tracked file outside _ARCHIVE/
  python3 scripts/aum_claim_gate.py --self-test   # proves it fails on a bad line and passes a good one

Exit 0 clean, 1 on a hit. Stdlib only.
"""
from __future__ import annotations

import re
import subprocess
import sys

# Built from parts so this file does not match itself.
PATTERN = re.compile(r"7\s?(?:B|billion)\s+(?:in\s+)?" + "A" + "UM", re.IGNORECASE)
EXEMPT = ("_ARCHIVE/",)
FIX = 'use "$7B, 10-product regulated launch" or "launched $7B across 10 regulated products"'


def git(*args: str) -> bytes:
    return subprocess.run(["git", *args], capture_output=True, check=False).stdout


def hits_in(text: str) -> list[tuple[int, str]]:
    return [(i, line.strip()[:160]) for i, line in enumerate(text.splitlines(), 1) if PATTERN.search(line)]


def scan(paths: list[str], read) -> int:
    bad = 0
    for p in paths:
        if not p or p.startswith(EXEMPT):
            continue
        raw = read(p)
        if b"\0" in raw[:8000]:
            continue  # binary (pdf, png)
        for n, line in hits_in(raw.decode("utf-8", "replace")):
            print(f"✖ aum-claim: {p}:{n}: {line}", file=sys.stderr)
            bad += 1
    if bad:
        print(f"  The Grayscale $7B is a launch figure, not AUM: {FIX}.", file=sys.stderr)
    return 1 if bad else 0


def self_test() -> int:
    bad = "Led GTM for 10 regulated products ($7B " + "AUM)."
    bad2 = "a $7 billion in " + "AUM suite"
    good = "Led GTM for 10 regulated products ($7B launched); $7B, 10-product regulated launch."
    ok = bool(hits_in(bad)) and bool(hits_in(bad2)) and not hits_in(good)
    print("aum_claim_gate self-test:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return self_test()
    if "--staged" in argv:
        paths = git("diff", "--cached", "--name-only", "--diff-filter=ACMR").decode().splitlines()
        return scan(paths, lambda p: git("show", f":{p}"))
    if "--all" in argv:
        paths = git("ls-files").decode().splitlines()
        return scan(paths, lambda p: open(p, "rb").read())
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
