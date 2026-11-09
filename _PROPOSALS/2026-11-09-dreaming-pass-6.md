# Dreaming pass 6 (nightly, 2026-11-09)

Proposals only. Nothing here is applied; Zach rules each row ACCEPT, AMEND or REJECT.

## Header

- Worktree: /tmp/dream-2026-11-09 at origin/main 99b4789d.
- Quiet-night check: 76 commits across all refs in the last 26h; 0 files changed under ~/Downloads/gauntlet-2026-11-06/ in 26h.
- `python3 scripts/dream_mine.py --days 2 --min-sessions 2`: 20 transcripts, 7 error clusters (>= 2 sessions), 4 corrections.
- `python3 scripts/dream_mine.py --corpus --stale-days 45`: 1346 docs, 139 dead cites, 108 verifications older than 45d, 0 near-duplicate memory pairs.
- `python3 scripts/orphanage.py --check`: 44 orphans, 10 cited, 3 unregistered, 0 awaiting a fate.
- Slice: dropped everything in `_PROPOSALS/*-dreaming-*.md` (passes 1 to 3) and in open draft PRs #2061 (pass 4) and #2071 (pass 5). RESIDUE-for-dream-2026-11-06.md is already cited by pass 4, so it is not re-used.
- KINTSUGI read: claude.ai Project claude/KINTSUGI.md, rows G1 to G43, read this pass. G43 (2026-11-08) is new since pass 4.
- Under 40 items: judged inline, no scouts. Transcript causes were checked in the session JSONL under ~/.claude/projects/, not only in the scan's truncated excerpts.

## Proposals

| id | pattern | prevalence | existing guard | proposal | file it would edit | risk |
|----|---------|-----------|----------------|----------|--------------------|------|
| H1 | `page_gate.py` passes a page that the pre-commit "kintsugi immune system" then blocks for net-new Impeccable design findings. The gate the rules say to run before showing a page does not run the detector the commit runs. | 2 sessions: 6055c769 (2026-11-09 01:15Z, public/gravity-brief.html, 2 findings: 11px body text, 0.06em body letter-spacing; the commit message already said "page-gate pass (--counterpart)"); 5adfa139 (2026-11-08 19:39Z, _ARTIFACTS/louisville-proposal/source.html, 5 findings, and an earlier block of 9 color and radius findings). KINTSUGI rows: G36 (visual build shipped without impeccable or page_gate). | `git grep -c impeccable scripts/page_gate.py`: 0. Detector call lives only in scripts/git-hooks/pre-commit lines 744 to ~820 (`$HOME/.claude/skills/impeccable/scripts/impeccable detect --json`, ratchet against HEAD). Memory `run-the-repos-own-gates-before-shipping` exists but cannot help when the gate itself is partial. | Add a STATIC check `E design-debt` to page_gate.py that runs the same detector with the same HEAD ratchet (n > HEAD n fails), and warns (not passes silently) when the impeccable binary is missing. Better still: move the hook's block into one function both call, so they cannot drift. | scripts/page_gate.py (and the kintsugi block of scripts/git-hooks/pre-commit if shared) | page_gate depends on a file under ~/.claude, absent in cloud sandboxes; must degrade to a visible warning. Slower by one detector run per page. |
| H2 | Counterpart copy drafted from a thread preview or the newest messages instead of the full thread and the call notes. Recall gap: the memory exists and did not fire. | KINTSUGI rows: G31 (2026-11-06, asked Zach facts Gmail held), G43 (2026-11-08, MyAlly intake and email drafted from a 33-message thread's preview; four sent terms and four open questions missed). 2 rows. | Memory `prep-read-full-thread-and-archive-before-structuring` (index line 36 of ~/.claude/projects/-Users-zharris-arcs-v9/memory/MEMORY.md, hook "Prep: full thread + archive first"). Its description scopes it to "interview or counterpart prep"; G43 was an email draft and an agreement revision, which the hook does not name. Repo grep for "full thread", "message preview" in CLAUDE.md, AGENTS.md, .claude: 0 hits. | Sharpen the description to also fire on "drafting any email, agreement, or counterpart page", add one How-to-apply line: "a search preview is the oldest few messages, not the thread: open every message and every Granola or Fathom summary with that counterpart, list the terms already sent and the questions they asked, and diff the draft against both". Change the MEMORY.md hook to "Counterpart copy: full thread + calls first". | ~/.claude/projects/-Users-zharris-arcs-v9/memory/prep-read-full-thread-and-archive-before-structuring.md; MEMORY.md line 36 | MEMORY.md is 23,952 bytes against the 24,576 budget (budget applicability per pass 4: unverified); keep the hook change net under ~30 bytes. |

## Evidence updates to proposals still open (not new proposals)

- Pass 5 F1 (bash 3.2.57 harness refusal, exit 126): now 7 sessions, up from 5. Strengthens the case for ruling F1.
- Pass 5 F4b (orphanage reports open-PR branches as unregistered orphans): now 3 hits, up from 1. scripts/engagement_calibrate.py and scripts/engagement_progress.py on claude/myally-progress (PR #2066 OPEN), scripts/myally_primer_terms.py on claude/myally-primer-terms (PR #2070 OPEN). No `--intake` run, per F4a.

## Not proposed (dropped after checking)

- `engagement_render.py` self-test `AssertionError` ("fixed $1,500" / "Dec 4"), 2 sessions on 2026-11-08 (e70f5a1d, 7757e3eb): both mid-edit in worktrees; `python3 scripts/engagement_render.py --self-test` passes on main 99b4789d. The test did its job.
- `JSONDecodeError: Expecting value`, 2 sessions (22d2d282 2026-11-07, 7757e3eb 2026-11-09): different causes (one `raw_decode` on a `find()` that returned -1); no shared pattern.
- 4 corrections: all 2026-11-04 to 11-07, about client scope and job-pipeline judgment, none points at a repo behavior.
- Corpus: 139 dead cites (pass 5: 132) and 108 stale verifications (same). Classes ruled in pass 3 (D1 to D4); the 7 new dead cites were not isolated (no saved per-item list from pass 5). Unverified.

## False-positive shapes to drop from the scan

- `head: illegal line count -- 0` rode along in the "book the seam" cluster: it came from Claude's own `git stash list | head -0` (BSD head rejects 0), not from a hook. The cluster key should be the hook's last line, not the first stderr line.
- `[resize_window] Viewport emulation cleared ...` (2 sessions): an informational tool message, not an error.
- User tool rejections (3 sessions): already noted in passes 4 and 5.
