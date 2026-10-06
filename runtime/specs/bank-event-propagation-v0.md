---
version: v0
status: PROPOSED (design only, nothing built, not scheduled)
date: 2026-10-06
seed: extends seed-gate-kinematic-adaptive-freshness (candidate), Part B of _SEEDS/ADR-CANDIDATE-2026-09-17-defeasible-context-codec-and-kinematic-freshness.md
governed_by: ROM primitive 1 (NOTOMATION), ROM primitive 6 (KINTSUGI immune system), memory lesson-banked-when-it-can-stop-you
script: scripts/bank_event.py (does not exist yet)
---

# Bank-event propagation v0: when a lesson is banked, it moves backward and forward

From a 2026-10-06 question from Zach: when we bank a failure or a pattern, do we propagate it
back and forward from anterior and posterior reasoning, so the flow moves through the
in-between organically?

## Rule

A lesson is **banked** only when two things are true: (1) everything that was built on the old
belief has been found and flagged (back), and (2) something mechanical will stop the next
occurrence or has an explicit reason it cannot (forward). Writing the lesson down is neither.

## Why now: what exists today (measured 2026-10-06)

- **Banking has levels but no trigger.** The hierarchy runs prose, memory, indexed memory,
  priced scar node, wired gate. Writing a memory, a pattern or a scar fires nothing.
- **Operator 21 (anterior/posterior spline inference) can be called on demand but no pipeline
  step or hook calls it.** `operator_client.py` registers it as `OPERATOR21` and can run it
  from the command line. Nothing in `operators/` pipelines, `.claude/hooks`, `scripts/` or
  `src/` invokes it.
- **The only propagation is for canon edits.** `canon_propagation_nightly.sh` mirrors canon
  facts forward onto a review branch. Lessons and failures do not use it.
- **A lesson can live where no scan reaches.** Today's lesson (a gate described as "manual"
  that is actually enforced at pre-commit) had 0 hits in git. The false claim lived in chat
  and in an artifact database. The scan has a blind spot there, and the design must say so.

## Terms

- **Bank event**: one durable record that a belief changed. It is a knot in the Operator 21
  sense: two resolved belief states with a curve between them.
- **Anterior**: what we believed before, and what that belief rested on.
- **Posterior**: what we believe now, and the evidence that moved it.
- **Axis** (from the claim-exit lattice): `falsified` (the answer changed, so correct it),
  `moot` (the question retired, so vacate and mark), `molted` (outgrown, kept dated),
  `new-pattern` (no anterior to defeat, forward only).

## Event schema

One JSON line in `_STATE/bank-events.jsonl` (append-only, gitignored, local first):

```json
{
  "id": "be-2026-10-06-a1b2c3",
  "kind": "failure | pattern",
  "axis": "falsified | moot | molted | new-pattern",
  "at": "2026-10-06T14:30:00-04:00",
  "source": {"type": "witness | memory | scar | adr | receipt | handoff", "ref": "..."},
  "anterior": {"claim": "...", "basis": "..."},
  "posterior": {"claim": "...", "basis": "..."},
  "defeats": [{"type": "regex | path | symbol | adr", "pattern": "...", "scope": ["docs", "code"]}],
  "guard": {"type": "risk-rule | pre-commit | defeater-trigger | session-start", "ref": "..."} ,
  "no_guard_reason": null,
  "banking_level": 1,
  "tuition": null
}
```

`guard` and `no_guard_reason` are mutually exclusive and one must be set. An event with neither
stays at level 4 or below and is listed as **unbanked**, with its age.

## Back-propagation (anterior): what was built on the old belief?

1. For each `defeats` matcher, scan git-tracked files, the memory index, and the debt register.
2. Each dependent found is marked **unverified**, with `defeated_by: <event id>`, a locator
   (file, line) and a `review_by` date from the same severity table as the risk sweep.
3. **Nothing is rewritten.** The break is shown, not patched (KINTSUGI). A person or a drafted
   fix repairs it. The axis sets the repair: `falsified` means correct and re-warrant, `moot`
   means vacate and mark with provenance.
4. Depth is one hop. A dependent is flagged, and its own dependents are not flagged in turn.
5. A dependent that is itself the record of the error (the ADR or script that describes the
   drift) is excluded by citation: a file that cites the event id or its source ref is a
   mention, not an assertion.

## Forward-propagation (posterior): what stops the next occurrence?

The guard is chosen from the banking ladder, strongest first:

| Guard | Fires when | Reuses |
|---|---|---|
| risk-rule | a new diff matches the failure's shape | `scripts/risk_sweep.py` rules |
| pre-commit | a staged file would repeat it | `scripts/git-hooks/pre-commit` |
| defeater-trigger | a warranted claim's trigger fires, so re-exhaust | Part B fields on the freshness gate |
| session-start | the lesson is worth a line at the next session | `.claude/hooks/session-start.sh` |

A guard graduates from advisory to blocking only after it has shown its precision (fires,
true-positive rate). A guard that has never fired and has no test by its horizon is flagged
as protection theater (seed `seed-anti-protection-theater`).

## Where events come from (capture)

Capture stays at the edge, where the session has the context. The engine has no LLM.

- v0 is opt-in: `bank_event.py record` is called by the session when it banks something.
- Later, a hook on writes to the memory directory, the scar ledger, `/witness` stubs, ADR
  minting and the handoff Lessons section proposes an event for confirmation.
- The judgment fields (anterior, posterior, matchers, guard) are authored at bank time. The
  engine only scans, flags, and tracks.

## Controls

- **Idempotent.** Dependent ids hash event id plus locator. Re-scanning writes nothing new.
- **Hit cap.** Record refuses a matcher over K hits (default 25) unless `--broad` is given and
  a reason is recorded. Measured below: specific matchers hit 0 to 2 files, broad ones hit
  168 to 849.
- **Storm cap.** Over the cap, write one summary row, not one row per hit.
- **Moot from git.** A flagged dependent resolves when the matched text is gone or the file
  is gone.
- **One-way doors.** An event that touches a write-locked item requires the write-lock
  declaration before any guard is wired.
- **Concurrency.** Append-only JSONL, re-fetch before write (shared-anchor-append rule).

## Reuse map

| Need | Existing piece |
|---|---|
| Storage, `review_by`, moot-from-git | risk register from `scripts/risk_sweep.py` |
| Axis (falsified vs moot) | claim-exit lattice memory |
| Horizon and defeater triggers | Part B of the freshness ADR candidate |
| Level 4 (priced scar) | `scar:` nodes in `_ARTIFACTS/catalog.json` (33 today, `tuition` null on all) |
| Capture source | `/witness` stubs in `_STATE/witness/` |
| Knot detection from numbers | Operator 21, later slice only |
| Rule precision over time | Accountant (Operator 19), which refuses to grade below n=30 |
| Canon fact mirroring | `canon_propagation_check.py` stays as is; canon facts keep their own path |
| Digest | night-moves reads the unbanked list and the day's events |

## Measured scan cost and noise (2026-10-06, 2,458 tracked files)

| Matcher | Hits | Files | Time |
|---|---|---|---|
| specific: `\b32 ADRs\b` | 2 | 2 (ADR-052 and the checker script, both mentions) | 0.7s |
| specific: integrity_gate near "manual" | 0 | 0 | 1.8s |
| broad: `\bmanual\b` | 353 | 168 | 0.9s |
| broad: `\bgate\b` | 4,884 | 849 | 1.2s |

Load of all files is 0.5s. Two consequences: scan in Python over `git ls-files`, not
`git grep -E` (BSD `git grep -E` on macOS has no `\b` and silently matched nothing), and the
two specific hits were mentions of the error, which is why citation-based exclusion is in the
rules.

## Failure modes

- **False defeat.** A loose matcher flags noise. Mitigation: the hit cap, a printed match
  count at record time, and citation exclusion.
- **Bad anterior authoring.** The engine trusts the author's matcher. Mitigation: record
  prints every dependent for a yes before it writes, in v0.
- **Blind spots.** Chat, the artifact database and untracked files are not scanned. Each event
  records the scopes it did cover, so absence of a hit never reads as absence of dependents.
- **Protection theater.** A register nobody acts on. Mitigation: unbanked events age in the
  night-moves digest, and guards report their fires.
- **Double counting with canon propagation.** Canon facts keep their own path; a bank event
  that defeats a canon fact links to the canon queue instead of re-flagging it.

## First slice (smallest thing that proves the loop)

`scripts/bank_event.py record | scan | list | --self-test`, stdlib only.

Acceptance:
1. `record` on a throwaway repo with one planted stale claim finds it, marks it unverified,
   and writes one dependent row. A second `record` of the same event writes 0 rows.
2. A matcher over the hit cap is refused without `--broad`.
3. A file that cites the event id is not flagged.
4. Removing the stale text resolves the dependent to moot on the next `scan`.
5. An event with no guard and no reason shows under `list --unbanked`.
6. The self-test runs in under 5 seconds and never touches the real register.

A real replay as the first proof: bank the "gate described as manual, actually pre-commit"
lesson with a `risk-rule` guard, and confirm the scan reports its blind spots honestly.

## Decisions needed from Zach

1. **Capture mode for v0.** Opt-in call at bank time (proposed), or a hook that proposes
   events from memory and scar writes from day one.
2. **Where unbanked events surface.** Night-moves digest only (proposed), or also
   session-start.
3. **Whether to cover the artifact database as a scan scope.** It closes today's blind spot
   but needs read access through the artifact tool, so it cannot run in a plain script.

## Not in scope

LLM-written anterior or posterior text, transitive propagation, automatic repair of
dependents, any change to canon propagation, and Operator 21 integration (revisit when a
bank event carries numeric confidences).
