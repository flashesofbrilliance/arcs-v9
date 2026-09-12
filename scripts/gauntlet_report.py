#!/usr/bin/env python3
"""gauntlet_report — render an ARCS gauntlet scar-log (adversarial findings) to a printable
FieldOS runbook. Data-driven: a findings JSON in, one exploded line-by-line HTML out, print /
PDF optimized (print-color-adjust: exact, page-break control). Stdlib only, zero LLM.

Usage: python3 scripts/gauntlet_report.py <findings.json> <out.html>
"""
import html as h
import json
import sys
from pathlib import Path

SEV = {  # severity → (label, hex)
    "kill":   ("KILL",   "#FF4D6D"),
    "high":   ("HIGH",   "#FF4D6D"),
    "med":    ("MED",    "#ff9d3c"),
    "low":    ("LOW",    "#FFD700"),
    "keep":   ("EARNS IT", "#00FF9D"),
}
STATUS = {  # kintsugi status → (label, hex)
    "fixed":   ("FIXED",   "#00FF9D"),
    "kept":    ("KEPT",    "#00F0FF"),
    "pending": ("PENDING", "#ff9d3c"),
    "wontfix": ("BY DESIGN", "#8593a6"),
}


def field(label, value):
    if not value:
        return ""
    return (f'<div class="f"><span class="fl">{h.escape(label)}</span>'
            f'<div class="fv">{value}</div></div>')


def code(txt):
    return f'<pre class="code">{h.escape(txt)}</pre>' if txt else ""


def finding(n, f):
    slabel, scolor = SEV.get(f.get("severity", "med"), SEV["med"])
    badges = [f'<span class="badge" style="--c:{scolor}">{slabel}</span>']
    if f.get("status"):
        stl, stc = STATUS.get(f["status"], STATUS["pending"])
        badges.append(f'<span class="badge" style="--c:{stc}">{stl}</span>')
    loc = f'<code class="loc">{h.escape(f["location"])}</code>' if f.get("location") else ""
    return f"""<article class="finding">
  <div class="fhead"><span class="fnum">{n:02d}</span>
    <h3>{h.escape(f["title"])}</h3>
    <span class="badges">{''.join(badges)}</span></div>
  {loc}
  {field("Defect", h.escape(f.get("defect","")))}
  {field("Repro", code(f.get("repro","")))}
  {field("Fix", h.escape(f.get("fix","")))}
  {field("Verdict / heal", h.escape(f.get("heal","")))}
</article>"""


def lens_block(lens):
    rows = "\n".join(finding(i + 1, f) for i, f in enumerate(lens["findings"]))
    return f"""<section class="lens">
  <div class="lhead">
    <h2>{h.escape(lens["name"])}</h2>
    <p class="lrole">{h.escape(lens.get("role",""))}</p>
  </div>
  <p class="lsummary">{h.escape(lens.get("summary",""))}</p>
  {rows}
</section>"""


PAGE = """<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<script defer src="/_vercel/insights/script.js"></script>
</head>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');
  :root {{
    --bg:#020408; --surface:#0d1117; --border:#1e293b;
    --fg1:#e2e8f0; --fg2:#94a3b8; --fg3:#8593a6; --fg4:#707e92;
    --cyan:#00F0FF; --green:#00FF9D; --gold:#FFD700; --red:#FF4D6D; --orange:#ff9d3c;
    --sans:'Inter',system-ui,sans-serif; --mono:'JetBrains Mono',ui-monospace,monospace;
  }}
  * {{ box-sizing: border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--fg1); font:16px/1.6 var(--sans);
    -webkit-font-smoothing:antialiased; }}
  .wrap {{ max-width: 900px; margin:0 auto; padding:56px 28px 96px; }}
  .eyebrow {{ font:700 .72rem/1 var(--mono); letter-spacing:.16em; text-transform:uppercase;
    color:var(--cyan); margin:0 0 .8em; }}
  h1 {{ font-size:clamp(1.8rem,4vw,2.6rem); line-height:1.12; letter-spacing:-.02em; margin:0 0 .5em; }}
  .lede {{ color:var(--fg2); font-size:1.05rem; max-width:66ch; margin:0 0 1.4em; }}
  .meta {{ font:.78rem/1.7 var(--mono); color:var(--fg3); border-top:1px solid var(--border);
    border-bottom:1px solid var(--border); padding:.9em 0; margin:0 0 2.4em;
    display:flex; flex-wrap:wrap; gap:.4em 1.6em; }}
  .meta b {{ color:var(--fg1); font-weight:600; }}
  .lens {{ margin:0 0 2.8em; }}
  .lhead {{ display:flex; align-items:baseline; gap:.9em; flex-wrap:wrap;
    border-bottom:2px solid var(--border); padding-bottom:.5em; margin:0 0 .3em; }}
  .lhead h2 {{ font-size:1.35rem; margin:0; }}
  .lrole {{ font:.72rem/1 var(--mono); text-transform:uppercase; letter-spacing:.08em; color:var(--fg4); margin:0; }}
  .lsummary {{ color:var(--fg2); font-size:.95rem; margin:.7em 0 1.4em; }}
  .finding {{ border:1px solid var(--border); border-radius:10px; background:var(--surface);
    padding:1.1em 1.2em; margin:0 0 1em; break-inside:avoid; page-break-inside:avoid; }}
  .fhead {{ display:flex; align-items:baseline; gap:.7em; flex-wrap:wrap; }}
  .fnum {{ font:700 .85rem/1 var(--mono); color:var(--fg4); }}
  .fhead h3 {{ font-size:1.02rem; font-weight:600; margin:0; flex:1 1 60%; line-height:1.35; }}
  .badges {{ display:flex; gap:.4em; flex-wrap:wrap; }}
  .badge {{ font:700 .62rem/1 var(--mono); letter-spacing:.08em; color:var(--c);
    border:1px solid var(--c); border-radius:4px; padding:.32em .5em; white-space:nowrap; }}
  .loc {{ display:inline-block; font:.74rem/1.4 var(--mono); color:var(--cyan);
    background:#0a0f18; border:1px solid var(--border); border-radius:4px; padding:.2em .5em; margin:.7em 0 .2em; }}
  .f {{ margin:.7em 0 0; }}
  .fl {{ font:700 .64rem/1 var(--mono); text-transform:uppercase; letter-spacing:.1em; color:var(--fg4);
    display:block; margin:0 0 .25em; }}
  .fv {{ color:var(--fg2); font-size:.92rem; }}
  .code {{ font:.78rem/1.5 var(--mono); color:var(--fg1); background:#0a0f18;
    border:1px solid var(--border); border-radius:6px; padding:.7em .8em; margin:0; overflow-x:auto;
    white-space:pre-wrap; word-break:break-word; }}
  footer {{ border-top:1px solid var(--border); margin-top:3em; padding-top:1.2em;
    font:.76rem/1.6 var(--mono); color:var(--fg3); }}
  @media print {{
    * {{ -webkit-print-color-adjust:exact !important; print-color-adjust:exact !important; }}
    body {{ background:#fff; }}
    .wrap {{ max-width:100%; padding:0; }}
    .finding {{ break-inside:avoid; page-break-inside:avoid; }}
    .lens {{ break-before:auto; }}
    a {{ text-decoration:none !important; }}
  }}
</style>
<body><div class="wrap">
<p class="eyebrow">{eyebrow}</p>
<h1>{h1}</h1>
<p class="lede">{lede}</p>
<div class="meta">{meta}</div>
{body}
<footer>{footer}</footer>
</div></body></html>
"""


def build(data, dst):
    meta = " · ".join(f'<span><b>{h.escape(str(v))}</b> {h.escape(k)}</span>'
                      for k, v in data.get("meta", {}).items())
    body = "\n".join(lens_block(l) for l in data["lenses"])
    dst.write_text(PAGE.format(
        title=h.escape(data["title"]), desc=h.escape(data.get("lede", "")),
        eyebrow=h.escape(data.get("eyebrow", "")), h1=h.escape(data["title"]),
        lede=h.escape(data.get("lede", "")), meta=meta, body=body,
        footer=h.escape(data.get("footer", ""))))
    return dst


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__); sys.exit(2)
    out = build(json.loads(Path(sys.argv[1]).read_text()), Path(sys.argv[2]))
    print(f"rendered {out} ({out.stat().st_size} bytes)")
