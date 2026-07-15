# ARCS as a Giga Network — The Alexandria Principles

**Epoch:** 2026-07-11 · **Artifact:** ARCS Alexandria rotunda (fire-test explorer) · **Parents:** Atomic Surface Map, Quiet Signals, meta-audit v1.5.0
**Thesis:** Alexandria burned because it was singular. A giga network (GIGI reading) inverts the library: every navigator carries a pocket Alexandria — a full, sovereign, local-first library in miniature — and the network is the inter-library loan system, never the vault. Burn any center and the library re-seeds from its edges.

## The five halls (principle → ARCS law → state)

| Hall | The law | Built | Partial | Gap |
|---|---|---|---|---|
| **Traceability** | Every scroll carries its own lineage: nothing enters without a receipt of where it came from | receiptId=trace_id, parentId lineage, NCI stamps, inchworm log | OTel proper (dep held for approval) | — |
| **Transparency** | The catalog of what is missing is shelved beside what exists | trust contract, in-product gap disclosure, honest NCI + self-grades, invariant grades, quiet-signals reporting | — | — |
| **Self-sovereignty** | Reading your own atlas never requires permission, an account, or a network | L1 anonymous + claim | L2 export-everywhere (specs export; receipts don't) | L3 local vault · L4 GIGI substrate |
| **Interoperability** | One canonical shape, many tongues: the Receipt grammar is the lingua franca | dewy-receipt-schema-v1, template {{params}} | Manifest Law specced (0 manifests), MCP surfaces | render-svc cross-compiler |
| **De/composability** | Compose up, decompose down, lose nothing; imports flow down, data flows up | 22 atoms · 16 molecules · 5 organisms · 10 doc patterns · 37 operators | — | tokens.json single source (3 sources unreconciled) |

## The fire test (the honest part)

The rotunda's 🔥 button burns the center. What the census shows:
- **Sovereign (survives):** everything git-tracked — canon, specs, operators, ADRs, ui kits, the lattice/backlog JSONs, inchworm log. Git is already the anti-fire: the corpus is a distributed-scroll library today.
- **Burns (single-copy today):** **user receipts** (Postgres only — no export path yet), **SageTrace**, **`~/.claude` memory shards** (machine-local; the `_MEMORY/` git shards were the right instinct — finish the move), and the **3 unreconciled token sources** (drift = slow fire).
- **Would-have-saved-them rungs:** L2 export-everywhere (Surface Map A4 — cheap, next), L3 local vault, L4 GIGI.

**The punchline the fire test is for:** the *product's* users currently have less sovereignty than the *project's* code. A visitor's receipts are the most burnable scrolls in the building. A4 (export .md/.json on every receipt and brief) is the single cheapest fix and it is already ranked.

## Sequencing (inherits all prior queues)

No new track. The Alexandria frame re-motivates existing ranked items: A4/L2 (export) → A1 (tokens.json) → A2 (manifests) → A3 (render-svc) → L3 vault ADR → L4 GIGI. Audit #01/#02 still first.
