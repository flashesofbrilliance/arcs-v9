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

# ---- Round 2 (pre-registered in the concept note before this was run) ----
# B12 three arms on the 64 row: unquantized / 4-bit quantize-only / 4-bit quantize+dither.
# B13 two real rendered images (central 256 crop): ordering a64<a128<a256 and K4 gap >= 4.8 vs NN4(64).
def round2():
    print("\nB12 arms (abs cutoff on the 64 row): unq / q4 / q4+dither ; shifts /32")
    for name, m in scenes:
        d64 = down(m, 4); u = absc(d64); q = absc(quant(d64, False)); qd = absc(quant(d64, True))
        print(f"{name:9} {u:3.0f} {q:3.0f} {qd:3.0f}   q4-vs-unq {abs(q-u)/32:4.2f}  dither-vs-q4 {abs(qd-q)/32:4.2f}")
    print("\nB13 real images")
    for path in ("public/good-fears-og.png", "public/honest-og.png"):
        w, h, pix = sc.read_png(open(path, "rb").read())
        y0, x0 = (h - 256) // 2, (w - 256) // 2
        m = [r[x0:x0 + 256] for r in pix[y0:y0 + 256]]
        a256, a128, a64 = absc(m), absc(down(m, 2)), absc(down(m, 4)); nn = absc(nn4(down(m, 4)))
        print(f"{path:26} {w}x{h} a64/a128/a256 {a64:.0f}/{a128:.0f}/{a256:.0f}  ordering {'ok' if a64 < a128 < a256 else 'INVERTS'}  K4gap {a256 - nn:.1f}")
if "--round2" in sys.argv: round2()

# ---- Round 3: pass PNG paths after --real (central 256 luma crop; same statistic as rounds 1 and 2) ----
if "--real" in sys.argv:
    print("\nreal PNGs")
    for path in sys.argv[sys.argv.index("--real") + 1:]:
        w, h, pix = sc.read_png(open(path, "rb").read())
        y0, x0 = (h - 256) // 2, (w - 256) // 2
        m = [r[x0:x0 + 256] for r in pix[y0:y0 + 256]]
        a256, a128, a64 = absc(m), absc(down(m, 2)), absc(down(m, 4)); nn = absc(nn4(down(m, 4)))
        print(f"{path.rsplit('/', 1)[-1]:16} {w}x{h} a64/a128/a256 {a64:.0f}/{a128:.0f}/{a256:.0f}  ordering {'ok' if a64 < a128 < a256 else 'INVERTS'}  K4gap {a256 - nn:.1f}")

# ---- Round 5: B18 footprint (pass 1024 PNGs after --down4) and B19 smoothness (pass 256 PNGs after --std) ----
if "--down4" in sys.argv:
    print("\ndown4 (1024 native region, box-downsampled 4x to 256)")
    for path in sys.argv[sys.argv.index("--down4") + 1:]:
        w, h, pix = sc.read_png(open(path, "rb").read())
        m = down(pix, 4); a256, a128, a64 = absc(m), absc(down(m, 2)), absc(down(m, 4)); nn = absc(nn4(down(m, 4)))
        print(f"{path.rsplit('/', 1)[-1]:12} a64/a128/a256 {a64:.0f}/{a128:.0f}/{a256:.0f}  ordering {'ok' if a64 < a128 < a256 else 'INVERTS'}  K4gap {a256 - nn:.1f}")
if "--std" in sys.argv:
    print("\nstd of luma per 256 crop")
    for path in sys.argv[sys.argv.index("--std") + 1:]:
        w, h, pix = sc.read_png(open(path, "rb").read()); v = [x for r in pix for x in r]; mu = sum(v) / len(v)
        print(f"{path.rsplit('/', 1)[-1]:12} std {(sum((x - mu) ** 2 for x in v) / len(v)) ** 0.5:.2f}")

# ---- Round 6: --r5 <256 png> ... prints std, K4 gap with nearest-neighbour and bilinear foils, and Spearman of std vs each gap ----
def _rank(v):
    s = sorted(range(len(v)), key=lambda i: v[i]); r = [0.0] * len(v); i = 0
    while i < len(s):
        j = i
        while j + 1 < len(s) and v[s[j + 1]] == v[s[i]]: j += 1
        for k in range(i, j + 1): r[s[k]] = (i + j) / 2 + 1
        i = j + 1
    return r
def spearman(a, b):
    ra, rb = _rank(a), _rank(b); n = len(a); ma, mb = sum(ra) / n, sum(rb) / n
    den = (sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb)) ** .5
    return sum((x - ma) * (y - mb) for x, y in zip(ra, rb)) / den if den else float("nan")
if "--r5" in sys.argv:
    print("\nr5 (std, K4 gap nearest, K4 gap bilinear)")
    sd, gn, gb = [], [], []
    for path in sys.argv[sys.argv.index("--r5") + 1:]:
        w, h, pix = sc.read_png(open(path, "rb").read()); v = [x for r in pix for x in r]; mu = sum(v) / len(v)
        s = (sum((x - mu) ** 2 for x in v) / len(v)) ** 0.5; d64 = down(pix, 4); a256 = absc(pix)
        n_, b_ = a256 - absc(nn4(d64)), a256 - absc(sc._bilinear2x(sc._bilinear2x(d64)))
        sd.append(s); gn.append(n_); gb.append(b_)
        print(f"{path.rsplit('/', 1)[-1]:12} std {s:5.2f}  nearest {n_:6.1f}  bilinear {b_:6.1f}")
    print(f"clear 4.8: nearest {sum(g >= 4.8 for g in gn)}/{len(gn)}  bilinear {sum(g >= 4.8 for g in gb)}/{len(gb)}")
    print(f"spearman std vs nearest gap {spearman(sd, gn):.3f}   std vs bilinear gap {spearman(sd, gb):.3f}")
