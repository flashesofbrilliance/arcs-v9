Same job as AGENT_PROMPT.md (read it and the rubric first), with these changes:
- Your batch file is _STATE/gone-in-30s/retry-NN.json. Output file: _STATE/gone-in-30s/retry-NN.jsonl
- APPEND one JSON line to the output file immediately after coding each meeting (do not hold results in memory until the end).
- Pace: after each transcript fetch, run `sleep 12` via Bash before the next fetch. Never use Monitor or any wait that ends your turn.
- On a rate-limit error: `sleep 45` via Bash, retry that meeting once. If it fails again, write its line with transcript_ok=false and continue.
- Finish every meeting in the file. Reply only with: path, processed, in_scope, hits, fetch_failures.
