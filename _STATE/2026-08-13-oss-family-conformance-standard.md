# OSS Family Conformance Standard — seed-to-harvest interop + family presentation

**Status:** STANDARD (draft) · 2026-08-13 · ARCS-private (rollout plan; the spec it points at is open)
**Grounded on:** germinate `SPEC.md` v0.1.0 (the open, RFC-2119 normative contract) ·
[[compaction-serialization-substrate-public-good]] · [[build-reusable-decomposable-interoperable-default]]

> The ask: *"if we're creating a web of interoperable microservices there has to be seed-to-harvest
> level conformity."* Right — but conformity is **two tiers**, not one. Some repos are **nodes in the
> seed web** (they move seeds/belief-logs/manifests and must interoperate); others are **family
> utilities** (they share the look and license but never touch a seed). Forcing interop conformance
> onto a toolbar-cleaner is the same over-build error as forcing a pricing ADR onto it. Cut honestly.

---

## The boundary (unchanged, carried from ADR-053)

- **The conformance *spec* is OPEN.** It already exists: germinate `SPEC.md` + `spec/` JSON Schemas +
  `conformance/` fixtures. Any repo declares conformance by satisfying it. No ARCS internals leak.
- **This *standard doc* is PRIVATE.** It is the ARCS rollout plan — which repos, which tier, what
  priority, the family strategy. It stays in arcs-v9. Public repos get only a conformance badge +
  adapter, never this file.

---

## Tier A — Interop conformance (the seed web)

A repo is a **node** if it *emits* or *consumes* any of germinate's canonical artifacts: a **seed**
(the seed schema), a **belief-log** (append-only JSONL of understanding), a **manifest** (surfaces +
sync state), or a **handoff** (head/tail compaction). Nodes MUST:

1. **Declare conformance** — `CONFORMS-TO: germinate SPEC vX.Y` in README + a machine-readable
   `conformance.json` (or equivalent) naming the artifacts it produces/consumes.
2. **Use germinate's schemas** — do not fork the seed/belief-log/manifest shape; depend on or vendor
   germinate's `spec/`. One service's *harvest* must validate as another's *seed*.
3. **Pass the shared fixtures** — germinate's `conformance/` valid/invalid cases for any artifact it
   handles (this is how germinate already verifies its own 4 runtimes).
4. **Ship an adapter** if it plugs a specific host (the `adapters/` pattern: claude-code, cursor, aider).

The verbs are the lifecycle contract: **seed → plant → water → germinate → sprout → grow → harvest.**
"seed-to-harvest conformity" = every node speaks these verbs over the same artifact schemas, so the
web composes end to end.

## Tier B — Family presentation conformance (the shared skeleton)

**Every** public repo (nodes and utilities alike) MUST share:
- **README skeleton** — one-line what · who-it's-for · install · usage · **family/ARCS relation** ·
  provenance line. (germinate's README is the reference voice.)
- **LICENSE** — MIT, present in-repo (not just the GitHub field).
- **description + tagline** — filled, in the family voice (no blanks).
- **topics** — a shared set for discoverability (e.g. `claude-code`, `agentic`, `arcs-family`, plus
  repo-specifics). All repos currently have **zero**.
- **ATTRIBUTION line** — one sentence: *"An open public good in the ARCS / flashesofbrilliance family;
  the animating spark stays private."* This is the ONLY place ADR-053 doctrine touches a public repo —
  one sentence, not a per-repo ADR.
- optional: `CHANGELOG.md`, `CONTRIBUTING.md`.

### Tier-B+ — ATG-FAQ coverage (README must answer the anticipated adopter questions)
A README passes only if a **cold reader** can answer these 5 ATG-anticipated questions *from the
README alone* (each scored ANSWERED / PARTIAL / MISSING):
1. **How do I use it?** — concrete install + first-run command from zero.
2. **Why different than ___?** — names a nearest alternative and why to pick this. *(Portfolio-wide
   weak axis: PARTIAL/MISSING on both POC repos — nobody names a rival. Highest-leverage adoption line.)*
3. **What problem does it solve?** — concrete pain, not abstract.
4. **Who is it for?** — explicit audience.
5. **How does it relate to the family / ARCS?** — placed in the ecosystem.

ATG may add repo-specific tributaries (e.g. field-scan: "is my data sent anywhere?" — a need-to-hear
question a privacy-conscious adopter has but won't ask). The eval is the reusable `readme-faq-eval`
(a cold-reader agent; seed `seed-readme-faq-eval` in `_SEEDS/index.jsonl`).
POC 2026-08-13: germinate 3/5, arcs-field-scan 1/5. Remaining 6 in progress.

---

## Per-repo audit

Hygiene columns are **verified live** (`gh api`, 2026-08-13). Tier assignment is **inferred from repo
description/purpose**, NOT from reading each repo's code — confirm by inspecting what artifacts each
actually emits before acting.

| repo | LICENSE | desc | topics | proposed tier | interop rationale (inferred) | gaps → fix |
|---|---|---|---|---|---|---|
| **germinate** | MIT | ✓ | 0 | **A (reference impl)** | Defines the spec; the bank + socket. | topics only |
| **state-sync-skill** | MIT | ✓ | 0 | **A** *(flag: fold?)* | Scaffolds `snapshot.json` = a *manifest/surface* — literally germinate's substrate. Overlap is real; fold-vs-standalone is its own decision (deferred). | declare conformance; reconcile schema w/ germinate; topics; attribution |
| **arcs-field-scan** | **NONE** | ✓ | 0 | **A (candidate)** | Profile/PDF → "ARCS energy scan" = a natural **seed emitter** (scan output could *be* a seed). | add MIT; make output conform to seed schema; README skeleton; topics; attribution |
| **arcs-claude-project-scaffold** | **NONE** | ✓ | 0 | **A (candidate)** | Scaffolds a Claude project = a natural **planter** (drops seeds into new soil). | add MIT; emit/accept seeds; README skeleton; topics; attribution |
| **rca-skill** | MIT | ✓ | 0 | **B** | Root-cause method; standalone. Could *optionally* emit a belief-log, but not required to be a node. | README skeleton; topics; attribution |
| **token-savings-bank** | MIT | **✗** | 0 | **B** | Budget-mode skill; no seed traffic. | **desc**; README skeleton; topics; attribution |
| **linkedin-connections-toolkit** | MIT | **✗** | 0 | **B** | Generic CSV parser; no seed traffic. | **desc**; README skeleton; topics; attribution |
| **fix-toolbar-comments-skill** | MIT | ✓ | 0 | **B** | Clears Vercel toolbar; pure utility. | README skeleton; topics; attribution |

**Excluded:** `flashesofbrilliance` (profile README — special), `blindsat` (private).

### Headline gaps
- **2 repos have NO in-repo LICENSE** (`arcs-field-scan`, `arcs-claude-project-scaffold`) — worst gap; both are also Tier-A candidates.
- **2 repos have blank descriptions** (`token-savings-bank`, `linkedin-connections-toolkit`).
- **All 8 have zero topics** — uniform discoverability miss, cheapest bulk fix.
- **Tier-A interop is aspirational for 3 of 4 nodes** — only germinate actually conforms today; state-sync/field-scan/scaffold would need real schema work, not just presentation.

---

## Rollout (phased; nothing public moves without owner authorization)

1. **DONE this session (read-only):** this standard + the audit. No public repo touched.
2. **Cheapest bulk win (gated):** Tier-B presentation pass on all 8 — README skeleton, the 2 missing
   LICENSEs, the 2 blank descriptions, shared topics, attribution line. One PR per repo, owner merges.
3. **Real interop (gated, larger):** Tier-A schema work — make state-sync/field-scan/scaffold actually
   emit/consume germinate-conformant seeds + declare conformance + pass fixtures. This is engineering,
   not cosmetics; scope each separately.
4. **Decide:** state-sync fold-into-germinate vs standalone (own decision, deferred).

## Open questions
- Is `state-sync` a germinate *module* or a peer node? (Affects whether it declares conformance or is absorbed.)
- Do the two `arcs-*` repos justify Tier-A schema work, or are they Tier-B for now and node-ified later?
- Should the family standard itself become an open repo (a `germinate-family` conformance profile) once proven — or stay a private rollout doc? (Boundary call: the *profile* could be open; the *priority/strategy* stays private.)
