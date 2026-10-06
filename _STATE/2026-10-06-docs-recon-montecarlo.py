#!/usr/bin/env python3
"""Monte Carlo over the Docs Reconciliation decision paths (stdlib only).
Durations (hours, tri(min,mode,max)) and p_fail are SUBJECTIVE PRIORS unless a comment cites a measurement.
Output is a ranking aid for the plan, not a forecast."""
import random, statistics, json, sys
random.seed(7)
# id: (label, who, (lo,mode,hi) hours, p_rework, deps, calendar_wait_days_after_deps)
T = {
 "S1":  ("confirm #1029/#1025 sessions stopped","Z",(.1,.2,.5),.10,[],0),
 "A1":  ("re-run #934/#932 (red = 10-06 14:18Z billing block, measured)","C",(.1,.2,.5),.30,[],0),
 "A5":  ("merge train 7 green PRs + receipts","C",(.3,.6,1.5),.20,["S1"],0),   # push reject if main moves; 33 merges/day measured
 "A7":  ("close 7 SECRETLY-DONE rows + stale rows","C",(.05,.1,.3),.05,[],0),
 "A2":  ("sage_efficacy .js cite fix (CLAUDE.md + ADR-026/059)","C",(.1,.2,.5),.10,[],0),
 "A3":  ("qualify old citations in _ARCHIVE/handoffs.md","C",(.5,1.0,3),.30,["A2"],0),
 "A4":  ("flip INTEGRITY_GATE_BLOCK=1 after clean week","Z",(.1,.1,.3),.25,["A3"],7),
 "A8":  ("Actions cost fix (collapse jobs, path-filter, skip drafts)","C",(1,2.5,6),.25,["A1"],0),
 "A8b": ("land #934 advisory gates path-filtered","C",(.5,1,2.5),.30,["A1","A8"],0),
 "A9":  ("ADR-085 accept/step-3 decision","Z",(.2,.4,1),.15,[],7),
 "A6":  ("Issues SSOT live + /api/pulse (post-train)","C",(.5,1,3),.25,["A5"],0),
 "A12": ("un-park main checkout (WIP-commit, merge, push)","C",(.2,.4,1),.20,[],0),
 "A11": ("move/delete old-key copies, then revoke","Z",(.3,.6,1.5),.30,["A5"],0),
 "A10a":("nftt index resync + tao mint","C",(.5,1,2.5),.30,[],0),
 "A10b":("#700 Tribes gates -> merge","C",(.5,1.2,3),.35,["A10a"],0),
 "Z1":  ("one-line Zach rulings (ADR-009, plugin scope, orphan scripts, nci dup, marketplace)","Z",(.2,.4,.8),.05,[],0),
}
# Ruin/fork events: (label, p, what it costs in Zach-hours, which task triggers it, condition)
RUIN = [
 ("key revoked before .env/.hermes/arcs-care copies moved -> scripts/previews 401", .22, 3.0, "A11"),
 ("un-park clobbers 13 dirty files / diverged branch (11 ahead, 36 behind)", .10, 4.0, "A12"),
 ("train push rejected non-FF, rebuild loop", .30, .7, "A5"),
 ("billing block recurs mid-train (hit twice in 3 days, measured)", .25, 1.5, "A5"),
 ("#934 adds 4 gates to every PR while P1 minutes leak (cost regress)", .50, 2.0, "A8b"),
 ("gate flip blocks main on a false positive", .20, 2.5, "A4"),
 ("ADR-085 step 3 locks out hotfix while 76% of merges bypass (8 of 33 locked, measured)", .30, 3.0, "A9"),
]
def tri(a): return random.triangular(a[0],a[2],a[1])
def run():
    fin={}; zt=0.0; cost={}; ruin_hits=[]
    # Z is serial, C parallel (cap 4 ~ no queue here). Day = 8h of Z attention; calendar waits are absolute days.
    order=[]; seen=set()
    def visit(k):
        if k in seen: return
        for d in T[k][4]: visit(d)
        seen.add(k); order.append(k)
    for k in T: visit(k)
    for k in order:
        lab,who,du,pr,deps,wait=T[k]
        start=max([fin[d] for d in deps],default=0.0)
        d=tri(du)
        if random.random()<pr: d*=1+random.uniform(.5,1.5)
        extra=0
        for l,p,c,t in RUIN:
            if t==k and random.random()<p: extra+=c; ruin_hits.append(l)
        d+=extra
        if who=="Z":
            zt+=d
        end=start+d/8.0+wait   # days
        fin[k]=end; cost[k]=d
    return fin,zt,ruin_hits,cost
N=20000; tot=[];zs=[];crit={k:0 for k in T};hit={}
for _ in range(N):
    fin,zt,rh,cost=run()
    T_end=max(fin.values()); tot.append(T_end); zs.append(zt)
    # critical task = on the longest dependency chain to the end
    k=max(fin,key=fin.get)
    while True:
        crit[k]+=1
        ds=T[k][4]
        if not ds: break
        k=max(ds,key=lambda x:fin[x])
    for l in set(rh): hit[l]=hit.get(l,0)+1
q=lambda a,p:sorted(a)[int(p*len(a))]
print(f"calendar days to all-decisions-clean: p50={q(tot,.5):.1f} p80={q(tot,.8):.1f} p95={q(tot,.95):.1f}")
print(f"Zach attention hours: p50={q(zs,.5):.1f} p80={q(zs,.8):.1f} p95={q(zs,.95):.1f}")
print("\ncriticality index (share of trials on the critical path):")
for k,v in sorted(crit.items(),key=lambda x:-x[1])[:8]: print(f"  {k:4} {v/N:5.0%}  {T[k][0]}")
print("\nruin events fired (share of trials):")
for l,v in sorted(hit.items(),key=lambda x:-x[1]): print(f"  {v/N:5.0%}  {l}")
# fork: wire #934 as-is vs after cost fix
def fork(order_fix_first):
    n=0;ex=[]
    for _ in range(8000):
        base=tri((1,2.5,6)); gates=tri((.5,1,2.5))
        regress = (not order_fix_first) and random.random()<.5   # gates land first -> minutes regress
        ex.append(base+gates+(2.0 if regress else 0)+ (3.0 if (not order_fix_first and random.random()<.15) else 0))
    return statistics.mean(ex), q(ex,.95)
print("\nfork: #934 before vs after cost fix (hrs, mean/p95):", fork(False), "vs", fork(True))
