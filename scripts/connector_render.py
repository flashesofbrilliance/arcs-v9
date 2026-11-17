#!/usr/bin/env python3
"""connector_render — render the ADR-056 <tool>.arcs.care connector fleet from SSOT.

One invariant page shape (frozen below, extracted from public/resume-tailor.html — the
hand-built REFERENCE), many surfaces. Layout never varies; only the per-tool DATA does.
Same "freeze layout, vary only the data" discipline as scripts/milestone_render.py.

Two inputs, both git-tracked SSOT — no second source of truth:
  * _SEEDS/distribution.jsonl  — repo / url / channels[] (channel, install, live, verify)
  * _SEEDS/connectors.json     — per-tool copy blocks (grounded in each repo's real README)

HONESTY GATE (hard, per the scope brief + ADR-056 air-gap):
  * A page renders an install channel ONLY if that channel is live:true in distribution.jsonl
    for the same repo. A copy block referencing a non-live channel is a hard error.
  * EXCLUDE list (registry live:false repos) can never be rendered — they have no live channel.
  * Air-gap: only ungated copy from connectors.json reaches the page. Nothing from the private
    _SEEDS registry internals, rosetta, or ripeness priors is templated in.

Usage:
  connector_render.py            # render every tool in connectors.json -> public/<repo>.html
  connector_render.py <repo> …   # render only the named tool(s)
  connector_render.py --check    # render in memory; exit 1 if any committed page differs
  connector_render.py gallery    # render only public/good.html
  connector_render.py --self-test
                                 # (a hand edit to a generated page belongs in this script)

Stdlib only.
"""
import json, os, sys, html

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fonts_selfhost  # noqa: E402  (self-hosted fonts are part of the rendered page)

ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
DIST = os.path.join(ROOT, "_SEEDS/distribution.jsonl")
DATA = os.path.join(ROOT, "_SEEDS/connectors.json")
OUTDIR = os.path.join(ROOT, "public")
CHECK = False   # --check: compare instead of write
DRIFT = []


def write_page(out, doc):
    """Every rendered page goes through here: fonts self-hosted, then written (or compared)."""
    doc = fonts_selfhost.transform(doc)
    if CHECK:
        cur = open(out, encoding="utf-8").read() if os.path.exists(out) else None
        if cur != doc:
            DRIFT.append(os.path.relpath(out, ROOT))
        return
    with open(out, "w", encoding="utf-8") as f:
        f.write(doc)

# ---- accent themes by group (group = hue family; leaves resume-tailor.html untouched) ----
# skill = canonical cyan/green (also what the hand-built resume-tailor.html uses)
# cli   = violet/indigo (the binary/engine tools)
# web   = amber/gold (clone-and-run web apps)
THEMES = {
    "skill": {"c1": "#00F0FF", "c2": "#00FF9D", "btn2": "#00c8dd", "rgb1": "0,240,255",  "rgb2": "0,255,157"},
    "cli":   {"c1": "#A78BFA", "c2": "#6D8BFF", "btn2": "#7C6BF0", "rgb1": "167,139,250", "rgb2": "109,139,255"},
    "web":   {"c1": "#FFC24D", "c2": "#FF8A3D", "btn2": "#F5A623", "rgb1": "255,194,77",  "rgb2": "255,138,61"},
}


def theme_vars(group):
    """Per-group :root override — only the accent variables change; structure is frozen."""
    t = THEMES.get(group, THEMES["skill"])
    r1, r2 = t["rgb1"], t["rgb2"]
    return (
        f"--cyan:{t['c1']};--green:{t['c2']};--btn2:{t['btn2']};"
        f"--glowA:rgba({r1},.11);--glowB:rgba({r2},.075);--kickbrd:rgba({r1},.36);"
        f"--btnglow:rgba({r1},.5);--glowsoft:rgba({r1},.25);--barbg:rgba({r1},.045);"
    )


# The kit tokens, inlined verbatim (sentinel kept) ahead of the house style so every rendered page
# inherits one palette instead of re-authoring it (token_source_gate; seam ledger 2026-10-08).
_TOKENS_PATH = os.path.join(ROOT, "src", "ui-kit", "recoil-report", "_tokens.css")
# Tolerant read: the argument-guard self-test runs in a scratch dir without the kit (it renders nothing).
TOKENS_CSS = open(_TOKENS_PATH, encoding="utf-8").read().rstrip() if os.path.exists(_TOKENS_PATH) else ""
# ---- frozen house style: <style> block from resume-tailor.html, accents lifted to vars ----
CSS = """  :root{
    /* neutrals: canonical ARCS design-system tokens (WORLD.md / colors_and_type) */
    --bg:#020408;--surface:#0d1117;--elev:#131a24;--border:#1e293b;--border2:#2b3a4f;
    --fg1:#e2e8f0;--fg2:#94a3b8;--fg3:#8391a7;--fg4:#7a8699;
    --cyan:#00F0FF;--green:#00FF9D;--gold:#FFD700;--red:#FF4D6D;--btn2:#00c8dd;
    --glowA:rgba(0,240,255,.11);--glowB:rgba(0,255,157,.075);--kickbrd:rgba(0,240,255,.36);
    --btnglow:rgba(0,240,255,.5);--glowsoft:rgba(0,240,255,.25);--barbg:rgba(0,240,255,.045);
    --sans:'Inter',system-ui,-apple-system,sans-serif;--mono:'JetBrains Mono','IBM Plex Mono',monospace;
  }
  *,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
  html{background:var(--bg);color:var(--fg1);font-family:var(--sans);-webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility;scroll-behavior:smooth;}
  ::selection{background:var(--cyan);color:#001014;}
  a{color:inherit;text-decoration:none;}
  .wrap{max-width:920px;margin:0 auto;padding:0 24px;}
  .mono{font-family:var(--mono);}

  header{position:relative;overflow:hidden;border-bottom:1px solid var(--border);
    background:radial-gradient(900px 420px at 20% -10%,var(--glowA),transparent 60%),radial-gradient(700px 380px at 92% 0,var(--glowB),transparent 55%);}
  .hero{padding-block:66px 58px;}
  .kick{display:inline-flex;align-items:center;gap:9px;font-family:var(--mono);font-size:11px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:var(--cyan);border:1px solid rgba(0,240,255,.35);border-radius:999px;padding:6px 13px;}
  .kick .dot{width:7px;height:7px;border-radius:50%;background:var(--green);box-shadow:0 0 10px var(--green);}
  h1{font-size:clamp(46px,9vw,88px);font-weight:800;letter-spacing:-.035em;line-height:.95;margin-top:22px;}
  h1 .g{background:linear-gradient(100deg,var(--cyan),var(--green));-webkit-background-clip:text;background-clip:text;color:transparent;}
  .lede{font-size:clamp(16px,2.5vw,20px);line-height:1.58;color:var(--fg2);max-width:640px;margin-top:22px;}
  .lede b{color:var(--fg1);font-weight:600;}
  /* full-width lede matches heading… hero lede spans the container, not a narrow column */
  .hero .lede{max-width:none;}
  .cta{display:flex;gap:12px;flex-wrap:wrap;margin-top:30px;}
  .btn{display:inline-flex;align-items:center;gap:9px;font-family:var(--mono);font-size:12px;font-weight:700;letter-spacing:.03em;padding:12px 18px;border-radius:9px;transition:.16s;cursor:pointer;border:none;}
  .btn.p{color:#001014;background:linear-gradient(100deg,var(--cyan),#00c8dd);box-shadow:0 8px 26px -10px rgba(0,240,255,.5);}
  .btn.p:hover{transform:translateY(-1px);}
  .btn.s{color:var(--fg1);border:1px solid var(--border2);background:var(--elev);}
  .btn.s:hover{border-color:var(--cyan);color:var(--cyan);}

  section{padding:52px 0;border-bottom:1px solid var(--border);}
  .sec-lbl{display:flex;align-items:baseline;gap:11px;margin-bottom:24px;}
  .sec-lbl .n{font-family:var(--mono);font-size:11px;font-weight:700;color:var(--cyan);}
  .sec-lbl h2{font-size:22px;font-weight:700;letter-spacing:-.01em;}
  .sec-lbl .sub{font-family:var(--mono);font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--fg4);margin-left:auto;}

  .thesis{font-size:clamp(19px,3vw,25px);line-height:1.5;font-weight:500;letter-spacing:-.01em;color:var(--fg1);max-width:780px;}
  .thesis b{color:var(--green);font-weight:600;}
  .thesis small{display:block;font-size:13.5px;font-weight:400;color:var(--fg3);margin-top:16px;line-height:1.65;}

  .grades{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-top:28px;}
  @media(max-width:720px){.grades{grid-template-columns:1fr;}}
  .grade{border:1px solid var(--border);border-radius:13px;padding:18px;background:linear-gradient(165deg,rgba(255,255,255,.02),rgba(0,0,0,.15));}
  .grade .g{font-family:var(--mono);font-size:11px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--cyan);}
  .grade p{font-size:12.5px;line-height:1.55;color:var(--fg2);margin-top:9px;}

  .oneshot{position:relative;border:1px solid var(--border2);border-radius:13px;background:linear-gradient(165deg,#0c1219,#080d13);box-shadow:0 12px 34px -18px rgba(0,240,255,.25);overflow:hidden;}
  .oneshot .bar{display:flex;align-items:center;justify-content:space-between;padding:11px 15px;border-bottom:1px solid var(--border);background:rgba(0,240,255,.04);}
  .oneshot .bar .l{font-family:var(--mono);font-size:11px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--cyan);}
  .oneshot .cp{font-family:var(--mono);font-size:11px;font-weight:700;letter-spacing:.06em;color:var(--fg3);border:1px solid var(--border2);background:var(--elev);border-radius:7px;padding:5px 11px;cursor:pointer;transition:.15s;}
  .oneshot .cp:hover{color:var(--cyan);border-color:var(--cyan);}
  /* Links in running text carry an underline, not color alone (WCAG 1.4.1). */
  a:not([class]):not(nav a){text-decoration:underline;text-underline-offset:.18em;text-decoration-thickness:1px;}
  .oneshot{min-width:0;max-width:100%;}
  .chan{min-width:0;}
  .oneshot pre{margin:0;padding:17px 18px;overflow-x:auto;}
  .oneshot code{font-family:var(--mono);font-size:12.5px;line-height:1.7;color:var(--fg1);white-space:pre-wrap;}
  .oneshot code .v{color:var(--gold);}

  .install-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px;}
  @media(max-width:720px){.install-grid{grid-template-columns:1fr;}}
  .install-grid.one{grid-template-columns:1fr;max-width:620px;}
  .chan h3{font-family:var(--mono);font-size:11px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--fg4);margin-bottom:8px;}

  pre.blk{background:var(--elev);border:1px solid var(--border);border-radius:11px;padding:15px 17px;overflow-x:auto;}
  pre.blk code{font-family:var(--mono);font-size:12.5px;color:var(--green);line-height:1.7;white-space:pre-wrap;}
  .note{font-size:12.5px;line-height:1.55;color:var(--fg3);margin-top:14px;} .note b{color:var(--fg2);font-weight:600;}

  footer{padding:34px 0 48px;}
  .foot{display:flex;justify-content:space-between;align-items:center;gap:16px;flex-wrap:wrap;font-family:var(--mono);font-size:11px;color:var(--fg4);letter-spacing:.04em;}
  .foot a{color:var(--fg3);} .foot a:hover{color:var(--cyan);}"""

COPY_JS = """  function copyFlash(b,ok){
    if(!b) return; if(b._t) clearTimeout(b._t); if(!b._o) b._o=b.textContent;
    b.textContent = ok ? 'copied ✓' : 'select + copy';
    b.style.color = ok ? '#00FF9D' : '#FFD700';
    b._t=setTimeout(function(){b.textContent=b._o;b.style.color='';},1800);
  }
  function legacyCopy(t){
    try{ var ta=document.createElement('textarea'); ta.value=t; ta.setAttribute('readonly','');
      ta.style.cssText='position:fixed;top:0;left:0;opacity:0';
      document.body.appendChild(ta); ta.select(); ta.setSelectionRange(0,t.length);
      var ok=document.execCommand('copy'); document.body.removeChild(ta); return ok;
    }catch(e){ return false; }
  }
  function copyCmd(btn){
    var t=btn.getAttribute('data-cmd')||'';
    if(navigator.clipboard && navigator.clipboard.writeText){
      navigator.clipboard.writeText(t).then(function(){copyFlash(btn,true);},
        function(){ copyFlash(btn, legacyCopy(t)); });
    } else { copyFlash(btn, legacyCopy(t)); }
  }"""


def esc(s):
    return html.escape(s, quote=True)


def load_ssot():
    rows = {}
    with open(DIST) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            rows[row["repo"]] = row
    return rows


def live_channels(row):
    """channel-name -> channel dict, for channels with live is True."""
    out = {}
    for ch in row.get("channels", []):
        if ch.get("live") is True:
            out[ch["channel"]] = ch
    return out


# ---- tool-getting-started (src/ui-kit/templates.json; docs/ui-kit-tool-template-plan.md) ----
# The template's head (tokens, grammar chips, kit CSS, fonts) is read from its canonical example so
# the kit has one copy; only title, description and the tool's one non-signal swatch change.
TOOL_TEMPLATE_SRC = os.path.join(OUTDIR, "good-rfp-engine.html")


FONT_REQUEST = ('<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800'
                '&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">')


def tool_template_head(title, desc, accent, note, jtbd=None):
    import re
    src = open(TOOL_TEMPLATE_SRC, encoding="utf-8").read()
    head = src[:src.index("</head>")]
    tail = src[src.index('<script>\ndocument.querySelectorAll("pre")'):]
    head = re.sub(r'<link rel="alternate"[^>]*>\n', "", head)
    head = re.sub(r'<link rel="preload"[^>]*as="font"[^>]*>\n', "", head)  # write_page re-adds fonts
    head = re.sub(r"/\* fonts_selfhost:begin.*?fonts_selfhost:end \*/\n", "", head, flags=re.S)
    head = head.replace("</title>", "</title>\n" + FONT_REQUEST, 1)
    head = re.sub(r"<title>[^<]*</title>", f"<title>{esc(title)}</title>", head)
    head = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{esc(desc)}">', head)
    head = re.sub(r":root\{--tool-accent:#[0-9a-fA-F]{6}\}", ":root{--tool-accent:%s}" % accent, head)
    head = re.sub(r"rfp-engine wears [^.]*?\)", note, head)
    head = re.sub(r'<html lang="en"[^>]*>', f'<html lang="en" data-jtbd="{esc(jtbd)}">' if jtbd else '<html lang="en">', head, count=1)
    # The tail carries the kit 51 display-preferences wiring, which needs its row and panel in the body.
    # Lift both from the canonical page too, so the markup and the wiring always travel together.
    row = re.search(r'<div class="dprefs">.*?</div>', src, re.S)
    panel = re.search(r'<section id="dp" class="dprefs-panel".*?</section>', src, re.S)
    dprefs = (row.group(0), panel.group(0)) if row and panel else ("", "")
    return head, tail, dprefs


def render_tool_page(repo, data, row, live):
    url = row["url"]
    gh = "https://" + url if not url.startswith("http") else url
    t = data["tool"]
    head, tail, (dp_row, dp_panel) = tool_template_head(f"{repo} · ARCS public goods", data["desc"], t["accent"], t["accent_note"], t.get("jtbd"))
    chips = "\n".join(
        f'<span class="g-chip" data-tone="{c["tone"]}"><span class="g-glyph">{ {"show": "●", "say": "◆", "limit": "▲"}[c["tone"]] }</span>'
        f'<span class="g-tag">{esc(c["tag"])}</span><span class="g-body">{esc(c["body"])}</span></span>'
        for c in t["chips"])
    installs = "\n".join(f'<pre>{esc(data["install"][ch]["cmd"])}</pre>' for ch in live if ch in data["install"])
    note = f'\n<p>{esc(data["note_linux"])}</p>' if data.get("note_linux") else ""
    rules = "\n".join(f'<div class="panel"><h3>{esc(c["t"])}</h3><p>{esc(c["p"])}</p></div>' for c in t["what"])
    gaps = "\n".join(f"<li>{esc(g)}</li>" for g in t["not_proven"])
    # Optional "try it" link to a companion page on the same host (rosetta-shell's /voice, 2026-11-15).
    tr = t.get("try")
    try_html = (f'\n\n<h2>{esc(tr["title"])}</h2>\n<div class="panel"><p>{esc(tr["text"])}</p>'
                f'<p><a href="{esc(tr["href"])}">{esc(tr["label"])}</a></p></div>') if tr else ""
    body = f"""</head>
<script defer src="/_vercel/insights/script.js"></script>
<body>
<main>
<div class="top">
<p class="section-label eyebrow">ARCS public goods · {esc(t["stage"])}</p>
{dp_row}
</div>
{dp_panel}
<h1>{esc(t["h1"])}</h1>
<p class="lede">{esc(t["lede"])}</p>
<div class="chips">
{chips}
</div>

<h2>Why it exists</h2>
<p>{esc(t["why"])}</p>

<h2>Install</h2>
{installs}{note}{try_html}

<h2>{esc(t["what_label"])}</h2>
<div class="rules">
{rules}
</div>

<h2>Not proven yet</h2>
<ul>
{gaps}
</ul>

<h2>For agents</h2>
<p>MIT and public: read the source at <a href="{esc(gh)}">{esc(url)}</a> before you install it.</p>
<p><a href="/">ARCS public goods</a> · <a href="/llms.txt">site llms.txt</a> · <a href="/AGENTS.md">site AGENTS.md</a></p>
</main>
"""
    # Frustration gate: wiring without its markup throws on every load (rosetta-shell and germinate did,
    # 2026-11-14). Refuse to write that page.
    if "querySelector('.dprefs')" in tail and 'class="dprefs"' not in body:
        raise SystemExit(f"REFUSED: {repo}.html would ship the display-preferences script without its row "
                         f"and panel; {TOOL_TEMPLATE_SRC} must carry both.")
    out = os.path.join(OUTDIR, f"{repo}.html")
    write_page(out, head + body + tail)
    chans = ", ".join(f"{c}✓" for c in live if c in data["install"])
    print(f"rendered public/{repo}.html  [{chans}] (tool-getting-started)")


def render(repo, data, row):
    live = live_channels(row)
    if not live:
        raise SystemExit(f"REFUSED: {repo} has no live:true channel in SSOT — cannot render a connector.")

    # honesty gate: every install block must map to a live SSOT channel
    for chname in data["install"]:
        if chname not in live:
            raise SystemExit(
                f"REFUSED: {repo} copy references channel '{chname}' which is NOT live:true in SSOT. "
                f"live channels: {sorted(live)}")

    if data.get("template") == "tool-getting-started":
        return render_tool_page(repo, data, row, live)

    url = row["url"]
    gh = "https://" + url if not url.startswith("http") else url

    # hero
    badge = f"{repo} · {data['badge_kind']}"
    h1 = f'<span class="g">{esc(data["title_g"])}</span> {esc(data["title_rest"])}'

    # what-it-does cards (2 or 3 col grid — grades class handles both via repeat(3) + wrap)
    cards = "\n".join(
        f'      <div class="grade"><div class="g">● {esc(c["t"])}</div><p>{esc(c["p"])}</p></div>'
        for c in data["what"])

    # install blocks — only live channels, in SSOT order
    blocks = []
    for chname, ch in live.items():
        if chname not in data["install"]:
            continue
        spec = data["install"][chname]
        cmd = spec["cmd"]
        blocks.append(
            f'      <div class="chan">\n'
            f'        <h3>{esc(spec["label"])}</h3>\n'
            f'        <div class="oneshot">\n'
            f'          <div class="bar"><span class="l">◈ {esc(chname)}</span>'
            f'<button class="cp" data-cmd="{esc(cmd)}" onclick="copyCmd(this)">copy</button></div>\n'
            f'          <pre><code>{esc(cmd)}</code></pre>\n'
            f'        </div>\n'
            f'      </div>')
    grid_cls = "install-grid one" if len(blocks) == 1 else "install-grid"
    install_html = f'    <div class="{grid_cls}">\n' + "\n".join(blocks) + "\n    </div>"

    # optional usage line
    usage_html = ""
    if data.get("usage"):
        u = data["usage"]
        usage_html = (
            f'\n    <h3 style="font-family:var(--mono);font-size:11px;font-weight:700;letter-spacing:.1em;'
            f'text-transform:uppercase;color:var(--fg4);margin:26px 0 10px;">{esc(u["label"])}</h3>\n'
            f'    <pre class="blk"><code>{esc(u["code"])}</code></pre>')
    if data.get("requires"):
        usage_html += f'\n    <p class="note">{data["requires"]}</p>'
    if data.get("note_linux"):
        usage_html += f'\n    <p class="note">{esc(data["note_linux"])}</p>'

    doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(repo)} · {esc(data['title_g'].rstrip(',').lower())}</title>
<meta name="description" content="{esc(data['desc'])}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
{TOKENS_CSS}
{CSS}
  :root{{{theme_vars(data.get('group','skill'))}}}
</style>
<script defer src="/_vercel/insights/script.js"></script>
</head>
<body>

<header>
  <div class="wrap hero">
    <span class="kick"><span class="dot"></span>{esc(badge)}</span>
    <h1>{h1}</h1>
    <p class="lede">{data['lede']}</p>
    <div class="cta">
      <a class="btn p" href="#start">↓ Install</a>
      <a class="btn s" href="{esc(gh)}">◇ GitHub</a>
    </div>
  </div>
</header>

<section>
  <div class="wrap">
    <div class="sec-lbl"><span class="n">01</span><h2>{esc(data['thesis_label'])}</h2><span class="sub">{esc(data['thesis_sub'])}</span></div>
    <p class="thesis">{data['thesis']}</p>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="sec-lbl"><span class="n">02</span><h2>{esc(data['what_label'])}</h2><span class="sub">{esc(data['what_sub'])}</span></div>
    <div class="grades">
{cards}
    </div>
  </div>
</section>

<section id="start">
  <div class="wrap">
    <div class="sec-lbl"><span class="n">03</span><h2>{esc(data['install_label'])}</h2><span class="sub">{esc(data['install_sub'])}</span></div>
{install_html}{usage_html}
  </div>
</section>

<section>
  <div class="wrap">
    <div class="sec-lbl"><span class="n">04</span><h2>Part of the ARCS family</h2><span class="sub">the tie-in</span></div>
    <p class="thesis">{esc(data['tie_in'])}</p>
  </div>
</section>

<footer>
  <div class="wrap foot">
    <span>{esc(repo)} · a public good by <a href="https://arcs.care">ARCS</a> · MIT</span>
    <span><a href="{esc(gh)}">github</a> · <a href="https://arcs.care">arcs.care</a></span>
  </div>
</footer>

<script>
{COPY_JS}
</script>
</body>
</html>
"""
    out = os.path.join(OUTDIR, f"{repo}.html")
    write_page(out, doc)
    chans = ", ".join(f"{c}✓" for c in live if c in data["install"])
    print(f"rendered public/{repo}.html  [{chans}]")


# tools that earn a standalone deep page; everyone else is a gallery card only.
STANDALONE_GROUPS = {"cli", "web"}
# tools with a hand-built page outside this renderer (do not re-render, but DO index on the gallery)
EXTERNAL_PAGES = {
    "honest": {
        "slug": "honest", "group": "web", "name": "check it before you say it",
        "line": "Five steps between an idea and a message, each stamped go or stop by rules you can read. It checks the facts you mark, not whether they are true. Runs in your browser; nothing is uploaded.",
        "page": "https://honest.arcs.care", "chips": ["web"],
        # its distribution row is keyed by the repo name, not the page slug
        "repo": "check-it-before-you-say-it",
    },
    "cruft-sweep-skill": {
        "slug": "cruft-sweep", "group": "skill", "name": "cruft-sweep-skill",
        "line": "Survey and safely reclaim stale git worktrees. Every prune writes a verified bundle first, and a salvage check flags claims that exist nowhere else before anything is removed.",
        "page": "", "repo": "cruft-sweep-skill",
    },
    "claims-skeptic-skill": {
        "slug": "claims-skeptic", "group": "skill", "name": "claims-skeptic-skill",
        "line": "An agent that checks each factual claim in a document against the live repository: verified with evidence, false with counter-evidence, or unverifiable with the check that would settle it.",
        "page": "", "repo": "claims-skeptic-skill",
    },
    "resume-tailor-skill": {
        "slug": "resume-tailor", "group": "skill", "name": "resume-tailor",
        "line": "Tailor a resume and cover letter to a role, graded by how checkable every line is.",
        "page": "https://resume-tailor.arcs.care",
    },
}
CHAN_CHIP = {"npm": "npm", "homebrew": "brew", "claude-plugin": "plugin",
             "pypi": "pip", "github": "clone"}


def first_sentence(s):
    s = s.strip()
    i = s.find(". ")
    return (s[:i + 1] if i != -1 else s)


def _card(name, line, chips, page, gh, group, live=True, variant="full", tag="soon"):
    t = THEMES.get(group, THEMES["skill"])
    accent = f"linear-gradient(90deg,{t['c1']},{t['c2']})"
    # a not-ready entry with its own live page (a preview) links that page and renders undimmed
    dim = "" if live or page else "opacity:.5;filter:saturate(.35);"
    chip_html = "".join(f'<span class="chip">{esc(c)}</span>' for c in chips)
    if live:
        primary = (f'<a class="clink" href="{esc(page)}">open ↗</a>' if page
                   else f'<a class="clink" href="{esc(gh)}">github ↗</a>')
        gh_link = f'<a class="cgh" href="{esc(gh)}">github</a>' if page and gh else ""
        tag = ""
    else:
        primary = (f'<a class="clink" href="{esc(page)}">open ↗</a>' if page
                   else f'<a class="clink" href="{esc(gh)}">github ↗</a>')
        gh_link = ""
        tag = f'<span class="soon">{esc(tag)}</span>'

    if variant == "compact":
        # secondary tier: denser, no chip row, single link — visually lighter
        return (
            f'    <div class="card compact" style="{dim}">\n'
            f'      <div class="cbar" style="background:{accent}"></div>\n'
            f'      <div class="cbody">\n'
            f'        <div class="chead"><span class="cname mono">{esc(name)}</span>{tag}</div>\n'
            f'        <p class="cline">{esc(line)}</p>\n'
            f'      </div>\n'
            f'      <div class="cfoot">{primary}</div>\n'
            f'    </div>')

    return (
        f'    <div class="card" style="{dim}">\n'
        f'      <div class="cbar" style="background:{accent}"></div>\n'
        f'      <div class="cbody">\n'
        f'        <div class="chead"><span class="cname mono">{esc(name)}</span>{tag}</div>\n'
        f'        <p class="cline">{esc(line)}</p>\n'
        f'        <div class="chips">{chip_html}</div>\n'
        f'      </div>\n'
        f'      <div class="cfoot">{primary}{gh_link}</div>\n'
        f'    </div>')


# Information hierarchy: lead with the fully-baked goods, in this order.
# Everything else live falls to the secondary "also in the toolkit" tier.
FEATURED_ORDER = ["honest", "resume-tailor-skill", "rosetta-shell", "germinate"]


# good.html blocks that are page structure, not per-tool data: kept verbatim here so the
# renderer reproduces the live page byte for byte (connector_render.py --check enforces it).
GOOD_HERO = """<header>
  <div class="wrap hero">
    <span class="kick"><span class="dot"></span><span style="display:inline-flex;gap:.45em;align-items:baseline"><span style="font-weight:800;letter-spacing:.22em">ARCS</span><span style="color:var(--fg3);font-weight:400;letter-spacing:.14em">Field OS</span></span> &middot; public goods</span>
    <h1>Open tools,<br><span class="g">honest by default.</span></h1>
    <p class="lede">Small, MIT-licensed tools we built for our own work and published as they proved out. The tools are <b>open</b>; the ARCS intelligence that orchestrates them stays private. Nothing here claims an install path that is not live.</p>

    <div class="oneshot" style="margin-top:30px;">
      <div class="bar">
        <span class="l">install the family · Claude Code</span>
        <button class="cp" data-copy="/plugin marketplace add flashesofbrilliance/arcs-skills">copy</button>
      </div>
      <pre><code>/plugin marketplace add <span class="v">flashesofbrilliance/arcs-skills</span></code></pre>
    </div>
    <p class="note">Five skills in one marketplace: <b>rca</b>, <b>state-sync</b>, <b>token-savings-bank</b>, <b>fix-toolbar-comments</b>, <b>resume-tailor</b>. Or reach for a single tool below. CLI tools also ship on Homebrew (<span class="mono">brew tap flashesofbrilliance/tap</span>) and npm.</p>
  </div>
</header>"""

# the series row, the ADR-076 agent-connector demand probe and its analytics events
GOOD_AFTER_BODY = """<style>
  /* ADR-076 MCP-led-growth demand probe (Stage 0, painted door). Honest framing: the connector
     does not exist yet; the CTA click is the interest signal, tracked via Vercel custom events. */
  .mcp-probe{padding:44px 0;border-bottom:1px solid var(--border);}
  .mp-card{border:1px solid rgba(0,240,255,.28);border-radius:16px;padding:26px 26px 24px;
    background:radial-gradient(700px 300px at 12% -30%,rgba(0,240,255,.08),transparent 60%),linear-gradient(165deg,rgba(255,255,255,.02),rgba(0,0,0,.16));}
  .mp-eyebrow{display:inline-flex;align-items:center;gap:8px;font-family:var(--mono);font-size:11px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:var(--cyan);}
  .mp-dot{width:7px;height:7px;border-radius:50%;background:var(--green);box-shadow:0 0 10px var(--green);}
  .mp-h{font-size:clamp(19px,3vw,25px);font-weight:800;letter-spacing:-.02em;line-height:1.2;margin-top:12px;color:var(--fg1);text-wrap:balance;}
  .mp-b{font-size:14.5px;line-height:1.6;color:var(--fg2);margin-top:11px;max-width:none;text-wrap:pretty;} .mp-b b{color:var(--fg1);font-weight:600;}
  .mp-cta{margin-top:18px;font-family:var(--mono);font-size:13px;font-weight:700;letter-spacing:.03em;color:#001014;background:linear-gradient(100deg,var(--cyan),var(--green));border:none;border-radius:10px;padding:12px 20px;cursor:pointer;transition:transform .15s;}
  .mp-cta:hover{transform:translateY(-1px);}
  .mp-cta:focus-visible{outline:2px solid var(--cyan);outline-offset:3px;}
  .mp-done{font-size:13.5px;line-height:1.6;color:var(--fg3);margin-top:16px;max-width:none;} .mp-done a{color:var(--cyan);}
</style>
<section>
  <div class="wrap">
    <div class="sec-lbl"><span class="n">◆</span><h2>Field notes and series</h2><span class="sub">the writing behind the tools</span></div>
    <div class="cards">
    <div class="card compact">
      <div class="cbar" style="background:linear-gradient(90deg,#00F0FF,#00FF9D)"></div>
      <div class="cbody">
        <div class="chead"><span class="cname mono">Notes from the Trenches</span></div>
        <p class="cline">Real stories from building ARCS in the open, each with the receipts.</p>
      </div>
      <div class="cfoot"><a class="clink" href="/blog/nftt">read &#8594;</a></div>
    </div>
    <div class="card compact">
      <div class="cbar" style="background:linear-gradient(90deg,#00F0FF,#00FF9D)"></div>
      <div class="cbody">
        <div class="chead"><span class="cname mono">Lore</span></div>
        <p class="cline">The stories ARCS is built on, each filed with a verdict and the test that would retire it.</p>
      </div>
      <div class="cfoot"><a class="clink" href="/series/lore">read &#8594;</a></div>
    </div>
    <div class="card compact">
      <div class="cbar" style="background:linear-gradient(90deg,#00F0FF,#00FF9D)"></div>
      <div class="cbody">
        <div class="chead"><span class="cname mono">Receipts</span></div>
        <p class="cline">Dated public predictions, each with its own falsifier, re-scored against the primary documents.</p>
      </div>
      <div class="cfoot"><a class="clink" href="/series/receipts">read &#8594;</a></div>
    </div>
    </div>
  </div>
</section>

<section class="mcp-probe" aria-label="Connect an agent (demand probe)">
  <div class="wrap">
    <div class="mp-card">
      <div class="mp-eyebrow"><span class="mp-dot"></span>Connect an agent &middot; considering this</div>
      <h2 class="mp-h">Query the ARCS field notes from your AI tools</h2>
      <p class="mp-b">We are weighing an ARCS connector for Claude, Cursor, and other agents: ask about anything in the <a href="https://good.arcs.care/blog/nftt" style="color:var(--cyan)">field notes</a> and get an answer that <b>cites its source, not a guess</b>. It does not exist yet. This is a live demand probe, so if you would use it, say so and we will build it.</p>
      <button class="mp-cta" id="mpCta" type="button">I'd use this &#8594;</button>
      <p class="mp-done" id="mpDone" hidden>Noted, thank you. Enough signal and we ship the connector. In the meantime the tools above are open at <a href="https://github.com/flashesofbrilliance/arcs-skills">github.com/flashesofbrilliance/arcs-skills</a>.</p>
    </div>
  </div>
</section>
<script>
  /* Vercel Web Analytics custom events; guarded so the page is fine if analytics is blocked. */
  (function(){
    function ev(name){ try{ window.va && window.va('event', { name: name, data: { surface: 'good' } }); }catch(e){} }
    var card = document.querySelector('.mcp-probe');
    if (card && 'IntersectionObserver' in window){
      var seen = false;
      var io = new IntersectionObserver(function(entries){
        entries.forEach(function(en){ if(en.isIntersecting && !seen){ seen = true; ev('mcp_probe_view'); io.disconnect(); } });
      }, { threshold: 0.4 });
      io.observe(card);
    }
    var cta = document.getElementById('mpCta'), done = document.getElementById('mpDone');
    if (cta){ cta.addEventListener('click', function(){ ev('mcp_probe_interest'); if(done){ done.hidden = false; } cta.disabled = true; cta.style.opacity = '.55'; cta.style.cursor = 'default'; }); }
  })();
</script>

"""

GOOD_TAIL = """<footer>
  <div class="wrap foot">
    <span>a public-goods index by <a href="https://arcs.care">ARCS</a> · MIT</span>
    <span><a href="https://github.com/flashesofbrilliance">github</a> · <a href="https://github.com/flashesofbrilliance/arcs-skills">marketplace</a> · <a href="/instruments">instruments</a> · <a href="https://arcs.care">arcs.care</a></span>
    <span>built by Zach Harris, one operator accountable end to end · proof over promises, sprint or in-house · <a href="https://zachharris.xyz">zachharris.xyz</a></span>
  </div>
</footer>

<script>
/* copy-to-clipboard for install one-liners; data-copy holds the exact command */
document.querySelectorAll('.cp[data-copy]').forEach(function(b){
  b.addEventListener('click', function(){
    navigator.clipboard.writeText(b.getAttribute('data-copy')).then(function(){
      var t=b.textContent; b.textContent='copied'; setTimeout(function(){b.textContent=t;},1400);
    }).catch(function(){});
  });
});
</script>
</body>
</html>
"""


def render_gallery(ssot, blob):
    tools = blob["tools"]
    soon = blob.get("soon", {})

    # Build a uniform meta record per live repo (rendered tools + external pages).
    meta = {}  # repo -> {group, name, line, chips, page, gh}
    for repo, data in tools.items():
        if "gallery_soon" in data:   # has its own page, but listed on the gallery as not ready
            continue
        g = data.get("group", "skill")
        url = ssot.get(repo, {}).get("url", "")
        gh = ("https://" + url) if url and not url.startswith("http") else url
        chips = [CHAN_CHIP.get(c, c) for c in live_channels(ssot.get(repo, {}))]
        if g == "skill":
            chips = ["skill"] + [c for c in chips if c != "clone"]
        page = f"https://{repo}.arcs.care" if g in STANDALONE_GROUPS else ""
        meta[repo] = dict(group=g, name=repo, line=data.get("gallery_line") or first_sentence(data["desc"]),
                          chips=chips, page=page, gh=gh)
    for repo, ext in EXTERNAL_PAGES.items():
        row = ssot.get(ext.get("repo", repo), {})
        url = row.get("url", "")
        gh = ("https://" + url) if url and not url.startswith("http") else url
        chips = list(ext.get("chips", ["plugin", "skill"]))
        if "repo" in ext:   # opted in: its live distribution channels add their chips (github -> clone)
            chips += [c for c in (CHAN_CHIP.get(ch, ch) for ch in live_channels(row)) if c not in chips]
        meta[repo] = dict(group=ext["group"], name=ext["name"], line=ext["line"],
                          chips=chips, page=ext["page"], gh=gh)

    def card_for(repo, variant="full"):
        m = meta[repo]
        return _card(m["name"], m["line"], m["chips"], m["page"], m["gh"],
                     m["group"], True, variant)

    featured = [card_for(r) for r in FEATURED_ORDER if r in meta]
    minor_repos = [r for r in meta if r not in FEATURED_ORDER]
    minor = [card_for(r, "compact") for r in minor_repos]

    # soon (ready-not-live) — muted cards, github only, no install claim
    soon_cards = []
    soon = {**{r: dict(d["gallery_soon"], group=d.get("group", "skill"))
               for r, d in tools.items() if "gallery_soon" in d}, **soon}
    for repo, s in soon.items():
        url = ssot.get(repo, {}).get("url", "")
        gh = ("https://" + url) if url and not url.startswith("http") else url
        soon_cards.append(_card(repo, s["line"], [s["chan"]], s.get("page", ""), gh, s.get("group", "skill"), False,
                                tag=s.get("tag", "soon")))

    def block(label, sub, cards, grid="cards"):
        if not cards:
            return ""
        return (
            f'<section>\n  <div class="wrap">\n'
            f'    <div class="sec-lbl"><span class="n">◆</span><h2>{esc(label)}</h2>'
            f'<span class="sub">{esc(sub)}</span></div>\n'
            f'    <div class="{grid}">\n' + "\n".join(cards) + "\n    </div>\n  </div>\n</section>")

    body = "\n\n".join(x for x in [
        block("Featured", "fully baked · usable today", featured, "cards featured"),
        block("Also in the toolkit", "smaller Claude Code skills · clone and add", minor, "cards minor"),
        block("Coming soon", "repo public · package or build pending", soon_cards, "cards minor"),
    ] if x)

    GAL_CSS = """
  .cards{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;}
  @media(max-width:820px){.cards{grid-template-columns:1fr 1fr;}}
  @media(max-width:560px){.cards{grid-template-columns:1fr;}}
  /* Featured tier: fewer, larger cards lead the page. */
  .cards.featured{grid-template-columns:repeat(2,1fr);gap:18px;}
  .cards.featured .cbody{padding:20px 20px 8px;}
  .cards.featured .cname{font-size:16px;}
  .cards.featured .cline{font-size:13px;}
  @media(max-width:640px){.cards.featured{grid-template-columns:1fr;}}
  /* Secondary tier: compact, denser, visually lighter. */
  .cards.minor{grid-template-columns:repeat(4,1fr);gap:12px;}
  @media(max-width:820px){.cards.minor{grid-template-columns:1fr 1fr;}}
  @media(max-width:480px){.cards.minor{grid-template-columns:1fr;}}
  .card.compact .cbar{height:2px;}
  .card.compact .cbody{padding:13px 14px 4px;}
  .card.compact .cname{font-size:12.5px;}
  .card.compact .cline{font-size:12px;margin-top:7px;}
  .card.compact .cfoot{padding:10px 14px;}
  .card{display:flex;flex-direction:column;border:1px solid var(--border);border-radius:14px;overflow:hidden;background:linear-gradient(165deg,rgba(255,255,255,.02),rgba(0,0,0,.18));transition:.16s;}
  .card:hover{border-color:var(--border2);transform:translateY(-2px);}
  .cbar{height:3px;width:100%;}
  .cbody{padding:16px 17px 6px;flex:1;}
  .chead{display:flex;align-items:center;justify-content:space-between;gap:8px;}
  .cname{font-size:14px;font-weight:700;color:var(--fg1);letter-spacing:-.01em;}
  .soon{font-family:var(--mono);font-size:11px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--fg4);border:1px solid var(--border2);border-radius:999px;padding:3px 8px;}
  .cline{font-size:12.5px;line-height:1.55;color:var(--fg2);margin-top:9px;}
  .chips{display:flex;gap:6px;flex-wrap:wrap;margin-top:13px;}
  .chip{font-family:var(--mono);font-size:11px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;color:var(--fg3);border:1px solid var(--border);border-radius:6px;padding:3px 7px;}
  .cfoot{display:flex;gap:16px;align-items:center;padding:13px 17px;border-top:1px solid var(--border);margin-top:12px;}
  .clink{font-family:var(--mono);font-size:11px;font-weight:700;letter-spacing:.04em;color:var(--cyan);}
  .cgh{font-family:var(--mono);font-size:11px;color:var(--fg4);}
  .cgh:hover{color:var(--fg2);}
  .gcount{font-family:var(--mono);font-size:11px;color:var(--fg4);letter-spacing:.06em;margin-left:auto;}
  .compass-tie{border-bottom:1px solid var(--border);
    background:radial-gradient(700px 300px at 50% -20%,var(--glowA),transparent 60%);}
  .compass-tie .wrap{padding-top:44px;padding-bottom:44px;text-align:center;}
  .ct-lede{font-size:clamp(16px,2.4vw,20px);line-height:1.55;color:var(--fg2);max-width:none;margin:0 auto;}
  .ct-lede b{color:var(--fg1);font-weight:600;}
  .ct-link{display:inline-block;margin-top:18px;font-size:12px;font-weight:700;letter-spacing:.06em;color:var(--cyan);border:1px solid var(--kickbrd);border-radius:9px;padding:11px 18px;transition:.16s;}
  .ct-link:hover{background:var(--barbg);}"""

    doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>arcs · public goods</title>
<meta name="description" content="Open, MIT-licensed tools built for our own work and published. The tools are open; the ARCS intelligence that orchestrates them stays private.">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
{TOKENS_CSS}
{CSS}
{GAL_CSS}
</style>
<script defer src="/_vercel/insights/script.js"></script>
</head>
<body>

{GOOD_HERO}

{body}

{GOOD_AFTER_BODY}<section class="compass-tie">
  <div class="wrap">
    <p class="ct-lede">These open tools feed the <b>ARCS compass</b>: the private intelligence that decides when, and for whom, a thing is ready to fire.</p>
    <a class="ct-link mono" href="https://arcs.care">see the compass →</a>
  </div>
</section>

{GOOD_TAIL}"""
    out = os.path.join(OUTDIR, "good.html")
    write_page(out, doc)
    print(f"rendered public/good.html  [{len(featured)} featured, "
          f"{len(minor)} also-in-toolkit, {len(soon_cards)} soon]")


def build_parser():
    import argparse
    ap = argparse.ArgumentParser(
        prog="connector_render.py",
        description="Render the ADR-056 connector fleet pages from _SEEDS SSOT.")
    ap.add_argument("--check", action="store_true",
                    help="render in memory; exit 1 if any committed page differs (writes nothing)")
    ap.add_argument("--self-test", action="store_true",
                    help="run the CLI in a throwaway project dir; never touches ROOT")
    ap.add_argument("repos", nargs="*",
                    help="tool(s) to render (default: every standalone tool), or the single word 'gallery'")
    return ap


def self_test():
    """Run the CLI in a temp CLAUDE_PROJECT_DIR seeded with copies of the SSOT + pages."""
    import tempfile, shutil, subprocess, hashlib
    me = os.path.abspath(__file__)
    fails = 0
    total = 0

    def check(name, ok):
        nonlocal fails, total
        total += 1
        print(("PASS " if ok else "FAIL ") + name)
        fails += 0 if ok else 1

    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "_SEEDS"))
        os.makedirs(os.path.join(tmp, "public"))
        shutil.copy2(DIST, os.path.join(tmp, "_SEEDS", "distribution.jsonl"))
        shutil.copy2(DATA, os.path.join(tmp, "_SEEDS", "connectors.json"))
        for n in os.listdir(OUTDIR):
            if n.endswith(".html"):
                shutil.copy2(os.path.join(OUTDIR, n), os.path.join(tmp, "public", n))
        env = dict(os.environ, CLAUDE_PROJECT_DIR=tmp)

        def run(*a):
            return subprocess.run([sys.executable, me, *a], env=env, cwd=tmp,
                                  capture_output=True, text=True)

        def snap():
            out = {}
            for d, _, fs in os.walk(tmp):
                for f in fs:
                    q = os.path.join(d, f)
                    out[q] = (hashlib.sha256(open(q, "rb").read()).hexdigest(),
                              os.stat(q).st_mtime_ns)
            return out

        before = snap()
        r = run("--check")
        check("--check runs (exit 0 or 1)", r.returncode in (0, 1))
        check("--check writes nothing", snap() == before)
        r = run("gallery", "--check")
        check("gallery --check runs (exit 0 or 1)", r.returncode in (0, 1))
        check("gallery --check writes nothing", snap() == before)
        check("unknown flag exits 2", run("--chek").returncode == 2)
        check("unknown flag writes nothing", snap() == before)
        check("unknown repo exits 2", run("no-such-tool").returncode == 2)
        check("gallery plus extra positional exits 2", run("gallery", "extra").returncode == 2)
        check("bad args write nothing", snap() == before)
        r = run("gallery")
        check("gallery write mode exits 0", r.returncode == 0)
        check("gallery write mode wrote public/good.html",
              os.path.exists(os.path.join(tmp, "public", "good.html")))
    print(f"connector_render self-test: {total - fails}/{total}")
    sys.exit(1 if fails else 0)


def main():
    global CHECK
    ap = build_parser()
    ns = ap.parse_args()
    if ns.self_test:
        if ns.check or ns.repos:
            ap.error("--self-test takes no other arguments")
        self_test()
    ssot = load_ssot()
    blob = json.load(open(DATA))
    tools = blob["tools"]
    CHECK = ns.check
    args = ns.repos

    if args == ["gallery"]:
        render_gallery(ssot, blob)
    else:
        # standalone deep pages: only tools whose group earns one.
        # Validate every name BEFORE rendering anything, so a typo never half-writes the fleet.
        want = args or [r for r, d in tools.items()
                        if d.get("group") in STANDALONE_GROUPS]
        for repo in want:
            if repo not in tools:
                ap.error(f"no copy block for '{repo}' in connectors.json")
            if repo not in ssot:
                ap.error(f"'{repo}' not in distribution.jsonl SSOT")
        for repo in want:
            render(repo, tools[repo], ssot[repo])

        # always refresh the gallery
        render_gallery(ssot, blob)

    if CHECK:
        for d in DRIFT:
            print(f"  drift: {d} differs from what connector_render.py renders")
        print(f"check: {len(DRIFT)} generated page(s) drifted")
        sys.exit(1 if DRIFT else 0)


if __name__ == "__main__":
    main()
