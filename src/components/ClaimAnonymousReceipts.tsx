"use client"

import { useEffect } from "react"
import { track } from "@vercel/analytics"

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
    // Phase 2 opt-in save (ADR-049): a bearing stashed by the ephemeral
    // receipt page's "Sign in & save" button, waiting for authentication.
    const rawPending = localStorage.getItem("arcs_pending_save")
    if (!stored && !rawPending) return

    const PENDING_TTL_MS = 7 * 86400000

    fetch("/api/auth/session")
      .then((r) => r.json())
      .then(async (s) => {
        if (cancelled || !s?.user?.id) return

        // (1) Legacy claim — pre-2026-07-13 anonymous receipts (retained per
        // ADR-049; new anonymous runs persist nothing, so for new sessions
        // this is a no-op).
        if (stored) {
          const r = await fetch("/api/receipts/claim", {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ sessionId: stored }),
          }).catch(() => null)
          if (r?.ok) {
            localStorage.removeItem("arcs_session_id")
            document.cookie = "arcs_session_id=; path=/; max-age=0"
          }
        }

        // (2) Pending ephemeral save — persist the bearing the user chose to
        // keep, then land them on the real receipt.
        if (rawPending) {
          try {
            const pending = JSON.parse(rawPending)
            if (pending?.bearing && Date.now() - (pending.savedAt ?? 0) < PENDING_TTL_MS) {
              const r = await fetch("/api/receipts/save", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ bearing: pending.bearing }),
              })
              if (r.ok) {
                const d = await r.json()
                localStorage.removeItem("arcs_pending_save")
                track("receipt_save_completed")
                if (d?.receipt_id && !cancelled) window.location.assign(`/receipt/${d.receipt_id}`)
              } else {
                track("receipt_save_failed", { status: r.status })
              }
            } else {
              // Pending save expired or malformed — never attempted the write.
              track("receipt_save_failed", { reason: "expired_or_malformed" })
              localStorage.removeItem("arcs_pending_save")
            }
          } catch {
            localStorage.removeItem("arcs_pending_save")
          }
        }
      })
      .catch(() => {})

    return () => { cancelled = true }
  }, [])

  return null
}
