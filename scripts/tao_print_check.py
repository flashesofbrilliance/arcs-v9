#!/usr/bin/env python3
"""tao_print_check.py: pre-registered kill checks for the Tao silkscreen print (K1-K4).

  K1 determinism  same (id, recipe, seed) -> byte-identical SVG
  K2 monotonic    registration offset and grain count are non-increasing in fidelity (structural)
  K3 machine blind-ranking proxy  six prints, labels shuffled; a reference-free score computed from
                  PIXELS ONLY (grey grain share + ink-colour centroid spread) must rank them with
                  Spearman rho >= 0.9 against declared fidelity. This is a MACHINE proxy: it shows the
                  encoding is recoverable from the image, NOT that a person perceives it.
  K4 twist        the closing Mobius panel is mirrored and ink-swapped, others are not

Needs playwright (repo node_modules), numpy, PIL for K3 only. `--blind-sheet DIR` also writes the
shuffled contact sheet + key for the human version of K3.
"""
import argparse, json, random, re, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import tao_print as T

PID = "adr039-W-recapitulate"
FS = [0.15, 0.30, 0.50, 0.70, 0.85, 0.97]


def page(svg_text):
    tok = (ROOT / "src/ui-kit/recoil-report/_tokens.css").read_text()
    return (f'<!doctype html><meta charset="utf-8"><style>{tok}body{{margin:0;background:var(--bg)}}'
            f'svg{{display:block;width:640px}}</style>{svg_text}')


def shot(svg_text, out):
    src = ROOT / ".claude" / "tmp_tao_shot.html"
    src.parent.mkdir(exist_ok=True)
    src.write_text(page(svg_text))
    js = ("const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();"
          "const p=await b.newPage({viewport:{width:640,height:900}});"
          f"await p.goto('file://{src}');await p.locator('svg').screenshot({{path:'{out}'}});await b.close()}})()")
    subprocess.run(["node", "-e", js], cwd=ROOT, check=True)
    src.unlink()


def score(png):
    import numpy as np
    from PIL import Image
    im = np.asarray(Image.open(png).convert("RGB")).astype(int)
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    grey = (abs(r - 0x83) < 14) & (abs(g - 0x91) < 14) & (abs(b - 0xa7) < 14)       # --dimmed grain
    cyan = (r < 90) & (g > 150) & (b > 150) & ~grey
    gold = (r > 180) & (g > 150) & (b < 120)
    red = (r > 180) & (g < 140) & (b > 60) & (b < 170)

    def cen(m):
        ys, xs = np.nonzero(m)
        return (xs.mean(), ys.mean()) if len(xs) else (0, 0)
    spread = np.mean([np.hypot(a[0] - c[0], a[1] - c[1]) for a, c in
                      [(cen(cyan), cen(gold)), (cen(gold), cen(red)), (cen(cyan), cen(red))]])
    return -(grey.mean() * 1000 + spread * 0.1)          # higher = clearer


def spearman(a, b):
    ra = [sorted(a).index(x) for x in a]
    rb = [sorted(b).index(x) for x in b]
    n = len(a)
    return 1 - 6 * sum((x - y) ** 2 for x, y in zip(ra, rb)) / (n * (n * n - 1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--blind-sheet")
    ap.add_argument("--skip-pixels", action="store_true")
    ns = ap.parse_args()
    row = T.load(PID)
    res = {}

    a, b = T.svg(row, 0.9, 7), T.svg(row, 0.9, 7)
    res["K1 determinism"] = a == b and a != T.svg(row, 0.9, 8)

    regs, specks = [], []
    for f in FS:
        s = T.svg(row, f, 7)
        panels = re.findall(r'data-k="(\d+)" data-reg="([\d.]+)" data-specks="(\d+)"', s)
        regs.append(sum(float(x[1]) for x in panels) / len(panels))
        specks.append(sum(int(x[2]) for x in panels))
    mono = lambda v: all(v[i] >= v[i + 1] for i in range(len(v) - 1))
    res["K2 monotonic (reg, grain)"] = mono(regs) and mono(specks) and regs[0] > regs[-1] and specks[0] > specks[-1]
    print("  reg by f   :", [round(x, 2) for x in regs])
    print("  specks by f:", specks)

    s = T.svg(row, 0.9, 7)
    tw = re.findall(r'data-twist="(\d)"', s)
    res["K4 twist only on closing panel"] = tw == ["0"] * 5 + ["1"] and "scale(-1 1)" in s

    if not ns.skip_pixels:
        tmp = Path(tempfile.mkdtemp())
        order = list(range(len(FS)))
        random.Random(11).shuffle(order)
        scores, pngs = {}, {}
        for i, f in enumerate(FS):
            p = tmp / f"{i}.png"
            shot(T.svg(row, f, 7), str(p))
            scores[f] = score(str(p))
            pngs[f] = p
        rho = spearman(list(FS), [scores[f] for f in FS])
        print("  pixel score:", {f: round(v, 2) for f, v in scores.items()}, "rho", round(rho, 3))
        res["K3 machine blind-ranking proxy (rho>=0.9)"] = rho >= 0.9
        if ns.blind_sheet:
            from PIL import Image
            d = Path(ns.blind_sheet)
            d.mkdir(parents=True, exist_ok=True)
            ims = [Image.open(pngs[FS[i]]) for i in order]
            w, h = ims[0].size
            sheet = Image.new("RGB", (w * 3, h * 2), (2, 4, 8))
            for n, im in enumerate(ims):
                sheet.paste(im, ((n % 3) * w, (n // 3) * h))
            sheet.save(d / "blind-sheet.png")
            (d / "blind-key.json").write_text(json.dumps(
                {chr(65 + n): FS[i] for n, i in enumerate(order)}, indent=1))
            print("  blind sheet ->", d)

    for k, v in res.items():
        print(("PASS " if v else "FAIL ") + k)
    sys.exit(0 if all(res.values()) else 1)


main()
