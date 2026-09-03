#!/usr/bin/env python3
"""atlas_render — render an atlas digest (the _ARTIFACTS/atlas/digest-*.json node schema) to a
self-contained HTML ziggurat: nodes grouped by tier, bottom tier widest, each card naming its
provenance and its links. Stdlib only, deterministic, zero LLM.

The existing _ARTIFACTS/atlas/atlas.html was hand-built with the same node schema and no
generator; this is the generator for that schema, extended with an optional "tiers" list and a
per-node "tier" integer. Digests without tiers render as one flat band.

Usage:  python3 scripts/atlas_render.py <digest.json> <out.html> [--theme light|dark]
Refuses (exit 2, no output) on: fewer than 2 nodes, a node whose tier is not declared, a link to an
unknown node id, or a missing preframe when audience is "external" (an external reader must be told
what they are looking at before the first card).
"""
import html, json, sys

STATUS = {"LIVE": "#067647", "HELD": "#b54708", "INTERNAL": "#6b7280", "DEMO": "#1d4ed8", "OPEN": "#b42318"}


def esc(s):
    return html.escape(str(s or ""), quote=True)


def refuse(msg):
    sys.stderr.write(f"atlas_render: REFUSED: {msg}\n")
    sys.exit(2)


def render(d, theme="light"):
    nodes = d.get("nodes", [])
    if len(nodes) < 2:
        refuse("fewer than 2 nodes")
    ids = {n["id"] for n in nodes}
    tiers = d.get("tiers") or [{"n": 0, "label": d.get("domain", "atlas"), "gloss": ""}]
    tier_ns = {t["n"] for t in tiers}
    for n in nodes:
        t = n.get("tier", tiers[0]["n"])
        if t not in tier_ns:
            refuse(f"node {n['id']} tier {t} not declared")
        for l in n.get("links", []):
            if l not in ids:
                refuse(f"node {n['id']} links to unknown id {l}")
    if d.get("audience") == "external" and not d.get("preframe"):
        refuse("external audience with no preframe")

    if theme == "dark":
        pal = dict(bg="#020408", fg="#e2e8f0", mute="#94a3b8", line="#1e293b", soft="#0d1117", ink="#e2e8f0")
    else:
        pal = dict(bg="#ffffff", fg="#1a1a1a", mute="#666", line="#e5e5e5", soft="#fafafa", ink="#1a1a1a")

    out = []
    a = out.append
    a('<!doctype html><html lang="en"><head><meta charset="utf-8">')
    a('<meta name="viewport" content="width=device-width,initial-scale=1">')
    a(f'<title>{esc(d.get("title", "Atlas"))}</title>')
    a(f'<meta name="description" content="{esc(d.get("preframe", {}).get("what", d.get("title", "")))[:300]}">')
    a("<style>")
    a(f'*{{box-sizing:border-box}}body{{margin:0;background:{pal["bg"]};color:{pal["fg"]};font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}}')
    a('.page{max-width:960px;margin:0 auto;padding:36px 20px 80px}')
    a('h1{font-size:28px;margin:0 0 6px;font-weight:600}')
    a(f'.sub{{color:{pal["mute"]};margin:0 0 22px}}')
    a(f'.pre{{border:1px solid {pal["line"]};border-radius:8px;padding:16px 18px;background:{pal["soft"]};margin:0 0 30px}}')
    a('.pre p{margin:0 0 8px}.pre p:last-child{margin:0}.pre b{display:inline-block;min-width:150px}')
    a(f'.key{{display:flex;gap:14px;flex-wrap:wrap;font-size:12px;color:{pal["mute"]};margin:0 0 26px}}')
    a('.key span i{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:6px;vertical-align:middle}')
    a('.zig{display:flex;flex-direction:column;align-items:center;gap:14px}')
    a(f'.tier{{border:1px solid {pal["line"]};border-radius:10px;padding:14px 16px 6px;background:{pal["bg"]};transition:width .2s}}')
    a(f'.tier h2{{font-size:13px;text-transform:uppercase;letter-spacing:.08em;color:{pal["mute"]};margin:0 0 2px;font-weight:600}}')
    a(f'.tier .gloss{{font-size:14px;color:{pal["mute"]};margin:0 0 12px}}')
    a('.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:10px;margin-bottom:10px}')
    a(f'.card{{border:1px solid {pal["line"]};border-radius:8px;padding:12px 13px;background:{pal["soft"]};font-size:14px;scroll-margin-top:16px}}')
    a('.card h3{font-size:15px;margin:0 0 6px;font-weight:600;display:flex;justify-content:space-between;gap:8px;align-items:baseline}')
    a('.card .st{font-size:10px;letter-spacing:.08em;text-transform:uppercase;font-weight:700;white-space:nowrap}')
    a('.card p{margin:0 0 8px}')
    a(f'.card .prov{{font-family:ui-monospace,Menlo,monospace;font-size:11.5px;color:{pal["mute"]};word-break:break-word}}')
    a(f'.card .links{{font-size:12px;color:{pal["mute"]};margin-top:6px}}.card .links a{{color:inherit;text-decoration:underline dotted}}')
    a('.arrow{font-size:12px;color:#999;letter-spacing:.1em;text-transform:uppercase}')
    a(f'.jump{{position:sticky;top:0;z-index:5;background:{pal["bg"]}ee;backdrop-filter:blur(6px);border-bottom:1px solid {pal["line"]};margin:0 -20px 26px;padding:10px 20px;display:flex;gap:6px;flex-wrap:wrap;font-size:12px}}')
    a(f'.jump a{{color:{pal["mute"]};text-decoration:none;border:1px solid {pal["line"]};border-radius:999px;padding:4px 10px}}.jump a b{{color:{pal["fg"]};font-weight:600;margin-right:4px}}')
    a('@media (max-width:700px){.tier{width:100%!important}.pre b{display:block;min-width:0}}')
    a("</style></head><body><div class=\"page\">")

    a(f'<h1>{esc(d.get("title", "Atlas"))}</h1>')
    reader = d.get("reader")
    a(f'<p class="sub">{esc(d.get("generated", ""))}{" · for " + esc(reader) if reader else ""} · {len(nodes)} artifacts · {len(tiers)} tiers</p>')
    pf = d.get("preframe")
    if pf:
        a('<div class="pre">')
        for k, lbl in (("what", "What you are looking at"), ("why", "Why it exists"), ("how", "How to read it")):
            if pf.get(k):
                a(f'<p><b>{lbl}</b> {esc(pf[k])}</p>')
        a("</div>")
    a('<nav class="jump" aria-label="Jump to tier">' + "".join(
        f'<a href="#tier-{t["n"]}"><b>{t["n"]:02d}</b>{esc(t["label"])}</a>' for t in sorted(tiers, key=lambda t: -t["n"])) + "</nav>")
    a('<div class="key">' + "".join(
        f'<span><i style="background:{c}"></i>{s}</span>' for s, c in STATUS.items()
        if any(n.get("status") == s for n in nodes)) + "</div>")

    # ziggurat: highest tier on top, narrowest; bottom tier full width
    ordered = sorted(tiers, key=lambda t: -t["n"])
    N = len(ordered)
    a('<div class="zig">')
    for i, t in enumerate(ordered):
        width = 100 - (N - 1 - i) * (40 / max(N - 1, 1))  # top = 60%, bottom = 100%
        tn = [n for n in nodes if n.get("tier", tiers[0]["n"]) == t["n"]]
        a(f'<div class="tier" style="width:{width:.0f}%" id="tier-{t["n"]}">')
        a(f'<h2>Tier {t["n"]} · {esc(t["label"])}</h2>')
        if t.get("gloss"):
            a(f'<p class="gloss">{esc(t["gloss"])}</p>')
        a('<div class="cards">')
        for n in tn:
            col = STATUS.get(n.get("status", ""), "#999")
            a(f'<div class="card" id="n-{esc(n["id"])}"><h3><span>{esc(n["title"])}</span><span class="st" style="color:{col}">{esc(n.get("status", ""))}</span></h3>')
            a(f'<p>{esc(n.get("claim", ""))}</p>')
            if n.get("provenance"):
                a(f'<div class="prov">{esc(n["provenance"])}</div>')
            if n.get("links"):
                a('<div class="links">serialized from / into: ' + ", ".join(
                    f'<a href="#n-{esc(l)}">{esc(l)}</a>' for l in n["links"]) + "</div>")
            a("</div>")
        a("</div></div>")
        if i < N - 1:
            a('<div class="arrow">serialized from ↓</div>')
    a("</div>")
    if d.get("footer"):
        a(f'<p class="sub" style="margin-top:28px">{esc(d["footer"])}</p>')
    a("</div></body></html>")
    return "\n".join(out)


def main(argv):
    if len(argv) < 3:
        sys.stderr.write(__doc__)
        return 1
    theme = "light"
    if "--theme" in argv:
        theme = argv[argv.index("--theme") + 1]
    d = json.load(open(argv[1], encoding="utf-8"))
    out = render(d, theme)
    with open(argv[2], "w", encoding="utf-8") as f:
        f.write(out)
    print(f"atlas_render: {len(d['nodes'])} nodes · {len(d.get('tiers', [1]))} tiers -> {argv[2]} ({len(out)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
