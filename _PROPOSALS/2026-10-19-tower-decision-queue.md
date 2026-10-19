# Tower decision queue, 2026-10-19

Control tower: session infallible-mirzakhani-f58a2a (branch claude/tower-decision-queue). The tower holds the critical path and this queue. It merges nothing itself and starts no work on a row until Zach rules on it. Ordered by fan-in: the rows each answer unblocks.

## A. Gravity wells (one answer unblocks many rows)

| # | Decision | Unblocks | Source |
|---|---|---|---|
| A1 | Rule D1 to D5 of `_PROPOSALS/2026-10-15-hud-moire-audit.json` | 11 HUD rows (all HOLDING or BLOCKED behind hud-proposals-ruling) | backlog row hud-proposals-ruling |
| A2 | Compass anti-distillation options (memo arriving from the compass child session) | compass-anti-distillation-build | row compass-anti-distillation-decisions (P0) |
| A3 | ADR-085 accept or re-decide (merge train vs bypass) | merge-train-only-path, doc-gates-blocking | row adr-085-acceptance-redecide (trigger date 10-13 passed) |
| A4 | Fates for the past-review_by rows (the hygiene child brings a proposed table) | about 43 rows | row backlog-fate-triage-2026-10-18 |

## B. One-way doors (WRITE-LOCK, Zach only)

| # | Decision | Source |
|---|---|---|
| B1 | rc-ops-001 graduation ruling | row rc-ops-001-graduation-ruling (RIPE) |
| B2 | agent-receipts audit, first conversion (an outward send) | row agent-receipts-audit-first-conversion (RIPE) |
| B3 | asm-003 cold molt | row asm-003-cold-molt-decided (RIPE) |
| B4 | Vico follow-up draft and stop-loss gates as scheduled checks | rows vico-followup-draft, vico-stop-loss-gates-scheduled (P0) |

## C. PRs waiting on your go (checked 2026-10-19 via gh)

1626 drift false-positive sample (green) · 1551 deps minor and patch (green) · 1622 allowlist 3 read-only commands · 1564 public-claims rows DONE · 1285 design house-style detector · 1291 @types/better-sqlite3 major bump · 1606 assembly-line triage (overlaps this tower, see E2) · 1634 farcaster docs · drafts 1588 (H8 librarian) and 730 (witness stub).

## D. Forensic pickup: stranded work found

| # | Finding | Ask |
|---|---|---|
| D1 | Local branch `claude/recursing-brattain-190758`: 6 commits never pushed (brand: identity-origami, composite-identity map, five-fathom resume sounding, provenance chip, attraction rules, plus a wip-preserve commit). Its worktree is gone. | Push and open a PR, bundle to the archive, or compost |
| D2 | `feat/audit-service`: 15 commits on origin not on main, last touched 2026-09-07 | Salvage or close |
| D3 | 3 old checkpoint trails (linkedin-alerts-scraper x2, agitated-feynman) have no branch delta left | None: mark claimed |
| D4 | Main checkout is detached at de463cb6, behind origin/main 69d36e79 (session-start sentry), so new agents and skills do not load | OK to move main to origin/main |

## E. Tower operating questions

| # | Question |
|---|---|
| E1 | Live sessions: 8 are running now (4 children from this fold plus drift sentry, field os weekly, jobs autorun, HUD audit), against the 4-session cap in memory `session-budget-discipline-cap-parallel-molt-long`. Should the tower hold new starts until it drops below 4? |
| E2 | RULED 2026-10-19 (relayed from the funny-burnell session, not given in the tower session): the "Session dependency hierarchy" session (local_5bd11219) and PR 1606 (assembly lines, local_e3ca00a6) both stay separate; the tower absorbs neither. |
| E3 | Carried from handoff v3.140.0, items 1 to 12 (Amy draft, covers sent, Norm PDF, backup encryption, funnel kill on 10-22, eye-tracking stub, Perplexity exports, port candidates, Actions billing lines, ADR-088 VICO, trust or status wording, Lead index verdict). Their status has not changed. |

## Critical path the tower now holds
jtbd-graph s3 gates, then s4 retrieval, then s5 feedback (s0 to s2 DONE: PRs 1621, 1630, 1640). The next child starts when E1 allows.
