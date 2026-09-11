# _SEEDS — the ARCS seed bank (alias index + ledger)

**Status:** LIVE (draft) · opened 2026-08-13 · ARCS-private
**Anchors:** germinate `SPEC.md` (the open contract) · ADR-053 (dormant seed / vox animus) ·
[[seed-bank-germination-conditions]] · [[lab-mint-factory]] · this session's
`_STATE/2026-08-13-oss-family-conformance-standard.md`

> The alias index that points at each atomized public repo, plus the append-only ledger that tracks
> its conformance/drift over time. germinate is the *open* seed-bank implementation; **this** is the
> *private* ARCS registry that orchestrates the family and feeds the lab. The boundary holds: the
> repos are public, the registry that ranks and routes them is not.

## Files
- **`index.jsonl`** — the alias index. One row per seed (currently: one per atomized repo). Points to
  repo URL + local path; carries `role` (bank/node/utility), `tier` (A interop / B family),
  `conforms_to`, germination fields, and a `lab_candidate` hook. This is the "seed bank" the request
  asked for: an alias index over the atomized repos.
- **`ledger.jsonl`** — the parallel ledger. Append-only, one event per line (cataloged / audited /
  conformance-checked / drifted / germinated). Same discipline as `_CANON/tao-proverbs.jsonl` and the
  lattice-drift receipts (ADR-051: every check a receipt). Never rewrite a past line; append.

## Schema (minimal — accretes from real seeds; no top-down taxonomy)
`index.jsonl` row:
```
id · kind:seed · seed_type · alias · repo · local · role · tier · conforms_to · family
germination{soil,triggers,applications} · lab_candidate{status,note} · status · provenance
```
`ledger.jsonl` row:
```
ts · seed · event · tier · conformance · gaps[] · receipt
```

## Germination pathway (the forward vision)
```
_SEEDS bank (dormant repos)
   → ripeness judgment / Kairos (ADR-053/054, the vox animus)
   → experiment candidate (lab_candidate.status = "ripe")
   → /lab-mint → lab.arcs.care PLG mini-app   (the seed germinates in public soil)
   → harvest signal feeds back as a ledger event
```
A repo-seed with `lab_candidate.status: "ripe"` is a queued lab experiment. `arcs-field-scan`
(profile/PDF → energy scan) is the clearest first candidate — it's already a self-contained interactive.

## Boundary note (ADR-053)
`index.jsonl` and `ledger.jsonl` are ARCS-private (they encode priority/strategy/routing). A public
repo learns only its own one-line conformance badge — never this bank. Do not mirror this into any
public repo.
