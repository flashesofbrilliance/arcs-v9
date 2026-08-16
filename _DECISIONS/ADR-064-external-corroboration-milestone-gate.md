# ADR-064 — External corroboration is the milestone gate; impact is the rank

- **Status:** Accepted
- **Date:** 2026-08-16
- **Allocated:** `scripts/oracle.py next adr` → 64 (never hand-guessed; see ADR-057)
- **Y-gate:** GREEN (unanimous 14-agent panel; the design is the *survivor* of the gauntlet, not its input)
- **Relates to:** ADR-046 (witness), ADR-053 (Tao / open-private seam), ADR-062 (a falsifier must turn
  on itself), the milestone-artifact engine, WORLD.md render-scale. Supersedes the "witnessed-provenance
  as the milestone ranking function" proposal.
- **Provenance:** falsification ledger **F33**; advisory-panel run `wf_b1f37548-af2` (7 C-suite chiefs +
  6 dialectic lenses + synthesis).

## Context

`status.arcs.care` (public resumeware, read by hiring panels / consulting buyers / boards) carries a
milestone timeline that goes stale — it froze at "Day 98" until hand-forward-propagated. The proposal
was to auto-source milestones from ADRs/DEWY receipts, **ranked by a witness-echo** (a live attestation
that a decision was a real flash, promoted only if durable), hardened by a five-fix "kintsugi" pass
(orthogonal-echo-only rank, oracle-timestamped contemporaneity, committed threshold, denominator, and a
flip to `gate=witnessed-provenance, rank=impact`).

A **14-agent independent gauntlet** (F33) **unanimously falsified** that design. The fatal finding:
kintsugi repairs #1 and #5 **mutually annihilate** — flipping the rank to *impact* welds shut the very
door the load-bearing orthogonal-echo detector was hardened to guard, collapsing the whole
witness→echo→oracle→air-gap apparatus into dead weight feeding a gate that certifies **typing-time, not
truth**, while "impact" ships undefined and self-scored over an **author-controlled corpus**. The panel
also surfaced a *live* defect: the page's milestone commit links pointed at a now-private repo and 404'd.

The honest lesson (F33): **independence, not thrift, was the operative variable** — a self-gauntlet
cannot catch its author's blind spot.

## Decision

**External corroboration is the gate. Impact is the rank. The provenance machinery is cut from v1.**

1. **GATE (eligibility, load-bearing — the renderer refuses to publish without it):** provenance-honesty
   floor **AND at least one reviewer-clickable proof-of-consequence the author does not custody** — a live
   URL strangers use, a merged PR in a repo the author does not own, a named reference who will take a
   call, a dollar figure with a source. Self-attested / author-custodied items may render as **quiet,
   labeled context** but can **never outrank** a corroborated item.
2. **RANK (within the corroborated tier only):** **impact = materiality × external-verifiability.**
   *Materiality* = it shipped and is live, or someone other than the author acted on it (adopted, paid,
   deployed, cited, hired). *External-verifiability* = the clickable proof above. Un-verifiable
   high-asserted impact ranks **below** modest verifiable impact. Witness echoes, ADR/commit counts, and
   provenance chains score **~0** — internal activity the reader does not weight. Recency is a tiebreak.
3. **CUT from v1** (demoted to a possible internal tool, earned back only if manual curation actually
   becomes the bottleneck or an adversarial audit materializes): the witness→echo layer, the
   machine-detected orthogonal-echo detector (per CTO/CDAIO, not buildable as a reliable checkbox), the
   sequence-oracle contemporaneity stamp, the air-gap *inference* pass, and the "N of M falsified" stat
   (kept only if the denominator of claims *made* is honest — otherwise survivorship).
4. **SENSITIVITY GATE:** a classifier decides which ADRs are milestone-eligible at all. A faithful gloss
   of a sensitive ADR (client names, unshipped strategy) is a faithful *leak* to an employer-facing page;
   drift-check only proves the gloss *matches* the source, not that it is *safe to show*.

## Build (smallest honest version)

A hand-curated flat-file (or a trivial script over the dated ADR/DEWY index) timeline. Each entry:
`{ date, gloss (one line), external_proof (required, reviewer-clickable), tier }`.
- The **only** auto-refreshed field is the **date** — which is all the actual Day-98 stale bug ever needed.
- The renderer **refuses to publish any entry missing `external_proof`**, and **verifies every link
  resolves at publish time** (arcs-v9 went private 2026-07-24; one dead "live" link is the cheapest
  kill-shot on an honesty page — this is the F33 defect made structural).
- Rank by the proof tier; render self-attested items as quiet labeled context.
- Disclose the page is a generated/AI-assisted artifact.

This cuts ~80% of the build and ~100% of the recurring token cost of the original proposal while
delivering 100% of the fix for the stated problem.

## Consequences

- The one primitive that was always the product — **a claim earns its place by a proof a stranger can
  open without your word** — is kept; everything built around it is dropped.
- Milestones with weak external proof (e.g. gradual internal mechanization) render as *context*, not top
  rank — correctly, for this reader. (This overturned an earlier author claim that low-echo/high-impact
  work should be *demoted*; the fix is that it is *eligible and context-ranked*, not hidden.)
- The `status.arcs.care` milestones should migrate to link reachable external proofs (`good.arcs.care`,
  connector pages, `resume.arcs.care`) rather than private-repo commits; the `82dd484` dead-link removal
  was the interim patch.
- **Cost line:** v1 ≈ one focused build (flat-file + a link-resolve check + a sensitivity filter); near-zero
  recurring cost. The cut machinery's cost goes to zero. Every future spec still carries its own cost line.
