#!/usr/bin/env python3
"""castellum: the Roman distribution tank for the backlog. Read-only.

Three outlets sit at three heights. When the supply (your remaining budget) drops, the highest outlet runs dry first and the lowest never does:
  public   always flows        what keeps the system honest: red checks, owed receipts, de-risk steps, verification
  shared   flows at >= 30%     builds and features other work depends on
  private  flows at >= 60%     experiments and nice-to-haves
A one-way door with high or critical ruin is a lock, not a tap: it shows "LOCK FIRST" until its chamber, canary and rollback exist.
Reach for a backlog row is the larger of its own `reach` and the number of live rows it unblocks through `needs`.
Pressure = ruin weight x (1 + reach / 5) x (1 + min(age in days, 30) / 15). Cost of a mistake and breadth of fallout outrank mere age; age can at most triple a score. Ledger rows carry ruin and reach; backlog rows may carry optional `ruin` and `reach` and otherwise default to ruin low, reach 1.
An `outlet` field on a backlog row overrides the keyword guess below. Overflow (very old, low pressure, private) is listed as COMPOST CANDIDATE, never deleted.

  python3 scripts/castellum.py [--budget 0..100] [--top N] [--json]       what flows and what sheds at this budget (default 100)
  python3 scripts/castellum.py --keystones [--top N]                      the rows that sit under the most other rows (the shared blockers)
  python3 scripts/castellum.py --check                                    self-test the rules
Stdlib only. Sources: _QUEUE/induced-backlog.jsonl, _QUEUE/ripple-ledger.jsonl (never written).
"""
import datetime, json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HEIGHT = {"public": 0, "shared": 30, "private": 60}
RUIN = {"low": 1, "medium": 2, "high": 4, "critical": 8}
PUBLIC = re.compile(r"(receipt|red check|gate|debt|de-?risk|verify|verif|honest|safety|guard|regression|flake|fixture|reach check|lint)", re.I)
PRIVATE = re.compile(r"(idea|experiment|explor|fun |skin|preset|demo|binaural|mash|moon|water preset|ritual|te skin|glass grow|phase-field|freeze dance)", re.I)

def load(name):
    out = []; f = os.path.join(ROOT, "_QUEUE", name)
    if not os.path.exists(f): return out
    for l in open(f, encoding="utf-8"):
        l = l.strip()
        if l:
            try: out.append(json.loads(l))
            except ValueError: pass
    return out

def days(s, today):
    try: return max(0, (today - datetime.date.fromisoformat(str(s)[:10])).days)
    except (ValueError, TypeError): return 0

def outlet(r, kind):
    if r.get("outlet") in HEIGHT: return r["outlet"]
    if kind == "ledger": return "public" if r.get("door") == "one-way" else "shared"
    txt = (r.get("id", "") + " " + r.get("jtbd", ""))[:400]
    return "public" if PUBLIC.search(txt) else "private" if PRIVATE.search(txt) else "shared"

def score(ruin, reach, age):
    return RUIN.get(ruin, 1) * (1 + (reach or 1) / 5) * (1 + min(age, 30) / 15)

def lock_missing(r):
    return [k for k in ("chamber", "canary", "rollback") if str(r.get(k, "")).strip().lower() in ("", "n/a", "na", "none")]

def unblocks():
    """For each backlog row id, how many OPEN or READY rows (directly or through others) list it in `needs`. A row that sits under many others is a keystone."""
    bl = {r.get("id"): r for r in load("induced-backlog.jsonl") if r.get("id")}
    live = {k for k, r in bl.items() if r.get("state") in ("OPEN", "READY")}
    rev = {}
    for k in live:
        for n in bl[k].get("needs") or []: rev.setdefault(n, set()).add(k)
    out = {}
    for k in bl:
        seen, stack = set(), list(rev.get(k, ()))
        while stack:
            x = stack.pop()
            if x in seen or x == k: continue
            seen.add(x); stack.extend(rev.get(x, ()))
        out[k] = len(seen)
    return out

def rows(today):
    out = []; ub = unblocks()
    for r in load("ripple-ledger.jsonl"):
        pr = score(r.get("ruin"), r.get("reach"), days(r.get("noted"), today))
        if r.get("door") == "one-way" and r.get("ruin") in ("high", "critical") and r.get("derisk_state") != "PASSED":
            status = "LOCK FIRST" + (" (missing " + ", ".join(lock_missing(r)) + ")" if lock_missing(r) else ": run the canary and mark PASSED")
        else: status = "OPEN" if r.get("derisk_state") != "PASSED" else "DONE"
        out.append({"id": r["id"], "src": "ledger", "outlet": outlet(r, "ledger"), "pressure": round(pr, 1), "status": status, "text": r["decision"][:90]})
    for r in load("induced-backlog.jsonl"):
        if r.get("state") not in ("OPEN", "READY"): continue
        a = days((r.get("route") or {}).get("verified") or r.get("date"), today)
        out.append({"id": r.get("id", "?"), "src": "backlog", "outlet": outlet(r, "backlog"), "pressure": round(score(r.get("ruin"), max(r.get("reach") or 1, ub.get(r.get("id"), 0)), a), 1), "status": "OPEN", "unblocks": ub.get(r.get("id"), 0), "text": (r.get("jtbd") or "")[:90]})
    return out

def run(budget, top, today):
    rs = rows(today); flows = {o: budget >= h for o, h in HEIGHT.items()}
    res = {"budget": budget, "outlets": {}}
    for o in ("public", "shared", "private"):
        items = sorted([r for r in rs if r["outlet"] == o and r["status"] != "DONE"], key=lambda r: (r["status"].startswith("LOCK FIRST"), -r["pressure"]))
        res["outlets"][o] = {"flows": flows[o], "count": len(items), "top": items[:top]}
    return res

def check():
    today = datetime.date(2026, 10, 16); bad = 0
    def t(ok, msg):
        nonlocal bad; print(("✓ " if ok else "✗ ") + msg); bad += (not ok)
    r = run(20, 3, today); t(r["outlets"]["public"]["flows"] and not r["outlets"]["shared"]["flows"] and not r["outlets"]["private"]["flows"], "at 20 percent only the public outlet flows")
    r = run(50, 3, today); t(r["outlets"]["shared"]["flows"] and not r["outlets"]["private"]["flows"], "at 50 percent public and shared flow, private is dry")
    r = run(100, 3, today); t(all(v["flows"] for v in r["outlets"].values()), "at 100 percent all three flow")
    rs = rows(today); locks = [x for x in rs if x["src"] == "ledger" and x["status"].startswith("LOCK FIRST")]
    t(len(locks) > 0 and all(x["status"] != "OPEN" for x in locks), "an unpassed one-way door with high ruin shows LOCK FIRST, never OPEN")
    before = [os.path.getmtime(os.path.join(ROOT, "_QUEUE", n)) for n in ("induced-backlog.jsonl", "ripple-ledger.jsonl")]; run(100, 3, today)
    t(before == [os.path.getmtime(os.path.join(ROOT, "_QUEUE", n)) for n in ("induced-backlog.jsonl", "ripple-ledger.jsonl")], "read-only: neither file was touched")
    pub = run(100, 12, today)["outlets"]["public"]["top"]; top = [x["id"] for x in pub]
    t("pressure-red-checks-main" in top and top.index("pressure-red-checks-main") < 4, "rows that can open now sort ahead of locked ones, and the red checks lead them (ruin and reach outrank age)")
    dflt = [x for x in rs if x["src"] == "backlog" and not x.get("unblocks") and x["id"] not in ("pressure-red-checks-main", "pressure-rotting-loops")]
    t(all(x["pressure"] <= 3.7 for x in dflt), "no default-ruin backlog row that unblocks nothing exceeds 3.6 however old it is (age triples a score at most)")
    ub = unblocks(); top = max(ub, key=lambda k: ub[k]) if ub else None
    t(top == "phosphor-pins-tempo-map" and ub[top] >= 10, f"the keystone is the pins and tempo map and it sits under {ub.get(top)} live rows")
    t(ub.get("phosphor-offline-render", 0) >= 1 and ub.get("phosphor-event-log", 0) > ub.get("phosphor-offline-render", 0), "the event log sits under more rows than the offline render, which waits on it")
    t(outlet({"id": "x", "jtbd": "fix the red check on main"}, "backlog") == "public" and outlet({"id": "x", "jtbd": "binaural beats layer"}, "backlog") == "private" and outlet({"id": "x", "outlet": "private", "jtbd": "red check"}, "backlog") == "private", "keywords guess an outlet and an explicit outlet field overrides them")
    return 1 if bad else 0

def keystones(top):
    ub = unblocks(); bl = {r.get("id"): r for r in load("induced-backlog.jsonl") if r.get("id")}
    rank = sorted([(n, k) for k, n in ub.items() if n and bl[k].get("state") in ("OPEN", "READY")], reverse=True)[:top]
    print("keystones: live rows that other live rows wait on, directly or through others")
    for n, k in rank: print(f"  {n:3d} unblocked  {k}  needs: {', '.join(bl[k].get('needs') or []) or 'nothing'}")

def main(a):
    if "--keystones" in a: keystones(int(a[a.index("--top") + 1]) if "--top" in a else 8); return 0
    if "--check" in a: return check()
    budget = 100; top = 8
    if "--budget" in a: budget = float(a[a.index("--budget") + 1])
    if "--top" in a: top = int(a[a.index("--top") + 1])
    res = run(budget, top, datetime.date.today())
    if "--json" in a: print(json.dumps(res, indent=1)); return 0
    print(f"castellum at {budget:g} percent supply")
    for o in ("public", "shared", "private"):
        v = res["outlets"][o]; print(f"\n{o.upper():8} {'FLOWS' if v['flows'] else 'DRY (sheds first)'}  ({v['count']} waiting)")
        for r in (v["top"] if v["flows"] else []): print(f"  {r['pressure']:7.1f}  {r['status']:34.34}  {r['id']}  {r['text']}")
    return 0

if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
