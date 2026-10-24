#!/usr/bin/env python3
"""risk_underwriter.py: price each induced-backlog row's risk. Read-only, stdlib, no model calls.

v0 of the risk underwriter (_PROPOSALS/2026-10-20-risk-underwriter-agent.md, PR #1694). It prices;
it never decides. It writes nothing to any row and keeps no ledger yet (no loading from pathogen
findings or kintsugi repairs: that is gap 2 of the proposal, so every price here has loading 0).

Pricing table v0 (proposal section 2, pre-registered; changed only by Zach's ruling):
  exposure          door      cover present               premium (coins)
  ruin low/blank    two-way   any gate                    0
  ruin medium       two-way   gate + rollback             1
  ruin medium       two-way   gate only                   2
  ruin high         two-way   gate + rollback + abort     3
  any               one-way   gate + abort + write-lock   4
  ruin high         one-way   no rollback, gate + abort   SPECIALTY (Zach 2026-10-20: a bespoke rider,
                                                          priced case by case; riders listed)
  ruin high         one-way   no rollback, no gate/abort  UNINSURABLE (shown, never blocked)
A blank door prices as two-way. A blank ruin on a two-way row prints UNPRICED, never 0 coins: an empty
exposure field is unmeasured, not safe (hardening 2026-10-20). A one-way row still prices from the door.
Cover written as "DRAFT ... unreviewed" counts, and is flagged. Missing cover is listed, never
filled in. Write-lock is never on a row today, so a one-way door always lists it as missing.

Durations and critical path (--path ROOT), three-point table v0, pre-registered 2026-10-20, in work hours:
  one value v (min, h, session = 2 h, d = 6 h)   best 0.5 v, likely v, worst 3 v
  range a to b                                   best a, likely (a + b) / 2, worst 2 b
  trivial 0.1/0.25/0.5 · small 0.5/1/3 · medium 2/4/10 · large 8/16/40
  "each" is per item with an unknown count: priced as one item and flagged
  "ongoing", or a row waiting on outside arrivals (jtbd says n>=): WAIT, never estimated
  tbd, blank or unparsed: UNKNOWN, never guessed
The critical path walks depends_on upstream of ROOT over non-terminal rows and takes the longest
chain per case. A path holding any WAIT or UNKNOWN row is reported as incomplete, with the rows named.

usage:
  risk_underwriter.py [--file F] [--ids a,b,c] [--all] [--json]
  risk_underwriter.py --path ROOT [--file F]
  risk_underwriter.py --self-test
With no --ids and no --all it prices the non-terminal rows that carry any risk field.
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_FILE = ROOT / "_QUEUE" / "induced-backlog.jsonl"
TERMINAL = {"DONE", "COMPOSTED", "SUPERSEDED"}
POLICY_VERSION = "v0-2026-10-20"
NO_ROLLBACK = re.compile(r"^\s*(?:DRAFT[^:]*:\s*)?(?:none|no rollback|cannot be undone)\b", re.I)
DRAFT = re.compile(r"\bDRAFT\b.*\bunreviewed\b", re.I | re.S)


def _text(v):
    if v is None:
        return ""
    if isinstance(v, list):
        return " ".join(str(x) for x in v)
    return str(v)


def price(row):
    ruin = (row.get("ruin") or "").strip().lower() or None
    door = (row.get("door") or "").strip().lower() or None
    gates = row.get("gates") or []
    rollback, abort = _text(row.get("rollback")), _text(row.get("abort"))
    has_gate, has_abort = bool(gates), bool(abort.strip())
    has_rollback = bool(rollback.strip()) and not NO_ROLLBACK.search(rollback)
    flags, missing = [], []
    if ruin is None:
        flags.append("exposure unpriced (ruin blank)")
    if door is None:
        flags.append("door blank, priced as two-way")
    if any(DRAFT.search(t) for t in (rollback, abort)):
        flags.append("cover is DRAFT, unreviewed")
    if rollback.strip() and not has_rollback:
        flags.append("rollback says none is possible")

    if door == "one-way":
        if ruin == "high" and not has_rollback:
            if has_gate and has_abort:
                riders = ["write-lock", "ex-ante receipt", "Zach reads before the act"]
                return _out(row, ruin, door, "SPECIALTY", flags, riders)
            return _out(row, ruin, door, "UNINSURABLE", flags, ["rollback (none possible)"] +
                        [n for n, ok in (("gate", has_gate), ("abort", has_abort)) if not ok])
        premium = 4
        for name, ok in (("gate", has_gate), ("abort", has_abort), ("write-lock", False)):
            if not ok:
                missing.append(name)
    elif ruin == "high":
        premium = 3
        for name, ok in (("gate", has_gate), ("rollback", has_rollback), ("abort", has_abort)):
            if not ok:
                missing.append(name)
    elif ruin == "medium":
        premium = 1 if (has_gate and has_rollback) else 2
        if not has_gate:
            missing.append("gate")
    elif ruin is None:
        premium = "UNPRICED"
        if not has_gate:
            missing.append("gate")
    else:
        premium = 0
        if not has_gate:
            missing.append("gate")
    return _out(row, ruin, door, premium, flags, missing)


def _out(row, ruin, door, premium, flags, missing):
    return {"id": row.get("id"), "state": row.get("state"), "ruin": ruin, "door": door,
            "premium": premium, "loading": 0, "missing_cover": missing, "flags": flags,
            "policy_version": POLICY_VERSION}


UNIT_H = {"min": 1 / 60, "h": 1.0, "session": 2.0, "d": 6.0}
WORDS = {"trivial": (0.1, 0.25, 0.5), "small": (0.5, 1, 3), "medium": (2, 4, 10), "large": (8, 16, 40)}
NUM_UNIT = re.compile(r"(\d+(?:\.\d+)?)\s*(?:(?:to|-)\s*(\d+(?:\.\d+)?)\s*)?(min|h|sessions?|d)\b", re.I)


def duration(row):
    """(best, likely, worst) work hours, or 'WAIT' / 'UNKNOWN', plus flags."""
    cp = str(row.get("cost_prior") or "").strip()
    flags = []
    if "ongoing" in cp.lower() or re.search(r"n\s*>=\s*\d+", str(row.get("jtbd") or "")):
        return "WAIT", ["waits on outside arrivals"]
    if cp.lower() in WORDS:
        return WORDS[cp.lower()], flags
    m = NUM_UNIT.search(cp)
    if not m:
        return "UNKNOWN", [f"cost_prior unparsed: {cp or 'blank'}"]
    unit = m.group(3).lower().rstrip("s").replace("sessio", "session")
    k = UNIT_H["session" if unit.startswith("session") else unit]
    a = float(m.group(1)) * k
    if unit == "d":
        flags.append("d read as 6 work hours")
    if re.search(r"\beach\b", cp):
        flags.append("per item, count unknown: priced as one")
    if m.group(2):
        b = float(m.group(2)) * k
        return (a, (a + b) / 2, 2 * b), flags
    return (0.5 * a, a, 3 * a), flags


def critical_path(rows, root):
    by = {r.get("id"): r for r in rows}
    if root not in by:
        raise SystemExit(f"risk_underwriter: unknown row id: {root}")
    memo = {}

    def walk(i, seen=()):
        if i in memo:
            return memo[i]
        r = by.get(i)
        if r is None or r.get("state") in TERMINAL or i in seen:
            return [0.0, 0.0, 0.0], [[], [], []], set()
        d, _ = duration(r)
        holes = {i} if isinstance(d, str) else set()
        own = (0.0, 0.0, 0.0) if isinstance(d, str) else d
        best = [0.0, 0.0, 0.0]
        chain = [[], [], []]
        for j in r.get("depends_on") or []:
            t, c, h = walk(j, seen + (i,))
            holes |= h
            for k in range(3):
                if t[k] > best[k] or not chain[k]:
                    if t[k] >= best[k]:
                        best[k], chain[k] = t[k], c[k]
        res = ([best[k] + own[k] for k in range(3)], [chain[k] + [i] for k in range(3)], holes)
        memo[i] = res
        return res

    totals, chains, holes = walk(root)
    return {"root": root, "best_h": round(totals[0], 2), "likely_h": round(totals[1], 2),
            "worst_h": round(totals[2], 2), "chains": {"best": chains[0], "likely": chains[1], "worst": chains[2]},
            "incomplete": sorted(holes)}


def render_path(cp, rows):
    by = {r.get("id"): r for r in rows}
    out = [f"critical path to {cp['root']} (work hours, longest dependency chain per case)",
           f"  best {cp['best_h']} h · likely {cp['likely_h']} h · worst {cp['worst_h']} h"]
    for case in ("best", "likely", "worst"):
        out.append(f"  {case:<6} chain: {' > '.join(cp['chains'][case])}")
    for i in cp["chains"]["likely"]:
        d, f = duration(by[i])
        shown = d if isinstance(d, str) else "/".join(f"{x:g}" for x in d) + " h"
        out.append(f"    {i:<44} {shown}" + (f"  ({'; '.join(f)})" if f else ""))
    if cp["incomplete"]:
        out.append(f"  INCOMPLETE: no estimate for {', '.join(cp['incomplete'])}; totals cover only the estimated rows")
    return "\n".join(out)


def load(path):
    rows = []
    for line in Path(path).read_text().splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def select(rows, ids=None, all_rows=False):
    if ids:
        want = [i.strip() for i in ids.split(",") if i.strip()]
        by = {r.get("id"): r for r in rows}
        missing = [i for i in want if i not in by]
        if missing:
            raise SystemExit(f"risk_underwriter: unknown row id(s): {', '.join(missing)}")
        return [by[i] for i in want]
    live = [r for r in rows if r.get("state") not in TERMINAL]
    if all_rows:
        return live
    keys = ("ruin", "door", "rollback", "abort")
    return [r for r in live if any(r.get(k) for k in keys)]


def render(priced):
    out = [f"risk underwriter {POLICY_VERSION}: {len(priced)} rows priced, loading 0 (no ledger yet). "
           "Prices only; fates stay human."]
    order = {"UNINSURABLE": 0, "SPECIALTY": 1, "UNPRICED": 3}
    for p in sorted(priced, key=lambda x: (order.get(x["premium"], 2), -(x["premium"] if isinstance(x["premium"], int) else 0), x["id"])):
        prem = p["premium"] if isinstance(p["premium"], str) else f"{p['premium']} coins"
        out.append(f"  {p['id']:<44} {prem:<12} door {p['door'] or '-':<8} ruin {p['ruin'] or '-'}")
        if p["missing_cover"]:
            label = "riders required" if p["premium"] == "SPECIALTY" else "missing cover"
            out.append(f"      {label}: {', '.join(p['missing_cover'])}")
        for f in p["flags"]:
            out.append(f"      flag: {f}")
    return "\n".join(out)


def self_test():
    cases = [
        ("blank ruin prints UNPRICED, never 0, lists gate", {"id": "a"},
         lambda p: p["premium"] == "UNPRICED" and "gate" in p["missing_cover"] and any("unpriced" in f for f in p["flags"])),
        ("low two-way with gate prices 0, nothing missing", {"id": "b", "ruin": "low", "door": "two-way", "gates": ["g"]},
         lambda p: p["premium"] == 0 and not p["missing_cover"]),
        ("medium with gate and rollback prices 1", {"id": "c", "ruin": "medium", "gates": ["g"], "rollback": "git revert"},
         lambda p: p["premium"] == 1),
        ("medium with gate only prices 2", {"id": "d", "ruin": "medium", "gates": ["g"]},
         lambda p: p["premium"] == 2),
        ("high two-way with no abort prices 3, lists abort", {"id": "e", "ruin": "high", "door": "two-way", "gates": ["g"], "rollback": "revert"},
         lambda p: p["premium"] == 3 and p["missing_cover"] == ["abort"]),
        ("one-way prices 4 and always lacks write-lock", {"id": "f", "door": "one-way", "gates": ["g"], "abort": "stop"},
         lambda p: p["premium"] == 4 and p["missing_cover"] == ["write-lock"]),
        ("high one-way, no rollback, gate + abort is SPECIALTY with riders",
         {"id": "g", "ruin": "high", "door": "one-way", "gates": ["g"], "abort": "stop", "rollback": "DRAFT (x, unreviewed): none once sent"},
         lambda p: p["premium"] == "SPECIALTY" and "write-lock" in p["missing_cover"]),
        ("high one-way, no rollback, no abort is UNINSURABLE",
         {"id": "g2", "ruin": "high", "door": "one-way", "gates": ["g"], "rollback": "none"},
         lambda p: p["premium"] == "UNINSURABLE" and "abort" in p["missing_cover"]),
        ("'none' rollback does not count as cover on medium", {"id": "h", "ruin": "medium", "gates": ["g"], "rollback": "none"},
         lambda p: p["premium"] == 2 and any("none is possible" in f for f in p["flags"])),
        ("DRAFT unreviewed cover is flagged", {"id": "i", "ruin": "low", "gates": ["g"], "abort": "DRAFT (Claude, unreviewed): stop"},
         lambda p: any("DRAFT" in f for f in p["flags"])),
    ]
    bad = [name for name, row, ok in cases if not ok(price(row))]
    dcases = [
        ("'small' maps to 0.5/1/3", {"cost_prior": "small"}, lambda d: d[0] == (0.5, 1, 3)),
        ("'2 to 3 h' maps to 2/2.5/6", {"cost_prior": "author estimate: 2 to 3 h"}, lambda d: d[0] == (2.0, 2.5, 6.0)),
        ("'45 min' maps to 0.375/0.75/2.25", {"cost_prior": "45 min"}, lambda d: tuple(round(x, 3) for x in d[0]) == (0.375, 0.75, 2.25)),
        ("'1 session' maps to 1/2/6", {"cost_prior": "1 session"}, lambda d: d[0] == (1.0, 2.0, 6.0)),
        ("'each' is flagged", {"cost_prior": "author estimate: 1 to 3 h each"}, lambda d: any("per item" in f for f in d[1])),
        ("'tbd' is UNKNOWN, never guessed", {"cost_prior": "tbd"}, lambda d: d[0] == "UNKNOWN"),
        ("'ongoing' is WAIT", {"cost_prior": "ongoing; ~5 min per receipt"}, lambda d: d[0] == "WAIT"),
        ("n>=30 in jtbd is WAIT", {"cost_prior": "small", "jtbd": "once it has n>=30 closed"}, lambda d: d[0] == "WAIT"),
    ]
    bad += [name for name, row, ok in dcases if not ok(duration(row))]
    chain = [{"id": "a", "cost_prior": "1 h"}, {"id": "b", "cost_prior": "2 h", "depends_on": ["a"]},
             {"id": "c", "cost_prior": "tbd", "depends_on": ["b", "z"]}, {"id": "z", "state": "DONE"}]
    cp = critical_path(chain, "c")
    if not (cp["likely_h"] == 3.0 and cp["chains"]["likely"] == ["a", "b", "c"] and cp["incomplete"] == ["c"]):
        bad.append("critical path sums the chain, skips DONE rows, names the hole")
    cases = cases + dcases + [None]
    try:
        select([{"id": "x"}], ids="nope")
        bad.append("unknown id must exit")
    except SystemExit:
        pass
    for name in bad:
        print(f"FAIL {name}", file=sys.stderr)
    print(f"risk_underwriter self-test: {len(cases) + 1 - len(bad)}/{len(cases) + 1} passed")
    return 1 if bad else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="Price induced-backlog row risk (read-only).")
    ap.add_argument("--file", default=str(DEFAULT_FILE))
    ap.add_argument("--ids")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--path", help="critical path, best/likely/worst, upstream of this row id")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    if a.path:
        rows = load(a.file)
        cp = critical_path(rows, a.path)
        print(json.dumps(cp, indent=1) if a.json else render_path(cp, rows))
        return 0
    priced = [price(r) for r in select(load(a.file), a.ids, a.all)]
    print(json.dumps(priced, indent=1) if a.json else render(priced))
    return 0


if __name__ == "__main__":
    sys.exit(main())
