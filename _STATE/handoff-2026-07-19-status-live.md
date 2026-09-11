# Handoff — Status-board goes live + issue tracker stood up (2026-07-19)

> Standalone handoff (NOT appended to CLAUDE.md/MEMORY.md). Rationale: a concurrent
> session was actively editing CLAUDE.md/MEMORY.md/snapshot.json during this thread
> (5+ interleaved commits/deploys to main). Appending to the shared hot-path files
> would be the exact clobber this session spent effort avoiding. Fold this into
> CLAUDE.md's handoff chain later, from a session that owns those files uncontended.

Branch: pushed straight to `main` (fast-forward each time; no clobbers).
Commit range this thread: `b8cba0f` → `0e19a69`. Latest deploy `0e19a69` = **READY**
in production, verified via Vercel API, aliased to status/chan/app.arcs.care + all.

---

## What this session shipped

### 1. GitHub Issues stood up as the actionable-work source of truth
Only 3 stale issues existed (all done). Created a triaged backlog and closed the stale ones.
- **Open (28):** security J-items, product loop-closers, governance. Human-action set
  **#72–78** (INTERNAL_EMAILS, GITHUB_TOKEN, secret rotation, branch protection,
  **#77 repo-split execution**, ADR-015 case-study, #89 orphaned tables) +
  vaguer backlog **#91–99** (J3/J15/J16/J18/J21→done/J22/J23/J24→done/J25).
- **Closed (26):** #1/#2/#5 stale-done, #95 (J21) + #98 (J24) shipped this session,
  and **#101–119** — 19 backfilled "shipped" workstreams (Compass, Y-gate, prep,
  brief, guide/history, auth, P4, RLS, Book II, design-system, CI/CD, Observatory,
  legal, EyebrowToast, Live Pulse, operators, ADR governance, anon-claim, subdomains).

**Label convention (keep this):** every tracked issue carries exactly one status label —
`in-progress` | `blocked` | `next` — or is `closed`/`completed` for shipped. `/api/pulse`
counts by these. New work must follow the convention or it won't appear on the board.

### 2. ADR-036 — repo split (public app / private sensitive)
Owner decided **split** (Option B). `_DECISIONS/ADR-036-repo-split-public-private.md`.
Staged so the irreversible history-rewrite is gated behind "private repo verified
complete + offline backup + concurrent sessions quiesced." **Execution is a separate,
owner-attended session — not done here.** Issue **#77**.
> Renumbered from 035 mid-session: a concurrent session claimed 035 for the Commit-NCI
> rubric (in index.json + nci-scoring skill). Caught same-session, fully reconciled.

### 3. J24 — external-surface leak gate (SHIPPED, #98 closed)
- `scripts/leak_check.sh` — scans all 25 subdomain-mapped `public/*.html` for internal
  markers (provenance, model ids, secret shapes, local paths, repo structure, patent
  strategy). Deny-by-default, fail-safe (empty glob=exit 2), `.leakignore` reports allows.
- Wired as a **hard CI gate** (`.github/workflows/ci.yml`, standalone bash job).
- **Caught 6 real leaks on first run** (not false positives): `claude-sonnet-5` on
  kelly page; `do-not-file`/`§101`/`USPTO`/internal-papers on state-of-union+status;
  `DATABASE_URL` infra note. All redacted.

### 4. J21 — reusable watchdog stop-rule (SHIPPED, #95 closed)
`scripts/watchdog.sh` — wrap any long-running command with a mandatory timeout →
`SIGNAL_WATCHDOG_TIMEOUT` (exit 124). Terminating, fail-safe (refuses unbounded),
coreutils-timeout + pure-bash fallback. Verified all 4 paths.

### 5. Status board is now genuinely "state of now"
The user's north star for status.arcs.care: *true state of now for all systems*.
- `/api/pulse` extended: **shipped** = closed-completed issues; **in-progress/blocked/
  next** = open issues by label (one `state=all` call, PRs + not_planned excluded).
  Whole State-of-the-Union board is issue-derived — no curated constant.
- `status.html`: bar widths, zone badges, lead line, provenance stamp all live; direct-
  GitHub fallback if `/api/pulse` down; truncation flag if backlog >100.
- **Live day-count**: header "Days" + era-head "DAY 0 → DAY N" compute from T0
  (first commit 2026-04-09) at load — retired the hardcoded "98" (already 3 days stale;
  today = 101). "APR–JUL 2026" → "SINCE APR 2026" so the range can't rot. Both
  status.html + chan.html.
- Cache 300→600s (+ aligned the `gh()` fetch-cache the build caught still at 300) →
  ~30 GitHub calls/hr, under the unauth 60/hr ceiling until GITHUB_TOKEN lands.

---

## Human actions still blocking (all tracked as issues)

| # | Action | Unblocks |
|---|--------|----------|
| #73 | Add `GITHUB_TOKEN` to Vercel (read-only) | lifts /api/pulse off the rate ceiling — the one thing that makes the live board bulletproof |
| #72 | Set `INTERNAL_EMAILS` in Vercel | low-pri (code already defaults to zach.harris@gmail.com) |
| #74 | `ANTHROPIC_API_KEY` in GitHub Actions Secrets | security-review workflow |
| #75 | Rotate Supabase pw + Resend key | overdue (ADR-048); Resend 401 blocks email |
| #76 | Branch protection on main | **concurrent-session clobber risk — live this session** |
| #77 | Execute the ADR-036 repo split | closes public exposure of dossiers/papers/patent IP |
| #78 | Build case-study social-proof section (Dan approved) | then flip CASE_STUDY_APPROVED |
| #89 | Triage 8 orphaned Supabase tables | keep pathogen_log/drift_signals for J12/Drift Sentinel |

---

## Durable learnings from this thread

1. **Concurrent sessions on main are a live hazard, not theoretical.** 5+ interleaved
   deploys during this thread; an ADR-number collision actually happened (035). Mitigation
   held (fetch+rebase before each push, `ls _DECISIONS/` before claiming a number), but
   the real fixes are **#76 (branch protection)** and **#80 (serializability/Yoav)**.
2. **A hard gate needs its surface clean first.** J24's gate couldn't land green until the
   6 real leaks were redacted — building the check surfaced pre-existing exposure.
3. **"Live-looking" ≠ live.** The board had a green pulse dot + ticking commit count while
   the status was hand-maintained and the day-count silently 3 days stale. Provenance
   stamps + computed-from-source are the fix; don't claim more liveness than exists.
4. **Don't derive "shipped" naively from closed issues** without backfill — it undercounts
   history badly (would've shown ~5 vs the real ~25). Backfilled instead.
5. **My curl to *.arcs.care 403s** (agent proxy / bot protection). Verify deploys via the
   **Vercel MCP** (`get_deployment`, team `team_narCbxUgS4eiieJKRv1QMfff`), not curl.

---

## Next session starts at

- Nothing open in this thread; everything committed + deployed + verified.
- Pick from the issue backlog. **Buildable, no human dependency:** #92 (J15 cheaper
  verify), #93 (J16 consented input allowlist), #94 (J18 rename agent primitives),
  #96 (J22 MCP identity pinning), #99 (J25 recursion audit), #85/#86 (P1 loop-closers).
- **Owner-gated / higher stakes:** #77 (repo-split execution), #80 (serializability ADR),
  #79 (harden /api/compass), #81 (Skeptic Sentinel operator).
- **State-sync note:** `_STATE/snapshot.json` semantic fields (session_summary/next_action)
  NOT hand-synced this session — deliberately, to avoid clobbering the concurrent session.
  Run `/init-state-sync` from an uncontended session (J17 / #fork-lineage).
