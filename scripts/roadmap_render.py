#!/usr/bin/env python3
"""roadmap_render.py: the Reading Room's sixth room, "what's next and what's blocked?". Read-only sweep, stdlib.

WHY: the induced backlog is one ledger among several. This room sweeps every ledger that holds open work,
sequences what the backlog graph can sequence, and lists the rest as unsequenced with its source, so the
roadmap never claims a smaller body of work than exists (absence rule, ADR-061).

WHAT IT READS (each row on the page names its source):
  backlog + debt   scripts/backlog_graph.py --json --debt   (waves, deps, tool fit, ripeness)
  risk             scripts/risk_underwriter.py --all --json  (premium, missing cover, flags)
  rows             _QUEUE/induced-backlog.jsonl              (jtbd, priority, door, ruin, route, issue links)
  github           gh issue list / gh pr list                 (open issues and PRs; skipped with --no-gh)
  corpus           _PROPOSALS/, _DECISIONS/ADR-*, runtime/specs/tool-catalog.json, surface-catalog.json,
                   _STATE/2026-10-07-tool-cluster-jtbd-map.json, _ARTIFACTS/atlas/intake-queue.json
  other repos      ~/ret-rfp-intelligence/TODO.md + BACKLOG.md, ~/arcs-decision-receipts/.github/backlog-index.md
  project          --project-json (a snapshot of the claude.ai Project ledgers: PARKED, open receipts, Kintsugi)

WHAT IT NEVER DOES: write to any ledger, change a row, guess a priority, an owner or a date. Waves are
dependency depth, not calendar time. Fates stay human (NOTOMATION).

Usage:
  python3 scripts/roadmap_render.py --project-json PATH            # sweep + render _ARTIFACTS/atlas/roadmap.html
  python3 scripts/roadmap_render.py --project-json PATH --no-gh    # skip GitHub (offline)
  python3 scripts/roadmap_render.py --self-test
"""
import argparse, datetime, glob, html, json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "_ARTIFACTS", "atlas", "roadmap.html")
TOKENS = os.path.join(ROOT, "src", "ui-kit", "recoil-report", "_tokens.css")  # inlined verbatim (token_source_gate)
HOME = os.path.expanduser("~")
LIVE = {"OPEN", "READY", "RUNNING", "BLOCKED", "HELD", "HOLDING"}
PRI = ["P0", "P1", "P2", "P3", "P4", "unranked"]


def run_json(cmd):
    try:
        out = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=300)
        return json.loads(out.stdout) if out.returncode == 0 and out.stdout.strip() else None, out.stderr.strip()[-300:]
    except Exception as e:  # report, never hide
        return None, str(e)


def norm_pri(p):
    p = str(p or "")
    m = re.match(r"P([0-4])", p)
    return "P" + m.group(1) if m else "unranked"


def sweep(project_json, use_gh):
    notes = []
    graph, err = run_json([sys.executable, "scripts/backlog_graph.py", "--json", "--debt"])
    if graph is None:
        notes.append("backlog_graph.py --debt failed: " + err)
        graph, err = run_json([sys.executable, "scripts/backlog_graph.py", "--json"])
    risk, rerr = run_json([sys.executable, "scripts/risk_underwriter.py", "--all", "--json"])
    if risk is None:
        notes.append("risk_underwriter.py failed: " + rerr)
    rows = {}
    for line in open(os.path.join(ROOT, "_QUEUE", "induced-backlog.jsonl")):
        if line.strip():
            r = json.loads(line)
            rows[r["id"]] = r
    riskmap = {x["id"]: x for x in (risk or [])}
    issues, prs = [], []
    if use_gh:
        i, e = run_json(["gh", "issue", "list", "--state", "open", "--limit", "500", "--json", "number,title,labels,url"])
        p, e2 = run_json(["gh", "pr", "list", "--state", "open", "--limit", "200", "--json", "number,title,isDraft,url,headRefName"])
        issues, prs = i or [], p or []
        if i is None: notes.append("gh issue list failed: " + e)
        if p is None: notes.append("gh pr list failed: " + e2)
    else:
        notes.append("GitHub not read (--no-gh)")

    # sequenced jobs: graph nodes enriched with their backlog row
    jobs = []
    for n in (graph or {}).get("nodes", []):
        r = rows.get(n["id"], {})
        route = r.get("route") or {}
        rk = riskmap.get(n["id"], {})
        sev = None
        if n["id"].startswith("debt:"):
            src = "GitHub debt issue (backlog_graph --debt)"
        else:
            src = "_QUEUE/induced-backlog.jsonl"
        jobs.append({
            "id": n["id"], "title": (r.get("jtbd") or n["id"])[:220], "state": n.get("state"), "wave": n.get("wave", 0),
            "pri": norm_pri(r.get("priority") or sev), "ripe": n.get("ripeness"), "ready": bool(n.get("ready_now")),
            "tool": n.get("tool"), "config": str(route.get("tool") or "")[:120], "deps": n.get("deps") or [],
            "unblocks": r.get("unblocks") or [], "desc": n.get("descendants", 0), "door": r.get("door") or "",
            "ruin": r.get("ruin") or "", "issue": r.get("gh_url") or (("#" + str(r["gh_issue"])) if r.get("gh_issue") else ""),
            "premium": rk.get("premium", ""), "cover": rk.get("missing_cover", []), "trigger": str(r.get("trigger") or "")[:160],
            "cost": n.get("cost") or "", "src": src,
        })
    seq_ids = {j["id"] for j in jobs}

    # unsequenced: everything open that the graph cannot see
    uns = []
    def add(kind, ident, title, src, state="open"):
        uns.append({"kind": kind, "id": str(ident), "title": str(title)[:200], "src": src, "state": state})
    for rid, r in rows.items():
        if r.get("state") in LIVE and rid not in seq_ids:
            add("backlog", rid, r.get("jtbd", ""), "_QUEUE/induced-backlog.jsonl (live, outside the graph)", r.get("state"))
    debt_marked = 0
    mirrors = 0
    for it in issues:
        labels = [l["name"] for l in it.get("labels", [])]
        if "debt" in labels:
            debt_marked += 1
            continue  # already sequenced through --debt
        mm = re.match(r"\[backlog\]\s+(\S+)", it.get("title", ""))
        if mm and (mm.group(1) in seq_ids or mm.group(1) in rows):
            mirrors += 1
            continue  # a GitHub mirror of a backlog row already counted
        add("issue", "#%s" % it["number"], it["title"], "GitHub issue (gh issue list)", ",".join(labels) or "open")
    for p in prs:
        add("pr", "PR #%s" % p["number"], p["title"], "GitHub PR (gh pr list)", "draft" if p.get("isDraft") else "open")
    for f in sorted(glob.glob(os.path.join(ROOT, "_PROPOSALS", "*.md")))[-80:]:
        head = open(f, errors="ignore").read(600)
        m = re.search(r"^#\s+(.+)$", head, re.M)
        add("proposal", os.path.basename(f), m.group(1) if m else os.path.basename(f), "_PROPOSALS/", "awaiting ruling")
    tc = json.load(open(os.path.join(ROOT, "runtime", "specs", "tool-catalog.json")))
    for t in tc.get("tools", []):
        if t.get("state") == "UNAUDITED":
            add("tool", t["name"], (t.get("jtbd") or "")[:160], "runtime/specs/tool-catalog.json", "UNAUDITED")
    cm_path = os.path.join(ROOT, "_STATE", "2026-10-07-tool-cluster-jtbd-map.json")
    if os.path.exists(cm_path):
        cm = json.load(open(cm_path))
        for k, g in enumerate(cm.get("job_clusters_without_a_tool", [])):
            add("job-without-tool", "gap-%d" % (k + 1), g, "_STATE/2026-10-07-tool-cluster-jtbd-map.json (DRAFT)", "no tool")
    sc = json.load(open(os.path.join(ROOT, "runtime", "specs", "surface-catalog.json")))
    for b in sc.get("broken_destinations", []):
        add("surface", "broken", json.dumps(b)[:160], "runtime/specs/surface-catalog.json", "broken destination")
    for u in sc.get("unrouted_public_html", []):
        add("surface", "unrouted", u if isinstance(u, str) else json.dumps(u)[:160], "runtime/specs/surface-catalog.json", "unrouted page")
    ret_n = 0
    for name in ("TODO.md", "BACKLOG.md"):
        p = os.path.join(HOME, "ret-rfp-intelligence", name)
        if os.path.exists(p):
            for line in open(p, errors="ignore"):
                m = re.match(r"^\s*(\d+)\.\s+(.+)", line)
                if m:
                    ret_n += 1
                    add("ret", "%s-%s" % (name.split(".")[0].lower(), m.group(1)), m.group(2), "~/ret-rfp-intelligence/" + name)
        else:
            notes.append("not found: ~/ret-rfp-intelligence/" + name)
    adr_repo = os.path.join(HOME, "arcs-decision-receipts", ".github", "backlog-index.md")
    if os.path.exists(adr_repo):
        for line in open(adr_repo, errors="ignore"):
            if line.startswith("|") and not re.match(r"^\|\s*[-:]+", line) and "Item" not in line[:30]:
                cells = [c.strip() for c in line.strip().strip("|").split("|")]
                if len(cells) >= 2 and cells[0]:
                    add("adr-repo", cells[0][:24], " / ".join(cells[1:3]), "~/arcs-decision-receipts/.github/backlog-index.md (last commit 2026-08-23)", "stale?")
    proj = json.load(open(project_json)) if project_json and os.path.exists(project_json) else None
    if proj:
        for n, t in proj.get("parked", []):
            add("parked", "#%s" % n, t, "Project claude/PARKED.md + addendum (snapshot)", "parked")
        for rid, t in proj.get("receipts_open", []):
            add("receipt", rid, t, "Project claude/RECEIPTS addenda (snapshot)", "open")
    else:
        notes.append("Project snapshot not given (--project-json)")
    intake = {}
    ip = os.path.join(ROOT, "_ARTIFACTS", "atlas", "intake-queue.json")
    if os.path.exists(ip):
        q = json.load(open(ip))
        for r in q.get("rows", []):
            intake[r.get("kind", "?")] = intake.get(r.get("kind", "?"), 0) + 1

    counts = {
        "backlog rows (all states)": len(rows),
        "backlog live": sum(1 for r in rows.values() if r.get("state") in LIVE),
        "graph active nodes (backlog + debt)": len(jobs),
        "debt issues sequenced": sum(1 for j in jobs if j["id"].startswith("debt:")),
        "open GitHub issues (not debt)": sum(1 for u in uns if u["kind"] == "issue"),
        "open PRs": len(prs),
        "issue mirrors of backlog rows (not counted)": mirrors,
        "proposals (newest 80 of _PROPOSALS)": sum(1 for u in uns if u["kind"] == "proposal"),
        "UNAUDITED tools": sum(1 for u in uns if u["kind"] == "tool"),
        "jobs with no tool": sum(1 for u in uns if u["kind"] == "job-without-tool"),
        "surface defects": sum(1 for u in uns if u["kind"] == "surface"),
        "RET backlog items": ret_n,
        "arcs-decision-receipts rows": sum(1 for u in uns if u["kind"] == "adr-repo"),
        "PARKED ideas": sum(1 for u in uns if u["kind"] == "parked"),
        "open receipts": sum(1 for u in uns if u["kind"] == "receipt"),
        "corpus records in no digest": sum(intake.values()),
        "ADR files": len(glob.glob(os.path.join(ROOT, "_DECISIONS", "ADR-*.md"))),
    }
    counts["total open items swept"] = len(jobs) + len(uns)
    return {"jobs": jobs, "uns": uns, "counts": counts, "intake": intake, "findings": (graph or {}).get("findings", {}),
            "waves": max([j["wave"] for j in jobs] or [0]), "proj": proj or {}, "notes": notes}


def risks(d):
    """The funhouse optics register (Chapter Book Canon, Funhouse Optics, Q1 to Q6). Rule-based, stated."""
    out = []
    J = d["jobs"]
    for j in J:
        if str(j["door"]).startswith("one-way") or str(j["ruin"]).split(" ")[0] in ("high", "medium") or j["premium"] in ("SPECIALTY", "UNINSURABLE"):
            out.append({"lens": "Concave", "q": "damage if wrong", "item": j["id"], "why": "door %s, ruin %s, premium %s%s" % (
                j["door"] or "blank", j["ruin"] or "blank", j["premium"] or "unpriced", ("; missing cover: " + ", ".join(j["cover"])) if j["cover"] else ""),
                "door": j["door"] or "two-way", "owner": "Zach (decision)", "src": "induced-backlog.jsonl + risk_underwriter.py"})
    for j in sorted(J, key=lambda x: -x["desc"])[:8]:
        if j["desc"]:
            out.append({"lens": "Convex", "q": "scales if right", "item": j["id"], "why": "unblocks %d downstream jobs" % j["desc"],
                        "door": j["door"] or "two-way", "owner": "agent, Zach rules the fate", "src": "backlog_graph.py descendants"})
    for name, n in d["proj"].get("kintsugi_classes", []):
        out.append({"lens": "Posterior", "q": "what past receipts say", "item": name, "why": "%d logged guards in this class; expect it again" % n,
                    "door": "two-way", "owner": "Claude (guard), Zach (rule)", "src": "Project claude/BOOT.md standing classes"})
    for u in d["uns"]:
        if u["kind"] == "job-without-tool":
            out.append({"lens": "Anterior", "q": "6 to 12 months out", "item": u["id"], "why": u["title"][:180],
                        "door": "two-way", "owner": "unassigned", "src": u["src"]})
    for o in d["proj"].get("overrides_of_R012", []):
        out.append({"lens": "Parabolic", "q": "emotional zoom", "item": o, "why": "built against the PARKED hold (R-012) on the day it was wanted",
                    "door": "two-way", "owner": "Zach", "src": "Project RECEIPTS / KINTSUGI"})
    for tag in ("receipt", "gate", "surface"):
        hits = [j["id"] for j in J if tag in (j["id"] + " " + j["title"]).lower()]
        if len(hits) >= 4:
            out.append({"lens": "Orthogonal", "q": "same shape elsewhere", "item": tag, "why": "%d jobs across workstreams share it: one primitive, not %d fixes" % (len(hits), len(hits)),
                        "door": "two-way", "owner": "agent proposes, Zach rules", "src": "job ids + jtbd text"})
    return out


CSS = """
:root{--ln2:#26374a;--dur-base:240ms}
*{box-sizing:border-box;margin:0;padding:0}
html{background:var(--bg);color:var(--text);font-family:var(--ds-font-sans);-webkit-font-smoothing:antialiased}
::selection{background:rgba(0,240,255,.25);color:var(--text)}
body{max-width:1180px;margin:0 auto;padding:24px 20px 80px;font-size:.925rem;line-height:1.6}
a{color:var(--cyan);text-underline-offset:3px}
h1{font-size:var(--fs-display);font-weight:600;letter-spacing:-.02em;text-wrap:balance;margin:0 0 6px}
h2{font-size:1.15rem;font-weight:600;margin:34px 0 6px}
.lede{color:var(--text-secondary);max-width:none;margin:0 0 4px}
.note{color:var(--dimmed);font-size:var(--fs-body)}
.mono{font-family:var(--ds-font-mono);font-variant-numeric:tabular-nums}
.label{font-family:var(--ds-font-mono);font-size:11px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:var(--dimmed)}
.deck{position:sticky;top:0;z-index:20;display:flex;flex-wrap:wrap;gap:8px;align-items:center;padding:10px 0;margin:14px 0 4px;
 background:rgba(2,4,8,.72);backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);border-bottom:1px solid var(--border)}
.deck button,.deck select,.deck input{font-family:var(--ds-font-mono);font-size:11px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--text-secondary);
 background:transparent;border:1px solid var(--border);border-radius:3px;padding:7px 10px;transition:border-color var(--dur-fast) var(--ease-out),color var(--dur-fast) var(--ease-out)}
.deck input{text-transform:none;letter-spacing:0;min-width:180px;background:var(--elevated)}
.deck button:hover,.deck button:focus-visible{border-color:var(--cyan);color:var(--cyan)}
.deck button[aria-pressed=true]{border-color:var(--cyan);color:var(--cyan);background:rgba(0,240,255,.08)}
:focus-visible{outline:2px solid var(--cyan);outline-offset:2px}
.counts{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:1px;background:var(--border);border:1px solid var(--border);border-radius:6px;overflow:hidden;margin:12px 0}
.counts div{background:var(--surface);padding:10px 12px}
.counts b{display:block;font-family:var(--ds-font-mono);font-size:var(--fs-headline);font-weight:700;font-variant-numeric:tabular-nums}
.counts span{font-size:var(--fs-body);color:var(--dimmed)}
.counts .total b{color:var(--cyan)}
.wrap{overflow-x:auto;border:1px solid var(--border);border-radius:6px;background:var(--surface);padding:6px}
.gantt{display:grid;min-width:880px}
.gr{display:contents}
.gr>div{border-bottom:1px solid rgba(30,41,59,.6);padding:5px 8px;font-size:var(--fs-body);min-height:30px;display:flex;align-items:center}
.gh>div{position:sticky;top:0;background:var(--elevated);font-family:var(--ds-font-mono);font-size:11px;font-weight:700;letter-spacing:.1em;color:var(--dimmed)}
.grp>div{background:rgba(17,24,39,.9);font-family:var(--ds-font-mono);font-size:11px;font-weight:700;letter-spacing:.12em;color:var(--text-secondary);cursor:pointer}
.id{font-family:var(--ds-font-mono);font-size:var(--fs-body);color:var(--cyan);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;cursor:pointer;background:none;border:0;text-align:left;width:100%}
.cell{position:relative;padding:0 !important}
.bar{position:absolute;top:7px;height:16px;border-radius:3px;border:1px solid var(--dimmed);background:var(--elevated)}
.bar.RUNNING{background:rgba(0,240,255,.35);border-color:var(--cyan)}
.bar.READY{background:rgba(0,255,157,.25);border-color:var(--green)}
.bar.BLOCKED{background:rgba(255,77,109,.25);border-color:var(--red)}
.bar.OPEN{background:rgba(167,139,250,.18);border-color:var(--violet)}
.bar.HELD,.bar.HOLDING{background:rgba(131,145,167,.12);border-style:dashed}
.bar.oneway{outline:1px solid var(--gold);outline-offset:1px}
.chip{display:inline-block;font-family:var(--ds-font-mono);font-size:11px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;border:1px solid var(--border);border-radius:3px;padding:1px 6px;margin:1px 4px 1px 0;color:var(--dimmed)}
.c-rd{color:var(--red);border-color:rgba(255,77,109,.5)}.c-go{color:var(--gold);border-color:rgba(255,215,0,.5)}.c-gr{color:var(--green);border-color:rgba(0,255,157,.45)}.c-cy{color:var(--cyan);border-color:rgba(0,240,255,.45)}
#detail{position:sticky;bottom:0;z-index:15;margin-top:10px;background:var(--surface);border:1px solid var(--ln2);border-radius:6px;padding:12px 14px;display:none}
#detail.on{display:block}
#detail dl{display:grid;grid-template-columns:120px 1fr;gap:4px 12px;font-size:var(--fs-body)}
#detail dt{font-family:var(--ds-font-mono);font-size:11px;font-weight:700;letter-spacing:.1em;color:var(--dimmed);text-transform:uppercase}
table{border-collapse:collapse;width:100%;font-size:var(--fs-body)}
th{text-align:left;font-family:var(--ds-font-mono);font-size:11px;font-weight:700;letter-spacing:.1em;color:var(--dimmed);border-bottom:1px solid var(--border);padding:7px 8px;white-space:nowrap;background:var(--elevated);position:sticky;top:0}
td{border-bottom:1px solid rgba(30,41,59,.6);padding:6px 8px;vertical-align:top}
td.k{font-family:var(--ds-font-mono);font-size:var(--fs-body);color:var(--cyan);white-space:nowrap}
.scroll{max-height:520px;overflow:auto}
details{margin-top:28px;color:var(--dimmed)}
summary{cursor:pointer;font-weight:600;font-size:var(--fs-body);color:var(--text-secondary)}
details p{margin:8px 0;font-size:var(--fs-body)}
::-webkit-scrollbar{height:8px;width:8px}::-webkit-scrollbar-thumb{background:var(--ln2);border-radius:3px}::-webkit-scrollbar-track{background:transparent}
@media (max-width:640px){.deck button,.deck input,#detail .chip,.id{min-height:44px;min-width:44px}.grp>div{min-height:44px}}
@media (prefers-reduced-motion:reduce){*{transition:none !important}}
"""

JS = r"""
const D=JSON.parse(document.getElementById('data').textContent);
const W=D.waves+1, PRI=["P0","P1","P2","P3","P4","unranked"];
let fState='live', fPri=new Set(PRI), q='', open=new Set(["P0","P1"]);
const el=(t,c,txt)=>{const e=document.createElement(t);if(c)e.className=c;if(txt!=null)e.textContent=txt;return e};
function pass(j){
 if(fState==='ready'&&!j.ready)return false;
 if(fState==='blocked'&&j.state!=='BLOCKED')return false;
 if(fState==='oneway'&&!String(j.door).startsWith('one-way'))return false;
 if(!fPri.has(j.pri))return false;
 if(q){const s=(j.id+' '+j.title+' '+j.config).toLowerCase();if(!s.includes(q))return false}
 return true}
function draw(){
 const g=document.getElementById('gantt');g.replaceChildren();
 g.style.gridTemplateColumns='minmax(200px,260px) minmax(260px,1fr) 70px repeat('+W+',minmax(34px,1fr))';
 const h=el('div','gr gh');['JOB','WHAT IT DOES','STATE'].forEach(t=>h.appendChild(el('div','',t)));
 for(let w=0;w<W;w++)h.appendChild(el('div','', 'W'+w));g.appendChild(h);
 let shown=0;
 PRI.forEach(p=>{
  const js=D.jobs.filter(j=>j.pri===p&&pass(j)).sort((a,b)=>a.wave-b.wave||(b.desc-a.desc));
  if(!js.length)return;
  const r=el('div','gr grp');const c=el('div','',(open.has(p)?'[-] ':'[+] ')+p+'  '+js.length+' jobs');
  c.style.gridColumn='1 / -1';c.tabIndex=0;c.setAttribute('role','button');
  c.onclick=c.onkeydown=(e)=>{if(e.type==='keydown'&&e.key!=='Enter')return;open.has(p)?open.delete(p):open.add(p);draw()};
  r.appendChild(c);g.appendChild(r);
  if(!open.has(p))return;
  js.forEach(j=>{shown++;
   const row=el('div','gr');const b=el('button','id',j.id);b.onclick=()=>detail(j);
   const c1=el('div');c1.appendChild(b);row.appendChild(c1);
   row.appendChild(el('div','',j.title.slice(0,120)));
   row.appendChild(el('div','mono',j.state));
   for(let w=0;w<W;w++){const cell=el('div','cell');if(w===j.wave){const bar=el('div','bar '+j.state+(String(j.door).startsWith('one-way')?' oneway':''));bar.style.left='3px';bar.style.right='3px';bar.title=j.id;cell.appendChild(bar)}row.appendChild(cell)}
   g.appendChild(row)})});
 document.getElementById('shown').textContent=shown+' shown'}
function detail(j){
 const d=document.getElementById('detail');d.classList.add('on');const dl=d.querySelector('dl');dl.replaceChildren();
 const add=(k,v,cls)=>{dl.appendChild(el('dt','',k));const dd=el('dd',cls||'');if(v instanceof Node)dd.appendChild(v);else dd.textContent=v||'none';dl.appendChild(dd)};
 add('Job',j.id,'mono');add('What',j.title);add('State',j.state+' · wave '+j.wave+' · '+(j.ripe||''));
 add('Priority',j.pri);add('Depends on',(j.deps||[]).join(', '));add('Unblocks',(j.unblocks||[]).join(', ')+(j.desc?'  ('+j.desc+' downstream)':''));
 add('Tool fit',j.tool);add('Config',j.config);add('Trigger',j.trigger);add('Door / ruin',(j.door||'blank')+' / '+(j.ruin||'blank'));
 add('Risk premium',String(j.premium||'')+((j.cover||[]).length?' · missing cover: '+j.cover.join(', '):''));
 add('Linked issue',j.issue);add('Cost',j.cost);add('Source',j.src);
 const a=el('a','', 'Open the field HUD');a.href='/hud';a.target='_top';add('HUD',a)}
document.querySelectorAll('[data-state]').forEach(b=>b.onclick=()=>{fState=b.dataset.state;document.querySelectorAll('[data-state]').forEach(x=>x.setAttribute('aria-pressed',x===b));draw()});
document.querySelectorAll('[data-pri]').forEach(b=>b.onclick=()=>{const p=b.dataset.pri;fPri.has(p)?fPri.delete(p):fPri.add(p);b.setAttribute('aria-pressed',fPri.has(p));draw()});
document.getElementById('q').oninput=e=>{q=e.target.value.toLowerCase().trim();draw()};
document.getElementById('closeDetail').onclick=()=>document.getElementById('detail').classList.remove('on');
draw();
"""


def page(d, rk):
    e = html.escape
    c = d["counts"]
    total = c.pop("total open items swept")
    cells = "".join('<div><b>%s</b><span>%s</span></div>' % (e(str(v)), e(k)) for k, v in c.items())
    cells = '<div class="total"><b>%d</b><span>total open items swept</span></div>' % total + cells
    rrows = "".join('<tr><td class="k">%s</td><td>%s</td><td class="k">%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % tuple(
        e(str(x)) for x in (r["lens"], r["q"], r["item"], r["why"], r["door"], r["owner"], r["src"])) for r in rk)
    urows = "".join('<tr><td>%s</td><td class="k">%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % tuple(
        e(str(x)) for x in (u["kind"], u["id"], u["title"], u["state"], u["src"])) for u in d["uns"])
    lens_n = {}
    for r in rk:
        lens_n[r["lens"]] = lens_n.get(r["lens"], 0) + 1
    lens_line = ", ".join("%s %d" % (k, v) for k, v in lens_n.items())
    deep = sum(1 for j in d["jobs"] if j["wave"] >= 1)
    front = sum(1 for j in d["jobs"] if j["wave"] == 0)
    ready = sum(1 for j in d["jobs"] if j["ready"])
    unranked = sum(1 for j in d["jobs"] if j["pri"] == "unranked")
    notes = "".join("<li>%s</li>" % e(n) for n in d["notes"]) or "<li>none</li>"
    data = json.dumps({"jobs": d["jobs"], "waves": d["waves"]}).replace("</", "<\\/")
    today = datetime.date.today().isoformat()
    pri_btns = "".join('<button type="button" data-pri="%s" aria-pressed="true">%s</button>' % (p, p) for p in PRI)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>ARCS Roadmap · what's next and what's blocked</title><meta name="robots" content="noindex, nofollow">
<style>
@@TOKENS@@
{CSS}</style></head><body>
<main>
<h1>What's next, and what's blocked</h1>
<p class="lede">{total} open items across every ledger. {len(d['jobs'])} are sequenced by the backlog graph: {ready} are ready to start now; {front} have no unfinished dependency (wave 0, many of them held), and {deep} wait on something upstream, in chains up to {d['waves']} waves deep. {unranked} of the sequenced jobs carry no priority yet. The other {len(d['uns'])} are open but not yet in the graph, listed with their source below.</p>
<p class="note mono">Rendered {today} by scripts/roadmap_render.py. Waves are dependency depth, not dates. Snapshot: re-run the script (or scripts/reading_room_sync.py) to refresh.</p>
<div class="counts">{cells}</div>

<h2 id="gantt-h">Sequence by priority</h2>
<p class="note">Each bar sits at its dependency wave. Gold ring: one-way door. Click a job for its dependencies, config, linked issue, risk and a link to the field HUD.</p>
<div class="deck" role="toolbar" aria-label="Filters">
<button type="button" data-state="live" aria-pressed="true">All live</button><button type="button" data-state="ready" aria-pressed="false">Ready now</button>
<button type="button" data-state="blocked" aria-pressed="false">Blocked</button><button type="button" data-state="oneway" aria-pressed="false">One-way doors</button>
{pri_btns}<input id="q" type="search" placeholder="Filter by id, words or tool" aria-label="Filter jobs"><span class="label" id="shown"></span></div>
<div class="wrap" tabindex="0" role="region" aria-label="Roadmap jobs by priority and wave"><div class="gantt" id="gantt"></div></div>
<div id="detail" role="region" aria-label="Job detail"><button type="button" id="closeDetail" class="chip" style="float:right;background:none;cursor:pointer">Close</button><dl></dl></div>

<h2 id="risk-h">Risk register: funhouse optics</h2>
<p class="note">Six lenses from the canon (Chapter Book Canon, Funhouse Optics, Q1 to Q6): {e(lens_line)}. Each row is placed by a stated rule (see the notes at the foot), never by judgment.</p>
<div class="wrap scroll" tabindex="0" role="region" aria-label="Risk register"><table><thead><tr><th>Lens</th><th>Question</th><th>Item</th><th>Why</th><th>Door</th><th>Owner</th><th>Source</th></tr></thead><tbody>{rrows}</tbody></table></div>

<h2 id="uns-h">Open, but not in the graph yet</h2>
<p class="note">These have no dependency edges, so they cannot be sequenced. Placing one is a Curator job: give it a row, a priority and its edges.</p>
<div class="wrap scroll" tabindex="0" role="region" aria-label="Unsequenced open items"><table><thead><tr><th>Kind</th><th>Id</th><th>What</th><th>State</th><th>Source</th></tr></thead><tbody>{urows}</tbody></table></div>

<details><summary>How this room is built, and what it does not show</summary>
<p>Sequenced jobs come from scripts/backlog_graph.py --json --debt (backlog rows plus GitHub debt issues), enriched with each row's priority, door, ruin, route and issue link from _QUEUE/induced-backlog.jsonl, and priced by scripts/risk_underwriter.py. Priority is copied from the row; a row with none shows as unranked, never guessed.</p>
<p>Risk rules: Concave = one-way door, ruin high or medium, or a SPECIALTY / UNINSURABLE premium. Convex = the eight jobs with the most downstream dependents. Posterior = each Kintsugi class from the Project ledger, with its guard count. Anterior = jobs the tool-cluster map lists as having no tool. Parabolic = builds made against the PARKED hold. Orthogonal = words shared by four or more jobs. Owners are a role, not a person assigned by this script.</p>
<p>HUD integration: NOW, each job links to the field HUD (arcs.care/hud). NEXT: the HUD takes a job id and draws its route (WORLD.md THE HUD: terrain, route, time); today src/app/hud reads no query parameter, so that seam is not built.</p>
<p>Not shown: calendar dates and durations (most rows carry none; risk_underwriter prints UNKNOWN rather than guess), and scenarios or premortems, which are written by hand. Reading-room cache slices stay as graded; this room does not regrade. Em-dashes in source text display as hyphens here; the ledgers are unchanged.</p>
<p>Graph findings: {e(json.dumps({k: len(v) for k, v in d['findings'].items()}))}. Sweep notes:</p><ul class="note">{notes}</ul>
</details>
</main>
<script id="data" type="application/json">{data}</script>
<script>{JS}</script>
</body></html>"""


def self_test():
    assert norm_pri("P1") == "P1" and norm_pri(None) == "unranked" and norm_pri("P0-when-resumed") == "P0"
    d = {"jobs": [{"id": "a", "title": "t", "door": "one-way", "ruin": "", "premium": "4", "cover": [], "desc": 3}],
         "uns": [{"kind": "job-without-tool", "id": "gap-1", "title": "x", "src": "s"}], "proj": {}, "counts": {}, "notes": []}
    r = risks(d)
    assert any(x["lens"] == "Concave" for x in r) and any(x["lens"] == "Anterior" for x in r)
    print("roadmap_render self-test: ok")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--project-json")
    ap.add_argument("--no-gh", action="store_true")
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    d = sweep(a.project_json, not a.no_gh)
    rk = risks(d)
    total = d["counts"]["total open items swept"]
    doc = page(d, rk).replace(chr(0x2014), " - ")  # source text keeps its em-dashes; the page shows hyphens (brand rule)
    assert chr(0x2014) not in doc, "em-dash in render"
    doc = doc.replace("@@TOKENS@@", open(TOKENS, encoding="utf-8").read())  # verbatim, header line included
    open(a.out, "w").write(doc)
    print("roadmap: %d open items (%d sequenced, %d unsequenced), %d risks -> %s" % (
        total, len(d["jobs"]), len(d["uns"]), len(rk), os.path.relpath(a.out, ROOT)))
    for n in d["notes"]:
        print("  note:", n)


if __name__ == "__main__":
    main()
