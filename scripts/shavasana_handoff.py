#!/usr/bin/env python3
"""
shavasana_handoff.py — the MECHANICAL half of Operator 25 (ShavasanaSpace) at the handoff door.
Spec: runtime/specs/operator-25-shavasana-v0.md. This script covers components 1 (trigger =
handoff), 3 (breath audit, counts + net direction), 5 (sycophancy check, threshold), 7 (integration
block, incl. the om metric). Components 4 (attachment release: cold re-read) and 6 (somatic read)
are judgment/human and are prompted, not computed; component 6's one number (conviction 0-10) is
taken from `--conviction` and is NEVER imputed. Component 8 (release or return) is always the
human's move.

Hard rule it enforces on ITSELF: the integration block contains NO new claim. Every line is a
count, a path, a sha, or a question. `--self-test` proves the block passes the altitude canary
(zero confidence markers, ground returns present).

The om metric (spec, "The om metric"; the Flow-State axis of the Hypersphere manifold, WORLD.md):
  confidence  = backed fraction of the draft's claims, mechanical: sections of the draft with at
                least one ground return (altitude_canary.py's cite classes) / non-empty sections
  conviction  = the human's felt read, 0-10, from --conviction; null when absent
  om_gap      = |confidence - conviction/10|, or null when either side is missing
Breath (Maekawa, LEGEND; assumption asm-009 in _STATE/assumptions.jsonl is OPEN): the block reports
the signed NET DIRECTION (exhale_n - inhale_n) alongside the balance string. The script does not
verdict on the direction; asm-009's test runs across ten handoffs, by a human.

Usage:
  python3 scripts/shavasana_handoff.py --draft <handoff-block.md>                  # audit a drafted handoff block
  python3 scripts/shavasana_handoff.py --draft <block.md> --conviction 7           # with the somatic read
  python3 scripts/shavasana_handoff.py --draft <block.md> --json                   # machine-readable fields
  python3 scripts/shavasana_handoff.py                                             # audit today's session, no draft
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


def _canary_module():
    p = ROOT / "scripts" / "altitude_canary.py"
    if not p.exists():
        return None
    spec = importlib.util.spec_from_file_location("altitude_canary", p)
    if not spec or not spec.loader:
        return None
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod


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


def breath(exh: dict, inh: dict) -> dict:
    """Component 3. Balance string (manifesto / mirror / breathing) plus the signed net direction.
    exhale_n = commits + receipts in the digest (merges are a subset of commits, not re-added);
    inhale_n = falsification rows + dissent markers + unconfirmed markers.
    net = exhale_n - inhale_n. Positive leans exhale (fold, outward); negative leans inhale (unfold, inward).
    No verdict is attached to the sign: asm-009 (Maekawa: a small net direction, not balance) is OPEN."""
    inward = inh["dissent_markers"] or inh["falsification_rows_today"]
    balance = "manifesto (exhale, no inhale)" if exh["commits"] and not inward else \
              "mirror (inhale, no exhale)" if not exh["commits"] and inward else "breathing (both directions)"
    exhale_n = exh["commits"] + (exh["receipts_in_digest"] or 0)
    inhale_n = inh["falsification_rows_today"] + inh["dissent_markers"] + inh["unconfirmed_markers"]
    net = exhale_n - inhale_n
    lean = "exhale-leaning" if net > 0 else ("inhale-leaning" if net < 0 else "balanced (Maekawa: a node with equal folds does not lie flat; asm-009 open)")
    return {"balance": balance, "exhale_n": exhale_n, "inhale_n": inhale_n, "net_direction": net, "lean": lean}


def sycophancy(inh: dict, exh: dict) -> dict:
    """Agreement with no dissent on record -> RETURN for re-evaluation (spec component 5)."""
    agree = inh["agreement_markers"] + exh["merges"]
    dissent = inh["dissent_markers"] + inh["falsification_rows_today"] + inh["unconfirmed_markers"]
    ratio = agree / (dissent + 1)
    verdict = "RETURN: agreement with no dissent on record" if (agree >= 5 and dissent == 0) else ("THIN: high agreement, little dissent" if ratio > 4 else "OK: dissent present")
    return {"agreement": agree, "dissent": dissent, "ratio": round(ratio, 2), "verdict": verdict}


def canary(draft_path: Path | None) -> dict | None:
    """Cold re-read helper: which sections of the draft carry claims with no ground return.
    Also carries the per-section ground-return counts that `confidence()` reads."""
    if not draft_path or not draft_path.exists():
        return None
    mod = _canary_module()
    if mod is None:
        return None
    r = mod.report(draft_path)
    return {"verdict": r["verdict"], "sections": r["sections"],
            "alarms": [s["section"] for s in r["sections"] if s["verdict"] == "NO GROUND RETURN"],
            "thin": [s["section"] for s in r["sections"] if s["verdict"] == "THIN AIR"]}


def confidence(can: dict | None) -> dict:
    """The mechanical side of the om metric: the backed fraction of the draft.
    A section is BACKED when the altitude canary finds at least one ground return in it (ADR, sha,
    repo path, script name, URL, receipt id, memory link). Denominator = non-empty sections.
    Reads the draft AS HANDED: re-run after the cold re-read drops claims to read the survivors."""
    if not can or not can.get("sections"):
        return {"backed_sections": None, "total_sections": None, "confidence": None}
    secs = [s for s in can["sections"] if s["words"] > 0]
    if not secs:
        return {"backed_sections": 0, "total_sections": 0, "confidence": None}
    backed = sum(1 for s in secs if s["ground_returns"] >= 1)
    return {"backed_sections": backed, "total_sections": len(secs), "confidence": round(backed / len(secs), 2)}


def om(conf: dict, conviction: float | None) -> dict:
    """om_gap = |confidence - conviction/10|. Null when either side is missing; conviction is the
    human's number from --conviction and is not imputed from anything."""
    c = conf.get("confidence")
    if c is None or conviction is None:
        return {"conviction": conviction, "om_gap": None}
    return {"conviction": conviction, "om_gap": round(abs(c - conviction / 10.0), 2)}


def fields(day: str, exh: dict, inh: dict, br: dict, syc: dict, can: dict | None, conf: dict, omr: dict, draft_path: Path | None) -> dict:
    """Machine-readable form of the block (for --json and the _STATE/ readings)."""
    return {"day": day, "draft": str(draft_path) if draft_path else None,
            "exhale": {k: v for k, v in exh.items() if k != "sends"},
            "inhale": inh,
            "breath": br, "sycophancy": syc,
            "cold_reread": None if can is None else {"verdict": can["verdict"], "alarms": can["alarms"], "thin": can["thin"]},
            "confidence": conf["confidence"], "backed_sections": conf["backed_sections"], "total_sections": conf["total_sections"],
            "conviction": omr["conviction"], "om_gap": omr["om_gap"],
            "breath_net_direction": br["net_direction"],
            "new_claims": 0}


def block(day: str, exh: dict, inh: dict, syc: dict, can: dict | None, draft_path: Path | None,
          br: dict | None = None, conf: dict | None = None, omr: dict | None = None) -> str:
    br = br or breath(exh, inh)
    conf = conf or confidence(can)
    omr = omr or om(conf, None)
    lines = [f"### Shavasana — handoff pause, {day} (Operator 25, mechanical half; spec runtime/specs/operator-25-shavasana-v0.md)",
             "",
             f"- **Exhale** (what went out): {exh['commits']} commits, {exh['merges']} merges to main, receipts in digest: {exh['receipts_in_digest'] if exh['receipts_in_digest'] is not None else 'no digest file'}.",
             f"- **Inhale** (what came in): {inh['falsification_rows_today']} falsification rows today, {inh['dissent_markers']} dissent markers, {inh['unconfirmed_markers']} unconfirmed markers in the day's records.",
             f"- **Breath balance**: {br['balance']}.",
             f"- **Breath net direction** (Maekawa; asm-009 open, read across ten handoffs): exhale {br['exhale_n']} minus inhale {br['inhale_n']} = {br['net_direction']:+d}, {br['lean']}.",
             f"- **Sycophancy check**: agreement {syc['agreement']} / dissent {syc['dissent']} (ratio {syc['ratio']}) → {syc['verdict']}."]
    if can:
        lines.append(f"- **Cold re-read (canary on the draft {draft_path.name if draft_path else ''})**: {can['verdict']}; no ground return: {can['alarms'] or 'none'}; thin air: {can['thin'] or 'none'}.")
    else:
        lines.append("- **Cold re-read**: no draft given; run again with --draft <handoff-block.md> before writing the delta.")
    if conf["confidence"] is None:
        conf_s = "confidence: no draft to read"
    else:
        conf_s = f"confidence {conf['confidence']} ({conf['backed_sections']} of {conf['total_sections']} sections carry a ground return)"
    if omr["conviction"] is None:
        om_s = "conviction: not given (--conviction absent); om_gap: null, not imputed"
    else:
        om_s = f"conviction {omr['conviction']:g} of 10 (from --conviction); om_gap {omr['om_gap'] if omr['om_gap'] is not None else 'null'}"
    lines.append(f"- **Om** (Flow-State axis; component 7): {conf_s}; {om_s}.")
    lines += ["- **Attachment release** (human): for each claim in the draft, does it survive without the momentum? Downgrade or drop, and say which.",
              "- **Somatic read** (human, one question): certainty now vs certainty at the start of the session, and were there sends today? Give the number as `--conviction 0-10` and re-run.",
              "- **Disposition** (human): release the handoff, or return it to the queue with this block attached.",
              "",
              "_This block asserts nothing new. Counts, paths, and questions only._"]
    return "\n".join(lines)


def self_test() -> int:
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    draft = tmp / "handoff.md"
    draft.write_text("# Handoff\n\nMerged 1ffed09e per ADR-062; see _STATE/night-moves/2026-09-27.md. One claim unconfirmed.\n"
                     "\n## Open\n\nThe next session should look at the queue and decide.\n", encoding="utf-8")
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
    # breath: net direction is a signed count, exhale_n - inhale_n, with the balance string kept
    br = breath(exh, inh2)
    check("breath net direction = exhale_n - inhale_n (signed)", br["exhale_n"] == 5 and br["inhale_n"] == 4 and br["net_direction"] == 1 and br["balance"].startswith("breathing"), br)
    br0 = breath({"commits": 2, "merges": 0, "receipts_in_digest": None}, {"falsification_rows_today": 1, "dissent_markers": 1, "unconfirmed_markers": 0})
    check("balanced breath reads 0 and names asm-009, no verdict", br0["net_direction"] == 0 and "asm-009" in br0["lean"], br0)
    # om: confidence is the backed fraction of sections; conviction is human or null; om_gap null when absent
    can = canary(draft)
    conf = confidence(can)
    check("confidence = backed sections / non-empty sections (1 of 2 here)", conf == {"backed_sections": 1, "total_sections": 2, "confidence": 0.5}, conf)
    check("conviction absent -> om_gap null (not imputed)", om(conf, None) == {"conviction": None, "om_gap": None}, om(conf, None))
    check("conviction 7 -> om_gap |0.5 - 0.7| = 0.2", om(conf, 7.0)["om_gap"] == 0.2, om(conf, 7.0))
    check("no draft -> confidence null and om_gap null", confidence(None)["confidence"] is None and om(confidence(None), 7.0)["om_gap"] is None, "")
    # the block adds no claim: zero confidence markers by the canary's own regex, ground returns present
    mod = _canary_module()
    for label, conv in (("without conviction", None), ("with conviction", 7.0)):
        b = block("2026-09-27", exh, inh2, sycophancy(inh2, exh), can, draft, br, conf, om(conf, conv))
        n_conf = len(mod.CONFIDENCE_RE.findall(b)) if mod else (1 if "clearly" in b else 0)
        check(f"block {label}: zero confidence markers, has ground returns", n_conf == 0 and "runtime/specs" in b, f"confidence_markers={n_conf}")
        out = tmp / f"block-{label.replace(' ', '-')}.md"; out.write_text(b, encoding="utf-8")
        c = canary(out)
        check(f"block {label} passes the altitude canary", c is None or c["verdict"] != "NO GROUND RETURN", c and c["verdict"])
        check(f"block {label} carries om_gap and breath net direction lines", "**Om**" in b and "**Breath net direction**" in b, "")
    f = fields("2026-09-27", exh, inh2, br, sycophancy(inh2, exh), can, conf, om(conf, None), draft)
    check("json fields: om_gap null, breath_net_direction signed, new_claims 0", f["om_gap"] is None and f["breath_net_direction"] == 1 and f["new_claims"] == 0, "")
    print(f"self-test: {'OK' if fails == 0 else f'{fails} FAIL'}")
    return 1 if fails else 0


def _conviction_arg(s: str) -> float:
    v = float(s)
    if not (0.0 <= v <= 10.0):
        raise argparse.ArgumentTypeError("--conviction is the human's felt read on a 0-10 scale")
    return v


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--draft", help="drafted handoff block (markdown) to cold-read")
    ap.add_argument("--day", default=today())
    ap.add_argument("--conviction", type=_conviction_arg, default=None,
                    help="the human's felt certainty on the surviving claims, 0-10 (component 6). Omit and om_gap is null.")
    ap.add_argument("--json", action="store_true", help="print the fields as JSON instead of the markdown block")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    dp = Path(a.draft) if a.draft else None
    draft = dp.read_text(encoding="utf-8") if dp and dp.exists() else ""
    exh = exhale(a.day); inh = inhale(a.day, draft); syc = sycophancy(inh, exh); can = canary(dp)
    br = breath(exh, inh); conf = confidence(can); omr = om(conf, a.conviction)
    if a.json:
        print(json.dumps(fields(a.day, exh, inh, br, syc, can, conf, omr, dp), indent=1))
    else:
        print(block(a.day, exh, inh, syc, can, dp, br, conf, omr))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
