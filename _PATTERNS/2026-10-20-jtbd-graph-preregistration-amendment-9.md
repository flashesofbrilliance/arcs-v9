# JTBD graph pre-registration, amendment 9 (2026-10-20): counter-agent fixes to amendment 8

Amends `_PATTERNS/2026-10-20-jtbd-graph-preregistration-amendment-8.md`. Written after the Sprint 6
claims-skeptic run on head c34bdba9 and before the fixes below were coded.

## What was seen first
1. Rule (c) is too loose: `get_purge`, `query_drop_table`, `list_then_destroy`, `search_unsubscribe`
   and `read_ack` classify read. The code followed the rule. None of the 453 read rows in the real
   snapshot had a side-effect name.
2. The gates and `jtbd(job)` accepted `receipt:<id>` evidence when the id was anywhere in the receipt
   projection, even on a line naming a different job. The adapter itself never emitted such an edge.
3. With ids near 900 characters, the answer could exceed 1,000 tokens through fields that were never
   trimmed (the MCP field itself held).
4. A `captured_at` in the future read as fresh; a schema written as a short JSON string in `purpose`
   passed the leak check.

## Rule changes
- Rule (c): these words join the write verbs: purge, drop, destroy, wipe, clear, archive, unarchive,
  unsubscribe, subscribe, ack, dismiss, revert, rollback, terminate, cancel, close, open, lock, unlock,
  invite, block, unblock, ban, flush, prune, sync, push, pull, refresh, reload, scrape, crawl, train,
  pay, charge, refund, order, book, schedule, notify, ping, trigger, invoke, call, exec, eval, shell,
  sudo, grant, deny, allow, link, unlink, attach, detach, mute, pin, unpin, star, like, follow,
  unfollow, vote, review, comment, tag, untag, reorder, sort, split, join, fork, clone, build, compile,
  install, uninstall, migrate, seed, backup, export, download, print, render, transcode, convert,
  translate, summarize, analyze, process, handle, do, make, perform.
  Read still requires the first remaining token to be a read verb.
- Rule (d): `receipt:<id>` evidence resolves for an edge only when that id's line in the projection
  names the edge's own `tool_id` (`from`) and `job_id` (`to`). The same check applies in `jtbd(job)`,
  which also accepts only edges with `rule = mcp-receipt`.
- Rule (e): if the answer is still over budget after the MCP and existing trims, drop `receipts`, then
  `matched_jobs`, then cut `assembly` to its first entry, then shorten any id over 120 characters with
  a trailing `...`. The budget holds unconditionally.
- Rule (a): a `captured_at` after today is STALE. A `purpose` that looks like JSON (starts with `{` or
  `[`, or contains `"type":` or `"properties"`) is a leak.
