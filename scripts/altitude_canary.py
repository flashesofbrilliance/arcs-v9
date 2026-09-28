#!/usr/bin/env python3
"""
altitude_canary.py — the canary in the coal mine for ALTITUDE SICKNESS in prose.

The tell (2026-09-27): the prose gets fluent and confident while the ground return goes quiet.
Radar-altimeter reading of a document: per section, how many confidence markers per ground
return. A section that is long, assertive, and cites NOTHING is "NO GROUND RETURN" — on an
aircraft that is the alarm that matters most.

Composes, never duplicates:
  ground returns  = the cite classes integrity_gate.py already extracts (ADR-NNN, commit shas,
                    repo paths, bare script names) + URLs + receipt ids + [[memory-links]]
                    (existence is integrity_gate's job; the canary only asks "is anything cited?")
  confidence      = assertive markers (clearly / always / proves / guarantees / the only / must /
                    exactly / undeniably ...) + bare quantified claims (N% / Nx / $N) — the class
                    provenance_lint gates on enrolled surfaces
  fluency         = words per sentence (long, smooth sentences with no anchors read as altitude)

Verdict per section:
  GROUNDED     ground returns >= 1 per ~120 words, or confidence low
  THIN AIR     confidence markers present, ground returns sparse (ratio > 2)
  NO GROUND RETURN   >= MIN_WORDS words, >= 2 confidence markers, 0 ground returns  (the canary drops)

Exit: 0 by default (advisory smoke test); --strict exits 1 on any NO GROUND RETURN.
Scope: prose files (.md/.txt). Code, JSON, JSONL are skipped. Fenced code blocks are stripped.
Pairing: the canary asks "is ANYTHING cited?"; integrity_gate.py asks "does what is cited EXIST?".
The 2026-09-27 Perplexity audit read only THIN AIR here (its tables cite plausible paths) and
FAILED integrity_gate (the paths were vapor). Altitude sickness has both symptoms; run both.

Usage:
  python3 scripts/altitude_canary.py <file.md> [...]         # report
  python3 scripts/altitude_canary.py --staged [--strict]     # pre-commit: staged .md under prose roots
  python3 scripts/altitude_canary.py --json <file>
  python3 scripts/altitude_canary.py --self-test
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# Records, not narrative: ADRs, handoffs, audits, seeds, specs. _CANON/ and WORLD.md are the
# world-building register and are uncited BY DESIGN (a manifesto cites nothing); they trip the
# canary honestly and are excluded from the staged scope, not from explicit runs.
PROSE_ROOTS = ("_DECISIONS/", "_STATE/", "_SEEDS/", "_PATTERNS/", "_SPECS/", "runtime/specs/", "AGENTS.md", "CLAUDE.md")
MIN_WORDS = 120

CONFIDENCE_RE = re.compile(
    r"\b(clearly|obviously|undeniably|certainly|definitively|unquestionably|always|never|guarantees?|"
    r"proves?|proven|the only (way|answer|option)|the (right|correct) (answer|way)|of course|no doubt|"
    r"it is (clear|obvious|certain)|must\b|will (always|never)|cannot fail|fully (production|proven)|"
    r"full production|production[- ]ready|battle[- ]tested|exactly|precisely)\b",
    re.I,
)
QUANT_RE = re.compile(r"(?<![\w.])(\$\s?\d[\d,.]*\s?[kmb]?|\d{1,3}(?:\.\d+)?\s?%|\d+(?:\.\d+)?x\b|\b\d{2,}\+)", re.I)
URL_RE = re.compile(r"https?://[^\s)>\]]+")
RECEIPT_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}--[a-z0-9-]+--[A-Z]{2}\b|\bOPR-\d{8}T\d{6}Z-[0-9a-f]{8}\b|\btao-\d{3}\b|\bF\d{1,3}\b(?=[\s,.)])")
MEMLINK_RE = re.compile(r"\[\[[a-z0-9-]+\]\]")
FENCE_RE = re.compile(r"```.*?```", re.S)
HEADING_RE = re.compile(r"^#{1,6}\s+.*$", re.M)
SENT_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z\"'(])")


def _load_integrity_extract():
    """Import integrity_gate.extract without running its main; fall back to a local regex set."""
    spec = importlib.util.spec_from_file_location("integrity_gate", ROOT / "scripts" / "integrity_gate.py")
    try:
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        return mod.extract
    except Exception:
        adr = re.compile(r"\bADR-0*(\d{1,3})\b"); sha = re.compile(r"(?<![0-9A-Za-z_/.-])([0-9a-f]{7,40})(?![0-9A-Za-z_/-])")
        path = re.compile(r"(?<![\w/.-])((?:_DECISIONS|_STATE|_SEEDS|_CANON|scripts|operators|runtime|src|public)/[\w./\[\]@+-]+)")
        bare = re.compile(r"(?<![\w/.-])([A-Za-z][\w-]*\.(?:py|sh|ts|tsx|mjs))(?![\w/-])")
        return lambda t: (set(adr.findall(t)), set(sha.findall(t)), set(path.findall(t)), set(bare.findall(t)))


EXTRACT = _load_integrity_extract()


def sections(text: str) -> list[tuple[str, str]]:
    """Split on markdown headings; heading-less files are one section. Fenced code removed."""
    text = FENCE_RE.sub("", text)
    out: list[tuple[str, str]] = []
    pos = 0
    title = "(preamble)"
    for m in HEADING_RE.finditer(text):
        body = text[pos:m.start()].strip()
        if body:
            out.append((title, body))
        title = m.group(0).lstrip("# ").strip()
        pos = m.end()
    body = text[pos:].strip()
    if body:
        out.append((title, body))
    return out or [("(empty)", "")]


def measure(body: str) -> dict:
    words = len(body.split())
    sents = [s for s in SENT_SPLIT.split(body) if s.strip()]
    wps = words / max(1, len(sents))
    adrs, shas, paths, bare = EXTRACT(body)
    ground = len(adrs) + len(shas) + len(paths) + len(bare) + len(URL_RE.findall(body)) + len(RECEIPT_RE.findall(body)) + len(MEMLINK_RE.findall(body))
    conf = len(CONFIDENCE_RE.findall(body)) + len(QUANT_RE.findall(body))
    ratio = conf / (ground + 1)
    if words >= MIN_WORDS and conf >= 2 and ground == 0:
        verdict = "NO GROUND RETURN"
    elif conf >= 2 and ratio > 2:
        verdict = "THIN AIR"
    else:
        verdict = "GROUNDED"
    return {"words": words, "words_per_sentence": round(wps, 1), "ground_returns": ground,
            "confidence_markers": conf, "ratio": round(ratio, 2), "verdict": verdict}


def report(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    rows = []
    for title, body in sections(text):
        m = measure(body)
        m["section"] = title[:60]
        rows.append(m)
    alarms = [r for r in rows if r["verdict"] == "NO GROUND RETURN"]
    thin = [r for r in rows if r["verdict"] == "THIN AIR"]
    return {"file": str(path), "sections": rows, "alarms": len(alarms), "thin": len(thin),
            "verdict": "NO GROUND RETURN" if alarms else ("THIN AIR" if thin else "GROUNDED")}


def print_report(r: dict) -> None:
    mark = {"GROUNDED": "✓", "THIN AIR": "⚠", "NO GROUND RETURN": "✖"}[r["verdict"]]
    print(f"{mark} {Path(r['file']).relative_to(ROOT) if str(r['file']).startswith(str(ROOT)) else r['file']}  — {r['verdict']} ({r['alarms']} alarm, {r['thin']} thin, {len(r['sections'])} sections)")
    for s in r["sections"]:
        if s["verdict"] != "GROUNDED":
            print(f"    {s['verdict']:<17} {s['section'][:44]:<44} words={s['words']:<5} conf={s['confidence_markers']:<3} ground={s['ground_returns']:<3} wps={s['words_per_sentence']}")


def staged_prose() -> list[Path]:
    out = subprocess.run(["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"], capture_output=True, text=True, cwd=ROOT).stdout.split()
    return [ROOT / f for f in out if f.endswith((".md", ".txt")) and any(f.startswith(r) or f == r for r in PROSE_ROOTS)]


def self_test() -> int:
    fluent = ("This is clearly the only answer and it always works. The architecture is production-ready and "
              "battle-tested, delivering a 75% improvement and 40+ deployments with 10x throughput. It proves that "
              "the approach is correct, and there is no doubt the method guarantees results. Every stakeholder "
              "must adopt it precisely as described, because the outcome is certain and the design is obviously "
              "superior to every alternative. The rollout will never fail. ") * 3
    grounded = ("The registry is generated by scripts/operator_registry_emit.py and committed at "
                "operators/OPERATOR-REGISTRY.json; the merge is 1ffed09ef946675833124abff971ca3b24d71aea per ADR-065. "
                "Self-test output and the stdio round trip are in the receipt "
                "2026-09-27--operator-mcp-bridge-registry-pr559-merge--ZH. See [[operator-numbering-locked-periodic-table-registry-generated]]. ") * 4
    fails = 0
    def check(label, cond, detail=""):
        nonlocal fails
        print(f"  {'PASS' if cond else 'FAIL'}  {label}  {detail}")
        fails += 0 if cond else 1
    a = measure(fluent); b = measure(grounded); c = measure("short and sure: clearly, always.")
    check("fluent + confident + uncited -> NO GROUND RETURN", a["verdict"] == "NO GROUND RETURN", a)
    check("cited prose -> GROUNDED", b["verdict"] == "GROUNDED", b)
    check("short assertive line does not alarm (below MIN_WORDS)", c["verdict"] != "NO GROUND RETURN", c)
    secs = sections("# A\n\ntext one\n\n```\ncode clearly always never proves 99%\n```\n\n## B\n\ntext two")
    check("fenced code stripped and headings split", [t for t, _ in secs] == ["A", "B"] and "clearly" not in secs[0][1], secs)
    print(f"self-test: {'OK' if fails == 0 else f'{fails} FAIL'}")
    return 1 if fails else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*")
    ap.add_argument("--staged", action="store_true")
    ap.add_argument("--strict", action="store_true", help="exit 1 on any NO GROUND RETURN")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    files = staged_prose() if a.staged else [Path(f) for f in a.files]
    if not files:
        print("altitude_canary: nothing to read"); return 0
    reports = [report(p) for p in files if p.exists()]
    if a.json:
        print(json.dumps(reports, indent=1));
    else:
        for r in reports:
            print_report(r)
    alarms = sum(r["alarms"] for r in reports)
    if alarms:
        print(f"altitude_canary: {alarms} section(s) with NO GROUND RETURN — fluent, confident, uncited. "
              f"Add the sha / path / ADR / receipt the claim stands on, or say it is unconfirmed.")
    return 1 if (a.strict and alarms) else 0


if __name__ == "__main__":
    raise SystemExit(main())
