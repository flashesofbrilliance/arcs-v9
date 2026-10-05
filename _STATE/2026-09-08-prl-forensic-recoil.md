# PRL forensic recoil — thread residue ⟶ live snapshot reconciliation (2026-09-08)

> Reverse-listen over the prl-chatbot-sugarcrm worktree thread, serialized against the most
> updated live snapshot on `prl.arcs.care` before Todd went dormant. Generative recoil (ADR-066):
> the point is not to re-narrate the session but to reconcile what the client can SEE against what
> the thread actually ESTABLISHED, and surface the honesty seam between them.

## Ground truth — Todd's last view
- **Most-updated live snapshot = `/status/catchup`** ("Back from training", Sep 8, shipped by a
  parallel session). `/status/progress` is stale (Aug 18) — do not treat it as current.
- Catchup BLUF: *"Phase 1.2 is closed and capped. Leads now land reliably in your CRM, you have a
  real baseline for the first time, and the one thing waiting on you is a single decision: does 1.3
  start now, or after we close a few small loose ends."*
- Also asserts: *"Leads are de-duplicated by our delivery step on email; Sugar has no native lead
  dedup."* · $4,500 cap held despite ~2x effort · 6 states get no rep · Support case 589806.

## The load-bearing seam (the recoil's keel)
The catchup page states the dedup safeguard **as fact**. This thread proved that safeguard has a
**live, unpatched failure mode**: an empty email makes the delivery step's Find-Record match an
arbitrary record, and Path A then UPDATES it. This already corrupted a real 2021 lead
(Roger A Lamarre, `ea77a7d2-1b0b-11ec-...`).

| Live-page claim (what Todd sees) | What this thread established | Verdict |
|---|---|---|
| "de-duplicated by our delivery step on email" | Empty email → false-positive match → real lead overwritten | **Overclaim — guard has a hole** |
| (Roger not mentioned) | Record **REPAIRED** via direct Sugar API PUT, 4 fields cleared | Cleanup done; invisible to page |
| (not itemized) | Prevention **filter STILL OWED** — non-empty-email gate before the search | **Open, unnamed on page** |
| (not itemized) | Path A pollutes **4** fields (`description`, `title`, `hint_account_industry`, `account_description`), not the 3 the brief listed | Harden task under-scoped |
| "1.2 closed and capped" | True for delivery leg; the items above ARE the "small loose ends" but are not named | Directionally honest, vague |

## Thread residue absent from every live surface
- **Journey-canvas "real-site look" rebuild** — requested ("rebuild the journey canvas on the real
  site look"), **never executed**. Canvas still on PRL dark/gold brand at
  `claude.ai/code/artifact/6adbc191-903c-41c5-abdb-44f925541c07`.
- **PR #180 e2e screenshots** — captured on the real staging site (site loads + AI Handoff flow
  fires), saved to user's local disk, **never dragged into the PR**.
- **Atlas artifact comments** — answered in-thread (cron/realtime, design session, audience tiers).

## Serialized owed-list (reconciled, dedup'd against the live page)
1. **Empty-email filter step** in Zap 376827315 — the PREVENTION. Must ship before more demo
   traffic AND must be NAMED as the specific loose end on the catchup page, not folded into "UAT."
   Roger repair was cleanup only.
2. **Harden Path A mapping for all 4 polluted fields** (not 3).
3. Two UAT items the page already implies (rep notification + spam check; test-lead cleanup).
4. Journey-canvas rebuild on real-site look — IF the wireframe deliverable is still wanted (the raw
   PR-180 screenshots may already satisfy the underlying need; confirm before spending on it).
5. PR #180: drag the captured screenshots in; do not submit a live lead while filter #1 is open.
6. 1.2-A web forms — payment-gated (invoice #NYQRTJPQ-0004), untouched until it clears.

## Cross-recoil: thread ⟷ last Todd call (Sep 1, Granola 35b35eff)
The authoritative call recoil is `_ARTIFACTS/prl-1-2-close-loop/2026-09-01-recoil-close.md`
(committed `e50ee851`). Reconciling it against this thread surfaces a **chain-of-custody drop**:

1. **This thread (Aug 18/27):** empty-email dedup false-positive is a LIVE, unpatched bug; already
   overwrote a real 2021 lead (Roger, sandbox copy). Cleanup shipped, prevention filter did not.
2. **Sep-1 call recoil:** records only *"dedup case still not visually confirmed (HITL)"* — framed
   as "not re-run," NOT as a known bug that already bit a real record. Empty-email filter, Roger,
   and the 4-field pollution appear NOWHERE in it.
3. **Sep-1 decision:** Todd chose **GO-LIVE-FIRST** — action item 6 = *"Tidio plugin on the LIVE
   WordPress site, pointed at PRODUCTION Sugar."*

**Escalation:** the go-live plan points a delivery step with a known, unpatched dedup hole at the
PRODUCTION CRM, and the recoil that authorized go-live silently dropped the bug. Sandbox: a false
positive overwrote a COPY of a 2021 lead. Production: the identical path overwrites a REAL live
customer record — and family-office reps (55+, manual conversion via Bill) would not notice a
silently corrupted lead. This moves the finding from "status-page honesty seam" to **production
ruin-vector, invisible in the authoritative call recoil.**

**What the Sep-1 call correctly added (not in this thread):** live demo worked (Norelle/UL V0/CT →
Lynn Winston); punch list = Lyro-synopsis→Sugar-Notes, assign Todd's account, notifications to
info@+rep, unassigned-lead fallback to Bill+digest, consult Tidio/Sugar PS before routing; Todd
owes W-Systems ZIP + territory reconcile (6 states no rep, correct the "6 reps" misstatement) +
ZoomInfo tier; ~$6,200 spent, $4,500 cap held. See [[project_todd_hotes_prl_resins]] and
[[prl-e2e-proven-once-not-always-on-hitl-required]].

## Sent-email reconciliation (recap "Chatbot // recap and next steps", Sep 1, thread 1a05f9080fc761fd)
Todd replied 🙏 "Great recap!" and is seeing Bill Friday. JTBD maps 1:1 (Bill W-Systems ZIP →
territory reconcile → ZoomInfo tier); no drift there. Three findings on the dedup bug:

1. **The bug is absent from the email AND reframed.** "De-duplicating" appears only under ZoomInfo
   ("whether it can help with matching and de-duplicating leads") — presenting dedup as a FUTURE
   ZoomInfo nice-to-have, when the delivery step already dedups on email today and that is the
   mechanism with the hole. The ruin-vector has now fallen out of ALL THREE counterpart-facing
   surfaces: catchup page, call recoil, sent recap. It survives only in thread memory + this receipt.
2. **The defined go-live gate cannot catch it.** Green light = "run a chat as a fresh visitor and
   watch the lead land with summary + alert." A fresh visitor with a VALID email never triggers the
   empty-email false-positive; the test proves the happy path only. Classic proven-once ≠ always-on
   ([[prl-e2e-proven-once-not-always-on-hitl-required]]). The go-live test must add an explicit
   empty-email / repeat-visitor case, or it green-lights over the bug.
3. **The promised "safety net" is the wrong net.** The catch-all + digest covers UNASSIGNED (routing)
   leads; it does nothing for a silently OVERWRITTEN real record (data integrity). Todd may read it
   as covering this risk when it doesn't.

## Recoil verdict
The live snapshot is honest in DIRECTION (it admits loose ends exist) but **presents the
empty-email dedup guard as complete when it is the single prevention gap still open** — and that
gap is the difference between "dedup protects you" and "dedup already bit a real record once."
The Sep-1 GO-LIVE-FIRST decision supersedes the "before 1.3" framing: **the empty-email filter is
now a blocking pre-condition of go-live, not a loose end** — because go-live points the buggy step
at PRODUCTION Sugar. Single highest-conviction move: ship the non-empty-email filter in Zap
376827315 AND surface it as an explicit go-live gate before the Tidio plugin touches the live site.
Everything else on the catchup page holds against the thread.
