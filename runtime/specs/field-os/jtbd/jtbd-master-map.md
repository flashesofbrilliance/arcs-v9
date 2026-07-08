# ARCS — JTBD Master Map

> **Version:** v0.1.0
> **Date:** 2026-05-26
> **Status:** CANONICAL — this is the governing product frame for all surface specs, PRDs, and implementation plans
> **Owner:** arcs-field-os
> **Runtime home:** arcs-v9

---

## The Four-Surface Architecture

ARCS is hired to perform four sequential jobs. Each job is a surface. The loop closes through the receipt layer.

```
┌─────────────────────────────────────────────────────────┐
│                                                       │
│   [D] CALIBRATE → [A] ORIENT → [C] CHART → [B] DETECT  │
│         ↑                                      │       │
│         └───── DEWY W-layer (receipt body) ──────┘       │
│                                                       │
└─────────────────────────────────────────────────────────┘
```

Detect feeds back into Calibrate because accumulated receipts change *what questions you know to ask* next cycle. This is the DEWY W-layer (Wisdom Distillate) promoting patterns back into the config layer as ROM candidates.

---

## Surface Map

| Order | Verb | JTBD | Hire condition | Engine | arcs-v9 issue | Build status |
|---|---|---|---|---|---|---|
| 1 | **Calibrate** | Help me ask the right question | User is in decision freeze / fatigue; question is malformed or unclear | ATG — Anticipatory Tributary Generator | Backlog (no issue yet) | 🔴 Not built |
| 2 | **Orient** | Help me find my position and True North | Question is clean; stakes are real; user needs a structured path | Compass → DEWY → Y-gate | [#2 DEWY Schema](https://github.com/flashesofbrilliance/arcs-v9/issues/2), [#3 Time ROM](https://github.com/flashesofbrilliance/arcs-v9/issues/3), [#4 Compass→DEWY](https://github.com/flashesofbrilliance/arcs-v9/issues/4) | 🟢 Shipped (v9 app) |
| 3 | **Chart Course** | Help me see who and what moves with me | Decision is oriented; user needs network + resource activation | Network scan suite + `arcs_cli.py` | Shipped scripts (no open issue) | 🟢 Shipped (scan suite) |
| 4 | **Detect** | Help me see threats, blindspots, biases, and non-obvious patterns I can't see myself | Receipt body exists; user is in a reflective / post-cycle state | Observatory + DEWY W-layer distillation | [#5 Book II Canon](https://github.com/flashesofbrilliance/arcs-v9/issues/5) (upstream dep) | 🟡 Backlog (needs receipt body) |

---

## JTBD Definitions

### [D] Calibrate — “Help me ask the right question”

**Hire condition:** The user is in decision fatigue, decision freeze, or approaching the Compass with a malformed question. They don't yet know if they're asking the right thing. The cognitive state is pre-ignition — fog before orientation.

**What ARCS does:** Surfaces the better version of the question before running the full L0–L5 pipeline. Prevents dirty inputs from propagating into the receipt layer. The HOLD gate (from the HOLD/REJECT validation layer) is the mechanical expression of this job — it fires when a question can't yet be trusted.

**Engine:** ATG (Anticipatory Tributary Generator) — the next major feature. Currently unbuilt. The meta-question tributary is the entry point for Calibrate.

**Why it's first:** Without calibration, Orient produces confident answers to the wrong question. The NOTOMATION rule applies here most forcefully — ARCS must scaffold the question, not compress or replace it.

---

### [A] Orient — “Help me find my position and True North”

**Hire condition:** The question is clean. Stakes are real. The user needs a structured path through a decision they're stuck on — not a search result, a structured judgment with a receipt.

**What ARCS does:** Runs the full L0–L5 Claude pipeline. Produces a DEWY receipt (Decision + Experience + Wisdom + Yield). Scores the session through the Y-gate (12-dimensional manifold: polarity × conviction × stability). Returns a True North + rationale.

**Engine:** Compass → DEWY → Y-gate. The most complete surface in the codebase.

**Why it's second:** You can only orient once you've calibrated. This is the primary ignition job — the core reason ARCS exists.

**Open arcs-v9 issues:** #2 (DEWY schema), #3 (Time ROM), #4 (Compass→DEWY flow)

---

### [C] Chart Course — “Help me see who and what moves with me”

**Hire condition:** The decision is oriented. The user needs to activate the right people, resources, and relationships to execute. The question is no longer *what do I do* but *who and what do I move with*.

**What ARCS does:** Runs the network scan suite against a live decision context. `forensic_scan.py` (5-lens detection), `archetype_scan.py` (8-archetype NCI scoring), `arcs_cli.py` (5-verb pipeline with apex spine DEWY receipt). Produces a ranked, scored network activation map.

**Engine:** Python scan suite in `scripts/`. `arcs_core.py` shared kernel. Zero external dependencies.

**Why it's third:** Network activation is only meaningful when filtered through a specific Compass question. C without A produces a list. C after A produces a move.

**Current NCI baseline:** [NCI:81] as of last commit (`arcs_cli.py`).

---

### [B] Detect — “Help me see threats, blindspots, biases, and patterns I can’t see myself”

**Hire condition:** A body of receipts exists. The user is in a reflective or post-cycle state — after a decision wave, a quarter end, a significant outcome. They're ready to extract patterns, not make a new decision.

**What ARCS does:** Runs the Observatory — replay and pattern extraction across the receipt archive. Surfaces Orthogonal Echo isomorphisms, recurring Loki patterns, Brier score drift, and ROM promotion candidates from the DEWY W-layer.

**Engine:** Observatory (not yet built) + DEWY W-layer distillation. Structurally depends on having run A and C multiple times.

**Why it's last:** Pattern detection requires a body of evidence. You cannot distill Wisdom (W-layer) from a single session. B is the long-horizon product surface — it upgrades every prior cycle retroactively once it exists.

**Feedback loop:** Detect → Calibrate. Accumulated patterns change what questions you know to ask next cycle. This is the W-layer promoting ROM candidates back into the config layer.

---

## Mapping to Cognitive State

| Stage | Verb | Cognitive state on hire | What ARCS resolves |
|---|---|---|---|
| 1 | Calibrate | Foggy / paralyzed / asking wrong question | Frame clarity |
| 2 | Orient | Oriented but uncertain about path | Structured judgment + receipt |
| 3 | Chart Course | Decided but unsupported | Network + resource activation |
| 4 | Detect | Reflective / post-cycle | Pattern extraction + wisdom upgrade |

---

## HOLD/REJECT Gate Alignment

The HOLD/REJECT validation layer (defined 2026-05-26, see `arcs-v9/SKILL.md`) maps to this JTBD sequence:

- **HOLD** fires most often at the Calibrate boundary — the question isn't clean enough to orient
- **REJECT** fires at the Orient boundary — integrity failure, fabrication, or bypass attempt
- **PASS** flows through all four surfaces in sequence

---

## Changelog

| Version | Date | Change |
|---|---|---|
| v0.1.0 | 2026-05-26 | Initial creation — four-surface architecture established from Perplexity ARCS session |
