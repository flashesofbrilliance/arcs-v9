# ADR-038 — Recoil Bookmark Primitive (lightweight moment-flag vs. full kinematic manifold)

> **Status:** RC — PROPOSED
> **Date:** 2026-07-31
> **Commit:** (set at merge)
> **Y:** YELLOW / MODERATE / SHIFTING
> **Relates to:** recoil-report skill, `runtime/recoil/generated/*.json`, `src/document/screens/RecoilReport.tsx`, the kinematic-manifold memory (ADR pending), the Observatory replay backlog

## D — The Decision

**Sharp question:** A recoil report needs a way to flag *which parts of a call are worth revisiting* — where
something resonated (a kairos peak) and where the counterpart pulled back (a park). The first instinct is a
**full kinematic manifold**: a per-segment resonance curve across the whole call (added to the Justin/Delaney
report as a proof of concept). That is expressive, but it is also *invasive*: it asks the analyst to score
every segment on a continuous 0–100 gradient, implies a rigor (a measured manifold) the input rarely supports,
and couples the report schema to a charting component. Is there a **less-invasive primitive** that captures the
same "go look here again" value without the overhead or the false precision?

**Decision (proposed):** Add a first-class **bookmark** primitive — a small, optional, additive list of flagged
moments — as the default way to mark call regions worth revisiting. Keep the full kinematic manifold as an
*opt-in* richer view derived from bookmarks, not the baseline.

A bookmark is deliberately minimal:

```jsonc
"bookmarks": [
  {
    "at": "34–42 min",           // where in the call (segment label or timestamp)
    "kind": "peak",              // peak | park | probe   (probe = worth investigating, unresolved)
    "label": "Live receipt co-build",
    "why": "Co-built his own vendor tripwire with real numbers — re-enter here.",
    "quote": "by October, if not generating incrementality of $120K/month, we put in end-of-year notice"
  }
]
```

Three kinds, no continuous score:
- **peak** — resonance spiked; the place to re-open the conversation.
- **park** — they pulled back / gated; the constraint to respect (do not push here).
- **probe** — an unresolved thread worth investigating or exploring further (the "flag a portion to explore"
  case from the ask that neither peak nor park quite covers).

The manifold, when wanted, is *rendered from* bookmarks (plot the peaks/parks on a lightweight sparkline), so
there is one source of truth and the expensive view is derived, not authored.

**Rejected alternative — manifold as baseline:** make every report carry a full per-segment resonance curve.
Rejected because it forces continuous scoring on qualitative input (false precision — an NCI/earned-fidelity
violation), inflates authoring cost on every call, and hard-couples the schema to a chart. The manifold is a
*fidelity ceiling we rarely earn*; bookmarks are honest at the fidelity we actually have.

## E — Entity / System

- **`runtime/recoil/generated/<id>.json`** gains an optional top-level `bookmarks: Bookmark[]`. Additive and
  optional: existing reports and the current renderer are unaffected if the key is absent.
- **`RecoilReport.tsx` / `RecoilReportFromData`** gains a `normalizeBookmarks()` that renders a compact
  "Bookmarks · where to re-enter" strip (kind-colored chips: peak=gold, park=vermilion, probe=cyan) above the
  call-walk, and threads the same flags onto the timeline dots it already draws.
- **`callWalk[].peak`** (already in the schema) is the degenerate case of a bookmark; bookmarks generalize it
  to park + probe and carry the *why* + *quote*. Migration: a `peak:true` segment maps to a `kind:"peak"`
  bookmark; no data rewrite required.
- **Kinematic manifold** becomes a derived, opt-in view (`kinematics` stays supported for reports that genuinely
  measured a gradient, e.g. via `arcs_kinematics.py`, but is never required).

## W — Window

Now, while the recoil skill is actively used (Justin/Delaney report shipped today). Small, additive, reversible —
the right size for an RC: ship the schema + renderer, use it on the next 2–3 reports, promote to DECIDED if it
earns its keep, or drop the key with zero migration if it does not.

## Y — Gate: YELLOW / MODERATE / SHIFTING

- **Polarity YELLOW:** clearly useful, but the exact taxonomy (peak/park/probe) and whether the manifold should
  ever be baseline are still contested — hence RC, not DECIDED.
- **Conviction MODERATE:** the primitive is obviously less invasive than the manifold; the open question is only
  where the ceiling sits.
- **Stability SHIFTING:** expect the `kind` set and the render to move after real use.

**Falsifier (how this RC gets killed):** if, across the next 3 reports, analysts consistently reach past
bookmarks for the full manifold (i.e. the continuous curve carries information the three kinds cannot), the
"bookmarks as baseline" decision is wrong and the manifold should be promoted instead. Score-back: after 3
reports.

## Notes

- **Provenance for this ADR:** surfaced live building the Justin/Delaney recoil — the full manifold was added as
  a proof of concept, and the question "is there a less invasive way to flag a portion worth revisiting" is the
  seed. The bookmark is the honest-fidelity answer.
- No em-dashes in the shipped schema strings (deliverable rule); this ADR is an internal decision doc.
