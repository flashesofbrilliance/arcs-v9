# ARCS

> Navigate to clarity. Survive the pressure. Find the flow.

**ARCS is decision intelligence.** A question goes in. A bearing comes out: the sharpened question, who else is in the terrain, the window it lives in, and an honest read on conviction — recorded as a receipt you can replay later.

The system never decides for you. It renders the terrain.

**Live:** [arcs.care](https://arcs.care) · [app.arcs.care](https://app.arcs.care)

## How it works

```
question + prep context
  → L0–L5 pipeline (Claude)   signal → coherence → survivability → cascade → cross-domain → global
  → DEWY decomposition         D: the real question · E: who's in the terrain · W: the window · Y: conviction
  → Y-gate                     GREEN / YELLOW / FORK / SCRATCH / DELTA / PARADOX / RED
  → Receipt                    a position on the manifold, frozen in time, replayable
```

Every session is recorded. The Observatory replays any decision as a kinematic trajectory — watch conviction peak and collapse, see where a YELLOW was overridden.

## Run it

The Python layer is a working instrument — stdlib only, zero dependencies.

```bash
python3 scripts/arcs_cli.py run --inputs *.json --out dewy_receipt.md    # full 5-verb pipeline
python3 scripts/arcs_cli.py analyze --inputs network.json | python3 scripts/arcs_cli.py synthesize --md
python3 scripts/score_me.py "Contact Name"                               # single-contact forensic receipt
```

analyze → assess → evaluate → synthesize → recapitulate. Each verb decomposes, composes, and pipes.

## Stack

Next.js 16 · Prisma 7 (SQLite dev / Postgres prod) · Auth.js v5 magic link · Anthropic SDK. Inline styles only — the UI renders at earned fidelity: coarse grain in fog, sharp at the ridge.

## Repo topology

| Path | What lives there |
|---|---|
| `src/app/` | Compass, briefs, Observatory — the navigable world |
| `src/lib/ygate.ts` | Y-gate: 12D manifold → polarity × conviction × stability |
| `operators/` | 34-file Python operator library (LAB · BAR · SAGE · KAIROS …) — L0–L5 as atomic components |
| `_CANON/` | The world documents. Read `WORLD.md` first — it is not documentation, it is the physics |
| `_DECISIONS/` | ADRs — every architectural decision has a receipt |
| `runtime/specs/` | DEWY receipt schema, Time ROM, machine-readable specs |
