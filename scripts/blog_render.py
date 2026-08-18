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
          "muted": "#94a3b8", "dimmed": "#64748b", "cyan": "#00F0FF", "green": "#00FF9D",
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
        a = re.sub(r'<a href="', '<a style="color:%s;text-decoration:underline" href="' % TOKENS["cyan"], a)
        s = s.replace(f"\x00{i}\x00", a)
    return s


def render(md: str) -> str:
    out = []
    P = 'style="margin:0 0 1.15em;line-height:1.75"'
    for block in re.split(r"\n\s*\n", md.strip()):
        b = block.strip()
        if not b:
            continue
        if b == "---":
            out.append(f'<hr style="border:none;border-top:1px solid {TOKENS["border"]};margin:2.5em 0">')
        elif b.startswith("# "):
            out.append(f'<p style="margin:0 0 .4em;font-size:.75rem;letter-spacing:.12em;text-transform:uppercase;font-family:ui-monospace,monospace;color:{TOKENS["cyan"]}">{inline(b[2:])}</p>')
        elif b.startswith("## ") and not out or b.startswith("## ") and len([x for x in out if "<h1" in x]) == 0:
            out.append(f'<h1 style="margin:0 0 1.2em;font-size:2rem;line-height:1.25;color:{TOKENS["text"]}">{inline(b[3:])}</h1>')
        elif b.startswith("## "):
            out.append(f'<h2 style="margin:2.2em 0 .8em;font-size:1.3rem;color:{TOKENS["text"]}">{inline(b[3:])}</h2>')
        elif b.startswith("— *"):
            color = TOKENS["red"] if "Red" in b[:14] else TOKENS["gold"] if "Gold" in b[:14] else TOKENS["verm"]
            out.append(f'<p class="stitch"><span style="color:{color}" aria-hidden="true">&#9473;&#9473;</span> {inline(b[2:])}</p>')
        elif b.startswith("*") and b.endswith("*") and "\n" not in b:
            body = inline(b[1:-1])
            aside = "In plain terms" in b
            cls = "plain" if aside else "aside"
            out.append(f'<div class="{cls}">{body}</div>')
        elif b.startswith("- "):
            items = "".join(f'<li style="margin:0 0 .8em;line-height:1.7">{inline(i[2:].strip())}</li>'
                            for i in re.split(r"\n(?=- )", b))
            out.append(f'<ul style="margin:0 0 1.15em;padding-left:1.3em">{items}</ul>')
        else:
            out.append(f"<p {P}>{inline(' '.join(l.strip() for l in b.splitlines()))}</p>")
    return "\n".join(out)


def ladder(dst_name: str) -> str:
    m = re.match(r"blog-nftt-(.+?)-(exec|brief|full)\.html$", dst_name)
    if not m:
        return ""
    slug, tier = m.groups()
    base = f"/blog/nftt/{slug}"
    tiers = [("exec", "90-second", base), ("brief", "operational", f"{base}/brief"), ("full", "surgical", f"{base}/full")]
    links = " · ".join(
        f'<span style="color:{TOKENS["text"]};font-weight:600">{label}</span>' if t == tier
        else f'<a style="color:{TOKENS["cyan"]};text-decoration:none" href="{href}">{label}</a>'
        for t, label, href in tiers)
    return (f'<nav style="margin:0 0 2.2em;padding:.55em .9em;background:{TOKENS["surface"]};'
            f'border:1px solid {TOKENS["border"]};border-radius:6px;font-family:ui-monospace,monospace;'
            f'font-size:.78rem;color:{TOKENS["muted"]}">depth: {links}</nav>')


PAGE = """<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="theme-color" content="#020408">
<meta name="description" content="{desc}">
</head>
<style>
  a {{ color: {cyan}; text-decoration: underline; text-underline-offset: 2px; }}
  a:hover {{ color: {text}; }}
  a:focus-visible {{ outline: 2px solid {cyan}; outline-offset: 2px; border-radius: 2px; }}
  ::selection {{ background: rgba(0,240,255,.25); }}
  .aside, .plain {{ margin: 1.4em 0; padding: .95em 1.15em; background: {surface};
    border: 1px solid {border}; border-radius: 6px; font-style: italic; color: {muted}; line-height: 1.7; }}
  .plain {{ border-color: rgba(0,255,157,.28); background: rgba(0,255,157,.04); }}
  .stitch {{ margin: 1.5em 0; font-family: ui-monospace, monospace; font-size: .82rem;
    color: {muted}; letter-spacing: .01em; }}
  nav a {{ text-decoration: none; }}
  nav a:hover {{ text-decoration: underline; }}
</style>
<body style="margin:0;background:{bg};color:{text};font-size:17px;font-family:Inter,system-ui,-apple-system,sans-serif;overflow-wrap:break-word">
<main style="max-width:68ch;margin:0 auto;padding:64px 22px 96px">
{ladder}{body}
<footer style="margin-top:4em;padding-top:1.5em;border-top:1px solid {border};font-size:.82rem;color:{muted};font-family:ui-monospace,monospace">
NFTT · notes from the trenches · <a style="color:{cyan}" href="https://good.arcs.care">good.arcs.care</a> · every claim traces to a commit
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
                               body=render(md), ladder=ladder(dst.name), **TOKENS))
    print(f"rendered {dst} ({dst.stat().st_size} bytes)")
