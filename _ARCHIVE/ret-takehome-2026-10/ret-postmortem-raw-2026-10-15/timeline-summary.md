# RET take-home timeline: T0 (2026-10-10 10:11 ET) to rc46 (2026-10-14 12:46 ET)

327 commits, 46 RCs, ~98 h. ET times; ZIP sizes decimal MB (recoil used MiB: rc1 5.40 MiB = 5.66 MB). rc1-22 phases follow the recoil; rc23+ are my split.

| Phase | RCs | Commits | What happened | ZIP MB | API $ |
|---|---|---|---|---|---|
| Build | rc1 | 149 | product, evals, deck, gates | 5.66 | 3.31 |
| Polishing | rc2-11 | 15 | deck/bench features | 5.7-6.45 | 0.76 |
| Surface grows | rc12-14 | 18 | bench rework, history bundle | 7.7-8.98 | 0.22 |
| Honesty | rc15-17 | 15 | claims audit, reasoning pages | 9.2-9.3 | 0.18 |
| Product defects | rc18-22 | 12 | K55-K58 class fixes | 9.5-9.89 | 0.75 |
| Rehearsal, packaging | rc23-32 | 38 | two rehearsals, install.sh, exact ZIP layout | 10.0-10.34 | 0.94 |
| Size cut | rc33-35 | 11 | wiki pages; bundle dropped | 10.45 to 3.35 | 0.24 |
| Design pass | rc36-38 | 50 | pages, nav, 19 rehearsals | 3.93 | 1.18 |
| Hardening | rc39-46 | 19 | amendment/stale-figure fixes, poller | 4.0-4.22 | 0.93 |

**Cadence.** RCs per day: 11, 3, 18, 3, 11. 18 of 45 gaps are 10 min or less (bursts rc2-4, rc29-30, rc36-38). Five gaps exceed 5 h (longest 30 h). The 10,000,000-byte cap, not restraint, ended growth (10.45 MB at rc33).

**Spend.** Cash API spend is $8.51 over 3,497 calls (matches E-build-spend): $4.07, 0.22, 1.89, 1.24, 1.08 per day. Sonnet 5.5 is $8.505, Haiku $0.007, local and mocks $0. The evidence ledger separately states a build-session floor of at least $262.77 (about $271 total); that is a session readout, not API log.

**Trend.** Claude eval cases passed by day: 96.1%, 61.1% (6 runs), 94.8%, 98.7%, 95.0%; last 15 runs all green. Rehearsal: 37 runs, 34 green, 5 live. Live e2e 15 of 17; wargame 17 of 17.

**What the layers caught.**
- Three red rehearsals: slide 5 text 232 px off-slide (pre-rc1), a failed canary, an internal path leaking into a shipped log. Each was green again within minutes.
- Kintsugi ledger: 79 mistakes; about 31 found by gates/tests/evals, 35 by human or external review, 13 other. Mostly the builder's own. K71 and K78: a stale figure passed the verbatim check (two amendments on one clause; refusal path).
- Trace: 327 of 327 commits have spans, but one (c92dbf7, hooks off) was reconstructed from git.

**Accounting gaps.**
- Pre-commit refusals (stale figure, leak, overflow) are not logged, so their counts are unknown.
- 253 failed model calls have no usd.
- 386 of 399 trace spans have cost basis "unknown"; human minutes unrecorded.
- Other sessions' spend not totalled.
- Eval counts mix mock, local and no-key runs.
- The shipped ZIP trims older log entries.
