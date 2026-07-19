# ADR-037 — Stateless Anonymous Brief Sharing (fragment payload, no server write)

> **Status:** DECIDED
> **Date:** 2026-07-19
> **Commit:** (set at merge)
> **Y:** GREEN / HIGH / STABLE
> **Relates to:** ADR-016 (anonymous compass), ADR-032 (anonymous-storage defect + repair seam)

## D — The Decision

**Sharp question:** Anonymous bearings are never persisted (trust contract: "no auth = no write path").
So `/brief/[id]` 404s for a recipient, and anonymous threads have no shareable/return path. How do we
make an anonymous bearing shareable **without** re-introducing the exact anonymous-storage defect that
ADR-032 fixed and publicly disclosed?

**Decision:** Encode the bearing into the **URL fragment** (`/brief/share#<payload>`). Browsers never
send the fragment to the server, Referer headers, or logs — so the recipient's browser recomposes the
brief entirely client-side with **zero server write**. The published "nothing is stored / no write path"
claims remain literally true; ADR-032 is **not** reversed.

Rejected alternative: a server-side one-time-token store. It would deliver hard-enforced "one view," but
requires an anonymous server write — reversing ADR-032 and forcing a trust-contract amendment. Not worth
it; the stateless design meets the goal at no privacy cost.

## E — Entity / System

- `src/lib/shareLink.ts` — `encodeShare`/`decodeShare`/`shareSeenKey`. **decodeShare sanitizes every
  field** through `sanitize.ts` clamps: a `#payload` link is fully attacker-controllable, so the recipient
  treats it as untrusted data (same trust-boundary principle as the compass pipeline).
- `src/app/brief/share/page.tsx` — recipient view. Decodes the fragment, renders `<Brief>`, and gates on a
  `localStorage` "seen" flag → after first view on that device, redirects to `/compass?shared=1`. Never
  reads `location.hash` into analytics/logs.
- `src/app/receipt/[receiptId]/page.tsx` — sharer affordance ("Share ↗") shown only for **ephemeral**
  (anonymous) bearings; persisted receipts keep their real `/brief/[id]`.
- `src/app/compass/page.tsx` — `?shared=1` onramp banner.
- `src/app/trust/page.tsx` §01 + `src/app/privacy/page.tsx` — copy carve-out (see Consequences).

## W — Window

QUARTER. Revisit if we ever want cross-device one-time enforcement (would require the server-token path +
a trust-contract amendment) or share-link analytics (must stay path-only, never fragment).

## Y — Gate

**GREEN / HIGH / STABLE.** The design fully preserves the existing trust contract; the only trade-off
(soft, per-device one-time rather than cryptographically enforced) is inherent to a zero-write design and
was explicitly chosen.

## Consequences

- **Canonical contract amended in the same change** (source of truth first, per its own header):
  `_CANON/trust-contract.md` → **v1.3**, §1 gains the "Sharing an anonymous bearing" carve-out + amendment-log
  row + a MEMORY.md entry. The derived pages then match it: `/trust` §01 carve-out (footer bumped to v1.3);
  `/privacy` row (footer bumped to v1.1). Wording avoids overclaiming — the one-view flag is per-device/soft,
  not "enforced."
- **Server-side claims unchanged** — no DB row, no reversal of ADR-032. A `privacy-review` pass verifies
  code-vs-claims before merge.
- **Soft one-time:** cannot be enforced across devices/cache-clears (no server state). Accepted.
- `/terms`: reviewed — no change required (existing user-shared-content terms cover it).
