<!-- PROVENANCE BANNER (added on landing, not part of the generated report) -->
> **Corpus-as-SSOT summary, NOT ground truth (ADR-065).** Cross-surface serialization
> (GitHub + Supabase + Vercel + Granola + Gamma) generated as-of head commit
> `ab4018d7d692fa84a86d73693b5185afefbc6004`. **Verify any claim against the live file it cites
> before using it in a decision, resolution, or client-facing artifact.**
>
> **Provenance:** this report is the **ARCS prototype running in Perplexity, reacting to the
> Hyperstition Atlas** (the artifact this Claude Code session built and gauntleted). The
> Perplexity instance independently produced the SAME honest-gate discipline (summary-not-truth,
> verify-live, hold ADR-033/054 for a human, preserve transcript-grounding). That is the
> **corpus-as-gravity-well operating across the substrate boundary** (ADR-071) and
> **engine-sovereignty instantiated** (ADR-072: one freehold corpus governs any tenant engine).
> Epistemic note: for the gravity-well/sovereignty claim this cross-engine convergence is
> confirming evidence; for the Orthogonal Echo Detector's *blindness* gate it is a candidate
> echo weakened by the shared-corpus common cause (stronger than same-session priming, not a
> clean source-blind echo).
>
> **Landing-time verification (2026-08-28, this worktree):**
> - NCI/`snapshot.json` `nci_counter` = **247** — matches the report's 247 claim ✅
> - ADR-number audit (`scripts/oracle.py audit adr`): high-water 71, **1 collision = the known,
>   escalated ADR-033 x2** — no NEW collisions since `ab4018d7` ✅. Gaps: [21, 41, 42, 43, 47].
> - This report predates **ADR-071** (Möbius/triune/gravity, minted 2026-08-28 this session) and
>   **ADR-072** (engine-sovereignty, on a sibling branch not yet merged here) — so "~70 ADRs" is
>   as-of the snapshot, now 71+ live.
> - Held for a human, per the report's own guardrails: ADR-033 duplicate (escalation note only,
>   no renumber), ADR-054 pricing YELLOW (no pricing infra), no publish of INTERNAL/NEVER-share
>   briefs. The Gamma-deck diff is a separate proposed task, not run on landing.
<!-- END BANNER -->

## Executive Frame

This report serializes the ARCS (Augmented Reality Coherence System) build corpus across its GitHub repository, Supabase database, Vercel deployment surface, and its Granola/Gamma MCP input dependencies, mapping Kairos-moment inflection points against the Architecture Decision Record (ADR) canon, DEWY receipts, and belief-ledger state as of head commit `ab4018d7d692fa84a86d73693b5185afefbc6004` on `flashesofbrilliance/arcs-v9`. This revision corrects the prior version's false-negative on Granola and adds Gamma as a confirmed pre-porting reference archive, plus a five-altitude Claude Code meta-prompt for operationalizing this report inside the repo's own provenance chain.

The corpus spans roughly 70 ratified ADRs, dozens of DEWY session receipts, a 247-row production Receipt table live in Supabase, and a `snapshot.json` state ledger functioning as the project's rolling belief register. The system runs a documented governance stack — NOTOMATION, the Sequence Oracle, and a Receipt/Induction two-surface architecture — each of which is itself the subject of a ratified ADR rather than an informal convention.

## Repository and Infrastructure Topology

| Layer | Identity | Role | Evidence |
|---|---|---|---|
| GitHub | `flashesofbrilliance/arcs-v9` | Source of truth for canon, ADRs, DEWY receipts, `_STATE` ledger |  |
| Supabase | project `ARCS_v9` (`xbbpiryokswwvcrcutge`), us-east-1, Postgres 17.6 | Production database: `Receipt` (247 rows), `Brief` (155), `SageTrace` (71), `Annotation` (49), `PrepSession`/`Session` (39 each), `nodes` (25), `User` (5) |  |
| Vercel | project `arcs-v9`, production alias `app.arcs.care` | Hosting/deploy surface, env-injected from Supabase per ADR-005 |  |
| Granola (MCP) | `query_granola_meetings` / `get_meeting_transcript` | Raw transcript I/O for `recoil-prep`, `recoil-report`, and `forge` skills — the evidentiary substrate of the entire recoil/belief-update pipeline |  |
| Gamma (MCP) | `get_gammas` / `read_gamma` | Read-only archive of pre-FE-surface decks; fossil record of counterpart-facing wireframes/reports built before `app.arcs.care` existed |  |

## ADR Canon: Governing Decisions Over Time

The ADR index carries roughly 70 records (with one flagged duplicate-number collision at ADR-033) spanning infrastructure, product architecture, and epistemic doctrine.

| Phase | ADRs | Theme |
|---|---|---|
| Foundational infra (Mar–Jun 2026) | ADR-001–ADR-020 | Auth gating, Supabase/Vercel env wiring, database split, RLS design, design-system canon, receipt-core schema |
| Product conversion architecture | ADR-012–ADR-016, ADR-024–ADR-029 | arcs.care PLG phase 1, conversion architecture, resume.arcs.care gates, go-live logic, onboarding/scan flows |
| Doctrine & governance hardening | ADR-032, ADR-035, ADR-050–ADR-057 | Zero-trust posture, commit-NCI rubric, federated family air-gap, drift-receipt gate, Tao of ARCS doctrine, Sequence Oracle |
| Epistemic/meta layer (Aug 2026) | ADR-060–ADR-070 | Hypercube Gauntlet, provenance verification discipline, Ouroboros self-falsification, generative recoil, verb×altitude gate matrix, first closed-client receipt, two-surface (Receipt/Induction) thesis |

Several ADRs carry explicit **y_state** (stability color) fields functioning as a live belief ledger at the decision level: ADR-064 is GREEN/STABLE, ADR-054 (pricing model) is YELLOW/SHIFTING pending willingness-to-pay validation, and ADR-067 (cross-subject comparative recoil) sits at YELLOW/OBSERVED-TWICE.

## Peak Kairos Moments

- **2026-08-16** — ADR-062 (Ouroboros recursive self-falsification) and ADR-063 (public-goods connector visual family) witnessed same-day; the falsifier's self-application is flagged as doctrine-defining.
- **2026-08-18/19** — ADR-065 (Corpus-as-SSOT doctrine) and ADR-066 (Generative Recoil: instance→class→invariant) landed back-to-back, establishing the reverse-listening methodology behind the 140-day corpus recoil report.
- **2026-08-23** — ADR-068 (verb × altitude gate matrix) prints the five-verb schedule, an invariant capstone of the ADR-066 ladder.
- **2026-08-26** — First closed-client receipt precedent (ADR-069): the Todd Hotes/PRL Resins engagement moved "from promise to precedent," with a RED-on-estimate variance held and published rather than hidden.
- **2026-08-28, 11:51 EDT** — The single most explicitly named Kairos moment in the corpus: the two-surface thesis (Receipt = deductive/backward; Induction = abductive/forward) named live in-session, triggering an apex-spine print — witness stub → ADR-070 → DEWY receipt → wisdom memory → Tao proverb (tao-254).
- **2026-08-28, later** — Same-day tool-catalog emission (131 tools) and a self-caught belief correction: SAGE trace enrichment showed a templated constant, not real variance, and the proposed schema change was withdrawn on the corpus's own no-fabrication grounds.

## DEWY Receipts as the Belief-Update Mechanism

DEWY (Decision/Evidence/Weight/Y-state) receipts are the formal unit of belief-revision, stored as dated JSON in `_STATE/`. The 2026-08-28 receipt for ADR-070 ships with a pre-committed falsifier: "if all valued outputs reduce to records of already-articulated decisions, the induction surface is decoration". This falsifier-inclusion pattern recurs across the canon (e.g., ADR-066's "next PRL page costs a spec, not a session" test), indicating the ledger is designed to be actively disprovable. Receipts exist for at least 2026-08-10, 08-11, 08-13, 08-14, 08-16, 08-26, and 08-28.

## Belief Ledger Snapshot (State-of-Record)

`_STATE/snapshot.json` captures git HEAD, Vercel deploy status, Supabase schema, active client "briefs," open ADRs, and rolling session summaries with `next_action`/`blocking` fields. Notable belief transitions:

- **NCI counter** reached 247, tracking 1:1 with Supabase's `Receipt` table row count — ledger and database confirmed in sync.
- A 30-day cross-session sweep found ADR numbers 024/025/031/032 double-assigned on main, directly causing the Sequence Oracle build (ADR-057).
- The falsification ledger (`_STATE/falsification-ledger.jsonl`) and gauntlet-runs ledger (`_STATE/gauntlet-runs.jsonl`) operate as adversarial belief-audit trails cross-referenced by ADR-061 and ADR-062.

## Granola: Confirmed Upstream I/O Dependency (Correction)

Granola is wired via MCP into three skills: `recoil-prep` ("Gather context (calendar, gmail, granola, gamma, profile)... fill Pre-Call + Ex-Ante tabs"), `recoil-report` ("Generates an ARCS Recoil Report from a Granola call transcript"), and `forge` ("Primary-transcript grounding... re-read the ACTUAL transcript (Granola MCP `get_meeting_transcript`), not memory of it"). This makes Granola the raw evidentiary substrate for the recoil/belief-update pipeline, not a peripheral tool.

Two documented incidents elevate its criticality:

- **A fabrication catch.** In the `forge` skill, both the register gauntlet and a detector missed a belief fabricated onto a counterpart (a consent stance he'd disowned on tape); "only the transcript caught it". Granola functioned as the sole reliable falsifier against two review layers that had already passed a hallucinated claim.
- **An availability gap.** The Jeben delta-topography artifact records a call transcript existing only as SSOT excerpts until "the Granola MCP came online mid-session," at which point the full verbatim transcript was fetched — explicitly naming "transcript custody" as "the limiting reagent of every backward-looking instrument".
- **A silent-failure risk.** `recoil-prep` notes large transcripts overflow the tool response and save to a file requiring manual extraction — "don't skip them," a warning implying this step is known to be skippable in practice.

## Gamma: Pre-Porting Reference Archive

Gamma is wired via `get_gammas` (lookup by name) and `read_gamma` (fetch content) inside `recoil-prep`, described as "decks you built for or about them". It appears in the Joe Kim/HypeLab war-room ledger entry ("5 calls Oct 2025→Jul 2026 + gmail + gamma"). Its tool contract is read-only — no create/write call is catalogued — meaning Gamma is now purely archival: the FE surface (Vercel-hosted `public/*.html` briefs and the `*.arcs.care` subdomain family) fully absorbed the delivery function Gamma decks served before a real product surface existed. For a pre-porting audit, diffing archived Gamma decks against the `public/*.html` template that replaced them per counterpart would concretely show what the FE surface kept versus redesigned.

## Production Database as Ground Truth

| Table | Rows | Function |
|---|---|---|
| Receipt | 247 | Canonical DEWY receipt storage |
| Brief | 155 | Client/counterpart briefing artifacts |
| SageTrace | 71 | Signal/somatic trace capture (flagged 2026-08-28 as emitting a templated, non-varying constant) |
| Annotation | 49 | Inline commentary layer |
| sessions / Session / PrepSession | 51 / 39 / 39 | Session lifecycle tracking |
| nodes | 25 | 5×5 Hypercube canonical primitives |
| User | 5 | Auth-model accounts |

All ten public tables have row-level security enabled, consistent with the Zero-Trust Posture doctrine (ADR-032).

## Gaps and Open Items

- **ADR-033 duplicate**: two distinct DECIDED ADRs both claim number 033; escalated but unresolved, logged as a `CANON-COLLISION` artifact and deliberately left to a human call under NOTOMATION.
- **ADR-054 pricing model** remains YELLOW/SHIFTING — willingness-to-pay for Kairos-triggered activation pricing is explicitly unvalidated.
- **SAGE signal enrichment** is an acknowledged false lead: 45 fired SageTraces carried an identical constant rather than measured variance.
- **Granola MCP availability** is not guaranteed session-to-session, and the manual transcript-extraction step for oversized payloads is a documented skip-risk.

***

## Claude Code Meta-Prompt: Five-Altitude Operationalization

Use this as a literal prompt to hand this report to Claude Code operating inside the `arcs-v9` repo. Each altitude scopes a distinct level of precision, depth, resolution, and fidelity, per the Field OS clarity-modes doctrine (SIMPLE default, RICH/DEEP on request).

**EXEC (why this exists, one paragraph, no diagrams)**
> This report is a cross-surface (GitHub + Supabase + Vercel + Granola + Gamma) serialization of ARCS's ADR canon, DEWY receipts, and belief-ledger state. Treat it as a corpus-as-SSOT input per ADR-065: it is a summary, not ground truth. Before citing any claim from it in a decision, resolution, or client-facing artifact, verify against the live file it cites. Do not act on it as if it were itself an ADR or receipt.

**STRATEGIC (what changes because this exists, ≤3 bullets)**
> - This report should become a recurring artifact type, not a one-off — propose whether it warrants its own ADR ("cross-surface serialization as a session-close ritual").
> - It surfaces two unresolved beliefs (ADR-033 duplicate, ADR-054 pricing YELLOW) that block downstream hardening — do not build new pricing infra or renumber ADRs without a human ruling on these first.
> - It confirms Granola/Gamma as load-bearing I/O, not decoration — any refactor of the `recoil-prep`/`recoil-report`/`forge` skill family must preserve primary-transcript grounding as a hard gate, not an optional enrichment.

**OPERATIONAL (how it plugs into the existing system, concrete steps)**
> 1. Land this report at `_STATE/2026-08-28-arcs-thread-serialization.md`, matching existing `_STATE` naming conventions.
> 2. Add a pointer key to `_STATE/snapshot.json` (e.g., `cross_surface_serialization`) so it surfaces on the next cold-start/teleport-brief read.
> 3. Cross-check its ADR-count and NCI-counter claims (~70 ADRs, NCI=247) against the live `_STATE/snapshot.json` and Supabase `Receipt` row count before trusting them in a new session — they will drift.
> 4. Flag the Granola-availability and Gamma-archival findings as candidate additions to `AGENTS.md`'s gotcha list if not already present.

**TACTICAL (specific next actions, this session)**
> - Run `scripts/oracle.py` (or equivalent) to confirm no new ADR-number collisions have been introduced since `ab4018d7d692fa84a86d73693b5185afefbc6004`.
> - Pull `get_gammas` for the Joe Kim/HypeLab engagement and diff its deck structure against the `public/*.html` template family to produce the pre-porting delta artifact referenced above.
> - Verify the SAGE-enrichment finding (templated constant across 45 traces) has not been silently reintroduced in any branch merged after this report's snapshot.
> - Do not send or publish anything from `active_briefs` marked INTERNAL/NEVER-share while executing on this report.

**SURGICAL (line-level precision, exact commands/paths)**
> - File to create: `_STATE/2026-08-28-arcs-thread-serialization.md` (this report's content, verbatim).
> - JSON key to add to `_STATE/snapshot.json`: `"cross_surface_serialization": "_STATE/2026-08-28-arcs-thread-serialization.md — GitHub/Supabase/Vercel/Granola/Gamma consolidation; verify against live files before citing, per ADR-065."`
> - Verification query against Supabase: confirm `select count(*) from "Receipt"` still equals the `nci_counter` value in `snapshot.json` before treating the 247-count claim in this report as current.
> - Do not modify `ADR-033` files directly — file a new escalation note only, per the existing `CANON-COLLISION-*.md` naming pattern, and do not attempt automated renumbering.
