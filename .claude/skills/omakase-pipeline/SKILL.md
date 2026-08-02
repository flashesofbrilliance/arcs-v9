---
name: omakase-pipeline
description: Turn one engagement corpus into the three-surface artifact family — back-of-house SSOT (gated), the canon/cellar (coursed narrative), and a target-tuned front-of-house suite at 25th-polish essence. The instance→class generalization of jeben.arcs.care → omakase.arcs.care → louisville.arcs.care. Use when standing up a new counterpart/engagement universe end to end, or leveling an existing one.
---

# /omakase-pipeline — one corpus, three fences, lossless at every altitude

> **Provenance (the instance this class is lifted from):** jeben.arcs.care (back of house)
> → omakase.arcs.care (the cellar/canon) → louisville.arcs.care (front of house, the
> target-tuned elevated state). Built Jul 2026; hardened by CISO review, two multi-agent
> gauntlets, and the reputation air-gap incident (see ADR-038 provenance + the
> internal-external air-gap memory). This skill is the repeatable version.

## The model

One **source corpus** renders as three surfaces, each a different setting of the three
dials (Register · Altitude · Fidelity — see the resonance filter / lossless-translation
codex). Nothing load-bearing is lost between surfaces; what a surface cannot carry is
withheld **and logged**, never dropped silently.

| Surface | Class | Altitude | Fidelity | Access | Instance |
|---|---|---|---|---|---|
| **Back of house** | SSOT + war room / thread book | Surgical → Tactical | SHARP (grades on the sleeve, candid reads, the recoil) | Auth: magic-link + ADMIN_EMAILS (never a shared password) | `jeben.arcs.care`, `/warroom/[slug]`, `/recoil/[id]` |
| **The cellar / canon** | Coursed narrative, the method as craft | Strategic → Operational | DEGRADED (the how without the weights; the resonance filter itself) | Open or soft-gated, method-not-weights | `omakase.arcs.care` |
| **Front of house** | Target-tuned suite, the taste | Operational → Exec | GRAIN→essence (the 25th polish; the value, never the recipe) | Open, counterpart-facing | `louisville.arcs.care` |

**The move is Surgical → Executive.** Same seed, walked *up* in altitude and *down* in
exposed fidelity, gaining breadth and losing nothing load-bearing. The front of house is
not a dumber back of house; it is the same corpus milled to its essence (seimaibuai).

## The invariants (the lossless guarantee)

Enforce these on every surface. Invariants 1, 2, 4, 5 are checked by Step 5's grep pass (the manual backstop); the loss log in #3 is mechanical ONLY for SSOT-authored surfaces (recoil_brief.py emits `_redaction_report`), and manual for hand-authored ones:
1. **Nothing load-bearing lost.** The falsifier, the line/exit, and the decision survive
   every altitude. The Elder guards this.
2. **Attribution rides through.** "per Jeben" stays "per Jeben" in every voice. Credit is
   load-bearing, never sanded off.
3. **Withholding is printed, never silent.** What a surface cannot carry goes to a loss
   log. This is mechanical (`_redaction_report`) only when the surface is rendered from the SSOT via recoil_brief.py; hand-authored surfaces (the louisville pattern) have no auto loss log, so Step 5's grep is the only backstop and MUST be run. `redaction_policy` in the SSOT is a human-readable intent note, not a wired control.
4. **Consonance, not contradiction.** No surface may contradict another. If two registers
   disagree, the translation failed, not the reader. The Skeptic guards this.
5. **Air gap ([[internal-external-artifact-air-gap]]):** show your own updates not their
   intent-scores; method crosses, subject-about-them never does; architecture crosses,
   weights don't. Any front-of-house surface is scanned before publish (grep the danger
   terms: candid reads, criticism of the counterpart, recoil internals).

## Composition & assembly rules (the guest test)

These are the critique findings from the omakase.arcs.care dual-agent review (2026-07-25),
lifted from one-off feedback into **assembly rules** the pipeline enforces on every coursed
or front-of-house surface. The named dominant failure mode is
**author-cosmology-over-guest** ([[author-cosmology-over-guest-design-risk]]): a surface
that serves the maker's meaning-making over the guest's job-to-be-done. Craft is necessary,
not sufficient — a surface can be beautifully authored and still fail this test.

Apply as composition rules while assembling (Step 3–4), and as a gate before ship (Step 7):

1. **Thesis before the curtain.** The load-bearing claim must reach a bounce-path visitor
   *before* any narrative device. Empty bounce path = fail. (The evaluator forwards a PDF,
   not the theater, if the thesis is gated behind an entrance sequence.)
2. **One primary door.** A finale/CTA offers exactly ONE primary action, with a reassurance
   line beside it. Collapse option-forests (an 11-option finale → one door; eggs/extras →
   a single secondary affordance). Disabled ghost buttons are dead weight — cut them.
3. **One claim, one course.** N metaphors for a single claim = one course with N doors, not
   N courses. Merge metaphor-redundancy; match structure to substance (e.g. 9 scenes ↔ 9
   lanterns, not 12).
4. **Forward-this, not a PDF.** For each persona, ask: would they forward *this surface*, or
   extract a plain summary and forward that? If the latter, the theater is in the way of the
   value — mill it down (seimaibuai) until the surface itself is the forwardable thing.
5. **Guest altitude, not author altitude.** Never render above the guest's altitude
   ([[met-at-your-level-onramp-design-principle]]); the self-referential cosmology that
   thrills the maker reads as "theater over my problem" to the buyer.
6. **Reachability of the payoff.** The gift / kernel / real value must not sit 4+ interactions
   deep. Count taps to the payoff per persona; if it's buried, promote it.

Run these as a **persona pass**: walk each target persona (maker / steward / weaver /
auditor / evaluator) through the assembled surface and record where each rule breaks. A rule
break is a P0/P1, not a nitpick.

## The cutting crew (the six operators, one cut each)

Weaver → register · Jeweler → fidelity/essence · Elder → the lossless invariant ·
Skeptic → consonance/falsifier · Loki → the mask (wears the register, then checks it is
resonance not flattery) · Curator → synthesis into the final surface + the loss log.

## The pipeline

**Step 1 — Ground the source corpus.** Gather the real material (transcripts, notes, the
SSOT if one exists, prior recoils). One source of truth. No fabrication; every claim
traces (real-data rule). If a war-room SSOT exists, it is the corpus; else scaffold it
(`/recoil-new`).

**Step 2 — Build the back of house (SHARP, gated).** The internal war room / thread book /
recoil at full fidelity: candid reads, grades on the sleeve, the falsifier and the exit.
Auth-gated (magic-link + ADMIN_EMAILS). This is where nothing is withheld.

**Step 3 — Cut the cellar / canon (DEGRADED, method-not-weights).** The coursed narrative:
the method shown as craft (the resonance filter, the dual bar-raiser, kintsugi) without the
weights, DDL, or tunable params. This is the "one craftsman to another" register.

**Step 4 — Tune the front of house (essence, open).** The target-tuned suite at 25th polish:
the taste and the value, never the recipe. Register-cut per persona (maker / steward /
weaver / auditor), altitude at Exec/Operational, fidelity GRAIN. Cone-of-silence preserving.
**Assemble against the Composition & assembly rules above** — thesis before the curtain, one
primary door, one-claim-one-course, forward-this-not-a-PDF. These are compositional
constraints during assembly, not polish applied afterward.

**Step 5 — Run the consonance + air-gap check across all three.** Prove lossless: the same
load-bearing content resolves in every surface; attribution preserved; the loss report is
populated, not empty-because-nothing-was-checked. Grep every open surface for danger terms
(counterpart criticism, recoil internals, weights). Fail closed.

**Step 6 — Deploy + gate.** Back of house behind auth; cellar soft-gated or open
method-only; front of house open. Verify gates live (`curl` an unauth request → the right
redirect/404). Never a shared password (that was removed; identity gating only).

**Step 7 — Harden (the gauntlet).** Fan out a multi-agent critique (LAB / BAR / COURT /
funhouse / KKL lenses) → adversarially verify → distill surviving findings → apply. **Include
the guest-test persona pass** (Composition & assembly rules above) as an explicit lens — it
catches author-cosmology-over-guest, which the security/ruin lenses miss. This is the "25th
polish" bar: iterate the distillation until the corpus is a self-contained internal/external
universe with no load lost, no leak, and no theater in front of the value. See `/code-review
ultra` or a Workflow gauntlet.

## Anti-goals

- A front of house that is a watered-down back of house (loses load) instead of a milled
  essence (keeps load, sheds exposure).
- Silent redaction (a surface that drops something without logging it).
- A shared-password gate on any internal surface (identity gating only).
- Register drift: the same fact contradicting itself across surfaces.
- Author-cosmology-over-guest: the maker's self-referential theater in front of the guest's
  value (thesis gated behind a curtain, option-forest finales, N metaphors for one claim,
  payoff buried 4+ taps deep). Beautiful and still wrong — the guest test is a ship gate.
