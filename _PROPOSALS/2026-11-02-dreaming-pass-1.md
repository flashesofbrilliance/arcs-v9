# Dreaming pass 1 (2026-11-02): proposed memory edits

Prototype of the out-of-band "dreaming" loop from Lamis Mukta's AI Native DevCon talk
(Context Engineering, Memory Systems, and Dreaming). Proposals only; nothing below has
been written to memory. Mark each **ACCEPT / REJECT / EDIT**.

**Ruling (Zach, 2026-11-02):** accept all except A5 and A6 (rejected). Applied the same day to
the project memory: new `long-inline-shell-goes-in-a-script-file` (A1), `preview-file-tab-page-tools-dont-act` (A4),
`never-attribute-unconfirmed-identity` (B3), `fix-defect-in-place-dont-delete` (B4); amended
`edit-jsonl-and-html-surgically` (A2), `bsd-sed-no-word-boundary-use-python-regex` (A3), the Vercel analytics
index hook (A7), `feedback-counterpart-text-first-person-singular-no-royal-we` (B1, memory half only; the grep
gate is still open), `fact-check-final-pass-vs-transcript` (B2), `writing-register-inquisitive-erudite-minimal-laconic` (B5).

- **Scout:** `python3 scripts/dream_mine.py --days 7 --min-sessions 2` (deterministic, ~2s,
  stdlib). Output: `_STATE/dream/mine.json` (gitignored).
- **Window:** 7 days, 67 arcs-v9 transcripts, 74 tool-error clusters seen in 2+ sessions,
  78 de-duplicated correction-shaped user turns.
- **Judgment:** this session read the clusters and the corrections, dropped false positives
  (gates working as designed, regex hits that were not corrections), and checked each
  candidate against the existing memory index first.
- **Prevalence** = distinct sessions (total hits). Session ids are the transcript file's
  first 8 characters.

## A. Shell and harness mistakes (tool errors)

| # | Pattern | Prevalence | Existing memory | Proposal |
|---|---|---|---|---|
| A1 | Multi-line `bash -c`/heredoc quoting breaks: `eval: unexpected EOF while looking for matching '` | 9 (12) e.g. d4f48498 | none | **New feedback memory:** put any command with nested quotes or over ~20 lines in a scratchpad script file and run it; never inline it. |
| A2 | `node -e` / `new Function` scripts dying with `SyntaxError: Unexpected end of input`; Playwright 30s click timeouts | 6 (19) e.g. ddddb1df, f6552a1d | `edit-jsonl-and-html-surgically` says "parse every script" | **Extend that memory:** the same rule covers throwaway node/JS one-liners; write to a file, `node --check` it first. |
| A3 | macOS has no GNU `timeout` (exit 127) | 3 (3) d4f48498, 126fc091 | `bsd-sed-no-word-boundary-use-python-regex` covers sed only | **Broaden that memory** into "macOS BSD userland": no `timeout` (use `perl -e 'alarm N; exec @ARGV'` or the tool's own timeout), no `head -n -N`, no `\b` in sed. |
| A4 | Page tools used on a `file://` preview tab ("This tab shows a local file") | 8 (11) | none | **New feedback memory:** to inspect a local HTML file, serve it (`python3 -m http.server` from its folder, via preview_start) or read it; page tools do not act on file tabs. |
| A5 | Foreground `sleep N && …` blocked by the harness | 5 (5) | none | **New feedback memory:** wait with Monitor/until-loops or `run_in_background`; never foreground sleep. (Low value: the error message already says so; REJECT is reasonable.) |
| A6 | Tool called as `bash` (lowercase) | 4 (4) | none | REJECT suggested: self-correcting in one call, costs nothing. |
| A7 | Vercel `count_events`/`count_pageviews` retried after 404 "Web Analytics not found" | 2 (8) ddddb1df | `vercel-web-analytics-not-enabled-arcs-v9` already says this READ path is broken | **No new memory; a recall gap.** The memory exists but the session retried 8 times. Proposal: rename its index hook from "Web Analytics IS on" to "Vercel analytics MCP 404 = broken read, don't retry", so the failure text matches the hook. |

Dropped as gates working as designed: pre-commit Kintsugi seam (6), jtbd-graph orphan (4),
user rejections (6), auto-mode "Merge Without Review" denials (4).

## B. Your corrections (judgment; the regex only nominated these)

| # | Pattern | Evidence (session: your words, paraphrased) | Existing memory | Proposal |
|---|---|---|---|---|
| B1 | Royal "we" in counterpart copy | 35dfa562/ad8934f8: "don't need to make it royal we (just me)" | `feedback-counterpart-text-first-person-singular-no-royal-we` exists | **Recall gap again.** Add it to the `pre-send gauntlet` / page-gate checklist as a grep (`\bwe\b` in counterpart-facing copy), per the Frustration Gate rule, rather than another memory. |
| B2 | Claims about what a counterpart said that the source does not support | ddddb1df: framing "isn't what Sam said"; "I literally shared that in email"; 35dfa562: "I said weeks not hours on the call" | `fact-check-final-pass-vs-transcript` exists | **Strengthen:** the check runs *before* first draft of any counterpart quote or number, not only as a final pass. Add "search the transcript/thread for the exact figure before stating it". |
| B3 | Unverified counterpart identity written into a page | 737e1ef4: "don't know that's the guy", repeated with "Again, remove" | `inbound-opportunity-three-gate-smoke-test` (identity, but for inbound calls) | **New feedback memory:** never name or attribute a person on a page or draft unless Zach or a primary source confirmed it; mark unknowns as unknown. Repeated correction in one session = high priority. |
| B4 | A fix that removes the broken thing instead of fixing it | ad8934f8: "you just cut off that piece entirely, that's not the fix" | `cut-not-add-provable-architecture` (could be misread as license) | **New feedback memory:** a visual or layout defect is fixed in place; deleting the element is a different change and needs his OK. Add a "not this" line to `cut-not-add`. |
| B5 | "I don't understand, help me / explain like I'm 5" after dense output | 35dfa562 (x2), 77cf38b8, cc50e305 | `writing-register-inquisitive-erudite-minimal-laconic`, `always-expand-acronyms` | **Strengthen register memory:** when presenting a choice or a mechanism, lead with one plain sentence of what it does for him before structure. Four sessions in a week. |

## Not done in this prototype (next if it earns its keep)

1. Subagent fan-out over full transcripts (the talk's design). Here the scout plus one
   reader was enough; 67 transcripts is small.
2. Scheduling. Lamis's guidance and the Managed Agents docs suggest weekly, with human
   review of every edit. Candidate: fold into the weekly `token-kaizen` routine.
3. Applying accepted edits. On your marks, one session writes them and updates `MEMORY.md`.
4. The correction regex is noisy (most hits are ordinary "don't"). A cheap improvement:
   only count a turn that follows an assistant turn and is under 200 characters.
