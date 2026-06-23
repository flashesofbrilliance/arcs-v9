# ARCS Canon — Reference

> **What this is:** Compact reference for the ARCS v8.5/v9 Canon.
> Covers DEWY vector, Y-gate states, L0–L5 pipeline, ROM primitives,
> Triune logic, and Kairos Lock. Surface-agnostic — valid in Perplexity,
> Claude Code, and any other Claude surface.
>
> **Authority:** `WORLD.md` governs runtime physics. `orient-prd.md` governs
> the Orient surface implementation. This file is a read-only reference —
> do not derive implementation decisions from it without checking those sources.

---

## DEWY State Vector

Every session and receipt is anchored to a four-field position on the decision manifold:

| Field | Name | What it captures |
|---|---|---|
| **D** | Decision | The sharpened question — what is actually being decided |
| **E** | Entity | Who or what else is in the terrain (person, org, market, relationship) |
| **W** | Window | Time horizon: today / this week / this quarter / 1–3 years |
| **Y** | Y-gate | Conviction gradient — how solid is the current position |

The DEWY vector is a coordinate, not a form. It positions the operator on the decision manifold and determines which navigation mode applies.

---

## Y-Gate States

Canonical polarity enum: `SCRATCH | YELLOW | PARADOX | FORK | DELTA | GREEN | LOCKED`  
Conviction: `LOW | MEDIUM | HIGH` — Stability: `SHIFTING | CONTESTED | STABLE`

| Polarity | Meaning | Navigate |
|---|---|---|
| `SCRATCH` | No coherent position yet | Orient only — do not commit |
| `YELLOW` | Contested — real uncertainty, conviction active | Y gate active — careful movement |
| `PARADOX` | Options non-separable | Court auto-invoked; receipt deferred until resolved |
| `FORK` | Two live paths with significant separation | Skintrack choice — some options disappear after |
| `DELTA` | Conviction collapsed — inflection point tracked | Watch for phase change |
| `GREEN` | High conviction — clear directional signal | Move confidently — lock what you've earned |
| `LOCKED` | Post-Court resolved — Kairos Lock active | Superionic — structure + flow fused |

Authority: `runtime/specs/dewy-receipt-schema-v1.json` — `dewy_vector.Y.polarity`

---

## L0–L5 Pipeline

Every Orient session runs input through six sequential stages:

| Stage | Name | What happens |
|---|---|---|
| **L0** | Raw input | Receive the question exactly as given |
| **L1** | Parse & validate | HOLD/REJECT gate — resolve aliases, apply defaults, Kintsugi scan |
| **L2** | Decompose | Extract D, E, W from the input; infer Y-gate opening state |
| **L3** | Bayesian update | Apply prior receipts, domain context, and Strand A/B scoring |
| **L4** | Triune classify | Assign NULL / OM / UNDEFINED to each dimension |
| **L5** | Receipt emit | Produce the frozen DEWY coordinate + Y-gate state + BAR fields |

No stage may be skipped. L1 is the gate — a REJECT at L1 stops the pipeline entirely.

---

## ROM Primitives (never violate)

| # | Name | Rule |
|---|---|---|
| 1 | **NOTOMATION** | Tools may only externalize/scaffold/sequence human cognition. Never compress or overrule revealed preference. |
| 2 | **HYPERSPHERE CONTEXT MANIFOLD** | Every input is positioned across five axes: What / Who / Where-When / Why / Flow-State |
| 3 | **HYPERSTITION PIPELINE** | Ethereal → Loki Test → Receipt Evaluation → ROM. Ideas earn structure — they don't start with it. |
| 4 | **GOLDEN INCHWORM** | Red Thread → Golden Thread → Needle. Three-pass, non-blocking. Every abstraction earned by a concrete example first. |
| 5 | **ORTHOGONAL ECHO DETECTOR** | Surface cross-domain kinematic isomorphisms. When two domains move the same way, name the pattern. |
| 6 | **KINTSUGI IMMUNE SYSTEM** | Repair seams visibly. No silent patching of integrity failures. Show the break and the gold. |
| 7 | **WRITE-LOCK** | One-way gate decisions require explicit write-lock declaration before commit. Irreversibility is declared, not assumed. |

---

## Triune Logic

Three truth states replace binary true/false:

| State | Meaning | When to use |
|---|---|---|
| `NULL` | Explicitly absent — known unknown | Field was checked; nothing is there |
| `OM` | Present and resolved — known known | Field has a confident, stable value |
| `UNDEFINED` | Not yet evaluated — unknown unknown | Field hasn't been reached in the pipeline yet |

Do not collapse UNDEFINED to NULL. They are different failure modes.
NULL means "I looked and found nothing." UNDEFINED means "I haven't looked yet."

---

## Kairos Lock

A Kairos Lock is a write-lock on a spec or artifact that has reached ROM status within its surface.

**Conditions for Kairos Lock:**
- The artifact has a confirmed, working canonical form
- It is being referenced as an authority by downstream artifacts
- Breaking changes would require a version bump and PR

**What Kairos Lock means in practice:**
- The file may not be edited in place without a version bump
- New behavior is added by appending or creating a new versioned file
- Any session that modifies a Kairos Locked file must log the change in MEMORY.md

**Currently Kairos Locked:**
- `arcs-field-os/specs/orient-prd.md` v0.1.0 (as of 2026-05-26)

---

## BAR / KKL / LAB Macros

Three always-on analysis lenses applied at L3–L4:

| Macro | Stands for | What it surfaces |
|---|---|---|
| **BAR** | Bayesian / Adversarial / Ruin | Risk-weighted view — what kills this decision (risk tier enum: Baseline / Asymmetric / Ruin; macro lens: Bayesian / Adversarial / Ruin) |
| **KKL** | Known-Known / Known-Unknown / Loki | Epistemic map — what do we actually know vs. assume |
| **LAB** | Loki / Advisor / Bayes | Three-voice cross-check — adversarial, advisory, probabilistic |

> **Disambiguation (2026-06-23):** `ADR-020-tribune-intelligence-layer.md`'s timing-signal triad
> uses `KLC` (Kairos / Lock / Chronos) — distinct from this `KKL`. Do not conflate.

---

## Clarity Modes

| Mode | When | Output |
|---|---|---|
| `SIMPLE` | Default | 1 True North + ≤3 why bullets |
| `RICH` | On request or medium stakes | Simple + 1 visual or extended explanation |
| `DEEP` | On explicit request or high stakes only | Full pipeline shown, all macros surfaced |

Default is always SIMPLE. DEEP is never assumed.
