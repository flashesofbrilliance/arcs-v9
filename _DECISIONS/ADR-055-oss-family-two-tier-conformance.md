# ADR-055 — OSS family: two-tier conformance + the private seed-bank registry

**Status:** Accepted · 2026-08-13

## Context
The public repos under `github.com/flashesofbrilliance` grew inconsistent (mixed READMEs, 2 with no
in-repo LICENSE, 2 blank descriptions, all with zero topics). The ask ([[oss-family-seedbank-two-tier-conformance]])
was "seed-to-harvest conformity" for a web of interoperable microservices. But forcing one uniform
bar over-builds: a toolbar-cleaner is not a seed-web node. germinate already supplies an open
conformance contract (`SPEC.md` + schemas + fixtures).

## Decision
Conformity is **two tiers**, anchored on germinate's open SPEC:

- **Tier A — interop (the seed web):** repos that emit/consume seeds · belief-logs · manifests ·
  handoffs. They declare conformance to germinate `SPEC vX.Y`, use its schemas, pass its
  `conformance/` fixtures, and speak the lifecycle verbs seed→…→harvest. Nodes: germinate (reference),
  state-sync, arcs-field-scan, arcs-claude-project-scaffold.
- **Tier B — family presentation:** ALL repos share README skeleton · MIT LICENSE · description ·
  topics · a one-line ARCS-family attribution.
- **Tier B+ — ATG-FAQ coverage:** a cold reader must answer the 5 ATG-anticipated questions
  (how-to-use · **why-different-than-X** · what-problem · who-for · how-relates) from the README alone.
- **The `_SEEDS` bank is the private registry:** `_SEEDS/index.jsonl` (alias index over the repos) +
  `_SEEDS/ledger.jsonl` (append-only conformance/drift receipts). germinate is the *open* seed-bank
  implementation; `_SEEDS/` is the *private* registry that ranks and routes the family.

## Consequences
- **Boundary (ADR-053):** repos public, the `_SEEDS` registry private. Never mirror `_SEEDS` into a public repo.
- Standard + audit: `_STATE/2026-08-13-oss-family-conformance-standard.md`. Pathway: bank → ripeness/Kairos → `/lab-mint` → lab.arcs.care.
- ATG-FAQ eval proved the portfolio-wide weak axis is **"why different than X"** (no repo names a rival) — a positioning/GTM gap, forked out.
- Enforced by the seed-bank inchworm (session-start drift-check; mirrors ADR-052) and the `/faq-eval` skill.

## Lineage
[[oss-family-seedbank-two-tier-conformance]] · ADR-053 · germinate `SPEC.md` · [[build-reusable-decomposable-interoperable-default]].
