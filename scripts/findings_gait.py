#!/usr/bin/env python3
"""findings_gait: an append-only findings ledger driven by the pulse beat (ADR-086 part E).

The detectors (pulse, lattice-drift, seedbank-drift) print findings and nothing closes them.
This ledger gives every finding an owner-or-compost fate and a close, and reads the pulse beat
as a two-phase clock so the Golden Inchworm alternates: EXTEND beat (detect, ingest) then
CONTRACT beat (fate and close). First run is LOOSE: the stretch cap only warns.

Events (one JSON line each, never edited): open | fate | close.
State is folded from events. Stdlib only. Reuses scripts/pulse.py for the beat.

  findings_gait.py open --source S --text T       record a finding
  findings_gait.py ingest FILE.jsonl              open findings from the LAST row of a drift receipt (idempotent)
  findings_gait.py fate ID --owner O --due BEAT   or  --compost SUPERSESSOR
  findings_gait.py close ID --note N
  findings_gait.py plan --days N                  set the race: clear the open findings by beat (now+N); marks 25/50/75/100% aid stations
  findings_gait.py status [--json]                phase, open, oldest age, displacement, warnings
  findings_gait.py --self-test                    runs in a throwaway dir, never touches real state
"""
import argparse, datetime, hashlib, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pulse  # noqa: E402

ROOT = pulse.ROOT
LEDGER = os.environ.get("FINDINGS_LEDGER") or os.path.join(ROOT, "_STATE", "findings.jsonl")
STRETCH_CAP = 10      # advisory only in the loose run
STRETCH_AGE = 3       # beats
WINDOW = 7            # beats for displacement


def _now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _beat():
    return pulse.global_beat(pulse._load())


def _append(ev):
    os.makedirs(os.path.dirname(LEDGER), exist_ok=True)
    with open(LEDGER, "a") as f:
        f.write(json.dumps(ev, sort_keys=True) + "\n")


def _events():
    if not os.path.exists(LEDGER):
        return []
    out = []
    for line in open(LEDGER):
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except ValueError:
                pass
    return out


def fold():
    st = {}
    for ev in _events():
        i = ev.get("id")
        t = ev.get("type")
        if t == "open" and i not in st:
            st[i] = {"id": i, "source": ev["source"], "text": ev["text"], "opened_beat": ev["beat"], "state": "OPEN"}
        elif i in st and t == "fate":
            st[i].update(fate={k: ev[k] for k in ("owner", "due", "compost") if k in ev}, fated_beat=ev["beat"])
        elif i in st and t == "close":
            st[i].update(state="CLOSED", closed_beat=ev["beat"], note=ev.get("note", ""))
    return st


def _plan():
    p = None
    for ev in _events():
        if ev.get("type") == "plan":
            p = ev
    return p


def cmd_plan(days):
    st = fold()
    n = sum(1 for v in st.values() if v["state"] == "OPEN")
    b = _beat()
    _append({"type": "plan", "start_beat": b, "end_beat": b + int(days), "start_open": n, "beat": b, "ts": _now()})
    print(f"race set: {n} open findings, beats {b} to {b + int(days)}")


def pacing(b, open_now, closed_since):
    """Marathon pacing. Even split of start_open over the horizon; the first quarter is allowed to run
    slow (do not go out too fast); aid stations at 25/50/75/100 percent are the check-in points."""
    p = _plan()
    if not p:
        return None
    span = max(1, p["end_beat"] - p["start_beat"])
    frac = min(1.0, max(0.0, (b - p["start_beat"]) / span))
    target = p["start_open"] * frac * (0.6 if frac < 0.25 else 1.0)
    gap = closed_since - target
    stations = [0.25, 0.5, 0.75, 1.0]
    nxt = next((x for x in stations if x > frac), None)
    return {"fraction": round(frac, 2), "target_closed": round(target, 1), "closed": closed_since, "gap": round(gap, 1),
            "next_station": None if nxt is None else {"pct": int(nxt * 100), "beat": p["start_beat"] + round(span * nxt)},
            "wall_risk": frac >= 0.5 and gap < -0.25 * p["start_open"], "start_open": p["start_open"]}


def _fp(source, text):
    return "f-" + hashlib.sha1(f"{source}|{text}".encode()).hexdigest()[:10]


def cmd_open(source, text):
    i = _fp(source, text)
    if i in fold():
        print(f"exists {i}")
        return i
    _append({"type": "open", "id": i, "source": source, "text": text, "beat": _beat(), "ts": _now()})
    print(f"opened {i}")
    return i


def cmd_ingest(path):
    last = None
    for line in open(path):
        if line.strip():
            last = json.loads(line)
    if not last:
        print("no rows")
        return 0
    n = 0
    src = last.get("check", os.path.basename(path))
    for f in last.get("findings", []):
        if f.get("drift", True):
            before = len(fold())
            cmd_open(src, f"[{f.get('claim','?')}] {f.get('detail','')}")
            n += len(fold()) - before
    print(f"ingested {n} new from {src} row dated {last.get('ts','?')}")
    return n


def cmd_fate(i, owner=None, due=None, compost=None):
    if i not in fold():
        sys.exit(f"unknown id {i}")
    if compost:
        _append({"type": "fate", "id": i, "compost": compost, "beat": _beat(), "ts": _now()})
    elif owner and due is not None:
        _append({"type": "fate", "id": i, "owner": owner, "due": int(due), "beat": _beat(), "ts": _now()})
    else:
        sys.exit("fate needs --compost SUPERSESSOR, or --owner and --due BEAT")
    print(f"fated {i}")


def cmd_close(i, note):
    if i not in fold():
        sys.exit(f"unknown id {i}")
    _append({"type": "close", "id": i, "note": note, "beat": _beat(), "ts": _now()})
    print(f"closed {i}")


def status():
    b = _beat()
    st = fold()
    open_ = [v for v in st.values() if v["state"] == "OPEN"]
    unfated = [v for v in open_ if "fate" not in v]
    aged = [v for v in open_ if b - v["opened_beat"] > STRETCH_AGE]
    opened_w = sum(1 for v in st.values() if b - v["opened_beat"] < WINDOW)
    closed_w = sum(1 for v in st.values() if v["state"] == "CLOSED" and b - v["closed_beat"] < WINDOW)
    overdue = [v for v in open_ if "fate" in v and "due" in v["fate"] and b > v["fate"]["due"]]
    warn = []
    if len(aged) > STRETCH_CAP:
        warn.append(f"STRETCH (loose, advisory): {len(aged)} open findings older than {STRETCH_AGE} beats exceed cap {STRETCH_CAP}")
    if overdue:
        warn.append(f"{len(overdue)} fated finding(s) past their due beat")
    if open_ and closed_w == 0:
        warn.append(f"no finding closed in the last {WINDOW} beats (displacement {closed_w - opened_w:+d})")
    since = p0["start_beat"] if (p0 := _plan()) else None
    closed_since = sum(1 for v in st.values() if v["state"] == "CLOSED" and (since is None or v["closed_beat"] >= since)) if since is not None else 0
    pace = pacing(b, len(open_), closed_since)
    if pace and pace["wall_risk"]:
        warn.append("WALL RISK: past halfway and more than a quarter of the field behind pace. Shorten the stride (close small), do not sprint")
    return {"pace": pace, "beat": b, "phase": "EXTEND" if b % 2 == 0 else "CONTRACT", "open": len(open_), "unfated": len(unfated),
            "oldest_age": max((b - v["opened_beat"] for v in open_), default=0),
            "opened_window": opened_w, "closed_window": closed_w, "displacement": closed_w - opened_w,
            "window_beats": WINDOW, "warnings": warn, "mode": "LOOSE"}


def cmd_status(as_json=False):
    s = status()
    if as_json:
        print(json.dumps(s, indent=2))
        return
    print(f"beat {s['beat']} phase {s['phase']} ({s['mode']}) | open {s['open']} (unfated {s['unfated']}) | oldest {s['oldest_age']} beats")
    print(f"last {s['window_beats']} beats: opened {s['opened_window']}, closed {s['closed_window']}, displacement {s['displacement']:+d}")
    pc = s["pace"]
    if pc:
        ns = pc["next_station"]
        print(f"pace: {int(pc['fraction']*100)}% of race, closed {pc['closed']} vs target {pc['target_closed']} ({pc['gap']:+}); " + (f"next aid station {ns['pct']}% at beat {ns['beat']}" if ns else "past the finish"))
    for w in s["warnings"]:
        print("  WARN", w)
    if s["phase"] == "CONTRACT":
        print("  contract beat: give the oldest open finding a fate and close at least one, or print why not")


def self_test():
    import tempfile
    d = tempfile.mkdtemp()
    global LEDGER
    LEDGER = os.path.join(d, "findings.jsonl")
    ok = True

    def check(name, cond):
        nonlocal ok
        print(("PASS " if cond else "FAIL ") + name)
        ok = ok and cond

    a = cmd_open("t", "alpha")
    check("open is idempotent", cmd_open("t", "alpha") == a and len(fold()) == 1)
    cmd_fate(a, owner="zach", due=_beat() + 2)
    check("fate recorded", fold()[a]["fate"]["owner"] == "zach")
    check("status shows open+warns on no close", status()["open"] == 1 and any("no finding closed" in w for w in status()["warnings"]))
    cmd_close(a, "done")
    check("close folds to CLOSED and displacement positive", fold()[a]["state"] == "CLOSED" and status()["displacement"] == 0)
    rp = os.path.join(d, "r.jsonl")
    open(rp, "w").write(json.dumps({"check": "x", "ts": "t", "findings": [{"claim": "c", "drift": True, "detail": "d1"}, {"claim": "c", "drift": False, "detail": "skip"}]}) + "\n")
    check("ingest takes drift rows only", cmd_ingest(rp) == 1 and cmd_ingest(rp) == 0)
    cmd_plan(14)
    pc = status()["pace"]
    check("plan sets pace and next aid station", pc is not None and pc["next_station"]["pct"] == 25 and pc["wall_risk"] is False)
    check("pacing math: even split, slow first quarter", pacing(_beat(), 1, 0)["target_closed"] == 0.0)
    bad = False
    try:
        cmd_close("nope", "x")
    except SystemExit:
        bad = True
    check("unknown id refused", bad)
    print("self-test:", "OK" if ok else "FAILED")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(prog="findings_gait")
    ap.add_argument("--self-test", action="store_true")
    sub = ap.add_subparsers(dest="cmd")
    o = sub.add_parser("open"); o.add_argument("--source", required=True); o.add_argument("--text", required=True)
    g = sub.add_parser("ingest"); g.add_argument("file")
    f = sub.add_parser("fate"); f.add_argument("id"); f.add_argument("--owner"); f.add_argument("--due"); f.add_argument("--compost")
    c = sub.add_parser("close"); c.add_argument("id"); c.add_argument("--note", default="")
    pl = sub.add_parser("plan"); pl.add_argument("--days", required=True)
    s = sub.add_parser("status"); s.add_argument("--json", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        sys.exit(self_test())
    if a.cmd == "open": cmd_open(a.source, a.text)
    elif a.cmd == "ingest": cmd_ingest(a.file)
    elif a.cmd == "fate": cmd_fate(a.id, a.owner, a.due, a.compost)
    elif a.cmd == "plan": cmd_plan(a.days)
    elif a.cmd == "close": cmd_close(a.id, a.note)
    else: cmd_status(getattr(a, "json", False))


if __name__ == "__main__":
    main()
