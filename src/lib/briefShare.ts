// Brief share tokens (Zach, 2026-10-05). A brief is owner-only by its receipt id;
// to show it to anyone else the owner mints a token here. The token is 32 random
// bytes (base64url, 43 chars); only its SHA-256 is stored, so the table cannot be
// replayed into working links. Revocation sets revokedAt on every active row.
//
// Anonymous (userId null) receipts have no owner and so no way to mint: since the
// trust-contract change, anonymous compass runs are never persisted, and their
// sharing path is the stateless fragment link `/brief/share#...` (ADR-037,
// src/lib/shareLink.ts). Legacy anonymous rows become reachable only after their
// browser claims them on sign-in (POST /api/receipts/claim), which makes them owned.

import { createHash, randomBytes } from "node:crypto"

export const MAX_ACTIVE_SHARES = 10

export function mintToken(): string {
  return randomBytes(32).toString("base64url")
}

export function hashToken(token: string): string {
  return createHash("sha256").update(token).digest("hex")
}

// Cheap shape check before any DB read: exactly 43 base64url chars.
export function isTokenShaped(token: string): boolean {
  return /^[A-Za-z0-9_-]{43}$/.test(token)
}

// Token rides in the fragment: browsers never send it to the server, Referer
// headers, or pathname-only analytics. The page POSTs it to /api/shared/brief.
export function sharePath(token: string): string {
  return `/shared/brief#${token}`
}
