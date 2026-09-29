#!/usr/bin/env python3
"""
tao_coverage_check.py — every NFTT and TIL post should have minted at least one Tao proverb.

Zach 2026-09-27: "have we minted a tao for each NFTT post and TIL post? If not, that's a
mechanical miss." Count on that day: 2 of 37 NFTT posts cited by any proverb, TIL unchecked.
The Tao is lore distilled; a post that produced no proverb either taught nothing (unlikely) or
its lesson evaporated (the cheap-write / expensive-read sink, in essay form).

Mechanical half (this script): which posts have NO proverb citing their slug in the Tao canon
(_CANON/tao-proverbs.jsonl, the single source of truth since the Option A ruling of 2026-09-27;
runtime/tao/proverbs.json is a derived projection and is NOT read here). Judgment half (NOT this script):
minting, via /tao-mint (anti-padding: an honest zero is allowed, but must be DECLARED with a
`<!-- tao-waiver: <reason> -->` marker in the post).

Exempt by shape: report fragments and HUDs (recon-report-*, post-N-brief/exec, *-dossier,
loop-hud) — companion artifacts, not essays.

Usage:
  python3 scripts/tao_coverage_check.py            # coverage report (exit 0)
  python3 scripts/tao_coverage_check.py --staged   # pre-commit: a NEWLY ADDED post must have a
                                                   #   proverb or a tao-waiver marker (exit 1 otherwise)
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUB = ROOT / "public"
EXEMPT = re.compile(r"(recon-report-|post-\d+-(brief|exec)$|-dossier$|^loop-hud$|^index$)")
WAIVER = re.compile(r"<!--\s*tao-waiver:\s*(.+?)\s*-->")


def posts() -> list[tuple[str, str, Path]]:
    out = []
    for p in sorted(PUB.glob("blog-nftt-*.html")):
        slug = p.stem.replace("blog-nftt-", "")
        if not EXEMPT.search(slug):
            out.append(("nftt", slug, p))
    for p in sorted(PUB.glob("*til-*.html")):
        slug = p.stem.replace("blog-", "")
        out.append(("til", slug, p))
    return out


def tao_blob() -> str:
    c = ROOT / "_CANON" / "tao-proverbs.jsonl"
    if not c.exists():
        return ""
    return "\n".join(l.lower() for l in c.read_text(encoding="utf-8").splitlines() if l.strip())


def coverage() -> list[dict]:
    blob = tao_blob()
    rows = []
    for kind, slug, p in posts():
        cited = slug.lower() in blob
        text = p.read_text(encoding="utf-8", errors="replace")
        w = WAIVER.search(text)
        rows.append({"kind": kind, "slug": slug, "cited": cited, "waiver": w.group(1) if w else None})
    return rows


def main(argv: list[str]) -> int:
    rows = coverage()
    if "--staged" in argv:
        added = subprocess.run(["git", "diff", "--cached", "--name-only", "--diff-filter=A"], capture_output=True, text=True, cwd=ROOT).stdout.split()
        added_slugs = {Path(a).stem.replace("blog-nftt-", "").replace("blog-", "") for a in added if a.startswith("public/") and a.endswith(".html")}
        bad = [r for r in rows if r["slug"] in added_slugs and not r["cited"] and not r["waiver"]]
        for r in bad:
            print(f"✖ new post {r['kind']}/{r['slug']} has no Tao proverb citing it and no <!-- tao-waiver: ... --> marker", file=sys.stderr)
        return 1 if bad else 0
    by = {}
    for r in rows:
        by.setdefault(r["kind"], []).append(r)
    for kind, rs in by.items():
        cov = sum(r["cited"] for r in rs); wv = sum(1 for r in rs if r["waiver"] and not r["cited"])
        print(f"{kind.upper()}: {cov}/{len(rs)} posts cited by a proverb · {wv} waived · {len(rs)-cov-wv} MISSING")
        for r in rs:
            if not r["cited"] and not r["waiver"]:
                print(f"   missing  {r['slug']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
