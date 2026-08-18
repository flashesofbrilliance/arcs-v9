# Opportunity-Cost Investment Bank · v1 synthesis
**2026-08-18 · five airgapped sweeps (4 top-down desks + 1 bottom-up folksonomy counter-pass) · all outcomes labeled DOCUMENTED vs INFERRED · no writes were made by any sweep**

Companion data: `_ARTIFACTS/drift-book.json` (9 positions, mechanical proxies). Sweep transcripts in session task logs.

## Executive read

1. **The north-star metric is two-column or it is a lie.** Internal compounding (echo-over-epochs) × external landing (money, replies, offers). Echo-only rewards drift by construction; outcome-only erases R&D. Yuri is the proof case: negative on its own P&L (one unanswered email for ~36 commits), strongly positive as R&D (forge CLI, ADR-044, the blueprint, the skills that shipped Kam at ~zero marginal cost).
2. **Secondary corpus yield is inversely correlated with primary outcome** across all 8 job loops. Effort making an artifact reusable is not effort making it land. Neither is waste — but they must be *booked separately*.
3. **The gate that decides primary outcomes is "did the evaluator see it," not "was it built."** Meridian: a 1–2h take-home got 15K+ insertions and the entire 8-script tier was never wired to the server. Gamma: 3 artifacts never rendered past a generation ID.
4. **The loop-killer is consumability, not fit.** Ahmed "hard to follow" + Yuri "too abstract," three weeks apart, different artifact families. The specced fix (60-Second Read) is the highest-leverage unshipped item in the corpus.
5. **Method yield survives dead deals.** Joe Kim → the active-listening law; Fanatics → recoil UI-kit + redaction doctrine; Jeben → the omakase class. Dead-loop harvest should be a ritual, not an accident.
6. **`[NCI:SKIP]` is the blind-spot generator** (~70% of window commits). Skip-scoring became skip-visibility: the three largest unnamed labor categories (render-micro-physics, vocabulary demotion, wrong-surface reflex) live almost entirely inside skipped commits.
7. **The falsification ledger is a scar log, not a falsifier** — 33/33 FALSIFIED means rows are written after the surprise. A real ex-ante ledger carries live and CONFIRMED rows too.
8. **The law (W5):** *the gate's first true positive is always the author.* ADR-062 ouroboros ≅ the PII re-privatization ≅ the air-gap gate's 100% first-run refusal ≅ ADR-065's tripwire catching its own minting commit. Canonized once; observed four times.
9. **Calibration bias, measured:** the ex-ante consistently undershoots warm peers (Yuri, Ahmed — same direction twice). The product's own calibration loop, now running on its maker.
10. **Every closed-loop win quoted the counterpart's own words back; every stall was self-originated framing.**

## Desk summaries

- **Positions (drift-book):** best mark = connector fleet (echo Σ10); fastest mint-to-reuse = self-cataloging→Louisville (~4h); most expensive logged = milestone falsification (1.18M tokens, bought an avoided build).
- **Clients:** Yuri (open, R&D-positive) · Robin (platinum master, warm) · Kam (open, awaiting score-back; circle files Zach as connector/GTM not builder) · Ahmed (consumability-blocked) · dead-but-fertile: Fanatics, Joe, Jeben.
- **Jobs:** resume.arcs.care = the compounding engine (164 commits, no attributed interview, enormous secondary yield) · Meridian = evaluator-visibility failure · clinical-AI = 95% cost collapse via skill amortization but zero capture (no project_ memory) · Prophet = stale-"Active", fast-track went silent.
- **Product/OSS:** recoil = highest compounding + only money receipt ($2,070 invoice) · ready-not-live trio = best trade (minutes of effort) · germinate = LIVE CATALOG PARADOX (npm-live 08-14 per distribution.jsonl; "unpublished/owner-gated" per index.jsonl + handoffs) · kairos = most-developed uncatalogued idea · observatory = decide merge-or-kill (kill: same yield, tenth effort).
- **Folksonomy (counter-pass):** 15 emergent clusters; 7 taxonomy blind spots; Louisville + Comet mis-filed (class-level results booked as client/job deliverables); the Folksonomist operator itself cannot see the corpus (domain-typed to gauntlet verdicts); the word "folksonomy" was deleted from the product's public copy (`f47cdd5`).

## Ranked action queue (approval-gated; nothing executed without sign-off)

### Fixes — mechanical, ruin-risk first
| # | Action | Effort | Note |
|---|---|---|---|
| F1 | **Close the PII flag**: `arcs-claude-project-scaffold` has PUBLIC `memory/USER_PROFILE.md` (flagged 08-13, open) | minutes | BEFORE any npm tag; ruin-class |
| F2 | **Reconcile the germinate PARADOX**: index.jsonl `status` + handoff text vs distribution.jsonl truth; extend the drift tripwire to seed `status` fields | minutes | ADR-065 ROM RC applies: fail closed, file receipt |
| F3 | **Ship the ready-not-live trio** (2 CI secrets + 3 tags): scaffold, linkedin-connections-toolkit, blindsat | minutes | after F1; takes family 8/11 → 11/11 live |
| F4 | vercel.json: remove 2 stale kelly-interview rewrites (flagged 07-27) | one line | |
| F5 | Mark Prophet memory STALLED (26d stale-"Active"); mint the missing clinical-AI `project_*` memory | minutes | jobs-desk capture gaps |
| F6 | **`_STATE/job-loops.jsonl`** — the missing outcomes ledger (sent_at/stage/last_signal/kairos_deadline), same shape as distribution.jsonl | ~1h | turns INFERRED outcomes into rows |
| F7 | Observatory branch: **decide** merge-or-kill (kill = same yield, 1/10 effort) | decision | longest-open loop, 06-23 |
| ✓ | Handoff-number collisions → oracle | DONE | ns seeded `{"handoff": 39}` this session |

### Mints — memories/seeds/practices
| # | Mint | Source desk |
|---|---|---|
| M1 | **W5 law**: "the gate's first true positive is always the author" (generalize ADR-062 from instance to law) | folksonomy |
| M2 | **`[NCI:SKIP]` ≠ invisibility**: skipped-from-scoring must still be clustered/named (practice change + possibly a sweep default) | folksonomy |
| M3 | **Ex-ante rows in the falsification ledger**: file hypotheses BEFORE outcomes; scar-only ledgers can't calibrate | folksonomy |
| M4 | **60-Second Read** — build it (consumability is the loop-killer; spec exists at `_ARTIFACTS/sixty-second-read.html`) | clients |
| M5 | Warm-peer ex-ante correction factor (calibration bias, 2 instances) | clients |
| M6 | Dead-loop harvest ritual | clients |
| M7 | "Parameterize on the third hand-built instance" | product |
| M8 | kairos (public-good #2) seed row | product |
| M9 | Evaluator-visibility gate ("did they SEE it") + counterpart's-own-words rule | jobs |
| M10 | Folksonomy S1–S6 (house-style artifact · register-demotion gate · surface-capability map · exposure-ratchet ledger · one-door operator · decay-auditor loop) + "four inchworms, one uncut mold" refactor candidate | folksonomy |

## Framework debts (so the bank doesn't lie to itself)
Echo prices only memories/seeds/scars (ADRs/scripts/artifacts read 0) · one epoch ≠ a curve · $ cost unlogged outside gauntlet runs · commit counts inflated ~2× by branch duplication · 5/8 job outcomes INFERRED for want of a ledger · the two-column north star (internal echo × external landing) is designed but not yet instrumented.
