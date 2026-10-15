# Pre-registered (before run): K1 ordering abs64<abs128<abs256 and oversharp gap (abs256-abs64)/32>=0.15;
# K2 |abs(dither64)-abs(clean64)|/32 < 0.15; K3 smooth scene K1 gap holds; K4 abs(true256)-abs(NN4(64)) >= 4.8.
import sys, random, math
sys.path.insert(0, "scripts")
import sharpness_cutoff as sc
B4 = [[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]]
def absc(p): return sc.cutoff_ratio(p) * (len(p[0]) // 2)
def down(p, k): return [[int(round(v)) for v in r] for r in sc.box_down(p, k)] if k > 1 else p
def quant(p, dither):
    out = []
    for y, r in enumerate(p):
        row = []
        for x, v in enumerate(r):
            t = (B4[y % 4][x % 4] + 0.5) / 16 - 0.5 if dither else 0.0
            q = min(15, max(0, int(round(v / 255 * 15 + t))))
            row.append(int(q / 15 * 255))
        out.append(row)
    return out
def nn4(p): return [[v for v in r for _ in range(4)] for r in p for _ in range(4)]
def edge(seed, n=256):
    rnd = random.Random(seed); g = [[100] * n for _ in range(n)]
    for _ in range(40):
        x0, y0 = rnd.randrange(n), rnd.randrange(n); w, h, c = rnd.randrange(8, 80), rnd.randrange(8, 80), rnd.randrange(256)
        for y in range(y0, min(n, y0 + h)):
            for x in range(x0, min(n, x0 + w)): g[y][x] = c
    return g
def noisy(seed, n=256):
    rnd = random.Random(seed); b = sc._analytic_smooth(n)
    return [[max(0, min(255, v + rnd.randrange(-8, 9))) for v in r] for r in b]
scenes = [("edge s1", edge(1)), ("edge s2", edge(2)), ("edge s3", edge(3)), ("smooth", sc._analytic_smooth(256)),
          ("noisy s1", noisy(1)), ("noisy s2", noisy(2)), ("noisy s3", noisy(3))]
print(f"{'scene':9} a64 a128 a256 gap  dither64 d/32  NN4  K4gap   K1 K2 K4")
for name, m in scenes:
    a256, a128, a64 = absc(m), absc(down(m, 2)), absc(down(m, 4))
    d64 = down(m, 4); dd = absc(quant(d64, True)); cc = absc(quant(d64, False))
    nn = absc(nn4(d64)); gap = (a256 - a64) / 32; dz = abs(dd - cc) / 32; k4 = a256 - nn
    k1 = a64 < a128 < a256 and gap >= .15; k2 = dz < .15; k4ok = k4 >= 4.8
    print(f"{name:9} {a64:3.0f} {a128:4.0f} {a256:4.0f} {gap:5.2f} {dd:5.0f}/{cc:3.0f} {dz:4.2f} {nn:4.0f} {k4:6.1f}  {'P' if k1 else 'F'}  {'P' if k2 else 'F'}  {'P' if k4ok else 'F'}")
