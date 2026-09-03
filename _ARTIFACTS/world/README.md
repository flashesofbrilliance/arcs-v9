# ARCS World — the 720° Möbius surface

One navigable surface, two faces. Eight rooms × two faces = sixteen stops of 45°; one turn (360°) puts
you on the other face of the same room, two turns (720°) bring you home. That is how a Möbius strip
works, and ADR-071 already made the ARCS mark a Möbius.

| Room | Public face | Private face |
|---|---|---|
| The Threshold | taglines · what is federated · load-bearing chemistry (lattice diamonds) · invariants | survey numbers · great moments |
| The Compass | L0–L5 · Y states · trust §7 | the DEWY receipts |
| The Grove | ADR titles + status, by month | sharp questions · witness stubs |
| The Ziggurat | the knowledge lattice (radial: stratum × domain; gold arcs = cross-domain echoes) | memory ziggurat stats + hubs · recoil ledgers |
| The Trenches | NFTT story envelopes with arcs | war rooms · recoil |
| The Covenant | trust contract · privacy · terms | the ADRs that enforce it |
| The Field Guide | flora/fauna plates | ore + grades |
| The Spine | the apex spine (Möbius induction circuit) | what was witnessed and receipted that night |

**Doors** between rooms exist only where a lattice edge crosses domains (an orthogonal echo). The **time
rail** fogs anything dated after the chosen "now" (earned fidelity in time). A proverb is drawn per room
by its DEWY aspect (pollen).

## Build

```
python3 scripts/world_build.py --tier both      # → world.{public,private}.json + arcs-world.{public,private}.html
```

`world.template.html` carries the slot `/*__WORLD__*/{}` and the token `__TIER__`. The public build
strips every private-face key (DEWY, witness, moments, memory catalog, recoil, war rooms, survey, ADR
sharp questions) and renders a gated notice in its place. Harvest only, never infer: every room is fed
from files that already exist (see the docstring in `scripts/world_build.py`).

Keys: ← → turn · F flip 360° · 1–8 jump to a room · click a strip stop.
