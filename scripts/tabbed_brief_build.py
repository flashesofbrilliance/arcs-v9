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
  python3 scripts/tabbed_brief_build.py DATA.json --apply EXPORT [...]   the tuner's exports back to source (scripts/page_tune.py), then rebuild
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
import page_tune as pt  # the shared --tune / --apply mechanics
import proof_emit as pe  # the proof claims and falsification ledger, read at build time so quoted claims and counts never drift
TUNE = [False]  # --tune build: [True, page base name]; pt.TUNE makes md() wrap each data string in its JSON pointer (data-src)


def e(s):
    return html.escape(str(s), quote=True)


# ---------- live sources: proof claims + falsification ledger (scripts/proof_emit.py load()) ----------
_SRC = []
GEN = [False]  # True while rendering a block generated from the sources: no data-src pointer for the tuner
TOK = re.compile(r"\{([a-z_]+)\}")
STATUS_TONE = {"shown": "cyan", "on-request": "plain", "not-yet": "gold"}  # kit 54 tones: cyan has a public record, gold is a gap
THIRD = re.compile(r"\b(he|his|him)\b", re.I)  # ledger claims are third person; a first-person page quotes only the ones that read either way


def src():
    """(claims by id, ledger by id, count tokens, ledger ids the public may read). Tokens: proof_emit's fill plus the claim scoreboard."""
    if not _SRC:
        d, ledger, fill = pe.load()
        claims = {c["id"]: c for q in d["questions"] for c in q["claims"]}
        n = lambda st: str(sum(1 for c in claims.values() if c["status"] == st))
        tok = dict(fill, claims_total=str(len(claims)), claims_shown=n("shown"), claims_on_request=n("on-request"), claims_not_yet=n("not-yet"))
        public = {fid for c in claims.values() for fid in c.get("ledger", [])}  # cleared through the proof page; the rest stay shape-only
        _SRC.append((claims, ledger, tok, public))
    return _SRC[0]


def fill(s):
    return TOK.sub(lambda m: src()[2].get(m.group(1), m.group(0)), s)


def plain(s):
    return s.replace(" \u2014 ", "; ").replace("\u2014", ", ")


def claim_row(c):
    ev = c["evidence"].rstrip(": ")
    ev += "" if ev.endswith(".") else "."
    rec = (" Record: [%s](%s)." % (c.get("label") or "link", c["url"])) if c.get("url") else ""
    return {"chip": pe.STATUS_LABEL[c["status"]], "tone": STATUS_TONE[c["status"]], "status": True, "signal": c["date"], "text": "**%s** %s%s" % (c["claim"], ev, rec)}


def claim_ref(c):
    return ("[%s](%s)" % (c["claim"].rstrip("."), c["url"])) if c.get("url") else "%s (%s)" % (c["claim"].rstrip("."), pe.STATUS_LABEL[c["status"]])


def expand(b):
    """The three live block types become a kit 54 ledger or a table, filled from the sources."""
    claims, ledger, _, _ = src()
    if b["type"] == "proof":
        return {"type": "ledger", "groups": [{"label": g["label"], "rows": [claim_row(claims[i]) for i in g["ids"]]} for g in b["groups"]]}
    if b["type"] == "beliefs":
        rows = [{"chip": ledger[i]["scope"], "tone": "plain", "signal": "killed " + ledger[i]["ts"],
                 "text": "**Believed:** %s **Test:** %s **Found:** %s" % (plain(ledger[i]["claim"]), plain(ledger[i]["test"]), plain(ledger[i]["delta"]))} for i in b["ids"]]
        return {"type": "ledger", "groups": [{"label": b["label"], "rows": rows}]}
    if b["type"] == "hats":
        return {"type": "table", "head": ["Hat", "What I would do", "Shown by"],
                "rows": [[r["hat"], r["text"], "; ".join(claim_ref(claims[i]) for i in r["ids"])] for r in b["rows"]]}
    return b


def md(s, src=None):
    """Escape, then allow two inline marks only: [text](https://... or mailto:...) and **bold**. src: the JSON pointer of s (used by --tune only).
    {tokens} fill from the live sources first (see src())."""
    t = e(fill(s))
    src = None if GEN[0] else src
    t = re.sub(r"\[([^\]]+)\]\(((?:https?://|mailto:)[^)\s]+)\)", lambda m: '<a href="%s">%s</a>' % (m.group(2), m.group(1)), t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    return pt.span(t, src)


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

    claims, ledger, tok, public = src()

    def ids_ok(where, ids):
        for c in ids:
            if c not in claims:
                errs.append("%s: claim %r is not in runtime/specs/proof-claims.json" % (where, c))
            elif THIRD.search(claims[c]["claim"] + " " + claims[c]["evidence"]):
                errs.append("%s: claim %r is third person (he/his); this page is first person, pick another or reword the claim" % (where, c))

    def blocks(where, bl):
        for i, b in enumerate(bl):
            if b.get("type") == "proof":
                for g in b.get("groups", []):
                    ids_ok("%s[%d]" % (where, i), g.get("ids", []))
            if b.get("type") == "hats":
                for r in b.get("rows", []):
                    ids_ok("%s[%d]" % (where, i), r.get("ids", []))
            if b.get("type") == "beliefs":
                for f in b.get("ids", []):
                    if f not in ledger:
                        errs.append("%s[%d]: ledger id %r is not in _STATE/falsification-ledger.jsonl" % (where, i, f))
                    elif f not in public:
                        errs.append("%s[%d]: ledger id %r is not cleared for the public (only ids a proof claim cites are)" % (where, i, f))
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
    for name in sorted(set(TOK.findall(json.dumps(d, ensure_ascii=False))) - set(tok)):
        errs.append("$: unknown token {%s}; known: %s" % (name, ", ".join(sorted(tok))))
    return errs


# ---------- organisms ----------
TABLE_N = [0]  # each scroll region gets its own name (axe landmark-unique)


def nbh(x):
    """No-wrap hyphens (U+2011) between letters in display text, never inside a markdown link target:
    a U+2011 in an href breaks the link (it shipped once on the Gravity overview, 2026-11-11)."""
    parts = re.split(r"(\]\([^)]*\))", x)
    return "".join(q if q.startswith("](") else re.sub(r"(?<=[a-z])-(?=[a-z])", "\u2011", q) for q in parts)


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
        rows = "".join('<li class="sl-row is-%s"><div class="sl-key"><span class="chip%s">%s</span><span class="sl-sig">%s</span></div><p class="sl-ev">%s</p></li>' % (
            re.sub(r"[^a-z0-9]+", "-", r["chip"].lower()).strip("-"), ("" if r.get("tone", "plain") == "plain" else " " + r["tone"]) + (" status" if r.get("status") else ""), md(r["chip"], "%s/rows/%d/chip" % (gp, ri)),
            md(r["signal"], "%s/rows/%d/signal" % (gp, ri)), md(r["text"], "%s/rows/%d/text" % (gp, ri))) for ri, r in enumerate(g["rows"]))
        gid = "sl-%s-%d" % (re.sub(r"[^a-z0-9]+", "-", p.lower()).strip("-"), gi)
        n = len(g["rows"])
        gs.append('<section class="sl-group%s" aria-labelledby="%s"><div class="sl-gh"><h%d class="section-label" id="%s">%s</h%d></div><ul class="sl-rows">%s</ul></section>' % (
            " is-judgment" if g.get("judgment") else "", gid, hlevel, gid, md(g["label"], gp + "/label"), hlevel, rows))
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
        p = paths[n] if paths else "%s/%d" % (base, n)
        GEN[0] = b["type"] in ("proof", "beliefs", "hats")
        if GEN[0]:
            b = expand(b)  # generated copy has no data pointer (GEN), so the tuner leaves it alone
        t = b["type"]
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
        elif t == "timeline":  # dated releases on one track: the Week One stepper molecule, vertical
            out.append('<ol class="tb-tl">%s</ol>' % "".join('<li class="tb-tl-i"><p class="section-label tb-tl-d">%s</p><p class="tb-tl-t">%s</p></li>' % (
                md(d, "%s/rows/%d/0" % (p, i)), md(x, "%s/rows/%d/1" % (p, i))) for i, (d, x) in enumerate(b["rows"])))
        elif t == "callout":
            out.append('<p class="callout"><b>%s</b>%s</p>' % (md(b["lead"], p + "/lead"), md(b["text"], p + "/text")))
        elif t == "list":
            tag = "ol" if b.get("ordered") else "ul"
            out.append('<%s class="tb-list">%s</%s>' % (tag, "".join("<li>%s</li>" % md(it, "%s/items/%d" % (p, i)) for i, it in enumerate(b["items"])), tag))
    GEN[0] = False
    if TUNE[0] and base and len(out) > 1:  # tune copy only: each block carries its pointer so the tuner can reorder it
        out = ['<div data-blk="%s/%d">%s</div>' % (base, n, h) for n, h in enumerate(out)]
    return "\n".join(out)


def r_fold(s, horizons, p=""):
    sid = s["id"]
    op = "true" if s.get("open") else "false"
    hid = "" if s.get("open") else " hidden"
    tag = '<span class="tb-tag">%s</span>' % md(s["tagline"], p + "/tagline") if s.get("tagline") else ""
    return ('<section class="tb-fold" id="%s"><h2 class="tb-h2"><button type="button" class="tb-fold-btn" aria-expanded="%s" aria-controls="%s-body">'
            '<span><span class="tb-fold-t">%s</span>%s</span></button></h2>'
            '<div class="tb-fold-body" id="%s-body"%s>%s</div></section>') % (sid, op, sid, md(s["title"], p + "/title"), tag, sid, hid, r_blocks(s["blocks"], horizons, 3, p + "/blocks"))


def r_overview(d):
    o = d["overview"]
    h = "".join('<span class="hl">%s</span>' % md(nbh(x), "/overview/headline/%d" % i) for i, x in enumerate(o["headline"]))
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
    lk = o.get("lockup")
    if lk:  # kit 71 proof lockup: kicker, one panel of proofs, closer; replaces the lede and the fact tiles
        cells = "".join('<li class="plk-cell"><span class="plk-lab">%s</span> <span class="plk-fig">%s</span> <span class="plk-cap">%s</span></li>' % (
            md(t["k"], "/overview/tiles/%d/k" % i), md(t["v"], "/overview/tiles/%d/v" % i), md(t["note"], "/overview/tiles/%d/note" % i)) for i, t in enumerate(o["tiles"]))
        proof = '<div class="plk">%s<ul class="plk-cells" aria-label="At a glance">%s</ul>%s</div>' % (
            ('<p class="plk-kick">%s</p>' % md(lk["kicker"], "/overview/lockup/kicker")) if lk.get("kicker") else "", cells,
            ('<p class="plk-close">%s</p>' % md(lk["closer"], "/overview/lockup/closer")) if lk.get("closer") else "")
    else:
        proof = '<div class="ftiles-c"><ul class="ftiles is-4" aria-label="At a glance">%s</ul></div>' % tiles
    out = ('<div id="pane-ov" class="tb-pane" role="tabpanel" aria-labelledby="t-ov">\n<h1 class="tb-h1">%s</h1>\n%s%s%s'
            '%s\n'
            '%s'
            '%s<div class="tb-expand%s"><button type="button" class="tb-btn" id="tb-expand" aria-pressed="false">Expand all</button></div>\n'
            '<div class="tb-folds">%s</div>\n</div>') % (h, (('<p class="tb-byline">%s</p>\n' % md(o["byline"], "/overview/byline")) if o.get("byline") else "") + ("" if o.get("bites_at") in ("end", "top") else r_bites(o)), ('<h2 class="tb-sub">%s</h2>\n' % md(o["subhead"], "/overview/subhead")) if o.get("subhead") else "", ('<p class="tb-lede">%s</p>\n' % "".join('<span class="ln">%s</span>' % md(nbh(x), "/overview/lede/%d" % i) for i, x in enumerate(o["lede"]))) if o.get("lede") else "",
         proof, go, cr,
         " solo" if len(o["sections"]) < 2 else "", folds)
    if o.get("receipt"):  # the proof object: one real dated call, above the tiles
        r = o["receipt"]
        ask = ""
        if r.get("ask"):
            link = ('<a class="rcpt-mail" href="%s">%s</a>' % (e(r["ask_href"]), e(r.get("ask_label") or r["ask_href"].replace("mailto:", "")))) if r.get("ask_href") else ""
            ask = '<p class="rcpt-ask">%s %s</p>\n' % (md(r["ask"], "/overview/receipt/ask"), link)
        card = ask + ('<section class="rcpt" aria-labelledby="rcpt-claim"><p class="rcpt-meta"><span>%s</span><span>Written %s</span><span>Resolves %s</span></p>'
                '<p class="rcpt-claim" id="rcpt-claim">%s%s</p><dl class="rcpt-rows"><dt>Kill it if</dt><dd>%s</dd><dt>Status</dt><dd>%s</dd>%s</dl></section>\n%s') % (
            md(r["kind"], "/overview/receipt/kind"), md(r["written"], "/overview/receipt/written"), md(r["resolves"], "/overview/receipt/resolves"),
            ('<span class="rcpt-odds">%s</span> ' % md(r["odds"], "/overview/receipt/odds")) if r.get("odds") else "",
            md(r["claim"], "/overview/receipt/claim"), md(r["kill"], "/overview/receipt/kill"), md(r["status"], "/overview/receipt/status"),
            ('<dt>Last resolved</dt><dd>%s</dd>' % md(r["last"], "/overview/receipt/last")) if r.get("last") else "", "")
        assert proof in out
        out = out.replace(proof, card + proof, 1)
    if o.get("bites_at") == "top" and o.get("bites"):  # quote first, a rule, then the headline (Zach, header option B, 2026-11-13)
        h1 = '<h1 class="tb-h1">'
        assert out.count(h1) == 1
        out = out.replace(h1, r_bites(o).replace('class="sb', 'class="sb is-top', 1) + '<hr class="tb-hd-rule">\n' + h1, 1)
    if o.get("bites_at") == "end" and o.get("bites"):  # evidence first, then what colleagues say
        assert out.endswith("</div>\n</div>")
        out = out[:-len("</div>")] + r_bites(o) + "</div>"
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
        # each unit is a fold, the overview's pattern: first open unless the data says otherwise; Expand all once there are two or more
        def unit_fold(k, u):
            sid = "%s-%s" % (tid, re.sub(r"[^a-z0-9]+", "-", u["title"].lower()).strip("-"))
            return r_fold(dict(u, id=sid, open=u.get("open", k == 0)), horizons, "%s/units/%d" % (p, k))
        units = "\n".join(unit_fold(k, u) for k, u in enumerate(t["units"]))
        exp = '<div class="tb-expand"><button type="button" class="tb-btn" id="tb-expand" aria-pressed="false">Expand all</button></div>\n' if len(t["units"]) > 1 else ""
        units = '%s<div class="tb-folds">%s</div>' % (exp, units)
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
    return ('<div class="tb-navwrap"><nav class="shnav" id="shnav" aria-label="Pages" data-menu-below="%d"><span class="shnav-current" aria-hidden="true"></span><div class="shnav-tabs" id="viewtabs">%s</div>%s'
            '<button type="button" class="shnav-menu" aria-expanded="false" aria-controls="viewtabs" aria-label="Go to a page"><span></span></button></nav></div>') % (stack_below(d), tabs, r_name(d))


def r_nav(d):
    tabs = ['<button type="button" class="shnav-tab" role="tab" id="t-ov" aria-controls="pane-ov" data-target="pane-ov" aria-selected="true" aria-current="true">%s</button>' % md(d["overview"]["label"])]
    for t in d["tabs"]:
        tabs.append('<button type="button" class="shnav-tab" role="tab" id="t-%s" aria-controls="pane-%s" data-target="pane-%s" aria-selected="false" tabindex="-1">%s%s</button>' % (
            t["id"], t["id"], t["id"], md(t["label"]), ('<span class="shnav-pill">%s</span>' % md(t["rank"])) if t.get("rank") else ""))
    return ('<div class="tb-navwrap"><nav class="shnav" id="shnav" aria-label="Sections" data-menu-below="%d"><span class="shnav-current" aria-hidden="true"></span><div class="shnav-tabs" id="viewtabs" aria-label="View">%s</div>%s'
            '<button type="button" class="shnav-menu" aria-expanded="false" aria-controls="viewtabs" aria-label="Jump to a section"><span></span></button></nav></div>') % (stack_below(d), "".join(tabs), r_name(d))


def r_name(d):
    """The author's name, large, at the right end of the tab row (replaces the From line in the meta strip)."""
    if not d.get("masthead"):
        return ""
    sub = ('<span class="tb-name-sub">%s</span>' % md(d["masthead_sub"], "/masthead_sub")) if d.get("masthead_sub") else ""
    return '<p class="tb-name"><span class="tb-name-main">%s</span>%s</p>' % (md(d["masthead"], "/masthead"), sub)


def stack_below(d):
    """Width below which the tabs fold into the menu and the roles stack (burger at 900px and down, the myAlly breakpoint; data may move it)."""
    return int(d.get("stack_below", 901))


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
    meta = ('<dl class="tb-meta"><div class="opt"><dt>Prepared for</dt><dd>%s</dd></div>%s'
            '%s%s</dl>') % (
        md(m["prepared_for"]), "" if d.get("masthead") else '<div><dt>From</dt><dd>%s</dd></div>' % md(m["from"]),
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
    # Inter and JetBrains Mono from Google Fonts, the design-system reference faces (Zach, 2026-11-12); SF Pro / system-ui is the fallback
    fonts = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
             '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600;700%s&display=swap">\n') % ("&family=Newsreader:ital,wght@1,400" if d.get("overview", {}).get("bites_at") == "top" else "")
    head = ('<title>%s</title>\n<meta name="robots" content="noindex, nofollow">\n%s%s\n<style>\n%s</style>\n') % (e(title), fonts, head_js, css)
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


def bad_hrefs(html_):
    """Link targets carrying a non-ASCII character (a U+2011 no-wrap hyphen, a smart quote): each one is a dead link."""
    return [h for h in re.findall(r'href="([^"]*)"', html_) if any(ord(c) > 127 for c in h)]


def outputs(d, out, artifact=False):
    """Every file one data file produces: {path: html}. Pages mode adds one file per role beside the overview."""
    res = _outputs(d, out, artifact)
    dead = [(p, h) for p, x in res.items() for h in bad_hrefs(x)]
    if dead:
        for p, h in dead:
            print("✖ non-ASCII link target in %s: %s" % (os.path.basename(p) or "page", h))
        raise SystemExit(1)
    return res


def _outputs(d, out, artifact=False):
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
    pt.refuse_public(out)
    TUNE[:] = [True, re.sub(r"\.html$", "", os.path.basename(out))]
    pt.TUNE[0] = True
    try:
        d = json.load(open(path, encoding="utf-8"))
        res = outputs(d, out)
    finally:
        TUNE[:] = [False]
        pt.TUNE[0] = False
    for f, h in res.items():
        pt.tune_write(h, f, stack_below(d), "/stack_below")
    return res


def apply_patch(data_path, patch_paths, version=None):
    """The tuner's exports back to source: text and the breakpoint to the data file, tokens and wrapping to shell.css."""
    return pt.apply(patch_paths if isinstance(patch_paths, list) else [patch_paths], [("json", data_path)],
                    style=("block", os.path.join(TDIR, "shell.css")), bp_ptr="/stack_below", bp_default=901, version=version, validate=validate)


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
    live = {"type": "proof", "groups": [{"label": "x", "ids": ["no-such-claim"]}]}
    x = copy.deepcopy(base); x["tabs"][0]["units"][0]["blocks"].append(live); cases.append(("proof block cites a missing claim", x, "not in runtime/specs/proof-claims.json"))
    x = copy.deepcopy(base); x["tabs"][0]["units"][0]["blocks"].append({"type": "hats", "rows": [{"hat": "h", "text": "t", "ids": ["outage"]}]}); cases.append(("hat cites a third-person claim", x, "third person"))
    x = copy.deepcopy(base); x["tabs"][0]["units"][0]["blocks"].append({"type": "beliefs", "label": "x", "ids": ["F1"]}); cases.append(("belief not cleared for the public", x, "not cleared"))
    x = copy.deepcopy(base); x["overview"]["tiles"][0]["v"] = "{no_such_count}"; cases.append(("unknown count token", x, "unknown token"))
    ok = True
    for name, d, want in cases:
        errs = validate(d)
        hit = any(want in er for er in errs)
        print(("PASS " if hit else "FAIL ") + name)
        ok = ok and hit
    x = copy.deepcopy(base); x["overview"]["headline"][0] = "[a-b](https://x.example/how-to-x) read-me"
    h = render(x, True, "ov") if x.get("pages") else render(x, True)
    hit = not bad_hrefs(h) and "how-to-x" in h and bool(bad_hrefs('<a href="https://x.example/how\u2011to">'))
    print(("PASS " if hit else "FAIL ") + "no-wrap hyphens stay out of link targets, and the guard catches one")
    ok = ok and hit
    good = not validate(base)
    print(("PASS " if good else "FAIL ") + "the committed data is valid")
    return 0 if ok and good else 1


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("data", nargs="?")
    ap.add_argument("-o", "--out")
    ap.add_argument("--artifact")
    pt.add_args(ap)
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
        apply_patch(a.data, a.apply, a.version)
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
