---
title: Stopped light, quantum memory, and what ARCS can steal from them
version: 0.1.0
date: 2026-10-03
status: research (no build decided)
source: LinkedIn post by Vincentius Liong/Leong (Sep 23) on Lene Vestergaard Hau's slow/stopped-light work, read 2026-10-03
---

# Stopped light, quantum memory, and what ARCS can steal from them

The shape of the field in one line: **you cannot hold light, but you can pour it into matter,
hold the matter, and pour it back out, if you do it slowly enough and protect it from noise
while it waits.** Almost every hard problem in ARCS memory (compaction, handoff, stale claims,
receipts that never close) is that same sentence.

## 0. Claim check on the source post

| Claim in the post | Verdict | Evidence |
|---|---|---|
| 1999: pulse slowed to 17 m/s in ultracold sodium via EIT, Nature | CONFIRMED | Hau, Harris, Dutton, Behroozi, Nature 397, 594 (1999) |
| 17 m/s is about 38 mph, roughly 20 million times slower than c | CONFIRMED, rounded up | 17 m/s = 38.0 mph; c / 17 = 17.6 million |
| 2001: pulse stopped, stored in atomic coherence, revived, Nature | CONFIRMED, but incomplete | Liu, Dutton, Behroozi, Hau, Nature 409, 490 (2001). The post omits that Phillips, Fleischhauer, Walsworth, Lukin did it at the same time in warm Rb vapor (PRL 86, 783, 2001) |
| Later: information transferred between cold atomic clouds | CONFIRMED | Ginsberg, Garner, Hau, Nature 445, 623 (2007): stored in one BEC, revived from a different BEC 160 um away, carried by a travelling matter wave |
| "Did not literally make photons sit motionless" | CONFIRMED (the post's best paragraph) | The photon is gone; its amplitude and phase live in a spin wave of the atoms |
| Sources | THIN | lnkd.in shortlinks, "Credits: CTTO" (credit to the owner, i.e. unknown) |

Net: accurate science, credit to one lab for a two-lab result, provenance unrecorded. In ARCS
terms the facts go in `what_confirmed`, the attribution goes in `what_unconfirmed`.

## 1. The physics, without the jargon wall

- **EIT (electromagnetically induced transparency).** An opaque cloud of atoms is made
  transparent to a weak "probe" beam by shining a strong "control" beam on it. The two paths
  that would let the atom absorb the probe cancel each other (destructive interference). The
  transparency window is narrow, and narrow windows mean steep dispersion, and steep dispersion
  means slow group velocity. That is the 17 m/s.
- **Dark-state polariton** (Fleischhauer and Lukin, PRL 84, 5094, 2000). Inside the cloud the
  pulse is not pure light; it is a mixture of light and atomic spin excitation. A single dial,
  the *mixing angle*, set by the control beam's strength, decides the ratio. Turn the control
  beam down and the pulse becomes more matter and slower; turn it off and it is 100% matter and
  stopped. Turn it back on and the light comes back with the same shape and phase.
- **Adiabatic.** The dial must be turned slowly compared with the transparency window, or the
  information scatters out instead of transferring. Fast is lossy.
- **Coherence time (T2) and decoherence.** Stored information decays as each atom's phase
  drifts at its own rate. Storage time is set by how well you protect phase, not how well you
  hold atoms.
- **Spin echo / dynamical decoupling.** If atoms dephase because each sits in a slightly
  different environment, a well-timed flip pulse makes them run the drift backwards and line
  up again (rephase). Repeat the flips and slow noise cancels.
- **ZEFOZ (zero first-order Zeeman).** Pick a magnetic field where the storage transition is,
  to first order, insensitive to field noise. Store in a representation the noise cannot touch.
- **Atomic frequency comb (AFC).** Carve the absorption spectrum into evenly spaced teeth
  before the light arrives. The comb spacing fixes, in advance, the moment the echo comes back
  (1/spacing). The recall time is designed at write time.
- **Heralding.** A memory that emits a signal saying "I stored it" so the network only builds
  on links that actually succeeded.
- **Quantum repeater.** Entangle short segments independently, park each in memory until both
  sides herald, then join them with a swap. Memory is what lets slow, unreliable links compose.

## 2. State of the art (as of 2026-10)

| Axis | Record / frontier | Platform |
|---|---|---|
| Storage time | ~1 hour coherent optical storage (Ma et al., Nat Commun 12, 2381, 2021); ~53 min reported with dynamical decoupling | Eu:YSO rare-earth crystal, ZEFOZ + DD |
| Storage time, cold atoms | > 1 s in a BEC (Zhang, Garner, Hau, PRL 103, 233602, 2009) | BEC in optical dipole trap |
| Storage time, room temp | ~1 s in warm alkali vapor (Katz and Firstenberg, Nat Commun 9, 2074, 2018) | warm Rb/Cs vapor |
| Efficiency | ~90% in an impedance-matched cavity (arXiv 2609.19807, 2026); integrated chip memories 80% (weak pulses), ~70% heralded single photons (arXiv 2511.05928) | rare-earth crystal |
| Multimode | 100 to >1000 temporal modes in one crystal | AFC rare-earth |
| Networking | Heralded entanglement between solid-state memories over 14.5 km with Bell violation (arXiv 2508.17940, Nat Photon 2026) | multiplexed repeater, no fiber phase stabilization |
| Deployability | Rack-mount warm-vapor memory, no cryogenics: ~95% fidelity, ~1 ms, ~5% efficiency (Qunnect) | warm Rb, 2U chassis |
| Light to sound | Coherent optical RAM in acoustic waves on chip (arXiv 2311.06219); coherent refresh extends storage | stimulated Brillouin scattering |
| Photon logic | Single-photon transistor, gain > 10 free space, > 10^3 with a cavity | Rydberg EIT, blockade |

The headline pattern: **no platform wins every axis.** The hour-long memory is cryogenic and
inefficient to read; the 90% memory holds briefly; the deployable one is 5% efficient and
ships. Memory is judged on a vector (efficiency, fidelity, storage time, bandwidth, mode count,
noise, deployability), never a scalar.

### Adjacent and orthogonal results worth knowing

- **"Negative time" (Angulo, Thompson, Nixon, Jiao, Wiseman, Steinberg, 2024).** Measured by
  weak probing, the time a transmitted photon spends as an atomic excitation equals the group
  delay, which can be negative. No signal goes faster than light; the pulse is reshaped so its
  peak exits early. Lesson: an aggregate timing metric can read "impossible" without anything
  impossible happening.
- **Time reflection (Alu group, CUNY, Nature Physics 2023).** Change a medium's impedance
  abruptly *in time* and part of a travelling wave reflects backwards with all its frequencies
  converted. A temporal interface does to waves what a mirror does in space.
- **Quantum Zeno effect** (Misra and Sudarshan 1977; single-atom real-space demonstration
  2025/26). Measure a system often enough and it stops evolving. Measure at the wrong rate and
  you can speed decay (anti-Zeno).
- **Quantum memory as a learning resource (Huang, Preskill et al., Science 376, 2022).** An
  experiment that *stores* quantum states and processes them jointly can learn with
  exponentially fewer runs than one that measures each state immediately and processes the
  classical results, even with unlimited classical compute. Measuring early is the loss.
- **Hau's later turn** (2009 to 2010): electro-optical nanotraps and single carbon nanotubes
  that capture and field-ionize cold atoms. Same instinct: control one degree of freedom
  exquisitely and the system becomes an instrument.

## 3. Isomorphisms to ARCS

Each row says whether it is a *mechanism* match (same math, could transfer a design rule) or a
*metaphor* (useful lens, no math carried over). Metaphors are labeled so nobody builds on one
as if it were load-bearing.

| # | Physics | ARCS counterpart (real file) | Kind | Design rule it carries |
|---|---|---|---|---|
| I1 | Dark-state polariton: one dial moves a pulse from light to matter | Live conversation (fast, volatile) to receipt / commit (slow, durable). The ADR candidate's Part A redactive codec (`_SEEDS/ADR-CANDIDATE-2026-09-17-defeasible-context-codec-and-kinematic-freshness.md`) | mechanism | **Adiabatic condition:** convert to the durable medium *while the control field is still on.* Compaction at session end is turning the control beam off abruptly; the information scatters. The Witness (WORLD.md) is the right instinct: write during, not after |
| I2 | Stored in BEC #1, revived from BEC #2 by a messenger matter wave (2007) | Cross-session and cross-harness handoff (Claude Code to Hermes; CLAUDE.md handoff block; `_STATE/snapshot.json`) | mechanism | Revival works only if the second medium is phase-coherent with the first and re-lit by the *same* control beam. A handoff must carry **phase** (the bearing, the why) not just **amplitude** (the facts), and the receiver must share the schema |
| I3 | T2 decoherence; dynamical decoupling; ZEFOZ | Defeasible claims and the freshness horizon (Part B of the same ADR candidate); pinning by sha/path in receipts | mechanism | Two separate protections: (a) *refocus* on a schedule (re-exhaust a claim before its horizon), and (b) *store in a noise-insensitive basis* (cite content hashes and invariants, never "latest" or "currently") |
| I4 | Spin echo: inhomogeneous dephasing is reversible with a flip pulse | Parallel sessions drifting apart (oracle number collisions, worktree divergence, `sync_worktree.sh`) | mechanism | Drift from *different local environments* is reversible if you rephase before the information is truly lost. Reconcile on a cadence shorter than the drift time, not after a collision |
| I5 | AFC: recall time is designed into the comb at write time | Receipt outcome capture: 2/247 closed (AGENTS.md backlog table). The debrief-email nudge exists but recall is not designed per receipt | mechanism | **Echo-scheduled receipts:** every receipt carries its recall moment at write time, derived from its horizon (`today` / `this-week` / `this-quarter` / `1-3y`). The comb *is* the horizon field; nothing new to ask the user |
| I6 | Memory figure of merit is a vector | Librarian (Op 21) `reserve_ratio`, `curation_debt`; Accountant (Op 19) | mechanism | Score ARCS memory on the same seven axes: recall efficiency, recall fidelity, useful lifetime, write bandwidth, mode count, false-recall noise, deployability. A scalar hides the trade-off |
| I7 | Heralding: build only on links that announced success | `what_confirmed` vs `what_unconfirmed`; "receipts or it didn't happen" | mechanism | Already present. Physics adds: the herald must be emitted by the *memory*, not inferred by the reader. A receipt is a herald only if the system that did the write emits it |
| I8 | Repeater: segments herald independently, then an irreversible swap joins them | WRITE-LOCK (ROM primitive 7); multi-stakeholder decisions | mechanism | Do not commit end to end until every segment has heralded. The swap (Bell measurement) is the one-way door: declare it, then fire it once |
| I9 | Rydberg blockade: within a radius, only one excitation can exist | Oracle-first numbering (gotcha 12); git non-fast-forward as the atomic lock | mechanism | A blockade radius is a named scope in which concurrent writes are physically refused. The oracle already is one; the transistor gain (>10) says one gate signal (an explicit "go") may legitimately control many downstream writes |
| I10 | Quantum Zeno: measure too often and evolution freezes | Kinematic re-check pacing in Part B, which today has only a **Nyquist floor** | mechanism (new) | Add a **Zeno ceiling**: re-checking a live decision faster than it can evolve freezes it (and burns review attention). The legal re-check band is between Nyquist and Zeno, and the band is per decision |
| I11 | Store-then-process beats measure-then-process (Huang/Preskill) | Summaries as measurement; NOTOMATION; Part A keep-verbatim | metaphor with a real classical shadow | Summarizing each item on arrival is measuring it: the collapse is irreversible. Keep raw spans addressable and compare jointly later. The exponential advantage does not transfer to classical text; the direction (do not collapse early) does |
| I12 | Negative group delay: the average exits before the input | Dashboards over receipts (time-to-decision, NCI trends, closure rate) | metaphor (cautionary) | A reshaped distribution can make an aggregate look acausal. When a metric reads impossible, look at per-item dwell, not the mean. Pairs with the Accountant's n >= 30 rule |
| I13 | Time reflection: an abrupt change in the medium reflects in-flight waves | Pivots: stakes change, a counterpart leaves, a fact flips | metaphor with a usable trigger | An abrupt change of the *medium* (not of the decision) should emit a reflected copy of every in-flight receipt for re-evaluation. That is a concrete defeater trigger for Part B |
| I14 | Warm vapor ships at 5% efficiency; cryogenic records stay in the lab | stdlib-only operators; "teleport to terminal" (gotcha 11) | metaphor | Deployable beats record. Prefer the room-temperature operator |
| I15 | Brillouin memory: move light into slow sound, refresh coherently | Chat (fast medium) to git (slow medium); periodic re-pump of stale memory | metaphor | Store in the slow medium. Refresh costs noise; refresh on a schedule, not continuously |

## 4. Inventions, ranked by evidence-per-effort

### INV-1. Zeno ceiling for kinematic freshness (extends ADR candidate Part B)
- **What:** each warranted claim or live decision gets `recheck_band = [nyquist_floor, zeno_ceiling]`.
  Floor: sample faster than twice the observed rate of change (already in the candidate).
  Ceiling: never re-check faster than the claim's minimum observed change interval, because
  re-checks that find nothing new are pure cost and, for human-facing decisions, pressure that
  stalls movement.
- **Why it is new:** the candidate defines a lower bound only. Every scheduler with only a
  lower bound drifts toward over-polling. (This session's own PR check-in rule is an instance:
  it stops after 3 empty check-ins, which is a hand-tuned Zeno ceiling.)
- **Falsifiable test:** over the existing drift sentinel and check-in logs, count re-checks that
  found no change. Prediction: > 60% of re-checks are null. If < 20%, there is no Zeno regime
  worth bounding and INV-1 is withdrawn.

### INV-2. Echo-scheduled receipts (attack the 2/247 closure gap)
- **What:** at receipt write time, compute `recall_at` from `horizon` (the comb spacing) and
  store it on the receipt. The debrief nudge fires at `recall_at`, not on a generic cadence.
  Optional: a two-tooth comb (early read at 1/3 horizon, closing read at horizon) for
  `this-quarter` and `1-3y`.
- **Why:** AFC memories get on-demand, directional recall because the recall time was
  engineered at write time. ARCS receipts are written with a horizon and then never told when
  to come back.
- **Falsifiable test:** for receipts written after the change, closure rate at
  `recall_at + 7 days` vs the 2/247 baseline. Kill condition: no lift above baseline after 30
  receipts reach their `recall_at`. Respects the Accountant's sufficiency rule (n >= 30 before
  any calibration claim).

### INV-3. Seven-axis memory scorecard (Librarian / memory pipeline)
- **What:** a stdlib script that scores a memory source (handoff blocks, `MEMORY.md`, witness
  stubs, the Librarian's picks) on recall efficiency, fidelity, lifetime, write bandwidth,
  mode count, false-recall noise, deployability, emitting a vector, never a total.
- **Why:** the physics community stopped arguing "best memory" once it adopted the vector.
  ARCS has three memory surfaces competing on vibes.
- **Falsifiable test:** the vector must rank at least one pair of surfaces differently on two
  axes (a real trade-off). If one surface dominates every axis, the scorecard collapses to a
  scalar and the extra axes were decoration.

### INV-4. Phase-carrying handoff check (from the 2007 two-BEC result)
- **What:** a cold-read test for handoff blocks: give a fresh session only the block and ask it
  for the *next move and why*. Score agreement with the author's stated bearing, not fact recall.
- **Falsifiable test:** if fact recall is high and bearing agreement is low on >= 3 recent
  handoffs, handoffs carry amplitude without phase, and the block template needs a bearing line.

### INV-5. Time-interface trigger (from time reflection)
- **What:** a defeater trigger that fires when a counterpart's or project's *medium* changes
  (stakes field edited, owner changed, a dependency repo archived), emitting re-evaluation
  flags for every open receipt in that medium. Lower priority: needs a medium registry first.

## 5. What not to take from this

- No quantum anything in the product. These are design rules borrowed by isomorphism; the
  stack stays Next.js + stdlib Python.
- The polariton picture is a two-state mixing dial. It does not license a "quantum decision"
  claim in public copy (Myst, not vaporware; WORLD.md tonal register).
- The negative-time result is not time travel, and the post does not claim it is. Keep it as a
  cautionary metaphor only.

## Sources

- Hau et al., Nature 397, 594 (1999): light speed reduction to 17 m/s
- Liu, Dutton, Behroozi, Hau, Nature 409, 490 (2001); Phillips, Fleischhauer, Walsworth, Lukin, PRL 86, 783 (2001): https://link.aps.org/pdf/10.1103/PhysRevLett.86.783
- Fleischhauer and Lukin, dark-state polaritons, PRL 84, 5094 (2000): https://journals.aps.org/prl/pdf/10.1103/PhysRevLett.84.5094 ; PRA 65, 022314 (2002): https://link.aps.org/pdf/10.1103/PhysRevA.65.022314
- Ginsberg, Garner, Hau, Nature 445, 623 (2007): https://www.laserfocusworld.com/test-measurement/research/article/16553016/laser-optical-data-processing-bose-einstein-condensates-enable-light-revival
- Zhang, Garner, Hau, PRL 103, 233602 (2009): https://arxiv.org/abs/0909.3203
- Hau lab later work (nanotube field ionization, PRL 104, 133002, 2010): https://physics.aps.org/synopsis-for/10.1103/PhysRevLett.104.133002
- One-hour AFC storage, Nat Commun 2021: https://www.nature.com/articles/s41467-021-22706-y
- Light storage for one second at room temperature: https://www.nature.com/articles/s41467-018-04458-4
- 90% efficient rare-earth storage: https://arxiv.org/pdf/2609.19807 ; integrated memory: https://arxiv.org/pdf/2511.05928
- Rare-earth quantum networks review: https://arxiv.org/pdf/2501.06110
- AFC / echo memory explainer: https://arxiv.org/pdf/0908.2309 ; https://arxiv.org/pdf/1902.04313
- Metropolitan multiplexed repeater with Bell nonlocality: https://arxiv.org/html/2508.17940 ; https://www.nature.com/articles/s41566-026-01911-5
- Field-deployable warm-vapor memory (Qunnect): https://arxiv.org/pdf/2205.13091 ; https://thequantuminsider.com/2025/03/19/scientists-achieve-telecom-compatible-quantum-entanglement-with-room-temperature-memory/
- Brillouin photonic RAM in sound waves: https://arxiv.org/abs/2311.06219 ; refresh: https://arxiv.org/pdf/1904.13167
- Rydberg nonlinear optics and single-photon transistors: https://arxiv.org/pdf/2608.02992 ; https://arxiv.org/abs/1404.2876 ; https://www.nature.com/articles/s41598-019-41185-2
- Negative time: https://www.scientificamerican.com/article/evidence-of-negative-time-found-in-quantum-physics-experiment/ ; https://phys.org/news/2024-12-scientists-negative-quantum.html
- Time reflection: https://asrc.gc.cuny.edu/headlines/2023/03/scientists-demonstrate-time-reflection-of-electromagnetic-waves-in-a-groundbreaking-experiment/
- Quantum Zeno, single atom: https://www.nature.com/articles/s41467-026-74332-1
- Quantum advantage in learning from experiments: https://www.science.org/doi/10.1126/science.abn7293 ; https://preskill.caltech.edu/pubs/preskill-2022-quantum-advantage.pdf
