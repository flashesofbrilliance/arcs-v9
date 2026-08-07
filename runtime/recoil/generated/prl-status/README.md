# PRL daily exec-status routine

A weekday 9:31 AM (local) routine that drafts a visual exec-status email to Todd,
and only when the status board actually moved since the last one.

## Two copies (by design)
- **Operational SSOT (what the scheduled task reads):**
  `/Users/zharris/.claude/scheduled-tasks/prl-daily-status/board.json`
  This path is stable across git worktree churn, which is why the task uses it.
- **Versioned reference (this folder):** the committed copy, so the engine is in git history.

When a workstream moves, edit the **operational** `board.json` (the one under
`~/.claude/scheduled-tasks/prl-daily-status/`). Keep this repo copy in sync when convenient.

## Files
- `board.json` - the source of truth: phases -> items -> {name, status, note, refinement_needed?, owner}.
- `render_status.py` - renders an email-safe HTML body + text fallback + a content signature. Stdlib only.

## Statuses
`not_started` | `in_progress` | `troubleshooting` | `pending_review` | `acceptance_testing` (+ optional `refinement_needed`) | `done`

## How the "only when changed" gate works
`render_status.py --changed-since last-sent.json` exits 0 ("changed") or 3 ("unchanged"),
comparing a hash of the meaningful fields (name/status/note/refinement) against the last draft.
After a draft is created, `--mark-sent last-sent.json --sent-date <YYYY-MM-DD>` records the new
signature, so tomorrow only fires if something moved.

## Delivery
Draft-only today: the routine creates a Gmail **draft** to todd.hotes@prlresins.com (never sends).
Zach reviews and sends. To upgrade to true hands-off auto-send, authorize the Resend connector and
switch Step 3 of the task from create-draft to send (note: Resend sends from a verified domain, not
zach.harris@gmail.com).

## Manual run
`cd ~/.claude/scheduled-tasks/prl-daily-status && python3 render_status.py --html /tmp/x.html` then open it.
Or use "Run now" on the task in the Scheduled sidebar (recommended once, to pre-approve the Gmail tool).
