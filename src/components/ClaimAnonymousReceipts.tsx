"use client"

import { useEffect } from "react"

// Runs on every page (mounted in the root layout), not just dashboard/brief —
// the original per-page checks missed the actual magic-link landing page
// (/compass, per auth.ts's pages.signIn), so a user who signed in and never
// happened to visit dashboard or a brief page first never got their
// anonymous receipts claimed. Found via a real first-external-user incident:
// receipt cmqo7hylu000204l1zq0nqm8z was created anonymously, the user signed
// in two minutes later, and it was never linked — fixed manually, this is
// the structural fix.
//
// localStorage is checked first (cheap, no request); the `arcs_session_id`
// cookie (set server-side in compass/route.ts) is a secondary path for the
// same-browser-context case where localStorage was cleared or unavailable.
// Neither survives a genuinely different browser context (e.g. an in-app
// webview vs. the system browser opened from a Mail app) — that failure
// mode is a separate, harder problem this does not attempt to solve.
export function ClaimAnonymousReceipts() {
  useEffect(() => {
    let cancelled = false

    function readCookie(name: string): string | null {
      const match = document.cookie.match(new RegExp(`(?:^|; )${name}=([^;]*)`))
      return match ? decodeURIComponent(match[1]) : null
    }

    const stored = localStorage.getItem("arcs_session_id") ?? readCookie("arcs_session_id")
    if (!stored) return

    fetch("/api/auth/session")
      .then((r) => r.json())
      .then((s) => {
        if (cancelled || !s?.user?.id) return
        return fetch("/api/receipts/claim", {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ sessionId: stored }),
        })
      })
      .then((r) => {
        if (r?.ok) {
          localStorage.removeItem("arcs_session_id")
          document.cookie = "arcs_session_id=; path=/; max-age=0"
        }
      })
      .catch(() => {})

    return () => { cancelled = true }
  }, [])

  return null
}
