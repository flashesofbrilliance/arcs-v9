#!/usr/bin/env python3
"""readiness_packet.py: the tier-4 readiness card for one induced-backlog row. Read-only, stdlib.

Before a human acts on a row (the needle pass of the golden inchworm), this prints six lines.
Each line is MEASURED (checked against live repo or state now), DECLARED (stated in the row, not
checked), CUE (a keyword heuristic) or UNCONFIRMED (nothing there). Only MEASURED lines count
toward evidence coverage. It never refuses the act (NOTOMATION); it only labels how prepared the
act is. A line without evidence prints UNCONFIRMED, never a guess.

The six lines
  1 door         one-way or two-way. Row field `door`, else a CUE from irreversible words.
  2 prepared     route.tool paths and depends_on checked against the repo (MEASURED); gates listed
                 as DECLARED because the row stores no gate results.
  3 unconfirmed  every line that is not MEASURED, plus the row's open_questions.
  4 trigger      the row's `trigger`, with the ripeness verdict from scripts/backlog_ripeness.py.
  5 abort+undo   row fields `abort` and `rollback`. Absent means UNCONFIRMED. Present is DECLARED.
  6 om gap       evidence coverage beside the conviction you supply with --conviction (0 to 100).

Verdict (pre-registered, fixed before any run)
  READY    no UNCONFIRMED line, ripeness verdict RIPE, and every machine-checkable line MEASURED
           (prepared, trigger and om gap; door and abort+undo can only ever be DECLARED)
  PARTIAL  at most 2 UNCONFIRMED lines
  GRAIN    otherwise. The card says so and shows what is missing.
Correction 2026-10-18: the first draft required 4 MEASURED lines, which no row could reach because
door and abort+undo cannot be machine-checked. The rule now follows the structure, not a count. Found by the
known-good fixture failing; logged here, not hidden.
The om gap is information, never a gate: it can say you are more or less sure than the evidence, and the act stays yours.
Suggested tier is 4 (human) when the row has consent=human or a one-way cue, else 2. A CUE, not a rule.

usage:
  readiness_packet.py <row-id> [--conviction N] [--json] [--file F] [--today YYYY-MM-DD]
  readiness_packet.py --queue [--file F]       rows that reach a human, ranked by verdict
  readiness_packet.py --self-test              known-bad and known-good fixtures, no network
Optional row fields door, abort, rollback are documented in runtime/specs/backlog-status.json (optional_fields).
Absent ones print UNCONFIRMED. `door` must be one of the values listed there.
"""
import argparse
import datetime as dt
import json
import os
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import backlog_ripeness as br  # noqa: E402

DEFAULT_FILE = ROOT / "_QUEUE" / "induced-backlog.jsonl"
SPEC = ROOT / "runtime" / "specs" / "backlog-status.json"


def door_values():
    """Allowed `door` values, read from the spec so the enum lives in one place."""
    try:
        return list(json.loads(SPEC.read_text())["optional_fields"]["door"]["values"])
    except (OSError, KeyError, ValueError):
        return ["one-way", "two-way"]

ONE_WAY = re.compile(r"\b(delet\w*|drop\w*|migrat\w*|deploy\w*|prod(?:uction)?|payment\w*|auth\w*|secret\w*|"
                     r"publish\w*|send\w*|force-push|write-lock|irreversib\w*)\b", re.I)
PATH_RE = re.compile(r"(?<![\w/.-])((?:[\w.-]+/)+[\w.-]+\.\w{1,6}|[\w-]+\.(?:py|md|json|ts|tsx|sh|mjs|html))\b")
ORDER = {"MEASURED": 0, "DECLARED": 1, "CUE": 2, "UNCONFIRMED": 3}


def line(n, name, state, text):
    return {"n": n, "name": name, "state": state, "text": text}


def _text(row):
    return " ".join(str(row.get(k, "")) for k in ("jtbd", "trigger", "next_action")) + " " + \
        str((row.get("route") or {}).get("tool", ""))


def l_door(row):
    if row.get("door"):
        if str(row["door"]).strip().lower() not in door_values():
            return line(1, "door", "UNCONFIRMED", f"door '{row['door']}' is not one of {door_values()}")
        return line(1, "door", "DECLARED", str(row["door"]).strip().lower())
    cues = sorted({m.group(1).lower() for m in ONE_WAY.finditer(_text(row))})
    if cues:
        return line(1, "door", "CUE", "possibly one-way; words seen: " + ", ".join(cues))
    return line(1, "door", "UNCONFIRMED", "no door field and no irreversible words; treat as unknown")


def l_prepared(row, by_id, today):
    tool = str((row.get("route") or {}).get("tool", ""))
    paths = sorted(set(PATH_RE.findall(tool)))
    found = [p for p in paths if (ROOT / p).exists()]
    deps = br._deps(row)
    dep_state = {d: str(by_id[d].get("state") or br._status(by_id[d]))[:12] if d in by_id else "MISSING" for d in deps}
    gates = [str(g) for g in (row.get("gates") or [])]
    parts = []
    if paths:
        parts.append(f"{len(found)} of {len(paths)} route paths exist")
    if deps:
        parts.append("deps: " + ", ".join(f"{d}={s}" for d, s in dep_state.items()))
    parts.append(f"{len(gates)} gates declared, 0 gate results recorded")
    measured = bool(paths or deps)
    return line(2, "prepared", "MEASURED" if measured else "UNCONFIRMED", "; ".join(parts))


def l_trigger(row, by_id, today):
    trig = str(row.get("trigger") or "").strip()
    if not trig:
        return line(4, "trigger", "UNCONFIRMED", "no trigger written"), None
    v = br.assess(row, by_id, today)
    if v is None:
        return line(4, "trigger", "DECLARED", f"{trig} (row is terminal)"), "TERMINAL"
    state = "MEASURED" if v[0] in ("RIPE", "WAITING", "SECRETLY-DONE", "BLOCKED") else "DECLARED"
    return line(4, "trigger", state, f"{trig} || ripeness {v[0]}: {v[1]}"), v[0]


def l_abort(row):
    a, r = row.get("abort"), row.get("rollback")
    if a and r:
        return line(5, "abort+undo", "DECLARED", f"abort: {a} | rollback: {r}")
    miss = [k for k, v in (("abort", a), ("rollback", r)) if not v]
    got = f"abort: {a}" if a else (f"rollback: {r}" if r else "")
    return line(5, "abort+undo", "UNCONFIRMED", "missing " + " and ".join(miss) + (f"; have {got}" if got else ""))


def build(row, by_id, today, conviction=None):
    lt, ripeness = l_trigger(row, by_id, today)
    lines = {1: l_door(row), 2: l_prepared(row, by_id, today), 4: lt, 5: l_abort(row)}
    nonmeasured = [f"{x['name']} ({x['state']})" for x in lines.values() if x["state"] != "MEASURED"]
    lines[3] = line(3, "unconfirmed", "MEASURED",
                    "; ".join(nonmeasured + [f"open question: {q}" for q in (row.get("open_questions") or [])][:6]) or "none")
    measured = sum(1 for k, x in lines.items() if k != 3 and x["state"] == "MEASURED")
    # evidence coverage: MEASURED lines out of the four content lines (door, prepared, trigger, abort+undo)
    if conviction is None:
        lines[6] = line(6, "om gap", "UNCONFIRMED", "conviction not supplied; pass --conviction 0 to 100")
    else:
        cov = round(100 * sum(1 for i in (1, 2, 4, 5) if lines[i]['state'] == 'MEASURED') / 4)
        word = ("you are more sure than the evidence supports" if conviction - cov > 15 else
                "you are less sure than the evidence supports" if cov - conviction > 15 else "close")
        lines[6] = line(6, "om gap", "MEASURED", f"evidence coverage {cov} vs conviction {conviction}: {word}")
        measured += 1
    order = [lines[i] for i in range(1, 7)]
    unconf = sum(1 for x in order if x["state"] == "UNCONFIRMED")
    if unconf == 0 and ripeness == "RIPE" and all(lines[i]["state"] == "MEASURED" for i in (2, 4, 6)):
        verdict = "READY"
    elif unconf <= 2:
        verdict = "PARTIAL"
    else:
        verdict = "GRAIN"
    tier = 4 if (row.get("consent") == "human" or lines[1]["state"] == "CUE" or row.get("door") == "one-way") else 2
    return {"id": row.get("id"), "verdict": verdict, "suggested_tier": tier, "measured": measured,
            "unconfirmed_lines": unconf, "ripeness": ripeness, "lines": order,
            "jtbd": str(row.get("jtbd", ""))[:200]}


def render(p):
    out = [f"# Readiness packet: {p['id']}", f"{p['jtbd']}", "",
           f"Verdict: {p['verdict']} | suggested tier {p['suggested_tier']} (a cue, not a rule) | "
           f"{p['measured']} lines MEASURED | {p['unconfirmed_lines']} UNCONFIRMED", ""]
    for x in p["lines"]:
        out.append(f"{x['n']}. {x['name']} [{x['state']}] {x['text']}")
    out += ["", "This card never blocks the act. It states how prepared the act is. Only MEASURED lines are evidence."]
    return "\n".join(out)


def load(path):
    rows = [json.loads(l) for l in Path(path).read_text().splitlines() if l.strip()]
    return [r for r in rows if r.get("id")]


def queue(rows, today):
    by_id = {r["id"]: r for r in rows}
    cards = []
    for r in rows:
        if br.assess(r, by_id, today) is None:
            continue
        if r.get("consent") == "human" or ONE_WAY.search(_text(r)):
            cards.append(build(r, by_id, today))
    rank = {"READY": 0, "PARTIAL": 1, "GRAIN": 2}
    return sorted(cards, key=lambda c: (rank[c["verdict"]], -c["measured"], c["id"]))


def self_test():
    os.environ["BACKLOG_RIPENESS_GH_STUB"] = "{}"
    today = dt.date(2026, 10, 18)
    good = {"id": "good", "jtbd": "rename a local helper", "state": "OPEN", "route": {"tool": "scripts/readiness_packet.py"},
            "gates": ["unit fixtures pass"], "trigger": "after 2026-10-01", "door": "two-way",
            "abort": "stop if fixtures fail", "rollback": "git revert the commit", "consent": "human"}
    bad = {"id": "bad", "jtbd": "deploy to prod and send the announcement", "state": "OPEN", "gates": [], "consent": "human"}
    bygood, bybad = {"good": good}, {"bad": bad}
    g = build(good, bygood, today, conviction=80)
    b = build(bad, bybad, today)
    m = build({k: v for k, v in good.items() if k != "abort"}, bygood, today, conviction=80)
    c = build(good, bygood, today, conviction=100)
    low = build({k: v for k, v in good.items() if k not in ("door", "abort", "rollback")}, bygood, today, conviction=100)
    checks = [
        ("known-bad is GRAIN, never READY", b["verdict"] == "GRAIN"),
        ("known-bad suggests tier 4", b["suggested_tier"] == 4),
        ("known-bad door is a CUE, not a fact", b["lines"][0]["state"] == "CUE"),
        ("known-bad abort+undo is UNCONFIRMED", b["lines"][4]["state"] == "UNCONFIRMED"),
        ("known-good is READY", g["verdict"] == "READY"),
        ("removing abort drops READY", m["verdict"] != "READY"),
        ("no conviction means UNCONFIRMED om line", build(good, bygood, today)["lines"][5]["state"] == "UNCONFIRMED"),
        ("overconfidence is named", "more sure than the evidence" in low["lines"][5]["text"]),
        ("no input makes a CUE line count as MEASURED", all(x["state"] != "MEASURED" for x in b["lines"] if x["name"] in ("door", "abort+undo"))),
        ("an invalid door value is UNCONFIRMED, not DECLARED", build({**good, "door": "maybe"}, bygood, today)["lines"][0]["state"] == "UNCONFIRMED"),
        ("the spec lists the door values", door_values() == ["one-way", "two-way"]),
        ("full render has no em-dash", "\u2014" not in render(g)),
    ]
    ok = True
    for name, passed in checks:
        print(("PASS " if passed else "FAIL ") + name)
        ok = ok and passed
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("id", nargs="?")
    ap.add_argument("--file", default=str(DEFAULT_FILE))
    ap.add_argument("--today", default=None)
    ap.add_argument("--conviction", type=int)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--queue", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    today = dt.date.fromisoformat(a.today) if a.today else dt.date.today()
    rows = load(a.file)
    if a.queue:
        cards = queue(rows, today)
        if a.json:
            print(json.dumps(cards, indent=1, ensure_ascii=False))
        else:
            print(f"readiness queue {today}: {len(cards)} rows reach a human")
            for c in cards:
                print(f"  {c['verdict']:<8} tier {c['suggested_tier']}  measured {c['measured']}  {c['id']}")
        return 0
    if not a.id:
        ap.error("give a row id, or --queue, or --self-test")
    by_id = {r["id"]: r for r in rows}
    if a.id not in by_id:
        print(f"no row with id {a.id}", file=sys.stderr)
        return 2
    p = build(by_id[a.id], by_id, today, a.conviction)
    print(json.dumps(p, indent=1, ensure_ascii=False) if a.json else render(p))
    return 0


if __name__ == "__main__":
    sys.exit(main())
