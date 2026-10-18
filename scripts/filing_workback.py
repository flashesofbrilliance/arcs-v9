#!/usr/bin/env python3
"""filing_workback: backward schedule + countdown for the patent filing plan (stdlib only).

python3 scripts/filing_workback.py                 # text report
python3 scripts/filing_workback.py --html          # also write _ARTIFACTS/filing-workback.html
python3 scripts/filing_workback.py --anchor arcs-v9-first-deploy   # plan against a different anchor
python3 scripts/filing_workback.py --slip ledger-final=10          # what a 10-day slip does downstream
python3 scripts/filing_workback.py --check         # gates: exit 1 on negative slack, bad DAG, done without evidence
python3 scripts/filing_workback.py --strict        # also fail on an UNVERIFIED anchor or a too-comfortable plan
python3 scripts/filing_workback.py --self-test     # plant faults, prove each gate fails on them
python3 scripts/filing_workback.py --calibration   # pre-registered beliefs and Brier score (n shown)
python3 scripts/filing_workback.py --backlog [--write]   # plan nodes as _QUEUE/induced-backlog.jsonl rows
python3 scripts/filing_workback.py --backlog-check # plan statuses must agree with the queue states

Same plan shape as the RET take-home plan.json (id, needs, owner, status, done_when), plus `days`.
Plan date = chosen anchor + 12 months - buffer. The `file` node must finish by then; every ancestor
gets a latest-finish / latest-start walked backward, and slack = latest start - earliest start.
Planning aid, not legal advice: counsel decides what each anchor means.
"""
import argparse
import datetime as dt
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLAN = os.path.join(ROOT, "runtime", "specs", "filing-workback-plan.json")
TOKENS = os.path.join(ROOT, "src", "ui-kit", "recoil-report", "_tokens.css")
OUT = os.path.join(ROOT, "_ARTIFACTS", "filing-workback.html")


def add_months(d, m):
    y, mo = divmod(d.month - 1 + m, 12)
    y += d.year
    mo += 1
    day = min(d.day, [31, 29 if y % 4 == 0 and (y % 100 or y % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][mo - 1])
    return dt.date(y, mo, day)


def load(args, plan=None):
    plan = plan if plan is not None else json.load(open(PLAN))
    nodes = {n["id"]: dict(n) for n in plan["nodes"]}
    for n in nodes.values():
        for d in n["needs"]:
            assert d in nodes, "%s needs unknown %s" % (n["id"], d)
    today = dt.date.fromisoformat(plan["today_override"]) if plan.get("today_override") else dt.date.today()
    anchors = {a["id"]: a for a in plan["anchors"]}
    anchor = anchors[args.anchor] if getattr(args, "anchor", None) else min(plan["anchors"], key=lambda a: a["date"])
    plan_date = add_months(dt.date.fromisoformat(anchor["date"]), 12) - dt.timedelta(days=plan["buffer_days"])
    if plan.get("base_case") and not getattr(args, "anchor", None):
        plan_date = dt.date.fromisoformat(plan["base_case"]["plan_date"])  # pinned base case; --anchor shows a scenario instead
    for s in getattr(args, "slip", None) or []:
        k, v = s.split("=")
        nodes[k]["days"] += int(v)
    return plan, nodes, today, anchor, plan_date


def order(nodes):
    seen, out = set(), []

    def visit(i, stack=()):
        assert i not in stack, "cycle at " + i
        if i in seen:
            return
        for d in nodes[i]["needs"]:
            visit(d, stack + (i,))
        seen.add(i)
        out.append(i)
    for i in nodes:
        visit(i)
    return out


def schedule(nodes, today, plan_date):
    topo = order(nodes)
    done = {i for i, n in nodes.items() if n["status"] == "done"}
    down = {i: [j for j, m in nodes.items() if i in m["needs"]] for i in nodes}
    for i in topo:  # forward: earliest start/finish from today
        n = nodes[i]
        dur = 0 if i in done else n["days"]
        es = max([today] + [nodes[d]["ef"] for d in n["needs"] if d not in done])
        n["es"], n["ef"] = es, es + dt.timedelta(days=dur)
    fil = nodes["file"]
    for i in reversed(topo):  # backward: latest finish/start so `file` still lands on plan_date
        n = nodes[i]
        if i == "file":
            lf = plan_date
        else:
            succ = [nodes[j]["ls"] for j in down[i] if "ls" in nodes[j] and nodes[j].get("gates_file")]
            lf = min(succ) if succ else None
        n["gates_file"] = i == "file" or lf is not None
        if lf is not None:
            n["lf"] = lf
            n["ls"] = lf - dt.timedelta(days=0 if i in done else n["days"])
            n["slack"] = (n["ls"] - n["es"]).days
    # downstream of file: scheduled forward from the actual/earliest file date
    for i in topo:
        n = nodes[i]
        if not n["gates_file"]:
            n["ls"] = n["lf"] = None
            n["slack"] = None
            if i == "nonprov":
                n["ef"] = fil["ef"] + dt.timedelta(days=n.get("lag_after_file", 0))
                n["es"] = n["ef"]
    # propagation: what a pending/blocked node holds up
    for i in nodes:
        seen, fr = set(), [i]
        while fr:
            fr = [j for f in fr for j in down[f] if j not in seen]
            seen |= set(fr)
        nodes[i]["holds"] = sorted(seen)
    return topo, done


def critical(nodes, done):
    cur, path = "file", ["file"]
    while True:
        pend = [d for d in nodes[cur]["needs"] if d not in done]
        if not pend:
            break
        cur = max(pend, key=lambda d: nodes[d]["ef"])
        path.append(cur)
    return list(reversed(path))


def report(plan, nodes, today, anchor, plan_date, topo, done):
    print("FILING WORKBACK  today %s" % today)
    print("Anchor: %s %s (%s)  -> +12 months -%dd buffer = PLAN DATE %s  (%d days from today)" % (
        anchor["id"], anchor["date"], anchor["status"], plan["buffer_days"], plan_date, (plan_date - today).days))
    if plan.get("base_case"):
        print("BASE CASE (pinned by Zach): %s. Scenarios by anchor:" % plan["base_case"]["plan_date"])
        for sid, sd, st, pd in scenarios(plan):
            print("   %-22s %s %-10s -> file by %s%s" % (sid, sd, st, pd, "  (= base)" if str(pd) == plan["base_case"]["plan_date"] else ""))
    print("Earliest possible `file` date given the chain: %s  (slack %s days)\n" % (nodes["file"]["ef"], nodes["file"]["slack"]))
    print("%-24s %-7s %-8s %5s %-11s %-11s %6s  holds" % ("node", "owner", "status", "days", "latest-start", "latest-fin", "slack"))
    for i in sorted(topo, key=lambda i: (nodes[i]["ls"] is None, nodes[i]["ls"] or today)):
        n = nodes[i]
        print("%-24s %-7s %-8s %5s %-11s %-11s %6s  %d" % (i, n["owner"], n["status"], n["days"], n["ls"] or "-", n["lf"] or "-",
              "-" if n["slack"] is None else n["slack"], len(n["holds"])))
    cp = critical(nodes, done)
    print("\nCRITICAL PATH: %s" % " -> ".join(cp))
    ready = [i for i in topo if i not in done and all(d in done for d in nodes[i]["needs"])]
    print("READY NOW: " + ", ".join("%s[%s]" % (i, nodes[i]["owner"]) for i in sorted(ready, key=lambda i: -len(nodes[i]["holds"]))))
    neg = [i for i in topo if nodes[i]["slack"] is not None and nodes[i]["slack"] < 0]
    print("NEGATIVE SLACK: %s" % (", ".join(neg) or "none"))
    return cp, ready, neg


def html(plan, nodes, today, anchor, plan_date, topo, done, cp, ready):
    tokens = open(TOKENS).read()
    rows = []
    for i in sorted(topo, key=lambda i: (nodes[i]["ls"] is None, nodes[i]["ls"] or today)):
        n = nodes[i]
        rows.append({"id": i, "title": n["title"], "owner": n["owner"], "status": "ready" if i in ready else n["status"],
                     "days": n["days"], "ls": str(n["ls"]) if n["ls"] else None, "lf": str(n["lf"]) if n["lf"] else None,
                     "ef": str(n["ef"]), "slack": n["slack"], "needs": n["needs"], "holds": n["holds"], "cp": i in cp,
                     "done_when": n.get("done_when", ""), "why": n.get("why", ""), "ms": bool(n.get("milestone"))})
    data = {"today": str(today), "plan_date": str(plan_date), "anchor": anchor, "anchors": plan["anchors"], "rows": rows,
            "note": plan["note"], "buffer": plan["buffer_days"],
            "gates": [{"name": g[0], "hard": g[1], "ok": g[2], "msg": g[3]} for g in gates(plan, nodes, anchor, today, topo, done)],
            "beliefs": plan.get("beliefs", []), "lessons": plan.get("lessons", [])}
    page = TEMPLATE.replace("/*TOKENS*/", tokens).replace("/*DATA*/", json.dumps(data))
    open(OUT, "w").write(page)
    print("wrote " + os.path.relpath(OUT, ROOT))


TEMPLATE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Filing workback</title>
<style>
/*TOKENS*/
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);font-family:'JetBrains Mono','JetBrains Mono Fallback','IBM Plex Mono',ui-monospace,'SF Mono',Menlo,Consolas,monospace;font-size:.925rem;font-weight:400;line-height:1.6}
main{max-width:1100px;margin:0 auto;padding:32px 16px 64px}
h1{font-family:'Iowan Old Style','Palatino Linotype',Palatino,Georgia,'Newsreader',serif;font-size:clamp(1.5rem,4vw,2.4rem);font-weight:500;line-height:1.2;letter-spacing:-.02em;margin:0 0 6px}
h2{font-family:'JetBrains Mono','JetBrains Mono Fallback','IBM Plex Mono',ui-monospace,'SF Mono',Menlo,Consolas,monospace;font-size:1.15rem;font-weight:600;line-height:1.25;letter-spacing:-.01em;margin:24px 0 8px}
.lede{color:var(--muted);margin:0 0 24px}
.big{display:flex;flex-wrap:wrap;gap:12px;margin:0 0 20px}
.card{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:16px;flex:1 1 220px}
.k{font-family:'JetBrains Mono','JetBrains Mono Fallback','IBM Plex Mono',ui-monospace,'SF Mono',Menlo,Consolas,monospace;font-size:.6875rem;font-weight:700;line-height:1.4;letter-spacing:.06em;color:var(--dimmed)}
.v{font-family:'JetBrains Mono','JetBrains Mono Fallback','IBM Plex Mono',ui-monospace,'SF Mono',Menlo,Consolas,monospace;font-size:clamp(1.5rem,4vw,2.4rem);font-weight:700;line-height:1.2;color:var(--cyan);margin-top:4px}
.v.sm{font-size:1.15rem}
.sub{color:var(--muted)}
.warn{border:1px solid var(--gold);background:var(--gold-bg);padding:12px 16px;margin:0 0 20px;border-radius:6px}
table{width:100%;border-collapse:collapse}
th{text-align:left;font-family:'JetBrains Mono','JetBrains Mono Fallback','IBM Plex Mono',ui-monospace,'SF Mono',Menlo,Consolas,monospace;font-size:.6875rem;font-weight:700;line-height:1.4;letter-spacing:.06em;color:var(--dimmed);padding:8px;border-bottom:1px solid var(--border)}
td{padding:8px;border-bottom:1px solid var(--border);vertical-align:top}
tr.cp td:first-child{box-shadow:inset 0 0 0 1px var(--cyan)}
.pill{font-family:'JetBrains Mono','JetBrains Mono Fallback','IBM Plex Mono',ui-monospace,'SF Mono',Menlo,Consolas,monospace;font-size:.6875rem;font-weight:700;padding:3px 8px;border-radius:999px;border:1px solid var(--border)}
.s-ready{color:var(--green);border-color:var(--green)}.s-blocked{color:var(--red);border-color:var(--red)}.s-done{color:var(--dimmed)}
.neg{color:var(--red);font-weight:700}.ok{color:var(--green)}
.wrap{overflow-x:auto}
select{background:var(--surface);color:var(--text);border:1px solid var(--border);border-radius:6px;padding:8px;font-family:'JetBrains Mono','JetBrains Mono Fallback','IBM Plex Mono',ui-monospace,'SF Mono',Menlo,Consolas,monospace;font-size:.6875rem}
small{color:var(--dimmed);font-size:.6875rem}
</style></head><body><main>
<h1>Filing workback</h1>
<p class="lede" id="lede"></p>
<div class="warn" id="note"></div>
<div class="big">
  <div class="card"><div class="k">Plan date (file by)</div><div class="v" id="cd">-</div><div class="sub" id="cdsub"></div></div>
  <div class="card"><div class="k">Next start by</div><div class="v" id="nx">-</div><div class="sub" id="nxsub"></div></div>
  <div class="card"><div class="k">Anchor in use</div><div class="v sm" id="an">-</div><div class="sub" id="ansub"></div></div>
</div>
<h2>Gates</h2><div id="gates" class="wrap" tabindex="0" role="region" aria-label="Gates"></div>
<p><label class="k" for="pick">Show</label> <select id="pick"><option value="all">all steps</option><option value="ready">ready now</option><option value="cp">critical path</option></select></p>
<div class="wrap" tabindex="0" role="region" aria-label="Filing steps"><table><thead><tr><th>Step</th><th>Owner</th><th>Status</th><th>Days</th><th>Start by</th><th>Finish by</th><th>Slack</th><th>Needs / holds up</th></tr></thead><tbody id="rows"></tbody></table></div>
<h2>Pre-registered beliefs</h2><div id="beliefs" class="wrap" tabindex="0" role="region" aria-label="Beliefs"></div>
<p class="sub">Slack is days between the latest start that still meets the plan date and the earliest start from today. Negative means the plan date cannot be met on these estimates. Rebuild with <code>python3 scripts/filing_workback.py --html</code> after changing statuses in <code>runtime/specs/filing-workback-plan.json</code>.</p>
</main>
<script>
var D=/*DATA*/;
function days(a,b){return Math.round((b-a)/864e5)}
function esc(s){var d=document.createElement('div');d.textContent=s;return d.innerHTML}
document.getElementById('lede').textContent='Backward schedule from the filing date. Built '+D.today+'.';
document.getElementById('note').textContent=D.note+' Anchor dates marked UNVERIFIED may move once the ledger is verified.';
function tick(){
  var now=new Date(),t=new Date(D.plan_date+'T23:59:59');var ms=t-now;
  var d=Math.floor(ms/864e5),h=Math.floor(ms%864e5/36e5),m=Math.floor(ms%36e5/6e4),s=Math.floor(ms%6e4/1e3);
  document.getElementById('cd').textContent=ms<0?'PASSED':d+'d '+h+'h '+m+'m '+s+'s';
  document.getElementById('cdsub').textContent=D.plan_date+' = anchor + 12 months - '+D.buffer+' day buffer';
}
tick();setInterval(tick,1000);
var ready=D.rows.filter(function(r){return r.status==='ready'&&r.ls}).sort(function(a,b){return a.ls<b.ls?-1:1})[0];
if(ready){document.getElementById('nx').textContent=ready.ls;document.getElementById('nxsub').textContent=ready.title+' ('+ready.owner+', '+days(new Date(),new Date(ready.ls))+' days from now)'}
document.getElementById('an').textContent=D.anchor.date;
document.getElementById('ansub').textContent=D.anchor.id+' ['+D.anchor.status+']: '+D.anchor.what;
function draw(){
  var f=document.getElementById('pick').value,h='';
  D.rows.filter(function(r){return f==='all'||(f==='ready'&&r.status==='ready')||(f==='cp'&&r.cp)}).forEach(function(r){
    var sl=r.slack===null?'<small>after filing</small>':'<span class="'+(r.slack<0?'neg':'ok')+'">'+r.slack+'</span>';
    h+='<tr class="'+(r.cp?'cp':'')+'"><td><b>'+esc(r.id)+(r.ms?' (milestone)':'')+'</b><br>'+esc(r.title)+'<br><small>done when: '+esc(r.done_when)+'</small></td><td>'+esc(r.owner)+'</td><td><span class="pill s-'+r.status+'">'+r.status+'</span></td><td>'+r.days+'</td><td>'+(r.ls||'-')+'</td><td>'+(r.lf||r.ef)+'</td><td>'+sl+'</td><td><small>needs: '+(r.needs.join(', ')||'none')+'<br>holds up '+r.holds.length+': '+esc(r.holds.join(', ')||'none')+'</small></td></tr>';
  });
  document.getElementById('rows').innerHTML=h;
}
document.getElementById('pick').onchange=draw;draw();
document.getElementById('gates').innerHTML='<table><tbody>'+D.gates.map(function(g){return '<tr><td><b>'+esc(g.name)+'</b></td><td><span class="pill s-'+(g.ok?'ready':(g.hard?'blocked':'done'))+'">'+(g.ok?'ok':(g.hard?'FAIL':'warn'))+'</span></td><td>'+esc(g.msg)+'</td></tr>'}).join('')+'</tbody></table>';
document.getElementById('beliefs').innerHTML='<table><thead><tr><th>Id</th><th>Claim</th><th>Prior</th><th>Scope / frame</th><th>Test</th><th>Verdict</th></tr></thead><tbody>'+D.beliefs.map(function(b){return '<tr><td>'+esc(b.id)+'</td><td>'+esc(b.claim)+'<br><small>step: '+esc(b.node)+'</small></td><td>'+b.p+'</td><td><small>'+esc(b.test)+'</small></td><td><span class="pill">'+esc(b.verdict)+'</span></td></tr>'}).join('')+'</tbody></table>';
</script></body></html>
"""


# ---- gates (lessons L1-L6 from the RET take-home post-mortem; see plan.json "lessons") ----

def gates(plan, nodes, anchor, today, topo, done):
    """Return [(name, hard, ok, message)]. hard=False gates only fail under --strict."""
    out = []
    fil = nodes.get("file")
    anc = 0
    if fil:
        seen, fr = set(), ["file"]
        while fr:
            fr = [d for f in fr for d in nodes[f]["needs"] if d not in seen]
            seen |= set(fr)
        anc = len(seen)
    out.append(("dag_nonvacuous", True, anc >= 3, "`file` has %d ancestors (a plan whose gate depends on nothing proves nothing)" % anc))
    bad = []
    for i in done:
        n = nodes[i]
        ok = False
        try:
            ok = dt.date.fromisoformat(n.get("done_on", "")) <= today and os.path.exists(os.path.join(ROOT, n.get("evidence", "\0")))
        except ValueError:
            ok = False
        if not ok:
            bad.append(i)
    out.append(("done_evidence", True, not bad, "done without a real done_on + evidence path: %s" % (", ".join(bad) or "none")))
    neg = [i for i in topo if nodes[i].get("slack") is not None and nodes[i]["slack"] < 0]
    out.append(("slack", True, not neg, "negative slack: %s" % (", ".join(neg) or "none")))
    if plan.get("base_case"):
        base = dt.date.fromisoformat(plan["base_case"]["plan_date"])
        earlier = [x for x in scenarios(plan) if x[3] < base]
        out.append(("base_case", True, not earlier, "base case %s; anchors that would put the date earlier: %s" % (base, ", ".join("%s -> %s" % (x[0], x[3]) for x in earlier) or "none")))
    out.append(("anchor_verified", False, anchor["status"] == "VERIFIED",
                "plan date rests on the %s anchor %s (%s)" % (anchor["status"], anchor["id"], anchor["date"])))
    window = (plan_date_of(plan, anchor) - today).days
    slacks = [nodes[i]["slack"] for i in topo if nodes[i].get("slack") is not None and i not in done]
    mn = min(slacks) if slacks else 0
    out.append(("inlier", False, mn <= window / 2.0,
                "minimum slack %s of a %s-day window: comfortable everywhere, so check the estimates before trusting it" % (mn, window)))
    tot = sum(nodes[i]["days"] for i in nodes if i not in done)
    est = sum(nodes[i]["days"] for i in nodes if i not in done and not nodes[i].get("measured"))
    out.append(("estimate_share", False, est == 0, "%d of %d remaining schedule days (%d%%) are author estimates" % (est, tot, round(100.0 * est / max(tot, 1)))))
    return out


def plan_date_of(plan, anchor):
    if plan.get("base_case"):
        return dt.date.fromisoformat(plan["base_case"]["plan_date"])
    return add_months(dt.date.fromisoformat(anchor["date"]), 12) - dt.timedelta(days=plan["buffer_days"])


def scenarios(plan):
    return [(a["id"], a["date"], a["status"], add_months(dt.date.fromisoformat(a["date"]), 12) - dt.timedelta(days=plan["buffer_days"])) for a in plan["anchors"]]


def run_gates(plan, args, quiet=False):
    plan_, nodes, today, anchor, pdate = load(args, plan)
    topo, done = schedule(nodes, today, pdate)
    res = gates(plan_, nodes, anchor, today, topo, done)
    fails = [r for r in res if not r[2] and (r[1] or getattr(args, "strict", False))]
    if not quiet:
        print("\nGATES (%s):" % ("strict" if getattr(args, "strict", False) else "hard gates fail; others warn"))
        for name, hard, ok, msg in res:
            print("  %-16s %-5s %s" % (name, "ok" if ok else ("FAIL" if (hard or getattr(args, "strict", False)) else "warn"), msg))
    return fails


def self_test():
    """Plant a fault per gate and require the gate to catch it; plant a harmless change and require silence."""
    base = json.load(open(PLAN))
    ns = argparse.Namespace(anchor=None, slip=None, strict=False)

    def fails(mut, strict=False):
        p = json.loads(json.dumps(base))
        mut(p)
        a = argparse.Namespace(anchor=None, slip=None, strict=strict)
        try:
            return {f[0] for f in run_gates(p, a, quiet=True)}
        except AssertionError as e:
            return {"assert:" + str(e)[:20]}

    def node(p, i):
        return next(n for n in p["nodes"] if n["id"] == i)

    assert not fails(lambda p: None), "clean plan must pass hard gates: %s" % fails(lambda p: None)
    assert "slack" in fails(lambda p: node(p, "draft").update(days=400)), "slack gate cannot fail"
    assert "slack" not in fails(lambda p: node(p, "conception").update(days=3 + 5)), "slack gate fired on a harmless change"
    assert any(x.startswith("assert:cycle") for x in fails(lambda p: node(p, "select-counsel")["needs"].append("file"))), "cycle undetected"
    assert "done_evidence" in fails(lambda p: node(p, "retro-sweep").update(evidence="nope/missing.md")), "fake evidence accepted"
    assert "done_evidence" in fails(lambda p: node(p, "retro-sweep").pop("done_on")), "missing done_on accepted"
    assert "dag_nonvacuous" in fails(lambda p: node(p, "file").update(needs=[])), "empty gate graph accepted"
    assert "base_case" in fails(lambda p: p["anchors"].append({"id": "t", "date": "2026-04-09", "status": "UNVERIFIED", "what": "planted"})), "earlier anchor not caught by base_case"
    assert "base_case" not in fails(lambda p: None), "base_case fired on the clean plan"
    assert "anchor_verified" in fails(lambda p: None, strict=True), "strict does not flag the unverified anchor"
    assert "anchor_verified" not in fails(lambda p: p.update(anchors=[dict(a, status="VERIFIED") for a in p["anchors"]]), strict=True), "verified anchor still flagged"
    def mk(v, p, scope="records", frame="fact", **kw):
        return dict({"id": "t", "p": p, "verdict": v, "scope": scope, "frame": frame, "node": "n", "claim": "c",
                     "reason_logged_at": "2026-10-01", "resolved_on": "2026-10-02"}, **kw)
    rs = [mk("CONFIRMED", .9), mk("FALSIFIED", .8, "channels"), mk("CONFIRMED", .7, "channels"), mk("FALSIFIED", .3), mk("CONFIRMED", .6, "schedule", "estimate")]
    assert consistency(rs, "scope")[0] and consistency(rs, "frame")[0], "weighted-mean identity failed on a clean ledger"
    assert consistency(rs, "scope", assign=lambda r: "all")[0], "one-group split must equal the whole"
    g = groups(rs, "scope")
    dropped = {k: v for k, v in g.items() if k != "channels"}
    assert not consistency(rs, "scope", _groups=dropped)[0], "a dropped group went unnoticed"
    g["records"] = g["records"] + g["records"][:1]
    assert not consistency(rs, "scope", _groups=g)[0], "a double-counted row went unnoticed"
    assert score(rs)["n"] == 5 and score(rs[:3] + [mk("REVISED", .5)])["excluded"] == 1, "REVISED handling wrong"
    assert score([mk("CONFIRMED", 1.0)] * 3)["bs"] == 0.0, "perfect forecasts must score 0"
    late = {"beliefs": [mk("CONFIRMED", .9, reason_logged_at="2026-10-09", resolved_on="2026-10-02")], "scopes": ["records"], "frames": ["fact"]}
    assert belief_problems(late), "post hoc reasoning accepted"
    assert belief_problems({"beliefs": [mk("OPEN", .5, scope="oops")], "scopes": ["records"], "frames": ["fact"]}), "unregistered scope accepted"
    assert not belief_problems({"beliefs": [mk("OPEN", .5)], "scopes": ["records"], "frames": ["fact"]}), "clean belief rejected"
    print("self-test OK: 22 planted faults and controls behaved (schedule gates plus score, cross-scale identity, REVISED handling, post hoc reasoning, unregistered scope)")


def _rows(plan):
    return [b for b in plan.get("beliefs", []) if b["verdict"] in ("CONFIRMED", "REVISED", "FALSIFIED")]


def score(rows):
    """Brier over resolved beliefs. Three-outcome (uniform baseline 2/3) when every row has `pr`, else binary
    with REVISED excluded. Skill is against always saying the in-sample base rate; n is always returned."""
    three = bool(rows) and all("pr" in b for b in rows)
    use = rows if three else [b for b in rows if b["verdict"] != "REVISED"]
    n = len(use)
    if n == 0:
        return {"n": 0, "bs": None, "ref": None, "skill": None, "three": three, "excluded": len(rows) - n}
    if three:
        k = ["CONFIRMED", "REVISED", "FALSIFIED"]
        freq = [sum(1 for b in use if b["verdict"] == c) / float(n) for c in k]
        bs = ref = 0.0
        for b in use:
            pv = [b["p"], b["pr"], 1 - b["p"] - b["pr"]]
            o = [1.0 if b["verdict"] == c else 0.0 for c in k]
            bs += sum((x - y) ** 2 for x, y in zip(pv, o)) / n
            ref += sum((x - y) ** 2 for x, y in zip(freq, o)) / n
    else:
        base = sum(1 for b in use if b["verdict"] == "CONFIRMED") / float(n)
        bs = sum((b["p"] - (1.0 if b["verdict"] == "CONFIRMED" else 0.0)) ** 2 for b in use) / n
        ref = base * (1 - base)
    return {"n": n, "bs": bs, "ref": ref, "skill": (1 - bs / ref) if ref else None, "three": three, "excluded": len(rows) - n}


def groups(rows, key, assign=None):
    g = {}
    for b in rows:
        g.setdefault((assign or (lambda r: r[key]))(b), []).append(b)
    return g


def consistency(rows, key, assign=None, _groups=None):
    """The whole-ledger score must equal the count-weighted mean of the group scores (cross-scale check)."""
    whole = score(rows)
    if whole["bs"] is None:
        return True, "no resolved beliefs"
    parts = [(score(v), len(v)) for v in (_groups if _groups is not None else groups(rows, key, assign)).values()]
    tot = sum(s["n"] for s, _ in parts)
    if tot != whole["n"]:
        return False, "groups by %s cover %d resolved beliefs but the ledger has %d" % (key, tot, whole["n"])
    w = sum(s["bs"] * s["n"] for s, _ in parts if s["bs"] is not None) / tot
    return abs(w - whole["bs"]) < 1e-9, "whole %.4f vs weighted group mean %.4f (%s)" % (whole["bs"], w, key)


def belief_problems(plan):
    bad = []
    for b in plan.get("beliefs", []):
        if b.get("scope") not in plan.get("scopes", []):
            bad.append("%s: scope %r not in the pre-registered list" % (b["id"], b.get("scope")))
        if b.get("frame") not in plan.get("frames", []):
            bad.append("%s: frame %r not in the pre-registered list" % (b["id"], b.get("frame")))
        if b["verdict"] in ("CONFIRMED", "REVISED", "FALSIFIED"):
            if not b.get("resolved_on"):
                bad.append("%s: resolved without resolved_on" % b["id"])
            elif b.get("reason_logged_at", "9999") > b["resolved_on"]:
                bad.append("%s: reasoning logged after the outcome (post hoc)" % b["id"])
    return bad


def calibration(plan):
    rows = _rows(plan)
    print("BELIEFS (priors written before any check; verdicts follow the RET ledger)")
    for b in plan.get("beliefs", []):
        print("  %-4s p=%.2f %-9s %-12s %-8s [%s] %s" % (b["id"], b["p"], b["verdict"], b.get("scope", "?"), b.get("frame", "?"), b["node"], b["claim"][:70]))
    bad = belief_problems(plan)
    for x in bad:
        print("  PROBLEM " + x)
    w = score(rows)
    if w["n"] < 5:
        print("Brier: insufficient, n=%d resolved (need 5). Baselines: 0.25 always-50%% (yes/no), 0.667 uniform over 3 outcomes" % w["n"])
    else:
        print("Brier %.3f, base-rate reference %.3f, skill %+.0f%% over n=%d (%s; %d REVISED excluded)" % (
            w["bs"], w["ref"], 100 * w["skill"], w["n"], "three-outcome" if w["three"] else "binary", w["excluded"]))
    for key in ("scope", "frame"):
        ok, msg = consistency(rows, key)
        print("by %-5s: %s -> %s" % (key, msg, "ok" if ok else "FAIL"))
        for name, v in sorted(groups(rows, key).items()):
            s = score(v)
            print("   %-13s n=%d %s" % (name, s["n"], "insufficient (n<5)" if s["n"] < 5 else "Brier %.3f skill %+.0f%%" % (s["bs"], 100 * (s["skill"] or 0))))
        bad = bad + ([] if ok else ["cross-scale mismatch by " + key])
    return bad


# ---- induced backlog bridge ----

QUEUE = os.path.join(ROOT, "_QUEUE", "induced-backlog.jsonl")
TOOL = {"claude": "this session; scripts/filing_workback.py and the ledger", "zach": "Zach (human step)", "counsel": "patent counsel (external)"}
STATE_OK = {"done": {"DONE"}, "ready": {"READY", "RUNNING", "BLOCKED", "HELD"}, "blocked": {"HOLDING", "BLOCKED", "HELD"}}


def rows_for(plan, nodes, today):
    out = []
    for i, n in nodes.items():
        if n["status"] == "done":
            continue
        ready = n["status"] == "ready"
        deps = ["filing-" + d for d in n["needs"] if nodes[d]["status"] != "done"]
        out.append({
            "id": "filing-" + i,
            "jtbd": n["title"],
            "route": {"tool": TOOL[n["owner"]], "source": "runtime/specs/filing-workback-plan.json", "verified": str(today)},
            "gates": [n["done_when"], "evidence path recorded in the plan (scripts/filing_workback.py --check)"] +
                     (["outbound send: confirm with Zach first"] if i == "counsel-intake" else []),
            "trigger": "now" if ready else "when " + ", ".join(deps) + " are done",
            "cost_prior": "%s d (author estimate)" % n["days"],
            "state": "READY" if ready else "HOLDING",
            "status_note": ("ready: no open upstream" if ready else "waiting on " + ", ".join(deps)) + "; ledger " + plan["ledger"],
            "depends_on": deps,
            "unblocks": ["filing-" + j for j, m in nodes.items() if i in m["needs"] and m["status"] != "done"],
            "added": str(today),
            "source": "Zach, session 2026-10-15 (filing workback)",
        })
    return out


def backlog(plan, nodes, today, write):
    have = {}
    if os.path.exists(QUEUE):
        for l in open(QUEUE):
            if l.strip():
                r = json.loads(l)
                have[r.get("id")] = r
    new = [r for r in rows_for(plan, nodes, today) if r["id"] not in have]
    print("%d plan rows, %d already in the queue, %d to append" % (len(rows_for(plan, nodes, today)), len(rows_for(plan, nodes, today)) - len(new), len(new)))
    if write and new:
        with open(QUEUE, "a") as f:
            for r in new:
                f.write(json.dumps(r) + "\n")
        print("appended %d rows to _QUEUE/induced-backlog.jsonl (run scripts/backlog_status_check.py --check)" % len(new))
    elif not write:
        for r in new:
            print("  would add %s [%s] needs %s" % (r["id"], r["state"], r["depends_on"] or "-"))


def backlog_check(nodes):
    have = {}
    for l in open(QUEUE):
        if l.strip():
            r = json.loads(l)
            have[r.get("id")] = r
    bad = []
    for i, n in nodes.items():
        r = have.get("filing-" + i)
        if r is None:
            if n["status"] != "done":
                bad.append("%s: no queue row" % i)
            continue
        if r.get("state") not in STATE_OK[n["status"]]:
            bad.append("%s: plan %s but queue %s" % (i, n["status"], r.get("state")))
    print("backlog-check: " + ("OK, plan and queue agree" if not bad else "; ".join(bad)))
    return bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--html", action="store_true")
    ap.add_argument("--anchor")
    ap.add_argument("--slip", action="append")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--calibration", action="store_true")
    ap.add_argument("--backlog", action="store_true")
    ap.add_argument("--backlog-check", action="store_true")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    plan, nodes, today, anchor, plan_date = load(args)
    if args.calibration:
        raise SystemExit(1 if calibration(plan) else 0)
    topo, done = schedule(nodes, today, plan_date)
    if args.backlog:
        return backlog(plan, nodes, today, args.write)
    if args.backlog_check:
        raise SystemExit(1 if backlog_check(nodes) else 0)
    cp, ready, neg = report(plan, nodes, today, anchor, plan_date, topo, done)
    fails = run_gates(json.load(open(PLAN)), args) if (args.check or args.strict) else []
    if args.check or args.strict:
        for x in belief_problems(plan):
            print("  BELIEF PROBLEM " + x)
            fails.append(x)
    if args.html:
        html(plan, nodes, today, anchor, plan_date, topo, done, cp, ready)
    if fails:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
