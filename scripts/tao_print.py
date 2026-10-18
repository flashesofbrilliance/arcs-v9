#!/usr/bin/env python3
"""tao_print.py: deterministic silkscreen-style print of one Tao proverb (stdlib only).

A print is a pure function of (proverb id, recipe, seed). Form borrowed from serial screenprint
practice: ONE mold repeated in a grid, flat posterized inks, registration and ink loss drifting
across repeats. Subject is the proverb; no third-party imagery.

Honest encoding (design note _PATTERNS/2026-10-15-tao-silkscreen-prints.md):
  shape code  = (aspect index in D R W C H, verb index in the ADR-041 order)  -> mold geometry + ink order
  fidelity f  = recipe input in [0,1]. Proverbs carry NO per-row NCI or Y state, so f is DECLARED,
                never inferred. misregistration and grain scale with (1 - f).

  python3 scripts/tao_print.py <proverb-id> [--fidelity 0.9] [--seed 7] [--out print.svg]
"""
import argparse, hashlib, json, math, random, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASPECTS = "DRWCH"
VERBS = ["analyze", "assess", "evaluate", "synthesize", "recapitulate"]
INKS = ["var(--cyan)", "var(--green)", "var(--gold)", "var(--red)"]
SWAP = {0: 2, 1: 3, 2: 0, 3: 1}          # half twist swaps cyan<->gold, green<->red
CELL = 120                                # panel size in user units
MAX_OFFSET = 9.0                          # px of misregistration at f=0 on the last repeat
MAX_SPECKS = 140                          # grain specks per panel at f=0 on the last repeat


def load(pid):
    rows = json.loads((ROOT / "runtime/tao/proverbs.json").read_text())["proverbs"]
    for r in rows:
        if r["id"] == pid:
            return r
    sys.exit(f"unknown proverb id: {pid}")


def rng(pid, seed, *k):
    h = hashlib.sha256(f"{pid}|{seed}|{'|'.join(map(str, k))}".encode()).digest()
    return random.Random(int.from_bytes(h[:8], "big"))


NU = 56               # facets around the strip
NV = 4                # bands across the strip (four inks)
PHASE = 0.9           # instrument default rotation
HORIZON = 64          # horizon y in panel units
MAX_PLATE = 7.0       # plate misregistration in panel units at f=0 on the last repeat


def project(u, v, ph):
    """Same parametrization as _ARTIFACTS/arcs-moire-mobius.html, in a 100-unit panel. Returns x, y, depth."""
    x = (1 + v * math.cos(u / 2)) * math.cos(u)
    y = (1 + v * math.cos(u / 2)) * math.sin(u)
    z = v * math.sin(u / 2)
    x1 = x * math.cos(ph) + z * math.sin(ph)
    z1 = -x * math.sin(ph) + z * math.cos(ph)
    t = -0.52
    y1 = y * math.cos(t) - z1 * math.sin(t)
    z2 = y * math.sin(t) + z1 * math.cos(t)
    sc = 3.4 / (3.4 + z2) * 34
    return 50 + x1 * sc, 46 + y1 * sc, z2


def facets(ph=PHASE):
    """Depth-sorted flat facets of the strip. Each carries its face (the sign of its screen area flips as the
    strip twists, so the two faces of the Moebius print in different inks) and its band."""
    out = []
    vs = [(-0.5 + j / NV) * 0.8 for j in range(NV + 1)]
    for i in range(NU):
        u0, u1 = 2 * math.pi * i / NU, 2 * math.pi * (i + 1) / NU
        for j in range(NV):
            q = [project(u0, vs[j], ph), project(u1, vs[j], ph),
                 project(u1, vs[j + 1], ph), project(u0, vs[j + 1], ph)]
            area = sum(q[k][0] * q[(k + 1) % 4][1] - q[(k + 1) % 4][0] * q[k][1] for k in range(4))
            out.append((sum(p[2] for p in q) / 4, area > 0, j, " ".join(f"{p[0]:.1f},{p[1]:.1f}" for p in q), i))
    out.sort(key=lambda t: -t[0])
    return out


_FC = {}


def facets_at(ph):
    if ph not in _FC:
        _FC[ph] = facets(ph)
    return _FC[ph]


# Permutation table: each repeat is a lawful variant of the same mold (ADR-071: one surface, many views).
VIEWS = [0.9, 0.1, 1.15, -0.6, 2.2, 0.5, -0.9, 2.6, 0.0]       # strip rotation per repeat
GROUNDS = [None, 2, None, 3, 0, None, 1, None, 2]            # flat ink ground per repeat (index into PLATES)
PLATES = ["var(--cyan)", "var(--green)", "var(--gold)", "var(--red)"]   # ink = face * 2 + band parity


def panel(pid, seed, f, k, n, a, v, swap=False, mirror=False):
    """One pull of the mold. Four plates (inks), each printed flat and offset from the others by an amount that
    grows with (1 - f) and the repeat index (misregistration); ink drops out in patches with the same law
    (the instrument's fog); grain specks sit on the horizon band."""
    drift = k / max(1, n - 1)
    loss = 1.0 - f
    drop = 0.7 * loss * (0.2 + 0.8 * drift)
    plates = [[], [], [], []]
    dropped = 0
    r = rng(pid, seed, "ink", k)
    ph = VIEWS[k % 9]
    gnd = GROUNDS[k % 9]
    for _, face, band, pts, i in facets_at(ph):
        ink = ((2 if face else 0) + (band % 2) + k) % 4          # ink rotation: which plate prints which face and band
        if swap:
            ink = (ink + 2) % 4
        if ink == gnd:
            ink = (ink + 1) % 4
        if r.random() < drop:
            dropped += 1
            continue
        plates[ink].append(f'<polygon points="{pts}"/>')
    offs, layers = [], []
    for pi, polys in enumerate(plates):
        rr = rng(pid, seed, "plate", k, pi)
        ox = (rr.random() * 2 - 1) * MAX_PLATE * loss * drift
        oy = (rr.random() * 2 - 1) * MAX_PLATE * loss * drift
        offs.append(math.hypot(ox, oy))
        layers.append(f'<g fill="{PLATES[pi]}" stroke="{PLATES[pi]}" stroke-width=".35" stroke-linejoin="round" transform="translate({ox:.2f} {oy:.2f})">{"".join(polys)}</g>')
    ns = int(round(MAX_SPECKS * loss * (0.25 + 0.75 * drift)))
    rs = rng(pid, seed, "grain", k)
    specks = "".join(
        f'<circle cx="{rs.random()*100:.1f}" cy="{HORIZON-24+rs.random()*48:.1f}" r="{0.5+rs.random()*1.1:.2f}"/>'
        for _ in range(ns))
    gaps = "".join(f'<rect x="{rs.random()*90:.1f}" y="{HORIZON-1}" width="{3+rs.random()*8:.1f}" height="4" fill="var(--bg)"/>'
                   for _ in range(int(round(10 * loss * drift))))
    tf = ' transform="translate(100 0) scale(-1 1)"' if mirror else ""
    return (
        f'<g data-k="{k}" data-reg="{sum(offs)/len(offs):.3f}" data-specks="{ns + dropped}"{tf}>'
        f'<rect width="100" height="100" fill="{PLATES[gnd] if gnd is not None else "var(--bg)"}"/>'
        f'<rect y="{HORIZON}" width="100" height="2.4" fill="{"var(--bg)" if gnd is not None else "var(--gold)"}"/>{gaps.replace("var(--bg)", PLATES[gnd]) if gnd is not None else gaps}'
        f'<g style="mix-blend-mode:{"normal" if gnd is not None else "screen"}">{"".join(layers)}</g>'
        f'<g fill="{"var(--bg)" if gnd is not None else "var(--dimmed)"}">{specks}</g></g>'
    )


def svg(row, f, seed):
    pid = row["id"]
    a = ASPECTS.index(row["aspect"])
    v = VERBS.index(row["verb"])
    cols = 3
    n = cols * cols
    gap = 14
    W = cols * CELL + (cols - 1) * gap
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {W+150}" role="img" '
           f'aria-label="Silkscreen print of the proverb: {row["text"]}" data-id="{pid}" '
           f'data-fidelity="{f}" data-seed="{seed}">',
           f'<rect width="{W}" height="{W+150}" fill="var(--bg)"/>']
    for k in range(n):
        x = (k % cols) * (CELL + gap)
        y = (k // cols) * (CELL + gap)
        out.append(f'<svg x="{x}" y="{y}" width="{CELL}" height="{CELL}" viewBox="0 0 100 100">'
                   + panel(pid, seed, f, k, n, a, v) + "</svg>")
    # Mobius strip: one row of 6 panels, the closing panel is mirrored with swapped inks
    m = 6
    sy = W + 18
    sw = (W - (m - 1) * 6) / m
    out.append(f'<g data-strip="mobius">')
    for k in range(m):
        x = k * (sw + 6)
        twist = k == m - 1
        out.append(f'<svg x="{x:.1f}" y="{sy}" width="{sw:.1f}" height="{sw:.1f}" viewBox="0 0 100 100" data-twist="{int(twist)}">'
                   + panel(pid, seed, f, k + n, n + m, a, v, swap=twist, mirror=twist) + "</svg>")
    out.append("</g>")
    words = row["text"].rstrip(".").split()
    h = (len(words) + 1) // 2
    out.append(f'<text x="0" y="{W+sw+54:.0f}" fill="var(--text)" font-family="var(--ds-font-display)" font-size="15">'
               f'{" ".join(words[:h])}</text>')
    out.append(f'<text x="{W}" y="{W+sw+78:.0f}" text-anchor="end" fill="var(--text)" '
               f'font-family="var(--ds-font-display)" font-size="15">{" ".join(words[h:])}.</text>')
    out.append(f'<text x="0" y="{W+sw+106:.0f}" fill="var(--dimmed)" font-family="var(--ds-font-mono)" font-size="12">'
               f'{pid}  {row["aspect"]}.{row["verb"].upper()}</text>')
    out.append(f'<text x="0" y="{W+sw+126:.0f}" fill="var(--dimmed)" font-family="var(--ds-font-mono)" font-size="12">'
               f'f={f}  seed={seed}  {row["canon_ref"].split("#")[-1]}</text>')
    out.append("</svg>")
    return "\n".join(out)


def html(row, f, seed):
    tok = (ROOT / "src/ui-kit/recoil-report/_tokens.css").read_text()
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Tao Print Prototype</title>
<style>
{tok}
:root {{ color-scheme: dark; --lane: 720px; --gutter: 16px; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: var(--bg); color: var(--text); font-family: var(--ds-font-sans); font-size: var(--fs-body); line-height: 1.6; padding: 32px var(--gutter) 72px; }}
.lane {{ max-width: var(--lane); margin-inline: auto; }}
.eyebrow {{ font-family: var(--ds-font-mono); font-size: var(--fs-label); letter-spacing: .14em; text-transform: uppercase; color: var(--cyan); margin: 0 0 12px; }}
h1 {{ font-family: var(--ds-font-display); font-weight: 600; font-size: var(--fs-display); line-height: 1.05; margin: 0 0 16px; text-wrap: balance; }}
.lede {{ color: var(--dimmed); max-width: none; margin: 0 0 24px; }}
svg {{ display: block; width: 100%; height: auto; }}
.note {{ color: var(--dimmed); font-size: var(--fs-body); font-family: var(--ds-font-mono); margin: 20px 0 0; }}
</style>
</head>
<body>
<main class="lane">
<p class="eyebrow">Tao print prototype</p>
<h1>One mold, repeated until the ink gives out</h1>
<p class="lede">The ARCS Möbius, pulled nine times in four flat inks. The two faces of the strip print in different inks, so you can see it has one surface. Plates slip, ink drops out and the horizon breaks up in proportion to (1 minus fidelity). Fidelity is declared in the recipe, not measured. The last panel of the strip turns over with its inks swapped.</p>
{svg(row, f, seed)}
<p class="note">Reproducible from proverb id, recipe and seed. Not an edition: no scarcity, no registry.</p>
</main>
</body>
</html>
"""


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("id")
    ap.add_argument("--fidelity", type=float, default=0.9)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--out")
    ap.add_argument("--html", action="store_true")
    ns = ap.parse_args()
    s = (html if ns.html else svg)(load(ns.id), ns.fidelity, ns.seed)
    Path(ns.out).write_text(s) if ns.out else print(s)
