#!/usr/bin/env python3
"""tao_print_export.py: export a Tao print as a PNG (the Artifact viewer blocks downloads; this runs outside it).

  python3 scripts/tao_print_export.py <proverb-id> [--fidelity 0.8] [--seed 7] [--ground dark|paper] [--scale 3] --out print.png
  python3 scripts/tao_print_export.py --recipe <recipe.json | 'inline json'> [--scale 3] --out print.png

--recipe exports exactly what the Tao print studio (_ARTIFACTS/tao-print-studio.html) shows for that recipe, every style and
control included, by driving the studio headless (scripts/tao_studio_export.mjs). Get a recipe with the studio's "Copy recipe".
  python3 scripts/tao_print_export.py [<proverb-id>] --preset silk|street|fancy|brain|invader|tag [--fidelity 0.8] [--seed 7] [--ground dark|paper] --out print.png

--panels DIR (with --preset or --recipe) also writes the whole print and one PNG per panel into DIR.
--preset exports one of the studio's style presets (brain = Brainwash pop splatter and halftone, invader = tile mosaic, fancy =
hand-lettered, tag = the AI tag artist). The proverb, fidelity, seed and ground are applied only when you give them.

Renders the print SVG inside a margin with a title band and a provenance band, kit tokens inlined (src/ui-kit/recoil-report/_tokens.css) through Playwright (repo
node_modules), so the PNG matches the page. Deterministic from (id, fidelity, seed, ground). Not an edition.
"""
import argparse, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import tao_print as T

ap = argparse.ArgumentParser()
ap.add_argument("id", nargs="?")
ap.add_argument("--recipe", help="studio recipe: a JSON file or inline JSON; exports the studio look instead of the default recipe")
ap.add_argument("--fidelity", type=float, default=None)
ap.add_argument("--seed", type=int, default=None)
ap.add_argument("--ground", choices=["dark", "paper"], default=None)
ap.add_argument("--panels", metavar="DIR", help="also save the whole print and every panel as its own PNG into DIR (studio export only)")
ap.add_argument("--preset", choices=["silk", "street", "fancy", "brain", "invader", "tag"], help="export a studio style preset")
ap.add_argument("--scale", type=int, default=3)
ap.add_argument("--out", required=True)
ns = ap.parse_args()
if ns.recipe or ns.preset:
    import json
    over = json.loads(ns.recipe) if ns.recipe and ns.recipe.lstrip().startswith("{") else (json.loads(Path(ns.recipe).read_text()) if ns.recipe else {})
    if ns.id: over["proverb"] = ns.id
    if ns.fidelity is not None: over["fidelity"] = round(ns.fidelity * 100)
    if ns.seed is not None: over["seed"] = ns.seed
    if ns.ground is not None: over["ground"] = ns.ground
    cmd = ["node", str(ROOT / "scripts/tao_studio_export.mjs"), json.dumps(over) if over else "-", str(Path(ns.out).resolve()), "--scale", str(ns.scale)]
    if ns.preset: cmd += ["--preset", ns.preset]
    if ns.panels: cmd += ["--panels", str(Path(ns.panels).resolve())]
    subprocess.run(cmd, cwd=ROOT, check=True)
    sys.exit(0)
if not ns.id:
    ap.error("give a proverb id, --recipe, or --preset")
ns.fidelity = 0.8 if ns.fidelity is None else ns.fidelity
ns.seed = 7 if ns.seed is None else ns.seed
ns.ground = ns.ground or "dark"

T.PAPER = ns.ground == "paper"
row = T.load(ns.id)
svg = T.svg(row, ns.fidelity, ns.seed, caption=False)
tok = (ROOT / "src/ui-kit/recoil-report/_tokens.css").read_text()
ref = row["canon_ref"].split("#")[-1]
tmp = Path(tempfile.mkdtemp()) / "print.html"
tmp.write_text(f"""<!doctype html><meta charset="utf-8"><style>{tok}
body{{margin:0;background:var(--bg);color:var(--text)}}
.sheet{{width:996px;padding:48px;box-sizing:border-box}}
.band{{display:flex;justify-content:space-between;align-items:baseline;gap:16px;font-family:var(--ds-font-mono);font-size:14px;letter-spacing:.14em;text-transform:uppercase;color:var(--dimmed)}}
.band b{{color:var(--cyan);font-weight:600}}
.top{{padding-bottom:20px;border-bottom:1px solid var(--border);margin-bottom:28px}}
.bot{{padding-top:20px;border-top:1px solid var(--border);margin-top:28px;letter-spacing:.04em;text-transform:none;flex-wrap:wrap}}
svg{{display:block;width:900px}}</style>
<div class="sheet" id="sheet"><div class="band top"><b>The Tao of ARCS</b><span>{ref} &middot; {row["aspect"]}.{row["verb"]}</span></div>{svg}
<div class="band bot"><span>{row["id"]} &middot; fidelity {ns.fidelity} &middot; seed {ns.seed} &middot; {ns.ground} ground</span><span>Reproducible from id, recipe and seed. Not an edition.</span></div></div>""")
out = str(Path(ns.out).resolve())
js = ("const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();"
      f"const p=await b.newPage({{viewport:{{width:900,height:1200}},deviceScaleFactor:{ns.scale}}});"
      f"await p.goto('file://{tmp}');await p.locator('#sheet').screenshot({{path:'{out}'}});await b.close()}})()")
subprocess.run(["node", "-e", js], cwd=ROOT, check=True)
print(out)
