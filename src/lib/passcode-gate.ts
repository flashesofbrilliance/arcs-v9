// Per-counterpart passcode gate. Same mechanism as ammo-gate.ts (SHA-256 token in
// an httpOnly cookie, secret only in an env var, fail-closed), but each gate gets
// its OWN namespace, cookie and secret, so one counterpart's passcode never opens
// another counterpart's pages. Web Crypto only: runs in proxy.ts and route handlers.

export const MYALLY_GATE = { ns: "myally", cookie: "myally_gate", env: "MYALLY_PASSCODE" } as const
export const MONDAY_GATE = { ns: "monday", cookie: "monday_gate", env: "MONDAY_PASSCODE" } as const

export async function gateToken(ns: string, secret: string): Promise<string> {
  const data = new TextEncoder().encode(ns + ":" + secret)
  const digest = await crypto.subtle.digest("SHA-256", data)
  return Array.from(new Uint8Array(digest))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("")
}

export async function gateUnlocked(
  ns: string,
  cookieValue: string | undefined,
  secret: string | undefined,
): Promise<boolean> {
  if (!cookieValue || !secret) return false
  const expected = await gateToken(ns, secret)
  if (cookieValue.length !== expected.length) return false
  let diff = 0
  for (let i = 0; i < expected.length; i++) {
    diff |= cookieValue.charCodeAt(i) ^ expected.charCodeAt(i)
  }
  return diff === 0
}
