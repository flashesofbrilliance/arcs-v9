# JTBD graph pre-registration, amendment 10 (2026-10-20): counter-agent round 2

Amends amendments 8 and 9. Written after the round 2 claims-skeptic run on head 87f3fffb, before the
fix below was coded.

## What was seen first
1. Rule (c) matched exact tokens only: `list_dropped` and `get_purges` classified read, and so did
   `get_nuke`, `query_truncate`, `fetch_evict`, `read_consume` and `get_pop`.
2. The gates accepted a `tool:mcp` serves edge with no `receipt:` item at all (the receipt check was
   vacuously true). This broke amendment 8 rule (d) as written, so the fix needs no new rule.

## Rule change
- Rule (c): before looking up a token, also try its verb forms: a trailing `ed`, `d` or `ing` removed,
  then with a doubled final consonant collapsed (`dropped` -> `drop`) and with `e` restored
  (`wiping` -> `wipe`); a write verb in any of these forms makes the name write. Plural `s`/`es` is not
  stripped: a first draft that stripped it was measured on the real index and turned 34 read tools
  into write through plural nouns that are also verbs (`list_comments`, `list_labels`, `list_issues`,
  `get_records`, `list_workflow_runs`). So `get_purges` stays read: a known miss. These words join the write verbs:
  nuke, truncate, evict, consume, pop, kick, expire, invalidate, void, burn, reap, scrub, erase, mutate.
- Known limit, recorded rather than hidden: a deny list can always miss a new verb. The guard behind
  it is that the class is advisory and `jtbd(job)` flags only `write`; an allowlist of nouns was
  considered and not adopted because nearly every read tool would turn into write and the flag would
  stop meaning anything. Revisit if a real read-class tool with a side effect is found.
