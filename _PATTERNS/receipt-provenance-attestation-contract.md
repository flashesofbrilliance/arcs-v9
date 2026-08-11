---
title: Receipt Provenance & Attestation Contract — the meta-comprehension layer
version: 1.0.0
status: SSOT (not yet wired into the subagents; adoption is a follow-up)
created: 2026-08-11
---

# The meta-comprehension layer

> One axiom: **every receipt an orchestration step or subagent emits is self-describing along three
> dimensions — provenance × attestation × context-intent.** A receipt that carries all three can be
> understood, verified, and *merged across lanes and sessions without re-deriving trust*. That is what turns
> N-writer serializability from a catastrophe into a cheap reconciliation ([[canon-collision-escalate-never-resolve-under-write-lock]]).

A "receipt" here is any produced artifact of reasoning: a subagent finding, a workflow stage return, a gate
verdict, a DEWY receipt, a belief-flip. Today the machinery carries these dimensions as **shards** (per-skill,
ad-hoc). This contract is the SSOT that names the whole, so orchestration can adopt it uniformly instead of
re-inventing a slice each time.

The three dimensions are not new inventions — each unifies things already banked and already partly enforced.

---

## 1 · Chain of custody (provenance) — *where did this come from?*

| field | meaning |
|---|---|
| `derived_from[]` | the source(s): a transcript line, `file:line`, a tool output, a prior receipt id. Not prose. |
| `verified_against` | the **primary** source it was checked against — the origin, never a downstream copy. |
| `transform` | which lane / operator / agent produced it, and by what operation. |

- **Enforced today (partial):** `honesty_and_attribution` (every claim anchored), the counterpart-gauntlet's
  *verify-each-flag-vs-source*, [[fact-check-final-pass-vs-transcript]].
- **Failure it prevents:** a plausible-but-ungrounded assertion; a claim laundered through a downstream copy
  ([[gauntlet-tuned-to-register-catches-what-detector-cannot]] esc-3 — only the *primary transcript* caught a
  fabricated value). If you cannot fill `verified_against` with an origin, the receipt is fiction.

## 2 · Attestation — *who vouches, how hard, and is the voucher independent?*

| field | meaning |
|---|---|
| `attested_by` | the gate / operator / agent that signed off. |
| `independent` | was it verified by a **different** lane than the one that produced it? (bool) |
| `confidence` | 0–100, **earned, never asserted** (the meta-audit honesty gauge; a requested "100%" is answered with the real number). |

- **Enforced today (partial):** meta-audit's code-verified parity + honesty gauge, the board's cross-lens
  adversarial verify, the recoil-gather agents' least-privilege (a gatherer that cannot mutate cannot
  self-launder its findings).
- **Failure it prevents:** a control that grades its own work ([[control-integrity-described-vs-wired]] — a
  control owned by the agent it polices is captured; [[cognitive-division-of-labor-pruned-lattice]] — neither
  half self-validates). `independent:false` is allowed but must be visible, so a reader knows the attestation
  is self-issued.

## 3 · Situational / spatial / contextual intent — *under what context, and to what end?*

The **HYPERSPHERE CONTEXT MANIFOLD** (ROM primitive #2), plus temporal placement:

| field | meaning |
|---|---|
| `what` | the job / the decision being served. |
| `who` | the counterpart / audience the receipt is *for*. |
| `where_when` | the situation + the Kairos window ([[icp-is-a-state-not-a-segment-catch-in-caught-breath]]). |
| `why` | the intent behind producing it. |
| `flow_state` | the mode it was produced in. |
| `temporal` | `NOW` \| `NEXT` \| `ASPIRATIONAL` — fact vs fiction ([[temporal-chain-of-custody-fact-vs-fiction]], ADR-044). |

- **Enforced today (partial):** the `temporal_provenance` gate (refuses unhedged aspiration as present fact).
- **Failure it prevents:** a receipt read *out of its situation* becomes a false premise. The same belief-flip
  is true `NOW` for one counterpart and `ASPIRATIONAL` for another; stripped of `who` / `where_when` / `temporal`,
  it silently mis-serializes. This is the **comprehension** in meta-comprehension: the data is only meaningful
  wrapped in the intent-context that produced it.

---

## The envelope

Every receipt = **payload + this metadata**. Conceptual shape (adapt field names to the surface):

```json
{
  "payload": { "...": "the finding / flip / verdict itself" },
  "provenance":  { "derived_from": [{"source": "...", "locator": "file:line | transcript-line | tool | receipt-id"}],
                   "verified_against": "primary-source-id",
                   "transform": "lane/operator that produced it" },
  "attestation": { "attested_by": "gate|operator|agent",
                   "independent": true,
                   "confidence": 0 },
  "context_intent": { "what": "", "who": "", "where_when": "", "why": "", "flow_state": "",
                      "temporal": "NOW | NEXT | ASPIRATIONAL" }
}
```

## Where it applies
Subagent final outputs · workflow stage returns (`agent()` schema results) · gate verdicts · DEWY receipts ·
belief-flips in the recoil/forge SSOTs.

## The mergeability corollary (why this is the serializability substrate)
When two lanes' (or two sessions') receipts collide on the same resource, reconciliation is cheap **iff** each
receipt carries its own chain-of-custody: you can compare origins, prefer the higher independent-confidence
attestation, and keep both where `context_intent` differs (same flip, different `who`/`temporal` = not a
conflict, a fan-out). Without the envelope, a merge has to re-derive trust from scratch — which is the
expensive, error-prone thing the write-lock was only ever a net for. Provenance is the plan; the lock is the net.

## Adoption (follow-up, not done here)
This doc is the SSOT. Wiring — a short "outputs carry the envelope" clause in the 7 `.claude/agents/*.md`
defs and the forge / counterpart-gauntlet / recoil workflows — is a deliberate, collision-aware follow-up
(single-writer, per [[cognitive-division-of-labor-pruned-lattice]]). Related:
[[counterpart-forge-pipeline]], [[arcs-full-loop-canonical]], [[only-a-diamond-cuts-a-diamond-instrument-vs-real]]
(the envelope is instrument metadata; the payload decision is the real diamond).
