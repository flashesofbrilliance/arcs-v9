#!/usr/bin/env python3
"""field_render.py: a bird's-eye "field" page over the repo's live state, built on the ARCS ui-kit.

Read-only. Reads git worktrees, _QUEUE/induced-backlog.jsonl, scripts/open_loops.py --json,
the memory folder's file ages, and _PROPOSALS/*.json. Writes one self-contained page plus a
machine layer (<script type="application/json" id="arcs-field">).

Honest labels: counts and ages are measured (MEASURED). The circuit reading of backlog states
(flowing, stored, resistance, sink) is an analogy (METAPHOR): nothing measures current yet.

  python3 scripts/field_render.py                  # writes _PROPOSALS/rendered/field.html
  python3 scripts/field_render.py --self-test

Stdlib only.
"""
import argparse, collections, datetime as dt, glob, html, json, math, os, subprocess, sys, time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TOKENS = os.path.join(ROOT, "src", "ui-kit", "recoil-report", "_tokens.css")
MEM = os.path.expanduser("~/.claude/projects/-Users-zharris-arcs-v9/memory")
CIRCUIT = [  # state -> (role, colour var, plain meaning)
    ("OPEN", "flowing", "cyan"), ("READY", "flowing", "cyan"), ("RUNNING", "flowing", "cyan"),
    ("HOLDING", "stored", "gold"), ("HELD", "stored", "gold"),
    ("BLOCKED", "resistance", "red"),
    ("DONE", "sink", "green"), ("COMPOSTED", "sink", "green"), ("SUPERSEDED", "sink", "green"),
]
ROLE_TEXT = {"flowing": "Flowing: work that can move now", "stored": "Stored (capacitor): held until a trigger fires",
             "resistance": "Resistance: blocked by a gate or dependency", "sink": "Sink: finished, composted or replaced"}
CSS = """
* { box-sizing: border-box; }
body { background: var(--bg); color: var(--text); font-family: var(--font-sans); font-size: 15px; line-height: 1.6; margin: 0; padding-inline: 16px; padding-block: 28px; }
main { max-width: 1040px; margin: 0 auto; display: flex; flex-direction: column; gap: 24px; }
h1 { font-family: var(--font-display); font-size: clamp(1.5rem, 4vw, 2.2rem); font-weight: 600; line-height: 1.2; margin: 0 0 6px; text-wrap: balance; }
h2 { font-size: 1rem; margin: 0 0 6px; }
p { margin: 0 0 10px; }
.recoil-header { display: flex; align-items: stretch; background: var(--surface); border: 1px solid var(--border); border-radius: var(--r-lg); overflow: hidden; }
.recoil-header::before { content: ''; width: 4px; flex-shrink: 0; background: var(--cyan); }
.header-arcs { padding: 16px 24px; border-right: 1px solid var(--border); display: flex; flex-direction: column; justify-content: center; }
.arcs-mark { font-family: var(--font-display); font-size: 28px; font-weight: 700; color: var(--cyan); line-height: 1; }
.arcs-sub { font-family: var(--font-mono); font-size: 10px; color: var(--muted); letter-spacing: .12em; text-transform: uppercase; margin-top: 6px; }
.header-center { flex: 1; min-width: 0; padding: 16px 24px; }
.receipt-id { font-family: var(--font-mono); font-size: 11px; color: var(--dimmed); margin-bottom: 8px; overflow-wrap: anywhere; }
.section-label { font-family: var(--font-mono); font-size: 11px; letter-spacing: .12em; text-transform: uppercase; color: var(--muted); margin-bottom: 12px; }
.panel { background: var(--surface); border: 1px solid var(--border); border-radius: var(--r-md); padding: 20px; }
.muted { color: var(--dimmed); font-size: 13px; }
.kpis { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; }
.kpi { background: var(--surface-2); border: 1px solid var(--border); border-radius: var(--r-sm); padding: 12px; }
.kpi b { display: block; font-family: var(--font-mono); font-size: 28px; line-height: 1.1; }
.kpi span { font-size: 12px; color: var(--dimmed); }
.two { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; align-items: start; }
.legend { list-style: none; margin: 0; padding: 0; display: grid; gap: 8px; }
.legend li { display: grid; grid-template-columns: 14px 1fr auto; gap: 10px; align-items: baseline; font-size: 13px; }
.sw { width: 12px; height: 12px; border-radius: 3px; display: inline-block; }
.wt { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 8px; }
.cell { background: var(--surface-2); border: 1px solid var(--border); border-left-width: 4px; border-radius: var(--r-sm); padding: 8px 10px; min-width: 0; font-size: 12px; }
.cell b { display: block; font-family: var(--font-mono); font-size: 11px; overflow-wrap: anywhere; }
.cell i { font-style: normal; color: var(--dimmed); }
.cell.g { border-left-color: var(--green); } .cell.c { border-left-color: var(--cyan); }
.cell.y { border-left-color: var(--gold); } .cell.r { border-left-color: var(--red); }
.pill { display: inline-block; padding: 1px 9px; border-radius: 99px; font-family: var(--font-mono); font-size: 11px; border: 1px solid; white-space: nowrap; }
.pill.green { color: var(--green); border-color: var(--green); background: var(--green-bg); }
.pill.gold { color: var(--gold); border-color: var(--gold); background: var(--gold-bg); }
.pill.red { color: var(--red); border-color: var(--red); background: var(--red-bg); }
.pill.cyan { color: var(--cyan); border-color: var(--cyan); background: var(--cyan-bg); }
.bar { display: flex; height: 22px; border-radius: 4px; overflow: hidden; border: 1px solid var(--border); }
.bar div { min-width: 2px; }
.tw { overflow-x: auto; }
table { border-collapse: collapse; width: 100%; font-size: 13px; }
th, td { text-align: left; padding: 7px 10px; border-bottom: 1px solid var(--border); vertical-align: top; }
th { color: var(--muted); font-family: var(--font-mono); font-size: 11px; letter-spacing: .06em; text-transform: uppercase; font-weight: 500; }
td.mono { font-family: var(--font-mono); font-size: 12px; }
a { color: var(--cyan); }
footer { font-family: var(--font-mono); font-size: 11px; color: var(--muted); }
@media (max-width: 640px) { .recoil-header { flex-direction: column; } .header-arcs { border-right: 0; border-bottom: 1px solid var(--border); } }
"""


def e(x):
    return html.escape(str(x), quote=True)


def sh(args, cwd=ROOT, timeout=20):
    try:
        return subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=timeout).stdout
    except Exception:
        return ""


def gather_worktrees(now):
    out, cur = [], {}
    for line in sh(["git", "worktree", "list", "--porcelain"]).splitlines() + [""]:
        if not line.strip():
            if cur.get("worktree"):
                out.append(cur)
            cur = {}
            continue
        k, _, v = line.partition(" ")
        cur[k] = v or True
    rows = []
    for w in out:
        path = w["worktree"]
        if "prunable" in w or not os.path.isdir(path) or path.startswith("/private/tmp"):
            continue
        ts = sh(["git", "-C", path, "log", "-1", "--format=%ct"]).strip()
        age = (now - int(ts)) / 86400 if ts.isdigit() else None
        dirty = len([l for l in sh(["git", "-C", path, "status", "--porcelain"]).splitlines() if l.strip()])
        branch = (w.get("branch") or "detached").replace("refs/heads/", "")
        rows.append({"name": os.path.basename(path.rstrip("/")) if "/worktrees/" in path else "main checkout",
                     "branch": branch, "age_days": None if age is None else round(age, 1), "dirty_files": dirty})
    rows.sort(key=lambda r: (r["age_days"] is None, r["age_days"] or 0))
    return rows


def gather_backlog():
    states = collections.Counter()
    for l in open(os.path.join(ROOT, "_QUEUE", "induced-backlog.jsonl"), encoding="utf-8"):
        l = l.strip()
        if not l:
            continue
        try:
            r = json.loads(l)
        except ValueError:
            continue
        if isinstance(r, dict) and "id" in r and r.get("state"):
            states[r["state"]] += 1
    return dict(states)


def gather_loops():
    raw = sh([sys.executable, os.path.join(ROOT, "scripts", "open_loops.py"), "--json", "--cap", "6"], timeout=60)
    try:
        d = json.loads(raw)
    except ValueError:
        return []
    return [{"title": s[0], "items": s[1]} for s in d.get("sections", []) if isinstance(s, list) and len(s) == 2]


def gather_memory(now):
    b = collections.OrderedDict([("under 7 days", 0), ("7 to 30 days", 0), ("30 to 90 days", 0), ("over 90 days", 0)])
    n = 0
    for f in glob.glob(os.path.join(MEM, "*.md")):
        if os.path.basename(f) == "MEMORY.md":
            continue
        age = (now - os.path.getmtime(f)) / 86400
        n += 1
        b["under 7 days" if age < 7 else "7 to 30 days" if age < 30 else "30 to 90 days" if age < 90 else "over 90 days"] += 1
    return {"files": n, "buckets": dict(b)}


def gather_proposals():
    rows = []
    for f in sorted(glob.glob(os.path.join(ROOT, "_PROPOSALS", "*.json"))):
        try:
            d = json.load(open(f, encoding="utf-8"))
        except ValueError:
            continue
        if isinstance(d, dict) and "controls" in d:
            tested = sum(1 for c in d["controls"] if "scored" in c.get("stage", "") or "adopted" in c.get("stage", ""))
            rows.append({"stem": os.path.splitext(os.path.basename(f))[0], "title": d["title"], "date": d["date"],
                         "decisions": len(d["decisions"]), "controls": len(d["controls"]), "tested": tested})
    return rows


def age_class(a):
    return "y" if a is None else "g" if a < 1 else "c" if a < 7 else "y" if a < 30 else "r"


def donut(states):
    roles = collections.OrderedDict((r, 0) for r in ROLE_TEXT)
    colour = {}
    for s, role, c in CIRCUIT:
        roles[role] += states.get(s, 0)
        colour[role] = c
    total = sum(roles.values()) or 1
    r, cx, cy, sw = 70, 90, 90, 26
    circ = 2 * math.pi * r
    off, parts = 0.0, []
    for role, n in roles.items():
        if not n:
            continue
        seg = circ * n / total
        parts.append('<circle r="%d" cx="%d" cy="%d" fill="none" stroke="var(--%s)" stroke-width="%d" stroke-dasharray="%.2f %.2f" '
                     'stroke-dashoffset="%.2f" transform="rotate(-90 %d %d)"><title>%s: %d</title></circle>'
                     % (r, cx, cy, colour[role], sw, seg, circ - seg, -off, cx, cy, e(role), n))
        off += seg
    svg = ('<svg viewBox="0 0 180 180" width="180" height="180" role="img" aria-label="Backlog by circuit role">'
           + "".join(parts) + '<text x="90" y="88" text-anchor="middle" font-family="var(--font-mono)" font-size="26" fill="var(--text)">%d</text>'
           '<text x="90" y="108" text-anchor="middle" font-family="var(--font-mono)" font-size="11" fill="var(--muted)">rows</text></svg>' % sum(roles.values()))
    return svg, roles, colour


def build():
    now = time.time()
    data = {"generated": dt.datetime.now().strftime("%Y-%m-%d %H:%M"), "worktrees": gather_worktrees(now),
            "backlog": gather_backlog(), "loops": gather_loops(), "memory": gather_memory(now), "proposals": gather_proposals()}
    return data


def render(d):
    tokens = open(TOKENS, encoding="utf-8").read()
    wts, bl, loops, mem, props = d["worktrees"], d["backlog"], d["loops"], d["memory"], d["proposals"]
    svg, roles, colour = donut(bl)
    rot = next((len(s["items"]) for s in loops if s["title"] == "Rotting"), 0)
    stale = sum(1 for w in wts if (w["age_days"] or 0) >= 7)
    o = ['<!doctype html><html lang="en"><head><!-- @arcs-template: recoil-report -->\n<!-- @arcs-mode: operate -->',
         '<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ARCS Field View</title>',
         '<style>\n' + tokens + '\n' + CSS + '</style></head><body><main>']
    o.append('<div class="recoil-header"><div class="header-arcs"><div class="arcs-mark">ARCS</div><div class="arcs-sub">Field view</div></div>'
             '<div class="header-center"><div class="receipt-id">snapshot %s · read-only · counts are measured, the circuit reading is an analogy</div>'
             '<h1>The whole mountain at a glance</h1><p>Where work is moving, where it is stored, where it is stuck, and what has gone stale. '
             'Built from the repo as it is right now, not from memory.</p></div></div>' % e(d["generated"]))
    o.append('<section class="kpis">'
             '<div class="kpi"><b>%d</b><span>worktrees (%d untouched for a week or more)</span></div>'
             '<div class="kpi"><b>%d</b><span>backlog rows (%d flowing, %d stored, %d blocked)</span></div>'
             '<div class="kpi"><b>%d</b><span>loops flagged rotting</span></div>'
             '<div class="kpi"><b>%d</b><span>memory notes (%d older than 90 days)</span></div>'
             '<div class="kpi"><b>%d</b><span>proposals (%d decisions waiting)</span></div></section>'
             % (len(wts), stale, sum(roles.values()), roles["flowing"], roles["stored"], roles["resistance"], rot, mem["files"],
                mem["buckets"]["over 90 days"], len(props), sum(p["decisions"] for p in props)))

    o.append('<section class="panel"><div class="section-label">§ Work on the loop</div><div class="two"><div>' + svg +
             '<p class="muted">Read it as a circuit. <span class="pill gold">METAPHOR</span> The row counts are measured; calling them current, '
             'capacitors and resistors is an analogy, because nothing measures flow between states yet.</p></div><div><ul class="legend">')
    for role, text in ROLE_TEXT.items():
        parts = ", ".join("%s %d" % (s, bl.get(s, 0)) for s, r, _ in CIRCUIT if r == role and bl.get(s, 0))
        o.append('<li><span class="sw" style="background:var(--%s)"></span><span>%s<br><span class="muted">%s</span></span><b>%d</b></li>'
                 % (colour[role], e(text), e(parts or "none"), roles[role]))
    o.append('</ul></div></div></section>')

    o.append('<section class="panel"><div class="section-label">§ Worktrees, freshest first</div>'
             '<p class="muted">Edge colour is the age of the last commit: green under a day, cyan under a week, gold under a month, red older. '
             'Each cell also says how many files are changed but not committed.</p><div class="wt">')
    for w in wts:
        a = w["age_days"]
        o.append('<div class="cell %s"><b>%s</b><i>%s · %s</i></div>'
                 % (age_class(a), e(w["name"]), "age unknown" if a is None else ("%.0f d" % a if a >= 1 else "today"),
                    ("%d uncommitted" % w["dirty_files"]) if w["dirty_files"] else "clean"))
    o.append('</div></section>')

    o.append('<section class="panel"><div class="section-label">§ Open loops, by how urgent</div><div class="tw" tabindex="0"><table><tr><th>Group</th><th>Count shown</th><th>First items</th></tr>')
    for s in loops:
        if s["items"]:
            o.append('<tr><td>%s</td><td class="mono">%d</td><td>%s</td></tr>'
                     % (e(s["title"]), len(s["items"]), "<br>".join(e(i["text"][:96]) + ' <span class="muted">(' + e(i["why"]) + ')</span>' for i in s["items"][:3])))
    o.append('</table></div></section>')

    tot = mem["files"] or 1
    cols = ["green", "cyan", "gold", "red"]
    o.append('<section class="panel"><div class="section-label">§ How fresh is what we know</div>'
             '<p class="muted">Memory notes by days since last edit. Old does not mean wrong. It means nobody has re-checked it, and the repo\'s own rule is to verify a recalled fact before relying on it.</p>'
             '<div class="bar" role="img" aria-label="Memory note age">')
    for (k, n), c in zip(mem["buckets"].items(), cols):
        o.append('<div style="background:var(--%s);width:%.1f%%" title="%s: %d"></div>' % (c, 100.0 * n / tot, e(k), n))
    o.append('</div><ul class="legend" style="margin-top:12px">')
    for (k, n), c in zip(mem["buckets"].items(), cols):
        o.append('<li><span class="sw" style="background:var(--%s)"></span><span>%s</span><b>%d</b></li>' % (c, e(k), n))
    o.append('</ul></section>')

    o.append('<section class="panel"><div class="section-label">§ Proposals under test</div><div class="tw" tabindex="0"><table>'
             '<tr><th>Date</th><th>Proposal</th><th>Decisions waiting</th><th>Controls tested</th></tr>')
    for p in props:
        o.append('<tr><td class="mono">%s</td><td><a href="%s.html">%s</a></td><td>%d</td><td>%d of %d</td></tr>'
                 % (e(p["date"]), e(p["stem"]), e(p["title"]), p["decisions"], p["tested"], p["controls"]))
    o.append('</table></div></section>')

    o.append('<section class="panel"><div class="section-label">§ Not measured yet</div><ul>'
             '<li><span class="pill red">UNBUILT</span> Internal versus external side: which rows and events came from inside the system and which from the world, and how often work crosses between them.</li>'
             '<li><span class="pill red">UNBUILT</span> Flow between states: how many rows move per week and which gates slow them. The backlog stores state, not transitions; git history of the file holds them.</li>'
             '<li><span class="pill red">UNBUILT</span> Which memory notes are re-verified versus merely old.</li></ul>'
             '<p class="muted">Each is read-only to compute. Proposed as the next step on the proposals page.</p></section>')
    machine = json.dumps(d, indent=1, ensure_ascii=False).replace("</", "<\\/")
    o.append('<footer>Generated by scripts/field_render.py · machine layer: JSON block id arcs-field</footer></main>')
    o.append('<script type="application/json" id="arcs-field">\n%s\n</script></body></html>' % machine)
    return "\n".join(o)


def self_test():
    fake = {"generated": "t", "worktrees": [{"name": "a", "branch": "b", "age_days": 0.2, "dirty_files": 3},
                                            {"name": "c", "branch": "d", "age_days": 40, "dirty_files": 0}],
            "backlog": {"OPEN": 2, "HELD": 1, "BLOCKED": 1, "DONE": 3}, "loops": [{"title": "Rotting", "items": [{"text": "x", "why": "y"}]}],
            "memory": {"files": 4, "buckets": {"under 7 days": 1, "7 to 30 days": 1, "30 to 90 days": 1, "over 90 days": 1}}, "proposals": []}
    page = render(fake)
    assert "stroke-dasharray" in page and "cell g" in page and "cell r" in page
    assert "—" not in page.replace(open(TOKENS, encoding="utf-8").read(), ""), "em-dash"
    assert json.loads(page.split('id="arcs-field">')[1].split("</script>")[0].replace("<\\/", "</"))["backlog"]["OPEN"] == 2
    assert age_class(0.5) == "g" and age_class(40) == "r" and age_class(None) == "y"
    print("self-test ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        self_test()
    else:
        d = build()
        dest = os.path.join(ROOT, "_PROPOSALS", "rendered", "field.html")
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        open(dest, "w", encoding="utf-8").write(render(d))
        print("wrote", os.path.relpath(dest, ROOT), "worktrees:", len(d["worktrees"]), "backlog rows:", sum(d["backlog"].values()))
