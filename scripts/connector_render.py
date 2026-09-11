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

Stdlib only.
"""
import json, os, sys, html

ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
DIST = os.path.join(ROOT, "_SEEDS/distribution.jsonl")
DATA = os.path.join(ROOT, "_SEEDS/connectors.json")
OUTDIR = os.path.join(ROOT, "public")

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


# ---- frozen house style: <style> block from resume-tailor.html, accents lifted to vars ----
CSS = """  :root{
    /* neutrals: canonical ARCS design-system tokens (WORLD.md / colors_and_type) */
    --bg:#020408;--surface:#0d1117;--elev:#131a24;--border:#1e293b;--border2:#2b3a4f;
    --fg1:#e2e8f0;--fg2:#94a3b8;--fg3:#64748b;--fg4:#4a5a6d;
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
  .hero{padding:66px 0 58px;}
  .kick{display:inline-flex;align-items:center;gap:9px;font-family:var(--mono);font-size:10px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:var(--cyan);border:1px solid rgba(0,240,255,.35);border-radius:999px;padding:6px 13px;}
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
  .sec-lbl .sub{font-family:var(--mono);font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:var(--fg4);margin-left:auto;}

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
  .oneshot .bar .l{font-family:var(--mono);font-size:10px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--cyan);}
  .oneshot .cp{font-family:var(--mono);font-size:10px;font-weight:700;letter-spacing:.06em;color:var(--fg3);border:1px solid var(--border2);background:var(--elev);border-radius:7px;padding:5px 11px;cursor:pointer;transition:.15s;}
  .oneshot .cp:hover{color:var(--cyan);border-color:var(--cyan);}
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
{CSS}
  :root{{{theme_vars(data.get('group','skill'))}}}
</style>
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
    with open(out, "w") as f:
        f.write(doc)
    chans = ", ".join(f"{c}✓" for c in live if c in data["install"])
    print(f"rendered public/{repo}.html  [{chans}]")


# tools that earn a standalone deep page; everyone else is a gallery card only.
STANDALONE_GROUPS = {"cli", "web"}
# tools with a hand-built page outside this renderer (do not re-render, but DO index on the gallery)
EXTERNAL_PAGES = {
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


def _card(name, line, chips, page, gh, group, live=True, variant="full"):
    t = THEMES.get(group, THEMES["skill"])
    accent = f"linear-gradient(90deg,{t['c1']},{t['c2']})"
    dim = "" if live else "opacity:.5;filter:saturate(.35);"
    chip_html = "".join(f'<span class="chip">{esc(c)}</span>' for c in chips)
    if live:
        primary = (f'<a class="clink" href="{esc(page)}">open ↗</a>' if page
                   else f'<a class="clink" href="{esc(gh)}">github ↗</a>')
        gh_link = f'<a class="cgh" href="{esc(gh)}">github</a>' if page else ""
        tag = ""
    else:
        primary = f'<a class="clink" href="{esc(gh)}">github ↗</a>'
        gh_link = ""
        tag = '<span class="soon">soon</span>'

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
FEATURED_ORDER = ["resume-tailor-skill", "rosetta-shell", "germinate", "arcs-field-scan"]


def render_gallery(ssot, blob):
    tools = blob["tools"]
    soon = blob.get("soon", {})

    # Build a uniform meta record per live repo (rendered tools + external pages).
    meta = {}  # repo -> {group, name, line, chips, page, gh}
    for repo, data in tools.items():
        g = data.get("group", "skill")
        url = ssot.get(repo, {}).get("url", "")
        gh = ("https://" + url) if url and not url.startswith("http") else url
        chips = [CHAN_CHIP.get(c, c) for c in live_channels(ssot.get(repo, {}))]
        if g == "skill":
            chips = ["skill"] + [c for c in chips if c != "clone"]
        page = f"https://{repo}.arcs.care" if g in STANDALONE_GROUPS else ""
        meta[repo] = dict(group=g, name=repo, line=first_sentence(data["desc"]),
                          chips=chips, page=page, gh=gh)
    for repo, ext in EXTERNAL_PAGES.items():
        url = ssot.get(repo, {}).get("url", "")
        gh = ("https://" + url) if url and not url.startswith("http") else url
        meta[repo] = dict(group=ext["group"], name=ext["name"], line=ext["line"],
                          chips=["plugin", "skill"], page=ext["page"], gh=gh)

    def card_for(repo, variant="full"):
        m = meta[repo]
        return _card(m["name"], m["line"], m["chips"], m["page"], m["gh"],
                     m["group"], True, variant)

    featured = [card_for(r) for r in FEATURED_ORDER if r in meta]
    minor_repos = [r for r in meta if r not in FEATURED_ORDER]
    minor = [card_for(r, "compact") for r in minor_repos]

    # soon (ready-not-live) — muted cards, github only, no install claim
    soon_cards = []
    for repo, s in soon.items():
        url = ssot.get(repo, {}).get("url", "")
        gh = ("https://" + url) if url and not url.startswith("http") else url
        soon_cards.append(_card(repo, s["line"], [s["chan"]], "", gh, s.get("group", "skill"), False))

    def block(label, sub, cards, grid="cards"):
        if not cards:
            return ""
        return (
            f'<section>\n  <div class="wrap">\n'
            f'    <div class="sec-lbl"><span class="n">◆</span><h2>{esc(label)}</h2>'
            f'<span class="sub">{esc(sub)}</span></div>\n'
            f'    <div class="{grid}">\n' + "\n".join(cards) + "\n    </div>\n  </div>\n</section>")

    body = "\n\n".join(x for x in [
        block("Featured", "fully baked · installable today", featured, "cards featured"),
        block("Also in the toolkit", "smaller Claude Code skills · clone and add", minor, "cards minor"),
        block("Coming soon", "built · not yet published", soon_cards, "cards minor"),
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
  .card.compact .cline{font-size:11.5px;margin-top:7px;}
  .card.compact .cfoot{padding:10px 14px;}
  .card{display:flex;flex-direction:column;border:1px solid var(--border);border-radius:14px;overflow:hidden;background:linear-gradient(165deg,rgba(255,255,255,.02),rgba(0,0,0,.18));transition:.16s;}
  .card:hover{border-color:var(--border2);transform:translateY(-2px);}
  .cbar{height:3px;width:100%;}
  .cbody{padding:16px 17px 6px;flex:1;}
  .chead{display:flex;align-items:center;justify-content:space-between;gap:8px;}
  .cname{font-size:14px;font-weight:700;color:var(--fg1);letter-spacing:-.01em;}
  .soon{font-family:var(--mono);font-size:9px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--fg4);border:1px solid var(--border2);border-radius:999px;padding:3px 8px;}
  .cline{font-size:12.5px;line-height:1.55;color:var(--fg2);margin-top:9px;}
  .chips{display:flex;gap:6px;flex-wrap:wrap;margin-top:13px;}
  .chip{font-family:var(--mono);font-size:9.5px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;color:var(--fg3);border:1px solid var(--border);border-radius:6px;padding:3px 7px;}
  .cfoot{display:flex;gap:16px;align-items:center;padding:13px 17px;border-top:1px solid var(--border);margin-top:12px;}
  .clink{font-family:var(--mono);font-size:11px;font-weight:700;letter-spacing:.04em;color:var(--cyan);}
  .cgh{font-family:var(--mono);font-size:11px;color:var(--fg4);}
  .cgh:hover{color:var(--fg2);}
  .gcount{font-family:var(--mono);font-size:11px;color:var(--fg4);letter-spacing:.06em;margin-left:auto;}
  .compass-tie{border-bottom:1px solid var(--border);
    background:radial-gradient(700px 300px at 50% -20%,var(--glowA),transparent 60%);}
  .compass-tie .wrap{padding-top:44px;padding-bottom:44px;text-align:center;}
  .ct-lede{font-size:clamp(16px,2.4vw,20px);line-height:1.55;color:var(--fg2);max-width:640px;margin:0 auto;}
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
{CSS}
{GAL_CSS}
</style>
</head>
<body>

<header>
  <div class="wrap hero">
    <span class="kick"><span class="dot"></span>the arcs family · public goods</span>
    <h1>Open tools, <span class="g">honest by default.</span></h1>
    <p class="lede">Small, MIT-licensed tools we built for our own work and published as they proved out. The tools are <b>open</b>; the ARCS intelligence that orchestrates them stays private. Nothing here claims an install path that is not live.</p>
  </div>
</header>

{body}

<section class="compass-tie">
  <div class="wrap">
    <p class="ct-lede">These open tools feed the <b>ARCS compass</b>: the private intelligence that decides when, and for whom, a thing is ready to fire.</p>
    <a class="ct-link mono" href="https://arcs.care">see the compass →</a>
  </div>
</section>

<footer>
  <div class="wrap foot">
    <span>a public-goods index by <a href="https://arcs.care">ARCS</a> · MIT</span>
    <span><a href="https://github.com/flashesofbrilliance">github</a> · <a href="https://arcs.care">arcs.care</a></span>
  </div>
</footer>

</body>
</html>
"""
    out = os.path.join(OUTDIR, "good.html")
    with open(out, "w") as f:
        f.write(doc)
    print(f"rendered public/good.html  [{len(featured)} featured, "
          f"{len(minor)} also-in-toolkit, {len(soon_cards)} soon]")


def main():
    ssot = load_ssot()
    blob = json.load(open(DATA))
    tools = blob["tools"]
    args = sys.argv[1:]

    if args == ["gallery"]:
        render_gallery(ssot, blob)
        return

    # standalone deep pages: only tools whose group earns one
    want = args or [r for r, d in tools.items()
                    if d.get("group") in STANDALONE_GROUPS]
    for repo in want:
        if repo not in tools:
            raise SystemExit(f"no copy block for '{repo}' in connectors.json")
        if repo not in ssot:
            raise SystemExit(f"'{repo}' not in distribution.jsonl SSOT")
        render(repo, tools[repo], ssot[repo])

    # always refresh the gallery
    render_gallery(ssot, blob)


if __name__ == "__main__":
    main()
