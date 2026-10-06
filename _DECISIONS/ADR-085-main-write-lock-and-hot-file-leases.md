# ADR-085 — Serialize the collision points, not the sessions: a main write-lock and hot-file leases on git refs

> **Status:** PROPOSED
> **Date:** 2026-10-06
> **Author:** Claude Opus 5.5, from the 2026-10-05 orchestration session with Zach
> **Oracle:** number allocated via `scripts/oracle.py next adr` (85); `_SEEDS/_oracle.json` committed on this branch.
> **Commit:** (set at merge)
> **WRITE-LOCK (ROM 7):** declared one-way door. See "Write-lock declaration" below.

---

## D — The Decision

**Sharp question:** With dozens of parallel sessions landing on main, how do we stop collisions on
the few shared write points (the push to main, and a handful of hot files) without serializing the
sessions themselves?

**Proposed answer (for review, not decreed):** Four parts, all built on the one atomic primitive this
repo already trusts (git refusing a ref update that does not descend from the ref's current value):

1. **(a) Main write-lock.** A lock on a dedicated remote ref, `refs/locks/main`, acquired by
   `scripts/merge_train.sh --lock` (and by hand with `scripts/write_lock.py lock acquire`) before it
   fetches main, held until its push lands, released on exit. Metadata: holder session, host, pid,
   reason, acquired_at, expires_at (TTL, capped at 2h), seq, took_over_from.
   Stale-lock rule: a lock past `expires_at + grace` is STALE. A plain `acquire` still refuses it;
   the taker must run `lock takeover`, which records the previous holder in the lock commit. The
   takeover is declared, never silent.
2. **(b) Kairos sets cadence, never permission.** The Kairos operator decides WHEN a train runs
   (queue depth or time window). It never decides WHETHER to lock: every train that writes main
   under this ADR holds the lock, no exceptions by mode.
3. **(c) Hot-file leases.** A committed lease registry, `leases.json` on its own ref
   `refs/locks/leases`, claimed through the same compare-and-swap. Claims are all-or-nothing over a
   path set, expire on a TTL (default 2h, capped at 4h), and are released only by their holder.
   Pre-commit policy: WARN by default (print the holder, exit 0), BLOCK only for paths listed as
   block-tier, and BLOCK on unreachable remote only in block-tier (warn-tier fails open).
4. **(d) Remove the hotspots structurally.** Leases are the stopgap; deleting the shared file is the
   cure. Handoffs become per-session fragment files folded into CLAUDE.md once, by one writer under
   the main lock. Pre-commit gates load from `scripts/git-hooks/pre-commit.d/*` instead of one
   782-line shared file.

---

## E — Entity / System

- `scripts/write_lock.py` (new, this PR): `lock acquire|release|status|takeover`,
  `lease claim|release|list|check`, `--self-test`. Stdlib Python, git CLI only.
- `scripts/merge_train.sh` (#874): new `--lock` flag, default OFF. Self-test cases (f) and (g) added;
  (a) to (e) unchanged and still passing.
- `scripts/oracle.py`: not changed. Same mechanism, different namespace: the oracle CASes a counter
  file on a branch, this CASes a JSON file on a lock ref.
- `operators/arcs_operator_kairos.py`: not changed. Its `TimeMode.WRITE_LOCK` maps to the train
  window in (b); wiring is in the migration plan, not this PR.
- Every session that pushes to main or edits a hot file (after migration). No session is affected
  by this PR: nothing calls the new code unless a caller opts in.

---

## W — Window

**Horizon:** QUARTER
**Revisit trigger:** (1) GitHub refuses pushes to `refs/locks/*` (fall back to `--prefix
refs/heads/locks/`); (2) a takeover fires on a lock whose holder was still alive (grace too small
for real clock skew); (3) a lease blocks a commit for longer than one working session without the
holder present; (4) the repo moves to a plan with a native merge queue.

---

## Context

The night of 2026-10-05 every conflict was in a hot shared file, never a general clash:

| Collision | Hot point |
|---|---|
| #771 vs #775 | `src/app/jobs/JobsBoard.tsx` |
| #715 vs `claude-models.ts` | 7 API routes via two competing model registries |
| #811 | CLAUDE.md handoff blocks |
| #854 vs #796 | forge resume files |
| #715 | `scripts/git-hooks/pre-commit` |

Two kinds of write point produced all of them: the push to main (sequential merges racing the same
tip) and a short list of files that many sessions append to. Everything else parallelized fine. So
the target is narrow: serialize those points and leave sessions alone.

Prior art in the repo: `oracle.py` already proved that git's non-fast-forward rejection is a usable
atomic gate across harnesses (AGENTS.md gotcha #12). `merge_train.sh` already refuses to force and
exits "main moved; re-run" on a non-ff rejection. What is missing is a way for a session to know
BEFORE it does the work that someone else is mid-write, and a TTL so a crashed session cannot wedge
everyone.

**One finding from building it (corrected by the red-team pass, see below):** the guarantee comes
from a plain, non-forced push of a child commit. If two writers read the same state and each push a
child of it, the second is not a descendant of the first and is refused. The first draft of this ADR
also claimed `--force` could not break it because `receive-pack` compare-and-swaps the old value.
That is false: under `--force` the old value checked is whatever the server advertised at the start
of that same push, not the state the writer read earlier, so a forced writer with a stale read
silently erases the other grant (reproduced by the red team in a temp repo). The "one winner even
under force" result in early testing was a timing artifact of the barrier. Rule: writers never force;
the self-test's negative control (a blind force-retry writer) double-grants, which proves the race
assertion has teeth.

---

## Options Considered

### Option A — Global session serialization (one session at a time)
- Pros: no collisions by construction.
- Cons: kills the parallelism that is the whole point of the fleet; a 5-minute docs fix waits behind
  a 2-hour build session. Rejected.

### Option B — GitHub merge queue / branch protection
- Pros: platform-native, server-enforced.
- Cons: unavailable. The repo is private on a free personal plan: no merge queue, no enforceable
  branch protection (the same reason gotcha #17 is enforced by a daily detector). Rejected for now;
  revisit trigger (4).

### Option C — A lock server (Redis, Supabase row lock, a tiny HTTP service)
- Pros: real TTLs, server clock.
- Cons: a new always-on dependency for a local-first workflow, a new credential in every harness,
  and a second source of truth beside git. The ask was explicit: reuse the oracle mechanism, do not
  invent a server. Rejected.

### Option D — Lock file committed on main (`_STATE/lock.json`, `_STATE/leases.json`)
- Pros: same CAS, visible in the tree.
- Cons: every acquire/release becomes a commit on main, so the lock registry becomes the hottest
  file in the repo and floods main's history and Vercel with lock churn. Rejected in favour of
  dedicated refs. (The task brief suggested `_STATE/leases.json`; this is a deliberate deviation.
  A read-only mirror into `_STATE/` for `/loops` is possible later; the authority stays on the ref.)

### Option E — Dedicated lock refs with parent-chained state commits (CHOSEN)
- Each state change is a commit whose parent is the state it was computed from, pushed without force.
- Pros: atomic via git itself, works for every harness that can `git push`, full audit trail
  (`git log refs/locks/main`), no effect on branches, invisible to default clones and fetches.
- Cons: wall-clock TTL (skew risk, see failure modes); each operation is one network round trip
  (about 0.5 to 1s against GitHub); GitHub's acceptance of `refs/locks/*` is unverified (fallback
  prefix exists).

---

## Decision detail

### (a) Lock semantics
| Verb | Rule |
|---|---|
| acquire | free or absent: grant. Held live by me: extend (re-entrant). Held live by another: refuse, name holder. Held but expired: refuse with "declare it with takeover". `--wait N` polls. |
| release | holder only; a crashed holder that comes back after a takeover cannot release the new holder's lock |
| takeover | only when `now > expires_at + grace`; records `took_over_from` |
| status | exit 0 free, 3 live, 4 stale |

`merge_train.sh --lock` acquires before `git fetch origin main` (so BASE is read under the lock),
holds through build and push, and releases in its EXIT trap. TTL 30 min, renewed (re-entrant
acquire) after the build and again after the push prompt, so a slow build or a person at the `[y/N]`
prompt cannot outlive it; a failed renewal means someone took it over, and the train exits with
nothing pushed. Each train run has its own identity (`merge-train@host:pid:repo`), `LOCKED=1` is set
before the acquire so an interrupt mid-acquire still releases, and `--dry-run --lock` skips the lock.

**Identity.** Default session id is `user@host:<worktree path>`, never the branch: two clones on one
host, or two detached-HEAD worktrees, must not share an identity (they would extend and release each
other's lock). `WRITE_LOCK_SESSION` or `--session` overrides it.

**Safety argument:** correctness of main never depends on the lock. The train's push is still
fast-forward only. If the lock fails in any way (early takeover from skew, a session that ignores
it, an expired TTL mid-build), the worst case is today's behaviour: the second push is rejected and
prints "main moved; re-run". The lock turns a wasted build into a refused start; it never turns a
safe push into a clobber. This argument covers main only. The lock refs' own history is a
best-effort audit trail: a writer that forces (against the rule) can rewrite it and erase a
takeover record.

### (b) Kairos cadence
Kairos proposes the train window; it never touches the lock. Initial policy (configurable, to be
wired in migration step 4): run a train when green-PR queue depth >= 3, or when the oldest green PR
has waited >= 30 min, whichever comes first; no trains in `SANCTUARY`; `TimeMode.WRITE_LOCK` is the
name for the window while a train holds the lock. NOTOMATION holds: a human can run a train at any
time, and the lock still applies.

### (c) Lease policy
- Claim is all-or-nothing over a set of paths; a conflicting live lease by another session refuses
  the whole claim and names the holder.
- Expired leases are ignored and garbage-collected on the next write.
- `lease check PATH...` in pre-commit: warn-tier prints and exits 0; block-tier (`--block`) exits 1.
- Initial block-tier list: none. Start everything in warn and promote a path to block only after it
  causes a collision while warned (pre-register the rule before counting).
- Candidate warn-tier list from 2026-10-05: `src/app/jobs/JobsBoard.tsx`, `CLAUDE.md`,
  `scripts/git-hooks/pre-commit`, the model registry files, `_SEEDS/_oracle.json` (already CASed by
  its own push; listed for visibility only).

### (d) Structural removal
- **Handoff fragments:** `/handoff` writes `_HANDOFFS/fragments/<date>--<branch>.md` (one new file
  per session, never a shared append). A fold step (`/handoff --fold`, run by one session holding the
  main lock) moves fragments into the CLAUDE.md block and the archive in one commit.
- **pre-commit.d:** `scripts/git-hooks/pre-commit` becomes a 20-line runner that executes
  `scripts/git-hooks/pre-commit.d/*` in lexical order, failing on the first non-zero. Each existing
  gate moves into its own file unchanged. A new gate is a new file, so two sessions adding gates no
  longer touch the same lines.

---

## Failure modes

| Failure | What happens | Mitigation |
|---|---|---|
| Crashed holder | Lock sits until `expires_at`; then STALE (status exit 4) | TTL cap 2h; `takeover` after expiry; takeover is recorded; the returning holder cannot release the new lock |
| Clock skew | Expiry uses the holder's clock, takeover compares against the taker's | `--grace` (default 120s) must exceed real skew; all hosts on NTP. Worst case is an early takeover, which degrades to today's non-ff "re-run", never a clobber (safety argument above) |
| Offline session | `lock` exits 5; `lease check` warns "state UNKNOWN" | An offline session cannot push main anyway. Warn-tier fails open, block-tier fails closed |
| Lease squatting | A session claims hot files and walks away | TTL capped at 4h; `lease list` names holders; leases never block the holder's own commits, and warn-tier never blocks anyone |
| Remote refuses `refs/locks/*` | Push of the lock commit fails | `--prefix refs/heads/locks/` (a visible branch). Verify against GitHub in migration step 1 |
| Push refused with no competing write (hook, ruleset, permission) | Exit 6, distinct from offline (5), so it is never mistaken for "offline, fail open" | Fix the remote config; do not treat as unreachable |
| Contention storm | Many racers on one ref | CAS retries up to 8 times with a fresh read each time, then refuses |
| A session bypasses the lock | It pushes main directly | Not prevented (no branch protection). Main is still non-ff safe; the daily squash detector pattern can be extended to flag main pushes without a matching lock commit |
| Lock ref history grows | One commit per operation | Tiny (one blob each). Prune by pushing a fresh orphan state while holding the lock, if ever needed |

---

## Write-lock declaration (ROM 7)

This is declared a **one-way door**. Rationale: once sessions are told the lock exists and start
relying on it, the lock refs and their JSON schema become a shared contract across every harness;
changing the semantics later means coordinating every running session at once, and a semantic
change done carelessly (for example, making plain `acquire` take over stale locks silently) would
hide integrity failures instead of showing them (ROM 6). The prototype in this PR is opt-in and
reversible; the door closes at migration step 3, when hooks or trains start calling it by default.
Nothing in this PR crosses it.

---

## Migration plan

1. **Probe the remote (needs Zach's yes).** Push one state commit to a throwaway ref
   (`refs/locks-probe/x`) on GitHub, confirm it is accepted and invisible in the UI, delete it.
   If refused, standardize on `--prefix refs/heads/locks/`.
2. **Opt-in trains.** Use `merge_train.sh --lock` for every manual train for one week. Log every
   refusal and takeover. No hook changes.
3. **One-way door: default on.** Flip `--lock` to default in merge_train.sh (with `--no-lock` as
   the escape hatch) and add the warn-tier `lease check` to the pre-commit runner. Separate PR, its
   own receipt.
4. **Kairos cadence.** Wire the (b) policy into the scheduled train runner.
5. **Structural removal.** pre-commit.d split (one PR, mechanical move, byte-identical gate bodies);
   handoff fragments + fold step (one PR). After these, drop CLAUDE.md and pre-commit from the lease
   list.
6. **Block-tier promotion.** Only for a path that collided while warned, one path at a time.

Rollback at any step before 3: delete the flag usage. After 3: `--no-lock`, and remove the
pre-commit.d lease gate file.

---

## Evidence (this PR)

- `python3 scripts/write_lock.py --self-test`: ALL PASS, repeated runs. Covers two racers
  through a barrier (both read the same state before either pushes) with exactly one winner, for
  both the lock and a lease; stale takeover; holder-only release; warn vs block; TTL clamp; offline
  behaviour; default identity across two clones (4b); lease path spellings (4c); and a negative control proving the race assertion is not vacuous (a blind force-retry
  writer double-grants and the test sees it).
- `sh scripts/merge_train.sh --self-test`: ALL PASS, (a) to (e) unchanged, plus (f) `--lock` refused
  while another session holds the lock with main unchanged, (g) `--lock` merges, pushes and releases.
- Live dry run: two git worktrees racing against a throwaway bare remote in the session scratchpad
  (never origin). Output in the PR body.

---

## Red-team pass

Run 2026-10-06 by the `claims-skeptic` agent with a BAR (ruin) lens, against the first draft and
first prototype, temp repos only. Verdict on the first draft: core design holds (plain push refuses a
stale update, both self-tests pass, main stays fast-forward only), but one false claim and one
blocker. Findings and responses:

| # | Sev | Finding | Response |
|---|---|---|---|
| 1 | major | False claim: "two writes from the same state can never both land, forced or not". Under `--force` the checked old value is the one advertised at push time; a stale forced write erased a grant | **Fixed (ADR).** Claim corrected in Context; rule is "writers never force". Kept plain push (no `--force-with-lease`): the ancestry check already encodes "child of what I read" |
| 2 | blocker | Default session id `user@host:branch` let two clones (or two detached HEADs) on one host share a lock; one released the other's | **Fixed (code).** Default id is now `user@host:<worktree path>`; merge_train passes a per-run `--session`. New self-test (4b) runs WITHOUT `WRITE_LOCK_SESSION` and asserts the second clone is refused and cannot release; it fails on the old default by construction |
| 3 | major | 30 min TTL never renewed; a long build or a person at the prompt could outlive it | **Fixed (code).** `lock_renew` after the build and after the prompt; renewal failure exits with nothing pushed |
| 4 | minor | Ctrl-C between acquire and `LOCKED=1` leaks the lock until TTL | **Fixed.** `LOCKED=1` set before acquire, reset on refusal |
| 5 | minor | `--dry-run --lock` blocks real trains for a run that pushes nothing | **Fixed.** Lock skipped on dry run |
| 6 | minor | Lease paths compared after `normpath` only: absolute or subdirectory-relative paths never matched | **Fixed.** Paths resolved to repo-root relative (from cwd when inside the repo, else from the repo root); outside-repo paths refused. Self-test (4c) |
| 7 | minor | Push refused with no competing write surfaced as "unreachable" (exit 5), so warn-tier would fail open on a ruleset rejection | **Fixed.** New exit 6 |
| 8 | minor | Safety argument overstated: lock history is rewritable by a forcing writer | **Fixed (ADR).** Scoped to main; audit trail called best-effort |
| 9 | open | GitHub acceptance and visibility of `refs/locks/*` unverified | **Open.** Migration step 1, needs Zach's yes to push one probe ref |

Re-run after fixes: `write_lock.py --self-test` ALL PASS (twice), `merge_train.sh --self-test` ALL
PASS.
