"""tabbed_brief_build: render a tabbed counterpart brief from the tabbed-brief template plus a data file.
The page is generated from four parts and never hand-edited:
  tokens    src/ui-kit/recoil-report/_tokens.css, inlined verbatim (sentinel line kept)
  kit       the @prim blocks of the parts the page uses, copied verbatim from src/ui-kit/recoil-report/NN-*.html
            (27 section-label, 28 chip, 29 tile, 31 callout, 38 wordmark, 39 theme light remap, 42 shell-nav, 51 display-preferences, 52 plan-matrix, 53 cold-read)
  template  src/ui-kit/tabbed-brief/shell.css + shell.js (frame and page organisms, no counterpart content)
  data      a JSON file valid against src/ui-kit/tabbed-brief/brief.schema.json (all copy; links as [text](url), bold as **text**)
  python3 scripts/tabbed_brief_build.py DATA.json -o OUT.html            write the full page (doctype, analytics if the data asks)
  python3 scripts/tabbed_brief_build.py DATA.json --artifact OUT.html    write the Artifact body (no doctype, no analytics)
  python3 scripts/tabbed_brief_build.py --check                          exit 1 if a registered page differs from its data
  python3 scripts/tabbed_brief_build.py --self-test                      prove the validator rejects each bad shape
Stdlib only.
"""
import argparse, copy, html, json, os, re, sys, tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KIT = os.path.join(ROOT, "src/ui-kit/recoil-report")
TDIR = os.path.join(ROOT, "src/ui-kit/tabbed-brief")
SCHEMA = os.path.join(TDIR, "brief.schema.json")
PARTS = ["27-section-label", "28-chip", "29-tile", "31-callout", "38-wordmark", "39-theme-toggle", "42-shell-nav", "51-display-preferences", "52-plan-matrix", "53-cold-read"]
REGISTERED = {"_ARTIFACTS/tabbed-brief/gravity.json": "public/gravity-brief.html"}
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import precall_brief_build as pb  # the stdlib JSON Schema subset lives there; reuse it, do not fork it


def e(s):
    return html.escape(str(s), quote=True)


def md(s):
    """Escape, then allow two inline marks only: [text](https://...) and **bold**."""
    t = e(s)
    t = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", lambda m: '<a href="%s">%s</a>' % (m.group(2), m.group(1)), t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    return t


def kit_block(name):
    src = open(os.path.join(KIT, name + ".html"), encoding="utf-8").read()
    m = re.search(r"(/\* @prim:begin %s \*/\n.*?/\* @prim:end %s \*/\n)" % (re.escape(name), re.escape(name)), src, re.S)
    if not m:
        raise SystemExit("kit part %s has no @prim block" % name)
    return m.group(1)


def tokens():
    t = open(os.path.join(KIT, "_tokens.css"), encoding="utf-8").read()
    assert t.startswith("/* ARCS Recoil Report"), "token sentinel missing"
    return t


def shnav_js():
    spec = json.load(open(os.path.join(ROOT, "src/ui-kit/specimens/shell-nav.json"), encoding="utf-8"))
    return spec["tail_js"]


# ---------- validation ----------
def validate(d):
    schema = json.load(open(SCHEMA, encoding="utf-8"))
    errs = pb._errs(d, schema, schema, "$")
    n = len(d.get("horizons", []))
    ids = [t.get("id") for t in d.get("tabs", [])]
    if len(set(ids)) != len(ids):
        errs.append("$.tabs: tab ids must be unique")
    secs = [s.get("id") for s in d.get("overview", {}).get("sections", [])] + ([d["overview"]["coldread"]["id"]] if d.get("overview", {}).get("coldread") else [])

    def blocks(where, bl):
        for i, b in enumerate(bl):
            if b.get("type") == "plan":
                for j, r in enumerate(b.get("rows", [])):
                    if len(r) != n + 1:
                        errs.append("%s[%d].rows[%d]: needs the duty plus %d horizon cells" % (where, i, j, n))
                if len(b.get("know", [])) != n:
                    errs.append("%s[%d].know: needs %d entries, one per horizon" % (where, i, n))
            if b.get("type") == "table":
                w = len(b.get("head", []))
                for j, r in enumerate(b.get("rows", [])):
                    if len(r) != w:
                        errs.append("%s[%d].rows[%d]: %d cells for %d columns" % (where, i, j, len(r), w))
    for k, s in enumerate(d.get("overview", {}).get("sections", [])):
        blocks("$.overview.sections[%d].blocks" % k, s.get("blocks", []))
    for k, t in enumerate(d.get("tabs", [])):
        for u, un in enumerate(t.get("units", [])):
            blocks("$.tabs[%d].units[%d].blocks" % (k, u), un.get("blocks", []))
    for a in d.get("overview", {}).get("actions", []):
        if "tab" in a and a["tab"] not in ids:
            errs.append("$.overview.actions: tab %r does not exist" % a["tab"])
        if "section" in a and a["section"] not in secs:
            errs.append("$.overview.actions: section %r does not exist" % a["section"])
    if "—" in json.dumps(d, ensure_ascii=False):
        errs.append("$: em-dash found; use a comma, colon or period")
    return errs


# ---------- organisms ----------
TABLE_N = [0]  # each scroll region gets its own name (axe landmark-unique)


def r_table(b):
    TABLE_N[0] += 1
    head = "".join("<th>%s</th>" % md(h) for h in b["head"])
    rows = "".join("<tr>%s</tr>" % "".join(('<td data-label="%s">%s</td>' % (e(b["head"][i]), md(c))) if i else "<td>%s</td>" % md(c) for i, c in enumerate(r)) for r in b["rows"])
    return '<div class="tb-scroll" tabindex="0" role="region" aria-label="Table %d: %s"><table class="tb-table"><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (
        TABLE_N[0], e(", ".join(b["head"])), head, rows)


def r_plan(b, horizons):
    hs = "".join("<th>By day %d</th>" % h for h in horizons)
    rows = ""
    for r in b["rows"]:
        cells = "<td>%s</td>" % md(r[0]) + "".join('<td data-label="By day %d">%s</td>' % (horizons[i], md(c)) for i, c in enumerate(r[1:]))
        rows += "<tr>%s</tr>" % cells
    know = "".join('<div class="pm-k"><p class="pm-kl">Day %d</p><p>%s</p></div>' % (horizons[i], md(k)) for i, k in enumerate(b["know"]))
    note = '<p class="pm-note">%s</p>' % md(b["note"]) if b.get("note") else ""
    return ('<div class="pm"><p class="pm-src">%s</p>%s<table class="pm-table"><thead><tr><th>Your page asks me to</th>%s</tr></thead>'
            '<tbody>%s</tbody></table><p class="pm-khead">How you would know it is working</p><div class="pm-know">%s</div></div>') % (md(b["source"]), note, hs, rows, know)


def r_cards(b, hlevel):
    out = []
    for c in b["cards"]:
        ref = '<p class="tb-card-ref">%s</p>' % md(c["ref"]) if c.get("ref") else ""
        out.append('<div class="tb-card"><h%d class="tb-card-t">%s</h%d>%s<p>%s</p></div>' % (hlevel, md(c["title"]), hlevel, ref, md(c["text"])))
    return '<div class="tb-cards">%s</div>' % "".join(out)


def r_blocks(bl, horizons, hlevel):
    out = []
    for b in bl:
        t = b["type"]
        if t == "p":
            out.append('<p class="tb-p">%s</p>' % md(b["text"]))
        elif t == "table":
            out.append(r_table(b))
        elif t == "plan":
            out.append(r_plan(b, horizons))
        elif t == "cards":
            out.append(r_cards(b, hlevel))
        elif t == "coldread":
            slots = "".join('<dt class="section-label">%s</dt><dd>%s</dd>' % (md(k), md(v)) for k, v in b["slots"])
            how = "".join('<li class="cr-step"><p class="section-label">%s</p><p class="cr-when">%s</p><p class="cr-what">%s</p></li>' % (md(a), md(w), md(x)) for a, w, x in b.get("how", []))
            how = '<div class="cr-howwrap"><p class="section-label" id="cr-how-l">How</p><ol class="cr-how" aria-labelledby="cr-how-l">%s</ol></div>' % how if how else ""
            read = '<p class="callout cr-read"><b>How to read</b>%s</p>' % md(b["read"]) if b.get("read") else ""
            out.append('<div class="cr"><dl class="cr-slots">%s</dl>%s%s</div>' % (slots, how, read))
        elif t == "list":
            tag = "ol" if b.get("ordered") else "ul"
            out.append('<%s class="tb-list">%s</%s>' % (tag, "".join("<li>%s</li>" % md(i) for i in b["items"]), tag))
    return "\n".join(out)


def r_fold(s, horizons):
    sid = s["id"]
    op = "true" if s.get("open") else "false"
    hid = "" if s.get("open") else " hidden"
    return ('<section class="tb-fold" id="%s"><h2 class="tb-h2"><button type="button" class="tb-fold-btn" aria-expanded="%s" aria-controls="%s-body">'
            '<span><span class="tb-fold-t">%s</span><span class="tb-tag">%s</span></span></button></h2>'
            '<div class="tb-fold-body" id="%s-body"%s>%s</div></section>') % (sid, op, sid, md(s["title"]), md(s["tagline"]), sid, hid, r_blocks(s["blocks"], horizons, 3))


def r_overview(d):
    o = d["overview"]
    h = "".join('<span class="hl">%s</span>' % md(re.sub(r"(?<=[a-z])-(?=[a-z])", "‑", x)) for x in o["headline"])
    acts = []
    for a in o["actions"]:
        cls = "tb-btn primary" if a.get("primary") else "tb-btn"
        if "tab" in a:
            acts.append('<a class="%s" href="#%s" data-go-tab="%s">%s</a>' % (cls, a["tab"], a["tab"], md(a["label"])))
        else:
            acts.append('<a class="%s" href="#%s" data-go-section="%s">%s</a>' % (cls, a["section"], a["section"], md(a["label"])))
    tiles = "".join('<div class="tile" role="listitem"><div class="v">%s</div><div class="k">%s</div><p class="tb-tile-note">%s</p></div>' % (md(t["v"]), md(t["k"]), md(t["note"])) for t in o["tiles"])
    folds = "\n".join(r_fold(s, d["horizons"]) for s in o["sections"])
    cr = ""
    if o.get("coldread"):
        c = o["coldread"]
        cr = '<section class="tb-coldread" id="%s" aria-labelledby="%s-h"><h2 class="tb-h2" id="%s-h">%s</h2>%s</section>\n' % (c["id"], c["id"], c["id"], md(c["title"]), r_blocks([c["block"]], d["horizons"], 3))
    return ('<div id="pane-ov" class="tb-pane" role="tabpanel" aria-labelledby="t-ov">\n<h1 class="tb-h1">%s</h1>\n%s<p class="tb-lede">%s</p>\n'
            '<div class="tb-go"><p class="tb-go-h">%s</p><p class="tb-go-t">%s</p>\n<div class="tb-actions">%s%s</div></div>\n'
            '%s<div class="tiles" role="list" aria-label="At a glance">%s</div>\n<div class="tb-expand"><button type="button" class="tb-btn" id="tb-expand" aria-pressed="false">Expand all</button></div>\n'
            '<div class="tb-folds">%s</div>\n</div>') % (h, ('<h2 class="tb-sub">%s</h2>\n' % md(o["subhead"])) if o.get("subhead") else "", md(o["lede"]), md(o["next_step"]["lead"]),
         md(o["next_step"]["text"]), "".join(acts), ('<p class="tb-note">%s</p>' % md(o["action_note"])) if o.get("action_note") else "", cr, tiles, folds)


def r_tab(t, horizons, i):
    tid = t["id"]
    units = "\n".join('<section class="unit"><h3 class="tb-h3">%s</h3>%s</section>' % (md(u["title"]), r_blocks(u["blocks"], horizons, 4)) for u in t["units"])
    calls = "".join('<p class="callout"><b>%s</b>%s</p>' % (md(c["label"]), md(c["text"])) for c in t.get("callouts", []))
    calls = '<div class="seat-callouts">%s</div>' % calls if calls else ""
    op = "true" if i == 0 else "false"
    return ('<div id="pane-%s" class="tb-pane seat" role="tabpanel" aria-labelledby="t-%s">\n<div class="seat-head"><h2 class="seat-h">'
            '<button type="button" class="seat-btn" aria-expanded="%s" aria-controls="seat-%s-body"><span><span class="seat-eyebrow">%s<span class="shnav-pill">%s</span></span>'
            '<span class="seat-title">%s</span></span></button></h2></div>\n<div class="seat-body" id="seat-%s-body"><p class="seat-lede">%s</p>\n%s\n%s</div>\n</div>') % (
        tid, tid, op, tid, md(t["name"]), md(t["rank"]), md(t["headline"]), tid, md(t["lede"]), units, calls)


# kit 51 display preferences: the global header control (theme switch + reading options), same on every template
SUN = ('<svg viewBox="0 0 20 20" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round">'
       '<circle cx="10" cy="10" r="3.6"/><path d="M10 1.8v2M10 16.2v2M1.8 10h2M16.2 10h2M4.2 4.2l1.4 1.4M14.4 14.4l1.4 1.4M4.2 15.8l1.4-1.4M14.4 5.6l1.4-1.4"/></svg>')
DPREFS_ROW = ('<div class="dprefs"><button type="button" class="dprefs-theme" aria-pressed="false" aria-label="Dark mode">' + SUN +
              '<span class="dprefs-ttl">Dark mode</span><span class="dprefs-trk" aria-hidden="true"></span></button>'
              '<button type="button" class="dprefs-aa" aria-expanded="false" aria-controls="dprefs" aria-label="Reading options"><span aria-hidden="true">Aa</span></button></div>')
DP_GROUPS = [("font", "Font", [("std", "Standard"), ("easy", "Easy-read")]),
             ("size", "Text size", [("std", "Standard"), ("l", "Larger"), ("xl", "Largest")]),
             ("space", "Spacing", [("std", "Standard"), ("roomy", "Roomy")])]


def dprefs_panel():
    g = "".join('<div class="dprefs-group" role="group" aria-labelledby="dprefs-%s"><span id="dprefs-%s" class="dprefs-label">%s</span><span class="dprefs-btns">%s</span></div>' % (
        k, k, lab, "".join('<button type="button" data-k="%s" data-v="%s" aria-pressed="%s">%s</button>' % (k, v, str(v == "std").lower(), t) for v, t in opts))
        for k, lab, opts in DP_GROUPS)
    return ('<section id="dprefs" class="dprefs-panel" role="dialog" aria-modal="false" aria-labelledby="dprefs-h" hidden>'
            '<p id="dprefs-h" class="dprefs-title">Reading options</p>%s<div class="dprefs-actions"><button type="button" data-reset>Reset</button>'
            '<button type="button" data-close>Close</button></div></section>') % g


def r_nav(d):
    tabs = ['<button type="button" class="shnav-tab" role="tab" id="t-ov" aria-controls="pane-ov" data-target="pane-ov" aria-selected="true" aria-current="true">%s</button>' % md(d["overview"]["label"])]
    for t in d["tabs"]:
        tabs.append('<button type="button" class="shnav-tab" role="tab" id="t-%s" aria-controls="pane-%s" data-target="pane-%s" aria-selected="false" tabindex="-1">%s<span class="shnav-pill">%s</span></button>' % (
            t["id"], t["id"], t["id"], md(t["label"]), md(t["rank"])))
    return ('<div class="tb-navwrap"><nav class="shnav" id="shnav" aria-label="Sections" data-menu-below="1024"><span class="shnav-current" aria-hidden="true"></span><div class="shnav-tabs" id="viewtabs" aria-label="View">%s</div>'
            '<button type="button" class="shnav-menu" aria-expanded="false" aria-controls="viewtabs" aria-label="Jump to a section"><span></span></button></nav></div>') % "".join(tabs)


def date_long(iso):
    import datetime
    dt = datetime.date.fromisoformat(iso)
    return dt.strftime("%B ") + str(dt.day) + dt.strftime(", %Y")


def render(d, artifact=False):
    TABLE_N[0] = 0
    m = d["meta"]
    css = tokens() + "\n" + "".join(kit_block(p) for p in PARTS) + open(os.path.join(TDIR, "shell.css"), encoding="utf-8").read()
    # pre-paint: one saved object per page (theme, font, size, space); light unless the reader chose dark
    head_js = ("<script>(function(){var d=document.documentElement,s={};try{var r=localStorage.getItem('%s')||'';"
               "s=r.charAt(0)==='{'?JSON.parse(r):(r?{theme:r}:{})}catch(e){}"
               "d.setAttribute('data-theme',s.theme==='dark'?'dark':'light');"
               "var A={font:'data-font',size:'data-size',space:'data-space'};for(var k in A){if(s[k]&&s[k]!=='std')d.setAttribute(A[k],s[k])}})();</script>") % d["storage_key"]
    meta = ('<dl class="tb-meta"><div class="opt"><dt>Prepared for</dt><dd>%s</dd></div><div><dt>From</dt><dd>%s</dd></div>'
            '%s%s</dl>') % (
        md(m["prepared_for"]), md(m["from"]),
        ('<div><dt>Updated</dt><dd><time datetime="%s">%s</time></dd></div>' % (e(m["updated"]), date_long(m["updated"]))) if m.get("updated") else "",
        ('<div class="opt"><dt>Status</dt><dd>%s</dd></div>' % md(m["status"])) if m.get("status") else "")
    line = ('<span class="chip cyan">Private</span><p>%s</p>' % md(d["top_line"])) if d.get("top_line") else ""
    top = ('<header class="tb-top"><span class="wordmark tb-brand"><span class="wa">ARCS</span><span class="wf">FIELD OS</span></span>%s%s</header>\n%s') % (
        line, DPREFS_ROW, dprefs_panel())
    body = "\n".join([r_overview(d)] + [r_tab(t, d["horizons"], i) for i, t in enumerate(d["tabs"])])
    main = ('<main class="tb" data-store="' + e(d["storage_key"]) + '">\n%s\n<section class="tb-frame" aria-label="%s">\n%s\n%s\n<div class="tb-body">\n%s\n</div>\n</section>\n</main>\n'
            '<script>%s</script>\n<script>%s</script>') % (top, e(d["doc_title"]), meta, r_nav(d), body, shnav_js()[len("<script>"):-len("</script>")],
                                                           open(os.path.join(TDIR, "shell.js"), encoding="utf-8").read())
    marks = "<!-- @arcs-template: tabbed-brief -->\n<!-- @arcs-mode: persuade -->\n"
    head = ('<title>%s</title>\n<meta name="robots" content="noindex, nofollow">\n%s\n<style>\n%s</style>\n') % (e(d["doc_title"]), head_js, css)
    if artifact:
        return marks + '<meta name="claude:viewport-fit-sides" content="cover">\n' + head + main + "\n"
    ana = '<script defer src="/_vercel/insights/script.js"></script>\n' if d.get("analytics") else ""
    return ('<!doctype html>\n' + marks + '<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n<meta name="color-scheme" content="light dark">\n%s%s</head>\n<body>\n%s\n</body>\n</html>\n') % (
        head, ana, main)


def build(path, out=None, artifact=False):
    d = json.load(open(path, encoding="utf-8"))
    errs = validate(d)
    if errs:
        for x in errs:
            print("✖ " + x)
        raise SystemExit(1)
    page = render(d, artifact)
    if artifact:
        page = page.replace('<html lang="en"', '<html lang="en"')  # no-op; the Artifact host supplies <html>
    if out:
        open(out, "w", encoding="utf-8").write(page)
    return page


def check():
    bad = 0
    for data, page in REGISTERED.items():
        want = build(os.path.join(ROOT, data))
        have = open(os.path.join(ROOT, page), encoding="utf-8").read() if os.path.exists(os.path.join(ROOT, page)) else ""
        if want != have:
            bad += 1
            print("✖ %s differs from %s. Run python3 scripts/tabbed_brief_build.py %s -o %s" % (page, data, data, page))
        else:
            print("✓ %s matches %s" % (page, data))
    return 1 if bad else 0


def self_test():
    base = json.load(open(os.path.join(ROOT, "_ARTIFACTS/tabbed-brief/gravity.json"), encoding="utf-8"))
    cases = []
    x = copy.deepcopy(base); x["tabs"][0]["units"][0]["blocks"][0]["rows"][0].pop(); cases.append(("plan row short a horizon", x, "horizon cells"))
    x = copy.deepcopy(base); x["tabs"][1]["id"] = x["tabs"][0]["id"]; cases.append(("duplicate tab id", x, "unique"))
    x = copy.deepcopy(base); x["overview"]["actions"][0]["tab"] = "nope"; cases.append(("action to a missing tab", x, "does not exist"))
    x = copy.deepcopy(base); x["overview"]["lede"] += " — x"; cases.append(("em-dash in copy", x, "em-dash"))
    x = copy.deepcopy(base); del x["meta"]; cases.append(("missing meta", x, "meta"))
    x = copy.deepcopy(base); x["horizons"] = [30, 90]; cases.append(("horizons change without rows", x, "horizon"))
    ok = True
    for name, d, want in cases:
        errs = validate(d)
        hit = any(want in er for er in errs)
        print(("PASS " if hit else "FAIL ") + name)
        ok = ok and hit
    good = not validate(base)
    print(("PASS " if good else "FAIL ") + "the committed data is valid")
    return 0 if ok and good else 1


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("data", nargs="?")
    ap.add_argument("-o", "--out")
    ap.add_argument("--artifact")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    if a.check:
        return check()
    if not a.data:
        ap.error("give a data file, --check or --self-test")
    if a.artifact:
        build(a.data, a.artifact, artifact=True)
        print("wrote " + a.artifact)
    if a.out or not a.artifact:
        out = a.out or re.sub(r"\.json$", ".html", a.data)
        build(a.data, out)
        print("wrote " + out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
