import { createHmac, timingSafeEqual } from "crypto"
import { APP_URL } from "@/lib/env"

// Signed one-click links for debrief reminder opt-in/out. The link used to
// carry a bare uid, and /api/brief exposed receipt owners' uids, so anyone
// could flip anyone's setting. The signature binds uid + action to
// AUTH_SECRET; without the secret no link verifies (fail closed).
export type ReminderAction = "opt-in" | "opt-out"

function sign(uid: string, action: ReminderAction): string | null {
  const secret = process.env.AUTH_SECRET
  if (!secret) return null
  return createHmac("sha256", secret).update(`reminders:${action}:${uid}`).digest("base64url")
}

export function reminderUrl(uid: string, action: ReminderAction): string | undefined {
  const sig = sign(uid, action)
  if (!sig) return undefined
  return `${APP_URL}/api/account/reminders?action=${action}&uid=${encodeURIComponent(uid)}&sig=${sig}`
}

export function verifyReminder(uid: string, action: ReminderAction, sig: string | null): boolean {
  const want = sign(uid, action)
  if (!want || !sig) return false
  const a = Buffer.from(want), b = Buffer.from(sig)
  return a.length === b.length && timingSafeEqual(a, b)
}
