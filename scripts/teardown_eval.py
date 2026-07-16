#!/usr/bin/env python3
"""
teardown_eval.py - deterministic gate harness for /teardown and /precall-brief artifacts.

Grades an ALREADY-PRODUCED artifact HTML file. Does not run the LLM itself - this is a
static-analysis linter + fixture-mode fact-checker, run as the last step before an artifact
is called final (see .claude/commands/teardown.md Step 4).

Honesty note (read before trusting a PASS): several of the checks below are hard,
deterministic gates - regex/string matching that either finds a violation or doesn't, same
result every run. A few (sycophancy density) are heuristic PROXIES for a semantic judgment
this script cannot actually make - they are reported as scores/warnings, not hard failures,
and are clearly labeled as such in the output. True hallucination and true sycophancy
detection require a semantic judge (an LLM), which is not deterministic across runs/models -
this script does not attempt that. What it CAN do deterministically: check that every claim
carries a citation, that cited sources actually contain what's claimed (in fixture mode,
against known ground truth), that high-stakes claims have more than one independent source,
and that a fixed set of style/process rules are followed.

Citation convention this script expects artifacts to use (retrofit into any HTML the skill
produces):

    <span class="claim" data-src="https://example.com/page" data-stakes="normal">
      claim text, or a "verbatim quote"
    </span>

- data-src: one or more source URLs/identifiers, comma-separated if the claim is
  cross-referenced against multiple independent sources.
- data-stakes="high": claims where being wrong matters more (pricing, funding, liability
  claims, anything used to argue a gap exists) - these require >=2 distinct data-src values.

Usage:
    python3 scripts/teardown_eval.py <artifact.html>
    python3 scripts/teardown_eval.py <artifact.html> --fixtures tests/fixtures/teardown-eval
    python3 scripts/teardown_eval.py <artifact.html> --fixtures ... --json

Exit code 0 = all hard gates passed. Exit code 1 = at least one hard gate failed.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Optional

EM_DASH = "—"

PROCESS_NARRATION_PHRASES = [
    "correction from an earlier pass",
    "correcting my own",
    "an earlier draft",
    "earlier pass on",
    "the way i just checked",
    "i originally wrote",
    "in my first draft",
    "my earlier guess",
    "my earlier claim",
]

GAUNTLET_LENSES = ["BAR", "LAB", "KKL", "COURT", "Funhouse"]

SYCOPHANCY_WORDS = [
    "unusually good", "genuinely credible", "genuinely impressive", "impressive",
    "amazing", "brilliant", "exceptional", "incredible", "outstanding", "phenomenal",
    "stellar", "world-class", "game-changing", "revolutionary", "groundbreaking",
    "unparalleled", "best-in-class", "truly remarkable",
]

# Match the full opening <span ...> tag (attribute order-independent) plus its inner
# content up to the closing </span>. Attributes are then extracted independently from the
# captured tag blob - avoids the classic bug where a greedy [^>]* before an optional
# attribute group swallows the whole tag and leaves the optional group empty.
CLAIM_SPAN_RE = re.compile(
    r'<span\s+([^>]*class="claim"[^>]*)>(.*?)</span>',
    re.IGNORECASE | re.DOTALL,
)
DATA_SRC_RE = re.compile(r'data-src="([^"]*)"', re.IGNORECASE)
DATA_STAKES_RE = re.compile(r'data-stakes="([^"]*)"', re.IGNORECASE)

MONEY_RE = re.compile(r'\$\d[\d,]*(?:\.\d+)?(?:/mo|/month|/yr|/year|[kKmMbB]\+?)?')
QUOTED_RE = re.compile(r'"([^"]{6,})"')


def strip_tags(html: str) -> str:
    return re.sub(r"<[^>]+>", " ", html)


def find_claims(html: str):
    """Returns list of dicts: {sources: [...], stakes: str, text: str (tags stripped)}."""
    claims = []
    for m in CLAIM_SPAN_RE.finditer(html):
        tag_attrs, inner = m.group(1), m.group(2)
        src_m = DATA_SRC_RE.search(tag_attrs)
        stakes_m = DATA_STAKES_RE.search(tag_attrs)
        src = src_m.group(1) if src_m else ""
        stakes = (stakes_m.group(1).strip() if stakes_m else "") or "normal"
        claims.append({
            "sources": [s.strip() for s in src.split(",") if s.strip()],
            "stakes": stakes,
            "text": strip_tags(inner).strip(),
        })
    return claims


def gate_em_dash(html: str):
    count = html.count(EM_DASH)
    return {
        "gate": "em_dash",
        "hard": True,
        "passed": count == 0,
        "detail": f"{count} em-dash(es) found" if count else "clean",
    }


def gate_ch_width(html: str):
    hits = re.findall(r"max-width:\s*\d+ch", html, re.IGNORECASE)
    return {
        "gate": "ch_width_cap",
        "hard": True,
        "passed": len(hits) == 0,
        "detail": f"{len(hits)} ch-width cap(s) found: {hits}" if hits else "clean",
    }


def gate_text_balance(html: str):
    hits = re.findall(r"text-wrap:\s*balance", html, re.IGNORECASE)
    return {
        "gate": "text_wrap_balance",
        "hard": True,
        "passed": len(hits) == 0,
        "detail": f"{len(hits)} instance(s) found" if hits else "clean",
    }


def gate_process_narration(html: str):
    text = strip_tags(html).lower()
    hits = [p for p in PROCESS_NARRATION_PHRASES if p in text]
    return {
        "gate": "process_narration",
        "hard": True,
        "passed": len(hits) == 0,
        "detail": f"found: {hits}" if hits else "clean",
    }


def gate_gauntlet_presence(html: str, gauntlet_report_path: Optional[Path]):
    """Per Funhouse discipline, the gauntlet report is NOT supposed to live inside the
    customer-facing artifact (see .claude/commands/teardown.md Step 4) - narrating the
    audit process at the reader is exactly what Funhouse flags. So this checks a SEPARATE
    report file, not the artifact HTML itself. No report file provided = can't verify the
    gauntlet ran at all, which is its own real finding, not a false requirement on the page."""
    if gauntlet_report_path is None:
        return {
            "gate": "gauntlet_lenses_present",
            "hard": True,
            "passed": False,
            "detail": "no --gauntlet-report provided - cannot verify BAR/LAB/KKL/COURT/Funhouse "
                      "were actually run (this checks a companion report file, not the shipped "
                      "artifact - the gauntlet report belongs off the customer-facing page)",
        }
    if not gauntlet_report_path.exists():
        return {
            "gate": "gauntlet_lenses_present",
            "hard": True,
            "passed": False,
            "detail": f"--gauntlet-report {gauntlet_report_path} does not exist",
        }
    text = gauntlet_report_path.read_text()
    missing = [lens for lens in GAUNTLET_LENSES if not re.search(r"\b" + re.escape(lens) + r"\b", text)]
    return {
        "gate": "gauntlet_lenses_present",
        "hard": True,
        "passed": len(missing) == 0,
        "detail": f"missing from {gauntlet_report_path.name}: {missing}" if missing else
                  f"all 5 lenses present in {gauntlet_report_path.name}",
    }


def gate_sycophancy_density(html: str):
    text = strip_tags(html).lower()
    word_count = max(len(text.split()), 1)
    hits = []
    for w in SYCOPHANCY_WORDS:
        n = text.count(w)
        if n:
            hits.extend([w] * n)
    density_per_1000 = round(1000 * len(hits) / word_count, 2)
    # heuristic proxy only - never a hard gate
    return {
        "gate": "sycophancy_density_heuristic",
        "hard": False,
        "passed": density_per_1000 < 3.0,
        "detail": f"{len(hits)} superlative hit(s), {density_per_1000}/1000 words: {hits[:10]}",
    }


def gate_claims_exist(claims):
    return {
        "gate": "claims_present",
        "hard": True,
        "passed": len(claims) > 0,
        "detail": f"{len(claims)} cited claim(s) found" if claims else
                   "0 citation spans found - artifact is not using the citation convention, "
                   "cannot verify anything below this gate",
    }


def gate_high_stakes_cross_referenced(claims):
    bad = [c for c in claims if c["stakes"] == "high" and len(set(c["sources"])) < 2]
    return {
        "gate": "high_stakes_cross_referenced",
        "hard": True,
        "passed": len(bad) == 0,
        "detail": (f"{len(bad)} high-stakes claim(s) with fewer than 2 independent sources: "
                   + "; ".join(c["text"][:60] for c in bad)) if bad else
                  "all high-stakes claims have >=2 independent sources",
    }


def load_fixture_sources(fixtures_dir: Path):
    sources_json = fixtures_dir / "sources.json"
    if not sources_json.exists():
        return None
    raw = json.loads(sources_json.read_text())
    out = {}
    for src_id, meta in raw.items():
        if src_id.startswith("_"):
            continue
        fpath = fixtures_dir / meta["file"]
        content = strip_tags(fpath.read_text()) if fpath.exists() else ""
        out[src_id] = {**meta, "content": content, "content_lower": content.lower()}
    return out


def gate_fact_check(claims, fixture_sources):
    """For each claim citing a known fixture source, verify money-amounts and quoted
    strings in the claim actually appear in that source's real content. Flags the
    homepage-only trap (fact only present on a deeper page, but cited to the homepage)
    and the unreliable-secondary-source trap (fact only present in the simulated
    WebSearch summary, nowhere in a real page)."""
    if fixture_sources is None:
        return {"gate": "fact_check", "hard": True, "passed": True,
                "detail": "SKIPPED - no --fixtures dir provided"}

    all_source_text = " ".join(s["content_lower"] for s in fixture_sources.values())
    failures = []

    for c in claims:
        tokens = set(m.group(0) for m in MONEY_RE.finditer(c["text"]))
        tokens |= set(m.group(1) for m in QUOTED_RE.finditer(c["text"]))
        if not tokens:
            continue

        cited_srcs = {sid: fixture_sources.get(sid) for sid in c["sources"]}
        for sid, src in cited_srcs.items():
            if src is None:
                failures.append(f"cites unknown source '{sid}' for claim: {c['text'][:60]}")

        known_cited = {sid: s for sid, s in cited_srcs.items() if s is not None}
        if not known_cited:
            continue

        for tok in tokens:
            tok_l = tok.lower()
            # cross-reference semantics: a token is verified if it appears in ANY of the
            # claim's cited sources (each source may back a different part of the claim)
            verified_in = [sid for sid, s in known_cited.items() if tok_l in s["content_lower"]]
            if verified_in:
                continue

            # not verified against any cited source - is it findable elsewhere, or nowhere?
            found_elsewhere = [
                sid for sid, s in fixture_sources.items()
                if sid not in known_cited and tok_l in s["content_lower"]
            ]
            any_cited_is_homepage = any(s.get("is_homepage") for s in known_cited.values())
            if any_cited_is_homepage and found_elsewhere:
                failures.append(
                    f"HOMEPAGE-ONLY TRAP: claim '{tok}' cited to {list(known_cited)} (incl. "
                    f"homepage) but only actually present on: {found_elsewhere} - "
                    f"claim: {c['text'][:60]}"
                )
            elif tok_l in all_source_text:
                real_src = [sid for sid, s in fixture_sources.items() if tok_l in s["content_lower"]]
                failures.append(
                    f"WRONG SOURCE: claim '{tok}' cited to {list(known_cited)} but none of "
                    f"those contain it - actually found in {real_src} - claim: {c['text'][:60]}"
                )
            else:
                failures.append(
                    f"UNVERIFIABLE: claim '{tok}' (cited to {list(known_cited)}) does not "
                    f"appear in ANY known real source - possible hallucination or reliance on "
                    f"an unreliable secondary source - claim: {c['text'][:60]}"
                )

    return {
        "gate": "fact_check",
        "hard": True,
        "passed": len(failures) == 0,
        "detail": ("clean - every cited money/quote token verified against its source"
                   if not failures else "\n    - " + "\n    - ".join(failures)),
    }


def run(artifact_path: Path, fixtures_dir: Optional[Path], gauntlet_report: Optional[Path]):
    html = artifact_path.read_text()
    claims = find_claims(html)
    fixture_sources = load_fixture_sources(fixtures_dir) if fixtures_dir else None

    results = [
        gate_em_dash(html),
        gate_ch_width(html),
        gate_text_balance(html),
        gate_process_narration(html),
        gate_gauntlet_presence(html, gauntlet_report),
        gate_claims_exist(claims),
        gate_high_stakes_cross_referenced(claims),
        gate_fact_check(claims, fixture_sources),
        gate_sycophancy_density(html),
    ]
    return results


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("artifact", type=Path, help="HTML artifact to grade")
    ap.add_argument("--fixtures", type=Path, default=None,
                     help="fixture dir (with sources.json) for fact-check mode")
    ap.add_argument("--gauntlet-report", type=Path, default=None,
                     help="companion file (e.g. a scratch .md note) containing the BAR/LAB/"
                          "KKL/COURT/Funhouse writeup - kept OFF the shipped artifact per "
                          "Funhouse discipline, so this is checked separately")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()

    if not args.artifact.exists():
        print(f"error: {args.artifact} not found", file=sys.stderr)
        sys.exit(2)

    results = run(args.artifact, args.fixtures, args.gauntlet_report)
    hard_failures = [r for r in results if r["hard"] and not r["passed"]]

    if args.json:
        print(json.dumps({"results": results, "exit": 1 if hard_failures else 0}, indent=2))
    else:
        print(f"\nteardown_eval: {args.artifact}")
        if args.fixtures:
            print(f"  fixtures: {args.fixtures}")
        print()
        for r in results:
            tag = "HARD" if r["hard"] else "soft"
            status = "PASS" if r["passed"] else "FAIL"
            marker = "✓" if r["passed"] else "✗"
            print(f"  [{marker}] {status:4} ({tag}) {r['gate']}")
            print(f"        {r['detail']}")
        print()
        if hard_failures:
            print(f"RESULT: FAIL - {len(hard_failures)} hard gate(s) failed. Do not ship.")
        else:
            print("RESULT: PASS - all hard gates clear. (Soft/heuristic gates are informational - read them anyway.)")

    sys.exit(1 if hard_failures else 0)


if __name__ == "__main__":
    main()
