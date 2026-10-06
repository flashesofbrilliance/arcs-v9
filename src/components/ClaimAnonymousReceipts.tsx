"use client"

import { useEffect } from "react"
import { track } from "@vercel/analytics"

// Runs on every page (mounted in the root layout) so a pending opt-in save
// (ADR-049) lands wherever the magic link drops the user.
//
// The legacy anonymous-receipt claim (PATCH /api/receipts/claim) was removed
// 2026-10-05: anonymous runs have persisted nothing since 2026-07-13, and the
// 7-day claim cookie that proved possession of the 48 pre-cutoff rows expired
// by 2026-07-20, so the endpoint could only ever hand those rows to whoever
// presented a leaked sessionId.
export function ClaimAnonymousReceipts() {
  useEffect(() => {
    let cancelled = false

    // Phase 2 opt-in save (ADR-049): a bearing stashed by the ephemeral
    // receipt page's "Sign in & save" button, waiting for authentication.
    const rawPending = localStorage.getItem("arcs_pending_save")
    if (!rawPending) return

    const PENDING_TTL_MS = 7 * 86400000

    fetch("/api/auth/session")
      .then((r) => r.json())
      .then(async (s) => {
        if (cancelled || !s?.user?.id) return

        // Pending ephemeral save — persist the bearing the user chose to
        // keep, then land them on the real receipt.
        if (rawPending) {
          let pending: { bearing?: unknown; savedAt?: number } | null = null
          try { pending = JSON.parse(rawPending) } catch { pending = null }
          const fresh = !!pending?.bearing && Date.now() - (pending?.savedAt ?? 0) < PENDING_TTL_MS
          if (!fresh) {
            // Pending save expired or malformed: the write was never attempted,
            // and there is nothing usable to retry. Drop the stash.
            track("receipt_save_failed", { reason: "expired_or_malformed" })
            localStorage.removeItem("arcs_pending_save")
            return
          }
          try {
            const r = await fetch("/api/receipts/save", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ bearing: pending!.bearing }),
            })
            if (r.ok) {
              const d = await r.json()
              localStorage.removeItem("arcs_pending_save")
              track("receipt_save_completed")
              if (d?.receipt_id && !cancelled) window.location.assign(`/receipt/${d.receipt_id}`)
            } else {
              // Server said no; keep the stash so the next page load retries
              // inside the TTL.
              track("receipt_save_failed", { status: r.status })
            }
          } catch {
            // Network exception (dropped connection, offline): the bearing is
            // not lost and the write did not happen. Keep the stash so the
            // next page load retries, same as the !r.ok branch. Before this
            // (spec _SPECS/receipt-save-nudge-v1.md §6.2) a flaky network
            // silently discarded the one bearing the visitor chose to keep.
            track("receipt_save_failed", { reason: "network" })
          }
        }
      })
      .catch(() => {})

    return () => { cancelled = true }
  }, [])

  return null
}
