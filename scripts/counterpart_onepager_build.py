#!/usr/bin/env python3
"""counterpart_onepager_build: render a counterpart one-pager from the counterpart-onepager template plus a data file.

The page is rebuilt from the ui-kit levels, never hand-edited:
  atoms      src/ui-kit/recoil-report/_tokens.css, inlined verbatim
  molecules  kit @prim blocks 28 chip, 29 tile, 31 callout, 32 evidence ref, 33 led, 24 segmented control,
             39 theme toggle, pulled from the kit files at build time
  candidates shapes with one real case so far (headline-deck lockup, heard/check grid, case switcher,
             sans-value receipt table, depth checklist); their CSS lives here until a second page needs them
  template   counterpart-onepager in src/ui-kit/templates.json
  data       _ARTIFACTS/counterpart-onepager/<name>.json (copy is data; the fields are trusted authored HTML)

  python3 scripts/counterpart_onepager_build.py _ARTIFACTS/counterpart-onepager/brooks.json     write the page
  python3 scripts/counterpart_onepager_build.py --check                                        exit 1 if any page differs
                                                                                               or an outcome block is unsound
  python3 scripts/counterpart_onepager_build.py --receipt [data.json]                          print the ex-ante receipt template
  python3 scripts/counterpart_onepager_build.py DATA.json --tune OUT.html                      internal copy with the live editor
  python3 scripts/counterpart_onepager_build.py DATA.json --apply EXPORT [...]                 text and tokens back to DATA, rebuild
Stdlib only.
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import page_tune as pt  # noqa: E402  the shared --tune / --apply mechanics

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KIT = os.path.join(ROOT, "src/ui-kit/recoil-report")
DATA = os.path.join(ROOT, "_ARTIFACTS/counterpart-onepager")
SPECS = os.path.join(ROOT, "src/ui-kit/specimens")
PRIMS = ["28-chip", "29-tile", "31-callout", "32-evidence-ref", "33-led", "24-segmented-control"]


def prim(name):
    for f in os.listdir(KIT):
        if re.match(r"\d\d-.*\.html$", f):
            m = re.search(r"/\* @prim:begin %s \*/\n.*?/\* @prim:end %s \*/\n" % (name, name), open(os.path.join(KIT, f), encoding="utf-8").read(), re.S)
            if m:
                return m.group(0)
    raise SystemExit(f"kit primitive {name} has no @prim block")


def tokens():
    return open(os.path.join(KIT, "_tokens.css"), encoding="utf-8").read()


LAYOUT = """/* Page layer: non-signal aliases and spacing only. Palette and fonts inherit verbatim above. */
:root{--secondary:var(--text-secondary);--mono:var(--ds-font-mono);--sans:var(--ds-font-sans);--serif:var(--ds-font-display);--measure:640px;--fs-step:1.25rem;--fs-title:0.95rem;--sp-1:8px;--sp-2:16px;--sp-3:24px;--sp-4:40px;--sp-5:64px;--lh:1.6;}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
body{background:var(--bg);color:var(--text);font-family:var(--sans);font-size:var(--fs-body);line-height:var(--lh);padding:var(--sp-5) 20px 96px;-webkit-font-smoothing:antialiased;}
.page{max-width:var(--measure);margin:0 auto;display:flex;flex-direction:column;gap:var(--sp-5);}
section{display:flex;flex-direction:column;gap:var(--sp-2);}
p,li{max-width:none;text-wrap:pretty;}
"""

# Page roles (DESIGN.md: display, headline, title, body, label) and the hero, which composes kit tiles and a chip.
ROLES = """/* page roles (DESIGN.md: display, headline, title, body, label) */
h1{font-family:var(--sans);font-size:var(--fs-display);font-weight:700;letter-spacing:-0.02em;line-height:1.2;text-wrap:balance;}
.verdict{font-family:var(--serif);font-size:var(--fs-step);font-weight:500;line-height:1.45;color:var(--text);margin-top:var(--sp-3);}
.aside{color:var(--secondary);margin-top:var(--sp-2);}
.slabel{font-family:var(--sans);font-size:var(--fs-step);font-weight:600;letter-spacing:-0.01em;line-height:1.25;color:var(--text);text-wrap:balance;}
.card{background:var(--surface);border:1px solid var(--border);border-radius:var(--ds-r-md);padding:20px 22px;}
.tiles{margin-top:var(--sp-4);}
.tile .v{font-size:1.6rem;white-space:nowrap;}
.scorebar{display:flex;align-items:center;gap:10px 14px;flex-wrap:wrap;margin-top:var(--sp-2);}
.callout{max-width:none;}
.callout p{color:var(--text);font-size:var(--fs-step);line-height:1.45;margin-top:6px;}
footer p{color:var(--secondary);text-align:center;}
@media (max-width:640px){
  body{padding-top:var(--sp-4);}
  .page{gap:var(--sp-4);}
  .card{padding:18px 16px;}
  .tiles{grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;}
  .tile{padding:12px 10px;}
  .tile .v{font-size:1rem;white-space:nowrap;}
  .tile .k{letter-spacing:0.06em;}
}
"""

# Candidate: headline-plus-deck lockup (section heading with a full-width deck under it).
LOCKUP = """/* candidate: headline-deck lockup */
.lockup{display:flex;flex-direction:column;gap:6px;}
.lockup .deck{color:var(--secondary);text-wrap:pretty;}
"""

# Candidate: heard/check paired-row grid. On a phone the right header hides and each check row carries a prefix.
HEARD = """/* candidate: heard-check paired-row grid */
.hgrid{display:grid;grid-template-columns:1fr 1fr;column-gap:var(--sp-4);}
.hhead{font-family:var(--sans);font-size:var(--fs-title);font-weight:600;color:var(--secondary);padding-bottom:var(--sp-1);}
.hhead.c{color:var(--cyan);}
.hrow{display:contents;}
.hrow > div{padding:var(--sp-2) 0;border-top:1px solid var(--border);}
@media (max-width:640px){
  .hgrid{grid-template-columns:1fr;}
  .hhead.c{display:none;}
  .hrow > .hc{border-top:none;padding-top:0;}
  .hrow > .hc::before{content:"%s";font-weight:600;color:var(--cyan);}
}
"""


def case_css(n):
    """Candidate: case switcher. Kit 24 segmented control drives panels with radios and :checked, no script."""
    ids = range(1, n + 1)
    on = ",".join(f"#c{i}:checked ~ .panels .p{i}" for i in ids)
    lab = ",".join(f"#c{i}:checked ~ .seg label[for=c{i}]" for i in ids)
    foc = ",".join(f"#c{i}:focus-visible ~ .seg label[for=c{i}]" for i in ids)
    return f"""/* candidate: case switcher (24 segmented control with panels, pure CSS) */
.seg-wrap .panel{{display:none;}}
.seg-wrap .panels{{padding-top:var(--sp-3);min-height:7.5em;}}
.seg-wrap .case{{font-family:var(--sans);font-size:var(--fs-title);font-weight:600;color:var(--text);margin-bottom:4px;}}
.seg-wrap .panel p:not(.case){{color:var(--text-secondary);}}
.seg-wrap b{{font-weight:600;}}
.seg label{{font-size:var(--fs-body);}}
{on}{{display:block;}}
.seg-wrap .seg{{position:relative;}}
.vh{{position:absolute;opacity:0;pointer-events:none;width:1px;height:1px;}}
{lab}{{background:var(--cyan-bg);color:var(--text);box-shadow:inset 0 -2px 0 var(--cyan);}}
{foc}{{outline:2px solid var(--cyan);outline-offset:-2px;}}
@media (max-width:640px){{
  .seg label{{font-size:0.85rem;padding:10px 4px;white-space:nowrap;}}
}}
"""


# Candidate: sans-value receipt table (08 receipt table adapted: sans values for reading, the Three-Voice Rule).
RECEIPT = """/* candidate: sans-value receipt table (08-receipt-table organism, adapted: sans values for reading, Three-Voice Rule) */
.receipt-table{width:100%;background:var(--surface);border:1px solid var(--border);border-radius:var(--ds-r-md);overflow:hidden;border-collapse:collapse;}
.receipt-table tr{border-bottom:1px solid rgba(30,41,59,0.6);}
.receipt-table tr:last-child{border-bottom:none;}
.receipt-table td{padding:14px 18px;vertical-align:top;}
.td-key{font-family:var(--mono);font-size:var(--fs-label);font-weight:700;letter-spacing:0.14em;text-transform:uppercase;color:var(--secondary);width:28%;border-right:1px solid var(--border);line-height:1.5;}
.td-val{font-family:var(--sans);font-size:var(--fs-body);color:var(--text);line-height:1.6;text-wrap:pretty;}
.td-val ul{margin:0 0 0 1.1rem;display:flex;flex-direction:column;gap:6px;}
.proofrow{display:flex;align-items:center;gap:12px;margin-top:10px;flex-wrap:wrap;}
.prooflink{display:inline-block;padding:10px 0;color:var(--cyan);font-family:var(--mono);font-size:var(--fs-body);text-underline-offset:2px;}
@media (max-width:640px){
  .receipt-table tr{display:block;padding:14px 16px;}
  .receipt-table td{display:block;padding:0;border-right:none;width:auto;}
  .td-key{margin-bottom:6px;}
}
"""

# Candidate: depth checklist (a details disclosure holding a numbered criteria list; added items in gold).
DEPTH = """/* candidate: depth checklist */
details.depth{border-top:1px solid var(--border);border-bottom:1px solid var(--border);}
details.depth summary{cursor:pointer;list-style:none;padding:var(--sp-2) 0;font-family:var(--sans);font-size:var(--fs-title);font-weight:600;color:var(--secondary);display:flex;justify-content:space-between;gap:12px;}
details.depth summary::-webkit-details-marker{display:none;}
details.depth summary::after{content:"+";color:var(--cyan);}
details.depth[open] summary::after{content:"\\2212";}
details.depth summary:focus-visible{outline:2px solid var(--cyan);outline-offset:4px;}
.depth-body{padding:0 0 var(--sp-3);display:flex;flex-direction:column;gap:var(--sp-2);}
.depth-body > p{color:var(--secondary);}
ol.crit{list-style:none;}
ol.crit li{display:grid;grid-template-columns:2.2rem 1fr;gap:4px 12px;padding:10px 0;}
ol.crit li + li{border-top:1px solid var(--border);}
ol.crit .n{font-family:var(--mono);font-weight:700;color:var(--cyan);font-variant-numeric:tabular-nums;}
ol.crit li.add .n{color:var(--gold);}
ol.crit b{font-weight:600;}
"""

# Candidate: question-and-answer card (three questions the counterpart would ask, each an h3 and a paragraph).
QA = """/* candidate: question-and-answer card */
.qa{display:flex;flex-direction:column;gap:var(--sp-2);}
.qa h3{font-family:var(--sans);font-size:var(--fs-title);font-weight:600;line-height:1.35;color:var(--text);margin-bottom:6px;}
"""

# Candidate: icon theme button (sun and moon over kit 39's text button). Kit 39's toggle logic, its own label and markup.
ICON_BTN = """/* candidate: icon theme button over kit 39 */
.themebtn{justify-content:center;width:44px;height:44px;color:var(--secondary);border:1px solid var(--border);border-radius:999px;}
.themebtn[hidden]{display:none;}
.themebtn[data-next="light"] .i-moon,.themebtn[data-next="dark"] .i-sun{display:none;}
.themebtn:hover,.themebtn:focus-visible{color:var(--cyan);border-color:var(--cyan);text-decoration:none;}
"""
ICONS = '<svg class="i-sun" viewBox="0 0 24 24" width="20" height="20" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="12" cy="12" r="4.2"/><path d="M12 2.5v2.2M12 19.3v2.2M2.5 12h2.2M19.3 12h2.2M5.3 5.3l1.6 1.6M17.1 17.1l1.6 1.6M5.3 18.7l1.6-1.6M17.1 6.9l1.6-1.6"/></svg><svg class="i-moon" viewBox="0 0 24 24" width="20" height="20" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"><path d="M20 14.6A8.2 8.2 0 0 1 9.4 4a8.2 8.2 0 1 0 10.6 10.6z"/></svg>'
ICON_JS = """<script>(function(){var d=document.documentElement,b=document.getElementById('themebtn');if(!b)return;var mq=window.matchMedia?matchMedia('(prefers-color-scheme: light)'):null;function cur(){var t=d.getAttribute('data-theme');if(t)return t;return mq&&mq.matches?'light':'dark';}function label(){var n=cur()==='light'?'dark':'light';b.setAttribute('data-next',n);b.setAttribute('aria-label','Switch to '+n+' mode');b.title='Switch to '+n+' mode';}b.hidden=false;label();b.addEventListener('click',function(){var n=cur()==='light'?'dark':'light';d.setAttribute('data-theme',n);try{localStorage.setItem('{key}',n);}catch(e){}label();});if(mq&&mq.addEventListener)mq.addEventListener('change',label);})();</script>"""

# Candidate: US Letter print. Kit 39's print palette (light tokens), every case panel shown, the checklist opened.
# Paper is not a screen. Every size and gap is a kit token: in print 1rem = 11.5pt, so --fs-body is 10.5pt and the
# scale runs display, step, headline, body; gaps are --sp-1 (half and whole) and --sp-3. One family (sans), one
# accent (teal). One 6-column grid: halves for paired rows, thirds (label left, text across two) for the stats, the
# three questions, the ask and the checklist. Page 1 holds the hero through the three questions; the ask opens
# page 2; the footer is page 2's bottom margin box. Both pages share one set of margins.
PRINT = """/* Print: US Letter, two pages (one sheet, both sides). Kit tokens only, one family, one accent, one grid. */
@page{size:Letter;margin:0.45in 0.5in 0.6in;@bottom-left{content:"{footer}";font-family:var(--ds-font-sans);font-size:var(--fs-label);color:var(--text-secondary);vertical-align:top;padding-top:var(--sp-1);}}
@page:first{@bottom-left{content:none;}}
@media print{
html{font-size:11.5pt;}
body{padding:0;font-size:var(--fs-body);line-height:calc(var(--lh) - 0.27);-webkit-print-color-adjust:exact;print-color-adjust:exact;}
:root{--g:var(--sp-3);--gap:var(--sp-2);--half:calc(var(--sp-1) / 2);--third:calc((100% - 2 * var(--g)) / 3 + var(--g));}
.themebtn,.seg,.vh,footer,details.depth summary::after{display:none!important;}
p,li,h3,ol.crit .d{orphans:2;widows:2;}
.qa p,.panel p,ol.crit .d,.depth-body > p{text-wrap:wrap;}
.page{max-width:none;gap:var(--gap);}
section{gap:var(--sp-1);break-inside:avoid;}
h1{font-size:var(--fs-display);line-height:1.15;letter-spacing:-0.015em;}
.verdict{font-family:var(--sans);font-size:var(--fs-headline);font-weight:400;line-height:1.4;margin-top:var(--sp-1);}
.aside{color:var(--secondary);margin-top:var(--half);}
.slabel,details.depth summary{font-size:var(--fs-headline);font-weight:700;letter-spacing:-0.01em;line-height:1.25;color:var(--text);}
.lockup{gap:var(--half);}
.tiles{margin-top:var(--sp-1);gap:var(--g);grid-template-columns:repeat(3,1fr);}
.tile{background:linear-gradient(var(--text),var(--text)) top left / 100% 1.5pt no-repeat;border-width:0;border-radius:0;padding:var(--sp-1) 0 0;}
.tile .v{font-family:var(--sans);font-size:var(--fs-step);font-weight:700;line-height:1.2;color:var(--text);}
.tile .v.cyan{color:var(--cyan);}
.tile .k{font-family:var(--sans);font-size:var(--fs-body);letter-spacing:0;text-transform:none;color:var(--secondary);margin-top:0;}
.scorebar{margin-top:var(--sp-1);}
.chip,.chip.green{font-family:var(--sans);font-size:var(--fs-body);font-weight:700;letter-spacing:0;text-transform:none;color:var(--cyan);background:none;border-width:0;padding:0;border-radius:0;}
.card{background:none;border-width:0;border-radius:0;padding:0;box-shadow:none;}
.hgrid{column-gap:var(--g);}
.hhead{font-size:var(--fs-body);font-weight:700;color:var(--text);padding-bottom:var(--half);}
.hhead.c{color:var(--cyan);}
.hrow > div{padding:var(--half) 0;border-top:0.75pt solid var(--border);}
.seg-wrap .panels{display:grid;grid-template-columns:1fr 1fr;column-gap:var(--g);padding-top:0;min-height:0;}
.seg-wrap .panel{display:block!important;}
.seg-wrap .case{font-size:var(--fs-body);font-weight:700;margin-bottom:0;}
.seg-wrap .panel p:not(.case){color:var(--text);}
.qa{gap:var(--sp-1);}
.qa > div{display:grid;grid-template-columns:repeat(3,1fr);column-gap:var(--g);}
.qa h3{font-size:var(--fs-body);font-weight:700;line-height:inherit;margin:0;text-wrap:balance;}
.qa p{grid-column:2 / 4;}
.callout{break-before:page;margin-top:calc(-1 * var(--gap));display:grid;grid-template-columns:repeat(3,1fr);column-gap:var(--g);align-items:baseline;position:relative;background:none;border-width:0;border-radius:0;padding:var(--sp-2) 0 var(--sp-2);color:var(--text);}
.callout::before{content:"";position:absolute;inset:0 0 auto;height:1.5pt;background:var(--cyan);}
.callout b{font-family:var(--sans);font-size:var(--fs-body);font-weight:700;letter-spacing:0;text-transform:none;color:var(--cyan);margin:0;}
.callout p{grid-column:2 / 4;font-size:var(--fs-headline);line-height:1.4;margin:0;}
details.depth{border-width:0;margin-top:var(--sp-2);}
ol.crit b .p{display:none;}
details.depth::details-content{content-visibility:visible;display:block;}
details.depth summary{padding:0 0 var(--sp-1);display:block;}
.depth-body{padding:0;gap:var(--sp-1);}
.depth-body > p{color:var(--text);margin-left:var(--third);}
ol.crit{display:block;border-top:0.75pt solid var(--border);border-bottom:0.75pt solid var(--border);}
ol.crit li{grid-template-columns:repeat(3,1fr);column-gap:var(--g);padding:var(--sp-1) 0;break-inside:avoid;}
ol.crit li + li{border-top:0.75pt solid var(--border);}
ol.crit .t{display:contents;}
ol.crit .n{grid-area:1 / 1;font-family:var(--sans);font-weight:700;color:var(--cyan);font-variant-numeric:tabular-nums;}
ol.crit li.add .n{color:var(--cyan);}
ol.crit b{grid-area:1 / 1;padding-left:2.2em;font-weight:700;}
ol.crit .d{grid-area:1 / 2 / 2 / 4;}
.hrow > div,.callout,.tile{break-inside:avoid;}
.lockup,.slabel,.hhead,details.depth summary,.depth-body > p:first-child{break-after:avoid;}
h1,.slabel,details.depth summary{text-wrap:balance;}
a{color:var(--cyan);}
}
"""
PRINT_JS = """<script>(function(){var d=document.querySelector("details.depth");if(!d)return;var was;addEventListener("beforeprint",function(){was=d.open;d.open=true;});addEventListener("afterprint",function(){d.open=was;});if(matchMedia)matchMedia("print").addListener(function(m){if(m.matches)d.open=true;});})();</script>"""


def theme_js(key, icon=False):
    spec = json.load(open(os.path.join(SPECS, "theme-toggle.json"), encoding="utf-8"))
    return spec["head_js"].replace("{key}", key), (ICON_JS if icon else spec["tail_js"]).replace("{key}", key)


def widont(t):
    """Bind the last two words with a no-break space so a block never ends on a one-word line."""
    head, sep, tail = t.rpartition(" ")
    return head + "\u00a0" + tail if sep and "<" not in tail and len(tail) < 16 else t


def dot(t):
    """Wrap a label's closing period so print, where the label sits in its own column, can drop it."""
    return t[:-1] + '<span class="p">.</span>' if t.endswith(".") else t


def voice(v):
    return f' data-voice="{v}"' if v else ""


def lockup(s):
    deck = f'<p class="deck"{voice(s.get("deck_voice"))}>{s["deck"]}</p>' if s.get("deck") else ""
    return f'  <div class="lockup"><h2 class="slabel"{voice(s.get("heading_voice"))}>{s["heading"]}</h2>{deck}</div>\n'


def case_switcher(s):
    g, cs = s["group"], s["cases"]
    radios = "".join(f'<input type="radio" name="{g}" id="c{i}"{" checked" if i == 1 else ""} class="vh">' for i in range(1, len(cs) + 1))
    labels = "".join(f'<label for="c{i}">{c["label"]}</label>' for i, c in enumerate(cs, 1))
    panels = "".join(f'      <div class="panel p{i}"><p class="case">{c["case"]}</p><p>{widont(c["body"])}</p></div>\n' for i, c in enumerate(cs, 1))
    return (lockup(s) + '  <div class="card seg-wrap">\n'
            f"    {radios}\n"
            f'    <div class="seg" role="radiogroup" aria-label="{s["aria_label"]}">{labels}</div>\n'
            '    <div class="panels">\n' + panels + "    </div>\n  </div>\n")


def heard_check(s):
    rows = "".join(f'    <div class="hrow"><div class="hh"{voice(r.get("heard_voice"))}>{widont(r["heard"])}</div><div class="hc">{widont(r["check"])}</div></div>\n' for r in s["rows"])
    return (lockup(s) + '  <div class="hgrid">\n'
            f'    <div class="hhead">{s["left_head"]}</div><div class="hhead c">{s["right_head"]}</div>\n' + rows + "  </div>\n")


def receipt(s):
    rows = "".join(f'      <tr><td class="td-key">{r["key"]}</td><td class="td-val">{r["value"]}</td></tr>\n' for r in s["rows"])
    return lockup(s) + '  <table class="receipt-table">\n    <tbody>\n' + rows + "    </tbody>\n  </table>\n"


def qa(s):
    qs = "".join(f'    <div><h3{voice(q.get("voice"))}>{q["q"]}</h3><p>{widont(q["a"])}</p></div>\n' for q in s["questions"])
    return lockup(s) + '  <div class="card qa">\n' + qs + "  </div>\n"


SECTIONS = {"case-switcher": case_switcher, "heard-check": heard_check, "receipt": receipt, "qa": qa}


def build(d):
    kinds = [s["kind"] for s in d["sections"]]
    icon = d.get("theme_button") == "icon"
    cases = next((len(s["cases"]) for s in d["sections"] if s["kind"] == "case-switcher"), 0)
    prefix = next((s["mobile_prefix"] for s in d["sections"] if s["kind"] == "heard-check"), "")
    tuned = "".join(f"{k}:{v};" for k, v in d.get("tokens", {}).items())
    css = (tokens() + "\n" + LAYOUT + (f"/* page tokens, tuned (src/ui-kit/token-tuner.js) */\n:root{{{tuned}}}\n" if tuned else "")
           + "/* kit primitives, verbatim */\n" + "".join(prim(p) for p in PRIMS) + ROLES + LOCKUP
           + (HEARD % prefix if "heard-check" in kinds else "") + (case_css(cases) if cases else "")
           + (RECEIPT if "receipt" in kinds else "") + (QA if "qa" in kinds else "") + (DEPTH if d.get("depth") else "")
           + "/* Light mode: kit 39 theme toggle. Follows the OS unless the reader picks; kit tokens remap, kit primitives stay verbatim. */\n"
           + prim("39-theme-toggle") + (ICON_BTN if icon else "") + (PRINT.replace("{footer}", d["footer"].replace('"', '\\"')) if d.get("print") else ""))
    head_js, tail_js = theme_js(d["theme_key"], icon)
    if d.get("print") and d.get("depth"):
        tail_js += "\n" + PRINT_JS
    h = d["hero"]
    tiles = "".join(f'    <div class="tile"><div class="v{" " + t["tone"] if t.get("tone") else ""}">{t["value"]}</div><div class="k">{t["key"]}</div></div>\n' for t in h["tiles"])
    btn = (f'<button type="button" class="themebtn" id="themebtn" aria-label="Switch to light mode" title="Switch to light mode" hidden>{ICONS}</button>'
           if icon else '<button type="button" class="themebtn" id="themebtn" hidden>Light mode</button>')
    body = (f'<header>\n  {btn}\n'
            f'  <h1>{h["title"]}</h1>\n  <p class="verdict">{h["verdict"]}</p>\n  <p class="aside">{h["aside"]}</p>\n'
            '  <div class="tiles">\n' + tiles + "  </div>\n"
            f'  <div class="scorebar"><span class="chip {h["chip"]["tone"]}">{h["chip"]["text"]}</span></div>\n</header>\n\n')
    for s in d["sections"]:
        body += "<section>\n" + SECTIONS[s["kind"]](s) + "</section>\n\n"
    if d.get("ask"):
        body += f'<div class="callout"><b>{d["ask"]["label"]}</b><p>{d["ask"]["body"]}</p></div>\n\n'
    if d.get("depth"):
        dp = d["depth"]
        add = ' class="add"'
        items = "".join(f'  <li{add if i.get("added") else ""}><span class="n">{i["n"]}</span><span class="t"><b>{dot(i["title"])}</b> <span class="d">{widont(i["body"])}</span></span></li>\n' for i in dp["items"])
        body += (f'<details class="depth">\n<summary>{dp["summary"]}</summary>\n<div class="depth-body">\n  <p>{dp["intro"]}</p>\n'
                 '  <ol class="crit">\n' + items + "  </ol>\n" + (f'  <p>{dp["outro"]}</p>\n' if dp.get("outro") else "") + "</div>\n</details>\n\n")
    body += f'<footer><p>{d["footer"]}</p></footer>\n'
    return f"""<!DOCTYPE html>
<!-- @arcs-template: counterpart-onepager -->
<!-- @arcs-mode: persuade -->
<!-- generated by scripts/counterpart_onepager_build.py from the data file; edit the data, not this page -->
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="{d["robots"]}">
<title>{d["title"]}</title>
{head_js}
<style>
{css}</style>
</head>
<body>
<main class="page">

{body}
</main>
{tail_js}
</body>
</html>
"""


# Outcome fields (2026-11-09): an optional "outcome" block maps each claim the page makes to the parts that carry it,
# keyed to a backlog job, so a close can score claims against what the reader did. Never rendered.
CANDIDATES = {"lockup", "heard-check", "case-switcher", "receipt-sans", "qa-card", "depth-checklist"}
PAGE_PARTS = {"hero"}
BACKLOG = os.path.join(ROOT, "_QUEUE/induced-backlog.jsonl")


def resolve(d, path):
    cur = d
    for k in path.split("."):
        cur = cur[int(k)] if isinstance(cur, list) else cur[k]
    return cur


def backlog_row(job_id):
    key = job_id.split(":", 2)[-1]
    for line in open(BACKLOG, encoding="utf-8"):
        if line.strip() and json.loads(line).get("id") == key:
            return json.loads(line)
    return None


def validate(d):
    """Problems with the outcome block; empty when it is sound or absent."""
    o = d.get("outcome")
    if not o:
        return []
    bad = []
    if not o.get("job_id", "").startswith("job:backlog:") or not backlog_row(o["job_id"]):
        bad.append(f"job_id {o.get('job_id')!r} names no row in _QUEUE/induced-backlog.jsonl")
    blocks = {"hero"} | {f"sections.{i}" for i in range(len(d["sections"]))} | ({"ask"} if d.get("ask") else set()) | ({"depth"} if d.get("depth") else set())
    claimed = set()
    for c in o.get("claims", []):
        for p in c["parts"]:
            kind, _, name = p.partition(":")
            ok = (kind == "kit" and os.path.exists(os.path.join(KIT, name + ".html"))) or (kind == "candidate" and name in CANDIDATES) or (kind == "page" and name in PAGE_PARTS)
            if not ok:
                bad.append(f"{c['id']}: part {p!r} is not a kit file, a known candidate or a page part")
        for path in c["data"]:
            try:
                resolve(d, path)
            except (KeyError, IndexError, ValueError, TypeError):
                bad.append(f"{c['id']}: data path {path!r} does not resolve")
            claimed |= {b for b in blocks if path == b or path.startswith(b + ".")}
    bad += [f"block {b} is on the page but no claim names it" for b in sorted(blocks - claimed)]
    return bad


def q(s):
    return "'" + str(s).replace("'", "''") + "'"


def receipt_sql(d):
    """An ex-ante decision_receipt INSERT template. Judgment fields stay <REQUIRED ...> placeholders; never written."""
    o = d["outcome"]
    out = os.path.join(ROOT, d["out"])
    built = os.path.exists(out) and open(out, encoding="utf-8").read() == build(d)
    row = backlog_row(o["job_id"]) or {}
    fates = ", ".join(row.get("fates", [])) or "<none on the row>"
    unconf = [f"{c['id']} lands with the reader: {c['claim']}" for c in o["claims"]]
    refs = [d["out"]] + [f"claim:{c['id']} parts={','.join(c['parts'])} data={','.join(c['data'])}" for c in o["claims"]]
    arr = lambda xs: "ARRAY[" + ", ".join(q(x) for x in xs) + "]"
    return f"""-- ex-ante decision_receipt template for {o['job_id']} (fill every <REQUIRED ...>; run via Supabase execute_sql). Not written by this script.
-- Fates on the backlog row, to score at close: {fates}
-- supersedes names the stale ex-ante this one replaces; the old row stays (the ledger is append-only).
INSERT INTO public.decision_receipt
  (receipt_id, question, horizon, stakes, mode, what_confirmed, what_unconfirmed, operator, event_at, source_repo, refs, job_id, tool_id, supersedes)
VALUES (
  '<REQUIRED YYYY-MM-DD--<slug>-exante--ZH>',
  '<REQUIRED the send question, e.g. Send {d['title']}?>',
  '<REQUIRED today|this-week|this-quarter|1-3y>',
  '<REQUIRED low|medium|high|critical>',
  '<REQUIRED QUICKMOVE|PLAN|COURT>',
  {arr(([d['out'] + ' matches its data (counterpart_onepager_build.py --check)'] if built else []) + [f"{len(o['claims'])} claims mapped to kit parts and data paths; every rendered block is claimed"])},
  {arr(([] if built else [d['out'] + ' differs from its data; rebuild before sending']) + unconf)},
  '<REQUIRED operator>',
  '<REQUIRED event_at, timestamptz>',
  'flashesofbrilliance/arcs-v9',
  {arr(refs)},
  {q(o['job_id'])},
  'tool:script:counterpart_onepager_build.py',
  {q(o['supersedes']) if o.get('supersedes') else 'NULL'}
);"""


def main(argv):
    if "--tune" in argv or "--apply" in argv:
        import argparse
        ap = argparse.ArgumentParser(description="counterpart_onepager_build --tune / --apply")
        ap.add_argument("data")
        pt.add_args(ap)
        a = ap.parse_args(argv)
        if a.tune:
            pt.tune_write(build(json.load(open(a.data, encoding="utf-8"))), a.tune)
            return 0
        # fields are trusted authored HTML, so new text is escaped; token sliders land in the data's own "tokens"
        pt.apply(a.apply, [("json-html", a.data)], style=("json-tokens", a.data, "tokens"), version=a.version, validate=validate)
        argv = [a.data]
    if "--receipt" in argv:
        for p in [a for a in argv if not a.startswith("--")] or sorted(os.path.join(DATA, f) for f in os.listdir(DATA) if f.endswith(".json")):
            d = json.load(open(p, encoding="utf-8"))
            if d.get("outcome"):
                bad = validate(d)
                if bad:
                    print("\n".join("✖ " + b for b in bad)); return 1
                print(receipt_sql(d))
        return 0
    check = "--check" in argv
    paths = [a for a in argv if not a.startswith("--")] or sorted(os.path.join(DATA, f) for f in os.listdir(DATA) if f.endswith(".json"))
    bad = 0
    for p in paths:
        d = json.load(open(p, encoding="utf-8"))
        out, page = os.path.join(ROOT, d["out"]), build(d)
        for b in validate(d):
            print(f"✖ {os.path.relpath(p, ROOT)} outcome: {b}"); bad += 1
        if check:
            same = os.path.exists(out) and open(out, encoding="utf-8").read() == page
            print(("✓ " if same else "✖ ") + d["out"] + ("" if same else f" differs from {os.path.relpath(p, ROOT)}; rebuild"))
            bad += 0 if same else 1
        else:
            open(out, "w", encoding="utf-8").write(page)
            print(f"wrote {d['out']}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
