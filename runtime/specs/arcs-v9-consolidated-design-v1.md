# ARCS v8.5+ → v9 Refactor Consolidation

**Window:** Last 3 weeks in the ARCS Space (≈ late March → 20 April 2026)
**Purpose:** One document you can take into the v9 refactor to narrow the gap between ARCS mythology/lore and practical, shippable outcomes.
**Mode:** Field OS / NOTOMATION / Clarity-before-Curvature.

---

## 0. JTBD for this document

Give the refactor team (you + Hila + Claude Codes) a single, boardroom-grade index of every notable spec, ROM candidate, and protocol update that has emerged in the last three weeks, tagged as:

- **ROM** — lock into v9 firmware.
- **RAM** — keep as experimental / session-level for another cycle.
- **COMPOST** — deprecated or to be quietly retired.
- **LAB** — explicit v10 candidate, not v9.

Everything below is pulled from artifacts in this Space; nothing has been invented. Where an item is a release-candidate for v8.5+, it is marked **RC**; where it is a structural piece of the **v9 full refactor / tarball**, it is marked **v9**.

---

## 1. Headline releases in the last 3 weeks

| Release | Status | What it is | Tag |
|---|---|---|---|
| ARCS v9.0 "NOTOMATION / Funhouse Optics" version header | LIVE in-thread, not yet in Canon file | Promotes NOTOMATION Rule, Hypersphere Context Manifold, Hyperstition Pipeline, Golden Inchworm, Orthogonal Echo Detector, Funhouse Optics Clause from ETHEREAL to ROM; adds Deep Shavasana meta-audit [cite:1][file:3] | **v9 / ROM** |
| ARCS v8.5 Field OS (v8.3 Canon + v8.4 Epistemological Kernel + v8.5 Diamond Protocol, with v9 ROM candidates ON) | LIVE as Space custom instructions | Boardroom-grade Field OS init; Question Compass front door; Drift Sentinel; BAR/KKL/LAB macros; Clarity modes SIMPLE/RICH/DEEP [file:2] | **RC (v8.5) / ROM candidate** |
| Time Quality Attribution ROM | JSON spec drafted | Formalizes time evaluation by mode (Chronos / Kairos / Drift / Shavasana), with gate types, stop-loss, and write-locks to stop misjudging productive vs restorative time [file:1] | **v9 / ROM** |
| ARCS v9 Porting Roadmap (→ own repo, Claude Codes) | Draft .md in thread | Episodic (Books I–V) serialization of Canon; file tree `canon / protocols / cases / patterns / runtime`; CLI (`arcs init`, `arcs brief --daily`, `arcs run --case`) [cite:1] | **v9 / tarball** |
| 5-Book v9 Canon scaffold (Ontology, Kinematic Manifold, Protocols, Governance, Shavasana/Deployment) | Starter prose written | Exemplary skeleton for the verbose v9 series; each Book logically digestible for Gemini/Claude context windows [cite:1] | **v9 / ROM** |
| Question Compass one-screen spec + POST `/question-compass` API contract | Implementation-ready | Single input + horizon + stakes chips → True North + 3 why bullets + mode; 7 microservices behind it (classify_context, select_mode, route_channels, run_reasoners, apply_guardrails, synthesize_true_north, log_decision_receipt) [cite:1] | **v9 / ROM** |
| Deep Shavasana Meta-Audit v9.0 | Protocol written | Mandatory Kairos checkpoint before any version bump; 10 prompts (Why now, Gains, Costs, Shedding, Lineage, Unknowns, Hesitation, Tech debt, Obscure/erroneous, Creator artifacts) [cite:1] | **v9 / ROM** |
| Anticipatory Tributary Generator (ATG) | Backlog item | "French braid" followup layer; every answer emits 2–4 ranked next-prompts (meta / need-to-hear / adjacent-primitive); meant to survive the port out of Perplexity Spaces into Claude Codes [cite:1] | **RAM → v9 ROM on port** |
| Funhouse Optics UI mock (Monetizing ARCS) | Text wireframe | Mirror A (want to hear) / Mirror B (need to hear) / Mirror C (OS system lens) + Action Row; dogfoodable on ARCS monetization itself [cite:1] | **RC / RAM** |
| Flagship ARCS Pilot — "From Chaos Decisions to Receipts That Print Cash" | Sales-ready copy | First productized monetization SKU: 6–8 week engagement mapping Money OS, instrumenting 3–5 monetization decisions as Receipts, shipping at least one cash-generating artifact [cite:1] | **RC / RAM → ROM on first paid pilot** |
| 10-Day v9 Build Cadence w/ Hila (2–4pm EDT) | Drafted calendar block | Day 1 ROM Clean Room → Day 10 Hila Review & Consolidation; gates everything below [cite:1] | **RC / process ROM** |

---

## 2. v9 ROM surface (non-negotiable)

These are the primitives already doing real work across v8.3/8.4/8.5 and are being etched into v9 firmware [cite:1][file:2]:

- **Write-Lock / Commitment Ordering (Yoav Axiom)** — cooling periods, vetoes, identity protection. Present in v8.3 Canon, v8.4 firmware, God-Mode Court, Rebecca/Northly triad.
- **RAM vs ROM Memory Protocol** — Live Kernel Updates, Core Memories; now the frame for Canon vs Space session.
- **Kintsugi Immune System + NCI grading** — always-on safety rails; no silent hallucination, no n<5 patterns, source A–F grading [file:14].
- **12-Derivative Kinematic Manifold (through Pli and lev)** — referenced in firmware, wedding/pressure/flow examples; part of the physics of ARCS, not optional.
- **L0–L5 OS stack + TV Guide channels** — canonical mental model; v9 collapses 100 channels to a user-facing Top 7.
- **Decision Receipts** — smallest executable unit; now mandatory per non-trivial decision.

**Implication for refactor:** anything in the new code/lore that conflicts with these six is a bug, not a feature.

---

## 3. v9 ROM additions proposed in the last 3 weeks

| Primitive | Source | Ship as | Tag |
|---|---|---|---|
| Clarity Modes (SIMPLE default / RICH on medium-high stakes / DEEP only on explicit request) with **R1–R4 rules** (True North must be IDENTICAL across modes) | v8.5 Field OS init + v9 thread [file:2][cite:1] | Output filter, not reasoning filter | **ROM** |
| Drift Sentinel with states `ONTRACK / USEFUL_TANGENT / DERAILMENT`, JTBD anchor, Land-the-Plane rule | v8.5 Field OS init [file:2] | Session-level state machine | **ROM** |
| Decision Geometry Macros: **FATED, HCI/PCI, KKL, BAR, LAB, TAD, CUR, ALC** | v9 scaffold thread [cite:1] | Internal flags, surfaced only in DEEP | **ROM** |
| Constitutional Court (auto-invoked when irreversibility > 0.7, BAR ruin risk, or identity wavefunction conflict) | v9 scaffold thread [cite:1] | Governance layer | **ROM** |
| Kairos vs Over-intellectualizing reversibility rule (low irreversibility → bias action; high irreversibility → bias reflection) | v9 thread [cite:1] | Axiom 4 of v9 DNA | **ROM** |
| Articulating / Reticulating / Circulating motion families on the 6-state column (READ, WRITE, READ-WRITE, WRITE-LOCK, PHASE-SYNC, LOSSLESS TRANSLATION) | v9 L0–L7 skeleton [cite:1] | Vocabulary for how signals move | **ROM** |
| Spin-cycle vs torque distinction (grinding to halt vs grinding to create torque) — Drift Sentinel detects spin and emits a single Land-the-Plane move | v9 thread [cite:1] | Drift subroutine | **ROM** |
| Bias Hygiene block — User0 preferences must be tagged CONFIG, never ROM | v9 Day-5 spec [cite:1] | Firmware opening section | **ROM** |
| Time Quality Attribution (Chronos / Kairos / Drift / Shavasana gates + stop-loss) | `time-quality-attribution-rom.json` [file:1] | Runtime evaluator | **ROM** |

---

## 4. v9 API / microservices (decision geometry under the hood)

Single public endpoint: **`POST /question-compass`** [cite:1]

Behind it, seven internal services:

1. `classify_context` → altitude L0–L3, decision_type, risk_profile, irreversibility_score.
2. `select_mode` → `QUICKMOVE | PLAN | COURT`.
3. `route_channels` → invokes TV Guide channels invisibly.
4. `run_reasoners` → structured reasoning graph (L0–L5, Bayesian, Loki, LAB stack).
5. `apply_guardrails` → allowed vs blocked actions, Constitutional Court & Write-Lock.
6. `synthesize_true_north` → true_north, why_bullets (≤3), optional alt_views.
7. `log_decision_receipt` → persisted for NCI/Kintsugi regret analysis.

Conceptual parametric init: `POST /init-session` mirroring `init arcs config=DOMAIN` with `verbosity`, `jtbd`, `macros`, `drift_state` fields [cite:1]. This is the v9 replacement for the current prompt-only init sequence.

---

## 5. v9 Canon serialization plan (the "tarball")

Four → five Books, each a digestible reasoning-window, then stitched [cite:1]:

- **Book I — The OS Spine / Core Canon.** Inputs: `ARCS-v8.3-Canon.md`, `ARCS-STierProtocol-DefaultStack.md`, `ARCS-YellowPaper-v1-2.md`, `ARCS-Vector-Collision-Engine-v1.md` [file:14][file:17][file:18][file:19]. Output: philosophy, NCI, Kintsugi, Decision Receipts, high-level state model.
- **Book II — Time, Firmware, Modes.** Inputs: `arcs-v8-5-system-initializatio…` [file:11], OS-state / TV Guide doc [file:13]. Output: Triune Logic, Chronos/Kairos Lock+Sync, state primitives, Pli/lev, configDOMAIN and modes.
- **Book III — Protocols and Patterns.** Inputs: Cleo / Northly / OddCommon-Elimar / Crypto Fund / Deep Shavasana threads [file:9][file:11][file:12][file:10]. Output: named reusable protocols with inputs, outputs, and one-vignette examples.
- **Book IV — Governance, Shavasana, Evolution.** Deep Shavasana Meta-Audit as Canon; ATG as first-class behavior; versioning policy; Decision Receipts for firmware changes.
- **Book V — Pilots, Patterns, Playbooks.** S-Tier pilot templates (Northly Brain, ARCS Monetization Lab, Rebecca/Northly triad), walkthroughs for low/medium/high stakes, CUR/ALC patterns library, v10 Lab section.

**Target repo layout** (ARCS v9 Porting Roadmap) [cite:1]:
```
arcs-v9/
  canon/        arcs-canon-v9-draft.md
  protocols/    kintsugi.md, notomation.md, deep-shavasana.md, s-tier.md
  cases/        cleo/, northly/, elimar/, fund-25m-close/
  patterns/     7-pillars.md, l0-l5.md, receipt-templates.md
  runtime/      engine.py, atg.py, receipts.py
  cli/          arcs init / arcs brief --daily / arcs run --case
```

---

## 6. Operational releases (product / GTM shipped or specced)

- **Flagship ARCS Pilot SKU** — productized monetization container; 6–8 weeks; maps Money OS, instruments 3–5 decisions as Receipts, ships one cash-generating artifact [cite:1].
- **Northly Brain pilot kit** (Jog / Run / Sprint — $5k / $8k/mo / $15k/mo) — generalized to a reusable Pilot Kit v1 [file:11].
- **Rebecca / Northly adapted MVAs (Tally Diagnostic, Heisman Narrative, 3-Tier Menu, Mad-Libs SOW)** — live sales artifacts adapted from v8.5 Diamond Protocol [file:11].
- **Ripple-BVF S-Tier package (Gold Master memo, CFO one-pager, Ripple-Fit Technical Standard rubric, Anticipatory QA, Pre-Mortem, Track-Changes log, Patrick O'Kain voice calibration)** — live proof point for v9 primitives (NOTOMATION, Write-Lock, Decision Receipts, bias hygiene) [file:9].
- **Funhouse Optics Monetization dogfood** — one-screen mock + 10-day cadence turning "how do I monetize ARCS?" into Decision Receipts [cite:1].

---

## 7. Gauntlet — mythology vs. practical outcomes

To narrow the gap you named, the 3-week gauntlet pass surfaced [cite:1]:

**Likely over-sold (move from lore → plain language in v9):**
- "Diamond Protocol / Superconductive / NULL-OM-UNDEFINED" — keep the logic, rewrite the packaging in non-fiction tone.
- "God Mode / Court" dramatic naming — collapse into `mode = COURT` internal flag; surface only in DEEP.
- Multiple overlapping time frames (Chronos/Kairos, Diamond Protocol, Epistemological Kernel) — consolidate under Time Quality Attribution ROM [file:1].

**Under-sold (promote visibility):**
- Decision Receipts as the product — most GTM still leads with lore, not receipts.
- Bias Hygiene / "why not just GPT/Claude?" differentiator — 3-bullet block belongs at the top of `ARCSv9Firmware.md` [cite:1].
- L0–L5 altitude ladder as a standard scoping tool for every pilot.

**Loops to close (zip stalled energy into kinetic):**
- Move Canon out of Perplexity Space into owned repo (Claude Codes) — the tarball [cite:1].
- Stand up the Question Compass endpoint with the 7 microservices behind it.
- Promote Deep Shavasana Meta-Audit from "we should" to required pre-commit ritual.
- Kill the cobbler's-kids drift: while you prioritize paid pilots, still log each pilot move as a v9 ROM candidate receipt so Canon catches up as cash arrives [cite:1].

**Spark-plug moments still in the void:**
- ATG shipped as a real head on the model (not an emulation) — biggest near-term leverage once in Claude Codes.
- Funhouse Optics rendered as an actual UI, not just wireframe text.
- Institutional Memory Engine pattern (from Northly) formalized as a generic product, separable from consulting.

---

## 8. Recommended next moves (next 10 working days)

1. **Lock the tarball scaffold** — create `arcs-v9` repo with the folder tree in §5 and paste the 5-Book scaffold into `canon/arcs-canon-v9-draft.md` [cite:1].
2. **Run Book I episode** in Gemini/Claude using the exact scaffold prompt in the thread; commit output verbatim.
3. **Stand up `/question-compass` as a stub service** with the 7 internal functions as no-ops returning fixed JSON; wire Decision Receipt logging first.
4. **Promote Time Quality Attribution ROM** (`time-quality-attribution-rom.json`) into `canon/protocols/time-quality.md` and make it a required gate before any shipping session [file:1].
5. **Make Deep Shavasana Meta-Audit the pre-commit hook** for any v9 firmware change; log as Decision Receipt.
6. **Day 1–10 cadence with Hila (2–4pm EDT)** [cite:1]: ROM Clean Room → Compass UX → Agency Guardrails → Pilot Template → Bias Hygiene → Top 7 Channels → ROM Changelog & Naming → Onboarding Script → Metrics & Receipts → Hila Review & Consolidation.
7. **Ship one paid Flagship Pilot** in parallel — cash funds Canon cleanup; every move in the pilot is logged as a v9 ROM candidate receipt.

---

## Appendix A — Source map (Space files cited above)

- `time-quality-attribution-rom.json` — Time Quality Attribution ROM spec [file:1]
- `field-os-init.md` — ARCS v8.5 Field OS init guide [file:2]
- `based-on-my-tendency-to-speak-…md` — v9.0 version header, Porting Roadmap, 5-Book scaffold, Question Compass spec, ATG, Funhouse Optics, gauntlet pass [file:3]
- `whats-the-best-way-to-position-…md` — Pilot's Manual positioning [file:4]
- `activate-arcs-in-deep-creative-…md` — Cleo creative thread (Book III source) [file:10]
- `arcs-v8-5-system-initializatio-…md` — Diamond Protocol v8.5, Northly pilot stack [file:11]
- `activate-arcs-in-deep-shavasan-…md` — Deep Shavasana thread [file:12]
- `i-ve-been-using-arcs-for-creat-…md` — OS state primitives, TV Guide, v8.4 firmware [file:13]
- `ARCS-v8.3-Canon.md` — transversal Canon, NCI, Kintsugi [file:14]
- `ARCS-STierProtocol-DefaultStack.md` — S-Tier protocol [file:17]
- `ARCS-YellowPaper-v1-2.md` — math foundations [file:18]
- `ARCS-Vector-Collision-Engine-v1.md` — vector engine spec [file:19]
- `you-are-an-s-tier-equity-forme-…md` — Ripple-BVF live proof point [file:9]

*If a spec you remember isn't reflected above, it is almost certainly in `based-on-my-tendency-to-speak-…md` (the longest thread of the 3-week window) and can be pulled in a follow-up pass.*
