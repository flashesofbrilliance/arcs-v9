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


def mold(a, v):
    """Twisted-ring mold: a lemniscate whose lobe pinch comes from the aspect, stroke count from the verb."""
    pinch = 0.55 + 0.1 * a
    strokes = v + 1
    out = []
    for s in range(strokes):
        r = 1.0 - 0.13 * s
        pts = []
        for i in range(61):
            t = 2 * math.pi * i / 60
            d = 1 + pinch * math.sin(t) ** 2
            x = 50 + 44 * r * math.cos(t) / d
            y = 50 + 44 * r * math.sin(t) * math.cos(t) / d * 1.9
            pts.append(f"{x:.2f},{y:.2f}")
        out.append("M" + " L".join(pts) + "Z")
    return out


def panel(pid, seed, f, k, n, a, v, swap=False, mirror=False):
    """One repeat. k = repeat index (0 = first pull), n = total repeats."""
    drift = k / max(1, n - 1)
    loss = 1.0 - f
    paths = mold(a, v)
    order = [(a + i) % 4 for i in range(3)]          # three inks per print, rotated by aspect
    layers = []
    offs = []
    for li, ink in enumerate(order):
        r = rng(pid, seed, "reg", k, li)
        ox = (r.random() * 2 - 1) * MAX_OFFSET * loss * drift
        oy = (r.random() * 2 - 1) * MAX_OFFSET * loss * drift
        offs.append(math.hypot(ox, oy))
        op = 1.0 - 0.5 * loss * drift
        col = INKS[SWAP[ink] if swap else ink]
        d = " ".join(paths[: max(1, min(len(paths), li + 1 + (len(paths) > 2)))])
        layers.append(
            f'<path d="{d}" transform="translate({ox:.2f} {oy:.2f})" fill="none" stroke="{col}" '
            f'stroke-width="{7 - 2 * li}" stroke-linejoin="round" opacity="{op:.3f}"/>'
        )
    ns = int(round(MAX_SPECKS * loss * (0.25 + 0.75 * drift)))
    r = rng(pid, seed, "grain", k)
    specks = "".join(
        f'<circle cx="{r.random()*100:.1f}" cy="{r.random()*100:.1f}" r="{0.5+r.random()*1.2:.2f}"/>'
        for _ in range(ns)
    )
    tf = f' transform="translate(100 0) scale(-1 1)"' if mirror else ""
    return (
        f'<g data-k="{k}" data-reg="{sum(offs)/len(offs):.3f}" data-specks="{ns}"{tf}>'
        + "".join(layers)
        + f'<g fill="var(--dimmed)">{specks}</g></g>'
    )


def svg(row, f, seed):
    pid = row["id"]
    a = ASPECTS.index(row["aspect"])
    v = VERBS.index(row["verb"])
    cols = 3
    n = cols * cols
    gap = 14
    W = cols * CELL + (cols - 1) * gap
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {W+136}" role="img" '
           f'aria-label="Silkscreen print of the proverb: {row["text"]}" data-id="{pid}" '
           f'data-fidelity="{f}" data-seed="{seed}">',
           f'<rect width="{W}" height="{W+136}" fill="var(--bg)"/>']
    for k in range(n):
        x = (k % cols) * (CELL + gap)
        y = (k // cols) * (CELL + gap)
        out.append(f'<g transform="translate({x} {y}) scale({CELL/100})">'
                   + panel(pid, seed, f, k, n, a, v) + "</g>")
    # Mobius strip: one row of 6 panels, the closing panel is mirrored with swapped inks
    m = 6
    sy = W + 18
    sw = (W - (m - 1) * 6) / m
    out.append(f'<g data-strip="mobius">')
    for k in range(m):
        x = k * (sw + 6)
        twist = k == m - 1
        out.append(f'<g transform="translate({x:.1f} {sy}) scale({sw/100:.3f})" data-twist="{int(twist)}">'
                   + panel(pid, seed, f, k + n, n + m, a, v, swap=twist, mirror=twist) + "</g>")
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
<p class="lede">Nine pulls of one mold, then a six-panel strip whose last panel turns over with its inks swapped. Misregistration and grain scale with (1 minus fidelity). Fidelity is declared in the recipe, not measured.</p>
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
