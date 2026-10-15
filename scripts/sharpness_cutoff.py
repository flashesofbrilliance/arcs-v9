#!/usr/bin/env python3
"""sharpness_cutoff: spectral-cutoff check of an image against its claimed resolution (stdlib only).

Reads an 8-bit PNG (gray, RGB, RGBA; non-interlaced), takes luma, and measures where horizontal
spectral energy ends. ratio = the frequency, as a fraction of Nyquist, containing 99% of AC energy.
A native capture is broadband (ratio near 1); a k-times upscale is band-limited (ratio near 1/k).
It flags band-limited, NOT fake: a smooth native image also scores low (known false positive).

  python3 scripts/sharpness_cutoff.py image.png    # prints the ratio
  python3 scripts/sharpness_cutoff.py --self-test  # plants upscale / native / smooth / injected / jpeg-like / overfit
  python3 scripts/sharpness_cutoff.py --compare claimed.png source.png  # test (b): round-trip and residual (2x)
"""
import cmath, math, struct, sys, zlib

def read_png(data):
    assert data[:8] == b"\x89PNG\r\n\x1a\n", "not a PNG"
    pos, idat, w = 8, b"", None
    while pos < len(data):
        n, t = struct.unpack(">I4s", data[pos:pos + 8]); body = data[pos + 8:pos + 8 + n]; pos += 12 + n
        if t == b"IHDR":
            w, h, depth, ctype, _, _, inter = struct.unpack(">IIBBBBB", body)
            assert depth == 8 and ctype in (0, 2, 6) and inter == 0, "unsupported PNG"
        elif t == b"IDAT": idat += body
    ch = {0: 1, 2: 3, 6: 4}[ctype]; raw = zlib.decompress(idat); stride = w * ch
    rows, prev = [], bytearray(stride)
    for y in range(h):
        f = raw[y * (stride + 1)]; cur = bytearray(raw[y * (stride + 1) + 1:(y + 1) * (stride + 1)])
        for i in range(stride):
            a = cur[i - ch] if i >= ch else 0; b = prev[i]; c = prev[i - ch] if i >= ch else 0
            if f == 1: cur[i] = (cur[i] + a) & 255
            elif f == 2: cur[i] = (cur[i] + b) & 255
            elif f == 3: cur[i] = (cur[i] + (a + b) // 2) & 255
            elif f == 4:
                p = a + b - c; pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                cur[i] = (cur[i] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        rows.append(cur); prev = cur
    return w, h, [[r[x * ch] if ch == 1 else (r[x*ch] * 299 + r[x*ch+1] * 587 + r[x*ch+2] * 114) // 1000
                   for x in range(w)] for r in rows]

def write_png(pix):
    h, w = len(pix), len(pix[0])
    raw = b"".join(b"\x00" + bytes(r) for r in pix)
    def chunk(t, b): return struct.pack(">I", len(b)) + t + b + struct.pack(">I", zlib.crc32(t + b))
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 0, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))

def cutoff_ratio(pix, rows=16, frac=0.99):
    h, w = len(pix), len(pix[0]); half = w // 2; energy = [0.0] * half
    for y in range(0, h, max(1, h // rows)):
        r = pix[y]; m = sum(r) / w; x = [v - m for v in r]
        for k in range(1, half + 1):
            s = sum(x[n] * cmath.exp(-2j * math.pi * k * n / w) for n in range(w))
            energy[k - 1] += abs(s) ** 2
    tot = sum(energy) or 1.0; acc = 0.0
    for k, e in enumerate(energy, 1):
        acc += e
        if acc >= frac * tot: return k / half
    return 1.0

def _native(n, seed):
    s = seed; out = []
    for _ in range(n):
        row = []
        for _ in range(n):
            s = (s * 1103515245 + 12345) & 0x7fffffff; row.append((s >> 16) & 255)
        out.append(row)
    return out

def _bilinear2x(p):
    n = len(p)
    def g(y, x): return p[min(y, n - 1)][min(x, n - 1)]
    return [[int(sum(g((y + dy) // 2, (x + dx) // 2) for dy in (0, 1) for dx in (0, 1)) / 4)
             for x in range(2 * n)] for y in range(2 * n)]

def _smooth_native(n):
    return [[int(128 + 60 * math.sin(x / (n / 3.0)) * math.cos(y / (n / 4.0)) + ((x * 7 + y * 13) % 5)) for x in range(n)]
            for y in range(n)]

def tail_ratio(pix, rows=16, cap=256):
    """Mean energy of the top 20% of bins over mean energy of the 25-50% band (rescues smooth-but-noisy natives)."""
    h, w = len(pix), min(len(pix[0]), cap); half = w // 2; energy = [0.0] * half
    for y in range(0, h, max(1, h // rows)):
        r = pix[y][:w]; m = sum(r) / w; x = [v - m for v in r]
        for k in range(1, half + 1):
            energy[k - 1] += abs(sum(x[n] * cmath.exp(-2j * math.pi * k * n / w) for n in range(w))) ** 2
    mid = energy[half // 4: half // 2]; tail = energy[int(half * 0.8):]
    return (sum(tail) / len(tail)) / ((sum(mid) / len(mid)) or 1.0)

def box_down(p, k=2):
    n = len(p) // k
    return [[sum(p[y * k + dy][x * k + dx] for dy in range(k) for dx in range(k)) / (k * k) for x in range(n)] for y in range(n)]

def mse(a, b):
    n = sum(len(r) for r in a)
    return sum((u - v) ** 2 for ra, rb in zip(a, b) for u, v in zip(ra, rb)) / n

def inject_detail(p, d=20):
    """Zero-mean-per-2x2-block fake detail: survives a box round trip, adds no information."""
    sg = ((1, -1), (-1, 1))
    return [[v + d * sg[y % 2][x % 2] for x, v in enumerate(r)] for y, r in enumerate(p)]

def jpeg_like(p, q=40):
    """8x8 DCT, uniform quantization, inverse: stdlib stand-in for JPEG loss (no JPEG decoder in stdlib)."""
    n = len(p); c = [[math.sqrt((1 if u == 0 else 2) / 8) * math.cos((2 * x + 1) * u * math.pi / 16) for x in range(8)] for u in range(8)]
    out = [[0] * n for _ in range(n)]
    for by in range(0, n, 8):
        for bx in range(0, n, 8):
            blk = [[p[by + y][bx + x] - 128 for x in range(8)] for y in range(8)]
            t = [[sum(c[u][y] * sum(c[v][x] * blk[y][x] for x in range(8)) for y in range(8)) for v in range(8)] for u in range(8)]
            t = [[round(t[u][v] / q) * q for v in range(8)] for u in range(8)]
            for y in range(8):
                for x in range(8):
                    out[by + y][bx + x] = max(0, min(255, int(128 + sum(c[u][y] * sum(c[v][x] * t[u][v] for v in range(8)) for u in range(8)))))
    return out

def splat_gap(width, n_train=24, n_test=200):
    """Toy for test (c): 1D scene fit by one Gaussian bump per training sample. Returns held-out MSE / train MSE."""
    f = lambda x: math.sin(2 * math.pi * x) + 0.5 * math.sin(6 * math.pi * x)
    st = [99]
    def noise():
        st[0] = (st[0] * 1103515245 + 12345) & 0x7fffffff
        return (st[0] / 0x7fffffff - 0.5) * 0.6
    xs = [(i + 0.5) / n_train for i in range(n_train)]; ys = [f(x) + noise() for x in xs]
    def fit(x):
        wts = [math.exp(-((x - xi) / width) ** 2) for xi in xs]
        return sum(w * y for w, y in zip(wts, ys)) / (sum(wts) or 1e-12)
    tr = sum((fit(x) - y) ** 2 for x, y in zip(xs, ys)) / n_train
    te = sum((fit(x) - f(x)) ** 2 for x in [(i + 0.37) / n_test for i in range(n_test)]) / n_test
    return te / max(tr, 1e-9)

def _noisy_smooth(n):
    s = 5; out = _smooth_native(n)
    for r in out:
        for i in range(n):
            s = (s * 1103515245 + 12345) & 0x7fffffff; r[i] = max(0, min(255, r[i - 0] + ((s >> 16) % 7) - 3))
    return out

def _analytic_smooth(n):
    return [[int(128 + 60 * math.sin(x / (n / 3.0)) * math.cos(y / (n / 4.0))) for x in range(n)] for y in range(n)]

def self_test():
    rt = lambda v: read_png(write_png(v))[2]  # round-trips the PNG decoder
    src = _native(32, 7); native = _native(64, 7); up = _bilinear2x(src)
    cases = {"native": native, "upscale2x": up, "smooth_native": _smooth_native(64)}
    res = {k: cutoff_ratio(rt(v)) for k, v in cases.items()}
    for k, v in res.items(): print(f"  {k:14s} cutoff_ratio={v:.3f}")
    ok = res["native"] > 0.85 and res["upscale2x"] < 0.7
    print("B1 (native > 0.85, upscale < 0.7):", "PASS" if ok else "FAIL")
    print("B2 (smooth native not flagged by cutoff):", "PASS" if res["smooth_native"] >= 0.7 else "FAIL = known false positive (round 1)")
    # B3 / B4: test (b), downscale-then-compare against the source
    other = _bilinear2x(_native(32, 11)); inj = [[max(0, min(255, v)) for v in r] for r in inject_detail(up)]
    rt_err = {k: mse(box_down(v), src) for k, v in {"faithful": up, "wrong_content": other, "injected": inj}.items()}
    res_err = {k: mse(v, up) for k, v in {"faithful": up, "wrong_content": other, "injected": inj}.items()}
    print("  round-trip mse vs source:", {k: round(v, 1) for k, v in rt_err.items()})
    print("  residual mse vs up(source):", {k: round(v, 1) for k, v in res_err.items()})
    b3 = rt_err["wrong_content"] > 3 * max(rt_err["faithful"], 1.0)
    print("B3 (round trip separates wrong content):", "PASS" if b3 else "FAIL")
    b4a = rt_err["injected"] <= 3 * max(rt_err["faithful"], 1.0); b4b = res_err["injected"] > 3 * max(res_err["faithful"], 1.0)
    print("B4 (round trip misses injected detail, residual catches it):", "PASS" if (b4a and b4b) else f"FAIL (rt_misses={b4a}, residual_catches={b4b})")
    # B5: noise-floor statistic
    t = {"native": tail_ratio(native), "upscale2x": tail_ratio(up), "smooth_noisy": tail_ratio(_noisy_smooth(64)), "smooth_analytic": tail_ratio(_analytic_smooth(64))}
    print("  tail_ratio:", {k: round(v, 3) for k, v in t.items()})
    b5 = t["smooth_noisy"] > 0.3 and t["upscale2x"] < 0.3
    print("B5 (noise floor rescues smooth+noise native):", "PASS" if b5 else "FAIL")
    print("  limit (expected): smooth_analytic tail", "also low = indistinguishable from upscale" if t["smooth_analytic"] < 0.3 else "is high (limit not reproduced)")
    # B6: JPEG-like loss
    jq = cutoff_ratio(jpeg_like(native)); jt = tail_ratio(jpeg_like(native))
    print(f"  jpeg_like native: cutoff_ratio={jq:.3f} tail_ratio={jt:.3f}")
    print("B6 (jpeg-like loss false-positives under cutoff):", "PASS (confirmed false positive)" if jq < 0.85 else "FAIL (cutoff robust to it at q=40 on a white-noise texture)")
    jh = jpeg_like(native, q=400)  # post-hoc probe, NOT part of B6: coarse quantizer
    print(f"  post-hoc probe q=400: cutoff_ratio={cutoff_ratio(jh):.3f} tail_ratio={tail_ratio(jh):.3f}")
    # B7: toy test (c)
    g_over, g_fit = splat_gap(0.004), splat_gap(0.05)
    print(f"  splat gap (held-out/train mse): overfit={g_over:.2f} wellfit={g_fit:.2f}")
    b7 = g_over > 3 * g_fit
    print("B7 (toy held-out gap separates overfit):", "PASS" if b7 else "FAIL")
    return 0 if (ok and b3 and b4a and b4b and b5 and b7) else 1  # B2, B6 and the analytic limit are reported findings, not gates

if __name__ == "__main__":
    if sys.argv[1:] == ["--self-test"]: sys.exit(self_test())
    if len(sys.argv) == 4 and sys.argv[1] == "--compare":
        c = read_png(open(sys.argv[2], "rb").read())[2]; sr = read_png(open(sys.argv[3], "rb").read())[2]
        print(f"round_trip_mse={mse(box_down(c), sr):.2f} residual_mse={mse(c, _bilinear2x(sr)):.2f}"); sys.exit(0)
    if len(sys.argv) == 2:
        w, h, p = read_png(open(sys.argv[1], "rb").read()); print(f"{cutoff_ratio(p):.3f}"); sys.exit(0)
    print(__doc__); sys.exit(2)
