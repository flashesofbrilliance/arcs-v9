# Token Kaizen — weekly window-cost improvement loop

**Kaizen = one small, continuous improvement per cycle.** This routine keeps finding
ways to lower the ARCS per-session window/token cost, one concrete cut per week, and
tracks whether the last cut landed. It builds ON the one-off analyses
(`_PATTERNS/2026-07-19-token-efficiency-audit.md`; the 2026-09-08 cloud "Token cost
ROI analysis" + "Token-efficient handoff" sessions) — it is the missing *cadence*, not
a re-analysis.

## Grounding (why the FLOOR, not the work)
A 342-turn session ran ~15.4M effective tokens, ~90% of it the FIXED per-turn floor
(system prompt + tool schemas + auto-loaded CLAUDE/AGENTS/WORLD re-read every turn),
not the work. Effective-token weights: `cache_read x0.1 · cache_write x2 · output x5`.
Caching already does "load once, hold" — don't chase it. Compaction helps the tail,
not the floor. **Levers, biggest first:** (1) prune the per-session connector/plugin
roster, (2) leaner auto-loaded docs, (3) fewer/shorter sessions + fold earlier.

## The loop (weekly)
1. `python3 scripts/token_kaizen.py` — measures the floor deterministically, appends a
   dated row to `_STATE/token-kaizen/ledger.jsonl`, prints the delta vs last run and a
   ranked candidate-cut shortlist. (Mechanical; no LLM needed.)
2. Read the delta: **did last week's cut land?** (`docs_tokens_est` down = the doc lever
   landed; connector/session levers the human confirms — they're not repo-visible.)
3. Pick **exactly ONE** cut for the coming week from the shortlist — smallest change with
   the biggest measured leverage. Judgment stays human-owned (NOTOMATION): the script
   ranks, the human chooses.
4. Record it: `python3 scripts/token_kaizen.py --record-cut <lever> <target> "<why>"`
   (or edit the row's `this_cut`). Do the cut if it's mechanical and safe (doc trim,
   allow-list collapse); leave connector/session-behavior cuts as a one-line nudge.
5. One-line report: floor now, delta, last cut's fate, this week's cut. Cheap — git +
   a stdlib script, no network.

## Scope / anti-duplication
- arcs-v9 only. The existing `arcs-field-os-weekly` scheduled task targets a DIFFERENT
  repo (`/Users/zharris/A.R.C.S.`) — do NOT bolt onto it.
- The cloud "Token cost ROI" sessions are idle one-off analyses (can't be scheduled,
  can't message back). This routine consumes their findings; it does not re-run them.

## Falsifier
If four consecutive weeks show no landed cut AND no new lever surfaced, the floor is at
its irreducible minimum for the current architecture — pause the cadence to monthly and
say so, rather than manufacturing busywork.
