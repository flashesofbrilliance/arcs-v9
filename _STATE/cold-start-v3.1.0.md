# Cold-Start Pickup Prompt — v3.1.0

> Paste this whole file as your first message in a fresh thread with zero prior context.
> It's self-contained — you should not need to ask Zach anything before starting one of
> the unblocked tasks. If something below contradicts live state, trust live state and
> flag the doc as stale (see the verification protocol in `~/.claude/CLAUDE.md`) — don't
> silently proceed on a contradiction.

---

## Where you are

Repo: `flashesofbrilliance/arcs-v9`, branch `main`, HEAD `3474d10`. This repo serves
`app.arcs.care`, `www.arcs.care`, `arcs.care`, and `resume.arcs.care` — all one Vercel
deployment, confirmed via `get_deployment`. (A standalone `arcs-care` Vercel project
still exists but is `live: false` — don't build there by mistake.)

Read in this order, don't skip, don't re-derive what's already written down:
1. `_STATE/snapshot.json` — machine-state facts (deploy status, env vars, DB)
2. `MEMORY.md` `[v3.1.0]` entry (top of file) — full narrative of what landed last session
3. `_PATTERNS/2026-06-23-governance-roadmap.md` — the 8-item dependency graph, pathogen
   taxonomy, fat-tail/long-tail pre-mortem. **This is real analysis, not boilerplate** —
   read it, don't skim it.
4. `_PATTERNS/2026-06-23-s-tier-execution-plan.md` — per-task plan, including a withdrawn
   citation (read the "Addendum" sections — they're corrections, not noise)
5. `TaskList` — live status of all 8 items. This is the source of truth for what's done,
   not any of the files above.

## What NOT to do

- Don't assume `_CANON/`, `SKILL.md`, `AGENTS.md`, or any canon doc is internally
  consistent. This session found a real contradiction (`BAR` meant two different things
  in two files) that sat unnoticed until someone read both files end-to-end instead of
  grepping. If you're about to build something on top of a canon definition, confirm it
  against the *other* file that might also define it, not just the first one you find.
- Don't treat anything in `operators/` tagged `ROM Candidate` as production-trustworthy.
  `RC-OPS-001` (`arcs_inchworm_echo.py`) is real, working, independently verified code —
  but it's explicitly not yet ROM, and its promotion is gated on an Observatory period
  that hasn't started (Observatory itself isn't even fully built yet — see task #7).
- Don't trust a claim of "all bugs fixed" or "verified" without actually running the code
  or checking the cited source yourself. This exact session caught two cases where a
  confident claim didn't survive independent execution/citation-checking. That discipline
  is the whole reason this handoff chain is trustworthy — don't relax it because it's a
  new thread.
- Don't rewrite git history for task #6 (commit trailers). Forward-only. The plan doc
  names this as the single highest-irreversibility item if mishandled.

## The 8 tracked items — pick one of the unblocked three to start

| # | What | Status | Notes |
|---|---|---|---|
| 1 | Backup repo for `~/.claude` globals | **Unblocked, start cold** | Scope already decided: exclude `settings.local.json` (leaked credential, see #2) |
| 2 | Rotate/confirm-dead leaked Supabase password | **Blocked on Zach** | Not yours to resolve — flag it, move on |
| 3 | Consolidate 3 overlapping narrative logs | **Unblocked, start cold** | Sequencing point — must land before #4's build and #6's retrofit |
| 4 | Drift-sensor cadence/severity/display | Design done, build not started | The long pole. Blocked by #6 (trailer syntax) and #7 (Observatory display) |
| 5 | Audit prose-rules for enforcement gaps | **Unblocked, start cold** | Scope to `SKILL.md` first |
| 6 | DEWY commit/PR stamp (`ADR-Ref:`/`Y-Gate:` trailers) | Ready after #3+#5 | Forward-only, never rewrite history |
| 7 | Cherry-pick orphaned Observatory commit `35070a3` | **Unblocked, start cold** | From stale clone `/Users/zharris/arcs` — do not use that path as a working directory otherwise, it's 2+ weeks stale |
| 8 | Reformat the S-tier plan into the corpus's canonical Section 1-7 format | Deferred, not started | Format is on page 9 of `RECOIL-PROTOCOL.pdf` if Zach has it handy; otherwise ask |

**Recommended first move:** #1, #5, or #7 — all three have zero dependencies and zero
human blockers. Pick whichever matches what Zach actually asks for first; don't just
grab #1 by default.

## Two things to carry forward, not just historically interesting

**On scope, corrected after this session ended:** arcs-v9 is only ~20% of the ARCS
corpus/canon — the rest lives and compiles in Perplexity Space. The BAR/KKL collision
and RC-OPS-001's freshness are real findings *about this port*, not evidence that the
corpus's own `Conviction ★★★★★`/`Coherence ★★★★★` self-grades (from `RECOIL-PROTOCOL.pdf`)
are overclaimed — those grades were almost certainly assessed against the full corpus,
not this partial port. An earlier version of this session's own write-up made exactly
that scope error (compared port-level findings against corpus-level self-grades) before
catching it. **The honest framing: port lag, not corpus incoherence.** That's also a
*more* useful framing operationally — "the port lags the corpus" is actionable (port
more, sync more often); "the corpus overclaims itself" isn't something arcs-v9 work can
fix at all.

**On the independent-read question:** when asked to cross-check a document against this
session's findings, the honest answer to "was that an independent/blind read" was no —
the session was already primed to find exactly the kind of gap it found. That observation
stood, and was explicitly *not* something to apologize for: deliberately injecting a
primed, skeptical reader is the same generative move `RECOIL-PROTOCOL.pdf` itself names
as **productive discord** — friction as raw material, not an error state, the same engine
behind every Loki Test in the corpus's own Hyperstition Pipeline. The point of pairing
with an external reader isn't to get an uncorrelated second opinion; it's to get friction
you can't generate by re-reading your own work alone. If asked for an "independent" check
again, name the priming honestly — but don't treat the priming itself as the problem.

---

*This file is a point-in-time snapshot, not a permanent fact. If it's been more than a
session or two since `captured_at_v3_1_0_delta` in `_STATE/snapshot.json`, re-verify
before trusting anything above instead of assuming it's still current.*
