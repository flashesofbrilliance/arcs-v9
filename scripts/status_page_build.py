#!/usr/bin/env python3
"""status_page_build: generate public/status.html (status.arcs.care) from a data file plus kit parts. Never hand-edit the page.

  tokens + kit    src/ui-kit/recoil-report/_tokens.css, inlined verbatim, plus the @prim blocks of kit 38 (wordmark), 39 (light remap) and 51 (display preferences)
  data            _ARTIFACTS/status/status.json   copy, the State of the Union card order, gate thresholds, the figure registry
  floor           _ARTIFACTS/status/floor.json    every number stamped from a source (git, the tracker, proof-claims.json); written by scripts/status_floor_emit.py
  parts           _ARTIFACTS/status/parts/*.frag  the section content, verbatim, with {{tokens}} where a figure is stamped
  layers          _ARTIFACTS/status/page.css (page), states.css (hover, focus-visible, pressed, disabled), light.css (light theme for page-only tokens and colors)
  scripts         explorer.js (build explorer), pulse.js (live fill from /api/pulse)

  python3 scripts/status_page_build.py             write public/status.html
  python3 scripts/status_page_build.py --check     exit 1 if the page differs from what the sources build (the drift check)
  python3 scripts/status_page_build.py --figures   print every stamped figure with its source, and the figures that have none
  python3 scripts/status_page_build.py --self-test

Stdlib only. Gate-threshold tokens read GATES from src/lib/pulse.ts, so the page and the API cannot disagree.
"""
import argparse, html, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SDIR = os.path.join(ROOT, "_ARTIFACTS/status")
KIT = os.path.join(ROOT, "src/ui-kit/recoil-report")
PAGE = os.path.join(ROOT, "public/status.html")
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import tabbed_brief_build as tb  # kit block reader, header controls (kit 51 markup) and the shell's display-preferences logic

KIT_PARTS = ["38-wordmark", "39-theme-toggle", "51-display-preferences"]
TOK = re.compile(r"\{\{([a-z_]+)\}\}")
CARD_ORDER = [  # State of the Union order (Zach, 2026-11-12): Awaiting a decision, Next, In progress, Shipped
    # (key in /api/pulse items, element suffix, title, sub, color var, bar class)
    ("decision", "block", "Awaiting a decision", "Pressure band · awaiting input", "red", "b-red"),
    ("open", "next", "Next", "Outer fog · orient only", "cyan", "b-cyan"),
    ("in-progress", "prog", "In progress", "Clarity ridge · building", "gold", "b-gold"),
    ("done", "ship", "Shipped", "Superionic · full resolution", "green", "b-green"),
]
BAR_LABEL = {"decision": "Awaiting a decision", "open": "Next", "in-progress": "In progress", "done": "Shipped"}


def e(s):
    return html.escape(str(s), quote=True)


def read(*p):
    return open(os.path.join(*p), encoding="utf-8").read()


def load():
    return json.load(open(os.path.join(SDIR, "status.json"), encoding="utf-8")), json.load(open(os.path.join(SDIR, "floor.json"), encoding="utf-8"))


def gates():
    t = read(ROOT, "src/lib/pulse.ts")
    m = re.search(r"GATES\s*=\s*\{\s*calibrationClosed:\s*(\d+),\s*goalMapDecisions:\s*(\d+)", t)
    if not m:
        raise SystemExit("status_page_build: GATES not found in src/lib/pulse.ts")
    return {"gate_cal": m.group(1), "gate_goal": m.group(2)}


def tokens_for(floor):
    asof = __import__("datetime").date.fromisoformat(floor["as_of"])
    t = {"day": str(floor["day"]), "commits": "{:,}".format(floor["commits"]), "asof": asof.strftime("%b ") + str(asof.day) + asof.strftime(", %Y"),
         "tempo_json": json.dumps(floor["tempo"], separators=(",", ":"))}
    t.update(gates())
    return t


def fill(s, tok, where):
    unknown = sorted(set(TOK.findall(s)) - set(tok))
    if unknown:
        raise SystemExit("status_page_build: unknown token(s) %s in %s; known: %s" % (unknown, where, ", ".join(sorted(tok))))
    return TOK.sub(lambda m: tok[m.group(1)], s)


def su_section(data, floor):
    """State of the Union: the four status cards in the approved order. Counts and items are the build-time floor; pulse.js
    overwrites them from /api/pulse (counts from byStatus, items from items) and the degraded tag shows when the read fails."""
    d = floor["debt"]
    cnt = {"ship": d["done"], "prog": d["in-progress"], "block": d["decision"], "next": d["open"]}
    total = sum(cnt.values())
    bar = "".join('<span class="%s" id="su-bar-%s" style="width:%.1f%%"></span>' % (c[5], c[1], cnt[c[1]] / total * 100) for c in CARD_ORDER)
    lab = "".join('<span><i style="background:var(--%s)"></i> %s · <b id="su-lab-%s">%d</b></span>' % (c[4], c[2], c[1], cnt[c[1]]) for c in CARD_ORDER)
    lead_parts = " · ".join('<span id="su-lead-%s">%d</span> %s' % (c[1], cnt[c[1]], BAR_LABEL[c[0]].lower() if c[0] != "decision" else "awaiting a decision") for c in CARD_ORDER)
    zones = ""
    for key, suf, title, sub, col, _ in CARD_ORDER:
        items = floor["items"].get(key, [])
        lis = "".join('<li class="su-zli">%s</li>' % e(x) for x in items) or '<li class="su-zli su-none">Nothing in this state.</li>'
        zones += ('<section class="su-zone" style="--zc:var(--%s);" aria-labelledby="su-zn-%s"><div class="su-zone-h"><h2 class="su-zone-name" id="su-zn-%s">%s</h2>'
                  '<span class="su-zone-count" id="su-z-%s">%d</span></div><div class="su-zone-sub">%s</div><ul class="su-zl" id="su-items-%s">%s</ul></section>\n' % (col, suf, suf, title, suf, cnt[suf], sub, suf, lis))
    asof = __import__("datetime").date.fromisoformat(floor["as_of"])
    return ('  <!-- 01 STATE OF THE UNION (generated by scripts/status_page_build.py; edit _ARTIFACTS/status/status.json) -->\n'
            '  <div class="section">\n    <div class="section-head">\n      <div class="section-n">01</div>\n'
            '      <div class="section-label" style="color:var(--green);border-color:rgba(0,255,157,0.35);background:rgba(0,255,157,0.06);">STATE OF THE UNION</div>\n    </div>\n'
            '    <div class="section-title">%s</div>\n    <div class="section-body">\n'
            '      <p class="su-lead">%s <strong>%s</strong> (<span id="su-lead-total">%d</span> tracked).</p>\n'
            '      <div class="su-bar" role="img" aria-label="Distribution of tracked workstreams by status">%s</div>\n'
            '      <div class="su-barlabel">%s</div>\n'
            '      <span class="dg" id="dg-su">degraded · floor shown</span><div id="su-stamp" class="su-stamp">Counted from the issue tracker by status label · shipped is cumulative · as of %s</div>\n'
            '      <div class="su-zones">\n%s      </div>\n    </div>\n  </div>\n') % (
        e(data["su"]["title"]), e(data["su"]["lead"]), lead_parts, total, bar, lab, asof.strftime("%b ") + str(asof.day) + asof.strftime(", %Y"), zones)


def prefs_js():
    """The shell's display-preferences logic (theme switch, reading options, one saved object per page), sliced from the tabbed-brief shell."""
    js = read(tb.TDIR, "shell.js")
    a = js.index("/* header controls (kit 51)")
    b = js.index("\n  applyPrefs();\n", a) + len("\n  applyPrefs();")
    return ("(function () {\n  var doc = document.documentElement, KEY = %s, DEF = %s;\n  " % (json.dumps(DATA_KEY[0]), json.dumps(DATA_KEY[1]))) + js[a:b] + "\n})();"


DATA_KEY = ["", "dark"]
# The page's interactive components. Buttons get all four states; rows (click-to-open surfaces) get hover, focus-visible and pressed (a row is never disabled).
ROWS = [".section-head", ".ms.expandable", ".cad-col.design-win"]
INTERACTIVE = [".pulse-refresh", ".alt-btn", ".pres-btn", ".pres-bot", ".focus-btn", ".flow-expand", ".flow-lightbox-close", ".tele-tab", ".unlock-chip", ".ms-verify"] + ROWS


def render(data, floor):
    DATA_KEY[0], DATA_KEY[1] = data["storage_key"], data.get("default_theme", "dark")
    tok = tokens_for(floor)
    css = tb.tokens() + "\n" + "".join(tb.kit_block(p) for p in KIT_PARTS) + "\n".join(read(SDIR, f) for f in ("page.css", "states.css", "light.css"))
    pre = ("<script>(function(){var d=document.documentElement,s={};try{var r=localStorage.getItem('%s')||'';s=r.charAt(0)==='{'?JSON.parse(r):(r?{theme:r}:{})}catch(e){}"
           "d.setAttribute('data-theme',(s.theme||'%s')==='dark'?'dark':'light');var A={font:'data-font',size:'data-size',space:'data-space'};"
           "for(var k in A){if(s[k]&&s[k]!=='std')d.setAttribute(A[k],s[k])}})();</script>") % (data["storage_key"], data.get("default_theme", "dark"))
    top = ('<header class="st-top"><span class="wordmark st-brand"><span class="wa">ARCS</span><span class="wf">FIELD OS</span></span>'
           '<span class="st-live"><span class="st-dot" aria-hidden="true"></span>%s</span>%s</header>\n%s') % (e(data["top_line"]), tb.DPREFS_ROW, tb.dprefs_panel())
    parts = sorted(f for f in os.listdir(os.path.join(SDIR, "parts")) if f.endswith(".frag"))
    body = ""
    for f in parts:
        txt = read(SDIR, "parts", f)
        body += su_section(data, floor) if f.startswith("01-") else fill(txt, tok, f)
        body += "\n" if not body.endswith("\n\n") else ""
    scripts = "<script>\n%s\n</script>\n<script>\n%s</script>\n<script>\n%s</script>\n" % (prefs_js(), fill(read(SDIR, "explorer.js"), tok, "explorer.js"), read(SDIR, "pulse.js"))
    return ('<!DOCTYPE html>\n<!-- generated by scripts/status_page_build.py from _ARTIFACTS/status/ (status.json, floor.json, parts/, *.css, *.js); do not hand-edit -->\n'
            '<html lang="en" data-theme="%s">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n<meta name="color-scheme" content="dark light">\n'
            '<meta name="robots" content="noindex, nofollow">\n<title>%s</title>\n<meta name="description" content="%s">\n%s\n<style>\n%s</style>\n'
            '<link rel="preload" href="/fonts/inter-normal-100-900-latin-v1.woff2" as="font" type="font/woff2" crossorigin>\n%s</head>\n<body>\n\n<main class="page">\n\n%s\n%s\n</main>\n\n%s'
            '<script defer src="/_vercel/insights/script.js"></script>\n</body>\n</html>\n') % (e(data.get("default_theme", "dark")), e(data["doc_title"]), e(data["description"]), pre, css, read(SDIR, "fonts.frag"), top, body, scripts)


def validate(data, floor):
    errs = []
    if "—" in json.dumps(data, ensure_ascii=False) + json.dumps(floor, ensure_ascii=False):
        errs.append("em-dash in status.json or floor.json")
    for k in ("decision", "open", "in-progress", "done"):
        if k not in floor.get("items", {}):
            errs.append("floor.json items missing %r" % k)
        if k not in floor.get("debt", {}):
            errs.append("floor.json debt missing %r" % k)
    return errs


def build(write=True):
    data, floor = load()
    errs = validate(data, floor)
    out = render(data, floor)
    if "—" in re.sub(r"<style>.*?</style>", "", out, flags=re.S):  # the kit's token comments carry two, verbatim; the gate ignores CSS comments
        errs.append("em-dash in the built page")
    if errs:
        for x in errs:
            print("✖ " + x)
        raise SystemExit(1)
    if write:
        open(PAGE, "w", encoding="utf-8").write(out)
    return out


def check():
    want = build(write=False)
    have = open(PAGE, encoding="utf-8").read() if os.path.exists(PAGE) else ""
    if want != have:
        print("✖ public/status.html differs from its sources. Run python3 scripts/status_page_build.py (edit _ARTIFACTS/status/, never the page)")
        return 1
    print("✓ public/status.html matches _ARTIFACTS/status/")
    return 0


def figures():
    data, floor = load()
    print("STAMPED AT BUILD (scripts/status_floor_emit.py -> floor.json -> page)")
    for k, v in sorted(floor.get("sources", {}).items()):
        print("  %-22s %s" % (k, v))
    print("LIVE FROM /api/pulse (floor shown when degraded)")
    for k, v in data["figures"]["live"].items():
        print("  %-22s %s" % (k, v))
    print("NO SOURCE YET (hand-written on the page)")
    for k, v in data["figures"]["unsourced"].items():
        print("  %-22s %s" % (k, v))
    return 0


def self_test():
    data, floor = load()
    ok = True

    def case(name, cond):
        nonlocal ok
        print(("PASS " if cond else "FAIL ") + name)
        ok = ok and cond
    case("committed data builds clean", not validate(data, floor))
    try:
        fill("{{nope}}", tokens_for(floor), "t"); case("unknown token is refused", False)
    except SystemExit:
        case("unknown token is refused", True)
    html_ = render(data, floor)
    order = [html_.index('id="su-zn-%s"' % s) for s in ("block", "next", "prog", "ship")]
    case("cards ordered Awaiting, Next, In progress, Shipped", order == sorted(order))
    bad = json.loads(json.dumps(floor)); del bad["items"]["done"]
    case("a floor without every status is refused", bool(validate(data, bad)))
    bad = json.loads(json.dumps(data)); bad["su"]["lead"] += " — x"
    case("em-dash in the data is refused", bool(validate(bad, floor)))
    nums = re.findall(r"(\d+):\s*\"", re.search(r"PUBLIC_ITEMS: Record<number, string> = \{(.*?)\n\};", read(ROOT, "src/lib/pulse.ts"), re.S).group(1))
    case("no mapped issue number reaches the page", bool(nums) and not any(re.search(r"#%s\b|issues/%s\b" % (n, n), html_) for n in nums))
    sc = read(SDIR, "states.css") + read(SDIR, "page.css")  # a component may carry its own hover in page.css
    for state, needle in (("hover", ":hover"), ("focus-visible", ":focus-visible"), ("pressed", ":active"), ("disabled", ":disabled")):
        rules = " ".join(l for l in sc.split("\n") if needle in l)
        missing = [c for c in INTERACTIVE if c.split(" ")[0] not in rules and not (state == "disabled" and c in ROWS)]
        case("every interactive component has a %s state in states.css" % state, not missing or print("   missing:", missing))
    return 0 if ok else 1


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--figures", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    if a.check:
        return check()
    if a.figures:
        return figures()
    build()
    print("wrote public/status.html")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
