You are coding call transcripts against a PRE-REGISTERED rubric. Do not invent categories. Do not summarize calls.

Working directory: /Users/zharris/arcs-v9/.claude/worktrees/arcs-demo-ahmed-b0db74
Rubric (read it first, fully): _STATE/2026-09-03-gone-in-30s-preregistration.md
Your batch: _STATE/gone-in-30s/batch-NN.json (list of {id,title,date})

For EACH meeting in your batch:
1. Call the Granola MCP tool `get_meeting_transcript` with meeting_id = id. This returns the RAW transcript. Never use query_granola_meetings or get_meetings (summaries are not evidence).
2. Speaker labels: "Me" = Zach. "Them" or any named non-Zach speaker = counterpart. Only counterpart lines can be hits.
3. Decide scope: if Zach presented an artifact, a page, a report, a deck, a scan, OR explained ARCS/his method, the call is IN SCOPE. If not (pure catch-up, Zach being interviewed with no artifact, logistics), mark na=true and still record any C1-C5 hits if they occur (they count as observations but the call is excluded from the denominator).
4. Code hits per the rubric tags C1..C5 and misses M1/M2. Every hit MUST carry the verbatim line from the transcript (copy exactly, may trim with ... at ends). No paraphrase. If you cannot quote it, it is not a hit.
5. For each hit note prompted=true if Zach had asked for feedback on format/consumability in the preceding ~10 lines, else false.
6. Also record up to 3 Z-side lines (Zach saying the mechanism about his own material) under zside, verbatim.

Write ONE JSON line per meeting to: _STATE/gone-in-30s/batch-NN.jsonl  (create/overwrite that file; NN = your batch number)
Schema per line:
{"id":"...","title":"...","date":"...","in_scope":true|false,"artifact_presented":"one phrase or null","hits":[{"tag":"C1".."C5","quote":"verbatim","prompted":true|false}],"misses":[{"tag":"M1"|"M2","quote":"verbatim"}],"zside":["verbatim",...],"transcript_ok":true|false,"note":"<=20 words, optional"}
If the transcript fetch fails or is empty, write the line with transcript_ok=false and move on. Do not retry more than once.

Constraints: stdlib only if you write helper code; do not edit any other file; do not commit; do not read files outside _STATE/gone-in-30s and the rubric. When done, reply with ONLY: the path you wrote, count of meetings processed, count in_scope, count with >=1 hit.
