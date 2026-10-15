# ADR-087 — Animation in single-file instruments: one timeline, time as a recipe parameter, the resting state is the truth

> **Status:** DRAFT
> **Date:** 2026-10-15
> **Commit:** (set at merge)
> **Numbering note:** Minted through `scripts/oracle.py next adr` (counter to 87, `_SEEDS/_oracle.json` committed with this file). Next-free was 87 after high-water 86.
> **Lineage:** The Raw Capture page (`_ARTIFACTS/raw-capture.html`, PRs 1323 and 1326), a witnessed idea from this session (the stub is kept locally and is not committed), and the architecture skill's ADR shape (engineering plugin). Builds on the page's own claim: a render is a development of a stored capture, never a baked output.

---

## D — The Decision

**Sharp question:** How should animation be added to the Raw Capture page so that it stays deterministic, scrubbable, accessible, inside DESIGN.md, and inside the frame budget?

---

## E — Entity / System

- `_ARTIFACTS/raw-capture.html`, a single-file page with one live canvas instrument, a 271-cell contact sheet, and a gate panel (altitude 5).
- The Artifact page contract: no external scripts beyond a short allowlist, CSP-enforced, no downloads, 16 MB cap.
- Repo gates every page must pass: `page_gate.py`, `artifact_wrap_lint.py`, `token_source_gate.py`, and the kintsugi design-debt gate against DESIGN.md.
- Any later instrument page that wants motion. This is a pattern decision, not only a feature.

---

## W — Window

**Horizon:** WEEK
**Revisit trigger:** a second page adopts the timeline; the frame budget fails on a real mid-range device; DESIGN.md gains a motion section; a viewer reports motion discomfort.

---

## Context

The page already has two motions: a 1.5-second exposure sweep on load, written as ad hoc `requestAnimationFrame` code, and a rotate transition on the section toggle. The request is an animation feature built from the instrument. Constraints, each with where it comes from:

- **Repo rule:** no new dependencies without asking (AGENTS.md).
- **Page contract:** libraries only from a short CDN allowlist; a page must be complete at rest, so the first still frame carries everything meant to be read.
- **Accessibility:** `prefers-reduced-motion` must be honored; no flashing above three per second.
- **Tone:** WORLD.md asks for calm and precise. Motion is not celebration.
- **The page's own thesis:** a render is a development of a stored capture. An animation that bakes frames would contradict it.
- **Measured, 2026-10-15, headless run on an 8-core Mac:** one instrument frame costs a median 2.9 ms when developing from raw, and 18.1 ms (p90 19.8) in re-cut mode at 8 passes. The 60 fps budget is 16.7 ms, so the re-cut path misses it on this machine and will miss it by more on a phone.
- **Real data to animate:** 271 receipts in creation order, with one slope change at receipt 198 (the `atgTributaries` boundary).

Not verified: performance on a real phone or a throttled CPU. That is an action item before this ADR is DECIDED.

---

## Options Considered

### Option A: CSS keyframes and transitions per element
| Dimension | Assessment |
|---|---|
| Complexity | Low |
| Cost | No new code paths |
| Scalability | Poor past a few elements |
| Familiarity | High |

**Pros:** no JavaScript, compositor-friendly, reduced motion is one media query.
**Cons:** cannot drive canvas pixels or derived readouts; no scrub; the animated state is not inspectable; two sources of truth (CSS time and JS state).

### Option B: One timeline engine over a pure state function
| Dimension | Assessment |
|---|---|
| Complexity | Medium (about 60 lines for the engine) |
| Cost | In-file code, no dependency |
| Scalability | Good: tracks are data |
| Familiarity | Medium |

**What it is:** state = f(recipe, t) with t in [0, 1]. Tracks are pure functions of t that return partial state (exposure, pass count, receipt index, gates met). One `render(state)` serves both static and animated views. Play advances t by elapsed wall time; scrub sets t directly.
**Pros:** deterministic, scrubbable, pausable, testable, the same code path as the resting page, one place for reduced motion.
**Cons:** more code than CSS; the engine is ours to maintain.

### Option C: Pre-rendered frames or video as data URIs
| Dimension | Assessment |
|---|---|
| Complexity | Medium (a build step) |
| Cost | Size against the 16 MB cap |
| Scalability | Poor: every change re-renders |
| Familiarity | Medium |

**Pros:** smooth playback on any device.
**Cons:** baked output, the gem-cut anti-pattern the page argues against; not re-developable; no scrub into new parameters; size.

### Option D: An animation library from the CDN allowlist
| Dimension | Assessment |
|---|---|
| Complexity | Low to adopt |
| Cost | A dependency, which the repo asks about first |
| Scalability | Good |
| Familiarity | High |

**Pros:** mature easing and sequencing.
**Cons:** a new dependency for about three tracks; hides state behind the library; does not drive a canvas recipe without glue anyway.

### Option E: Leave the ad hoc sweep as is
**Pros:** no work. **Cons:** no feature; the existing sweep is untestable and cannot be scrubbed.

---

## Trade-off Analysis

The deciding question is whether time is a parameter or a medium. A, C and D treat time as a medium: the animation plays and the state is whatever it passed through. B treats time as one more parameter of the recipe, which is the same relationship the page claims between a receipt and its renders. That keeps the idea honest and makes the feature testable, because the resting state is `f(1)` and can be compared with the static page. The cost is owning about 60 lines of engine. C is ruled out on principle and size; D is ruled out by the dependency rule and because it still needs glue for the canvas; A cannot reach the canvas.

---

## Decision

**Chosen:** Option B.

**Rules this ADR sets:**

1. **Time is a recipe parameter.** State is `f(recipe, t)`. No track stores frames or mutates state outside `render(state)`.
2. **The rest invariant.** `f(1)` must equal the static default state. A check compares the readouts at t = 1 with the static render. A failing check blocks DECIDED.
3. **v1 tracks, three, data-declared:** *Develop* (an exposure and point sweep through the instrument), *Snap* (a time-lapse of the 271 receipts that pauses and flags the slope change at receipt 198), *Ignite* (the gate panel closing the spark gap in order). One track plays at a time.
4. **Shared transport:** Play and Pause buttons, a labeled scrubber, a step control. No autoplay except the existing opening sweep, which moves onto the same engine.
5. **Reduced motion.** With `prefers-reduced-motion: reduce`, nothing plays by itself and Play is replaced by stepping. The scrubber always works. Motion is never forced.
6. **Frame budget.** Advance by elapsed time, not by frame count, so speed stays right when frames drop. If the median frame cost exceeds 12 ms over 5 frames, cap at 30 fps; render full quality on pause. The re-cut path is the known offender.
7. **Pause when the tab is hidden.** Resume is manual.
8. **Accessibility.** Real `<button>` and `<input type="range">` elements with visible focus; live-region announcements only on pause and on end, never per frame; no flashing above three per second.
9. **Gates.** The page must still pass `page_gate`, wrap-lint, token-source and the design-debt gate. No library. Easing and durations come from two named constants so they are changeable in one place.

**Rationale:** it is the only option that keeps the page's own principle (a render is a development, not a baked output) while giving scrub, pause and a testable resting state at no dependency cost.

---

## Y — Gate

**Conviction:** YELLOW. The structure is sound and the measurements are real, but nothing has run on a phone, and the frame-budget rule is untested under throttling.
**Stability:** PROVISIONAL.
**Door:** two-way. This is one file and reverts by git.

---

## Consequences

- **Easier:** scrubbing and pausing any animation; a deterministic test of the resting state; one reduced-motion path; adding a track means adding data.
- **Harder:** slightly more code than CSS for trivial effects; the engine must be kept small and honest about what it does.
- **To revisit:** a second adopter (extract to `_PATTERNS/` as a snippet); a DESIGN.md motion section, since DESIGN.md has none today and the design-debt gate will judge motion by the page's own choices; real-device performance.

## Action Items

1. [ ] Implement the engine and the three v1 tracks in `_ARTIFACTS/raw-capture.html` (separate PR).
2. [ ] Add the rest-invariant check and run it in a headless pass.
3. [ ] Measure on a throttled CPU (4x slowdown) and on a phone before moving to DECIDED.
4. [ ] Move the opening sweep onto the engine.
5. [ ] Ask whether DESIGN.md should gain a motion section (durations, easing, reduced-motion rule).
6. [ ] Republish the artifact once the PR merges.

## Not decided here

How animation applies to the five-axis decision geometry, and any claim about what the Snap track proves. It shows a slope change in one column, once.
