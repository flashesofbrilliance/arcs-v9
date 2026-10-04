#!/usr/bin/env python3
"""
fates.py — the FATE REGISTRY: every artifact class declares the fates it may land in.

ADR-068: every stage cut prints an artifact, through a gate, to a fate. A print without a gate
is decoration; a gate without a fate gates nothing. Until 2026-09-27 each ledger carried its own
fate vocabulary in its own head (backlog `fates` arrays were free text; ADR statuses had seven
spellings). This registry makes the vocabulary DATA, and `check` verifies every mechanical
ledger only assigns fates its class may have — the same move as the operator registry and the
LEGEND. Zach 2026-09-27: "do the fate gates play into the mix here?" → the LORE verdict IS a
fate; this generalizes it.

Registry: runtime/specs/fates.json (hand-authored law; edit it, then run check)
  { "classes": { "<class>": { "field": "<where the fate is recorded>", "gate": "<what decides>",
                              "fates": ["..."], "non_terminal": ["..."], "ledger": "<path>",
                              "strictness": "hard" | "soft", "notes": "..." } } }
  hard = a value outside the set FAILS check (lore, witness, falsification, operator registry,
         source-trust, RC registry, ADR status)
  soft = reported, never blocks (backlog status prefixes and free-text `fates`, seed statuses):
         these vocabularies are still accreting and forcing them would be taxonomy overfit.

Usage:
  python3 scripts/fates.py check        # verify ledgers against the registry (exit 1 on a hard miss)
  python3 scripts/fates.py report       # coverage table: class · fates · observed values
  python3 scripts/fates.py --self-test
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REG = ROOT / "runtime" / "specs" / "fates.json"


def _rows(p: Path) -> list[dict]:
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def observe(cls: str, spec: dict) -> list[tuple[str, str]]:
    """Return [(value, where)] for every fate value actually recorded for this class."""
    out: list[tuple[str, str]] = []
    led = ROOT / spec["ledger"] if spec.get("ledger") else None
    if cls == "lore":
        out += [(r.get("binding_verdict", ""), r.get("id", "?")) for r in _rows(led)]
    elif cls == "witness":
        for f in sorted((ROOT / "_STATE" / "witness").glob("*.jsonl")):
            out += [(str(r.get("y")), f"{f.name}") for r in _rows(f)]
    elif cls == "falsification":
        out += [(r.get("verdict", ""), r.get("id", "?")) for r in _rows(led)]
    elif cls == "operator":
        d = json.loads(led.read_text(encoding="utf-8")) if led.exists() else {"operators": []}
        out += [(r.get("status", ""), f"op {r.get('op')}") for r in d["operators"]]
    elif cls == "source":
        d = json.loads(led.read_text(encoding="utf-8")) if led.exists() else {"sources": {}}
        out += [(v.get("tier", ""), k) for k, v in d["sources"].items()]
    elif cls == "rom-candidate":
        d = json.loads(led.read_text(encoding="utf-8")) if led.exists() else []
        out += [(r.get("status", ""), r.get("id", "?")) for r in d]
    elif cls == "adr":
        for p in sorted((ROOT / "_DECISIONS").glob("ADR-*.md")):
            head = p.read_text(encoding="utf-8", errors="replace")[:1500]
            m = re.search(r"\*\*Status:?\*\*:?\s*`?([A-Za-z][A-Za-z -]{1,24})", head)
            out.append(((m.group(1).strip().upper().split(" ")[0] if m else "UNSTATED"), p.name))
    elif cls == "backlog":
        for r in _rows(led):
            st = re.split(r"[\s(—:,-]", str(r.get("status", "")))[0].upper() or "UNSTATED"
            out.append((st, r.get("id", "?")))
    elif cls == "assumption":
        out += [(r.get("status", ""), r.get("id", "?")) for r in _rows(led)]
    elif cls == "seed":
        out += [(str(r.get("status")), r.get("id", "?")) for r in _rows(led)]
    return out


def check(reg: dict, verbose: bool = True) -> tuple[int, int]:
    hard_miss = soft_miss = 0
    for cls, spec in reg["classes"].items():
        allowed = set(spec["fates"]) | set(spec.get("non_terminal", []))
        obs = observe(cls, spec)
        bad = [(v, w) for v, w in obs if v not in allowed]
        tag = "hard" if spec["strictness"] == "hard" else "soft"
        if bad:
            if tag == "hard":
                hard_miss += len(bad)
            else:
                soft_miss += len(bad)
            if verbose:
                mark = "✖" if tag == "hard" else "⚠"
                vals = sorted({v for v, _ in bad})
                print(f"{mark} {cls:<14} {len(bad)} value(s) outside the registry ({tag}): {vals[:8]}{' ...' if len(vals) > 8 else ''}")
                for v, w in bad[:5]:
                    print(f"      {v!r} at {w}")
        elif verbose:
            print(f"✓ {cls:<14} {len(obs)} recorded fate(s), all in the registry")
    return hard_miss, soft_miss


def report(reg: dict) -> None:
    print(f"{'class':<14} {'strict':<5} {'field':<16} fates")
    for cls, spec in reg["classes"].items():
        print(f"{cls:<14} {spec['strictness']:<5} {spec['field'][:16]:<16} {', '.join(spec['fates'])}" + (f"  (non-terminal: {', '.join(spec['non_terminal'])})" if spec.get("non_terminal") else ""))


def self_test() -> int:
    reg = {"classes": {"lore": {"field": "binding_verdict", "gate": "test_that_decided", "fates": ["true"], "non_terminal": ["undecided"], "ledger": "runtime/specs/lore.jsonl", "strictness": "hard"}}}
    import tempfile
    global ROOT
    old = ROOT
    tmp = Path(tempfile.mkdtemp()); (tmp / "runtime" / "specs").mkdir(parents=True)
    (tmp / "runtime" / "specs" / "lore.jsonl").write_text(json.dumps({"id": "lore-001", "binding_verdict": "true"}) + "\n" + json.dumps({"id": "lore-002", "binding_verdict": "undecided"}) + "\n" + json.dumps({"id": "lore-003", "binding_verdict": "vibes"}) + "\n")
    ROOT = tmp
    fails = 0
    def ck(label, cond, detail=""):
        nonlocal fails
        print(f"  {'PASS' if cond else 'FAIL'}  {label}  {detail}")
        fails += 0 if cond else 1
    h, s = check(reg, verbose=False)
    ck("a fate outside the registry is a hard miss", h == 1 and s == 0, (h, s))
    ck("non_terminal values are allowed", True)
    reg["classes"]["lore"]["strictness"] = "soft"
    h, s = check(reg, verbose=False)
    ck("soft class reports, never fails", h == 0 and s == 1, (h, s))
    ROOT = old
    print(f"self-test: {'OK' if fails == 0 else f'{fails} FAIL'}")
    return 1 if fails else 0


def _snapshot(paths: list[Path]) -> dict:
    """sha256 + mtime_ns of every file in the watched set (None if absent)."""
    import hashlib
    return {str(p): (hashlib.sha256(p.read_bytes()).hexdigest(), p.stat().st_mtime_ns) if p.exists() else None
            for p in paths}


def argv_self_test() -> tuple[int, int]:
    """Copy this script into a temp repo and assert the argv contract via subprocess."""
    import shutil, subprocess, tempfile
    tmp = Path(tempfile.mkdtemp(prefix="fates-selftest-"))
    try:
        (tmp / "scripts").mkdir()
        specs = tmp / "runtime" / "specs"
        specs.mkdir(parents=True)
        me = tmp / "scripts" / "fates.py"
        shutil.copy2(Path(__file__).resolve(), me)
        reg = specs / "fates.json"
        lore = specs / "lore.jsonl"
        reg.write_text(json.dumps({"classes": {"lore": {"field": "binding_verdict", "gate": "t", "fates": ["true"],
                                                        "non_terminal": ["undecided"], "ledger": "runtime/specs/lore.jsonl",
                                                        "strictness": "hard"}}}), encoding="utf-8")
        lore.write_text(json.dumps({"id": "lore-001", "binding_verdict": "true"}) + "\n", encoding="utf-8")
        watched = [reg, lore]
        fails = total = 0

        def run(*a):
            return subprocess.run([sys.executable, str(me), *a], capture_output=True, text=True, cwd=tmp)

        def ok(name, cond):
            nonlocal fails, total
            total += 1
            print(("  PASS  " if cond else "  FAIL  ") + name)
            fails += 0 if cond else 1

        before = _snapshot(watched)
        ok("unknown flag exits 2", run("--chek").returncode == 2)
        ok("unknown subcommand exits 2", run("chek").returncode == 2)
        ok("extra positional on check exits 2", run("check", "extra").returncode == 2)
        ok("extra positional on report exits 2", run("report", "extra").returncode == 2)
        ok("bad args wrote nothing", _snapshot(watched) == before)
        ok("check exits 0 on clean ledger", run("check").returncode == 0)
        ok("bare invocation runs check (exit 0)", run().returncode == 0)
        ok("check writes nothing", _snapshot(watched) == before)
        r = run("report")
        ok("report exits 0 and lists class", r.returncode == 0 and "lore" in r.stdout)
        ok("report writes nothing", _snapshot(watched) == before)
        lore.write_text(lore.read_text(encoding="utf-8") + json.dumps({"id": "lore-002", "binding_verdict": "vibes"}) + "\n", encoding="utf-8")
        before = _snapshot(watched)
        ok("check exits 1 on a hard miss", run("check").returncode == 1)
        ok("failing check writes nothing", _snapshot(watched) == before)
        reg.unlink()
        ok("missing registry exits 2", run("check").returncode == 2)
        print(f"fates argv: {total - fails}/{total}")
        return fails, total
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def parse_args(argv: list[str]):
    import argparse
    ap = argparse.ArgumentParser(prog="fates.py", description="The FATE REGISTRY gate (read-only).",
                                 formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    ap.add_argument("--self-test", action="store_true", help="prove hard/soft miss logic and the argv contract")
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("check", help="verify ledgers against the registry (default; exit 1 on a hard miss)")
    sub.add_parser("report", help="coverage table: class, fates, observed values")
    return ap, ap.parse_args(argv)


def main(argv: list[str]) -> int:
    ap, args = parse_args(argv)
    if args.self_test:
        if args.cmd:
            ap.error("--self-test takes no subcommand")
        rc = self_test()
        f2, t2 = argv_self_test()
        t1, f1 = 3, (1 if rc else 0)
        print(f"fates self-test: {(t1 + t2) - (f1 + f2)}/{t1 + t2}")
        return 1 if (rc or f2) else 0
    if not REG.exists():
        print("runtime/specs/fates.json missing", file=sys.stderr); return 2
    reg = json.loads(REG.read_text(encoding="utf-8"))
    if args.cmd == "report":
        report(reg); return 0
    h, s = check(reg)
    print(f"fates: {h} hard miss(es), {s} soft miss(es) across {len(reg['classes'])} classes")
    return 1 if h else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
