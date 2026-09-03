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

**Doors** between rooms exist only where a lattice edge crosses domains (an orthogonal echo). A proverb is
drawn per room by its DEWY aspect (pollen).

**Chronos (the turntable).** The bottom of the page is a record player. The platter is the Möbius
ribbon: drag it to scrub time (it coasts when you let go), press play to spin it (90 s per revolution at
1.0×; ▶▶/◀◀ double the speed, `[` `]` on the keyboard, space to play/pause). The groove is every dated
receipt, decision, witness stub and epoch, etched as ticks. The tone arm is the row of rooms; the record
has two sides, A public and B private (F flips). Nothing exists before its date: scrub back and later
things are not drawn at all. What exists renders at a fidelity f = 0.35·maturity + 0.65·soundness, where maturity is
1 − e^(−age/21 days) and soundness comes from the evidence state (LOCKED/GREEN 1 · DECIDED .85 · YELLOW
.55 · DRAFT/candidate .4 · SCRATCH/PARADOX .3). f drives blur, opacity, weight and tracking together;
only nascent things (f < .5) wobble, never under reduced motion. Blur is distance from irrefutable.

**The explorer (Ziggurat).** Canvas. Altitude is the zoom (quantum core → meta; the private face draws
the memory ring beyond LIBRARY, 217 nodes / 595 declared edges). Vantage is the rotation; the front cone
is 140°. Fidelity is earned by distance from the focus stratum and by soundness (status). The sentinel
lists threat vectors oblique to the vantage (gated, shore, single-domain, dangling) with their bearing;
auto-look swings the camera to face the heaviest one you cannot see. It moves the view, never the
decision. Nodes drill atom → molecule → organism; interrupt returns to the atom.

## Build

```
python3 scripts/world_build.py --tier both      # → world.{public,private}.json + arcs-world.{public,private}.html
```

`world.template.html` carries the slot `/*__WORLD__*/{}` and the token `__TIER__`. The public build
strips every private-face key (DEWY, witness, moments, memory catalog, recoil, war rooms, survey, ADR
sharp questions) and renders a gated notice in its place. Harvest only, never infer: every room is fed
from files that already exist (see the docstring in `scripts/world_build.py`).

Keys: ← → room · F flip side · 1–8 jump to a room · space play/pause · [ ] speed.
