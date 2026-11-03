#!/usr/bin/env python3
"""proposal_render.py: render a _PROPOSALS/*.json proposal as a self-contained ARCS page.

One source, two parallel layers (a convenience beside the file, never a replacement for it):
  human    plain-language page assembled from the ui-kit (template recoil-report, mode operate)
  machine  the same facts as ids, enums and thresholds in <script type="application/json" id="arcs-proposal">

Tokens are inlined VERBATIM from src/ui-kit/recoil-report/_tokens.css (token_source_gate).
Heuristics are split on purpose: "for you" (the human reader) and "for the agent".

  python3 scripts/proposal_render.py _PROPOSALS/X.json            # writes _PROPOSALS/rendered/X.html
  python3 scripts/proposal_render.py --all                        # every _PROPOSALS/*.json with a "controls" key
  python3 scripts/proposal_render.py --self-test

Stdlib only.
"""
import argparse, glob, html, json, os, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TOKENS = os.path.join(ROOT, "src", "ui-kit", "recoil-report", "_tokens.css")
REQUIRED = ["id", "title", "date", "status", "one_line", "decisions", "controls", "heuristics"]

CSS = """
* { box-sizing: border-box; }
body { background: var(--bg); color: var(--text); font-family: var(--font-sans); font-size: 15px; line-height: 1.6; margin: 0; padding-inline: 16px; padding-block: 28px; }
main { max-width: 920px; margin: 0 auto; display: flex; flex-direction: column; gap: 28px; }
h1 { font-family: var(--font-display); font-size: clamp(1.5rem, 4vw, 2.2rem); font-weight: 600; line-height: 1.2; margin: 0 0 6px; text-wrap: balance; }
p { margin: 0 0 10px; }
.recoil-header { display: flex; align-items: stretch; background: var(--surface); border: 1px solid var(--border); border-radius: var(--r-lg); overflow: hidden; }
.recoil-header::before { content: ''; width: 4px; flex-shrink: 0; background: var(--gold); }
.header-arcs { padding: 16px 24px; border-right: 1px solid var(--border); display: flex; flex-direction: column; justify-content: center; }
.arcs-mark { font-family: var(--font-display); font-size: 28px; font-weight: 700; color: var(--cyan); line-height: 1; }
.arcs-sub { font-family: var(--font-mono); font-size: 10px; color: var(--muted); letter-spacing: .12em; text-transform: uppercase; margin-top: 6px; }
.header-center { flex: 1; min-width: 0; padding: 16px 24px; }
.receipt-id { font-family: var(--font-mono); font-size: 11px; color: var(--dimmed); letter-spacing: .04em; margin-bottom: 8px; overflow-wrap: anywhere; }
.y-gate-badge { display: inline-flex; background: var(--gold-bg); border: 1px solid var(--gold); color: var(--gold); border-radius: var(--r-sm); padding: 3px 12px; font-size: 11px; font-weight: 600; letter-spacing: .08em; }
.section-label { font-family: var(--font-mono); font-size: 11px; letter-spacing: .12em; text-transform: uppercase; color: var(--muted); margin-bottom: 12px; }
.panel { background: var(--surface); border: 1px solid var(--border); border-radius: var(--r-md); padding: 20px; }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 12px; }
.cell { background: var(--surface-2); border: 1px solid var(--border); border-radius: var(--r-sm); padding: 14px; min-width: 0; }
.cell b { display: block; font-family: var(--font-mono); font-size: 11px; letter-spacing: .08em; text-transform: uppercase; color: var(--cyan); margin-bottom: 6px; }
.decision { border-top: 1px solid var(--border); padding-block: 14px; }
.decision:first-of-type { border-top: 0; padding-top: 0; }
.decision .h3 { font-size: 1rem; margin: 0 0 4px; }
.decision .rec { color: var(--green); }
.decision .why, .muted { color: var(--dimmed); font-size: 13px; }
.did { font-family: var(--font-mono); font-size: 11px; color: var(--cyan); margin-right: 8px; }
.tw { overflow-x: auto; }
table { border-collapse: collapse; width: 100%; font-size: 13px; }
th, td { text-align: left; padding: 8px 10px; border-bottom: 1px solid var(--border); vertical-align: top; }
th { color: var(--muted); font-family: var(--font-mono); font-size: 11px; letter-spacing: .06em; text-transform: uppercase; font-weight: 500; }
td.mono { font-family: var(--font-mono); font-size: 12px; }
.pill { display: inline-block; padding: 1px 9px; border-radius: 99px; font-family: var(--font-mono); font-size: 11px; border: 1px solid; white-space: nowrap; }
.pill.green { color: var(--green); border-color: var(--green); background: var(--green-bg); }
.pill.gold { color: var(--gold); border-color: var(--gold); background: var(--gold-bg); }
.pill.red { color: var(--red); border-color: var(--red); background: var(--red-bg); }
.pill.cyan { color: var(--cyan); border-color: var(--cyan); background: var(--cyan-bg); }
.ctl { border-top: 1px solid var(--border); padding-block: 16px; }
.ctl:first-of-type { border-top: 0; padding-top: 0; }
.ctl .h3 { font-size: 1rem; margin: 0 0 6px; display: flex; gap: 10px; flex-wrap: wrap; align-items: baseline; }
.ab { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 10px; margin-top: 8px; }
.ab div { background: var(--surface-2); border-radius: var(--r-sm); padding: 10px 12px; font-size: 13px; min-width: 0; }
.ab .bad { border-left: 3px solid var(--red); }
.ab .good { border-left: 3px solid var(--green); }
.two { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 12px; }
.two ul { margin: 8px 0 0; padding-left: 18px; }
.two li { margin-bottom: 8px; }
blockquote { margin: 0; padding: 12px 16px; background: var(--surface-2); border: 1px solid var(--border); border-radius: var(--r-sm); font-size: 14px; }
a { color: var(--cyan); }
.prose h2 { font-size: 1.25rem; margin: 28px 0 8px; } .prose h3 { font-size: 1.05rem; margin: 22px 0 6px; } .prose h4 { font-size: .95rem; margin: 18px 0 6px; }
.prose ul, .prose ol { padding-left: 22px; margin: 0 0 12px; } .prose li { margin-bottom: 4px; }
.prose blockquote { margin: 12px 0; padding: 10px 14px; border-left: 3px solid var(--cyan); background: var(--surface-2); border-radius: var(--r-sm); }
.prose blockquote p { margin: 0; }
.prose pre { background: var(--surface-2); border: 1px solid var(--border); border-radius: var(--r-sm); padding: 12px; overflow-x: auto; font-size: 12px; line-height: 1.45; }
.prose pre code { color: var(--text); white-space: pre; } .prose hr { border: 0; border-top: 1px solid var(--border); margin: 24px 0; } .prose del { color: var(--dimmed); }
.fm { width: auto; } .fm td:first-child { font-family: var(--font-mono); font-size: 12px; color: var(--muted); white-space: nowrap; }
code { font-family: var(--font-mono); font-size: 12px; color: var(--cyan); overflow-wrap: anywhere; }
.toc { display: flex; flex-wrap: wrap; gap: 6px 16px; position: sticky; top: 0; background: var(--bg); padding-block: 8px; z-index: 1; border-bottom: 1px solid var(--border); }
.toc .section-label { margin: 0; align-self: center; }
.toc a { color: var(--cyan); font-size: 13px; text-decoration: none; padding: 10px 4px; display: inline-block; }
section { scroll-margin-top: 120px; }
h2.h3 { font-family: var(--font-sans); }
details > summary { cursor: pointer; list-style: none; }
dl { margin: 0; display: grid; grid-template-columns: minmax(120px, 220px) 1fr; gap: 8px 16px; }
dt { font-weight: 600; } dd { margin: 0; color: var(--dimmed); }
@media (max-width: 640px) { .toc { position: static; } dl { grid-template-columns: 1fr; } }
footer { font-family: var(--font-mono); font-size: 11px; color: var(--muted); }
@media (max-width: 640px) { .recoil-header { flex-direction: column; } .header-arcs { border-right: 0; border-bottom: 1px solid var(--border); } }
"""


def e(x):
    return html.escape(str(x), quote=True)


def stage_class(stage):
    s = stage.lower()
    if "scored" in s or "adopted" in s:
        return "green"
    if "untested" in s or "fail" in s:
        return "red"
    return "gold"


def verdict_class(v):
    v = v.lower()
    return "green" if v.startswith("clean") else ("gold" if v.startswith(("low", "expected")) else "red")


def action_class(a):
    return "green" if a.startswith("keep") else "red"


TOC = [("short", "Short version"), ("decisions", "Decisions"), ("heuristics", "Heuristics"), ("fields", "Fields"),
       ("leaks", "Leak check"), ("controls", "Controls"), ("terms", "Terms"), ("glossary", "Glossary"), ("files", "Files")]


def render(p):
    miss = [k for k in REQUIRED if k not in p]
    if miss:
        raise ValueError("proposal missing keys: " + ", ".join(miss))
    tokens = open(TOKENS, encoding="utf-8").read()
    o = []
    a = o.append
    a('<!doctype html><html lang="en"><head>')
    a('<!-- @arcs-template: recoil-report -->\n<!-- @arcs-mode: operate -->')
    a('<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">')
    a('<title>%s</title>' % e(p["title"]))
    a('<style>\n' + tokens + '\n' + CSS + '</style></head><body>')
    a('<main>')
    a('<div class="recoil-header"><div class="header-arcs"><div class="arcs-mark">ARCS</div><div class="arcs-sub">Proposal</div></div>'
      '<div class="header-center"><div class="receipt-id">%s · %s · %s</div><h1>%s</h1><p>%s</p>'
      '<span class="y-gate-badge">%s · nothing in production has changed</span></div></div>'
      % (e(p["id"]), e(p["date"]), e(p.get("base", "")), e(p["title"]), e(p["one_line"]), e(p["status"])))

    a('<nav class="toc" aria-label="Contents"><div class="section-label">Contents</div>' + ''.join('<a href="#%s">%s</a>' % (i, e(t)) for i, t in (TOC[:3] + [(t['id'], t['title'][:28]) for t in p.get('tables', [])] + TOC[3:])) + '</nav>')
    if p.get("bottom_line"):
        a('<section id="short"><div class="section-label">§ The short version</div><div class="grid">')
        for b in p["bottom_line"]:
            a('<div class="cell"><b>%s</b>%s</div>' % (e(b["label"]), e(b["text"])))
        a('</div></section>')

    ruled = all(d.get("ruling") for d in p["decisions"])
    a('<section class="panel" id="decisions"><div class="section-label">§ %s</div>' % ("Decisions, ruled" if ruled else "Decisions waiting on you"))
    for d in p["decisions"]:
        ruling = '<p class="rec">Ruled: %s</p>' % e(d["ruling"]) if d.get("ruling") else ""
        a('<div class="decision"><h2 class="h3"><span class="did">%s</span>%s</h2><p class="rec">Recommended: %s</p>%s<p class="why">%s</p></div>'
          % (e(d["id"]), e(d["question"]), e(d["recommended"]), ruling, e(d.get("why", ""))))
    a('</section>')

    a('<section class="panel" id="heuristics"><div class="section-label">§ Heuristics: for you, and for me</div><div class="two">')
    a('<div class="cell"><b>For you (human)</b><ul>' + ''.join('<li>%s</li>' % e(h) for h in p["heuristics"]["human"]) + '</ul></div>')
    a('<div class="cell"><b>For the agent (machine)</b><ul>' + ''.join('<li>%s</li>' % e(h) for h in p["heuristics"]["agent"]) + '</ul></div>')
    a('</div></section>')

    if p.get("fields"):
        a('<section class="panel" id="fields"><details open><summary class="section-label">§ What the answer call returns today (%d fields)</summary>' % len(p["fields"]) + ' returns today</div><div class="tw" tabindex="0"><table>'
          '<tr><th>Field</th><th>Who reads it</th><th>Proposal</th></tr>')
        for f in p["fields"]:
            a('<tr><td class="mono">%s</td><td>%s</td><td><span class="pill %s">%s</span></td></tr>'
              % (e(f["field"]), e(f["read_by"]), action_class(f["action"]), e(f["action"])))
        a('</table></div></details></section>')

    if p.get("leaks"):
        a('<section class="panel" id="leaks"><div class="section-label">§ What a browser can download</div><div class="tw" tabindex="0"><table>'
          '<tr><th>Looked for</th><th>Hits</th><th>Result</th></tr>')
        for l in p["leaks"]:
            a('<tr><td class="mono">%s</td><td>%s</td><td><span class="pill %s">%s</span></td></tr>'
              % (e(l["marker"]), e(l["browser_hits"]), verdict_class(l["verdict"]), e(l["verdict"])))
        a('</table></div>')
        a('<ul class="muted">' + ''.join('<li>%s</li>' % e(n) for n in p.get("leak_notes", [])) + '</ul></section>')

    for t in p.get("tables", []):
        a('<section class="panel" id="%s"><div class="section-label">§ %s</div>' % (e(t["id"]), e(t["title"])))
        if t.get("intro"):
            a('<p class="muted">%s</p>' % e(t["intro"]))
        a('<div class="tw" tabindex="0"><table><tr>' + ''.join('<th>%s</th>' % e(c) for c in t["columns"]) + '</tr>')
        for r in t["rows"]:
            cells = []
            for x in r:
                x = str(x)
                if x in ("MECHANISM", "METAPHOR", "UNBUILT", "MECHANISM (repo-level)"):
                    cells.append('<td><span class="pill %s">%s</span></td>' % ("green" if x.startswith("MECH") else ("red" if x == "UNBUILT" else "gold"), e(x)))
                else:
                    cells.append('<td>%s</td>' % e(x))
            a('<tr>' + ''.join(cells) + '</tr>')
        a('</table></div></section>')

    a('<section class="panel" id="controls"><div class="section-label">§ Proposed controls and how we will know each works</div>')
    a('<p class="muted">Each control is a guess until its test runs. A test has a known-bad case that must fail and a known-good case that must pass.</p>')
    for c in p["controls"]:
        a('<div class="ctl"><h2 class="h3"><span class="did">%s</span>%s <span class="pill %s">%s</span></h2><p>%s</p>'
          '<div class="ab"><div class="bad"><b class="muted">Must fail</b><br>%s</div><div class="good"><b class="muted">Must pass</b><br>%s</div></div>'
          '<p class="muted" style="margin-top:8px">Test status: %s%s</p></div>'
          % (e(c["id"]), e(c["name"]), stage_class(c["stage"]), e(c["stage"]), e(c["plain"]), e(c["bad"]), e(c["good"]),
             e(c.get("assay_ready", "")), (" · line: " + e(c["threshold"])) if c.get("threshold") else ""))
    a('</section>')

    if p.get("terms_text"):
        a('<section class="panel" id="terms"><div class="section-label">§ Suggested terms text (for counsel)</div><blockquote>%s</blockquote></section>' % e(p["terms_text"]))

    if p.get("glossary"):
        a('<section class="panel" id="glossary"><div class="section-label">§ Glossary</div><dl>' + ''.join('<dt>%s</dt><dd>%s</dd>' % (e(x["term"]), e(x["plain"])) for x in p["glossary"]) + '</dl></section>')
    a('<section class="panel" id="files"><div class="section-label">§ Every file this rests on</div><ul>' + ''.join('<li><code>%s</code></li>' % e(s) for s in p.get("sources", [])) + '<li><code>_PROPOSALS/%s.json</code> (source of this page)</li></ul></section>' % e(p.get("_stem", p["id"])))
    machine = json.dumps(p, indent=1, ensure_ascii=False).replace("</", "<\\/")
    a('<footer>Source: _PROPOSALS/%s.json · sources: %s · the machine layer is the JSON block in this page (id arcs-proposal)</footer>'
      % (e(p.get("_stem", p["id"])), e(", ".join(p.get("sources", [])))))
    a('</main>')
    a('<script type="application/json" id="arcs-proposal">\n%s\n</script></body></html>' % machine)
    return "\n".join(o)


def out_path(src):
    d = os.path.join(os.path.dirname(os.path.abspath(src)), "rendered")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, os.path.splitext(os.path.basename(src))[0] + ".html")


def run(src):
    p = json.load(open(src, encoding="utf-8"))
    p["_stem"] = os.path.splitext(os.path.basename(src))[0]
    out = render(p)
    dest = out_path(src)
    open(dest, "w", encoding="utf-8").write(out)
    print("wrote", os.path.relpath(dest, ROOT))
    return dest


def gather_legacy(files):
    """Group older .md/.html proposals by stem. Pure: reads files, returns rows."""
    import re
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import md_page
    groups = {}
    for f in files:
        stem, ext = os.path.splitext(f)
        groups.setdefault(stem, {})[ext[1:]] = os.path.join(ROOT, "_PROPOSALS", f)
    rows = []
    for stem in sorted(groups):
        g = groups[stem]
        fm, body, title, status = {}, "", stem[11:].replace("-", " "), ""
        if "md" in g:
            fm, body = md_page.split_front_matter(open(g["md"], encoding="utf-8").read())
            m = re.search(r"^#\s+(.*)$", body, re.M)
            if m:
                title = re.sub(r"^Proposal:\s*", "", m.group(1).strip())
                body = body.replace(m.group(0), "", 1)
            status = fm.get("status", "")
            if not status:
                m = re.search(r"\*\*Status:\*\*\s*(.+)", body)
                status = m.group(1).strip() if m else ""
        rows.append({"stem": stem, "date": stem[:10], "title": title, "status": status or "no status line",
                     "kind": "Essay draft (Lore series)" if "lore" in stem else "Proposal draft",
                     "md": g.get("md"), "html": g.get("html"), "fm": fm, "body": body})
    return rows


def write_legacy_pages(rows):
    import shutil
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import md_page
    tokens = open(TOKENS, encoding="utf-8").read()
    d = os.path.join(ROOT, "_PROPOSALS", "rendered")
    os.makedirs(d, exist_ok=True)
    for r in rows:
        if r["html"]:
            shutil.copyfile(r["html"], os.path.join(d, r["stem"] + ".html"))
        if not r["md"]:
            continue
        fmrows = "".join("<tr><td>%s</td><td>%s</td></tr>" % (e(k), e(v)) for k, v in r["fm"].items())
        page = ('<!doctype html><html lang="en"><head><!-- @arcs-template: recoil-report -->\n<!-- @arcs-mode: operate -->\n<meta charset="utf-8">'
                '<meta name="viewport" content="width=device-width,initial-scale=1"><title>%s</title><style>\n%s\n%s</style></head><body><main>'
                '<div class="recoil-header"><div class="header-arcs"><div class="arcs-mark">ARCS</div><div class="arcs-sub">Older proposal</div></div>'
                '<div class="header-center"><div class="receipt-id">%s · source %s · shown as written, not ranked</div><h1>%s</h1>'
                '<span class="y-gate-badge">%s</span></div></div>'
                '<p><a href="index.html">Back to the proposal wiki</a></p>%s'
                '<section class="panel prose"><div class="section-label">§ The document</div>%s</section>'
                '<footer>Rendered from _PROPOSALS/%s by scripts/md_page.py. Text is escaped, never executed.</footer></main></body></html>'
                % (e(r["title"]), tokens, CSS, e(r["date"]), e(os.path.basename(r["md"])), e(r["title"]), e(r["status"][:140]),
                   ('<section class="panel"><div class="section-label">§ Front matter</div><div class="tw" tabindex="0"><table class="fm">%s</table></div></section>' % fmrows) if fmrows else "",
                   md_page.md_to_html(r["body"]), e(os.path.basename(r["md"]))))
        open(os.path.join(d, "legacy-" + r["stem"] + ".html"), "w", encoding="utf-8").write(page)


def render_index(items):
    import datetime as dt
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import proposal_rank as pr
    props, edges, legacy = pr.load()
    rk = pr.rank(props, edges, dt.date.today())
    tokens = open(TOKENS, encoding="utf-8").read()
    rows, nested = [], []
    for r in rk["rows"]:
        sc = r["scores"]
        rows.append('<tr data-id="%s" %s><td class="mono">%s</td><td><a href="%s.html">%s</a></td>%s<td class="mono">%s</td><td>%d</td></tr>'
                    % (e(r["id"]), " ".join('data-%s="%s"' % (a_, "" if sc[a_] is None else sc[a_]) for a_ in pr.AXES), e(r["date"]), e(r["stem"]), e(r["title"]),
                       "".join("<td>%s</td>" % ("?" if sc[a_] is None else sc[a_]) for a_ in pr.AXES), e(r["cell"]), r["downstream_decisions"]))
        lis = []
        for i in r["issues"]:
            dep = ""
            if i["waits_on"]:
                dep = ' <span class="pill red">waits on %s</span>' % e(", ".join(x.split("#")[0][-14:] + "#" + x.split("#")[1] for x in i["waits_on"]))
            if i["blocks"]:
                dep += ' <span class="pill gold">holds up %d</span>' % len(i["blocks"])
            lis.append("<li><span class=\"did\">%s</span>%s%s</li>" % (e(i["id"].split("#")[1]), e(i["question"]), dep))
        nested.append('<details><summary>%s: %d decisions</summary><ul>%s</ul></details>' % (e(r["title"]), len(r["issues"]), "".join(lis)))
    probs = "".join("<li>%s</li>" % e(x) for x in rk["problems"]) or "<li>none</li>"
    legrows = ""
    for r in gather_legacy(legacy):
        links = []
        if r["md"]:
            links.append('<a href="legacy-%s.html">Text</a>' % e(r["stem"]))
        if r["html"]:
            links.append('<a href="%s.html">Original page</a>' % e(r["stem"]))
        legrows += ('<tr><td class="mono">%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>'
                    % (e(r["date"]), e(r["title"]), e(r["kind"]), e(r["status"][:110]), " · ".join(links)))
    dial = "".join('<label>%s <span class="muted">(%s)</span><input type="range" min="0" max="3" value="1" id="w-%s">'
                   '<span class="muted">0 = %s<br>%s = %s</span></label>'
                   % (a_, e(pr.BASIS[a_]), a_, e(pr.ANCHORS[a_][0]), next(d["scale_max"] for d in pr.RUBRIC["dims"] if d["key"] == a_), e(pr.ANCHORS[a_][1])) for a_ in pr.AXES)
    js = ("<script>(function(){var A=%s;var tb=document.getElementById('rk');function go(){var w={};A.forEach(function(a){w[a]=+document.getElementById('w-'+a).value});"
          "var rs=[].slice.call(tb.querySelectorAll('tr[data-id]'));rs.forEach(function(r){var t=0;A.forEach(function(a){var v=r.getAttribute('data-'+a);if(v!=='')t+=w[a]*v});r._t=t;r.querySelector('.tot').textContent=t});"
          "rs.sort(function(x,y){return y._t-x._t});rs.forEach(function(r){tb.appendChild(r)})}A.forEach(function(a){document.getElementById('w-'+a).addEventListener('input',go)});go()})()</script>"
          % json.dumps(pr.AXES))
    return ('<!doctype html><html lang="en"><head><!-- @arcs-template: recoil-report -->\n<!-- @arcs-mode: operate -->\n<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>Proposal Wiki</title><style>\n' + tokens + '\n' + CSS + '\nlabel { display: grid; gap: 4px; font-size: 13px; } input[type=range] { width: 100%; } .dial { display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 12px; } details { margin-bottom: 8px; } summary { cursor: pointer; }</style></head><body><main>'
            '<div class="recoil-header"><div class="header-arcs"><div class="arcs-mark">ARCS</div><div class="arcs-sub">Proposals</div></div>'
            '<div class="header-center"><h1>Proposal wiki</h1><p>Ranked on five axes, nested down to the decisions that block each other. Rebuilt from the files each time, so running it twice changes nothing.</p></div></div>'
            '<section class="panel"><div class="section-label">§ Field view</div><p><a href="field.html">The whole mountain at a glance</a>: worktrees, backlog circuit, open loops, how fresh our knowledge is.</p></section>'
            '<section class="panel"><div class="section-label">§ You set the frame</div><p class="muted">Rank depends on who is looking and why. Weight each axis 0 to 3. '
            'Axes with no score yet (shown ?) count as zero. The starting weights are all 1 and are an assumption, not a finding. The anchors under each dial are a draft awaiting your approval (status: ' + e(pr.RUBRIC['anchors_status']) + ').</p><div class="dial">' + dial + '</div></section>'
            '<section class="panel"><div class="section-label">§ Every proposal, ranked</div><div class="tw" tabindex="0"><table><thead><tr><th>Date</th><th>Page</th><th>recency</th><th>ripple</th><th>coherence</th><th>potency</th><th>relevancy</th><th>cell (5^5)</th><th>holds up</th><th>score</th></tr></thead><tbody id="rk">'
            + "".join(x.replace("</tr>", '<td class="tot mono"></td></tr>') for x in rows) + '</tbody></table></div>'
            '<p class="muted">recency and ripple are measured. coherence is a proxy: the share of controls that name both a failing and a passing case. '
            'potency and relevancy need a human score in _PROPOSALS/edges.json and stay ? until then. Ripple counts only edges someone wrote down, so it undercounts.</p></section>'
            '<section class="panel"><div class="section-label">§ Nested decisions and what blocks what</div>' + "".join(nested) + '</section>'
            '<section class="panel"><div class="section-label">§ Older proposals, shown as written</div><div class="tw" tabindex="0"><table>'
            '<tr><th>Date</th><th>Title</th><th>Kind</th><th>Status as written</th><th>Open</th></tr>' + legrows + '</table></div>'
            '<p class="muted">Not yet ranked: converting each into the JSON form needs a read and a judgment, so they are listed with their own status line, not scored. Private pages: personal drafts, do not share the link.</p></section>'
            '<section class="panel"><div class="section-label">§ Edge problems</div><ul>' + probs + '</ul></section>'
            '</main>' + js + '<script type="application/json" id="arcs-rank">' + json.dumps(rk, ensure_ascii=False).replace("</", "<\\/") + '</script></body></html>')


def self_test():
    good = json.load(open(os.path.join(ROOT, "_PROPOSALS", "2026-10-15-compass-exposure-audit.json"), encoding="utf-8"))
    page = render(good)
    assert "/* ARCS Recoil Report" in page, "tokens must be inlined verbatim"
    assert ".recoil-header" in page and ".section-label" in page
    assert "—" not in page.replace(open(TOKENS, encoding="utf-8").read(), ""), "em-dash found (outside the verbatim tokens)"
    blob = page.split('id="arcs-proposal">')[1].split("</script>")[0]
    assert json.loads(blob.replace("<\\/", "</"))["id"] == good["id"], "machine layer must round-trip"
    bad = dict(good)
    del bad["controls"]
    try:
        render(bad)
    except ValueError:
        pass
    else:
        raise AssertionError("known-bad (missing controls) must fail")
    print("self-test ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("src", nargs="?")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a_ = ap.parse_args()
    if a_.self_test:
        self_test()
    elif a_.all:
        items = []
        for f in sorted(glob.glob(os.path.join(ROOT, "_PROPOSALS", "*.json"))):
            d = json.load(open(f, encoding="utf-8"))
            if "controls" in d:
                run(f)
                d["_stem"] = os.path.splitext(os.path.basename(f))[0]
                items.append(d)
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import proposal_rank as _pr
        write_legacy_pages(gather_legacy(_pr.load()[2]))
        if items:
            dest = os.path.join(ROOT, "_PROPOSALS", "rendered", "index.html")
            open(dest, "w", encoding="utf-8").write(render_index(items))
            print("wrote", os.path.relpath(dest, ROOT))
    elif a_.src:
        run(a_.src)
    else:
        ap.print_help()
        sys.exit(2)
