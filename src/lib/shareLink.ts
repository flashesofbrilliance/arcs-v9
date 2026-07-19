// Stateless anonymous-brief sharing (ADR-037).
//
// An anonymous bearing is never persisted server-side (trust contract: "no auth =
// no write path"). To make it shareable without breaking that promise, we encode the
// CompassResult into the URL FRAGMENT (#...), which browsers never send to the server,
// Referer headers, or logs. The recipient's browser recomposes the brief entirely
// client-side. Nothing is written to our DB, logs, or analytics.
//
// SECURITY: a `/brief/share#<payload>` link is FULLY attacker-controllable — anyone can
// craft one and send it to a victim. So decodeShare() runs every field through the
// sanitize.ts trust-boundary clamps before it is handed to the renderer, exactly as the
// compass/brief pipeline does for model/user text. The Brief renderer escapes by default
// (no dangerouslySetInnerHTML), so this is defense-in-depth against overlong/control-char
// payloads, not the only line.

import type { CompassResult } from "@/lib/mockCompass"
import { clampText, clampInt, clampTextArray } from "@/lib/sanitize"

function toBase64Url(bytes: Uint8Array): string {
  let bin = ""
  for (let i = 0; i < bytes.length; i++) bin += String.fromCharCode(bytes[i])
  return btoa(bin).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "")
}

function fromBase64Url(s: string): Uint8Array {
  const b64 = s.replace(/-/g, "+").replace(/_/g, "/")
  const bin = atob(b64)
  const bytes = new Uint8Array(bin.length)
  for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i)
  return bytes
}

/** Encode a CompassResult into a URL-fragment-safe payload string. */
export function encodeShare(result: CompassResult): string {
  const json = JSON.stringify(result)
  return toBase64Url(new TextEncoder().encode(json))
}

/** A stable, non-cryptographic key for the recipient's one-view localStorage flag.
 *  djb2 over the encoded payload — collisions are harmless (worst case: a different
 *  shared bearing is treated as already-seen on this one device). */
export function shareSeenKey(encoded: string): string {
  let h = 5381
  for (let i = 0; i < encoded.length; i++) h = ((h << 5) + h + encoded.charCodeAt(i)) >>> 0
  return "arcs_shared_seen_" + h.toString(36)
}

/** Decode + SANITIZE a shared payload. Returns null on any malformed input.
 *  Every field is clamped because the fragment is attacker-controllable. */
export function decodeShare(fragment: string): CompassResult | null {
  try {
    const clean = fragment.replace(/^#/, "").trim()
    if (!clean) return null
    const json = new TextDecoder().decode(fromBase64Url(clean))
    const o = JSON.parse(json) as Record<string, unknown>
    if (!o || typeof o !== "object" || typeof o.true_north !== "string" || !Array.isArray(o.why)) return null

    const r = (o.reasoning ?? {}) as Record<string, unknown>
    const fated = (r.fated ?? {}) as Record<string, unknown>
    const tribs = Array.isArray(o.tributaries) ? o.tributaries : []

    const sanitized: CompassResult = {
      question: clampText(o.question, 4000),
      true_north: clampText(o.true_north, 2000),
      why: clampTextArray(o.why, 8, 2000),
      nci_score: clampInt(o.nci_score, 0, 100, 0),
      coherence_pct: typeof o.coherence_pct === "number" ? clampInt(o.coherence_pct, 0, 100, 0) : undefined,
      is_satoshi: Boolean(o.is_satoshi),
      door_class: clampText(o.door_class, 40) || "TWO_WAY",
      decision_mode: clampText(o.decision_mode, 40),
      y_state: clampText(o.y_state, 40) || "GREEN",
      render_resolution: clampText(o.render_resolution, 20) || "SHARP",
      nci_delta: typeof o.nci_delta === "number" ? clampInt(o.nci_delta, -100, 100, 0) : null,
      macro_tags: clampTextArray(o.macro_tags, 6, 40),
      tributaries: tribs.slice(0, 4).map((t) => {
        const tt = (t ?? {}) as Record<string, unknown>
        return { type: clampText(tt.type, 40), label: clampText(tt.label, 80), prompt: clampText(tt.prompt, 1000) }
      }) as CompassResult["tributaries"],
      reasoning: {
        fated: {
          facts: clampText(fated.facts, 1500),
          assumptions: clampText(fated.assumptions, 1500),
          tradeoffs: clampText(fated.tradeoffs, 1500),
          emotions: clampText(fated.emotions, 1500),
          direction: clampText(fated.direction, 1500),
        },
        paths: Array.isArray(r.paths) ? (r.paths.slice(0, 6) as CompassResult["reasoning"]["paths"]) : undefined,
        court_verdict: typeof r.court_verdict === "string" ? clampText(r.court_verdict, 1500) : undefined,
      } as CompassResult["reasoning"],
    }
    return sanitized
  } catch {
    return null
  }
}
