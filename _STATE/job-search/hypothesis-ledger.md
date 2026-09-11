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

### Amendment 2026-09-11 — outcome backfill (evidence: Gmail inbox sweep)

Backfilled from application-reply emails (not memory, not inference). Only company+role
matches written to the board; acks (ATS "we received it") are **not** counted as responses.

**Resolved (no-convert) written to board this pass:** Charlie Health (exact role match),
Sequence Holdings ×2, monday.com (Deployment Architect), Crosby (company match, eng role) →
all `laneStatus=rejected`. With prior Percepta/Monstro closes → **~9 resolved, 0 responses, 0 wins.**

**Advance-then-reject (flagged, not written):** a Google application reached an **Online Assessment**
(2026-09-10) and was rejected on results the same day. The email does not name the role, so it was
NOT attributed to a board row — could be the Lead GenAI FDE (board) or the Sr AI Product Ops Manager
(Yuri Kleban warm-referral). Needs human attribution.

**Material data-quality finding:** the board's 28 "applied" rows are a large **undercount**. The inbox
shows applications to many more (Figma, Baseten, Luma, Navan, Higharc, Reindeer, Chalk, Distyl, Parloa,
Tenex, Arcadia, Chainlink, Tabs, Mirage, Sailor Health, BOI, Raspberry AI, Infillion, Trunk Tools,
Console, Savvy Wealth, Sharp Electronics, …). **The true denominator is unknown**, so H1–H4 rates are
not yet computable from the board alone. Fix before any read: reconcile the full applied set from Gmail.

**Early directional read (UNDERPOWERED — not a verdict, n<30, all within the 21d ghost window):**
first ~9 resolutions are all rejections spanning both tiers; the only application to advance a step
(Google → assessment) was **prestige**, not IYKYK. No support yet for H1. Do not act on this.

**Warm-path signal (H3):** a real warm path exists and is unused in the funnel data — Yuri Kleban
(Google) offered a direct referral (2026-09-02). H3 should be run as a deliberate forward test.

### Amendment 2026-09-11 (b) — H3 precondition: warm must be INTO a real, defined, funded req (worked example: Fanatics)

**Why this amendment:** H3 as registered ("warm-path applications out-convert cold") has one
resolved warm-path case in the whole record, and it is a loss. Fanatics (Jun 24 to Jul 15, 2026):
founder-level intro (Chris Lamontagne, who in writing asked for Zach to meet Chase) → talent screen
passed (CJ Masopust, recoil NCI 88 GREEN) →
"thanks but no thanks" on Jul 13, 12 days later, with a hiring-manager conversation that never
happened. Full grounded post-mortem: `_STATE/job-search/postmortem-fanatics.md`.

**What it isolates:** warmth was real and verified (intro within 4 days, Calendly within 2 hours,
community invites). The outcome still resolved as no-convert because **there was no req**: no JD,
no comp sign-off, no decision-owner reached. Boardy's same-night read: "liked the work but never
found a concrete mandate that matched your shape." The fit-score and the recoil both saw the gap
(go-bag prior "active req attached: 30%"; scenario tree gave 5% to "stalls at Talent, no open req";
the req question was asked live and answered "being defined") and rendered SHARP anyway.

**H3 refined (H3'):** *Warm-path out-converts cold ONLY when the warm path lands INTO a req with
`req_reality >= 2`. At `req_reality <= 1`, warmth predicts goodwill and referrals, not offers, and
must be logged as a relationship asset, not a shot.*

- New required field on every warm shot: `req_reality` (0 = no JD/no owner met · 1 = verbal shape,
  no JD or budget · 2 = JD posted or cut, budget implied · 3 = JD + budget + decision-owner met).
- Cut for H3' becomes 2×2: `warm_path {>=1, 0}` × `req_reality {>=2, <=1}`. The H3 comparison is
  read on the `req_reality >= 2` row only. The `<=1` row is reported separately as the
  "manufactured-role" arm and is expected to be ~0 regardless of warmth (Fanatics n=1).
- Decision rule addendum: if the `<=1` arm stays ~0 while the `>=2` arm shows warm ≫ cold, the lever
  is "warm INTO real reqs" (relationship manufacturing pointed at posted mandates), NOT
  "manufacture the role through the relationship." Pilot/contract asks are the conversion path for
  `<=1`, tracked as a distinct outcome (`pilot`), not as an application.
- Fanatics is booked as: `warm_path=1 · req_reality=1 · laneStatus=rejected · resolved 2026-07-13`
  (transcript-verified 2026-09-11: Zach asked "real thing or exploratory?" on the Jul 1 screen; CJ:
  JD being defined, "not fully baked"; CJ's Jul 13 no: "we don't have a role in mind that's the
  right fit today")
  in the manufactured-role arm. It stands as a standing exclusion on the champion shortlist for the
  same reason (no req to target), with the door warm.

**Not changed:** the pre-registered H3 text, metric, and min_n stay as written; this block adds the
gate and the field. Read gate unchanged: no verdict before n ≥ 20 resolved warm shots, and the
`>=2` row needs its own n.
