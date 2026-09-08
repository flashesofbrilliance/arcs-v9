#!/usr/bin/env python3
"""story_render — render a data-driven ARCS story (Notes-from-the-Trenches class) to FieldOS HTML.

The extensible successor to blog_render.py. Separates the SYSTEM from the VOICE:

  * VOICE  — the essay body stays prose (markdown block grammar). You write a story, not a form.
  * SYSTEM — the structured envelope is DATA: a `---story---` JSON frontmatter block declaring
             the threads (palette + names + node shapes), the narrative arc (sparkline stops),
             the tier, and metadata. Threads are no longer hardcoded red/gold/verm; a story
             picks its own, from two to N, so the template extends past NFTT to any threaded
             trench story.

Bierut's rule, made mechanical: an arc renders only if it passes a five-second legibility
contract. A long arc auto-reflows from a cramped horizontal sparkline to a vertical ladder
(one stop per row, full-size labels) rather than shipping texture the reader cannot parse.

Stdlib only, zero LLM in the runtime path. Class-not-instance: the engine is fixed, each
story is a data envelope + prose.

Usage: python3 scripts/story_render.py <story.md> <out.html>
"""
import html as h
import json
import math
import re
import sys
from pathlib import Path

VOID = "#020408"  # the background every thread color must survive on


def _luminance(hexstr):
    r, g, b = (int(hexstr[i:i + 2], 16) / 255 for i in (1, 3, 5))
    lin = lambda v: v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    R, G, B = lin(r), lin(g), lin(b)
    return 0.2126 * R + 0.7152 * G + 0.0722 * B


def contrast(a, b):
    la, lb = _luminance(a), _luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)

# ---- FieldOS design tokens (DS SSOT be620c0c · colors_and_type.css). Re-sync = replace. ----
CSS_ROOT = """
    --bg:#020408; --surface:#0d1117; --elevated:#111827; --border:#1e293b;
    --fg1:#e2e8f0; --fg2:#94a3b8; --fg3:#8593a6; --fg4:#707e92;
    --cyan:#00F0FF; --green:#00FF9D; --gold:#FFD700; --orange:#ff9d3c; --red:#FF4D6D;
    --font-sans:'Inter',system-ui,-apple-system,sans-serif;
    --font-mono:'JetBrains Mono','IBM Plex Mono',ui-monospace,'SFMono-Regular',Menlo,monospace;
    --track-widest:0.14em; --radius-sm:6px; --radius-md:10px;
    --emboss:inset 0 1px 0 rgba(255,255,255,0.10), inset 0 -1px 1px rgba(0,0,0,0.55), 0 2px 6px rgba(0,0,0,0.45);
    --glass-surface:linear-gradient(160deg, rgba(255,255,255,0.06), rgba(255,255,255,0.01) 38%, rgba(0,0,0,0.18));
"""

# Five-second-test legibility contract for the arc. Above this stop count, a horizontal
# sparkline crams labels below readable size, so the arc reflows to a vertical ladder.
ARC_MAX_HORIZONTAL_STOPS = 6
ARC_MAX_LABEL_CHARS = 24  # a horizontal label longer than this overflows the column; force the ladder
ARC_LABEL_PX = 12.5  # rendered mono label floor; below this the arc is texture, not information


class StoryError(ValueError):
    """A story that cannot honestly render (bad envelope, undefined thread, illegible arc)."""


def inline(s: str) -> str:
    anchors = []
    def stash(m):
        anchors.append(m.group(0)); return f"\x00{len(anchors)-1}\x00"
    s = re.sub(r'<a href="[^"]+">[^<]+</a>', stash, s)
    s = h.escape(s, quote=False)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", s)
    for i, a in enumerate(anchors):
        s = s.replace(f"\x00{i}\x00", a)
    return s


# ---------------------------------------------------------------- envelope ---
def parse_story(text: str):
    """Split a story file into (envelope dict, prose body). Envelope is a JSON block:
       ---story---\n{ ... }\n---/story---  at the top of the file."""
    m = re.match(r"\s*---story---\s*\n(.*?)\n---/story---\s*\n(.*)$", text, re.S)
    if not m:
        raise StoryError("missing ---story--- envelope: a data-driven story declares its "
                         "threads and arc as JSON frontmatter (see the schema).")
    try:
        env = json.loads(m.group(1))
    except json.JSONDecodeError as e:
        raise StoryError(f"story envelope is not valid JSON: {e}")
    threads = env.get("threads")
    if not threads or len(threads) < 2:
        raise StoryError("a story needs at least two threads (the braid). Declare them in "
                         "the envelope with id, hex, name, and shape.")
    seen = set()
    for t in threads:
        for k in ("id", "hex", "name", "shape"):
            if k not in t:
                raise StoryError(f"thread {t.get('id','?')} missing '{k}'")
        if t["shape"] not in ("diamond", "circle", "square"):
            raise StoryError(f"thread {t['id']} shape must be diamond|circle|square")
        # hex is the one field that reaches an HTML/SVG attribute sink; a strict pattern here
        # closes the stored-XSS vector AND enforces the schema's #RRGGBB claim.
        if not re.fullmatch(r"#[0-9A-Fa-f]{6}", t["hex"]):
            raise StoryError(f"thread {t['id']} hex must be #RRGGBB, got {t['hex']!r}")
        if not re.fullmatch(r"[a-z][a-z0-9]*", t["id"]):
            raise StoryError(f"thread id {t['id']!r} must match [a-z][a-z0-9]* (referenced by arc stops)")
        # earned fidelity: a node the reader cannot see must not ship as if legible.
        if contrast(t["hex"], VOID) < 3.0:
            raise StoryError(f"thread {t['id']} hex {t['hex']} fails contrast on the void "
                             f"({contrast(t['hex'], VOID):.1f}:1, needs >= 3:1)")
        if len(t["name"]) > 40:
            raise StoryError(f"thread {t['id']} name too long ({len(t['name'])} chars, max 40)")
        if t["id"] in seen:
            raise StoryError(f"duplicate thread id '{t['id']}': ids must be unique")
        seen.add(t["id"])
    # Eager arc validation: a broken arc is refused whether or not it is ever placed.
    arc = env.get("arc")
    if arc:
        ids = {t["id"] for t in threads}
        for s in arc.get("stops", []):
            if s.get("thread") not in ids:
                raise StoryError(f"arc stop '{s.get('label','?')}' references undefined thread "
                                 f"'{s.get('thread')}'")
    return env, m.group(2)


# ------------------------------------------------------------------- marks ---
def _node(x, y, shape, color, r=5.5):
    if shape == "diamond":
        return f'<path d="M{x} {y-r-.5} L{x+r+.5} {y} L{x} {y+r+.5} L{x-r-.5} {y} Z" fill="{color}"/>'
    if shape == "square":
        return f'<rect x="{x-r+.5}" y="{y-r+.5}" width="{2*r-1}" height="{2*r-1}" fill="{color}"/>'
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}"/>'


def thread_legend(threads):
    """P1 fix: give the reader the thread key BEFORE the first stitch, so the code is
       legible when it starts carrying weight."""
    chips = []
    for t in threads:
        mark = _node(7, 7, t["shape"], t["hex"], r=4.5)
        chips.append(f'<span style="white-space:nowrap"><svg width="14" height="14" viewBox="0 0 14 14" '
                     f'style="vertical-align:-2px;margin-right:.35em">{mark}</svg>{h.escape(t["name"])}</span>')
    return ('<div class="threadkey" role="img" aria-label="Thread key">'
            + ' &nbsp;&nbsp; '.join(chips) + '</div>')


def arc_horizontal(stops, threads, caption):
    tmap = {t["id"]: t for t in threads}
    step, y = 122, 56
    W = step * (len(stops) - 1) + 96
    parts = ['<defs><filter id="underlit" x="-80%" y="-80%" width="260%" height="260%">'
             '<feDropShadow dx="0" dy="1.5" stdDeviation="3" flood-opacity="0.55"/></filter></defs>',
             f'<line x1="48" y1="{y}" x2="{W-48}" y2="{y}" stroke="#1e293b" stroke-width="2"/>']
    for i, s in enumerate(stops):
        t = tmap[s["thread"]]
        x = 48 + i * step
        ly = 26 if i % 2 == 0 else 92
        anchor = "start" if i == 0 else ("end" if i == len(stops) - 1 else "middle")
        glow = f'<circle cx="{x}" cy="{y+3}" r="9" fill="{t["hex"]}" opacity="0.18" filter="url(#underlit)"/>'
        parts.append(f'<g><title>{i+1}. {h.escape(s["label"])} ({h.escape(t["name"])})</title>{glow}'
                     f'{_node(x, y, t["shape"], t["hex"])}'
                     f'<text x="{x}" y="{ly}" text-anchor="{anchor}" style="font-family:var(--font-mono)" '
                     f'font-size="{ARC_LABEL_PX}" fill="#94a3b8">{h.escape(s["label"])}</text></g>')
    return (f'<figure class="arc" role="img" aria-label="{h.escape(caption)}: {len(stops)} stops">'
            f'<div style="overflow-x:auto;padding-bottom:4px;scrollbar-color:#1e293b #020408">'
            f'<svg width="{W}" height="118" viewBox="0 0 {W} 118" font-family="ui-monospace,monospace">'
            f'{"".join(parts)}</svg></div></figure>')


def arc_ladder(stops, threads, caption):
    """The five-second-test-passing form for long arcs: a vertical timeline, one stop per row,
       full-size labels, a spine connecting the nodes. Reads like a list, legible on any width."""
    tmap = {t["id"]: t for t in threads}
    rows = []
    for i, s in enumerate(stops):
        t = tmap[s["thread"]]
        mark = _node(9, 9, t["shape"], t["hex"], r=5.5)
        spine = "" if i == len(stops) - 1 else '<span class="arc-spine" aria-hidden="true"></span>'
        # show the ROLE (the meaning half of the name), not the color-name: the glyph already
        # carries the color, so a colored word repeating the color would add nothing.
        role = t["name"].split("·")[1].strip() if "·" in t["name"] else t["name"].strip()
        rows.append(
            f'<li class="arc-row"><span class="arc-mark">'
            f'<svg width="18" height="18" viewBox="0 0 18 18">{mark}</svg>{spine}</span>'
            f'<span class="arc-label">{h.escape(s["label"])}</span>'
            f'<span class="arc-thread" style="color:{t["hex"]}">{h.escape(role)}</span></li>')
    return (f'<figure class="arc arc-ladder" role="img" aria-label="{h.escape(caption)}: {len(stops)} stops">'
            f'<ol class="arc-list">{"".join(rows)}</ol></figure>')


def render_arc(env, threads):
    arc = env.get("arc")
    if not arc or not arc.get("stops"):
        return None
    stops = arc["stops"]
    tmap = {t["id"] for t in threads}
    for s in stops:
        if s.get("thread") not in tmap:
            raise StoryError(f"arc stop '{s.get('label','?')}' references undefined thread "
                             f"'{s.get('thread')}'")
    caption = arc.get("caption", "the arc")
    # Bierut legibility gate, both axes: reflow to the ladder past the stop COUNT or when any
    # label is too long to sit under a horizontal node without overflowing the column.
    longest = max((len(s["label"]) for s in stops), default=0)
    if len(stops) <= ARC_MAX_HORIZONTAL_STOPS and longest <= ARC_MAX_LABEL_CHARS:
        # horizontal nodes carry no words, so they need the legend beneath them.
        return f'{arc_horizontal(stops, threads, caption)}<figcaption class="arc-cap">{thread_legend(threads)}</figcaption>'
    # ladder rows are self-labeling (each names its thread), so no trailing legend.
    return arc_ladder(stops, threads, caption)


def braid_svg(threads):
    # A genuine weave, driven by the actual threads: N phase-offset sinusoids that repeatedly
    # cross, so adjacent strands interlace instead of merging to one point. Count = len(threads).
    n, W, H, amp, period = len(threads), 200, 36, 9, 88
    mid = H / 2
    parts = []
    for i, t in enumerate(threads):
        phase = i * (2 * math.pi / n)
        pts = " ".join(f"{x},{mid + amp * math.sin((x / period) * 2 * math.pi + phase):.1f}"
                       for x in range(0, W + 1, 6))
        parts.append(f'<polyline points="{pts}" fill="none" stroke="{t["hex"]}" '
                     f'stroke-width="2.5" stroke-linecap="round" opacity=".9"/>')
    return (f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" aria-hidden="true" '
            f'style="display:block;margin:.2em 0 1.2em">{"".join(parts)}</svg>')


def endmark_svg(threads):
    # The colophon reads from every declared thread, so it never claims a palette the story lacks.
    marks, x = [], 0
    for t in threads:
        marks.append(_node(x + 6, 6, t["shape"], t["hex"], r=5)); x += 23
    return f'<p class="endmark" aria-hidden="true"><svg width="{x}" height="12" viewBox="0 0 {x} 12">{"".join(marks)}</svg></p>'


# ------------------------------------------------------------------ body ---
def render_body(md, env, threads):
    out = []
    titled = seen_h2 = dropped_cap = keyed = False
    stitch_words = {t["name"].split("·")[0].strip().lower(): t["hex"] for t in threads}
    P = 'style="margin:0 0 1.15em;line-height:1.75"'
    blocks = [b.strip() for b in re.split(r"\n\s*\n", md.strip()) if b.strip()]

    # Pre-scan: for each section heading (every ## after the title), find the thread that
    # governs it, from the stitches inside. The living braid reads these to know which strand
    # leads where. A section with no stitch inherits the previous lead.
    def stitch_hex(b):
        head = b[:20].lower()
        return next((hx for w, hx in stitch_words.items() if w in head), None)
    section_leads, in_section, seen_title, tally, prev = [], False, False, {}, threads[0]["hex"]
    def flush():
        nonlocal tally, prev
        if tally:
            prev = max(tally, key=tally.get)
        section_leads.append(prev)
        tally = {}
    for b in blocks:
        if b.startswith("## ") and not seen_title:
            seen_title = True
        elif b.startswith("## "):
            if in_section:
                flush()
            in_section = True
        elif b.startswith("— *"):
            hx = stitch_hex(b)
            if hx:
                tally[hx] = tally.get(hx, 0) + 1
    if in_section:
        flush()
    lead_iter = iter(section_leads)

    for block in blocks:
        b = block.strip()
        if not b:
            continue
        if b == "---":
            out.append('<hr style="border:none;border-top:1px solid var(--border);margin:2.5em 0">')
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
            if not keyed and len(threads) >= 2:  # P1: thread key after the map, before the body
                out.append(thread_legend(threads)); keyed = True
            seen_h2 = True
            lead = next(lead_iter, threads[0]["hex"])
            out.append(f'<h2 data-thread="{lead}" style="margin:2.4em 0 .8em;font-size:1.375rem;font-weight:600;line-height:1.25;color:var(--fg1)">{inline(b[3:])}</h2>')
            if "braid" in b.lower():
                out.append(braid_svg(threads))
        elif b.startswith("[[ARC]]"):
            arc = render_arc(env, threads)
            if arc:
                out.append(arc)
        elif b.startswith("— *"):
            head = b[:20].lower()
            color = next((hexv for word, hexv in stitch_words.items() if word in head), threads[-1]["hex"])
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
                cls = "plain" if "in plain terms" in b.lower() else "aside"
                out.append(f'<div class="{cls}">{body}</div>')
        elif b.startswith("- "):
            items = "".join(f'<li style="margin:0 0 .8em;line-height:1.7">{inline(i[2:].strip())}</li>'
                            for i in re.split(r"\n(?=- )", b))
            out.append(f'<ul style="margin:0 0 1.15em;padding-left:1.3em">{items}</ul>')
        else:
            txt = inline(' '.join(l.strip() for l in b.splitlines()))
            if seen_h2 and not dropped_cap and len(b) > 180:
                out.append(f'<p class="dropcap" {P}>{txt}</p>'); dropped_cap = True
            else:
                out.append(f"<p {P}>{txt}</p>")
    out.append(endmark_svg(threads))
    return "\n".join(out)


def ladder(slug, tier, out_dir):
    tiers = [("exec", "90-second"), ("brief", "operational"), ("full", "surgical")]
    live = [(t, label) for t, label in tiers
            if t == tier or (out_dir / f"story-{slug}-{t}.html").exists()
            or (out_dir / f"blog-nftt-{slug}-{t}.html").exists()]
    if len(live) < 2:
        return ""
    base = f"/blog/nftt/{slug}"
    links = " · ".join(
        f'<span style="color:var(--fg1);font-weight:600">{label}</span>' if t == tier
        else f'<a style="text-decoration:none" href="{base if t=="exec" else base+"/"+t}">{label}</a>'
        for t, label in live)
    return (f'<nav style="margin:0 0 2.2em;padding:.55em .9em;background:var(--glass-surface),var(--surface);'
            f'border:1px solid var(--border);border-radius:var(--radius-md);box-shadow:var(--emboss);'
            f'font-family:var(--font-mono);font-size:.78rem;color:var(--fg3)">depth: {links}</nav>')


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
  :root {{{css_root}}}
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
  .standfirst {{ font-size: 1.125rem; line-height: 1.6; font-weight: 500; color: var(--fg2); margin: 0 0 1.8em; }}
  .threadkey {{ font-family: var(--font-mono); font-size: .8rem; color: var(--fg2);
    margin: 0 0 2em; padding: .7em .9em; border: 1px solid var(--border); border-radius: var(--radius-md);
    background: var(--glass-surface), var(--surface); box-shadow: var(--emboss); line-height: 2; }}
  .bq {{ margin: 1.6em 0; padding: .2em 0 .2em 1.1em; border-left: 1px solid var(--border);
    font-size: 1rem; font-weight: 400; font-style: italic; line-height: 1.7; color: var(--fg2); }}
  .dropcap::first-letter {{ float: left; font-size: 3.4em; line-height: .82; padding: .06em .14em 0 0;
    font-weight: 600; color: var(--fg1); }}
  .pull {{ margin: 2.2em 0; padding: 1.15em 0; border-top: 1px solid var(--border);
    border-bottom: 1px solid var(--border); font-size: 1.5rem; line-height: 1.4; font-weight: 600;
    color: var(--fg1); letter-spacing: -0.015em; }}
  /* section tick = the story's own thread gradient; pull-quote = a single accent. Different
     ranks, different marks, both driven by the declared palette (never a hardcoded triad). */
  .pull::before {{ content: ""; display: block; width: 34px; height: 2px; margin-bottom: .8em;
    background: var(--tick-accent); }}
  h2::before {{ content: ""; display: block; width: 48px; height: 2px; margin: 0 0 .9em;
    background: var(--tick); }}
  .arc {{ margin: 2.2em 0 1.4em; }}
  .arc-cap {{ margin-top: .5em; }}
  /* vertical arc ladder: the five-second-test form for long arcs */
  .arc-list {{ list-style: none; margin: 0; padding: 0; }}
  .arc-row {{ display: grid; grid-template-columns: 26px 1fr auto; align-items: baseline;
    column-gap: .8em; padding: 0; }}
  .arc-mark {{ position: relative; grid-row: 1; display: flex; justify-content: center; padding-top: .15em; }}
  .arc-spine {{ position: absolute; top: 20px; bottom: -6px; left: 50%; width: 2px;
    transform: translateX(-50%); background: var(--border); }}
  .arc-label {{ padding: 0 0 1.15em; line-height: 1.5; color: var(--fg1); }}
  .arc-thread {{ font-family: var(--font-mono); font-size: .72rem; letter-spacing: .04em;
    text-transform: uppercase; white-space: nowrap; opacity: .9; }}
  .endmark {{ margin: 2.6em 0 0; }}
  nav a {{ text-decoration: none; }}
  nav a:hover {{ text-decoration: underline; }}
  /* The living braid: a read-thread rail that reacts to scroll position, velocity, and
     direction, with a gold yad (the Torah pointer) marking your heading and your place. */
  .braid-rail {{ position: fixed; top: 0; left: 0; width: 56px; height: 100vh; z-index: 5;
    pointer-events: none; display: none; }}
  .braid-rail svg {{ display: block; width: 56px; height: 100%; }}
  .braid-resume {{ position: fixed; left: 62px; z-index: 6; transform: translateY(-50%);
    font: 600 .72rem/1 var(--font-mono); color: var(--bg); background: var(--gold);
    border: none; border-radius: 999px; padding: .5em .8em; cursor: pointer; display: none;
    box-shadow: 0 2px 10px rgba(0,0,0,.5); letter-spacing: .02em; }}
  @media (min-width: 1040px) {{ .braid-rail {{ display: block; }} }}
</style>
<body style="margin:0;background:var(--bg);color:var(--fg1);font-size:17px;font-family:var(--font-sans);overflow-wrap:break-word">
<main style="max-width:68ch;margin:0 auto;padding:64px 22px 96px">
{ladder}<article>
{body}
</article><footer style="margin-top:4em;padding-top:1.5em;border-top:1px solid var(--border);font-size:.82rem;color:var(--fg3);font-family:var(--font-mono)">
NFTT · notes from the trenches · <a href="https://good.arcs.care">good.arcs.care</a> · every claim traces to a commit
</footer>
</main>
<!--BRAID-->
</body></html>
"""


# The living braid + yad. Injected via string replace (never through PAGE.format) so its JS/CSS
# braces stay intact. __THREADS__ / __SLUG__ are filled by build().
BRAID_FEATURE = r"""<div class="braid-rail" aria-hidden="true"><svg width="56" height="100" preserveAspectRatio="none"></svg></div>
<button class="braid-resume" type="button">pick up where you left off</button>
<script id="braid-threads" type="application/json">__THREADS__</script>
<script>
(function(){
  var rail=document.querySelector('.braid-rail'); if(!rail) return;
  var svg=rail.querySelector('svg');
  var threads=JSON.parse(document.getElementById('braid-threads').textContent);
  var N=threads.length, W=56, cx=28;
  var reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
  var SVGNS='http://www.w3.org/2000/svg';
  var H=innerHeight;
  function fit(){ H=innerHeight; svg.setAttribute('viewBox','0 0 '+W+' '+H); }
  fit(); addEventListener('resize',fit,{passive:true});

  // The ARCS double helix: base-pair rungs behind, two backbones in front. The rungs are the
  // threads (coded by the section you are in); the backbones are the structure that carries them.
  var GAP=15, nR=Math.ceil(H/GAP)+3, rungs=[];
  for(var i=0;i<nR;i++){ var r=document.createElementNS(SVGNS,'line');
    r.setAttribute('stroke-linecap','round'); svg.appendChild(r); rungs.push(r); }
  var back=[0,1].map(function(k){
    var p=document.createElementNS(SVGNS,'polyline');
    p.setAttribute('fill','none'); p.setAttribute('stroke',(threads[k]||threads[0]).hex);
    p.setAttribute('stroke-linecap','round'); svg.appendChild(p); return p;
  });
  // the yad: a gold pointer riding a backbone at the reading line
  var yad=document.createElementNS(SVGNS,'g');
  yad.innerHTML='<circle r="7" fill="none" stroke="#FFD700" stroke-width="1.5" opacity=".9"/>'
    +'<path d="M0 -3 L0 6 M-3 3 L0 6 L3 3" stroke="#FFD700" stroke-width="1.8" fill="none" stroke-linecap="round"/>';
  svg.appendChild(yad);

  // lead thread per section, from the h2 data-thread the reader is currently under
  var heads=[].slice.call(document.querySelectorAll('h2[data-thread]'));
  function currentLead(){
    var mark=scrollY+innerHeight*0.4, hex=(threads[0]||{}).hex;
    for(var i=0;i<heads.length;i++){ if(heads[i].offsetTop<=mark) hex=heads[i].getAttribute('data-thread'); else break; }
    return hex;
  }

  var lastY=scrollY, vel=0, energy=0, phase=0, dir=1, leadHex=currentLead();
  addEventListener('scroll',function(){
    var y=scrollY, d=y-lastY; lastY=y;
    vel=d; if(d) dir=d>0?1:-1;
    energy=Math.min(1, energy+Math.min(0.9, Math.abs(d)/90));
    leadHex=currentLead();
    savePlace(y);
  },{passive:true});

  function docFrac(){ var m=document.documentElement.scrollHeight-innerHeight; return m>0?Math.min(1,scrollY/m):0; }

  var period=54;
  function draw(){
    var A=13+energy*7, spin=phase;               // helix radius opens with reading speed
    var a='', b='';
    for(var y=-12;y<=H+12;y+=8){
      var s=Math.sin(y/period+spin);
      a+=(cx+A*s).toFixed(1)+','+y+' ';
      b+=(cx-A*s).toFixed(1)+','+y+' ';
    }
    back[0].setAttribute('points',a); back[1].setAttribute('points',b);
    var bw=(1.8+energy*1.3).toFixed(1);
    back[0].setAttribute('stroke-width',bw); back[1].setAttribute('stroke-width',bw);
    back[0].setAttribute('opacity','0.9');  back[1].setAttribute('opacity','0.5');
    for(var i=0;i<rungs.length;i++){
      var yy2=i*GAP, s2=Math.sin(yy2/period+spin), r=rungs[i];
      r.setAttribute('x1',(cx+A*s2).toFixed(1)); r.setAttribute('y1',yy2);
      r.setAttribute('x2',(cx-A*s2).toFixed(1)); r.setAttribute('y2',yy2);
      r.setAttribute('stroke',leadHex);
      r.setAttribute('stroke-width',(1+energy*0.8).toFixed(1));
      r.setAttribute('opacity',(Math.abs(s2)*(0.4+energy*0.45)).toFixed(2)); // bright when facing us
    }
    // the yad rides a backbone at the reading line, tipped the way you are heading
    var ry=innerHeight*0.4, rx=cx + A*Math.sin(ry/period+spin);
    yad.setAttribute('transform','translate('+rx.toFixed(1)+','+ry.toFixed(1)+') scale(1,'+(dir<0?-1:1)+')');
    phase += dir*(0.01+energy*0.06) + 0.003;     // winds with you; idle drift keeps it alive
    energy*=0.94;                                  // settles back to a calm helix
    if(!reduce) requestAnimationFrame(draw);
  }

  // bookmark: remember the place; offer to resume on return
  var KEY='braid:'+'__SLUG__', saveT=0;
  function savePlace(y){ var now=Date.now(); if(now-saveT<400) return; saveT=now;
    try{ localStorage.setItem(KEY, JSON.stringify({f:docFrac(),t:now})); }catch(e){} }
  function offerResume(){
    var raw; try{ raw=localStorage.getItem(KEY); }catch(e){ return; }
    if(!raw) return; var st; try{ st=JSON.parse(raw); }catch(e){ return; }
    if(!st || st.f<0.06 || st.f>0.97 || scrollY>innerHeight*0.5) return;
    var btn=document.querySelector('.braid-resume');
    btn.style.top=(st.f*innerHeight)+'px'; btn.style.display='block';
    btn.addEventListener('click',function(){
      var target=st.f*(document.documentElement.scrollHeight-innerHeight);
      scrollTo({top:target,behavior:'smooth'}); btn.style.display='none';
    });
    ['scroll','keydown','wheel','touchstart'].forEach(function(ev){
      addEventListener(ev,function(){ btn.style.display='none'; },{once:true,passive:true}); });
  }

  if(reduce){ draw(); } else { requestAnimationFrame(draw); }
  offerResume();
})();
</script>"""


def build(src: Path, dst: Path):
    env, body_md = parse_story(src.read_text())
    threads = env["threads"]
    title = env.get("title") or next((l[3:].strip() for l in body_md.splitlines() if l.startswith("## ")), src.stem)
    desc = env.get("description", title)
    slug = env.get("slug", src.stem)
    tier = env.get("tier", "full")
    # Ornaments read from the declared palette: the section tick is the full thread gradient,
    # the pull-quote accent is the first thread. Never a hardcoded triad.
    tick = "linear-gradient(90deg, " + ", ".join(t["hex"] for t in threads) + ")"
    css_root = CSS_ROOT + f"    --tick:{tick}; --tick-accent:{threads[0]['hex']};\n"
    body = render_body(body_md, env, threads)
    page = PAGE.format(
        title=h.escape(f"{title} · NFTT"), desc=h.escape(desc), css_root=css_root,
        body=body, ladder=ladder(slug, tier, dst.parent))
    # Living braid + yad: injected by replace so its JS/CSS braces survive (never .format).
    palette = json.dumps([{"hex": t["hex"], "shape": t["shape"]} for t in threads])
    braid = BRAID_FEATURE.replace("__THREADS__", palette).replace("__SLUG__", slug)
    page = page.replace("<!--BRAID-->", braid)
    # Ship-gate: no story ships an em-dash, prose included (ADR-034: gate, not hope).
    if "—" in page:
        raise StoryError("em-dash (U+2014) in output. ARCS uses commas, colons, or periods. "
                         "Fix the prose, then re-render.")
    dst.write_text(page)
    return dst


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__); sys.exit(2)
    try:
        out = build(Path(sys.argv[1]), Path(sys.argv[2]))
    except StoryError as e:
        print(f"story_render: REFUSED: {e}", file=sys.stderr); sys.exit(1)
    print(f"rendered {out} ({out.stat().st_size} bytes)")
