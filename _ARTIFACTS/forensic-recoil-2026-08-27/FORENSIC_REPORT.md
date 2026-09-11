# ARCS Forensic-Recoil Sweep — Final Report

**Author:** SAGE-CONDUCTOR · **Date:** 2026-08-27 · **Method:** ARCS Folksonomist (bottom-up DBSCAN over pooled signals) → net-new ledger → skeptic adjudication vs live arcs-v9 canon.

---

## 1. BLUF

The sweep mined **190 decision-lineage records** across two primary source clusters (the `arcs-decision-receipts` live monorepo canon seed and the pre-v9 `A.R.C.S.` Phase 1–7 build lineage) plus eight satellite repos surfaced through cross-references. Bottom-up clustering coined **22 emergent folksonomy tags** and a **24-item net-new ledger**. When those candidates were held against the *live* arcs-v9 canon by the skeptic pass, the headline result inverted the intuition: **most of the "highest-value net-new" ROM candidates are already canon in arcs-v9** — Kintsugi (Primitive #6), Write-Lock (Primitive #7), the Time-Quality-Attribution ROM, the Court relief heuristic (RC-III-001), the Accumulation Protocol (part-v), and the Satoshi coherence-quantum are all present in the live repo, and the mining baseline that listed only five constitutional primitives was itself stale. The single **genuinely net-new, high-value recovery is the Norse pre-verbal witness stack** (Freyja→Odin→Tyr→Thor→Baldur→Ullr) living only in `arcs-care-local` — verified absent from arcs-v9 by a zero-hit grep — whose **Ullr graduation-invariant** ("retaining a fluent user is a NOTOMATION violation") and **Baldur non-instrumentalization no-go zones** are testable ROM candidates with no v9 equivalent. The net operational finding is therefore **canonization hygiene, not discovery**: number the de-facto axioms, consolidate divergent schema copies, and escalate three now-colliding constitutional vocabularies rather than mint a pile of "new" primitives that already exist.

---

## 2. Corpus Map

| Repo cluster | ROM | ADR | DEWY | WISDOM | WITNESS | exact-canon dupes |
|---|---:|---:|---:|---:|---:|---:|
| `arcs-decision-receipts` (live monorepo canon seed) | 6 | 20 | 5 | 12 | 0 | 0 |
| `A.R.C.S.` (pre-v9 Phase 1–7 lineage / ROM starter) | 6 | 7 | 11 | 6 | 0 | 0 |
| **Totals (primary clusters)** | **12** | **27** | **16** | **18** | **0** | **0** |

Satellite repos folded in via cross-reference (not separately counted above): `arcs` (live canon variant), `av9scrub` (scrub variant of live canon), `arcs-care-local` (Norse witness stack, PLG doctrine — sole home), `question-compass` (receipt_book), `germinate` (seed grammar / serializer), `arcs-mini`, `arcs_harmony_career_engine`, `arcs_cfa`, `arcs-memory-pipeline`, `arcs-app`. Scope excluded `node_modules/.next/.git` and nested stale app clones. **WITNESS count is 0 across the entire corpus** — no in-the-moment `/witness` stubs were mined; the witness *material* recovered (below) is reconstructed prose, not attested stubs.

---

## 3. Folksonomy (categorized backward) — the centerpiece

Twenty-two clusters, discovered from signal co-occurrence (≥3 members), tags coined bottom-up. Ranked by corpus share.

| # | Emergent tag | n | % | Description (compressed) | Promotion pattern |
|---|---|---:|---:|---|---|
| 1 | `phase-gate-sequencing-defer-until-threshold` | 10 | 5.3 | The dominant decision **grammar**: gate-before-branch. Don't promote a route/feature/migration until its enabling data model or usage threshold exists (`/brief/[id]` waits on BriefReceipt; SQLite→Postgres waits on >10K/day; Operator-20 cultivation waits on >50 receipts). | Canonize "defer-until-gate" as the *standard ADR shape*. This is the promotion rule itself, not one ADR. |
| 2 | `kintsugi-visible-repair` | 9 | 4.7 | A surfaced bias / repaired-on-false-premise receipt is a golden seam, not a failure. Repair is made **visible** (compression ratios, inferred/collision fields, `good_process_bad_luck`), decoupled from the Court, can audit offline. | **ALREADY CANON** (Primitive #6). Correct the stale 5-primitive baseline. |
| 3 | `receipt-schema-state-vector` | 9 | 4.7 | Receipt = state vector frozen at L0–L5 PASS: DEWY + Y-gate + NCI-by-lens + derived render_resolution + parent lineage. Only PASS gets full decomposition; HOLD/REJECT emit stubs. Machine JSON is the enforcement authority. | **CONSOLIDATION, not minting.** Pick one canonical `dewy-receipt-schema-v1.json`, write-lock per ADR-017, archive divergent copies. |
| 4 | `write-lock-irreversibility-declared` | 8 | 4.2 | One-way-door decisions require an explicit write-lock/Kairos-Lock **declaration** before commit — irreversibility is declared, not detected. Git non-fast-forward IS the physical write-lock for tracked files. | **ALREADY CANON** (Primitive #7) — but **VERIFIED-AS-PROSE ONLY**; no git hook enforces non-ff. Do not import the "git enforcement" claim as fact. |
| 5 | `time-quality-cadence-w-field` | 8 | 4.2 | Time is not neutral: every interval carries mode/quality/jurisdiction/reversibility (Chronos/Kairos/Drift/Shavasana). A well-formed question asked too early scores lower and can HOLD. | **ALREADY CANON** — same `time-quality-attribution-rom.json` lives in live arcs-v9. Gap is a *missing ADR number*, not new content. |
| 6 | `norse-preverbal-witness-canon` | 8 | 4.2 | Complete mythologized pipeline (Freyja→Odin→Tyr→Thor→Baldur→Ullr) living **only** in `arcs-care-local`: catch pre-verbal somatic signal → name without collapsing → constraint court → strike at Kairos-Lock → protect non-instrumentalizable fields → mastery = instrument disappears. | **GENUINELY NET-NEW** (grep-confirmed absent). Lift Ullr graduation-invariant + Baldur no-go zones as ROM candidates against NOTOMATION. |
| 7 | `constitutional-court-relief-and-disguise` | 8 | 4.2 | Two Court diagnostics: (1) **relief heuristic** — if a verdict would feel like relief not information, you've been deferring into Court territory; (2) **irreversibility-disguise** — a "be thorough" path hiding a ruin-level one-way door must STOP. | RC-III-001 relief is **ALREADY CANON** (part-iii, verbatim). Disguise-rule + Shared-Court extension are the live edges. |
| 8 | `notomation-anti-dopamine-corridor` | 7 | 3.7 | NOTOMATION as enforced ceiling: gates HALT never decide; product expression is "corridor not casino" (no gate before value, no guilt mechanics, clean exit). | NOTOMATION is canon; the six PLG hard-rules are net-new *enforcement surface* — fold in as the NOTOMATION product contract. |
| 9 | `rom-axiom-genome-l0-l7` | 7 | 3.7 | **Three competing constitutional vocabularies**: 5 primitives (AGENTS.md) vs 6 execution laws (rom.md) vs 7 epistemic axioms (book-ii). | **CANON COLLISION — escalate, do not silently resolve.** Run CANON_COLLISION to map the three onto one authoritative set. |
| 10 | `prod-deploy-silent-failure-forensics` | 7 | 3.7 | "Green build ≠ working DB": PrismaPg SSL against the pooler fails silently; Auth.js swallows schema-gap errors; Vercel build-log first line diagnoses stale deploys. Verify with a real `$queryRaw`. | No ADR needed — dedupe into the canonical `_PATTERNS/durable-gotchas.md`; wire each finding as a pre-deploy check. |
| 11 | `arcs-care-plg-founding-ten` | 7 | 3.7 | arcs.care serves warm founding-10 referrals, not cold PLG; prioritize email capture + case-study receipt + COCD loop. Category = "Field OS beneath decisions." | **Conditional** — per user CLAUDE.md these are built but not currently reachable (domain consolidation). Durable net-new is the Field-OS positioning + COCD frame; port to arcs-v9. |
| 12 | `determinism-processor-not-controller` | 7 | 3.7 | Engineering ethic across satellites: deterministic-first, missing=neutral(0), ARCS is a **processor not a controller** (no key custody, BYO creds per-request); six mechanism-bound principles. | Engine-sovereignty governance (ADR-067). Mint as the data-governance contract gating any GIGI/substrate wiring at the compass seam. |
| 13 | `seed-bank-germination-dormancy` | 6 | 3.2 | germinate botanical grammar: seven-verb lifecycle where harvest mints new seeds (bank compounds). Dormancy is first-class, not staleness. Belief-log flags confidence-climbing-while-risk-flat as unearned optimism. | Adopt germinate's dormancy + activation-contract vocabulary as canon; the confidence-vs-risk divergence lint is a directly wirable anti-sycophancy gate. |
| 14 | `triune-logic-null-om-undefined` | 5 | 2.6 | Three-valued epistemic kernel: NULL (looked, found nothing) vs OM (present, resolved) vs UNDEFINED (not yet evaluated); never collapse UNDEFINED→NULL. Not-legible is a valid high-status state. | Parent of the Y-gate enum + HOLD/REJECT gate. Canonize as the epistemic foundation in part-ii; make the Y-gate enum cite it. |
| 15 | `folksonomy-operator20-cultivation` | 5 | 2.6 | The categorization machinery itself (Operator-20 DBSCAN — this run's method). Surfaces a **DEWY naming collision**: v9 decision state-vector vs arcs-memory-pipeline tagging macro. | Escalate + disambiguate/rename the tagging macro. Corpus gate (>50 receipts) is met at 190. |
| 16 | `design-color-as-grammar-earned-fidelity` | 5 | 2.6 | Color IS meaning; never render more certainty than data deserves (earned fidelity); gradient buttons = AI-slop tripwire. | Mostly variant-in-canon. Net-new: the explicit "color is grammar" law + no-gradient rule → fold into FieldOS DS (project be620c0c). |
| 17 | `receipts-as-substrate-and-proof` | 5 | 2.6 | Receipts are the product **substrate** not a feature; proof not testimonials. Accumulation protocol treats each receipt as an open hypothesis (pending/live) with a close-time verification gate (anti-fossilization). | **ALREADY CANON** (part-v is live). The pending/live receipt-as-hypothesis mechanism is the anti-fossilization tool the drift-receipt loop (ADR-051/052) needs — wire the state into the schema. |
| 18 | `wisdom-lattice-stoic-hud-munger` | 4 | 2.1 | Field-os wisdom layer: the emotional dimension Munger omitted — Tolma / Prosopon-gap / Loki-sensitivity gauges; Circle of Competence extended **inward** against self-erasure. | High-value WISDOM outside v9 canon (all 2026-05-11 origin epoch). Land as _CANON wisdom; gauges are candidate instrument-board dimensions. |
| 19 | `two-surface-architect-implementor-sync` | 4 | 2.1 | Zero-infra stateful sync: `_STATE/snapshot.json` on main + raw.githubusercontent handoff; two-gate authoring path for canon commits. | De-facto canon (this session runs on it). Dedupe the two protocol copies; make the two-gate path the documented gate for `_CANON/` commits. |
| 20 | `tribune-annotation-layer` | 3 | 1.6 | Three-phase Anterior/Proactive/Posterior annotation wrapping the sealed receipt (ADR-020). av9scrub copy preserves pre-collision BAR/KKL naming. | ALREADY ADR-020. Net-new detail = av9scrub's pre-collision naming as forensic provenance; archive in the enforcement-parity ledger (ADR-033). |
| 21 | `folksonomy-operator20 residue` (singletons) | — | — | 10 residue items (ATG, Operator-17 adversary, ANTI-SIGNAL-VI, lose-the-room detectors, sage_bridge five-instruments, apex forensic DEWY, synthetic operator-20, PLG flywheel, skills posture, Loki Mischief) — each sub-tagged by unclear axis (who/when/why/where/what). | Hold as residue; the synthetic operator-20 example is explicitly fictional — **excluded from promotion** (receipts-as-proof rule). |

*(Cluster count in `folksonomy.json` is 22; rows 1–20 above are the full-member clusters, row 21 summarizes the residue bucket.)*

---

## 4. Verified Net-New Promotion List

Only skeptic-**confirmed** `NET_NEW` and high-value `VARIANT` items appear here, ranked by value. Everything the skeptic returned as `ALREADY_CANON` is dropped (see rejected line).

### P1 — NET-NEW (confirmed absent from live arcs-v9)

**Norse pre-verbal witness stack — Ullr graduation-invariant + Baldur non-instrumentalization no-go zones**
- **Type:** ROM (two candidate axioms)
- **Ref:** `arcs-care-local:02-canon/V9-PROSE-003-ullr-graduation-invariant` + `01-brand/MYTHOLOGY-002-baldur` (+ Freyja/Odin/Tyr/Thor supporting arc)
- **Folksonomy tag:** `norse-preverbal-witness-canon` (with `notomation-anti-dopamine-corridor`)
- **Lives in:** `arcs-care-local` only (grep for freyja/ullr/baldur/graduation-invariant/pre-verbal-witness across arcs-v9 = **zero hits**; odin/thor hits were substring false positives).
- **What it adds:** Operationalizes two already-constitutional primitives (NOTOMATION, the WITNESS section of WORLD.md) with a concrete pre-verbal→strike arc and *named no-go zones*. **Ullr:** mastery = the instrument disappears; retaining a fluent user is a NOTOMATION violation (graduation ≠ churn) — a distinct, testable rule. **Baldur:** grief/intimacy/trust must not be instrumentalized; pause into witness mode. WORLD.md's WITNESS section covers in-the-moment timing only, not a graduation invariant.
- **Target home:** Draft both as **ROM CANDIDATES against ROM Primitive 1 (NOTOMATION)** in `runtime/specs/ARCS-v9-ROM.md`, each with a falsifiable test (e.g. detect sessions where a user demonstrates fluency yet is re-onboarded). Land the **Witness Receipt template** as a canonical receipt type next to `_STATE/witness/*.jsonl`. Norse naming optional — the invariant is the substance.

### P2 — high-value VARIANT (confirmed, with caveat)

**Control-integrity: advisors-are-foreign / don't-grade-your-own-homework**
- **Type:** ROM (governance motion-rule)
- **Ref:** `arcs-mini:PREFECTURES.md advisors-are-foreign`
- **Folksonomy tag:** `constitutional-court-relief-and-disguise` (with `determinism-processor-not-controller`)
- **Lives in:** `arcs-mini` (single home).
- **What it adds:** A pithier statement of the existing control-integrity invariant (memory: `control-integrity-described-vs-wired.md`) — a control owned by the agent it polices is captured; verifying advisors must come from a different prefecture; Court seals, lords propose. **Caveat (skeptic):** this is a *weaker restatement* of an invariant arcs-v9 already holds, and like the canon version it is **described-not-wired**. Value is the crisp framing and its direct wirability as a **gauntlet constraint**, not new doctrine.
- **Target home:** Fold the phrasing into the control-integrity memory node and encode as an explicit constraint in the counterpart-gauntlet workflow (verifier facets must be foreign to the artifact's author).

### Rejected as ALREADY_CANON (skeptic-confirmed present in live arcs-v9, promotion = number/consolidate, not mint)
Kintsugi Immune System (ROM #6, `arcs-canon.md` L74 / part-ii Axiom V) · Write-Lock / Irreversibility-Declared (ROM #7, L75 / Axiom VII — **prose-only, no git enforcement**) · `time-quality-attribution-rom.json` (present in live runtime/specs; the "four copies" are one repo's worktrees) · RC-III-001 relief heuristic (part-iii, verbatim; av9scrub is a redundant scrub) · Accumulation Protocol / receipt-as-hypothesis (part-v, live, CANONICAL v1.0.0) · Satoshi coherence-quantum (LOCKED in `operators/arcs_rom.py` SATOSHI_CRITERIA). The mining baseline (CANON_INDEX line 7) under-counts primitives at five when live canon carries seven — **fix the baseline**.

> **Un-adjudicated high-value candidates (need a skeptic pass before promotion):** the ledger's ranks 7, 8, 12, 14, 15, 16 (Accumulation pending/live wiring, processor-not-controller engine contract, Stoic HUD gauges, Triune-Logic kernel numbering, **Shared Court part-vi** multi-agent extension, neurological-rescue origin framing) were clustered and ledgered but not individually verified against live canon. Given part-v was already canon, **part-vi (Shared Court) must be checked in the live repo before minting.** Do not treat these as confirmed net-new.

---

## 5. Witness & Wisdom Recoveries

**No attested WITNESS stubs exist in the corpus (count = 0).** The following are reconstructed-prose moments worth **re-attesting live** via `/witness` (per WORLD.md: attest in the moment, never dress reconstruction as witness):

- **"A surfaced bias is a receipt, not a failure."** (`arcs-decision-receipts:field-os/artifacts/06-kintsugi-immune-system.md`) — the full bias/drift failure taxonomy (midcurving, authority deference, commitment bias). The generative naming behind ROM #6.
- **Gyroscope-over-switcher** (`A.R.C.S.:HANDOFF.md`) — the naming moment: a manual mode-switcher is the wrong architecture; a gyroscope that auto-detects behind the scenes (human override wins) is right. The seed that became the Kairos operator-as-stub.
- **Neurological-rescue origin insight** (`arcs-decision-receipts:field-os/origins/arcs-thread-master-report.md`) — a 20-apps-in-30-min sprint is ~40 dopamine hits breaking a freeze/analysis-paralysis state, not a productivity hack. The human-physics "why" beneath the whole product; carries falsifiable claims.
- **Feature litmus test** (`A.R.C.S.:ARCS_v9_Meta_Audit.md`) — non-fiction + attainable(≤10 min) + low-key-brilliant; fail any → demote to LAB. A reusable, cheap feature-admission gate that prevents lore-creep.

**Distilled WISDOM worth landing in `_CANON`:**
- **Stoic HUD** (Tolma / Prosopon-gap / Loki-sensitivity) + the **inward** Circle-of-Competence extension — the emotional-competence dimension Munger omitted, mapping onto the five-derivative instrument model in `arcs-app:sage_bridge`.
- **Coal→diamond session compaction** + the **trace-elements-of-conviction lint** (confidence climbing while risk stays flat = unearned optimism) — a directly wirable anti-sycophancy gate.
- **Triune Logic NULL/OM/UNDEFINED** — canonize as the epistemic parent of the Y-gate enum; not-yet-legible is a valid high-status output.

---

## 6. Next Moves (ordered)

1. **Fix the stale baseline first.** Update `CANON_INDEX.md` (line 7) to list **seven** constitutional primitives, not five. Half the "net-new ROM" noise in this sweep traces to that under-count.
2. **Promote the one confirmed net-new:** draft Ullr (graduation-invariant) and Baldur (non-instrumentalization) as ROM CANDIDATES against NOTOMATION in `runtime/specs/ARCS-v9-ROM.md`, each with a falsifiable test; land the Witness Receipt template beside `_STATE/witness/*.jsonl`.
3. **Escalate the canon collision** (`rom-axiom-genome-l0-l7`): three constitutional vocabularies (5 primitives / 6 execution laws / 7 epistemic axioms) are live simultaneously. Run the CANON_COLLISION protocol to declare one authoritative set — do not silently resolve under write-lock.
4. **Consolidate, don't mint:** pick one canonical `dewy-receipt-schema-v1.json`, write-lock per ADR-017, archive divergent av9scrub/arcs copies. Same for the two `two-surface-protocol.md` copies and the two prod-failure post-mortems.
5. **Number the un-numbered:** mint ADRs for the Time-Quality-Attribution ROM (Axiom III) and the Accumulation Protocol so machine-authoritative specs stop floating without ADR references. Wire the pending/live receipt-hypothesis state into the schema (the anti-fossilization mechanism ADR-051/052 needs).
6. **Skeptic-verify the un-adjudicated set** before any further promotion — priority: **Shared Court (part-vi)** must be grepped against live canon (part-v was already there); then Stoic HUD, processor-not-controller, Triune-Logic numbering.
7. **Disambiguate the DEWY collision:** rename the arcs-memory-pipeline tagging macro (e.g. DEWEY-TAG) so it stops colliding with the DEWY decision state-vector.
8. **Correct the record:** Write-Lock is **VERIFIED-AS-PROSE only** — flag in canon that no git hook enforces non-fast-forward; do not propagate the germinate "git-is-the-serializer enforcement" claim as implemented fact.

---

## 7. VERIFIED CORRECTIONS (post-skeptic pass, 2026-08-27) — supersedes §3–§6 where they conflict

A second skeptic pass over the un-adjudicated set corrected the auto-generated report above. Trust this section over the earlier ones where they disagree.

- **Stoic HUD is ALREADY_CANON, not net-new wisdom.** §5 listed it as "WISDOM outside v9 canon" — wrong. It is a verbatim field-os artifact live at `runtime/specs/field-os/artifacts/02-stoic-hud-tolma-prosopon-loki.md` (subtitle "the emotional dimension Munger left out"). Drop from wisdom recoveries.
- **Shared Court (part-vi) is CANONICAL v1.0.0** (`_CANON/book-ii/part-vi-the-shared-court.md`, in `_CANON/index.md`). Not net-new.
- **Second confirmed NET_NEW recovered:** the **processor-not-controller engine contract** (deterministic-first · missing = neutral(0) · no key custody / BYO-creds-per-request). Zero trace in live repo. **Trap:** its stated anchor "ADR-067 = engine-sovereignty" is a *stale global-memory* claim — the repo's actual `_DECISIONS/ADR-067` is "cross-subject comparative recoil." ⇒ Global MEMORY.md and repo canon disagree on what ADR-067 *is*. Home the engine contract as a NEW ADR (not 067); reconcile the global-memory ADR-067 mapping separately.
- **Triune-Logic is canon; the "parent-of-the-Y-gate-enum" framing is NOT.** `src/lib/ygate.ts:5` declares the Y-gate enum's parent as `dewy-receipt-schema-v1.json`, not Triune Logic. Canon applies Triune per-DEWY-dimension — a different axis. Do not canonize the parentage claim.
- **Count-collision citations fixed** (see `_DECISIONS/CANON-COLLISION-rom-vocabulary.md` for the authoritative map): the 5-list is in **CLAUDE.md** (not AGENTS.md); the 6-list is **`runtime/specs/ARCS-v9-ROM.md`** (the report's `_CANON/living/rom.md` **does not exist**); the authoritative **7 primitives** live in **`.claude/arcs-canon.md:65–75`** (Kintsugi #6, Write-Lock #7 confirmed); part-ii holds 7 *axioms* (I–VII), a different list. "5→7 stale baseline" is TRUE — CLAUDE.md was a truncation, **de-rotted 2026-08-27**.

### Actions taken this session (not just recommended)
- ✅ CLAUDE.md de-rotted 5→7 primitives (aligned to `.claude/arcs-canon.md`).
- ✅ Norse ROM candidates drafted (PROPOSED, not ratified): `runtime/specs/ROM-CANDIDATES-norse-witness.md`.
- ✅ Canon-collision escalation filed (human-owned ruling): `_DECISIONS/CANON-COLLISION-rom-vocabulary.md`.
- ⏳ Not done (need your call): home the processor-not-controller contract as a new ADR; reconcile the global-memory ADR-067 mismatch; ratification of the Norse candidates (blocked on the collision ruling + one live receipt each).
