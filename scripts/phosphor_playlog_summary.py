#!/usr/bin/env python3
"""phosphor_playlog_summary: read a play log exported from Phosphor (the Copy log button) and print what the sessions show. Stdlib only, offline.

  pbpaste | python3 scripts/phosphor_playlog_summary.py        (a copied log on the clipboard)
  python3 scripts/phosphor_playlog_summary.py log.json         (a saved file)

Event rows are [wallMs, songSeconds or null, kind, id, value]. A new session starts at a start event or after 30 minutes of quiet.
Prints per session: length, time to first sound, taps, presets against slider moves, errors, the last control touched (where it stopped),
and across sessions: the most used controls and the controls that were never touched, if a --all-ids list is given.
"""
import json, sys, collections
def load():
    src = open(sys.argv[1]).read() if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else sys.stdin.read()
    d = json.loads(src)
    return d["events"] if isinstance(d, dict) else d
ev = load(); ses = []; cur = None
for e in ev:
    t, m, k, i, v = (e + [None] * 5)[:5]
    if k == "start" or cur is None or t - cur["last"] > 1800000:
        cur = {"t0": t, "last": t, "n": 0, "ttfs": None, "taps": 0, "pre": 0, "set": 0, "err": 0, "stop": "-", "ids": collections.Counter()}; ses.append(cur)
    cur["last"] = t; cur["n"] += 1
    if cur["ttfs"] is None and k in ("play", "key"): cur["ttfs"] = (t - cur["t0"]) / 1000
    if k == "tap": cur["taps"] += 1
    if k == "set": cur["set"] += 1
    if k == "preset" or (isinstance(i, str) and i.startswith(("gp=", "pre="))): cur["pre"] += 1
    if k == "err": cur["err"] += 1
    if k in ("tap", "set", "pick", "fx", "preset"): cur["stop"] = i; cur["ids"][i] += 1
tot = collections.Counter()
print("%d events, %d session(s)" % (len(ev), len(ses)))
for n, s in enumerate(ses, 1):
    print("session %d: %.1f min, first sound %s, %d taps, %d preset taps, %d slider moves, %d errors, stopped at %s" % (n, (s["last"] - s["t0"]) / 60000, ("%.1f s" % s["ttfs"]) if s["ttfs"] is not None else "never", s["taps"], s["pre"], s["set"], s["err"], s["stop"]))
    tot.update(s["ids"])
print("most used:", ", ".join("%s x%d" % kv for kv in tot.most_common(8)) or "none")
tt = sorted(s["ttfs"] for s in ses if s["ttfs"] is not None)
if tt: print("median first sound: %.1f s (target for a child with no instructions: 5 s)" % tt[len(tt) // 2])
