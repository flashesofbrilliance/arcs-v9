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


STRANDS = 18          # the instrument uses 44; fewer keeps a 15-panel print light
STEPS = 72
PHASE = 0.9           # instrument default rotation
HORIZON = 62          # horizon y in panel units (instrument: 0.62 of height)


def project(u, v, ph):
    """The ARCS Moebius strip, same parametrization as _ARTIFACTS/arcs-moire-mobius.html, in a 100-unit panel."""
    x = (1 + v * math.cos(u / 2)) * math.cos(u)
    y = (1 + v * math.cos(u / 2)) * math.sin(u)
    z = v * math.sin(u / 2)
    x1 = x * math.cos(ph) + z * math.sin(ph)
    z1 = -x * math.sin(ph) + z * math.cos(ph)
    t = -0.52
    y1 = y * math.cos(t) - z1 * math.sin(t)
    z2 = y * math.sin(t) + z1 * math.cos(t)
    sc = 3.4 / (3.4 + z2) * 30
    return 50 + x1 * sc, 46 + y1 * sc


def strand(vf, ph):
    v = (vf - 0.5) * 0.62
    pts = [project(2 * math.pi * i / STEPS, v, ph) for i in range(STEPS + 1)]
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)


def panel(pid, seed, f, k, n, a, v, swap=False, mirror=False):
    """One repeat of the mold. Fog = (1 - f), the instrument's own fog control; the gap between the two
    strand families (delta) widens across repeats in proportion to (1 - f), so interference is the misregistration."""
    drift = k / max(1, n - 1)
    loss = 1.0 - f
    delta = 0.022 + 0.16 * loss * drift
    c1, c2 = ("var(--gold)", "var(--cyan)") if swap else ("var(--cyan)", "var(--gold)")
    fam1 = "".join(f'<path d="{strand(i / (STRANDS - 1), PHASE)}"/>' for i in range(STRANDS))
    fam2 = "".join(f'<path d="{strand(i / (STRANDS - 1), PHASE + delta)}"/>' for i in range(STRANDS))
    fog = min(0.95, loss * (0.35 + 0.65 * drift) * 1.1)
    ns = int(round(MAX_SPECKS * loss * (0.25 + 0.75 * drift)))
    r = rng(pid, seed, "grain", k)
    specks = "".join(
        f'<circle cx="{r.random()*100:.1f}" cy="{HORIZON-20+r.random()*40:.1f}" r="{0.4+r.random()*0.9:.2f}"/>'
        for _ in range(ns))
    tf = ' transform="translate(100 0) scale(-1 1)"' if mirror else ""
    return (
        f'<g data-k="{k}" data-reg="{delta*100:.3f}" data-specks="{ns}"{tf}>'
        f'<rect width="100" height="100" fill="var(--bg)"/>'
        f'<rect y="{HORIZON}" width="100" height="1.1" fill="var(--gold)"/>'
        f'<g fill="none" stroke-width="0.55" style="mix-blend-mode:plus-lighter">'
        f'<g stroke="{c1}" opacity="{.5*(1-.6*fog):.3f}">{fam1}</g><g stroke="{c2}" opacity="{.32*(1-.6*fog):.3f}">{fam2}</g></g>'
        f'<rect y="{HORIZON-34}" width="100" height="68" fill="url(#fog)" opacity="{fog:.3f}"/>'
        f'<g fill="var(--dimmed)" opacity=".7">{specks}</g></g>'
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
           f'<defs><linearGradient id="fog" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#020408" stop-opacity="0"/>'
           f'<stop offset=".5" stop-color="#0d1117" stop-opacity="1"/><stop offset="1" stop-color="#020408" stop-opacity="0"/></linearGradient></defs>',
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
