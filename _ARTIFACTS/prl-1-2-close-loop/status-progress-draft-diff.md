# DRAFT diff — prl.arcs.care/status/progress (NOT applied; Zach says ship, then apply + deploy from main worktree)

Source file: `public/prl-status-progress.html`. Verified wins as of 2026-08-26. All edits below are
proposed; nothing deployed this session.

## 1. Meta line (line ~90)
- FROM: `Aug 18, 2026 · all work sandbox/staging · zero production impact`
- TO:   `Aug 26, 2026 · all work sandbox/staging · zero production impact`

## 2. BLUF (lines ~105-108) — append one sentence
Append after "…without waiting on any outside access.":
`Since then: the duplicate-matching bug is fixed and published, every test lead is cleaned out
of the sandbox, and your 24-month baseline is pulled for the first time.`

## 3. Checklist rows
- **Duplicate protection** (line ~122): sub → `Same person chatting twice updates their existing
  lead instead of creating a copy. A blank-email edge case that could match the wrong record is
  now guarded and published (v5). One 2-minute live test remains.` stat stays `built`, or `done ·
  published` if Zach prefers.
- **Baseline report** (line ~146): mark → check, stat → `done · pulled`. sub → `24 months pulled:
  942 leads, 4,238 opportunities. Headline finding: $43.7M of opportunities (48%) have no lead
  source recorded, so channel value is currently unprovable. The chatbot tags its source on every
  lead.`
- **Rep notification** (line ~140): sub append `Build sheet is written and verified; needs one
  editor session to install.`
- **NEW row** after Duplicate protection:
  `✓ Sandbox hygiene — Every synthetic test lead deleted and verified gone; the one record the old
  bug touched is repaired and clean. stat: done · verified`
- **NEW row** after Rep routing:
  `→ Unassigned-lead safety net — Daily digest of leads that route to no rep (currently 12 states),
  so nothing sits while territory is decided. Built as a sheet; needs one editor session. stat: staged`

## 4. Worked-around table (line ~166+) — add row
`| Blank-email chats matched the wrong CRM record | Added a guard: no email means create-new, never
update | Published (v5), record repaired |`
