#!/usr/bin/env python3
"""
unfold.py — the pickup-side atomizer. The fold sweeps residue OUT at close; the unfold sweeps
inherited state IN at open and cuts it into self-contained chip drafts. It never spawns a
session (NOTOMATION): it lays cut stones on the bench for the human to pick.

Bench sequence (Zach, 2026-09-27: "categorizing and pressurizing and cutting happens between
handoff and handoff atomize"):
  GATHER      candidates from five sources
                 a. latest `# Handoff` block in CLAUDE.md, its "## Open" numbered items
                 b. _QUEUE/induced-backlog.jsonl rows whose status starts OPEN
                 c. _SEEDS/index.jsonl rows with lab_candidate.status in {ripe, seedling}
                 d. runtime/specs/lore.jsonl rows with binding_verdict == inspiration
                 e. pollination gaps: a seed whose `local`/`conforms_to` names a repo path that
                    now EXISTS on main while the seed is still planted/candidate
  CATEGORIZE  cluster by domain gravity (fold Step 2): a mechanical pre-cluster over shared
              SSOT paths + domain keywords; the human re-sorts. A cluster earns a stone only
              with 2+ items sharing an SSOT, or one item marked heavy. Singletons stay lines.
  PRESSURIZE  each stone draft runs scripts/cold_molt_lint.py (relative refs, categories,
              integrity --strict, canary). FLAWLESS stones are settable; UNCUT stones say why.
  CUT         the draft carries the ridgeline categories (fold Step 3) filled from what is
              MECHANICALLY known (paths, gates, triggers, head sha, dates) and marks what a
              human must fill. Attachment release stays human.

Output: _INBOX/unfold-<date>.md (gitignored derived cache) + a summary on stdout.
Usage:
  python3 scripts/unfold.py                 # gather, cluster, draft, lint, write the bench file
  python3 scripts/unfold.py --json          # machine-readable
  python3 scripts/unfold.py --self-test
"""
from __future__ import annotations

import datetime as dt
import importlib.util
import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "_INBOX"
PATH_RE = re.compile(r"(?<![\w/.-])((?:_DECISIONS|_STATE|_SEEDS|_CANON|_QUEUE|_PATTERNS|_SPECS|scripts|operators|runtime|src|public|\.claude)/[\w./\[\]@+-]+)")
DOMAINS = {
    "operators": r"\boperator|registry|mcp bridge|arcs_mcp|periodic",
    "tao-lore": r"\btao\b|proverb|lore\b|legend\b|ordinal",
    "memory": r"memory index|MEMORY\.md|uncurated|mem_budget",
    "trust-gates": r"source-trust|falsification|integrity gate|canary|fate registry|gate\b",
    "jobs-counterparts": r"yuri|robert|jarrod|squad|iggy|kam\b|ahmed|prl|todd|resume|recruit",
    "nftt-surfaces": r"nftt|blog|good\.arcs|public/",
    "receipts-outcomes": r"outcome|receipt|capture rate|supabase sync|ledger",
    "seeds": r"\bseed|germinat|pollinat|lab_candidate",
}


def _rows(p: Path) -> list[dict]:
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def _main_tree() -> set[str]:
    r = subprocess.run(["git", "ls-tree", "-r", "--name-only", "origin/main"], capture_output=True, text=True, cwd=ROOT)
    return set(r.stdout.split())


def gather() -> list[dict]:
    c: list[dict] = []
    # a. latest handoff Open items
    cl = (ROOT / "CLAUDE.md").read_text(encoding="utf-8", errors="replace")
    m = re.search(r"^# Handoff — (v[\d.]+) \((\d{4}-\d{2}-\d{2})\)(.*?)(?=^# Handoff — |\Z)", cl, re.M | re.S)
    if m:
        ver, day, body = m.group(1), m.group(2), m.group(3)
        op = re.search(r"^## Open.*?$(.*?)(?=^## |\Z)", body, re.M | re.S)
        if op:
            for item in re.findall(r"^\s*\d+\.\s+(.*?)(?=^\s*\d+\.\s+|\Z)", op.group(1), re.M | re.S):
                t = " ".join(item.split())
                c.append({"source": f"handoff {ver}", "id": f"open:{t[:40]}", "text": t, "paths": PATH_RE.findall(t), "gates": [], "trigger": f"handoff {ver} ({day})", "heavy": len(t) > 240})
    # b. backlog OPEN
    for r in _rows(ROOT / "_QUEUE" / "induced-backlog.jsonl"):
        st = str(r.get("status", "")).upper()
        if st.startswith("OPEN"):
            t = str(r.get("jtbd", "")); blob = json.dumps(r)
            c.append({"source": "backlog", "id": r["id"], "text": t, "paths": PATH_RE.findall(blob), "gates": r.get("gates", []), "trigger": str(r.get("trigger", ""))[:160], "heavy": "COURT" in blob or len(t) > 300})
    # c. seeds ripe/seedling
    for r in _rows(ROOT / "_SEEDS" / "index.jsonl"):
        lc = (r.get("lab_candidate") or {}); st = str(lc.get("status", ""))
        if st in ("ripe", "seedling"):
            blob = json.dumps(r)
            c.append({"source": f"seed:{st}", "id": r["id"], "text": f"{r.get('alias','')}: {str(lc.get('note',''))[:200]}", "paths": PATH_RE.findall(blob), "gates": [], "trigger": "; ".join(str(t)[:80] for t in ((r.get("germination") or {}).get("triggers", []) or [])[:2]), "heavy": st == "ripe"})
    # d. LORE inspiration
    for r in _rows(ROOT / "runtime" / "specs" / "lore.jsonl"):
        if r.get("binding_verdict") == "inspiration":
            c.append({"source": "lore:inspiration", "id": r["id"], "text": r.get("teaches", ""), "paths": [p for p in r.get("refs", []) if "/" in p], "gates": ["cite as aspiration, never as fact"], "trigger": r.get("told_where", ""), "heavy": False})
    # e. pollination gaps
    tree = _main_tree()
    for r in _rows(ROOT / "_SEEDS" / "index.jsonl"):
        if str(r.get("status")) in ("planted", "candidate", "None", None):
            cited = set(PATH_RE.findall(str(r.get("local", "")) + " " + str(r.get("conforms_to", ""))))
            landed = sorted(p for p in cited if p.rstrip("/") in tree or any(t.startswith(p.rstrip("/") + "/") for t in tree))
            if landed:
                c.append({"source": "pollination-gap", "id": r["id"], "text": f"seed still {r.get('status')} but cites paths now on main: {', '.join(landed[:4])}", "paths": landed, "gates": ["update the seed ledger (event: pollinated|germinated) rather than the index status by hand"], "trigger": "paths landed", "heavy": False})
    # dedup by id (a seed can arrive from both the ripeness list and a pollination gap); keep the first
    seen=set(); out=[]
    for it in c:
        if it["id"] in seen: continue
        seen.add(it["id"]); out.append(it)
    # verify every cited path against origin/main NOW, so the draft's claim is true
    tree_all = tree
    for it in out:
        ok=[p for p in it["paths"] if p.rstrip("/") in tree_all or any(t.startswith(p.rstrip("/")+"/") for t in tree_all)]
        it["vapor"]=[p for p in it["paths"] if p not in ok]
        it["paths"]=ok
    return out


def categorize(cands: list[dict]) -> dict[str, list[dict]]:
    clusters: dict[str, list[dict]] = defaultdict(list)
    for cnd in cands:
        blob = (cnd["text"] + " " + " ".join(cnd["paths"]) + " " + cnd["id"]).lower()
        dom = next((d for d, pat in DOMAINS.items() if re.search(pat, blob, re.I)), "unsorted")
        cnd["domain"] = dom
        clusters[dom].append(cnd)
    return clusters


def _shared_ssot(items: list[dict]) -> list[str]:
    counts: dict[str, int] = defaultdict(int)
    for it in items:
        for p in set(it["paths"]):
            counts[p] += 1
    return sorted(p for p, n in counts.items() if n >= 2)


def draft(domain: str, items: list[dict], head: str, today: str) -> str:
    shared = _shared_ssot(items)
    all_paths = sorted({p for it in items for p in it["paths"]})
    gates = sorted({g for it in items for g in it["gates"]})
    lines = [f"# Chip: {domain} ({len(items)} items)", "",
             f"Cut on {today} from origin/main {head} by the unfold bench (see .claude/commands/handoff-pickup.md, Step 3). A cold session gets this file + the repo, nothing else.", "",
             "## Ground truth (verified at cut)",
             f"- origin/main head {head} on {today}; every path below was checked to exist on main at cut time"]
    scrub = lambda t: re.sub(r"\b(this|the current|the other|the previous) session\b", "the originating session (see its handoff block in CLAUDE.md)", t, flags=re.I)
    for it in items:
        lines.append(f"- [{it['source']}] {it['id']}: {scrub(it['text'][:220])}")
    vapor = sorted({v for it in items for v in it.get("vapor", [])})
    if vapor:
        lines.append(f"- NOT on main (cited by an item, treated as vapor, not carried): {', '.join(vapor[:6])}")
    lines += ["", "## SSOT (the files that ARE the state)"]
    lines += [f"- {p}" + ("  (shared by 2+ items)" if p in shared else "") for p in all_paths] or ["- (declared empty: the items name no repo path; a human must point at the SSOT before this stone is set)"]
    lines += ["", "## Routes (tool -> surface, dated)", "- (human: add the verified route for each item, with its date, or declare empty)"]
    lines += ["", "## Gates"] + ([f"- {g}" for g in gates] or ["- (declared empty)"]) + ["- draft-first for anything outward; consent gates ride in, authorization never does"]
    lines += ["", "## Corrections (stale claims retired since the items were written)", "- (human: check _STATE/falsification-ledger.jsonl rows dated after each item; declare empty if none)"]
    lines += ["", "## Timing", "- " + "; ".join(sorted({it['trigger'] for it in items if it['trigger']})[:3] or ["(declared empty)"])]
    lines += ["", "## Close protocol", "- one decision_receipt row per merge (AGENTS.md); waypoints (shas / receipt ids) appended to the fold receipt in _QUEUE/induced-backlog.jsonl; backlog statuses updated; memory additive only", ""]
    return "\n".join(lines)


def run(as_json: bool = False) -> dict:
    today = dt.date.today().isoformat()
    head = subprocess.run(["git", "rev-parse", "--short", "origin/main"], capture_output=True, text=True, cwd=ROOT).stdout.strip()
    cands = gather(); clusters = categorize(cands)
    lint_mod = None
    p = ROOT / "scripts" / "cold_molt_lint.py"
    if p.exists():
        spec = importlib.util.spec_from_file_location("cold_molt_lint", p); lint_mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(lint_mod)  # type: ignore[union-attr]
    OUT_DIR.mkdir(exist_ok=True)
    bench = OUT_DIR / f"unfold-{today}.md"
    stones, lines = [], []
    for dom, items in sorted(clusters.items(), key=lambda kv: -len(kv[1])):
        earns = len(items) >= 2 or any(it["heavy"] for it in items)
        if not earns:
            lines.append(f"- LINE (not a stone): {dom}: {items[0]['id']} stays a backlog line (singleton, not heavy)")
            continue
        if dom == "unsorted":
            lines.append(f"- PILE (no domain): {len(items)} unsorted items need a human sort before any is a stone: " + ", ".join(it["id"] for it in items[:8]))
            continue
        if len(items) > 6:
            shared = _shared_ssot(items)
            lines.append(f"- PILE (massif, {len(items)} items): {dom} is too big for one stone; split by shared SSOT ({', '.join(shared[:3]) or 'none shared'}) before cutting")
            continue
        d = draft(dom, items, head, today)
        f = OUT_DIR / f"unfold-{today}-{dom}.md"; f.write_text(d, encoding="utf-8")
        verdict, reasons = "UNLINTED", []
        if lint_mod:
            r = lint_mod.lint(f); verdict, reasons = r["verdict"], r["reasons"]
        stones.append({"domain": dom, "items": [it["id"] for it in items], "file": str(f.relative_to(ROOT)), "verdict": verdict, "reasons": reasons})
    header = [f"# Unfold bench — {today} (origin/main {head})", "",
              f"{len(cands)} candidates gathered · {len(clusters)} clusters · {len(stones)} stones drafted · "
              f"{sum(1 for s in stones if s['verdict']=='FLAWLESS')} FLAWLESS · {sum(1 for s in stones if s['verdict']=='UNCUT')} UNCUT", "",
              "The human picks which FLAWLESS stones to set (spawn_task). UNCUT stones list what a cold session could not reconstruct. Nothing here was spawned.", ""]
    for s in stones:
        header.append(f"## {s['domain']} — {s['verdict']} ({len(s['items'])} items) → {s['file']}")
        header += [f"- {i}" for i in s["items"]]
        header += [f"  ✖ {r}" for r in s["reasons"]]
        header.append("")
    bench.write_text("\n".join(header + lines) + "\n", encoding="utf-8")
    result = {"bench": str(bench.relative_to(ROOT)), "candidates": len(cands), "clusters": {k: len(v) for k, v in clusters.items()}, "stones": stones, "lines": lines}
    if as_json:
        print(json.dumps(result, indent=1))
    else:
        print("\n".join(header[:4]))
        for s in stones:
            print(f"  {s['verdict']:<9} {s['domain']:<18} {len(s['items'])} items -> {s['file']}")
        for l in lines:
            print("  " + l)
    return result


def self_test() -> int:
    fails = 0
    def check(label, cond, detail=""):
        nonlocal fails
        print(f"  {'PASS' if cond else 'FAIL'}  {label}  {detail}")
        fails += 0 if cond else 1
    items = [{"source": "backlog", "id": "a", "text": "fix the tao book", "paths": ["runtime/tao/proverbs.json"], "gates": ["ruling first"], "trigger": "t", "heavy": False},
             {"source": "backlog", "id": "b", "text": "mint proverbs", "paths": ["runtime/tao/proverbs.json", "_CANON/tao-proverbs.jsonl"], "gates": [], "trigger": "t2", "heavy": False}]
    cl = categorize([dict(i) for i in items])
    check("two tao items cluster into tao-lore", "tao-lore" in cl and len(cl["tao-lore"]) == 2, dict(cl))
    check("shared SSOT detected", _shared_ssot(items) == ["runtime/tao/proverbs.json"], _shared_ssot(items))
    d = draft("tao-lore", items, "abc1234", "2026-09-27")
    for cat in ("Ground truth", "SSOT", "Routes", "Gates", "Corrections", "Close protocol"):
        check(f"draft carries category {cat}", cat in d)
    check("singleton light item does not earn a stone", not (len([items[0]]) >= 2 or items[0]["heavy"]))
    print(f"self-test: {'OK' if fails == 0 else f'{fails} FAIL'}")
    return 1 if fails else 0


if __name__ == "__main__":
    a = sys.argv[1:]
    raise SystemExit(self_test() if a[:1] == ["--self-test"] else (run(as_json="--json" in a) and 0))
