#!/usr/bin/env python3
"""kit_specimen: one standard page for every ui-kit building block (atom, molecule, organism, lockup, template).

A specimen spec (src/ui-kit/specimens/<name>.json) goes in; a page in src/ui-kit/recoil-report/ comes out with the
same sections in the same order, so any block reads the same way:

  1 Head        layer, number, name, the one reader job (lede spans the full width)
  2 Stage       the block live, on real demo data
  3 States      the same block in every state it can take
  4 Anatomy     each part, its type role and its token
  5 Usage       use it when / do not use it when
  6 Data        the fields it reads
  7 Access      keyboard, screen reader, and how it reads without colour
  8 Relations   what it is built from and what uses it
  9 Gates       the checks that must pass

The page is enrolled in the kit-specimen template (src/ui-kit/templates.json), so component_source_gate refuses a
specimen that drops a section. Never hand-edit a generated page: edit the spec and rebuild.

  python3 scripts/kit_specimen.py src/ui-kit/specimens/change.json      build one
  python3 scripts/kit_specimen.py --all                                 build every spec
  python3 scripts/kit_specimen.py --check                               exit 1 if any page differs from its spec
Stdlib only.
"""
import html, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPECS = os.path.join(ROOT, "src/ui-kit/specimens")
KIT = os.path.join(ROOT, "src/ui-kit/recoil-report")
LAYERS = ("Atom", "Molecule", "Organism", "Lockup", "Template")
REQUIRED = ("number", "name", "layer", "job", "anatomy", "states", "use_when", "avoid_when", "data", "access", "built_from", "used_by", "gates", "demo")

CSS = """* { box-sizing: border-box; margin: 0; padding: 0; }
::selection { background: var(--cyan-bg); color: var(--text); }
body { background: var(--bg); color: var(--text); font-family: var(--ds-font-sans); font-size: var(--fs-body); line-height: 1.6; padding: 32px 16px 64px; }
main { max-width: 720px; margin: 0 auto; display: flex; flex-direction: column; gap: 40px; }
.section-label { font-family: var(--ds-font-mono); font-size: var(--fs-label); letter-spacing: 0.14em; text-transform: uppercase; color: var(--text-secondary); margin-bottom: 12px; font-weight: 600; }
.sp-head { display: flex; flex-direction: column; gap: 10px; }
.sp-crumb { display: flex; flex-wrap: wrap; gap: 0 8px; font-family: var(--ds-font-mono); font-size: var(--fs-label); letter-spacing: 0.08em; text-transform: uppercase; color: var(--text-secondary); }
.sp-crumb span + span::before { content: "/"; margin-right: 8px; color: var(--border); }
.sp-head h1 { font-family: var(--ds-font-display); font-size: var(--fs-display); font-weight: 500; line-height: 1.1; letter-spacing: -0.01em; text-wrap: balance; }
.sp-job { font-size: var(--fs-headline); line-height: 1.45; color: var(--text-secondary); max-width: none; text-wrap: pretty; }
.sp-stage { border: 1px solid var(--border); border-radius: var(--ds-r-sm); background: var(--surface); padding: 28px 24px; }
.sp-states { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 300px), 1fr)); gap: 12px; }
.sp-state { border: 1px solid var(--border); border-radius: var(--ds-r-sm); padding: 16px; display: flex; flex-direction: column; gap: 10px; }
.sp-state h3 { font-family: var(--ds-font-mono); font-size: var(--fs-label); letter-spacing: 0.08em; text-transform: uppercase; color: var(--text-secondary); font-weight: 600; }
.sp-state p { color: var(--text-secondary); font-size: var(--fs-body); line-height: 1.45; }
.sp-table { width: 100%; border-collapse: collapse; }
.sp-table th, .sp-table td { text-align: left; padding: 10px 12px; border-bottom: 1px solid var(--border); vertical-align: top; }
.sp-table thead th { font-family: var(--ds-font-mono); font-size: var(--fs-label); letter-spacing: 0.08em; text-transform: uppercase; color: var(--text-secondary); font-weight: 600; }
.sp-table td code, .sp-table th code, .sp-list code { font-family: var(--ds-font-mono); font-size: var(--fs-body); color: var(--text); white-space: nowrap; }
.sp-table td:first-child { white-space: nowrap; }
.sp-scroll { overflow-x: auto; }
.sp-scroll:focus-visible { outline: 2px solid var(--cyan); outline-offset: 2px; }
.sp-num { font-family: var(--ds-font-mono); font-variant-numeric: tabular-nums; color: var(--text-secondary); }
.sp-two { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; }
.sp-list { list-style: none; display: flex; flex-direction: column; gap: 8px; }
.sp-list li { padding-left: 18px; position: relative; }
.sp-list li::before { content: ""; position: absolute; left: 0; top: 0.7em; width: 8px; height: 1px; background: var(--text-secondary); }
.sp-yes h3, .sp-no h3 { font-family: var(--ds-font-mono); font-size: var(--fs-label); letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 10px; font-weight: 700; }
.sp-yes h3 { color: var(--green); } .sp-no h3 { color: var(--red); }
.sp-yes h3::before { content: "+ "; } .sp-no h3::before { content: "\\2212\\00a0"; }
.sp-rel { display: flex; flex-wrap: wrap; gap: 8px; }
.sp-rel a, .sp-rel span { font-family: var(--ds-font-sans); font-size: var(--fs-body); color: var(--text); border: 1px solid var(--border); border-radius: var(--ds-r-xs); padding: 6px 12px; text-decoration: none; min-height: 44px; display: inline-flex; align-items: center; }
.sp-rel a:hover { border-color: var(--text-secondary); }
.sp-rel a:focus-visible { outline: 2px solid var(--cyan); outline-offset: 2px; }
.sp-gates code { font-family: var(--ds-font-mono); font-size: var(--fs-label); }
"""

SECTION_IDS = ("sp-head", "sp-stage", "sp-states", "sp-anatomy", "sp-usage", "sp-data", "sp-access", "sp-relations", "sp-gates")


def e(s):
    return html.escape(str(s), quote=True)


def code(s):
    """Backticked spans in spec text become <code>; everything else is escaped."""
    parts = str(s).split("`")
    return "".join(e(p) if i % 2 == 0 else "<code>" + e(p) + "</code>" for i, p in enumerate(parts))


def build(spec, spec_path):
    missing = [k for k in REQUIRED if k not in spec]
    if missing:
        raise SystemExit(f"{spec_path}: missing {', '.join(missing)}")
    if spec["layer"] not in LAYERS:
        raise SystemExit(f"{spec_path}: layer must be one of {', '.join(LAYERS)}")
    n, name, layer = spec["number"], spec["name"], spec["layer"]
    slug = spec.get("slug") or name.lower().replace(" ", "-")
    css = CSS + spec.get("css", "")
    links = "".join(f'<link rel="stylesheet" href="{e(h)}">\n' for h in spec.get("links", []))  # shared kit stylesheets, such as _tokens-light.css
    rows_anat = "".join(f'<tr><td class="sp-num">{i + 1}</td><th scope="row">{e(a["part"])}</th><td>{code(a["role"])}</td><td>{code(a["token"])}</td></tr>'
                        for i, a in enumerate(spec["anatomy"]))
    rows_data = "".join(f'<tr><td><code>{e(d["field"])}</code></td><td>{e(d["type"])}</td><td>{"yes" if d.get("required") else "no"}</td><td>{code(d["note"])}</td></tr>'
                        for d in spec["data"])
    states = "".join(f'<figure class="sp-state"><h3>{e(s["name"])}</h3><div data-state="{i}"></div><p>{code(s["note"])}</p></figure>'
                     for i, s in enumerate(spec["states"]))
    li = lambda xs: "".join(f"<li>{code(x)}</li>" for x in xs)
    rel = lambda xs: "".join(f'<a href="{e(x["href"])}">{e(x["name"])}</a>' if x.get("href") else f"<span>{e(x['name'])}</span>" for x in xs) or "<span>none yet</span>"
    page = f"""<!-- @dsCard group="Specimens" name="{e(name)}" subtitle="{e(layer)} {e(n)} · {e(spec['job'])}" -->
<!-- @arcs-template: kit-specimen -->
<!-- generated by scripts/kit_specimen.py from {os.path.relpath(spec_path, ROOT)}; edit the spec, not this page -->
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(name)} · {e(layer)} {e(n)}</title>
<link rel="stylesheet" href="_tokens.css">
{links}<style>
{css}</style>
</head>
<body>
<main>
<header class="sp-head" id="sp-head"><div class="sp-crumb"><span>ARCS kit</span><span>{e(layer)} {e(n)}</span><span>{e(slug)}</span></div>
<h1>{e(name)}</h1>
<p class="sp-job">{code(spec['job'])}</p></header>
<section class="sp-stage" id="sp-stage" aria-label="Live specimen"><div data-stage></div></section>
<section id="sp-states" aria-labelledby="h-states"><h2 class="section-label" id="h-states">States</h2><div class="sp-states">{states}</div></section>
<section id="sp-anatomy" aria-labelledby="h-anat"><h2 class="section-label" id="h-anat">Anatomy</h2>
<div class="sp-scroll" tabindex="0" role="region" aria-label="Anatomy table"><table class="sp-table"><thead><tr><th scope="col">#</th><th scope="col">Part</th><th scope="col">Type role</th><th scope="col">Token (CSS variable)</th></tr></thead><tbody>{rows_anat}</tbody></table></div></section>
<section id="sp-usage" aria-labelledby="h-use"><h2 class="section-label" id="h-use">Usage</h2>
<div class="sp-two"><div class="sp-yes"><h3>Use it when</h3><ul class="sp-list">{li(spec['use_when'])}</ul></div><div class="sp-no"><h3>Do not use it when</h3><ul class="sp-list">{li(spec['avoid_when'])}</ul></div></div></section>
<section id="sp-data" aria-labelledby="h-data"><h2 class="section-label" id="h-data">Data it reads</h2>
<div class="sp-scroll" tabindex="0" role="region" aria-label="Data table"><table class="sp-table"><thead><tr><th scope="col">Field</th><th scope="col">Type</th><th scope="col">Required</th><th scope="col">Note</th></tr></thead><tbody>{rows_data}</tbody></table></div></section>
<section id="sp-access" aria-labelledby="h-acc"><h2 class="section-label" id="h-acc">Access</h2><ul class="sp-list">{li(spec['access'])}</ul></section>
<section id="sp-relations" aria-labelledby="h-rel"><h2 class="section-label" id="h-rel">Relations</h2>
<div class="sp-two"><div><h3 class="section-label">Built from</h3><div class="sp-rel">{rel(spec['built_from'])}</div></div><div><h3 class="section-label">Used by</h3><div class="sp-rel">{rel(spec['used_by'])}</div></div></div></section>
<section class="sp-gates" id="sp-gates" aria-labelledby="h-gates"><h2 class="section-label" id="h-gates">Gates</h2><ul class="sp-list">{li(spec['gates'])}</ul></section>
</main>
<script src="_player.js"></script>
<script>
var STATES = {json.dumps([s.get("args") for s in spec["states"]])};
{spec['demo']}
</script>
</body>
</html>
"""
    return f"{n}-{slug}.html", page


def specs():
    return sorted(os.path.join(SPECS, f) for f in os.listdir(SPECS) if f.endswith(".json")) if os.path.isdir(SPECS) else []


def main(argv):
    check = "--check" in argv
    paths = specs() if ("--all" in argv or check) else [a for a in argv if not a.startswith("--")]
    if not paths:
        print(__doc__); return 2
    bad = 0
    for sp in paths:
        name, page = build(json.load(open(sp, encoding="utf-8")), sp)
        out = os.path.join(KIT, name)
        if check:
            same = os.path.exists(out) and open(out, encoding="utf-8").read() == page
            print(("✓ " if same else "✖ ") + f"kit-specimen: {name}" + ("" if same else " differs from its spec; rebuild"))
            bad += 0 if same else 1
        else:
            open(out, "w", encoding="utf-8").write(page); print(f"wrote {os.path.relpath(out, ROOT)}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
