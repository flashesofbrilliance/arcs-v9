#!/usr/bin/env python3
"""
forge_counterpart.py -- deterministic generator for the counterpart artifact family.

Reads ONE forge SSOT (runtime/recoil/generated/<name>-forge.json), the synthesis of the two
seeds (enriched-profile scan + call transcript), and renders the 4-surface family:

  <name>.html          landing / one door (ungated)     surface A
  <name>-recoil.html   the loop, run on their own call  surface B
  <name>-codex.html    one decision, five altitudes     surface C  (+ presentation mode)
  <name>-demo.html     meta-cognitive inference ledger  surface D  (data-driven + JSON export)

Shared CSS/JS live in partials/ (single source of truth). This script inlines them, substitutes
{{PLACEHOLDER}} tokens, and emits self-contained pages. Same input -> same output, every time.

Mirrors the SSOT->render discipline of scripts/recoil_brief.py. Inline styles only; zero em-dashes;
noindex; pw-gate = counterpart first name; the fence held per meta.fence.

Usage:
  python scripts/forge_counterpart.py --data runtime/recoil/generated/<name>-forge.json
  python scripts/forge_counterpart.py --data <f> --surface recoil --stdout
  python scripts/forge_counterpart.py --data <f> --out-dir public
"""
import argparse, json, os, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PARTIALS = os.path.join(ROOT, "partials")

FORGE_SCHEMA_DOC = """forge SSOT schema (see partials/README.md):
  meta:     {id,name,counterpart,first_name,company,role,call_date,call_label,consent,
             seed_profile,seed_recoil,fence(tight|standard|loose),gate_password}
  landing:  {eyebrow,title,sub,onramp[{order,chip,chip_kind,title,what,why,unlocks,href}],
             felt_value{h2,intro,pillars[{title,text}]},offer{h2,text},studio{h2,text}}
  recoil:   {header{eyebrow,title,sub},onramp_card{h2,p[]},loop_steps[{n,title,tag,filled}],
             ex_ante{h2,fields[{label,value}]},said[{speaker,label,quote}],
             receipt_closed{h2,fields[]},felt_value{...},offer{...}}
  codex:    {header{...},sections[{id,n,k,shl,lede,deeper[]}],
             altitudes[{name,role,color,line}],said[],fence_card{h2,p[]}}
  demo:     {header{...},controls_note,reads[{band(pub|res),conclusion,confidence,conviction,
             clue,inference,source,disclosure}],beliefs[{label,moved_by,points[{t,note,conf}]}]}
"""

# ---------------------------------------------------------------------------
# partials + escaping
# ---------------------------------------------------------------------------
_CACHE = {}

def partial(name):
    if name not in _CACHE:
        with open(os.path.join(PARTIALS, name)) as f:
            _CACHE[name] = f.read()
    return _CACHE[name]

def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

EMDASH = "—"
HBAR = "―"

def _assert_no_emdash(html, surface):
    if EMDASH in html or HBAR in html:
        raise SystemExit(f"forge: em-dash found in rendered {surface} surface (violates project rule). "
                         "Fix the SSOT content, not the renderer.")

# ---------------------------------------------------------------------------
# head / gate / foot
# ---------------------------------------------------------------------------
MARKER = "<!-- forged by scripts/forge_counterpart.py from one SSOT; do not hand-edit -->"

def head(meta, title, css_parts, gated, export_file=None):
    css = partial("tokens.css") + partial("base.css") + "".join(css_parts)
    if gated:
        css += partial("gate.css")
    out = [f'<!DOCTYPE html>{MARKER}<html lang="en"><head><meta charset="utf-8">',
           '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
           '<meta name="robots" content="noindex, nofollow">',
           f'<title>{esc(title)}</title>',
           f'<style>{css}</style>',
           '<script defer src="/_vercel/insights/script.js"></script>',
           '</head><body>']
    if gated:
        out.append('<div id="pw-gate"><div class="pw-label">ARCS &#183; Private Brief</div>'
                   '<input id="pw-input" class="pw-input" type="password" placeholder="password" autocomplete="off"></div>')
    return "".join(out)

def gate_script(meta, surface):
    key = f'{meta["id"]}-{surface}-auth'
    pw = (meta.get("gate_password") or meta.get("first_name", "")).lower()
    js = partial("gate.js").replace("{{GATE_KEY}}", key).replace("{{GATE_PW}}", pw)
    return f"<script>{js}</script>"

def foot(meta, extra_scripts, gated, surface, dwell=True):
    parts = ['<div class="stamp">ARCS &#183; generated from one source record &#183; '
             f'{esc(meta.get("counterpart",""))}</div>', "</div>"]
    for s in extra_scripts:
        parts.append(s)
    if dwell:
        parts.append(f"<script>{partial('dwell.js')}</script>")
    if gated:
        parts.append(gate_script(meta, surface))
    parts.append("</body></html>")
    return "".join(parts)

# ---------------------------------------------------------------------------
# shared component render helpers (emit HTML using the partial CSS classes)
# ---------------------------------------------------------------------------
def header_cluster(h):
    return (f'<div><div class="eyebrow">{esc(h["eyebrow"])}</div><h1>{esc(h["title"])}</h1>'
            f'<div class="sub">{esc(h["sub"])}</div></div><div class="rule"></div>')

def said_block(s):
    them = "them" if s.get("speaker") == "counterpart" else ""
    return (f'<div class="said {them}"><div class="qk">{esc(s["label"])}</div>'
            f'<div class="qv">"{esc(s["quote"])}"</div></div>')

def receipt_card(block):
    body = "".join(f'<div class="ck" style="font-family:var(--mono);font-size:9px;'
                   f'letter-spacing:0.1em;text-transform:uppercase;color:var(--dimmed);margin-top:12px;">'
                   f'{esc(f["label"])}</div>'
                   f'<div style="font-size:13.5px;line-height:1.55;color:var(--text);">{esc(f["value"])}</div>'
                   for f in block["fields"])
    return f'<div class="card"><h2>{esc(block["h2"])}</h2>{body}</div>'

def felt_value(fv):
    pills = "".join(f'<li><span class="dot c"></span><div><strong>{esc(p["title"])}.</strong> '
                    f'{esc(p["text"])}</div></li>' for p in fv["pillars"])
    intro = f'<p style="margin-bottom:14px;">{esc(fv["intro"])}</p>' if fv.get("intro") else ""
    return f'<div class="card orient"><h2>{esc(fv["h2"])}</h2>{intro}<ul class="plain">{pills}</ul></div>'

def offer_card(o):
    return f'<div class="card pilot"><h2>{esc(o["h2"])}</h2><p>{esc(o["text"])}</p></div>'

def prose_card(block, klass="card"):
    ps = "".join(f"<p>{esc(p)}</p>" for p in block["p"])
    return f'<div class="{klass}"><h2>{esc(block["h2"])}</h2>{ps}</div>'

# ---------------------------------------------------------------------------
# surface A: landing (ungated one door)
# ---------------------------------------------------------------------------
def render_landing(data):
    meta, L = data["meta"], data["landing"]
    out = [head(meta, f'For {meta["first_name"]}, start here', [], gated=False), '<div class="page">',
           header_cluster({"eyebrow": L["eyebrow"], "title": L["title"], "sub": L["sub"]})]
    # onramp cards (the ordered navigation to the other 3 surfaces)
    for step in L["onramp"]:
        chip_color = "var(--green)" if step.get("chip_kind") == "start" else "var(--cyan)"
        out.append(
            f'<a href="{esc(step["href"])}" style="text-decoration:none;color:inherit;">'
            f'<div class="card" style="display:flex;flex-direction:column;gap:8px;">'
            f'<div style="display:flex;justify-content:space-between;align-items:center;">'
            f'<span style="font-family:var(--mono);font-size:11px;font-weight:700;color:var(--dimmed);">{esc(step["order"])}</span>'
            f'<span style="font-family:var(--mono);font-size:9px;font-weight:700;letter-spacing:0.08em;'
            f'text-transform:uppercase;color:{chip_color};border:1px solid {chip_color};border-radius:6px;padding:3px 8px;">{esc(step["chip"])}</span></div>'
            f'<div style="font-size:16px;font-weight:600;">{esc(step["title"])}</div>'
            f'<div style="font-size:13.5px;color:var(--muted);line-height:1.5;">{esc(step["what"])}</div>'
            f'<div style="font-size:13px;color:var(--text);line-height:1.5;"><strong>Why:</strong> {esc(step["why"])}</div>'
            f'<div style="font-family:var(--mono);font-size:10px;color:var(--cyan);margin-top:2px;">{esc(step["unlocks"])} &#8594;</div>'
            f'</div></a>')
    out.append(felt_value(L["felt_value"]))
    out.append(offer_card(L["offer"]))
    out.append(prose_card({"h2": L["studio"]["h2"], "p": [L["studio"]["text"]]}))
    html = "".join(out) + foot(meta, [], gated=False, surface="landing")
    _assert_no_emdash(html, "landing")
    return html

# ---------------------------------------------------------------------------
# surface B: recoil (the loop on their own call)
# ---------------------------------------------------------------------------
def render_recoil(data):
    meta, R = data["meta"], data["recoil"]
    subnav = ('<nav class="subnav"><a href="#what">what</a><a href="#loop">the loop</a>'
              '<a href="#exante">ex-ante</a><a href="#closed">scored</a><a href="#offer">offer</a></nav>')
    out = [head(meta, "The engine, run on our call", [], gated=True), '<div class="page">',
           header_cluster(R["header"]), subnav,
           f'<div id="what">{prose_card(R["onramp_card"], "card orient")}</div>']
    # the 6-step loop
    steps = "".join(
        f'<li><span class="dot {"c" if s.get("filled") else "g"}"></span>'
        f'<div><strong>{esc(s["n"])}. {esc(s["title"])}.</strong> '
        f'<span style="color:var(--dimmed);font-family:var(--mono);font-size:11px;">{esc(s["tag"])}</span></div></li>'
        for s in R["loop_steps"])
    out.append(f'<div class="sec-label" id="loop">The loop</div>'
               f'<div class="card"><h2>Six steps, one of them shown on you</h2><ul class="plain">{steps}</ul></div>')
    out.append(f'<div id="exante">{receipt_card(R["ex_ante"])}</div>')
    for s in R.get("said", []):
        out.append(said_block(s))
    out.append(f'<div id="closed">{receipt_card(R["receipt_closed"])}</div>')
    out.append(felt_value(R["felt_value"]))
    out.append(f'<div id="offer">{offer_card(R["offer"])}</div>')
    scripts = [f"<script>{partial('scrollspy.js')}</script>"]
    html = "".join(out) + foot(meta, scripts, gated=True, surface="recoil")
    _assert_no_emdash(html, "recoil")
    return html

# ---------------------------------------------------------------------------
# surface C: codex (five altitudes + presentation mode)
# ---------------------------------------------------------------------------
def render_codex(data):
    meta, C = data["meta"], data["codex"]
    nav_items = "".join(f'<a href="#{esc(s["id"])}">{esc(s["id"])}</a>' for s in C["sections"])
    out = [head(meta, "One decision, five altitudes", [partial("codex.css"), partial("present.css")], gated=True),
           '<div class="page">', header_cluster(C["header"]),
           f'<nav class="subnav">{nav_items}<a href="#alt">altitudes</a></nav>']
    for s in C["sections"]:
        deeper = "".join(f'<div class="card">{esc(p)}</div>' for p in s.get("deeper", []))
        det = f'<details class="deeper"><summary></summary>{deeper}</details>' if deeper else ""
        out.append(
            f'<section class="sec"><div class="seclead" id="{esc(s["id"])}">'
            f'<div class="n">{esc(s["n"])}</div><span class="k">{esc(s["k"])}</span></div>'
            f'<h2 class="shl">{esc(s["shl"])}</h2><p class="lede">{esc(s["lede"])}</p>{det}</section>')
    # altitude cards
    out.append('<div class="sec-label" id="alt">Five altitudes</div>')
    for a in C["altitudes"]:
        out.append(
            f'<div class="alt"><div class="bar" style="background:{a["color"]};"></div>'
            f'<div class="atop"><span class="aname">{esc(a["name"])}</span>'
            f'<span class="arole">{esc(a["role"])}</span></div>'
            f'<div class="aline">{esc(a["line"])}</div></div>')
    for s in C.get("said", []):
        out.append(said_block(s))
    if C.get("fence_card"):
        out.append(prose_card(C["fence_card"], "card fence"))
    # presentation-mode overlay + trigger
    out.append('<button id="present-btn">Present</button>'
               '<div id="present"><div class="pn"></div><div class="ph"></div><div class="pl"></div>'
               '<div class="phint">arrow keys to move &#183; G to go deeper &#183; Esc to exit</div>'
               '<div class="pbar"><button class="pbtn" data-a="prev">Prev</button>'
               '<button class="pbtn" data-a="deeper">Go deeper</button>'
               '<button class="pbtn" data-a="next">Next</button><span class="pcount"></span></div></div>')
    scripts = [f"<script>{partial('present.js')}</script>", f"<script>{partial('scrollspy.js')}</script>"]
    html = "".join(out) + foot(meta, scripts, gated=True, surface="codex")
    _assert_no_emdash(html, "codex")
    return html

# ---------------------------------------------------------------------------
# surface D: demo (data-driven inference ledger + JSON export)
# ---------------------------------------------------------------------------
def render_demo(data):
    meta, D = data["meta"], data["demo"]
    # the DATA object the ledger.js reads (SSOT subset -> the export payload)
    payload = {"meta": {"counterpart": meta["counterpart"], "company": meta["company"],
                        "call_date": meta["call_date"], "generated_by": "forge_counterpart.py"},
               "reads": D["reads"], "beliefs": D.get("beliefs", [])}
    out = [head(meta, "How I read you, and how sure I am",
                [partial("ledger.css"), partial("codex.css")], gated=True),
           '<div class="page">', header_cluster(D["header"])]
    note = f'<p style="font-size:13px;color:var(--muted);margin-bottom:6px;">{esc(D["controls_note"])}</p>' \
        if D.get("controls_note") else ""
    out.append(note)
    out.append('<div class="controls"><div class="seg" id="bandseg">'
               '<button class="on" data-band="pub">Public band</button>'
               '<button data-band="res">Reserved band</button></div>'
               '<button class="exp" id="expand">expand all</button>'
               '<button class="exp" id="export">export JSON</button></div>')
    out.append('<div id="ledger"></div>')
    out.append('<div class="sec-label">How a belief moved</div><div id="beliefs"></div>')
    export_file = f'{meta["first_name"].lower()}-reads.json'
    ledger_js = partial("ledger.js").replace("{{EXPORT_FILE}}", export_file)
    data_js = "var DATA=" + json.dumps(payload) + ";"
    scripts = [f"<script>{data_js}</script>", f"<script>{ledger_js}</script>"]
    html = "".join(out) + foot(meta, scripts, gated=True, surface="demo")
    _assert_no_emdash(html, "demo")
    return html

# ---------------------------------------------------------------------------
RENDERERS = {"landing": render_landing, "recoil": render_recoil,
             "codex": render_codex, "demo": render_demo}
# filename suffix per surface
SUFFIX = {"landing": "", "recoil": "-recoil", "codex": "-codex", "demo": "-demo"}


def main():
    ap = argparse.ArgumentParser(description="Deterministic counterpart artifact-family generator.")
    ap.add_argument("--data", required=True, help="path to <name>-forge.json SSOT")
    ap.add_argument("--surface", choices=["all"] + list(RENDERERS), default="all")
    ap.add_argument("--out-dir", default=os.path.join(ROOT, "public"))
    ap.add_argument("--stdout", action="store_true", help="print one surface to stdout (requires --surface)")
    ap.add_argument("--force", action="store_true",
                    help="overwrite an existing public file even if it was NOT forge-generated "
                         "(guards against clobbering a hand-authored live artifact)")
    a = ap.parse_args()

    with open(a.data) as f:
        data = json.load(f)
    name = data["meta"]["name"]
    surfaces = list(RENDERERS) if a.surface == "all" else [a.surface]

    if a.stdout:
        if a.surface == "all":
            sys.exit("--stdout requires a single --surface")
        sys.stdout.write(RENDERERS[a.surface](data))
        return

    written = []
    for s in surfaces:
        html = RENDERERS[s](data)
        path = os.path.join(a.out_dir, f"{name}{SUFFIX[s]}.html")
        # Guard: refuse to clobber an existing file that this generator did not create
        # (e.g. the hand-authored live yuri.html), unless --force. Re-rendering a previously
        # forged file is always allowed (it carries MARKER).
        if os.path.exists(path) and not a.force:
            with open(path) as ef:
                existing = ef.read(400)
            if MARKER not in existing:
                sys.exit(f"forge: refusing to overwrite non-forged file {os.path.relpath(path, ROOT)} "
                         "(no generator marker). Use a different --out-dir, rename meta.name, or pass --force.")
        with open(path, "w") as f:
            f.write(html)
        written.append(os.path.relpath(path, ROOT))
    for p in written:
        print(f"forged: {p}")


if __name__ == "__main__":
    main()
