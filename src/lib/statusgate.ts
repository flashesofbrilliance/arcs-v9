/**
 * status.arcs.care passcode gate — signed-cookie helpers.
 *
 * INTERIM measure: a coarse "avoid passerby indexing + machine-readability"
 * gate, not per-person identity. It exists only until the MCP veil replaces it,
 * so it is deliberately one small, dependency-free, deletable module.
 *
 * Edge-safe by construction: uses Web Crypto (`crypto.subtle`), which runs in
 * both the Next middleware (`src/proxy.ts`, edge runtime) and route handlers —
 * no Node `crypto`, no npm dep. The cookie is HMAC-SHA256 signed with
 * AUTH_SECRET (already set for Auth.js), so nothing new to provision.
 *
 * Cookie shape:  <base64url(payload)>.<base64url(hmac)>
 *   payload = { v: 1, iat: <unix seconds> }
 * Verified by recomputing the HMAC (constant-time compare) and checking TTL.
 */

const COOKIE_NAME = "arcs_status";
const TTL_SECONDS = 60 * 60 * 24 * 30; // 30 days

export const GATE_COOKIE = COOKIE_NAME;
export const GATE_MAX_AGE = TTL_SECONDS;

interface GatePayload {
  v: number;
  iat: number;
}

function secret(): string {
  const s = process.env.AUTH_SECRET;
  if (!s) throw new Error("AUTH_SECRET is required to sign the status gate cookie");
  return s;
}

// --- base64url without Buffer (edge-safe) ---
function b64urlEncode(bytes: Uint8Array): string {
  let bin = "";
  for (let i = 0; i < bytes.length; i++) bin += String.fromCharCode(bytes[i]);
  return btoa(bin).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}
function b64urlDecode(str: string): Uint8Array {
  const pad = str.length % 4 === 0 ? "" : "=".repeat(4 - (str.length % 4));
  const bin = atob(str.replace(/-/g, "+").replace(/_/g, "/") + pad);
  const out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
  return out;
}

const enc = new TextEncoder();

async function hmac(data: string): Promise<Uint8Array> {
  const key = await crypto.subtle.importKey(
    "raw",
    enc.encode(secret()),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"],
  );
  const sig = await crypto.subtle.sign("HMAC", key, enc.encode(data));
  return new Uint8Array(sig);
}

// Constant-time byte compare (avoid early-exit timing leak on the signature).
function timingSafeEqual(a: Uint8Array, b: Uint8Array): boolean {
  if (a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a[i] ^ b[i];
  return diff === 0;
}

/** Mint a fresh signed gate cookie value (call after a correct passcode). */
export async function signGate(): Promise<string> {
  const payload: GatePayload = { v: 1, iat: Math.floor(Date.now() / 1000) };
  const body = b64urlEncode(enc.encode(JSON.stringify(payload)));
  const sig = b64urlEncode(await hmac(body));
  return `${body}.${sig}`;
}

/** True iff the cookie value is well-formed, correctly signed, and unexpired. */
export async function verifyGate(value: string | undefined | null): Promise<boolean> {
  if (!value) return false;
  const dot = value.indexOf(".");
  if (dot <= 0) return false;
  const body = value.slice(0, dot);
  const sig = value.slice(dot + 1);
  let expected: Uint8Array;
  let given: Uint8Array;
  try {
    expected = await hmac(body);
    given = b64urlDecode(sig);
  } catch {
    return false;
  }
  if (!timingSafeEqual(expected, given)) return false;
  try {
    const payload = JSON.parse(new TextDecoder().decode(b64urlDecode(body))) as GatePayload;
    if (payload.v !== 1 || typeof payload.iat !== "number") return false;
    const age = Math.floor(Date.now() / 1000) - payload.iat;
    return age >= 0 && age <= TTL_SECONDS;
  } catch {
    return false;
  }
}

/**
 * Constant-time passcode check. Compares against STATUS_GATE_PASSCODE.
 * Returns false (fail-closed) if the env var is unset in production.
 */
export async function checkPasscode(submitted: string | undefined | null): Promise<boolean> {
  const expected = process.env.STATUS_GATE_PASSCODE;
  if (!expected) return false;
  if (typeof submitted !== "string" || submitted.length === 0) return false;
  // Hash both sides so the compare is fixed-length regardless of input length.
  const a = await hmac(`pass:${submitted}`);
  const b = await hmac(`pass:${expected}`);
  return timingSafeEqual(a, b);
}
