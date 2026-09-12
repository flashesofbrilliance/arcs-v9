# Sketch — the ARCS activation service (vox animus) ↔ `kairos` (public-good #2)

**Status:** SKETCH (not canon, not a decision) · 2026-08-13
**Grounded by:** ADR-053 (boundary) · ADR-054 (pricing) · [[seed-bank-germination-conditions]]

> A sketch, deliberately. It maps the seam between the open Kairos socket and the private ARCS
> current so neither is designed into a corner. Promote to an ADR only when the activation
> service is real enough to have real interfaces.

## The two organs

**`kairos` (public-good #2, open) — "conditional cron, not cron-driven."**
Cron fires on the *clock*. Kairos fires on *conditions*: a seed's `germination.triggers` /
`soil` matching the current context. It is the open **socket** — the generic "when *could* this
fire?" evaluator. It knows nothing private; it runs on any germinate install.

**ARCS activation service (private) — the vox animus / the current.**
Given that Kairos found a condition matched, ARCS answers the harder question the open socket
deliberately cannot: **"should it fire — now, for *you*?"** That is *ripeness judgment*, primed
by the private rosetta (accumulated priors). It is the spark that runs a meter (ADR-054).

## The seam (same boundary as germinate ↔ ARCS)

```
   context / soil
        │
        ▼
  ┌──────────────┐   condition matched     ┌─────────────────────────┐
  │   kairos      │ ──────────────────────▶ │  ARCS activation service │
  │  (open socket)│   "this COULD fire"     │  (private current)       │
  └──────────────┘                          │  ripeness judgment:      │
   generic trigger                          │  "should it, now, you?"  │
   match; no priors                         │  rosetta-primed          │
                                            └───────────┬─────────────┘
                                                        │ fire (metered gas)
                                                        ▼
                                              seed → kinetic (surfaced to
                                              the right human at Kairos)
```

**Crispness rule:** Kairos must run fully without ARCS priors. It surfaces *candidates* (could-fire).
ARCS is a pluggable ripeness layer on top — remove it and germinate still works (mechanical sprout,
free); add it and candidates get judged for ripeness (the ride, metered). The private priors never
leak down into the open socket.

## Meter alignment
The meter runs at exactly one place: the ARCS "should it fire, now, for you" call — the vox-animus
firing. Everything to the left of that call (Kairos condition matching, seed holding) is free by
construction. This is ADR-054's "bill per activation" made mechanical.

## Open questions (for the future ADR, not now)
- Interface shape between kairos and the ARCS ripeness layer (event stream? poll? callback?).
- Where "surface to the right human" lives — is notification part of ARCS or a third organ?
- Ripeness score representation (does it reuse the Y-gate / NCI vocabulary, or its own?).
