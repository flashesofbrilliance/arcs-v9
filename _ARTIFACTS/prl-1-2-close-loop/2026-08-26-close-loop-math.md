# PRL Phase 1.2 close-loop math — 2026-08-26 (internal, git-only)

> The overdue Aug-24 close-loop. This is the INTERNAL math sheet. The Todd-facing one-pager is
> `2026-08-26-close-loop-onepager.md`. Per gate (ADR-068 / backlog `prospecting-pass-1`):
> **re-pricing of 1.3–1.5 happens WITH Todd on a call, never unilaterally.** This sheet preps the call.

## The ex-ante receipt (from the live deck, todd-call.html, verbatim anchors)

- **Bet:** delivery + enrichment + 4-hour metric + baseline, at **$4,500, ~20 hours**, kicking Mon Aug 10.
- **Wrong if:** actual effort lands outside **12–30 hours**, or the 4h metric can't be built from existing data.
- **Mid-phase update (Aug 18, already published):** effort trending past the top of the band; build fast,
  coordination overhead blew the estimate; **cap holds**.

## Actual effort (proxy — no timesheet exists; method disclosed)

No hour log was kept, so the proxy is distinct work days x session-depth, cross-checked against commit density.

- Distinct 1.2-window work days touching PRL paths: **Aug 10, 11, 13, 17, 18, 19, 26 = 7 days** (Aug 23 commits were another engagement).
- PRL-path commits in window: **109** (Aug 18–19 alone ~65, the family-conformance + status-surface build-out).
- Plus non-commit work: Zapier co-pilot sessions, Sugar MCP sweeps, Tidio/vendor/IT coordination, the routing investigation.

| Scenario | hrs/day | Actual hours | Multiplier vs 20h bet | vs band top (30h) |
|---|---|---|---|---|
| Conservative floor | 4 | ~28 | 1.4x | at the top |
| Central | 6 | ~42 | **2.1x** | 1.4x past |
| High | 8 | ~56 | 2.8x | 1.9x past |

**Verdict: the "wrong if" clause FIRED.** Even the conservative floor sits at the band top; the central
estimate is ~2x the bet. Effective realized rate at central: $4,500 / 42h ≈ **$107/hr** vs the implied
$225/hr at bet. The cap held as designed — the overage is Zach's, banked as tuition, and it is exactly
what the receipt mechanism exists to surface.

## Where the hours actually went (drives the 1.3 conversation)

1. **Build itself: FAST and inside the bet.** Delivery verified with a real conversation, dedup + enrichment
   + timers live, baseline pulled (942 leads / 4,238 opps), routing ground truth swept (12 no-rep states).
2. **Coordination overhead: the blowout.** Tidio plan-tier surprise forcing re-architecture (Catch Hook, not
   API-call node), sandbox arriving mid-phase, vendor email deliverability loops, the routing investigation
   (which found a real pre-existing CRM issue — value, but unpriced).
3. **Surface polish: self-inflicted, now extracted.** ~65 commits of status-family conformance became the
   `prl-page-factory` skill — that class of cost won't recur.

## 1.2 scope scorecard at close (updates the Aug-18 DoD reconciliation)

| Criterion | At Aug-18 | At Aug-26 |
|---|---|---|
| Reliable delivery | MET | MET (+ v5 empty-email guard published; Roger Lamarre record repaired; test leads zero-proofed) |
| Enrichment (ZoomInfo email fill) | PARTIAL | PARTIAL — task10 diagnostic staged; close or re-baseline in writing |
| 4-hour metric (proxy allowed) | PARTIAL | **CLOSED mechanically** (Zach ruling 2026-08-26): chatbot leads timestamped at creation + assignment, Zap rule nudges past the elapsed window; hourly sweep staged as nice-to-have; Todd's written ack demoted to nice-to-have FYI |
| Baseline | NOT STARTED | **PULLED** (`_ARTIFACTS/prl-baseline/`): 942 leads, 4,238 opps, $43.7M / 48% of opps with blank lead_source |

So 1.2 closes at **2 MET + 2 cheap-to-close** — materially better than the Aug-18 picture.

## What the receipt sets for 1.3 (positions for the call — Todd decides)

1.3 was pre-disclosed at **$4,000 / ~18h**, "number confirmed against the 1.2 receipt before kickoff."
The honest read: the 1.2 overage was ~90% coordination, ~10% build. So the recommendation to bring to
Todd is NOT a higher price — it is the same range with the coordination priced as **preconditions**:

- Keep 1.3 at $4,000 top-of-range (not the discounted lower end — the receipt shows why).
- Precondition batch BEFORE the clock starts: sandbox written approval, ZoomInfo contact, negative-keyword
  list, Bill/territory call done. (The exact 1.1/1.2 failure mode: client inputs arriving mid-phase.)
- Widen the 1.3 "wrong if" band asymmetrically (e.g. 12–34h) since coordination risk is now measured, not guessed.

## Extraction queue (first prospecting pass, ranked by banked cost)

| Rank | Cost class (receipt evidence) | Extraction | Status |
|---|---|---|---|
| 1 | Zapier hand-editing loops (multiple sessions, human-gated) | Zap-kit build sheets, co-pilot-paste-ready | BUILT (`_ARTIFACTS/prl-zap-kit/`) — next: publish pass, then evaluate Zapier API/CLI route to kill the human gate |
| 2 | Status-family conformance polish (~65 commits) | `prl-page-factory` skill | EXTRACTED — residual cost near zero |
| 3 | Sugar bulk ops (12+ req/call pattern, sweeps) | Generalize sweep scripts into a `sugar_bulk` helper | CANDIDATE (cheap, do when next Sugar job lands) |
| 4 | Layer-0 eval/normalization suite | Already scripted (22,500-case grid) | EXTRACTED |
| 5 | Vendor/IT coordination loops | Not extractable — **price it** (preconditions + band width) | POLICY (this receipt) |
