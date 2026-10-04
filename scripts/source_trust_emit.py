#!/usr/bin/env python3
"""
source_trust_emit.py — per-source trust as a GENERATED table (Operator 12's source column).

Zach, 2026-09-27: "malleability is conditional and a function of trust; if the truths a
communicator shills turn out false, the gullibility suspicion goes up." So the evidence weight
of a claim is the SOURCE's track record, not the claim's fluency. The read-friction tier of a
source is not static; it is derived from its falsification history.

Inputs (SSOT, append-only, human- or hook-written):
  _STATE/source-trust-events.jsonl   one event per line:
    {"ts": "YYYY-MM-DD", "source": "<key>", "outcome": "falsified" | "confirmed",
     "claim": "<one line>", "ref": "<F-row | receipt id | path | sha>"}
  runtime/specs/source-trust-sources.json   the registry of source keys (+ optional pinned tier)

Output (GENERATED, never hand-edited): runtime/specs/source-trust.json

Derivation (mechanical, asymmetric, per source, no judgment):
  wf = Σ falsified  · exp(-age_days / HALF_LIFE)      weight 1.0 each   (trust drops fast)
  wc = Σ confirmed  · exp(-age_days / HALF_LIFE)      weight 0.1 each   (trust recovers slowly, 10:1)
  suspicion = (A0 + wf) / (A0 + B0 + wf + wc)   Beta-style prior A0=B0=1: no history = 0.5
             (unknown = spot-check, neither trusted nor damned); a fresh falsification lifts it,
             an old one fades because the prior dominates once wf has decayed
  tier:  ZERO-WEIGHT  pinned (a human ruling, with reason) or wf >= 3 and wc == 0
         ELEVATED     suspicion > 0.6    every claim needs a grep before it enters what_confirmed
         STANDARD     0.3 < suspicion <= 0.6
         LOW          suspicion <= 0.3   backed-by-record; still never exempt from the integrity gate
  Self-catch 2026-09-27: v0 used (1+wf)/(1+wf+wc), under which an ancient and a fresh falsification
  both read 1.0 with no confirmations, so decay could never act. The self-test caught it before
  the first table was written.
  Per source, never global: one liar must not close the membrane (that is the thermos).

Usage:
  python3 scripts/source_trust_emit.py            # regenerate runtime/specs/source-trust.json
  python3 scripts/source_trust_emit.py --check    # exit 1 if the generated table is stale
  python3 scripts/source_trust_emit.py --self-test
  python3 scripts/source_trust_emit.py add <source> <falsified|confirmed> "<claim>" "<ref>"   # append an event
"""
from __future__ import annotations

import datetime as dt
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EVENTS = ROOT / "_STATE" / "source-trust-events.jsonl"
SOURCES = ROOT / "runtime" / "specs" / "source-trust-sources.json"
OUT = ROOT / "runtime" / "specs" / "source-trust.json"
HALF_LIFE = 90.0
W_FALSIFIED, W_CONFIRMED = 1.0, 0.1
A0, B0 = 1.0, 1.0   # Beta-style prior pseudo-counts (falsified, confirmed): unknown source = 0.5


def load_events(path: Path = EVENTS) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    for i, l in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not l.strip():
            continue
        d = json.loads(l)
        for k in ("ts", "source", "outcome", "claim", "ref"):
            if k not in d:
                raise SystemExit(f"events line {i}: missing {k}")
        if d["outcome"] not in ("falsified", "confirmed"):
            raise SystemExit(f"events line {i}: outcome must be falsified|confirmed")
        rows.append(d)
    return rows


def derive(sources: dict, events: list[dict], today: dt.date) -> dict:
    per: dict[str, dict] = {k: {"wf": 0.0, "wc": 0.0, "falsified": 0, "confirmed": 0, "last_falsified": None, "last_confirmed": None}
                            for k in sources["sources"]}
    unknown = sorted({e["source"] for e in events} - set(per))
    if unknown:
        raise SystemExit(f"events name sources not in the registry: {unknown} (add them to {SOURCES.name})")
    for e in events:
        age = (today - dt.date.fromisoformat(e["ts"])).days
        decay = math.exp(-max(age, 0) / HALF_LIFE)
        p = per[e["source"]]
        if e["outcome"] == "falsified":
            p["wf"] += W_FALSIFIED * decay; p["falsified"] += 1
            p["last_falsified"] = max(p["last_falsified"] or "", e["ts"])
        else:
            p["wc"] += W_CONFIRMED * decay; p["confirmed"] += 1
            p["last_confirmed"] = max(p["last_confirmed"] or "", e["ts"])
    table = {}
    for k, p in per.items():
        meta = sources["sources"][k]
        susp = (A0 + p["wf"]) / (A0 + B0 + p["wf"] + p["wc"])
        if meta.get("pinned_tier"):
            tier = meta["pinned_tier"]
        elif p["wf"] >= 3 and p["wc"] == 0:
            tier = "ZERO-WEIGHT"
        elif susp > 0.6:
            tier = "ELEVATED"
        elif susp > 0.3:
            tier = "STANDARD"
        else:
            tier = "LOW"
        table[k] = {"label": meta["label"], "kind": meta["kind"], "tier": tier, "suspicion": round(susp, 3),
                    "falsified": p["falsified"], "confirmed": p["confirmed"],
                    "last_falsified": p["last_falsified"], "last_confirmed": p["last_confirmed"],
                    "pinned_reason": meta.get("pinned_reason"),
                    "verification_demand": {"ZERO-WEIGHT": "every claim needs an independent primary record; the source's word counts for nothing",
                                            "ELEVATED": "every claim needs a grep or a sha before it enters what_confirmed",
                                            "STANDARD": "spot-check load-bearing claims; unbacked claims stay what_unconfirmed",
                                            "LOW": "accept into what_unconfirmed freely; integrity gate still applies to what_confirmed"}[tier]}
    return {"$schema": "arcs-source-trust/v1", "generated_from": [str(EVENTS.relative_to(ROOT)), str(SOURCES.relative_to(ROOT))],
            "generator": "scripts/source_trust_emit.py", "derivation": "asymmetric decayed counts; see script docstring",
            "half_life_days": HALF_LIFE, "weights": {"falsified": W_FALSIFIED, "confirmed": W_CONFIRMED},
            "sources": table}


def render(today: dt.date | None = None) -> dict:
    today = today or dt.date.today()
    return derive(json.loads(SOURCES.read_text(encoding="utf-8")), load_events(), today)


def _strip(d: dict) -> dict:
    # suspicion decays with wall-clock; compare tiers + counts, not the float
    return {k: {kk: vv for kk, vv in v.items() if kk != "suspicion"} for k, v in d["sources"].items()}


def _parser():
    import argparse
    ap = argparse.ArgumentParser(prog="source_trust_emit.py", description="per-source trust as a GENERATED table")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="exit 1 if the generated table is stale (writes nothing)")
    mode.add_argument("--self-test", action="store_true", help="run the derivation + CLI self-test in a temp dir")
    sub = ap.add_subparsers(dest="cmd")
    add = sub.add_parser("add", help="append an event")
    add.add_argument("source")
    add.add_argument("outcome")
    add.add_argument("claim")
    add.add_argument("ref")
    return ap


def main(argv: list[str]) -> int:
    ap = _parser()
    args = ap.parse_args(argv)
    if args.cmd and (args.check or args.self_test):
        ap.error("add cannot be combined with --check or --self-test")
    if args.self_test:
        return self_test()
    if args.cmd == "add":
        ev = {"ts": dt.date.today().isoformat(), "source": args.source, "outcome": args.outcome, "claim": args.claim, "ref": args.ref}
        srcs = json.loads(SOURCES.read_text(encoding="utf-8"))["sources"]
        if ev["source"] not in srcs or ev["outcome"] not in ("falsified", "confirmed"):
            print(f"unknown source or outcome; sources: {sorted(srcs)}", file=sys.stderr); return 2
        EVENTS.parent.mkdir(parents=True, exist_ok=True)
        EVENTS.open("a", encoding="utf-8").write(json.dumps(ev, ensure_ascii=False) + "\n")
        print("appended; now regenerate: python3 scripts/source_trust_emit.py"); return 0
    table = render()
    text = json.dumps(table, indent=2, ensure_ascii=False) + "\n"
    if args.check:
        if not OUT.exists():
            print("source-trust.json missing", file=sys.stderr); return 1
        cur = json.loads(OUT.read_text(encoding="utf-8"))
        if _strip(cur) != _strip(table):
            print("runtime/specs/source-trust.json is stale vs the events/sources. Regenerate: python3 scripts/source_trust_emit.py", file=sys.stderr); return 1
        print(f"source-trust OK ({len(table['sources'])} sources: " + ", ".join(f"{k}={v['tier']}" for k, v in table["sources"].items()) + ")")
        return 0
    OUT.write_text(text, encoding="utf-8")
    for k, v in table["sources"].items():
        print(f"  {k:<18} {v['tier']:<12} suspicion={v['suspicion']:<6} falsified={v['falsified']} confirmed={v['confirmed']}")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


def _cli_self_test(check) -> None:
    """Run a copy of this script inside a throwaway tree (ROOT is script-relative). Never touches the real repo."""
    import hashlib, shutil, subprocess, tempfile

    def snap(root: Path) -> dict:
        return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in sorted(root.rglob("*")) if p.is_file() and "__pycache__" not in p.parts}

    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        (t / "scripts").mkdir(); (t / "_STATE").mkdir(); (t / "runtime" / "specs").mkdir(parents=True)
        me = t / "scripts" / "source_trust_emit.py"
        shutil.copy2(Path(__file__).resolve(), me)
        (t / "runtime" / "specs" / "source-trust-sources.json").write_text(json.dumps({"sources": {"s1": {"label": "S", "kind": "agent"}}}), encoding="utf-8")
        (t / "_STATE" / "source-trust-events.jsonl").write_text(json.dumps({"ts": "2026-09-27", "source": "s1", "outcome": "falsified", "claim": "c", "ref": "r"}) + "\n", encoding="utf-8")

        def run(*a):
            return subprocess.run([sys.executable, "-B", str(me), *a], capture_output=True, text=True, cwd=tmp)

        before = snap(t)
        check("CLI: unknown flag exits 2", run("--chek").returncode == 2)
        check("CLI: extra positional exits 2", run("bogus").returncode == 2)
        check("CLI: --check with extra positional exits 2", run("--check", "extra").returncode == 2)
        check("CLI: add with too few args exits 2", run("add", "s1", "falsified").returncode == 2)
        check("CLI: add with extra arg exits 2", run("add", "s1", "falsified", "c", "r", "x").returncode == 2)
        check("CLI: add with bad outcome exits 2", run("add", "s1", "maybe", "c", "r").returncode == 2)
        r = run("--check")
        check("CLI: --check on a missing table exits 1", r.returncode == 1)
        check("CLI: rejected calls and --check wrote nothing", snap(t) == before)
        check("CLI: regenerate exits 0 and writes the table", run().returncode == 0 and (t / "runtime" / "specs" / "source-trust.json").exists())
        mid = snap(t)
        r = run("--check")
        check("CLI: --check on a fresh table exits 0", r.returncode == 0, r.stderr.strip())
        check("CLI: --check (fresh) wrote nothing", snap(t) == mid)


def self_test() -> int:
    today = dt.date(2026, 9, 27)
    srcs = {"sources": {"liar": {"label": "L", "kind": "external"}, "saint": {"label": "S", "kind": "human"},
                        "blank": {"label": "B", "kind": "agent"}, "pinned": {"label": "P", "kind": "harness", "pinned_tier": "ZERO-WEIGHT", "pinned_reason": "ruling"}}}
    ev = [{"ts": "2026-09-27", "source": "liar", "outcome": "falsified", "claim": "x", "ref": "F1"}] * 3 + \
         [{"ts": "2026-09-27", "source": "saint", "outcome": "confirmed", "claim": "y", "ref": "r"}] * 20 + \
         [{"ts": "2026-09-27", "source": "saint", "outcome": "falsified", "claim": "z", "ref": "F2"}]
    t = derive(srcs, ev, today)["sources"]
    fails = total = 0
    def check(label, cond, detail=""):
        nonlocal fails, total
        total += 1
        print(f"  {'PASS' if cond else 'FAIL'}  {label}  {detail}")
        fails += 0 if cond else 1
    check("3 falsifications, 0 confirmations -> ZERO-WEIGHT", t["liar"]["tier"] == "ZERO-WEIGHT", t["liar"])
    check("20 confirmations + 1 falsification -> still not LOW (asymmetry 10:1)", t["saint"]["tier"] in ("STANDARD", "ELEVATED"), t["saint"])
    check("no history -> STANDARD at 0.5: unknown is spot-checked, neither trusted nor damned", t["blank"]["tier"] == "STANDARD" and t["blank"]["suspicion"] == 0.5, t["blank"])
    check("pinned tier wins", t["pinned"]["tier"] == "ZERO-WEIGHT" and t["pinned"]["pinned_reason"] == "ruling")
    old = derive(srcs, [{"ts": "2025-09-27", "source": "liar", "outcome": "falsified", "claim": "x", "ref": "F1"}], today)["sources"]["liar"]
    fresh = derive(srcs, [{"ts": "2026-09-27", "source": "liar", "outcome": "falsified", "claim": "x", "ref": "F1"}], today)["sources"]["liar"]
    check("a falsification decays with age (1y-old reads below a fresh one, and below ELEVATED)", old["suspicion"] < fresh["suspicion"] and old["tier"] != "ELEVATED", (old["suspicion"], fresh["suspicion"]))
    saint = derive(srcs, [{"ts": "2026-09-27", "source": "saint", "outcome": "confirmed", "claim": "y", "ref": "r"}] * 50, today)["sources"]["saint"]
    check("50 confirmations, 0 falsifications -> LOW", saint["tier"] == "LOW", saint["suspicion"])
    try:
        derive(srcs, [{"ts": "2026-09-27", "source": "ghost", "outcome": "falsified", "claim": "x", "ref": "F1"}], today); check("unknown source rejected", False)
    except SystemExit:
        check("unknown source rejected", True)
    _cli_self_test(check)
    print(f"source_trust_emit self-test: {total - fails}/{total}")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
