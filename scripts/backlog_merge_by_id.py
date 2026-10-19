#!/usr/bin/env python3
"""backlog_merge_by_id: resolve a git merge conflict in _QUEUE/induced-backlog.jsonl by row id (stdlib only).

Run in the middle of a conflicted merge. For every row id it takes the base, ours and theirs stages: if only one
side changed the row it keeps that side; if both changed it, it keeps theirs and prints the id for a human to look at.
Rows that exist on one side only are kept. Writes the merged file; you still `git add` and commit.
"""
import json, subprocess, sys
F = "_QUEUE/induced-backlog.jsonl"
def load(stage):
    t = subprocess.run(["git", "show", ":%d:%s" % (stage, F)], capture_output=True, text=True).stdout
    d, order = {}, []
    for l in t.split("\n"):
        if not l.strip(): continue
        try: r = json.loads(l)
        except Exception: continue
        k = r.get("id")
        if k: d[k] = r; order.append(k)
    return d, order
b, _ = load(1); o, oo = load(2); t, to = load(3)
out, both = [], []
for k in list(to) + [k for k in oo if k not in t]:
    base, ours, th = b.get(k), o.get(k), t.get(k)
    if th is None: r = ours
    elif ours is None or ours == th or base == ours: r = th
    elif base == th: r = ours
    else: r = th; both.append(k)
    out.append(r)
open(F, "w").write("\n".join(json.dumps(r) for r in out) + "\n")
print("rows %d, changed on both sides (theirs kept): %s" % (len(out), both or "none"))
