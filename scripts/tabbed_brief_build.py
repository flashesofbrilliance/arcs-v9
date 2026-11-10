"""tabbed_brief_build: render a tabbed counterpart brief from the tabbed-brief template plus a data file.
The page is generated from four parts and never hand-edited:
  tokens    src/ui-kit/recoil-report/_tokens.css, inlined verbatim (sentinel line kept)
  kit       the @prim blocks of the parts the page uses, copied verbatim from src/ui-kit/recoil-report/NN-*.html
            (27 section-label, 28 chip, 31 callout, 38 wordmark, 39 theme light remap, 42 shell-nav, 45 fact-tile, 51 display-preferences, 52 plan-matrix, 53 cold-read)
  template  src/ui-kit/tabbed-brief/shell.css + shell.js (frame and page organisms, no counterpart content)
  data      a JSON file valid against src/ui-kit/tabbed-brief/brief.schema.json (all copy; links as [text](url), bold as **text**)
  python3 scripts/tabbed_brief_build.py DATA.json -o OUT.html            write the full page (doctype, analytics if the data asks)
  python3 scripts/tabbed_brief_build.py DATA.json --artifact OUT.html    write the Artifact body (no doctype, no analytics)
  python3 scripts/tabbed_brief_build.py DATA.json --tune OUT.html        internal copy with the tuner: ?tune sliders, ?edit text; refuses public/
  python3 scripts/tabbed_brief_build.py DATA.json --apply PATCH.json     apply the JSON patch the tuner copies, then rebuild
  python3 scripts/tabbed_brief_build.py --check                          exit 1 if a registered page differs from its data
  python3 scripts/tabbed_brief_build.py --self-test                      prove the validator rejects each bad shape
Stdlib only.
"""
import argparse, copy, html, json, os, re, sys, tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KIT = os.path.join(ROOT, "src/ui-kit/recoil-report")
TDIR = os.path.join(ROOT, "src/ui-kit/tabbed-brief")
SCHEMA = os.path.join(TDIR, "brief.schema.json")
PARTS = ["27-section-label", "28-chip", "31-callout", "45-fact-tile", "54-signal-ledger", "55-sound-bite", "38-wordmark", "39-theme-toggle", "42-shell-nav", "51-display-preferences", "52-plan-matrix", "53-cold-read"]
REGISTERED = {"_ARTIFACTS/tabbed-brief/gravity.json": "public/gravity-brief.html"}
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import precall_brief_build as pb  # the stdlib JSON Schema subset lives there; reuse it, do not fork it
TUNE = [False]  # --tune build: each data string sits in a span carrying its JSON pointer (data-src) for the tuner's ?edit mode


def e(s):
    return html.escape(str(s), quote=True)


def md(s, src=None):
    """Escape, then allow two inline marks only: [text](https://...) and **bold**. src: the JSON pointer of s (used by --tune only)."""
    t = e(s)
    t = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", lambda m: '<a href="%s">%s</a>' % (m.group(2), m.group(1)), t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    return ('<span data-src="%s">%s</span>' % (e(src), t)) if (TUNE[0] and src) else t


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


def bite_js():
    return json.load(open(os.path.join(ROOT, "src/ui-kit/specimens/sound-bite.json"), encoding="utf-8"))["tail_js"]


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
                if "know" in b and len(b["know"]) != n:
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


def r_table(b, p=""):
    TABLE_N[0] += 1
    head = "".join("<th>%s</th>" % md(h, "%s/head/%d" % (p, i)) for i, h in enumerate(b["head"]))
    chips = b.get("chips") or []
    def first(c, j):
        k = chips[j] if j < len(chips) else ""
        q = "%s/rows/%d/0" % (p, j)
        return '<td><span class="chip %s">%s</span></td>' % (k, md(c, q)) if k else "<td>%s</td>" % md(c, q)
    rows = "".join("<tr>%s</tr>" % "".join(('<td data-label="%s">%s</td>' % (e(b["head"][i]), md(c, "%s/rows/%d/%d" % (p, j, i)))) if i else first(c, j) for i, c in enumerate(r)) for j, r in enumerate(b["rows"]))
    return '<div class="tb-scroll" tabindex="0" role="region" aria-label="Table %d: %s"><table class="tb-table"><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (
        TABLE_N[0], e(", ".join(b["head"])), head, rows)


def r_plan(b, horizons, p=""):
    hs = "".join("<th>By day %d</th>" % h for h in horizons)
    rows = ""
    for j, r in enumerate(b["rows"]):
        cells = "<td>%s</td>" % md(r[0], "%s/rows/%d/0" % (p, j)) + "".join('<td data-label="By day %d">%s</td>' % (horizons[i], md(c, "%s/rows/%d/%d" % (p, j, i + 1))) for i, c in enumerate(r[1:]))
        rows += "<tr>%s</tr>" % cells
    know = "".join('<div class="pm-k"><p class="pm-kl">Day %d</p><p>%s</p></div>' % (horizons[i], md(k, "%s/know/%d" % (p, i))) for i, k in enumerate(b.get("know", [])))
    know = ('<p class="pm-khead">How you would know it is working</p><div class="pm-know">%s</div>' % know) if know else ""
    note = '<p class="pm-note">%s</p>' % md(b["note"], p + "/note") if b.get("note") else ""
    return ('<div class="pm"><p class="pm-src">%s</p>%s<table class="pm-table"><thead><tr><th>Your page asks me to</th>%s</tr></thead>'
            '<tbody>%s</tbody></table>%s</div>') % (md(b["source"], p + "/source"), note, hs, rows, know)


def r_cards(b, hlevel, p=""):
    out = []
    for k, c in enumerate(b["cards"]):
        q = "%s/cards/%d" % (p, k)
        ref = '<p class="tb-card-ref">%s</p>' % md(c["ref"], q + "/ref") if c.get("ref") else ""
        out.append('<div class="tb-card"><h%d class="tb-card-t">%s</h%d>%s<p>%s</p></div>' % (hlevel, md(c["title"], q + "/title"), hlevel, ref, md(c["text"], q + "/text")))
    return '<div class="tb-cards">%s</div>' % "".join(out)


def r_ledger(b, p, hlevel):
    """kit 54 signal ledger: groups of rows, each a chip, the signal it rests on, and its evidence."""
    gs = []
    for gi, g in enumerate(b["groups"]):
        gp = "%s/groups/%d" % (p, gi)
        rows = "".join('<li class="sl-row"><div class="sl-key"><span class="chip%s">%s</span><span class="sl-sig">%s</span></div><p class="sl-ev">%s</p></li>' % (
            "" if r.get("tone", "plain") == "plain" else " " + r["tone"], md(r["chip"], "%s/rows/%d/chip" % (gp, ri)),
            md(r["signal"], "%s/rows/%d/signal" % (gp, ri)), md(r["text"], "%s/rows/%d/text" % (gp, ri))) for ri, r in enumerate(g["rows"]))
        gid = "sl-%s-%d" % (re.sub(r"[^a-z0-9]+", "-", p.lower()).strip("-"), gi)
        n = len(g["rows"])
        gs.append('<section class="sl-group%s" aria-labelledby="%s"><div class="sl-gh"><h%d class="section-label" id="%s">%s</h%d><span class="sl-gn">%d %s</span></div><ul class="sl-rows">%s</ul></section>' % (
            " is-judgment" if g.get("judgment") else "", gid, hlevel, gid, md(g["label"], gp + "/label"), hlevel, n, "row" if n == 1 else "rows", rows))
    return '<div class="sl">%s</div>' % "".join(gs)


def r_bites(o):
    """kit 55 sound bite: real, attributed quotes, one at a time, typed fast."""
    bs = o.get("bites")
    if not bs:
        return ""
    items = "".join('<li class="sb-item"><blockquote class="sb-q" style="margin:0"><p class="sb-t">%s</p></blockquote><p class="sb-by"><b>%s</b><span>%s</span></p></li>' % (
        md(x["text"], "/overview/bites/%d/text" % i), md(x["name"], "/overview/bites/%d/name" % i), md(x["role"], "/overview/bites/%d/role" % i)) for i, x in enumerate(bs))
    src = o.get("bites_source")
    src_html = '<span class="sb-src">%s</span>' % md(src, "/overview/bites_source") if src else ""
    return ('<figure class="sb" aria-label="What colleagues say"><ul class="sb-list">%s</ul><div class="sb-ctl"><button type="button" class="sb-btn" data-sb-prev aria-label="Previous quote">Prev</button>'
            '<span class="sb-n" aria-live="polite"></span><button type="button" class="sb-btn" data-sb-next aria-label="Next quote">Next</button>'
            '<button type="button" class="sb-btn" data-sb-pause aria-pressed="false">Pause</button>%s</div></figure>\n') % (items, src_html)


def r_blocks(bl, horizons, hlevel, base="", paths=None):
    """base: JSON pointer of the list (block i is base/i); paths overrides one pointer per block."""
    out = []
    for n, b in enumerate(bl):
        t = b["type"]
        p = paths[n] if paths else "%s/%d" % (base, n)
        if t == "p":
            out.append('<p class="tb-p">%s</p>' % md(b["text"], p + "/text"))
        elif t == "table":
            out.append(r_table(b, p))
        elif t == "plan":
            out.append(r_plan(b, horizons, p))
        elif t == "cards":
            out.append(r_cards(b, hlevel, p))
        elif t == "coldread":
            slots = "".join('<dt class="section-label">%s</dt><dd>%s</dd>' % (md(k, "%s/slots/%d/0" % (p, i)), md(v, "%s/slots/%d/1" % (p, i))) for i, (k, v) in enumerate(b["slots"]))
            how = "".join('<li class="cr-step"><p class="section-label">%s</p><p class="cr-when">%s</p><p class="cr-what">%s</p></li>' % (
                md(a, "%s/how/%d/0" % (p, i)), md(w, "%s/how/%d/1" % (p, i)), md(x, "%s/how/%d/2" % (p, i))) for i, (a, w, x) in enumerate(b.get("how", [])))
            how = '<div class="cr-howwrap"><p class="section-label" id="cr-how-l">How</p><ol class="cr-how" aria-labelledby="cr-how-l">%s</ol></div>' % how if how else ""
            read = '<p class="callout cr-read"><b>How to read</b>%s</p>' % md(b["read"], p + "/read") if b.get("read") else ""
            out.append('<div class="cr"><dl class="cr-slots">%s</dl>%s%s</div>' % (slots, how, read))
        elif t == "ledger":
            out.append(r_ledger(b, p, hlevel))
        elif t == "callout":
            out.append('<p class="callout"><b>%s</b>%s</p>' % (md(b["lead"], p + "/lead"), md(b["text"], p + "/text")))
        elif t == "list":
            tag = "ol" if b.get("ordered") else "ul"
            out.append('<%s class="tb-list">%s</%s>' % (tag, "".join("<li>%s</li>" % md(it, "%s/items/%d" % (p, i)) for i, it in enumerate(b["items"])), tag))
    return "\n".join(out)


def r_fold(s, horizons, p=""):
    sid = s["id"]
    op = "true" if s.get("open") else "false"
    hid = "" if s.get("open") else " hidden"
    return ('<section class="tb-fold" id="%s"><h2 class="tb-h2"><button type="button" class="tb-fold-btn" aria-expanded="%s" aria-controls="%s-body">'
            '<span><span class="tb-fold-t">%s</span><span class="tb-tag">%s</span></span></button></h2>'
            '<div class="tb-fold-body" id="%s-body"%s>%s</div></section>') % (sid, op, sid, md(s["title"], p + "/title"), md(s["tagline"], p + "/tagline"), sid, hid, r_blocks(s["blocks"], horizons, 3, p + "/blocks"))


def r_overview(d):
    o = d["overview"]
    h = "".join('<span class="hl">%s</span>' % md(re.sub(r"(?<=[a-z])-(?=[a-z])", "‑", x), "/overview/headline/%d" % i) for i, x in enumerate(o["headline"]))
    acts = []
    for a in o.get("actions", []):
        cls = "tb-btn primary" if a.get("primary") else "tb-btn"
        if "tab" in a:
            acts.append('<a class="%s" href="#%s" data-go-tab="%s">%s</a>' % (cls, a["tab"], a["tab"], md(a["label"])))
        else:
            acts.append('<a class="%s" href="#%s" data-go-section="%s">%s</a>' % (cls, a["section"], a["section"], md(a["label"])))
    tiles = "".join('<li class="ftile"><span class="ftile-lab">%s</span><span class="ftile-fig">%s</span><span class="ftile-cap">%s</span></li>' % (
        md(t["k"], "/overview/tiles/%d/k" % i), md(t["v"], "/overview/tiles/%d/v" % i), md(t["note"], "/overview/tiles/%d/note" % i)) for i, t in enumerate(o["tiles"]))
    folds = "\n".join(r_fold(s, d["horizons"], "/overview/sections/%d" % i) for i, s in enumerate(o["sections"]))
    cr = ""
    if o.get("coldread"):
        c = o["coldread"]
        cr = '<section class="tb-coldread" id="%s" aria-labelledby="%s-h"><h2 class="tb-h2" id="%s-h">%s</h2>%s</section>\n' % (c["id"], c["id"], c["id"], md(c["title"], "/overview/coldread/title"), r_blocks([c["block"]], d["horizons"], 3, paths=["/overview/coldread/block"]))
    # order is the 7-second read: claim, who, proof, one action; detail folds below
    ns = o.get("next_step", {})
    lead = ('<p class="tb-go-h">%s</p>' % md(ns["lead"], "/overview/next_step/lead")) if ns.get("lead") else ""
    cap = ('<p class="tb-go-t">%s</p>' % md(ns["text"], "/overview/next_step/text")) if ns.get("text") else ""
    note = ('<p class="tb-note">%s</p>' % md(o["action_note"], "/overview/action_note")) if o.get("action_note") else ""
    acts_html = ('<div class="tb-actions">%s</div>' % "".join(acts)) if acts else ""
    go = ('<div class="tb-go">%s%s%s%s</div>\n' % (lead, acts_html, cap, note)) if (lead or acts_html or cap or note) else ""
    out = ('<div id="pane-ov" class="tb-pane" role="tabpanel" aria-labelledby="t-ov">\n<h1 class="tb-h1">%s</h1>\n%s%s%s'
            '<div class="ftiles-c"><ul class="ftiles is-4" aria-label="At a glance">%s</ul></div>\n'
            '%s'
            '%s<div class="tb-expand%s"><button type="button" class="tb-btn" id="tb-expand" aria-pressed="false">Expand all</button></div>\n'
            '<div class="tb-folds">%s</div>\n</div>') % (h, (('<p class="tb-byline">%s</p>\n' % md(o["byline"], "/overview/byline")) if o.get("byline") else "") + r_bites(o), ('<h2 class="tb-sub">%s</h2>\n' % md(o["subhead"], "/overview/subhead")) if o.get("subhead") else "", ('<p class="tb-lede">%s</p>\n' % "".join('<span class="ln">%s</span>' % md(re.sub(r"(?<=[a-z])-(?=[a-z])", "‑", x), "/overview/lede/%d" % i) for i, x in enumerate(o["lede"]))) if o.get("lede") else "",
         tiles, go, cr,
         " solo" if len(o["sections"]) < 2 else "", folds)
    if d.get("pages") and len(o["sections"]) < 2:
        out = re.sub(r'<div class="tb-expand[^"]*"><button[^<]*</button></div>\n', "", out)
    return out


def r_tab(t, horizons, i, page=False, p=""):
    tid = t["id"]
    units = "\n".join('<section class="unit"><h3 class="tb-h3">%s</h3>%s</section>' % (md(u["title"], "%s/units/%d/title" % (p, k)), r_blocks(u["blocks"], horizons, 4, "%s/units/%d/blocks" % (p, k))) for k, u in enumerate(t["units"]))
    calls = "".join('<p class="callout"><b>%s</b>%s</p>' % (md(c["label"], "%s/callouts/%d/label" % (p, k)), md(c["text"], "%s/callouts/%d/text" % (p, k))) for k, c in enumerate(t.get("callouts", [])))
    calls = '<div class="seat-callouts">%s</div>' % calls if calls else ""
    op = "true" if i == 0 else "false"
    if page:
        # a role on its own page: no fold, the seat name shows as the eyebrow; headings step h1, h2, h3
        units = "\n".join('<section class="unit"><h2 class="tb-h3">%s</h2>%s</section>' % (md(u["title"], "%s/units/%d/title" % (p, k)), r_blocks(u["blocks"], horizons, 3, "%s/units/%d/blocks" % (p, k))) for k, u in enumerate(t["units"]))
        return ('<div id="pane-%s" class="tb-pane seat">\n<div class="seat-head"><p class="section-label seat-name">%s</p><h1 class="seat-h">%s</h1></div>\n'
                '<div class="seat-body" id="seat-%s-body"><p class="seat-lede">%s</p>\n%s\n%s</div>\n</div>') % (
            tid, md(t["name"], p + "/name"), md(t["headline"], p + "/headline"), tid, md(t["lede"], p + "/lede"), units, calls)
    return ('<div id="pane-%s" class="tb-pane seat" role="tabpanel" aria-labelledby="t-%s">\n<div class="seat-head"><h2 class="seat-h">'
            '<button type="button" class="seat-btn" aria-expanded="%s" aria-controls="seat-%s-body"><span><span class="seat-eyebrow">%s%s</span>'
            '<span class="seat-title">%s</span></span></button></h2></div>\n<div class="seat-body" id="seat-%s-body"><p class="seat-lede">%s</p>\n%s\n%s</div>\n</div>') % (
        tid, tid, op, tid, md(t["name"], p + "/name"), ('<span class="shnav-pill">%s</span>' % md(t["rank"], p + "/rank")) if t.get("rank") else "", md(t["headline"], p + "/headline"), tid, md(t["lede"], p + "/lede"), units, calls)


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


def page_hrefs(d, artifact):
    """Where each page lives: on the site a path per role; in the Artifact a sibling file per role; in a --tune build a sibling file that keeps ?tune."""
    if TUNE[0]:
        base = TUNE[1]
        return dict([("ov", base + ".html?tune&edit")] + [(t["id"], "%s-%s.html?tune&edit" % (base, t["id"])) for t in d["tabs"]])
    ov = "./" if artifact else "/"
    return dict([("ov", ov)] + [(t["id"], ("%s.html" if artifact else "/%s") % t["id"]) for t in d["tabs"]])


def r_nav_links(d, cur, hrefs):
    items = [("ov", d["overview"]["label"])] + [(t["id"], t["label"]) for t in d["tabs"]]
    tabs = "".join('<a class="shnav-tab" href="%s" data-target="pane-%s" aria-current="%s">%s</a>' % (e(hrefs[i]), i, "page" if i == cur else "false", md(lab)) for i, lab in items)
    return ('<div class="tb-navwrap"><nav class="shnav" id="shnav" aria-label="Pages" data-menu-below="%d"><span class="shnav-current" aria-hidden="true"></span><div class="shnav-tabs" id="viewtabs">%s</div>'
            '<button type="button" class="shnav-menu" aria-expanded="false" aria-controls="viewtabs" aria-label="Go to a page"><span></span></button></nav></div>') % (stack_below(d), tabs)


def r_nav(d):
    tabs = ['<button type="button" class="shnav-tab" role="tab" id="t-ov" aria-controls="pane-ov" data-target="pane-ov" aria-selected="true" aria-current="true">%s</button>' % md(d["overview"]["label"])]
    for t in d["tabs"]:
        tabs.append('<button type="button" class="shnav-tab" role="tab" id="t-%s" aria-controls="pane-%s" data-target="pane-%s" aria-selected="false" tabindex="-1">%s%s</button>' % (
            t["id"], t["id"], t["id"], md(t["label"]), ('<span class="shnav-pill">%s</span>' % md(t["rank"])) if t.get("rank") else ""))
    return ('<div class="tb-navwrap"><nav class="shnav" id="shnav" aria-label="Sections" data-menu-below="%d"><span class="shnav-current" aria-hidden="true"></span><div class="shnav-tabs" id="viewtabs" aria-label="View">%s</div>'
            '<button type="button" class="shnav-menu" aria-expanded="false" aria-controls="viewtabs" aria-label="Jump to a section"><span></span></button></nav></div>') % (stack_below(d), "".join(tabs))


def stack_below(d):
    """Width below which the tabs fold into the menu and the roles stack (shell.css writes 1024; data may move it)."""
    return int(d.get("stack_below", 1024))


def date_long(iso):
    import datetime
    dt = datetime.date.fromisoformat(iso)
    return dt.strftime("%B ") + str(dt.day) + dt.strftime(", %Y")


def render(d, artifact=False, page=None):
    TABLE_N[0] = 0
    m = d["meta"]
    shell = open(os.path.join(TDIR, "shell.css"), encoding="utf-8").read().replace("(min-width: 1024px)", "(min-width: %dpx)" % stack_below(d))
    rules = re.sub(r"/\*.*?\*/", "", shell, flags=re.S)  # braces quoted in comments do not count
    if rules.count("{") != rules.count("}"):  # an unclosed block swallows every rule after it, including a pasted tuner line
        raise SystemExit("shell.css: %d '{' but %d '}' outside comments; close the open block" % (rules.count("{"), rules.count("}")))
    css = tokens() + "\n" + "".join(kit_block(p) for p in PARTS) + shell
    # pre-paint: one saved object per page (theme, font, size, space); the page's default_theme (light if unset) unless the reader chose
    head_js = ("<script>(function(){var d=document.documentElement,s={};try{var r=localStorage.getItem('%s')||'';"
               "s=r.charAt(0)==='{'?JSON.parse(r):(r?{theme:r}:{})}catch(e){}"
               "d.setAttribute('data-theme',(s.theme||'%s')==='dark'?'dark':'light');"
               "var A={font:'data-font',size:'data-size',space:'data-space'};for(var k in A){if(s[k]&&s[k]!=='std')d.setAttribute(A[k],s[k])}})();</script>") % (d["storage_key"], d.get("default_theme", "light"))
    meta = ('<dl class="tb-meta"><div class="opt"><dt>Prepared for</dt><dd>%s</dd></div><div><dt>From</dt><dd>%s</dd></div>'
            '%s%s</dl>') % (
        md(m["prepared_for"]), md(m["from"]),
        ('<div><dt>Updated</dt><dd><time datetime="%s">%s</time></dd></div>' % (e(m["updated"]), date_long(m["updated"]))) if m.get("updated") else "",
        ('<div class="opt"><dt>Status</dt><dd>%s</dd></div>' % md(m["status"])) if m.get("status") else "")
    line = ('<span class="chip cyan">Private</span><p>%s</p>' % md(d["top_line"])) if d.get("top_line") else ""
    top = ('<header class="tb-top"><span class="wordmark tb-brand"><span class="wa">ARCS</span><span class="wf">FIELD OS</span></span>%s%s</header>\n%s') % (
        line, DPREFS_ROW, dprefs_panel())
    title = d["doc_title"]
    if page is None:
        body, nav, pages_attr = "\n".join([r_overview(d)] + [r_tab(t, d["horizons"], i, p="/tabs/%d" % i) for i, t in enumerate(d["tabs"])]), r_nav(d), ""
    else:
        # one pane per page; the nav links between pages
        t = next((x for x in d["tabs"] if x["id"] == page), None)
        body = r_overview(d) if t is None else r_tab(t, d["horizons"], 0, page=True, p="/tabs/%d" % d["tabs"].index(t))
        nav, pages_attr = r_nav_links(d, page, page_hrefs(d, artifact)), ' data-pages="1"'
        body = re.sub(r' role="tabpanel" aria-labelledby="t-[a-z0-9-]+"', "", body)  # a page, not a tab panel
        if t is not None:
            title = "%s · %s" % (t["name"], d["doc_title"])
    main = ('<main class="tb" data-store="' + e(d["storage_key"]) + '" data-default-theme="' + e(d.get("default_theme", "light")) + '"' + pages_attr + '>\n%s\n<section class="tb-frame" aria-label="%s">\n<div class="tb-head">%s\n%s</div>\n<div class="tb-body">\n%s\n</div>\n</section>\n</main>\n'
            '<script>%s</script>\n<script>%s</script>%s') % (top, e(d["doc_title"]), meta, nav, body, shnav_js()[len("<script>"):-len("</script>")],
                                                           open(os.path.join(TDIR, "shell.js"), encoding="utf-8").read(),
                                                           ("\n" + bite_js()[:-len("</script>")] + ";[].forEach.call(document.querySelectorAll('.sb'),function(f){sbInit(f,%s)});</script>" % ("{still:true}" if d["overview"].get("bites_still") else "{}")) if 'class="sb"' in body else "")
    marks = "<!-- @arcs-template: tabbed-brief -->\n<!-- @arcs-mode: persuade -->\n"
    head = ('<title>%s</title>\n<meta name="robots" content="noindex, nofollow">\n%s\n<style>\n%s</style>\n') % (e(title), head_js, css)
    if artifact and page in (None, "ov"):
        return marks + '<meta name="claude:viewport-fit-sides" content="cover">\n' + head + main + "\n"
    # a full document: the site page, or an Artifact subpage (served without the host's wrapper, so it brings its own head)
    ana = '<script defer src="/_vercel/insights/script.js"></script>\n' if d.get("analytics") and not artifact else ""
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
    return write_pages(d, out, artifact)


def outputs(d, out, artifact=False):
    """Every file one data file produces: {path: html}. Pages mode adds one file per role beside the overview."""
    if not d.get("pages"):
        return {out: render(d, artifact)}
    folder, base = os.path.split(out)
    res = {out: render(d, artifact, "ov")}
    for t in d["tabs"]:
        name = ("%s.html" % t["id"]) if artifact else re.sub(r"\.html$", "-%s.html" % t["id"], base)
        res[os.path.join(folder, name)] = render(d, artifact, t["id"])
    return res


def write_pages(d, out, artifact=False):
    res = outputs(d, out or "", artifact)
    if out:
        for p, html_ in res.items():
            open(p, "w", encoding="utf-8").write(html_)
    return res


def tune_build(path, out):
    """Internal copy for hand tuning: data-src spans, the breakpoint's data pointer on <main>, and the tuner inlined first in <body>."""
    import token_tuner_inline as tti
    if os.path.abspath(out).startswith(os.path.join(ROOT, "public") + os.sep):
        raise SystemExit("--tune output must not live under public/: the tuner is internal only")
    TUNE[:] = [True, re.sub(r"\.html$", "", os.path.basename(out))]
    try:
        d = json.load(open(path, encoding="utf-8"))
        res = outputs(d, out)
    finally:
        TUNE[:] = [False]
    for f, h in res.items():
        h = h.replace('<main class="tb"', '<main data-bp="%d" data-bp-src="/stack_below" class="tb"' % stack_below(d), 1)
        open(f, "w", encoding="utf-8").write(tti.inline(h))
        print("wrote %s (open with ?tune, add &edit to edit text)" % f)
    return res


def apply_patch(data_path, patch_path):
    """Apply an RFC 6902 patch (replace / add only, the two ops the tuner writes) to a data file, validate, keep the file's format."""
    d = json.load(open(data_path, encoding="utf-8"))
    ops = json.load(open(patch_path, encoding="utf-8"))
    for op in ops:
        if op.get("op") not in ("replace", "add"):
            raise SystemExit("unsupported op %r (the tuner writes replace and add)" % op.get("op"))
        keys = [k.replace("~1", "/").replace("~0", "~") for k in op["path"].split("/")[1:]]
        cur = d
        for k in keys[:-1]:
            cur = cur[int(k)] if isinstance(cur, list) else cur[k]
        last = keys[-1]
        if isinstance(cur, list):
            cur[int(last)] = op["value"]
        elif op["op"] == "replace" and last not in cur:
            raise SystemExit("replace on a missing key: %s" % op["path"])
        else:
            cur[last] = op["value"]
    errs = validate(d)
    if errs:
        for x in errs:
            print("✖ " + x)
        raise SystemExit(1)
    raw = open(data_path, encoding="utf-8").read()
    m = re.search(r"\n( +)\"", raw)  # keep the file's own indent, so a one-field patch is a one-line diff
    out = json.dumps(d, indent=len(m.group(1)) if m else 1, ensure_ascii=False) + ("\n" if raw.endswith("\n") else "")
    open(data_path, "w", encoding="utf-8").write(out)
    print("applied %d op(s) to %s" % (len(ops), data_path))


def check():
    bad = 0
    for data, page in REGISTERED.items():
        d = json.load(open(os.path.join(ROOT, data), encoding="utf-8"))
        for path, want in outputs(d, os.path.join(ROOT, page)).items():
            rel = os.path.relpath(path, ROOT)
            have = open(path, encoding="utf-8").read() if os.path.exists(path) else ""
            if want != have:
                bad += 1
                print("✖ %s differs from %s. Run python3 scripts/tabbed_brief_build.py %s -o %s" % (rel, data, data, page))
            else:
                print("✓ %s matches %s" % (rel, data))
    return 1 if bad else 0


def self_test():
    base = json.load(open(os.path.join(ROOT, "_ARTIFACTS/tabbed-brief/gravity.json"), encoding="utf-8"))
    cases = []
    x = copy.deepcopy(base); x["tabs"][0]["units"][0]["blocks"][0]["rows"][0].pop(); cases.append(("plan row short a horizon", x, "horizon cells"))
    x = copy.deepcopy(base); x["tabs"][1]["id"] = x["tabs"][0]["id"]; cases.append(("duplicate tab id", x, "unique"))
    x = copy.deepcopy(base); x["overview"]["actions"] = [{"label": "Go", "tab": "nope"}]; cases.append(("action to a missing tab", x, "does not exist"))
    x = copy.deepcopy(base); x["overview"]["headline"][0] += " — x"; cases.append(("em-dash in copy", x, "em-dash"))
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
    ap.add_argument("--tune", metavar="OUT.html")
    ap.add_argument("--apply", metavar="PATCH.json")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    if a.check:
        return check()
    if not a.data:
        ap.error("give a data file, --check or --self-test")
    if a.apply:
        apply_patch(a.data, a.apply)
        rebuilt = [p for dp, p in REGISTERED.items() if os.path.abspath(os.path.join(ROOT, dp)) == os.path.abspath(a.data)]
        for p in rebuilt:
            build(a.data, os.path.join(ROOT, p))
            print("rebuilt " + p)
        return 0
    if a.tune:
        tune_build(a.data, a.tune)
        return 0
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
