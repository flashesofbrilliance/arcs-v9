#!/usr/bin/env python3
"""
I.D.E.A. Monte Carlo — Instantiate · Disrupt · Evaluate · Anneal
Sufficiently Distributed Library of Alexandria simulation.

Coinage note: I.D.E.A. is defined HERE (first deliberate internal ARCS coinage,
per Quiet Signal QS3). All hazard rates are PRIORS (labeled assumptions), not data.

Model:
  A "library" = set of copies. Each copy: (navigator, platform_class, healthy, corrupted).
  Custody physics:
    STRUCTURE = integrity lattice (checksums/provenance/git): corruption is DETECTABLE,
                repair possible from any healthy copy.
    FLOW      = sync/replication current: destroyed/corrupted copies re-seed each year
                from a healthy copy (if structure permits detection).
    SUPERIONIC = structure + flow. Structure-only goes un-repaired; flow-only spreads rot.
  Disruption events (annual hazards — PRIORS):
    device failure          0.05 /device/yr
    navigator event         0.01 /navigator/yr  (death/abandonment/house-fire — kills ALL
                            that navigator's copies incl. their accounts: key-man fire)
    platform-class event    github 0.01 · db 0.02 · artifact-host 0.05 · paper 0.005 /yr
    silent corruption       0.01 /copy/yr (bit-rot, format death, undetected edit)
    global digital event    0.0005 /yr — all ONLINE copies destroyed; each device copy
                            survives w/ 0.5; paper survives w/ 0.95. Re-seed next year.

Reference run (12,000 trials, seed 42, 2026-07-11 — ±0.5% MC err):
  TODAY'S CENSUS: corpus(git,1 nav) 10.3%@10y / 68.0%@100y · artifacts 9.6%/63.9%
                  user receipts (db-only) 26.2%/95.3% · ~/.claude memory 51.2%/99.9%
  SWEEP: k=1+paper 1.58% · k=2,3cls+paper 0.10% · k=4+paper 0.02% · k=8,3cls+paper ~0.00%
  PHASE (k=4+paper): SUPERIONIC 0.03% · structure-only 63.0% · flow-only 96.8% · gas 63.0%
  CONCENTRATION: 12 copies/1 nav 63.2% vs 12 navs/1 copy each ~0.00%
  → Distribution beats replication; paper anchors beat extra clouds; custody must be
    superionic (structure AND flow). "Sufficiently distributed" ≈ ≥2–4 uncorrelated
    navigators × ≥3 platform classes + one offline anchor, synced, checksummed.
"""
import random

HAZ_PLATFORM = {"github": .01, "db": .02, "arthost": .05, "paper": .005, "device": None}
HAZ_DEVICE, HAZ_NAV, HAZ_ROT, HAZ_GLOBAL = .05, .01, .01, .0005

def simulate(copies, structure, flow, years, trials, seed):
    """copies: list of (navigator_id, platform_class). Returns P(total loss)."""
    rng = random.Random(seed)
    losses = 0
    navs = sorted({c[0] for c in copies if c[0] is not None})
    for _ in range(trials):
        alive = [True] * len(copies)      # copy exists
        clean = [True] * len(copies)      # copy uncorrupted
        lost = False
        for _y in range(years):
            # DISRUPT
            plat_hit = {p: rng.random() < h for p, h in HAZ_PLATFORM.items() if h}
            nav_hit = {n: rng.random() < HAZ_NAV for n in navs}
            glob = rng.random() < HAZ_GLOBAL
            for i, (nav, plat) in enumerate(copies):
                if not alive[i]:
                    continue
                if plat != "device" and plat_hit.get(plat):
                    alive[i] = False
                if plat == "device" and rng.random() < HAZ_DEVICE:
                    alive[i] = False
                if nav is not None and nav_hit[nav]:
                    alive[i] = False       # key-man fire: their devices AND accounts
                if glob:
                    if plat == "device":
                        alive[i] = alive[i] and rng.random() < .5
                    elif plat == "paper":
                        alive[i] = alive[i] and rng.random() < .95
                    else:
                        alive[i] = False
                if alive[i] and rng.random() < HAZ_ROT:
                    clean[i] = False
            healthy = [i for i in range(len(copies)) if alive[i] and clean[i]]
            # EVALUATE
            if not healthy:
                lost = True
                break
            # ANNEAL (the repair current)
            if flow:
                if structure:              # superionic: detect + repair + re-seed
                    for i in range(len(copies)):
                        alive[i] = True
                        clean[i] = True
                else:                      # flow-only: sync spreads rot from a random source
                    src = rng.choice([i for i in range(len(copies)) if alive[i]])
                    if not clean[src]:
                        for i in range(len(copies)):
                            if alive[i] and rng.random() < .5:
                                clean[i] = False
            # structure-only / neither: no repair, no re-seed
        if lost or not any(a and c for a, c in zip(alive, clean)):
            losses += 1
    return losses / trials

def lib(n_navs, classes_per_nav, anchor_paper=False):
    """Each navigator holds a device copy + copies on (classes_per_nav-1) online classes."""
    online = ["github", "db", "arthost"]
    copies = []
    for n in range(n_navs):
        copies.append((n, "device"))
        for c in range(classes_per_nav - 1):
            copies.append((n, online[c % 3]))
    if anchor_paper:
        copies.append((None, "paper"))     # institutional paper anchor, navigator-independent
    return copies

def run():
    T10, T100, N = 10, 100, 12000
    print(f"trials={N} · seed=42 · horizons {T10}y/{T100}y · MC std-err ≈ ±{(0.25/N)**.5:.4f}\n")
    print("== TODAY'S CENSUS (from the fire-test) ==")
    census = [
        ("corpus (git: 1 navigator, device+github)", [(0,"device"),(0,"github")], True, True),
        ("artifacts (git+claude.ai twins)", [(0,"device"),(0,"github"),(0,"arthost")], True, True),
        ("user receipts (db only, no export)", [(None,"db")], True, False),
        ("memory shards (~/.claude, 1 device)", [(0,"device")], False, False),
    ]
    for name, copies, st, fl in census:
        p10 = simulate(copies, st, fl, T10, N, 42)
        p100 = simulate(copies, st, fl, T100, N, 43)
        print(f"  {name:<46} P(loss@10y)={p10:6.1%}   P(loss@100y)={p100:6.1%}")
    print("\n== SUPERIONIC SWEEP: k navigators × platform diversity (structure+flow) ==")
    for k in [1, 2, 3, 4, 8, 16]:
        for d, anchor in [(2, False), (3, False), (3, True)]:
            copies = lib(k, d, anchor)
            p100 = simulate(copies, True, True, T100, N, 100 + k * 10 + d)
            tag = f"k={k:<2} navigators · {d} classes each{' + paper anchor' if anchor else ''}"
            print(f"  {tag:<52} P(loss@100y)={p100:8.2%}   copies={len(copies)}")
    print("\n== PHASE TEST at k=4 · 3 classes + paper (the diamond config) ==")
    diamond = lib(4, 3, True)
    for label, st, fl in [("SUPERIONIC (structure+flow)", True, True),
                          ("structure-only (no sync — solid)", True, False),
                          ("flow-only (no integrity — liquid)", False, True),
                          ("neither (gas)", False, False)]:
        p100 = simulate(diamond, st, fl, T100, N, 777)
        print(f"  {label:<38} P(loss@100y)={p100:8.2%}")
    print("\n== CONCENTRATION TEST: 12 copies, 1 navigator vs 12 copies, 12 navigators ==")
    one = [(0, "device")] * 4 + [(0, "github")] * 4 + [(0, "db")] * 4
    many = lib(12, 1)
    print(f"  1 navigator, 12 copies, 3 classes   P(loss@100y)={simulate(one, True, True, T100, N, 900):7.2%}")
    print(f"  12 navigators, 1 device copy each   P(loss@100y)={simulate(many, True, True, T100, N, 901):7.2%}")

if __name__ == "__main__":
    run()
