# Claude Code Pickup — ADR-085: Serialize the collision points, not the sessions: a main write-lock and hot-file leases on git refs

> **Status:** DRAFT
> **Generated from:** `_DECISIONS/ADR-085-main-write-lock-and-hot-file-leases.md`
> **Horizon:** QUARTER | **Conviction:** UNSET
> **Auto-generated:** 2026-10-10 22:10 UTC

---

## What was decided

### (a) Lock semantics
| Verb | Rule |
|---|---|
| acquire | free or absent: grant. Held live by me: extend (re-entrant). Held live by another: refuse, name holder. Held but expired: refuse with "declare it with takeover". `--wait N` polls. |
| release | holder only; a crashed holder that comes back after a takeover cannot release the new holder's lock |
| takeover | only when `now > expires_at + grace`; records `took_over_from` |
| status | exit 0 free, 3 live, 4 stale |

`merge_train.sh --lock` acquires before `git fetch origin main` (so BASE is read under the lock),
holds through build and push, and releases in its EXIT trap. TTL 30 min, renewed (re-entrant

## Implementation pointer

See ADR for details.

## Full ADR

See `_DECISIONS/ADR-085-main-write-lock-and-hot-file-leases.md` for complete context, options considered, and rationale.

## Done when

`_QUEUE/PENDING.md` ADR-085 row updated to `DONE` + commit.
