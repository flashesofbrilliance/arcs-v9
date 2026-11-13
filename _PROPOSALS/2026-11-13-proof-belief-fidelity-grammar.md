---
version: 0.1.0
date: 2026-11-13
status: PROPOSED (judgment, ungated; nothing here is in DESIGN.md, the kit or a gate until Zach rules)
parent: _PROPOSALS/2026-11-13-design-world-rules.md
---

# Proof, belief and fidelity grammar, with loss, gain, pressure and the unseen atoms

Why: Zach asked (2026-11-13) for a visual grammar of proof and belief, a more opinionated earned fidelity and kinematic manifold, a mark when altitude, time signature or resolution drops, its converse, the pressure differential in the room (qi, ma, wu wei), where people lean in or back, and the non-obvious atoms of the family, seen and unseen.

What: a vocabulary of marks and part-level declarations. Each is labelled with its basis: **measured** (counted in the repo), **existing** (already in the kit or rules), or **judgment** (mine, untested).

Why now: the HUD is about to load several atlases into one field. Without a shared proof grammar, a joined view cannot say which edge is observed and which is asserted.

How to read: section 1 is what the sweep measured. Sections 2 to 8 are the grammar. Section 9 lists what to test before any of it ships. Rendered options sit on the option board.

## 1. Sweep of the surfaces (measured, heuristic)

Read-only grep over the 200 distinct HTML and TSX files behind the 291 routed rows in `runtime/specs/surface-catalog.json`. Signals are regexes, so counts are a floor on intent and carry false positives (the "claim" regex also matches the word "prior").

| Signal | Files | Reading |
|---|---|---|
| Names a fidelity state (grain, moire, SHARP, DEGRADED, data-fidelity) | 37 | 1 in 5 pages speaks the render scale at all |
| Prints a sample size (`n=`, "sample size") | 17 | The "earned" half of earned fidelity is rare |
| Cites a basis (source, provenance, as-of) | 79 | Roughly 4 in 10 |
| Shows a repair or struck claim (seam, kintsugi, superseded) | 36 | Seams are present but sparse |
| Names decay (STALE, stale, decay) | 23 | Freshness is mostly implicit |
| Zero signal of any kind | 50 | A quarter of pages assert without basis, state or decay |
| Zero proof signal, by host | app 30, good 15, prl 9 | app.arcs.care is the biggest gap |

Limits: this counts words, not behaviour. A page can say "grain" and never draw it. A page with no match may be pure navigation, where proof marks do not apply. The sweep is a map of where to look, not a verdict.

## 2. Proof marks (judgment)

Four states for any claim a part displays. They extend the existing `claim-check` and `kintsugi-seam` specimens rather than replacing them.

| Mark | Meaning | Draw |
|---|---|---|
| Observed | Read from a source with a stamp | Solid rule, source and date printed |
| Inferred | Derived from observed claims | Dashed rule, names the parents |
| Asserted | Stated, no source | Open outline, labelled "asserted" |
| Struck | Was claimed, then falsified | Gold seam through the text, never erased (kintsugi) |

Rule: an asserted claim may never be drawn with the weight of an observed one. A struck claim stays on the page.

## 3. Belief grammar (judgment)

A belief is a claim, a prior, and a dated trail of updates. Draw it as a value on a scrub. Each update is a tick that names the evidence that moved it. A tick with no named evidence is not drawn as an update. This reuses `_STATE/belief-log.md` as the source.

## 4. Earned fidelity, more opinionated (judgment)

Fidelity is a function of two things: evidence count and evidence age.
- Thin evidence: grain, with the sample size printed (`n=3`).
- Old evidence: a drift hatch over the value, with the age printed.
- Both thin and old: grain under hatch, and the part may not show a headline number.
- Empty: flat, per rule O3. Never a zero.

Opinion: fidelity may fall by choice. A part at high altitude draws coarse on purpose and says so. Detail that the evidence cannot support is never added to look finished.

## 5. Kinematic manifold (judgment)

A position is a point with a velocity. Two axes carry it:
- Altitude is how surveyed the ground is (the Ziggurat's height).
- Time signature is belief velocity: how fast priors are moving here.

A fast-moving belief at low altitude is the dangerous cell. The HUD should mark it, not average it away. The canonical altitude ladder is still open (see parent proposal, decision 4); this section waits on it.

## 6. Loss and gain marks (judgment)

**Loss notch.** Whenever a value is shown at lower resolution than its source (altitude dropped, time signature slowed, a translation between ladders), the part carries a small notch that prints what was lost ("daily to weekly", "5 tiers to 3"). If nothing was lost, no notch is drawn. A lint can check this: any part that rebins or rounds must emit the notch.

**Gain seam.** The converse. When evidence arrives and a prior moves, draw a gold seam at the point of change and print the delta and the evidence. It is the same visual family as the kintsugi seam, because a repair and a gain are both visible history.

Corollary: a belief that has not moved for a long time under changing conditions is suspect. Stillness is shown as age, not as stability.

## 7. Pressure differential, qi, ma, wu wei (judgment)

**Pressure** is the gap between the stakes of the next action and the evidence earned for it. Draw it as a gauge on the page, in the page's own header. Low gap: calm. High gap: the page slows, shows the one-way-door flag, and asks for the write-lock before commit.

- **Qi:** evidence flow into a claim. Stagnant qi is the drift hatch.
- **Ma:** the earned interval. A deliberate empty slot labelled as a place ("no evidence yet, expected from X by date"), not an error state.
- **Wu wei:** the page shows the safest clear next step and stops. No urgency, no confetti, no countdown that the real kairos does not support.

## 8. Unseen atoms (judgment)

Rules a part carries that no pixel shows. Each becomes a field in `src/ui-kit/kit-manifest.json`.

| Atom | Field | Why |
|---|---|---|
| Declared zero point | `frame` | A part cannot join another without a frame (HUD join rule) |
| Refusal list | `refuses` | The part states what it will not render, so it cannot be misused |
| Decay rate | `decays_in` | The part knows when its data is stale and draws it so |
| Travelling provenance stamp | `stamp` | A copied value keeps its basis, so the basis cannot be stripped |
| Reversibility flag | `door` (`two-way` or `one-way`) | A one-way action draws heavier and slower |
| Snap contract | `accepts`, `emits` | Parts compose only through a declared data shape |
| Neighbour effect | `reads_beside` | The same number reads differently beside a seam than beside an assertion; the part declares which neighbour changes it |

Field in the presence of the field: a part's meaning is partly set by what sits beside it. `reads_beside` makes that explicit so a composed page can be checked, not just assembled.

## Lean in and lean back (hypotheses, untested)

- Lean in: visible seams, a small specific number with its basis, an open interval, anything that reacts to the reader's own input.
- Lean back: certainty without a source, a full dashboard, a call to act on thin evidence, motion the reader did not cause.
- Cheap test: dwell time and scroll depth on seam elements against assertion elements, on one page, before building anything.

## 9. Before any of this ships

1. Zach rules on this spec (nothing is gated until then).
2. Pick the canonical altitude ladder (parent proposal, decision 4).
3. Render the three open options (gain seam, open interval, pressure gauge) as A/B/C and pick one each.
4. Smallest first gate, read-only: every part that rebins data must emit a loss notch; every struck claim must stay in the DOM.
5. Add `frame`, `refuses`, `decays_in`, `door` to the manifest as optional fields with a coverage ratchet (starts at 0 of 88, only goes up), the same shape as the job-coverage ratchet.
6. Re-run the sweep with a rendered check (headless) so counts reflect what is drawn, not what is written.
