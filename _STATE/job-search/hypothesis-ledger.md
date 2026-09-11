# Job-Search Hypothesis Ledger — pre-registered

> **Registered:** 2026-09-11 (America/New_York) · **Registrant:** Zach Harris
> **Purpose:** make the job-search strategy *falsifiable*. We have priors (fit scores) and almost
> no posterior (outcomes). This ledger fixes the hypotheses, metrics, and decision rules **before**
> outcomes are counted, so later reads are tests — not post-hoc stories.
> **Discipline:** this file is the SSOT. Committed to git = the write-lock (the pre-registration is
> only real once it's timestamped in history). Do NOT edit a hypothesis after outcomes start landing;
> add a dated amendment block instead, and say why.

---

## Why this exists (the premise being tested)

The stated worry was *"am I chasing false premises — prestige?"* The board falsifies that worry
directly: of the funnel below, **25/30 applications are non-prestige (IYKYK/other), 5 prestige.**
The contrarian bet is already the revealed behavior — it does not need a new filter.

The premise we actually **can't** yet judge is **conversion**: whether *any* of these shots land.
Optimizing fit-scores against fit-scores is coherence, not correctness. This ledger is the loop that
turns shots into evidence.

## Frozen baseline (as of registration)

- **In-funnel:** 30 applications, all logged 2026-09-08 (one Monstro follow-on 2026-09-11).
- **Age:** ~3 days. **No ghost window has elapsed.** Non-response today is expected, not signal.
- **Tier mix:** 25 IYKYK/other · 5 prestige (OpenAI/Anthropic/Google/Bain/Aircall class).
- **Resolved outcomes at registration:** 2 — both losses (Percepta `closed:lost`, Monstro `closed`).
- **Warm-path:** ~0 across the board (cold applications).
- **Composite range of the funnel:** ~0.51–0.94 (mostly PURSUE).

## Outcome taxonomy (the states we capture, in `laneStatus`)

| status | meaning | counts as… |
|---|---|---|
| `applied` | submitted, no human reply yet | sent, unresolved |
| `ack` | ATS auto-acknowledge only ("we received it") | **not** a response |
| `rejected` | declined with no human screen | resolved — no-convert |
| `screen` | recruiter/HM replied wanting to talk | **response** (first real conversion) |
| `interview` | advanced into an interview loop | response + advance |
| `offer` | offer extended | win |
| `ghosted` | ≥21 days, no reply of any kind | resolved — no-convert |
| `withdrawn` | you pulled out | censored (exclude from rates) |

- **Response** = `screen` or better. This is the primary conversion event (a human engaged).
- **Ghost window = 21 days** from application date. Before that, `applied` ≠ negative.
- Every status change is **human-supplied or evidence-backed** (an inbox reply, a portal update).
  A row is never marked resolved on inference alone. *In datis veritas.*

---

## Pre-registered hypotheses

Power note up front: this pipeline is tiny (30 sent, ~2 resolved). **No hypothesis is read before
n ≥ 30 _resolved_ outcomes** (target ~end of the 21-day window on a ≥40-shot base). Earlier looks are
descriptive only, explicitly labeled "underpowered — not a verdict." Directional ≠ significant.

### H1 — Contrarian core *(primary)*
**Non-prestige applied-AI-eng roles convert to a response at a rate ≥ prestige roles.**
- Cut: `tier ∈ {iykyk/other}` vs `{prestige}` (recruiter-front excluded).
- Metric: response rate = `screen+ / (sent − withdrawn)`, per arm.
- Decision rule: if non-prestige response rate ≥ prestige **and** ≥ 10% absolute → contrarian bet
  confirmed, double down on IYKYK sourcing. If prestige materially higher (≥1.5×) → the premise is
  wrong; prestige access matters and warm-path into brands becomes the lever.

### H2 — Role-shape *(secondary)*
**FDE / engineer-shaped roles out-convert PM/strategy-shaped roles.**
- Cut: title-class engineer-shaped vs PM/strategy-shaped.
- Metric: response rate per arm. Decision: the losing shape gets deprioritized in sourcing/forge spend.

### H3 — Warm path *(secondary, likely the real lever)*
**Warm-path (referral/intro) applications out-convert cold ones.**
- Cut: `warm_path ≥ 1` vs cold. Currently ~0 warm, so this is mostly a *forward* test: deliberately
  route the next N shots through a warm path and compare.
- Metric: response rate. Decision: if warm ≫ cold (expected), the binding constraint isn't sourcing
  or tier — it's relationship manufacturing. Reallocate effort from volume to intros.

### H4 — Model audit *(the rubric's own falsification)*
**Composite fit-score is monotonically related to response rate.**
- Cut: composite tertiles (high ≥0.85 · mid 0.70–0.85 · applied-CONSIDER <0.70).
- Metric: response rate by tertile. Decision: if flat or inverted, the rubric is measuring the wrong
  thing — the scoring spec (v1.3) is due a rethink, not just a tweak.

### NULL / ruin-check *(the premise above all premises)*
**If overall response rate < ~10% at n ≥ 40 sent past the ghost window**, the false premise isn't
tier or role-shape — it's that **this profile is winnable via cold application at all.** Pivot the
whole strategy to warm-path/referral and founder-direct outreach; stop optimizing the cold funnel.

## Anti-Goodhart guard
The win is **interview/offer at target-fit roles**, not response rate. Do not juice response rate by
applying to easier, lower-fit roles. Response rate is the leading indicator; interview/offer at
composite ≥0.8 roles is the goal. If the two diverge, trust the latter.

## Cadence
Weekly readout: response/screen/interview counts by each cut above, labeled with n and power state.
Judgment stays human-owned — the ledger reports, Zach decides.

---

## Amendments
_(append dated blocks here; never edit the pre-registered sections above)_
