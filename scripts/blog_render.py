#!/usr/bin/env python3
"""blog_render — render a Notes-from-the-Trenches markdown post to a FieldOS-styled static HTML page.

Class-not-instance: the template is fixed (FieldOS tokens, thread colors, plain-terms asides);
each post is a two-second run. Stdlib only, zero LLM in the runtime path.

Usage: python3 scripts/blog_render.py <post.md> <out.html>
"""
import html as h
import re, sys
from pathlib import Path

# Omakase / Louisville variant of the FieldOS design system (public/omakase/index.html tokens).
# The omakase accent triad (red/gold/verm) IS the essay's braid — same three threads.
TOKENS = {"bg": "#020408", "surface": "#0d1117", "border": "#1e293b", "text": "#e2e8f0",
          "muted": "#94a3b8", "dimmed": "#8593a6", "cyan": "#00F0FF", "green": "#00FF9D",
          "gold": "#FFD700", "red": "#FF4D6D", "verm": "#ff9d3c"}


def inline(s: str) -> str:
    # preserve authored <a href> anchors; escape everything else
    anchors = []
    def stash(m):
        anchors.append(m.group(0)); return f"\x00{len(anchors)-1}\x00"
    s = re.sub(r'<a href="[^"]+">[^<]+</a>', stash, s)
    s = h.escape(s, quote=False)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", s)
    for i, a in enumerate(anchors):
        # links styled by the stylesheet (var(--cyan)); keep markup clean
        s = s.replace(f"\x00{i}\x00", a)
    return s


SPARK = {"r": "#FF4D6D", "g": "#FFD700", "v": "#FF6B2C"}  # verm stepped from #ff9d3c for dE (dataviz-validated)
SPARK_NAME = {"r": "red · gates", "g": "gold · assets", "v": "vermillion · fusion"}


def _node(x, y, cls, color):
    if cls == "r":   # diamond
        return f'<path d="M{x} {y-6} L{x+6} {y} L{x} {y+6} L{x-6} {y} Z" fill="{color}"/>'
    if cls == "v":   # square
        return f'<rect x="{x-5}" y="{y-5}" width="10" height="10" fill="{color}"/>'
    return f'<circle cx="{x}" cy="{y}" r="5.5" fill="{color}"/>'


def sparkline_svg(text):
    text = re.sub(r"^.*?Sparkline:\s*", "", text)
    stops = []
    for part in text.split("\u2192"):
        m = re.search(r"(.+?)\s*\^([rgv])\s*$", part.strip().rstrip(".*"))
        if m:
            stops.append((m.group(1).strip(), m.group(2)))
    if not stops:
        return None
    step, y = 118, 56
    W = step * (len(stops) - 1) + 80
    parts = [f'<line x1="40" y1="{y}" x2="{W-40}" y2="{y}" stroke="#1e293b" stroke-width="2"/>']
    parts.insert(0, '<defs><filter id="underlit" x="-80%" y="-80%" width="260%" height="260%">'
                    '<feDropShadow dx="0" dy="1.5" stdDeviation="3" flood-opacity="0.55"/></filter></defs>')
    for i, (label, cls) in enumerate(stops):
        x = 40 + i * step
        color = SPARK[cls]
        ly = 24 if i % 2 == 0 else 92
        anchor = "start" if i == 0 else ("end" if i == len(stops) - 1 else "middle")
        glow = f'<circle cx="{x}" cy="{y+3}" r="9" fill="{color}" opacity="0.18" filter="url(#underlit)"/>'
        parts.append(f'<g><title>{i+1}. {h.escape(label)} ({SPARK_NAME[cls]})</title>{glow}'
                     f'{_node(x, y, cls, color)}'
                     f'<text x="{x}" y="{ly}" text-anchor="{anchor}" style="font-family:var(--font-mono)" '
                     f'font-size="10.5" fill="#94a3b8">{h.escape(label)}</text></g>')
    small = {c: _node(6, 6, c, SPARK[c]).replace('r="5.5"', 'r="4.5"') for c in ("r", "g", "v")}
    legend = " &nbsp; ".join(
        f'<svg width="12" height="12" viewBox="0 0 12 12" style="vertical-align:-1px">{small[c]}</svg> {SPARK_NAME[c]}'
        for c in ("r", "g", "v"))
    return (f'<figure style="margin:2.2em 0 1.6em" role="img" aria-label="Invention sparkline: {len(stops)} stops from cold DM to witnessed law">'
            f'<div style="overflow-x:auto;padding-bottom:4px;scrollbar-color:#1e293b #020408"><svg width="{W}" height="112" viewBox="0 0 {W} 112" '
            f'font-family="ui-monospace,monospace">{"".join(parts)}</svg></div>'
            f'<figcaption class="stitch" style="margin-top:.4em">{legend}</figcaption></figure>')


BRAID = ('<svg width="200" height="36" viewBox="0 0 200 36" aria-hidden="true" style="display:block;margin:.2em 0 1.2em">'
         f'<path d="M4 8 C 60 8, 80 28, 130 28 S 190 18, 196 18" stroke="{SPARK["r"]}" stroke-width="2.5" fill="none" opacity=".9"/>'
         f'<path d="M4 18 C 60 18, 80 8, 130 8 S 190 18, 196 18" stroke="{SPARK["g"]}" stroke-width="2.5" fill="none" opacity=".9"/>'
         f'<path d="M4 28 C 60 28, 80 18, 130 18 S 190 18, 196 18" stroke="{SPARK["v"]}" stroke-width="2.5" fill="none" opacity=".9"/></svg>')


ENDMARK = ('<p class="endmark" aria-hidden="true"><svg width="46" height="12" viewBox="0 0 46 12">'
           f'<path d="M6 0 L12 6 L6 12 L0 6 Z" fill="{SPARK["r"]}"/>'
           f'<circle cx="23" cy="6" r="5" fill="{SPARK["g"]}"/>'
           f'<rect x="36" y="1" width="10" height="10" fill="{SPARK["v"]}"/></svg></p>')


def render(md: str) -> str:
    out = []
    titled = False
    seen_h2 = False
    dropped_cap = False
    P = 'style="margin:0 0 1.15em;line-height:1.75"'
    for block in re.split(r"\n\s*\n", md.strip()):
        b = block.strip()
        if not b:
            continue
        if b == "---":
            out.append(f'<hr style="border:none;border-top:1px solid var(--border);margin:2.5em 0">')
        elif b.startswith("#### "):
            out.append(f'<h4 style="margin:1.6em 0 .5em;font-family:var(--font-mono);font-size:.7rem;font-weight:700;letter-spacing:var(--track-widest);text-transform:uppercase;line-height:1.2;color:var(--fg4)">{inline(b[5:])}</h4>')
        elif b.startswith("### "):
            out.append(f'<h3 style="margin:1.8em 0 .6em;font-size:1.125rem;font-weight:600;line-height:1.3;color:var(--fg1)">{inline(b[4:])}</h3>')
        elif b.startswith("# "):
            out.append(f'<p style="margin:0 0 .4em;font-size:.75rem;letter-spacing:var(--track-widest);text-transform:uppercase;font-weight:700;font-family:var(--font-mono);color:var(--cyan)">{inline(b[2:])}</p>')
        elif b.startswith("## ") and not titled:
            titled = True
            out.append(f'<h1 style="margin:0 0 1.2em;font-size:clamp(2rem,5vw,3rem);line-height:1.15;letter-spacing:-0.02em;font-weight:600;color:var(--fg1)">{inline(b[3:])}</h1>')
        elif b.startswith("## "):
            seen_h2 = True
            out.append(f'<h2 style="margin:2.4em 0 .8em;font-size:1.375rem;font-weight:600;line-height:1.25;color:var(--fg1)">{inline(b[3:])}</h2>')
            if "braid" in b.lower():
                out.append(BRAID)
        elif b.startswith("— *Sparkline:"):
            svg = sparkline_svg(b)
            out.append(svg if svg else f"<p {P}>{inline(b)}</p>")
        elif b.startswith("— *"):
            color = TOKENS["red"] if "Red" in b[:14] else TOKENS["gold"] if "Gold" in b[:14] else TOKENS["verm"]
            out.append(f'<p class="stitch"><span style="color:{color}" aria-hidden="true">&#9473;&#9473;</span> {inline(b[2:])}</p>')
        elif b.startswith(">> "):
            q = " ".join(l.lstrip("> ").strip() for l in b.splitlines())
            out.append(f'<blockquote class="pull">{inline(q)}</blockquote>')
        elif b.startswith("> "):
            q = " ".join(l.lstrip("> ").strip() for l in b.splitlines())
            out.append(f'<blockquote class="bq">{inline(q)}</blockquote>')
        elif b.startswith("*") and b.endswith("*") and "\n" not in b:
            body = inline(b[1:-1])
            if not seen_h2:
                out.append(f'<p class="standfirst">{body}</p>')
            else:
                cls = "plain" if "In plain terms" in b else "aside"
                out.append(f'<div class="{cls}">{body}</div>')
        elif b.startswith("- "):
            items = "".join(f'<li style="margin:0 0 .8em;line-height:1.7">{inline(i[2:].strip())}</li>'
                            for i in re.split(r"\n(?=- )", b))
            out.append(f'<ul style="margin:0 0 1.15em;padding-left:1.3em">{items}</ul>')
        else:
            txt = inline(' '.join(l.strip() for l in b.splitlines()))
            if seen_h2 and not dropped_cap and len(b) > 180:
                out.append(f'<p class="dropcap" {P}>{txt}</p>')
                dropped_cap = True
            else:
                out.append(f"<p {P}>{txt}</p>")
    out.append(ENDMARK)
    return "\n".join(out)


def ladder(dst_name: str, out_dir: Path) -> str:
    m = re.match(r"blog-nftt-(.+?)-(exec|brief|full)\.html$", dst_name)
    if not m:
        return ""
    slug, tier = m.groups()
    base = f"/blog/nftt/{slug}"
    tiers = [("exec", "90-second", base), ("brief", "operational", f"{base}/brief"), ("full", "surgical", f"{base}/full")]
    # Only surface tiers whose HTML actually exists on disk; a dead depth link is a broken path.
    tiers = [(t, label, href) for (t, label, href) in tiers
             if t == tier or (out_dir / f"blog-nftt-{slug}-{t}.html").exists()]
    if len(tiers) < 2:  # single-tier post: no ladder rather than a one-item nav
        return ""
    links = " · ".join(
        f'<span style="color:var(--fg1);font-weight:600">{label}</span>' if t == tier
        else f'<a style="text-decoration:none" href="{href}">{label}</a>'
        for t, label, href in tiers)
    return (f'<nav style="margin:0 0 2.2em;padding:.55em .9em;background:var(--glass-surface),var(--surface);'
            f'border:1px solid var(--border);border-radius:var(--radius-md);box-shadow:var(--emboss);font-family:var(--font-mono);'
            f'font-size:.78rem;color:var(--fg3)">depth: {links}</nav>')


PAGE = """<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="theme-color" content="#020408">
<meta name="description" content="{desc}">
<script defer src="/_vercel/insights/script.js"></script>
</head>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');
  /* :root block imported verbatim from the DS SSOT (be620c0c · colors_and_type.css).
     Re-sync = replace this block. SVG marks keep literal hexes (attr context). */
  :root {{
    --bg:#020408; --surface:#0d1117; --elevated:#111827; --border:#1e293b;
    --fg1:#e2e8f0; --fg2:#94a3b8; --fg3:#8593a6; --fg4:#707e92;
    --cyan:#00F0FF; --green:#00FF9D; --gold:#FFD700; --orange:#ff9d3c; --red:#FF4D6D;
    --font-sans:'Inter',system-ui,-apple-system,sans-serif;
    --font-mono:'JetBrains Mono','IBM Plex Mono',ui-monospace,'SFMono-Regular',Menlo,monospace;
    --track-widest:0.14em; --radius-sm:6px; --radius-md:10px;
    --emboss:inset 0 1px 0 rgba(255,255,255,0.10), inset 0 -1px 1px rgba(0,0,0,0.55), 0 2px 6px rgba(0,0,0,0.45);
    --glass-surface:linear-gradient(160deg, rgba(255,255,255,0.06), rgba(255,255,255,0.01) 38%, rgba(0,0,0,0.18));
  }}
  a {{ color: var(--cyan); text-decoration: underline; text-underline-offset: 2px; }}
  a:hover {{ color: var(--fg1); }}
  a:focus-visible {{ outline: 2px solid var(--cyan); outline-offset: 2px; border-radius: 2px; }}
  ::selection {{ background: rgba(0,240,255,.25); }}
  .aside, .plain {{ margin: 1.4em 0; padding: 1em 1.2em; border-radius: var(--radius-md);
    background: var(--glass-surface), var(--surface);
    border: 1px solid var(--border); box-shadow: var(--emboss);
    font-style: italic; color: var(--fg2); line-height: 1.7; }}
  .plain {{ border-color: rgba(0,255,157,.22);
    background: linear-gradient(160deg, rgba(0,255,157,0.05), rgba(255,255,255,0.01) 38%, rgba(0,0,0,0.18)), var(--surface); }}
  .stitch {{ margin: 1.5em 0; font-family: var(--font-mono); font-size: .82rem;
    color: var(--fg2); letter-spacing: .01em; }}
  .standfirst {{ font-size: 1.125rem; line-height: 1.6; font-weight: 500; color: var(--fg2);
    margin: 0 0 1.8em; }}  /* .arcs-lead: medium weight, no italic */
  .bq {{ margin: 1.6em 0; padding: .2em 0 .2em 1.1em; border-left: 1px solid var(--border);
    font-size: 1rem; font-weight: 400; font-style: italic; line-height: 1.7; color: var(--fg2); }}
  .dropcap::first-letter {{ float: left; font-size: 3.4em; line-height: .82; padding: .06em .14em 0 0;
    font-weight: 600; color: var(--fg1); }}
  .pull {{ margin: 2.2em 0; padding: 1.15em 0; border-top: 1px solid var(--border);
    border-bottom: 1px solid var(--border); font-size: 1.5rem; line-height: 1.4; font-weight: 600;
    color: var(--fg1); letter-spacing: -0.015em; }}
  .pull::before {{ content: ""; display: block; width: 34px; height: 2px; margin-bottom: .8em;
    background: linear-gradient(90deg, var(--red), var(--gold), #FF6B2C); }}
  h2::before {{ content: ""; display: block; width: 48px; height: 2px; margin: 0 0 .9em;
    background: linear-gradient(90deg, var(--red), var(--gold), #FF6B2C); }}
  .endmark {{ margin: 2.6em 0 0; }}

  nav a {{ text-decoration: none; }}
  nav a:hover {{ text-decoration: underline; }}
</style>
<body style="margin:0;background:var(--bg);color:var(--fg1);font-size:17px;font-family:var(--font-sans);overflow-wrap:break-word">
<main style="max-width:68ch;margin:0 auto;padding:64px 22px 96px">
{ladder}<article>
{body}
</article><footer style="margin-top:4em;padding-top:1.5em;border-top:1px solid var(--border);font-size:.82rem;color:var(--fg3);font-family:var(--font-mono)">
NFTT · notes from the trenches · <a href="https://good.arcs.care">good.arcs.care</a> · every claim traces to a commit
</footer>
</main></body></html>
"""

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__); sys.exit(2)
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    md = src.read_text()
    title = next((l[2:].strip() for l in md.splitlines() if l.startswith("# ")), src.stem)
    m = re.search(r"^## (.+)$", md, re.M)
    subtitle = m.group(1) if m else ""
    dst.write_text(PAGE.format(title=h.escape(f"{subtitle} · NFTT"), desc=h.escape(title),
                               body=render(md), ladder=ladder(dst.name, dst.parent), **TOKENS))
    print(f"rendered {dst} ({dst.stat().st_size} bytes)")
