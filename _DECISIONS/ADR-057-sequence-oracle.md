# ADR-057 — The sequence oracle: a git-serialized ID + time authority for the distributed model

**Status:** Accepted · 2026-08-13
**Allocated by:** the oracle itself (`oracle next adr` → 57) — dogfooded on creation.

## Context
Parallel sessions/branches guess "the next ADR number" independently and **collide**. A 30-day sweep
found this is not hypothetical: **on main today ADR-024, 025, 031, 032 are each doubled** (two distinct
merged decisions sharing one number), plus cross-branch collisions (033×3, 039×3, 055×2). Humans cannot
hand-allocate a shared namespace concurrently. It needs a **serialization authority** — exactly as git
serializes file order (germinate `SPEC.md`, concurrent axis).

## Decision
`scripts/oracle.py` — a sequence + time authority, home in the `_SEEDS` bank.
- `oracle next <ns>` allocates the next monotonic id for a namespace (`adr`, `seed`, `receipt`, …) from
  a committed counter `_SEEDS/_oracle.json`. **Allocation is authoritative only once committed:** git's
  non-fast-forward rejection *is* the atomic gate — two sessions cannot both keep 57; the loser re-fetches
  and takes 58. The same guarantee git already gives tracked files, applied to a number namespace.
- `oracle now` emits a **grounded** ISO timestamp (host clock, surfaced explicitly — never a confabulated
  date; complements the session-start clock-grounding).
- `oracle audit adr` reports collisions / gaps / next-free (read-only reconciliation authority).

**Honest scope (refusal-to-overclaim + ADR-044 temporal-provenance):** "atomic clock oracle" is the
north-star metaphor. This is a **logical clock backed by git**, not GPS/atomic hardware; wall-clock is
the host's, surfaced not silently trusted. It MAY later be NTP-backed. We do not claim more than git +
grounded-`date` actually deliver.

## Consequences
- **Going forward:** every numbered artifact draws its id from the oracle. New collisions are prevented
  by construction (allocate → commit → git serializes).
- **The existing mess is NOT auto-rewritten.** References say only "ADR-032" and do not disambiguate which
  of two 032s they mean; some collided ADRs are governing (ADR-032 zero-trust). Renumbering is therefore a
  **human-ratified** act per pair — see the remap proposal (`_INBOX/adr-collision-remap.jsonl`). NOTOMATION:
  the oracle detects and prevents; the human disambiguates canon identity.
- First client: the ADR namespace. Generalizes to seed ids, receipt ids, tao/ordinal numbering.

## Lineage
[[git-is-the-write-lock-untracked-is-the-gap]] · [[compaction-serialization-substrate-public-good]] ·
[[dont-confabulate-timestamps-verify-with-date]] · ADR-044 · ADR-055 · germinate `SPEC.md`.
