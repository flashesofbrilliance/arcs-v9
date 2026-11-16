# projection-map

Counts how Zach projects on calls, from Granola transcripts, with no model judgment in the scoring.
Private by construction: this folder's `.gitignore` admits only code and docs. Transcripts, manifests,
titles, labels and results stay local and are never committed.

## Pipeline
1. **Fetch**: a helper calls the Granola `get_meeting_transcript` tool (fetch only, writes nothing).
2. **Extract**: `python3 -I extract.py <helper-log.jsonl> raw_exact/` pulls the exact tool output from the helper's log
   and checks each file's length against Granola's `total_chars` (MATCH / MISMATCH). Never retype transcripts.
3. **Score**: `projection.py` (per call: talk share, questions, uptake, length-controlled lift, circuit breakers).
   Laconic breaker = a turn of 150+ words; Grug breaker = >15% words of 3+ syllables or 2+ insider terms;
   mid-curve = both on one turn.
4. **Pool**: `pool.py [--sure-only]` reads `manifest.json` (`{audience: [ids]}`, optional `_unsure`), prints groups,
   pre-registered verdicts and permutation tests.
5. **Outcomes**: `outcome.py` reads `titles.tsv` (`id8<TAB>date<TAB>title`) and labels a call Advanced if a later
   call shares a name or company token. First-name-only matches are unreliable; exclude them in a sensitivity run.

## Rules
- Write predictions in `preregistration.md` (template here) before computing anything.
- Speaker labels: `Microphone` is Zach; `System audio` (optionally `(Name)`) is everyone else; timestamps optional.
  Three parser bugs each flipped a verdict once: audit labels on any dropped call before trusting results.
- Redact (cards, phones, emails, ID numbers) before any copy leaves the machine; delete raw copies when done.

See `ACCUMULATION.md` for the basin states, the frozen discovery/test line, and the candidate ledger (ADR-081 instance).
