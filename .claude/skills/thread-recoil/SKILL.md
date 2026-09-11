---
name: thread-recoil
description: Produce a belief-update ledger (audit log) for the CURRENT thread/session — the open→close belief-diff plus, for each prior that moved, the external data that moved it. Use when the user asks for "the recoil on this thread," a belief-change audit, "what did we update and why," a proof-of-belief-change, or a session self-audit. Takes an optional depth arg: simple | rich | deep. NOT the person/meeting `recoil-report` plugin (that fetches profiles/git-telemetry for a counterpart) — this audits THIS conversation's own transcript.
---

# Thread Recoil (session belief-update ledger)

Audits the **current conversation** and emits a belief-update ledger: what priors were held at the
open, what they became at the close, and — for each shift — **the external data that forced it**.

> **Source of truth for the method:** ROM Primitive #6 (`_DECISIONS/ADR-078-exogenous-forge.md`).
> This skill is a *dogfood* of the Exogenous Forge: it only counts a belief as "revised" when the
> revision was forced by something **external to the agent's own coherence** (corpus, adversarial
> skeptic, external source, or the human as not-the-agent ground). A prior that changed because the
> agent re-convinced itself is not a recoil — it is drift, and is reported as such.

## Depth parameter (`$ARGUMENTS`)

Inverted pyramid — each level is a strict superset of the one before. Default: **rich**.

| Level    | Emits | Use when |
|----------|-------|----------|
| `simple` | **Headline** only: the thesis-level Open→Close one-liner + the proof stat (`N priors revised · X/N moved by external ground · 0 by internal re-coherence`). | A quick "did our beliefs actually move, and honestly?" |
| `rich`   | Headline **+ lede**: the enumerated `PRIOR → POSTERIOR` shifts, one line each, each tagged with its evidence type. No triggering detail. | The default session wrap — what changed, at a glance. |
| `deep`   | Headline + lede **+ body**: for every shift, the specific **external data** that forced the prior (the audit detail), with source/turn. Optionally renders the visual ledger artifact. | A defensible audit log / proof point to keep or share. |

## Method

1. **Recover the open.** State the hypothesis/prior posture the thread began with (what the agent
   believed or proposed before grounding). One sentence.
2. **Walk the transcript for genuine updates.** A row qualifies only if a belief actually *moved*.
   For each, record: `PRIOR` (struck), `POSTERIOR`, and the **triggering external data**.
3. **Tag the evidence** — the "what data changed the prior" — by type:
   `CORPUS-READ` · `CLAIMS-SKEPTIC` · `USER-CHALLENGE` (human = external ground) ·
   `RECURRENCE` (empirical record of the agent's own behavior over turns) · `EXTERNAL-SOURCE`.
4. **Compute the proof stat.** `N revised` · `X/N forced by external ground` · count moved by
   *internal re-coherence* (should be 0; any nonzero is a flagged drift, not a recoil).
5. **Emit at the requested depth.**

## Honesty guardrails (forge N-rules — non-negotiable)

- **No fabricated confidence numbers.** Show *direction* and the real triggering evidence; never invent
  probabilities or made-up magnitudes (N5: felt-precision ≠ real precision).
- **If no belief changed, say so.** An empty ledger is a valid, honest result. Do not manufacture
  updates to fill the vacuum (that is the disease this skill exists to catch — see
  [[external-artifact-eval-ground-and-skeptic-route]]).
- **Label the human as external ground explicitly.** A `USER-CHALLENGE` counts as exogenous, but the
  stat must not overclaim that repo/skeptic data did work the human actually did.
- **Cite, don't assert.** Every triggering datum names its source (a file, a skeptic finding, a source,
  a specific user turn). Uncited = not counted.

## deep mode — optional visual artifact

At `deep`, offer (or, if asked, render) the ledger as a self-contained HTML artifact. Visual spec: the
ARCS cockpit tokens (`#020408` ground, `#00F0FF`/`#00FF9D`/`#FFD700`/`#FF4D6D`), mono-forward, an
Open→Close band, a vertical timeline of updates each showing `PRIOR (struck) → POSTERIOR` + the tagged
triggering data, and the proof stat as the headline. Reference build: the 2026-07-22 belief-ledger
(session 547bb1c2). Load `artifact-design` before authoring.

## Relationship to `recoil-report`

Sibling, not replacement. `recoil-report` (plugin) profiles a **counterpart** for a meeting — it gathers
external profiles/git-telemetry about a person. `thread-recoil` audits **this session's own belief
motion**. Same ARCS "recoil" concept (open hypothesis → close belief-diff), different subject: *them* vs.
*this thread*.
