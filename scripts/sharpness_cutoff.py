#!/usr/bin/env python3
"""sharpness_cutoff: spectral-cutoff check of an image against its claimed resolution (stdlib only).

Reads an 8-bit PNG (gray, RGB, RGBA; non-interlaced), takes luma, and measures where horizontal
spectral energy ends. ratio = the frequency, as a fraction of Nyquist, containing 99% of AC energy.
A native capture is broadband (ratio near 1); a k-times upscale is band-limited (ratio near 1/k).
It flags band-limited, NOT fake: a smooth native image also scores low (known false positive).

  python3 scripts/sharpness_cutoff.py image.png    # prints the ratio
  python3 scripts/sharpness_cutoff.py --self-test  # plants upscale / native / smooth native
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

def self_test():
    native = _native(64, 7)
    cases = {"native": native, "upscale2x": _bilinear2x(_native(32, 7)), "smooth_native": _smooth_native(64)}
    res = {k: cutoff_ratio(read_png(write_png(v))[2]) for k, v in cases.items()}  # round-trips the PNG decoder
    for k, v in res.items(): print(f"  {k:14s} cutoff_ratio={v:.3f}")
    ok = res["native"] > 0.85 and res["upscale2x"] < 0.7
    print("B1 (native > 0.85, upscale < 0.7):", "PASS" if ok else "FAIL")
    print("B2 (smooth native not flagged):", "PASS" if res["smooth_native"] >= 0.7 else "FAIL = known false positive")
    return 0 if ok else 1

if __name__ == "__main__":
    if sys.argv[1:] == ["--self-test"]: sys.exit(self_test())
    if len(sys.argv) == 2:
        w, h, p = read_png(open(sys.argv[1], "rb").read()); print(f"{cutoff_ratio(p):.3f}"); sys.exit(0)
    print(__doc__); sys.exit(2)
