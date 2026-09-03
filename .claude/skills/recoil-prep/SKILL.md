---
name: recoil-prep
description: T-minus phase. Gather context (calendar, gmail, granola, gamma, profile) for a counterpart and fill the Pre-Call + Ex-Ante tabs of their engagement SSOT, then render the internal war-room shell. Use before a call.
---

# /recoil-prep — fill Pre-Call + Ex-Ante, render the war-room shell

Operates on an existing SSOT (from /recoil-new). Fills the first two disciplines and renders.

## Step 1 — gather (breadth, then depth)
Pull everything available on the counterpart, in parallel where possible:
- **Calendar** (`mcp__<calendar>__list_events`) — the meeting, time, attendees.
- **Gmail** (`search_threads` on their address/domain, then `get_thread` on the substantive ones) —
  prior correspondence, what was promised, what went unanswered.
- **Granola** (`query_granola_meetings` / `get_meeting_transcript`) — any prior calls. Large
  transcripts overflow the tool and save to a file; extract via python/shell, don't skip them.
- **Gamma** (`get_gammas` by name, `read_gamma`) — decks you built for or about them.
- **Profile PDF / LinkedIn** — bio, background, the orthogonal-echo hooks.

## Step 1.5 — the pre-prep gate (ADR-075 amendment A; blocking)
Before filling anything, write the `pre_prep` block into the SSOT from the RAW sources gathered in
Step 1 and run `python3 scripts/pre_prep_gate.py runtime/recoil/generated/<id>.json`. It refuses on:
no verbatim transcript/thread on disk · no enumerated verbatim asks · reader or Receipt Loop stage
undeclared · artifact about the reader without the reader asking · no format spec from their words
(or explicit none) · no arriving-state quote · read budget over a tenth of build budget. **Do not
proceed to Step 2 on a FAIL.** The block is the ex-ante receipt for the artifact itself; /recoil-close
scores it. Summaries (`query_granola_meetings`) never satisfy the raw-source check.

## Step 2 — fill the SSOT (internal)
Into `runtime/recoil/generated/<id>.json`:
- **Pre-Call tab**: True North (one-sentence posture), Context (date / register / their goal / predicted
  Y-gate), Intel (who they are, most-diagnostic first), Questions + landmines.
- **Ex-Ante tab** (`receipt` block): file the decision receipt BEFORE the call — D/E/W, a *falsifiable*
  hypothesis, predicted Y-gate, pre-committed move, the belief most likely to update, the falsifier.
  This is what /recoil-close scores later. Do not skip it. (ADR-068: this is the mandatory
  ex-ante print; its fates are scored/unscored, and unscored is a drift receipt.)
- Set `meta.provenance` (sources + one load-bearing prior quote if any).

## Step 3 — render
```bash
./scripts/recoil --data runtime/recoil/generated/<id>.json --audience internal --format html \
    > public/<name>-war.html
```
Wire the subdomain (`next.config.ts` beforeFiles + `vercel domains add <name>-war.arcs.care`), gated
with the non-guessable internal password. Commit on the main worktree, push, verify live.

## Guardrails
- Everything here is `audience: internal`. Reads about the counterpart are war-room only.
- **Fact-check discipline**: quotes must be faithful to the source ([[fact-check-final-pass-vs-transcript]]).
- **Clean room, two ends** ([[pull-not-push-pre-render-legibility-gate]]): `pre_prep_gate.py` on the way in (Step 1.5), `cold_reader_gate.py` on every rendered page on the way out (/recoil-ship).
- **Active listening > magical thinking** ([[active-listening-over-magical-thinking]]): if the gathered
  record contains a disqualifying signal, log it now; don't build a pursuit that ignores it.

## Next
Have the call. Then run **/recoil-close** to score the ex-ante and fill the back four tabs.
