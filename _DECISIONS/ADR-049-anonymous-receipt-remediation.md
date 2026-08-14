# ADR-049 — Anonymous Receipt Remediation: Conform Forward, No Retroactive Purge, Opt-In Save

> **Status:** DECIDED
> **Date:** 2026-07-13
> **Commit:** Phase 1 `8b486e8` (shipped, verified in prod); Phase 2 this commit

---

## D — The Decision

**Sharp question:** Production stored anonymous receipts (question text, `userId: null`)
while `/trust` §1 and `/privacy` promised "anonymous sessions: nothing is stored / no auth
= no write path." How is the violation remediated — code, copy, and the 48 pre-fix rows?

**Chosen:**
1. **Conform the code to the promise, never the promise to the code** (Phase 1, shipped):
   anonymous runs persist nothing — no Receipt, no SageTrace, no PrepSession, no claim
   cookie. Results render ephemerally client-side (`eph_` ids, sessionStorage).
2. **No retroactive purge** — operator write-lock answer (Zach, 2026-07-13): receipt links
   are made to be shared, and some anonymous receipts are already referenced in the wild;
   deleting them breaks those references. Verified mechanically: legacy anonymous receipts
   remain publicly fetchable by ID post-fix (link-possession access, unguessable cuids).
3. **Opt-in save** (Phase 2, this commit): an anonymous bearing can be kept by signing in
   — the write happens strictly post-auth, so "no auth = no write path" holds to the letter.
4. **Visible repair seam, not silence** (Kintsugi): trust contract v1.2 adds a dated
   disclosure of the defect, the fix commit, and why the legacy rows were retained.

---

## E — Entity / System

- `/api/compass` + `/api/prep` (write guards, Phase 1) · `/api/receipts/save` (new, Phase 2)
- `/receipt/[id]` ephemeral surface · `ClaimAnonymousReceipts` (legacy claim by sessionId
  stays live — the retained rows remain claimable; + new pending-save consumer)
- `_CANON/trust-contract.md` v1.1 → v1.2 · `/trust` page
- The 48 retained rows: `SELECT COUNT(*) FROM "Receipt" WHERE "userId" IS NULL`

## W — Window

Phase 1 + 2 immediate. Revisit: if a user requests deletion of a pre-fix anonymous
receipt (honor it — the retention is a preservation-of-references default, not a refusal);
or if Phase 3 extracts the duplicated receipt-assembly into a shared builder.

---

## Why not the alternatives

- **Amend the promise to match the old code:** doesn't cure the past; triggers the privacy
  page's own 30-day-notice rule; the public repo makes the contradiction provable; the
  promise is the positioning.
- **Purge the 48 rows:** breaks in-the-wild receipt links — receipts exist to be durable
  references. Operator declined under write-lock.
- **Server-side re-verification of saved bearings:** re-running the pipeline would change
  the bearing the user chose to keep. Instead: Y-gate is recomputed server-side, payload
  fields are validated/clamped, and rows are marked `surface: "EPHEMERAL_SAVE"` so corpus
  analytics can distinguish client-attested rows (e.g. the ADR-023 baseline should filter
  or segment them).

## Consequences

- Anonymous UX preserved end-to-end (same result surface, NOT-STORED banner, sign-in nudge).
- The trust contract carries a permanent dated seam — repaired is never presented as
  never-broken (`repair_nci_discount` principle from the Kintsugi spec).
- Debt (accepted, documented): `/api/receipts/save` intentionally mirrors part of the
  compass route's receipt assembly; extraction into a shared builder is Phase 3 work.
- The corpus now has a provenance split: `ORIENT` (pipeline-minted) vs `EPHEMERAL_SAVE`
  (client-attested). Baseline measurements should note which slice they run on.

## Y — Gate

GREEN / HIGH / STABLE on Phases 1–2 (verified in production: anonymous ops write zero
rows; DB counts bit-identical across five anonymous operations). Purge question: CLOSED
by operator write-lock (answer: NO).

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
