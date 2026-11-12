---
name: night-moves
description: Housekeeping: day's work is scattered, or a scheduled run hung or never produced a digest? End-of-day work digest. Sweeps the day's commits (all branches/worktrees), net-new tools, ADRs/DEWY receipts, and memory writes, then synthesizes a five-part digest — what shipped · what's next · what we learned · the new shape of tools-for-JTBD · net-new tools built — into a dated markdown log at _STATE/night-moves/YYYY-MM-DD.md. Use at the end of a work session to keep a running record of the day. Manual, subscription-tier, cheap (git + find, no network).
---

# /night-moves [YYYY-MM-DD] — the nightly work digest

> "This is what shipped. This is what's next. This is what we learned.
>  This is the new shape of the tools. These are the net-new tools we built."

A calm end-of-day pass that turns a day of scattered commits across ~40 worktrees
into one legible record. It does NOT commit, deploy, or send anything. It reads,
synthesizes, and writes one dated markdown file. Run it when you're done for the night.

Defaults to today; pass a date to re-digest a past day (`/night-moves 2026-08-10`).

## Cost + register
- Subscription tier, interactive. Gather is pure `git log` + `find` (no network, no LLM).
- Only the synthesis of sections 3–5 costs tokens. Keep it tight. This is a log, not an essay.
- Voice: WORLD.md register — calm, precise, plain language, no em-dashes (per user memory
  [[writing-avoid-emdashes-plain-language]]). Earned fidelity: say what the day supports, no more.

## Step 1 — Gather (deterministic, run first)

```bash
scripts/night_moves_gather.sh [YYYY-MM-DD]
```

This prints, for the day: SHIPPED (commits deduped by message), NET-NEW TOOLS
(files added under scripts/ operators/ .claude/{skills,workflows,commands}/ src/lib/),
DECISIONS (ADRs + `.dewy.json` receipts touched), MEMORY (auto-memory files written),
and FILES (touched paths bucketed by area — the raw signal for the JTBD-shape read).

The RISK block is the deterministic `scripts/risk_sweep.py --day` delta: breaking and non-idempotent
changes with a heal tier each. Carry it into the digest as a short "Risk delta" line (new count + any
high-severity item + its heal tier). Do not triage or fix findings in the digest; the register owns them.

Do not re-run git by hand. The script already sweeps `--all` (every branch/worktree
shares one `.git`) and dedups. Read its output; that IS your source material.

## Step 2 — Synthesize the five sections

Write `_STATE/night-moves/<DAY>.md` using the template below. Rules per section:

1. **What shipped** — group the deduped commits by workstream (the `scope` in
   `type(scope):` is the natural key: yuri, todd/prl, watcher, forge, ...). One bullet
   per workstream with the concrete outcome, not a commit-by-commit dump. Lead each with
   whether it reached the outside world (SENT / deployed / merged) vs internal-only.

2. **What's next** — pull open loops from: the latest `# Handoff` "Next session starts at"
   + "Blocking" lines, any commit that names a pending gate ("awaiting X", "pending Y
   approval", "BLOCKED on Z"), and unfinished slices ("slice 1", "1.3 prework only").
   Each item: the move + what it's waiting on. Do not invent work that isn't in the signal.

3. **What we learned** — the day's durable lessons. Source: ADRs minted today (each ADR is
   a learning), DEWY receipts, and memory files written today (each memory IS a distilled
   lesson — read its `description`). Phrase as portable principles, not narrative. Link the
   backing artifact (`ADR-044`, `[[memory-slug]]`).

4. **The new shape of "tools for JTBD"** — the interpretive read. From the NET-NEW TOOLS +
   FILES-by-area buckets, name how the *jobs* the toolkit can do shifted today. Not "we added
   a file" but "the forge JTBD now refuses to ship aspiration as fact (temporal gate), so
   'stand up a counterpart' is now honesty-gated by construction." One to four of these.
   This is where the digest earns its keep — connect net-new capability to the job it changes.

5. **Net-new tools we built** — the concrete list from NET-NEW TOOLS. One line each: the
   tool + the one job it does. Distinguish genuinely new (status A) from extended-existing.

6. **Sequential vs parallel (open PRs)** — paste the read-only output of
   `python3 scripts/dependency_sweep.py` (see "Reticulated dependency map" below).

## Step 3 — Write + report

- Write the file. Ensure `_STATE/night-moves/` exists (`mkdir -p`).
- Do NOT commit or deploy unless the user asks. If they do, land it from the `main` worktree
  per the deploy rules (`git push --no-verify`; content-only, build-excluded).
- Report back: the path, the shipped-count, and the single highest-charge line from section 4
  (the day's most important shape-change). Nothing more.

## Output template

```markdown
# Night Moves — <DAY> (<weekday>)

> <one-sentence read of the day: the through-line, in plain language>

## 🚢 What shipped
- **<workstream>** — <outcome>. <SENT/deployed/internal>. `<lead sha>`
- ...
_<N> commits across <M> workstreams._

## 🎯 What's next
- **<move>** — waiting on <gate>. <source: handoff / commit / open slice>
- ...

## 🧠 What we learned
- <portable principle> — `ADR-0XX` / [[memory-slug]]
- ...

## 🔧 The new shape of tools for JTBD
- **<job>** now <how it changed> — because <net-new capability>.
- ...

## 🆕 Net-new tools we built
- `<path>` — <the one job it does>. <new | extends X>
- ...

## 🕸️ Sequential vs parallel (open PRs)
- **Blocking roots:** <check name> blocks N PRs — fix once, unblocks all N.
- **Sequential pairs:** #A <-> #B share <files> — land one before rebasing the other.
- **Parallel-safe:** <count> PRs with no shared root and no file overlap — fan out freely.

---
_Generated by /night-moves · gather: scripts/night_moves_gather.sh + scripts/dependency_sweep.py · <timestamp>_
```

## Notes
- Re-running the same day overwrites its file (idempotent; the log is one file per day).
- The gather's author filter defaults to `Zach`; override with `NIGHT_MOVES_AUTHOR=...`.
- Complements the ADR/DEWY watcher (`scripts/adr_dewy_watch.py`, `surface_watch.py`): the
  watcher surfaces *candidates* mid-session; night-moves is the *ledger* of what the day was.


## Counterpart pulse (added 2026-08-27, seed: counterpart-pulse-check)

After the digest parts, run a read-only pulse on active counterpart loops: for each
project_*.md memory file not marked CLOSED/STALLED, Gmail-search the counterpart's addresses
(both directions, newest message date) and compare against the memory file's newest recorded
action. Inbox-ahead-of-memory = a drift line in the digest ("Robin replied Aug-26; memory last
records Aug-6"), with thread id + date as evidence. Inbound on a CLOSED loop is its own
high-signal line. Never auto-send, never auto-close - receipt lines only; judgment stays human.
Tuition: 2026-08-26, three stale-loop misreads corrected only by live inbox reads.

**Skip auto-messages when picking the newest message.** Calendar replies (subject starts
`Accepted:`, `Declined:`, `Tentative:`, `Updated invitation`, or the message is only an
`invite.ics`), Mixmax/tracker reminders (`notifications@mixmax.com`), and other no-reply senders
are not counterpart actions. Read the subject (THREAD_VIEW_MINIMAL) before calling drift; if the
newest message is an auto-message, step back to the newest human one. Write Gmail ids as
`gmail thread <id>` so `integrity_gate.py` does not read them as commits.
Tuition: 2026-10-10, Todd's "unread Oct-06 email" was a calendar acceptance (corrected in #1234).

## Model drift (added 2026-10-04, ported from #715 on 2026-10-06)

Run `python3 scripts/model_drift_check.py` (live with `ANTHROPIC_API_KEY`, else skipped). Any
DRIFT line goes under "What's next" as a question for Zach ("COURT runs Sonnet 4.6; Sonnet 5.5
is out. Switch after an eval?"). Never edit `src/lib/claude-models.ts` from the digest.

## Reticulated dependency map (added 2026-09-26, seed: induced-dependency-mapping)

Before writing section 6, run:

```bash
python3 scripts/dependency_sweep.py
```

This is deterministic — pure `git diff` + `gh pr view/list`, no LLM, no merges, no
comments. It classifies every currently-open PR into:
- **Blocking root**: a failing check shared by 2+ PRs (fix once, unblocks all of them).
- **Sequential pair**: two open branches touching the same file(s) vs main (merge-order
  risk, not a bug in either — land one before rebasing the other).
- **Unique defect**: a failing check on exactly one PR (that PR's own bug).
- **Parallel-safe**: no shared root, no file overlap — safe to fan out or ignore independently.

Known-noisy mechanical files (`_STATE/snapshot.json`, `_STATE/pulse.json`,
`_INBOX/*.jsonl` — rewritten by session-start hooks regardless of what a branch is
actually doing) are excluded from file-overlap detection; edit `NOISY_FILES` in the
script if a new one shows up.

The sweep is read-only by default. `--emit` additionally makes each blocking root
durable as a native GitHub relation (find-or-create one `[blocking-root] <check>`
tracking issue, then add `blocked_by` edges from the affected PRs) — additive only,
never closes or unlinks. Preview with `--emit --dry-run` first. Do NOT run `--emit`
as part of the nightly digest by default; filing issues is a judgment call, and a
transient red check shouldn't mint a tracking issue. Run it deliberately, when a
root has proven persistent.

Paste the script's read-only markdown output straight into section 6 — don't
re-summarize it, the clustering *is* the finding. If "Blocking roots" is non-empty, lead the digest's
"What's next" section with it: a shared root blocking N PRs is higher-leverage than
any single PR's own fix. Never auto-close, rebase, or merge anything from this section —
receipt only; sequencing decisions stay human.

Tuition: 2026-09-26, this session manually cross-referenced 5 disconnected tracking
systems (GitHub PRs, `_PATTERNS/ledger.json`, `_QUEUE/induced-backlog.jsonl`, per-worktree
`_STATE/handoff-progress.jsonl`, `decision_receipt`) by hand to answer "what's actually
blocking what" — and the sweep then caught a live collision (PR #533 vs #537, both
touching the same leak-check files) that the manual pass had missed.

## Universe contamination sweep (added 2026-10-15)

Run `python3 scripts/universe_sweep.py` once per digest. It is read-only over the clean-room universes
(`_STATE/job-search/universe/`), appends one dated receipt to `_INBOX/universe-drift.jsonl`, and exits 2 on a
hard finding. Report the verdict line under "What we learned". Any CROSS-NAME, ALIAS-LEAK, CONTAMINATED or
UNSOURCED finding goes under "What's next" as a fix to the atom that carried it (fix upstream, not the leaf).
A `canon-adapter-receipt` DRIFT (canon source changed, or a canon file names a counterpart) is a question
for Zach; never edit `_CANON/` or `_DECISIONS/` from the digest. Re-run `python3 scripts/universe_canon_adapter.py`
first when canon changed.

## Tool recall + Reading Room sweep (added 2026-11-11, receipt R-026)

Why: Zach, 2026-11-11: "I'm reinventing the wheel because I don't remember the tools for the job that
we've already created ... if you're not wiring or mechanizing or operationalizing them in situ ... I'll
forget them." This digest is how a tool reaches him the next morning (the 7:12 AM preflight reads it),
so the sweep runs here, once per digest. All three are read-only; none may edit a file.

1. `python3 scripts/tests/test_prior_art_recall.py --json`: one line per recall fixture. Any `"ok": false`
   goes under "The new shape of tools for JTBD" as "recall miss: <want> for '<query>' (top: ...)" and
   under "What's next" as a fix to the ranker or to that tool's own description. Never delete a fixture.
2. `python3 scripts/tool_orphan_audit.py`: report the count of tools nobody references and up to 3 of
   them by name under "The new shape of tools for JTBD", each with its one-line fix.
3. `python3 scripts/reading_room_sync.py --check`: one line under "What we learned": renders ok or stale
   (which), cache slices dirty of total, intake records waiting. Stale renders go under "What's next" as
   "run python3 scripts/reading_room_sync.py". If the script is absent, say "not run (absent)".
Any new tool listed under "Net-new tools we built" that is missing from runtime/specs/tool-catalog.json
gets "not yet catalogued" next to it.
