---
status: DRAFT (pending Zach's voice pass)
series: Lore (good.arcs.care/series/lore, not yet built)
entry: 1
lore_class: myth            # a causal story about how the world works; the verdict grades it
binding_verdict: undecided  # may be TOLD, not CITED, until the falsifier below resolves
date: 2026-10-02
---

# The Exoskeleton

*Lore, entry one. Why ARCS is built the way it is.*

> Bracketed `[ZACH: ...]` marks are holes only you can fill. Everything else is a draft for you to
> cut. Every claim about the system cites a file you can open; anything unverified says so.

---

## The lede

An exoskeleton does not walk for you. It carries the load so your own legs can do the part only
legs can do. Everything in ARCS that looks like process is load-bearing hardware for a mind that
accelerates faster than it brakes. This is the story of why it was built, and the test that will
tell us whether it works.

## I. Lambo engine, bike brakes

I identify as ADHD. `[ZACH: confirm you want this named publicly, in these words.]`

The description I have used for years is a Lambo engine with bike brakes: high acceleration, high
synthesis, and throttle control as the edge I have never fully owned. `[ZACH: one concrete scene.
A specific morning, a specific loop you could see yourself in and could not exit. The essay lives
or dies on this paragraph.]`

Executive function is the clinical name for the brakes, the clutch and the dashboard. Psychologists
usually split it into a handful of jobs: holding things in mind (working memory), not acting on the
first impulse (inhibition), laying out steps before taking them (planning), switching tasks without
dropping the thread (shifting), and noticing when you have drifted (self-monitoring). For a mind
like mine those jobs are not absent. They are expensive, and they run out first.

## II. The prosthetic I kept describing

Long before there was an app I kept reaching for the same metaphor. In my own notes it shows up as
a "digital prosthetic surrogate prefrontal cortex," then as "an exoskeleton for the mind, not a
replacement brain." I said it, and then I built it, mostly without noticing that every new
instrument was another strut on the same frame.

Laid side by side, the mapping is almost embarrassing:

| Executive function job | The strut in ARCS | Where it lives |
|---|---|---|
| Working memory | **Receipts.** A decision frozen as a coordinate, so I carry two handles instead of twenty-five. | `_CANON/ARCS-PHASE-CHANGE-THESIS-001.md` ("External RAM") |
| Inhibition | **The Y gate.** A deliberate yellow light before commitment; RED says "you are free-soloing this." | `src/lib/ygate.ts`, `WORLD.md` |
| Planning | **PrepSession.** Five fields, two minutes, including the strongest argument against my instinct. | `src/app/api/prep/route.ts` |
| Self-monitoring | **Drift Sentinel and Throttle Gate.** Five turns without an artifact and the system asks: land the plane, or keep exploring? | `WORLD.md`, `arcs-intel-protocol/MEMORY.md` |
| Shifting | **Handoffs.** The session ends; the thread does not. The next session reads one block, not my whole head. | `CLAUDE.md` handoff policy, `_STATE/handoff-progress.jsonl` |
| Capture under load | **Witness.** When a flash lands mid-conversation, attest it now, verbatim, not reconstructed hours later. | `WORLD.md` ("The Witness") |

None of these were designed from that table. The table was found afterward, which is either the
most honest kind of design or the most flattering kind of hindsight. Section IV is how we find out
which.

## III. The rule that keeps it an exoskeleton

There is a version of this that becomes a wheelchair: the machine decides, the human rides. ARCS
has a constitutional rule against that, NOTOMATION: tools may scaffold and sequence cognition, never
compress, replace, or overrule a revealed preference. The machine explores options; the human
commits reality.

That rule is the whole difference between a prosthetic and a replacement. A prosthetic you stop
noticing. A replacement you stop being. `[ZACH: one line on a moment the scaffold handed a decision
back to you instead of making it.]`

## IV. The crack, shown not hidden

Here is the uncomfortable part. Of the receipts the system has filed, the last recorded count of
ones with an outcome closed is **2 of 247** (figure from the project handbook; re-measure against
the database before publishing).

An exoskeleton for executive function should help a mind like mine *finish*, not only *start*.
Starting is where ADHD already has horsepower to spare. If ARCS is brilliant at opening loops and
nearly silent at closing them, then what I have built so far is an exoskeleton for the engine,
not the brakes. That is a real finding, and it goes on the page in gold, not under a patch.

## V. The falsifier

This story is filed as **myth, verdict undecided**: told, not yet cited.

- **The claim:** ARCS scaffolds executive function, including the closing half of the loop.
- **What would prove it wrong:** outcome capture stays flat. Concretely, if by
  `[ZACH: date, suggest 2027-01-01]` no cohort reaches the Accountant's own calibration floor of
  **30 closed outcomes** (`operators/arcs_accountant.py`, `CALIBRATION_MIN_N = 30`), the thesis is
  downgraded from "exoskeleton" to "ignition system," publicly, here.
- **What would confirm it:** closures climb to that floor, and the closed receipts show calibration
  (outcome versus conviction) rather than noise.

Either way the entry stays up. The verdict changes; the story does not get rewritten.

## Coda

`[ZACH: the closing image. Suggestion: the exoskeleton is not the point. The point is the day you
notice you walked the last mile with it switched off.]`

---

### Draft LORE row (append to `runtime/specs/lore.jsonl` once wording is approved)

```json
{"id": "lore-015", "class": "myth",
 "story": "<ZACH's one paragraph, in his words>",
 "told_where": "good.arcs.care/series/lore/the-exoskeleton",
 "observation": "Every ARCS instrument maps to one executive-function job (receipts=working memory, Y gate=inhibition, PrepSession=planning, Drift Sentinel=self-monitoring, handoffs=shifting).",
 "mechanism_claimed": "Externalizing executive-function load frees the operator's own capacity for the judgment only they can make.",
 "binding_verdict": "undecided",
 "test_that_decided": null}
```

### Open before building the page
1. Zach's voice pass on every `[ZACH]` mark, and an explicit yes on naming ADHD publicly.
2. Re-measure the 2/247 figure against the DB.
3. Confirm the lore.jsonl id (the file's own check enforces sequence; next is `lore-015` if 14 rows hold).
4. Then: `good.arcs.care/series/lore` index (clone the `/series/receipts` shape), the entry page,
   `src/proxy.ts` routes, and the repo's gates (`artifact_wrap_lint.py`, width sweep, em-dashes 0).
