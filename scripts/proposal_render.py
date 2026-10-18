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

    a('<section class="panel" id="decisions"><div class="section-label">§ Decisions waiting on you</div>')
    for d in p["decisions"]:
        a('<div class="decision"><h2 class="h3"><span class="did">%s</span>%s</h2><p class="rec">Recommended: %s</p><p class="why">%s</p></div>'
          % (e(d["id"]), e(d["question"]), e(d["recommended"]), e(d.get("why", ""))))
    a('</section>')

    a('<section class="panel" id="heuristics"><div class="section-label">§ Heuristics: for you, and for me</div><div class="two">')
    a('<div class="cell"><b>For you (human)</b><ul>' + ''.join('<li>%s</li>' % e(h) for h in p["heuristics"]["human"]) + '</ul></div>')
    a('<div class="cell"><b>For the agent (machine)</b><ul>' + ''.join('<li>%s</li>' % e(h) for h in p["heuristics"]["agent"]) + '</ul></div>')
    a('</div></section>')

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
    a('<section class="panel" id="files"><div class="section-label">§ Every file this rests on</div><ul>' + ''.join('<li><code>%s</code></li>' % e(s) for s in p.get("sources", [])) + '<li><code>_PROPOSALS/%s.json</code> (source of this page)</li></ul></section>' % e(p["id"]))
    machine = json.dumps(p, indent=1, ensure_ascii=False).replace("</", "<\\/")
    a('<footer>Source: _PROPOSALS/%s.json · sources: %s · the machine layer is the JSON block in this page (id arcs-proposal)</footer>'
      % (e(p["id"]), e(", ".join(p.get("sources", [])))))
    a('</main>')
    a('<script type="application/json" id="arcs-proposal">\n%s\n</script></body></html>' % machine)
    return "\n".join(o)


def out_path(src):
    d = os.path.join(os.path.dirname(os.path.abspath(src)), "rendered")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, os.path.splitext(os.path.basename(src))[0] + ".html")


def run(src):
    p = json.load(open(src, encoding="utf-8"))
    out = render(p)
    dest = out_path(src)
    open(dest, "w", encoding="utf-8").write(out)
    print("wrote", os.path.relpath(dest, ROOT))
    return dest


def render_index(items):
    tokens = open(TOKENS, encoding="utf-8").read()
    rows = []
    for it in items:
        done = sum(1 for c in it["controls"] if "scored" in c["stage"] or "adopted" in c["stage"])
        rows.append('<tr><td class="mono">%s</td><td><a href="%s.html">%s</a></td><td><span class="pill gold">%s</span></td>'
                    '<td>%d</td><td>%d of %d</td><td>%s</td></tr>' % (e(it["date"]), e(it["_stem"]), e(it["title"]), e(it["status"]),
                    len(it["decisions"]), done, len(it["controls"]), e(it["one_line"])))
    return ('<!doctype html><html lang="en"><head><!-- @arcs-template: recoil-report -->\n<!-- @arcs-mode: operate -->\n<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>Proposal Wiki</title><style>\n' + tokens + '\n' + CSS + '</style></head><body><main>'
            '<div class="recoil-header"><div class="header-arcs"><div class="arcs-mark">ARCS</div><div class="arcs-sub">Proposals</div></div>'
            '<div class="header-center"><h1>Proposal wiki</h1><p>Every proposal in this worktree, with how many decisions wait on you and how many controls have been tested.</p></div></div>'
            '<section class="panel"><div class="section-label">§ Every proposal</div><div class="tw" tabindex="0"><table><tr><th>Date</th><th>Page</th><th>Status</th><th>Decisions</th><th>Controls tested</th><th>In one line</th></tr>'
            + ''.join(rows) + '</table></div></section></main></body></html>')


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
        if items:
            dest = os.path.join(ROOT, "_PROPOSALS", "rendered", "index.html")
            open(dest, "w", encoding="utf-8").write(render_index(items))
            print("wrote", os.path.relpath(dest, ROOT))
    elif a_.src:
        run(a_.src)
    else:
        ap.print_help()
        sys.exit(2)
