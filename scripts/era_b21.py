#!/usr/bin/env python3
"""era_b21: build and score the B21 vision-judge trials (stdlib; uses scripts/sharpness_cutoff.py).

  python3 scripts/era_b21.py make OUTDIR SRC.png [SRC.png ...]   # writes tNN_A.png, tNN_B.png; writes NO key
  python3 scripts/era_b21.py score ANSWERS.json SRC.png [...]     # ANSWERS = {"t01": "A", ...}; recomputes the order from SEED
Sources are cropped to the central 256x256. Foils: nn4 (NN 4x of the 64 row), bil4 (bilinear 4x of 64), bil2 (bilinear 2x of 128).
"""
import json, os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sharpness_cutoff as sc
SEED, FOILS = 21, ("nn4", "bil4", "bil2")

def load(path):
    w, h, pix = sc.read_png(open(path, "rb").read())
    y0, x0 = max(0, (h - 256) // 2), max(0, (w - 256) // 2)
    return [r[x0:x0 + 256] for r in pix[y0:y0 + 256]]
def down(p, k): return [[int(round(v)) for v in r] for r in sc.box_down(p, k)]
def clip(p): return [[min(255, max(0, int(v))) for v in r] for r in p]
def foil(p, kind):
    if kind == "nn4": return [[v for v in r for _ in range(4)] for r in down(p, 4) for _ in range(4)]
    if kind == "bil4": return clip(sc._bilinear2x(sc._bilinear2x(down(p, 4))))
    return clip(sc._bilinear2x(down(p, 2)))
def absc(p): return sc.cutoff_ratio(p) * (len(p[0]) // 2)
def plan(n_src):
    rnd = random.Random(SEED); t = [(s, f) for s in range(n_src) for f in FOILS]; rnd.shuffle(t)
    return [(i + 1, s, f, rnd.random() < 0.5) for i, (s, f) in enumerate(t)]  # (id, source, foil, genuine_is_A)
def make(out, srcs):
    os.makedirs(out, exist_ok=True); imgs = [load(p) for p in srcs]
    for tid, s, f, gA in plan(len(srcs)):
        g, u = imgs[s], foil(imgs[s], f); a, b = (g, u) if gA else (u, g)
        for name, im in (("A", a), ("B", b)): open(f"{out}/t{tid:02d}_{name}.png", "wb").write(sc.write_png(im))
    print(f"wrote {len(srcs) * len(FOILS)} trials to {out}; key not written")
def score(ans, srcs):
    imgs = [load(p) for p in srcs]; answers = json.load(open(ans)); tot = {f: [0, 0] for f in FOILS}; st = {f: [0, 0] for f in FOILS}
    for tid, s, f, gA in plan(len(srcs)):
        pick = answers.get(f"t{tid:02d}"); truth = "B" if gA else "A"
        tot[f][1] += 1; tot[f][0] += pick == truth
        gap = absc(imgs[s]) - absc(foil(imgs[s], f)); st[f][1] += 1; st[f][0] += gap >= 4.8
    for name, d in (("judge", tot), ("statistic", st)):
        print(name, {f: f"{d[f][0]}/{d[f][1]}" for f in FOILS}, "overall", f"{sum(v[0] for v in d.values())}/{sum(v[1] for v in d.values())}")
if __name__ == "__main__":
    if sys.argv[1] == "make": make(sys.argv[2], sys.argv[3:])
    elif sys.argv[1] == "score": score(sys.argv[2], sys.argv[3:])
