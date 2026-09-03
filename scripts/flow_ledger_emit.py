#!/usr/bin/env python3
"""flow_ledger_emit.py — read commit trailers back into arcs.trajectory.v1 metrics.

Groups commits by Claude-Session trailer (falling back to day), and emits one span per session
with the honest-null metric contract: a metric is null when it was never instrumented, never 0.

  commits     count of commits carrying that session (git, always available)
  turns       max Flow-Turns seen in the session (null if no commit carried it)
  flow_ratio  commits / turns (null until turns exists)
  nci         median of [NCI:NN] subject tags, ignoring [NCI:SKIP] (null if none scored)

Usage:  python3 scripts/flow_ledger_emit.py [--since 30.days] [--json runtime/specs/flow-ledger.json]
Deterministic: same log -> same output (run-twice-diff clean). stdlib only.
"""
import argparse, json, re, statistics, subprocess, sys
from collections import defaultdict

SEP = "\x1e"
def git_log(since):
    fmt = f"%H{SEP}%ad{SEP}%s{SEP}%(trailers:key=Claude-Session,valueonly){SEP}%(trailers:key=Flow-Turns,valueonly){SEP}%(trailers:key=Span,valueonly)%x00"
    out = subprocess.run(["git","log",f"--since={since}","--date=short",f"--format={fmt}"],capture_output=True,text=True,check=True).stdout
    for rec in out.split("\x00"):
        rec = rec.strip("\n")
        if not rec: continue
        h, day, subj, ses, turns, span = (rec.split(SEP)+[""]*6)[:6]
        yield dict(hash=h, day=day, subject=subj, session=ses.strip(), turns=turns.strip(), span=span.strip())

def nci_of(subject):
    m = re.search(r"\[NCI:(\d+)", subject)
    return int(m.group(1)) if m else None

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--since", default="90.days"); ap.add_argument("--json", default=None)
    a = ap.parse_args()
    spans = defaultdict(lambda: dict(commits=0, turns=[], nci=[], days=set(), kind="session"))
    for c in git_log(a.since):
        key = c["session"] or f"day:{c['day']}"
        s = spans[key]; s["commits"] += 1; s["days"].add(c["day"])
        if not c["session"]: s["kind"] = "day"
        if c["turns"].isdigit(): s["turns"].append(int(c["turns"]))
        n = nci_of(c["subject"])
        if n is not None: s["nci"].append(n)
    rows = []
    for key, s in sorted(spans.items(), key=lambda kv: (min(kv[1]["days"]), kv[0])):
        turns = max(s["turns"]) if s["turns"] else None
        rows.append({
            "schema_version": "arcs.trajectory.v1",
            "span": {"id": key.replace("day:",""), "kind": s["kind"], "frame": "arcs-v9@git",
                     "start": min(s["days"]), "end": max(s["days"]),
                     "provenance": [{"source":"git","confidence":"high"}],
                     "fidelity": "SHARP" if turns is not None else "GRAIN"},
            "metrics": {"turns": turns, "output_units": None, "commits": s["commits"],
                        "flow_ratio": (round(s["commits"]/turns, 3) if turns else None),
                        "nci": (int(statistics.median(s["nci"])) if s["nci"] else None)},
            "zones": [], "receipts": []})
    tagged = sum(1 for r in rows if r["span"]["kind"] == "session")
    print(f"# flow ledger · {len(rows)} spans · {tagged} session-tagged · since {a.since}")
    print("| span | kind | days | commits | turns | flow_ratio | nci |"); print("|---|---|---|---:|---:|---:|---:|")
    for r in rows:
        m = r["metrics"]; sp = r["span"]
        print(f"| {sp['id'][-28:]} | {sp['kind']} | {sp['start']}→{sp['end']} | {m['commits']} | {m['turns'] if m['turns'] is not None else 'null'} | {m['flow_ratio'] if m['flow_ratio'] is not None else 'null'} | {m['nci'] if m['nci'] is not None else 'null'} |")
    if a.json:
        json.dump({"generated_from": "git log", "since": a.since, "spans": rows}, open(a.json,"w"), indent=1)
        print(f"wrote {a.json}")

if __name__ == "__main__": main()
