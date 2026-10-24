#!/usr/bin/env python3
"""filing_workback: backward schedule + countdown for the patent filing plan (stdlib only).

python3 scripts/filing_workback.py                 # text report
python3 scripts/filing_workback.py --html          # also write _ARTIFACTS/filing-workback.html
python3 scripts/filing_workback.py --anchor arcs-v9-first-deploy   # plan against a different anchor
python3 scripts/filing_workback.py --slip ledger-final=10          # what a 10-day slip does downstream
python3 scripts/filing_workback.py --simulate      # event-time Monte Carlo: chance of making the date, percentile dates, criticality, paths
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
import inspect
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import filing_event_time as fet  # noqa: E402

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


def html(plan, nodes, today, anchor, plan_date, topo, done, cp, ready, simd=None):
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
            "beliefs": plan.get("beliefs", []), "lessons": plan.get("lessons", []),
            "sim": ({k: v for k, v in simd.items() if k != "_raw"} if simd else None)}
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
  <div class="card"><div class="k">Steps you can start</div><div class="v" id="nx">-</div><div class="sub" id="nxsub"></div></div>
  <div class="card"><div class="k">Anchor in use</div><div class="v sm" id="an">-</div><div class="sub" id="ansub"></div></div>
</div>
<h2>Chance of making the date</h2>
<div class="big" id="simcards"></div>
<div class="wrap" tabindex="0" role="region" aria-label="Alternative paths"><table id="paths"></table></div>
<h2>Most often on the critical path</h2>
<div id="crit"></div>
<h2>Gates</h2><div id="gates" class="wrap" tabindex="0" role="region" aria-label="Gates"></div>
<p><label class="k" for="pick">Show</label> <select id="pick"><option value="all">all steps</option><option value="ready">ready now</option><option value="cp">critical path</option></select></p>
<div class="wrap" tabindex="0" role="region" aria-label="Filing steps"><table><thead><tr><th>Step</th><th>Owner</th><th>Status</th><th>Days</th><th>Start by</th><th>Finish by</th><th>Slack</th><th>Needs / holds up</th></tr></thead><tbody id="rows"></tbody></table></div>
<h2>Pre-registered beliefs</h2><div id="beliefs" class="wrap" tabindex="0" role="region" aria-label="Beliefs"></div>
<p class="sub">The Start by, Finish by and Slack columns are the old point-estimate schedule (even integer days, one path): treat them as false precision and read the simulation above instead. Slack is days between the latest start that still meets the plan date and the earliest start from today. Negative means the plan date cannot be met on these estimates. Rebuild with <code>python3 scripts/filing_workback.py --html</code> after changing statuses in <code>runtime/specs/filing-workback-plan.json</code>.</p>
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
var rdy=D.rows.filter(function(r){return r.status==='ready'}).sort(function(a,b){return b.holds.length-a.holds.length});
document.getElementById('nx').textContent=rdy.length+' ready now';
document.getElementById('nxsub').textContent=rdy.length?('Biggest unlock first: '+rdy[0].title+' ('+rdy[0].owner+', holds up '+rdy[0].holds.length+' steps). Starting early costs nothing; waiting is what the simulation penalises.'):'Nothing is ready; see the blocked steps.';
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
if(D.sim){var S=D.sim;
 var cards='<div class="card"><div class="k">Chance of filing by '+S.deadline+'</div><div class="v">'+(S.p_on_time*100).toFixed(0)+'%</div><div class="sub">author-estimated spreads, '+S.runs+' runs</div></div>';
 if(S.p_stress!==null){cards+='<div class="card"><div class="k">With stalls (author priors)</div><div class="v">'+(S.p_stress*100).toFixed(0)+'%</div><div class="sub">median '+S.dates_stress['50']+', p95 '+S.dates_stress['95']+'</div></div>';}
 cards+='<div class="card"><div class="k">Finish interval, p10 to p95</div><div class="v sm">'+S.dates['10']+' to '+S.dates['95']+'</div><div class="sub">median '+S.dates['50']+', p80 '+S.dates['80']+'</div></div>';
 document.getElementById('simcards').innerHTML=cards;
 document.getElementById('paths').innerHTML='<thead><tr><th>Path</th><th>On time</th><th>With stalls</th><th>Median</th><th>p80</th><th>Doors</th><th>Trade-offs (no recommendation)</th></tr></thead><tbody>'+S.paths.map(function(x){return '<tr><td><b>'+esc(x.id)+'</b><br>'+esc(x.summary)+'</td><td>'+(x.p_on_time*100).toFixed(0)+'%</td><td>'+(x.p_stress===null?'-':(x.p_stress*100).toFixed(0)+'%')+'</td><td>'+x.dates['50']+'</td><td>'+x.dates['80']+'</td><td>'+x.doors.length+'</td><td><small>'+x.tradeoffs.map(esc).join('<br>')+'</small></td></tr>'}).join('')+'</tbody>';
 document.getElementById('crit').innerHTML='<table><tbody>'+S.crit.map(function(c){return '<tr><td style="width:30%"><b>'+esc(c[0])+'</b></td><td><div style="height:8px;border-radius:3px;background:var(--cyan);width:'+(c[1]*100).toFixed(0)+'%"></div></td><td style="width:15%">'+(c[1]*100).toFixed(0)+'%</td></tr>'}).join('')+'</tbody></table>';
}
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
    out.extend(sim_gates(plan, nodes, anchor, today))
    return out


def sim_gates(plan, nodes, anchor, today):
    """write-lock, confidence and path gates from the event-time layer (lessons L2, L4; ROM primitive 7)."""
    sim = plan.get("sim")
    if not sim:
        return []
    out = []
    pdate = plan_date_of(plan, anchor)
    problems = list(fet.write_lock_problems(nodes))
    errs = []
    for pth in plan.get("paths", []):
        try:
            pn = fet.apply_patch(nodes, pth.get("patch", {}))
            fet.order(pn)
            problems += ["[%s] %s" % (pth["id"], x) for x in fet.write_lock_problems(pn)]
            fet.simulate(pn, sim, pth.get("patch", {}).get("target", "file"), today, pdate, runs=200)
        except (ValueError, KeyError) as e:
            errs.append("%s: %s" % (pth["id"], e))
    out.append(("write_lock", True, not problems, "; ".join(problems) or "every one-way door has a declared write-lock step before it, in every path"))
    out.append(("paths", True, not errs, "; ".join(errs) or "%d alternative paths build, order and simulate" % len(plan.get("paths", []))))
    try:
        p = fet.simulate(nodes, sim, "file", today, pdate)["p_on_time"]
    except ValueError as e:
        return out + [("confidence_floor", True, False, str(e))]
    floor, want = sim.get("hard_floor", 0.5), sim.get("min_confidence", 0.8)
    out.append(("confidence_floor", True, p >= floor, "chance of filing by %s is %.0f%% (hard floor %.0f%%)" % (pdate, 100 * p, 100 * floor)))
    out.append(("confidence", False, p >= want, "chance of filing by %s is %.0f%% (wanted %.0f%%), on author-estimated spreads" % (pdate, 100 * p, 100 * want)))
    stall = sim.get("stall")
    if stall:
        ps = fet.simulate(nodes, sim, "file", today, pdate, stall=stall)["p_on_time"]
        out.append(("confidence_stress", False, ps >= want, "with heavy-tailed stalls (author priors) the chance of filing by %s is %.0f%% (wanted %.0f%%)" % (pdate, 100 * ps, 100 * want)))
    return out


def _date(today, days):
    return today + dt.timedelta(days=days)


def sim_data(plan, nodes, today, pdate):
    sim = plan.get("sim")
    if not sim:
        return None
    base = fet.simulate(nodes, sim, "file", today, pdate)
    stall = sim.get("stall")
    base_s = fet.simulate(nodes, sim, "file", today, pdate, stall=stall) if stall else None
    paths = []
    for pth in plan.get("paths", []):
        pn = fet.apply_patch(nodes, pth.get("patch", {}))
        tgt = pth.get("patch", {}).get("target", "file")
        r = fet.simulate(pn, sim, tgt, today, pdate, also=pth.get("patch", {}).get("also", []))
        rs = fet.simulate(pn, sim, tgt, today, pdate, stall=stall) if stall else None
        paths.append({"id": pth["id"], "title": pth["title"], "summary": pth.get("summary", ""), "tradeoffs": pth.get("tradeoffs", []),
                      "target": tgt, "p_on_time": r["p_on_time"], "p_stress": rs["p_on_time"] if rs else None,
                      "dates_stress": ({str(q): str(_date(today, v)) for q, v in rs["pct"].items()} if rs else None), "dates": {str(q): str(_date(today, v)) for q, v in r["pct"].items()},
                      "effort": r["mean_effort_days"], "doors": r["one_way_doors"],
                      "also": {a: {k: str(_date(today, v)) for k, v in d.items()} for a, d in r["also"].items()}})
    top = sorted(base["crit"].items(), key=lambda kv: -kv[1])[:8]
    return {"runs": base["runs"], "seed": base["seed"], "p_on_time": base["p_on_time"], "deadline": str(pdate),
            "p_stress": base_s["p_on_time"] if base_s else None, "p_if_earlier": base["p_if_earlier"],
            "p_if_earlier_stress": base_s["p_if_earlier"] if base_s else None,
            "dates_stress": ({str(q): str(_date(today, v)) for q, v in base_s["pct"].items()} if base_s else None),
            "dates": {str(q): str(_date(today, v)) for q, v in base["pct"].items()}, "crit": [[k, v] for k, v in top],
            "paths": paths, "floor": sim.get("hard_floor", 0.5), "want": sim.get("min_confidence", 0.8),
            "write_locks": [[i, n.get("declare", "")] for i, n in nodes.items() if n.get("kind") == "write_lock"],
            "_raw": base}


def sim_block(plan, nodes, today, pdate):
    d = sim_data(plan, nodes, today, pdate)
    if not d:
        return None
    print("\nEVENT-TIME SIMULATION (%d runs, seed %s). Durations are author estimates sampled as floats; each step fires when its preconditions finish." % (d["runs"], d["seed"]))
    print("  Chance of filing by %s: %.1f%%   (hard floor %.0f%%, wanted %.0f%%)" % (d["deadline"], 100 * d["p_on_time"], 100 * d["floor"], 100 * d["want"]))
    print("  Finish, as an interval not a point: p10 %s  p50 %s  p80 %s  p95 %s" % tuple(d["dates"][q] for q in ("10", "50", "80", "95")))
    if d["p_stress"] is not None:
        print("  With heavy-tailed stalls (author priors, not measurements): %.1f%% on time; p50 %s  p95 %s" % (100 * d["p_stress"], d["dates_stress"]["50"], d["dates_stress"]["95"]))
        print("  If the real deadline were earlier by 30 / 60 / 90 / 120 days: %s  (bounded)   %s  (with stalls)" % (
            " ".join("%3.0f%%" % (100 * d["p_if_earlier"][k]) for k in (30, 60, 90, 120)), " ".join("%3.0f%%" % (100 * d["p_if_earlier_stress"][k]) for k in (30, 60, 90, 120))))
    print("  Most often on the critical path: " + ", ".join("%s %.0f%%" % (k, 100 * v) for k, v in d["crit"][:6]))
    print("  Alternative paths, same random numbers (no recommendation; counsel decides):")
    print("    %-15s %-9s %-9s %-11s %-11s %-9s %-5s %s" % ("path", "on time", "stalls", "p50", "p80", "effort-d", "doors", "title"))
    for pth in d["paths"]:
        stress = "%7.1f%%" % (100 * pth["p_stress"]) if pth["p_stress"] is not None else "      -"
        print("    %-15s %7.1f%%  %s  %-11s %-11s %9.1f %5d %s" % (pth["id"], 100 * pth["p_on_time"], stress, pth["dates"]["50"], pth["dates"]["80"], pth["effort"], len(pth["doors"]), pth["title"][:40]))
        for a, v in pth["also"].items():
            print("      also %s: p50 %s p80 %s" % (a, v["p50"], v["p80"]))
    print("  Write-lock steps (one-way doors need one): " + ", ".join(i for i, _ in d["write_locks"]))
    return d


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
        if "sim" in p:
            p["sim"]["runs"] = min(p["sim"].get("runs", 1500), 1500)  # keep the self-test fast; the real runs use the plan setting
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
    assert "write_lock" in fails(lambda p: node(p, "file").update(needs=[x for x in node(p, "file")["needs"] if x != "wl-file"])), "one-way door without a write-lock accepted"
    assert "write_lock" in fails(lambda p: node(p, "wl-file").update(declare="")), "empty write-lock declaration accepted"
    assert "write_lock" not in fails(lambda p: None), "write_lock fired on the clean plan"
    assert "confidence_floor" in fails(lambda p: node(p, "select-counsel").update(days=900)), "confidence floor cannot fail"
    assert "confidence_floor" not in fails(lambda p: None), "confidence floor cried wolf on the clean plan"
    assert "paths" in fails(lambda p: p["paths"][1]["patch"]["nodes_add"][0]["needs"].append("file-thin")), "a cyclic alternative path was accepted"
    assert "paths" not in fails(lambda p: None), "paths gate fired on the clean plan"
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
    fet.self_test()
    n = sum(1 for l in inspect.getsource(self_test).splitlines() if l.strip().startswith("assert "))
    print("self-test OK: %d assertion sites here (schedule gates, score, cross-scale identity, REVISED handling, post hoc reasoning, unregistered scope, write-lock, confidence, paths) plus the event-time module's own" % n)


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
    ap.add_argument("--simulate", action="store_true")
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
    if args.simulate:
        sim_block(plan, nodes, today, plan_date)
        return
    cp, ready, neg = report(plan, nodes, today, anchor, plan_date, topo, done)
    simd = sim_block(plan, nodes, today, plan_date)
    fails = run_gates(json.load(open(PLAN)), args) if (args.check or args.strict) else []
    if args.check or args.strict:
        for x in belief_problems(plan):
            print("  BELIEF PROBLEM " + x)
            fails.append(x)
    if args.html:
        html(plan, nodes, today, anchor, plan_date, topo, done, cp, ready, simd)
    if fails:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
