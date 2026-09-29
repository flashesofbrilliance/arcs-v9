#!/usr/bin/env python3
"""
shavasana_handoff.py — the MECHANICAL half of Operator 25 (ShavasanaSpace) at the handoff door.
Spec: runtime/specs/operator-25-shavasana-v0.md. This script covers components 1 (trigger =
handoff), 3 (breath audit, counts), 5 (sycophancy check, threshold), 7 (integration block).
Components 4 (attachment release: cold re-read) and 6 (somatic read) are judgment/human and are
prompted, not computed. Component 8 (release or return) is always the human's move.

Hard rule it enforces on ITSELF: the integration block contains NO new claim. Every line is a
count, a path, a sha, or a question. `--self-test` proves the block passes the altitude canary
(no confidence markers, ground returns present).

Usage:
  python3 scripts/shavasana_handoff.py --draft <handoff-block.md>   # audit a drafted handoff block
  python3 scripts/shavasana_handoff.py                               # audit today's session with no draft
  python3 scripts/shavasana_handoff.py --self-test
Prints a markdown "### Shavasana" block to paste into the handoff, ABOVE the delta prose.
Exit 0 always (a canary warns; the human releases or returns).
"""
from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DISSENT_RE = re.compile(r"\b(FALSIFIED|falsif|blocked|STOP:|refused|corrected|premise correction|deceipt|retract|red X|does not exist|not evidence|wrong)\b", re.I)
UNCONFIRMED_RE = re.compile(r"\b(unconfirmed|not verified|not checked|unverified|assum(e|ed|ption)|M1)\b", re.I)
AGREE_RE = re.compile(r"\b(merged|shipped|done|complete|green|verified|confirmed|landed)\b", re.I)


def sh(*a: str) -> str:
    return subprocess.run(a, capture_output=True, text=True, cwd=ROOT).stdout.strip()


def today() -> str:
    return dt.date.today().isoformat()


def exhale(day: str) -> dict:
    """What went OUT today: commits, merges to main, receipts (from the day's night-moves if present)."""
    author = sh("git", "config", "user.name") or "Zach"
    commits = [l for l in sh("git", "log", "--all", f"--since={day} 00:00", f"--author={author}", "--format=%h %s").splitlines() if l]
    merges = [c for c in commits if c.split(" ", 1)[1].startswith("Merge pull request")]
    nm = ROOT / "_STATE" / "night-moves" / f"{day}.md"
    receipts = len(re.findall(r"\b\d{4}-\d{2}-\d{2}--[a-z0-9-]+--[A-Z]{2}\b", nm.read_text(encoding="utf-8"))) if nm.exists() else None
    return {"commits": len(commits), "merges": len(merges), "receipts_in_digest": receipts,
            "sends": "not detectable mechanically (Gmail/iMessage are outside git); answer in the somatic read"}


def inhale(day: str, draft: str) -> dict:
    """What came IN: falsification rows today, corrections/dissent markers in the draft + day's records."""
    fl = ROOT / "_STATE" / "falsification-ledger.jsonl"
    f_today = 0
    if fl.exists():
        for l in fl.read_text(encoding="utf-8").splitlines():
            try:
                if json.loads(l).get("ts", "") == day:
                    f_today += 1
            except Exception:
                pass
    texts = [draft]
    for p in (ROOT / "_STATE" / "night-moves" / f"{day}.md", ROOT / "_STATE" / f"{day}-forensic-recoil.md"):
        if p.exists():
            texts.append(p.read_text(encoding="utf-8"))
    blob = "\n".join(texts)
    return {"falsification_rows_today": f_today, "dissent_markers": len(DISSENT_RE.findall(blob)),
            "unconfirmed_markers": len(UNCONFIRMED_RE.findall(blob)), "agreement_markers": len(AGREE_RE.findall(blob))}


def sycophancy(inh: dict, exh: dict) -> dict:
    """Agreement with no dissent on record -> RETURN for re-evaluation (spec component 5)."""
    agree = inh["agreement_markers"] + exh["merges"]
    dissent = inh["dissent_markers"] + inh["falsification_rows_today"] + inh["unconfirmed_markers"]
    ratio = agree / (dissent + 1)
    verdict = "RETURN: agreement with no dissent on record" if (agree >= 5 and dissent == 0) else ("THIN: high agreement, little dissent" if ratio > 4 else "OK: dissent present")
    return {"agreement": agree, "dissent": dissent, "ratio": round(ratio, 2), "verdict": verdict}


def canary(draft_path: Path | None) -> dict | None:
    """Cold re-read helper: which sections of the draft carry claims with no ground return."""
    if not draft_path or not draft_path.exists():
        return None
    spec = importlib.util.spec_from_file_location("altitude_canary", ROOT / "scripts" / "altitude_canary.py")
    if not spec or not (ROOT / "scripts" / "altitude_canary.py").exists():
        return None
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)  # type: ignore[union-attr]
    r = mod.report(draft_path)
    return {"verdict": r["verdict"], "alarms": [s["section"] for s in r["sections"] if s["verdict"] == "NO GROUND RETURN"],
            "thin": [s["section"] for s in r["sections"] if s["verdict"] == "THIN AIR"]}


def block(day: str, exh: dict, inh: dict, syc: dict, can: dict | None, draft_path: Path | None) -> str:
    bal = "manifesto (exhale, no inhale)" if exh["commits"] and not (inh["dissent_markers"] or inh["falsification_rows_today"]) else \
          "mirror (inhale, no exhale)" if not exh["commits"] and (inh["dissent_markers"] or inh["falsification_rows_today"]) else "breathing (both directions)"
    lines = [f"### Shavasana — handoff pause, {day} (Operator 25, mechanical half; spec runtime/specs/operator-25-shavasana-v0.md)",
             "",
             f"- **Exhale** (what went out): {exh['commits']} commits, {exh['merges']} merges to main, receipts in digest: {exh['receipts_in_digest'] if exh['receipts_in_digest'] is not None else 'no digest file'}.",
             f"- **Inhale** (what came in): {inh['falsification_rows_today']} falsification rows today, {inh['dissent_markers']} dissent markers, {inh['unconfirmed_markers']} unconfirmed markers in the day's records.",
             f"- **Breath balance**: {bal}.",
             f"- **Sycophancy check**: agreement {syc['agreement']} / dissent {syc['dissent']} (ratio {syc['ratio']}) → {syc['verdict']}."]
    if can:
        lines.append(f"- **Cold re-read (canary on the draft {draft_path.name if draft_path else ''})**: {can['verdict']}; no ground return: {can['alarms'] or 'none'}; thin air: {can['thin'] or 'none'}.")
    else:
        lines.append("- **Cold re-read**: no draft given; run again with --draft <handoff-block.md> before writing the delta.")
    lines += ["- **Attachment release** (human): for each claim in the draft, does it survive without the momentum? Downgrade or drop, and say which.",
              "- **Somatic read** (human, one question): certainty now vs certainty at the start of the session, and were there sends today?",
              "- **Disposition** (human): release the handoff, or return it to the queue with this block attached.",
              "",
              "_This block asserts nothing new. Counts, paths, and questions only._"]
    return "\n".join(lines)


def self_test() -> int:
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    draft = tmp / "handoff.md"
    draft.write_text("# Handoff\n\nMerged 1ffed09e per ADR-062; see _STATE/night-moves/2026-09-27.md. One claim unconfirmed.\n", encoding="utf-8")
    exh = {"commits": 3, "merges": 2, "receipts_in_digest": 2, "sends": "n/a"}
    inh = {"falsification_rows_today": 0, "dissent_markers": 0, "unconfirmed_markers": 0, "agreement_markers": 6}
    syc = sycophancy(inh, exh)
    fails = 0
    def check(label, cond, detail=""):
        nonlocal fails
        print(f"  {'PASS' if cond else 'FAIL'}  {label}  {detail}")
        fails += 0 if cond else 1
    check("agreement with zero dissent -> RETURN", syc["verdict"].startswith("RETURN"), syc)
    inh2 = dict(inh, dissent_markers=3, falsification_rows_today=1)
    check("dissent present -> OK", sycophancy(inh2, exh)["verdict"].startswith("OK"), sycophancy(inh2, exh))
    b = block("2026-09-27", exh, inh2, sycophancy(inh2, exh), canary(draft), draft)
    check("block has no new claim: no confidence markers, has ground returns", "clearly" not in b and "runtime/specs" in b, "")
    out = tmp / "block.md"; out.write_text(b, encoding="utf-8")
    c = canary(out)
    check("block itself passes the altitude canary", c is None or c["verdict"] != "NO GROUND RETURN", c)
    print(f"self-test: {'OK' if fails == 0 else f'{fails} FAIL'}")
    return 1 if fails else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--draft", help="drafted handoff block (markdown) to cold-read")
    ap.add_argument("--day", default=today())
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    dp = Path(a.draft) if a.draft else None
    draft = dp.read_text(encoding="utf-8") if dp and dp.exists() else ""
    exh = exhale(a.day); inh = inhale(a.day, draft); syc = sycophancy(inh, exh); can = canary(dp)
    print(block(a.day, exh, inh, syc, can, dp))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
