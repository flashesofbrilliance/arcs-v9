'use client'

// Recipient view for a stateless anonymous share (ADR-037).
// The bearing arrives in the URL FRAGMENT (#...), decoded + sanitized entirely
// client-side (shareLink.ts) — nothing is fetched from or written to the server.
// One-time on this device: a localStorage flag flips the link to the sign-in onramp
// after the first view. We NEVER read location.hash into analytics/logs.
//
// PRIVACY ASSUMPTION (pinned): Vercel <Analytics/>/<SpeedInsights/> (mounted globally in
// layout.tsx) record pathname only, NOT the URL fragment — so the payload is never captured.
// If analytics config ever switches to full-URL capture, this page's fragment would leak;
// keep this page path-only and never pass location.hash to any tracker.

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { Brief } from "@/organisms/Brief"
import { Button } from "@/ui/Button"
import { SequenceLoader } from "@/molecules/SequenceLoader"
import { surface, text, signal, font, border, contentContainer } from "@/ui/tokens"
import { useVw } from "@/ui/useVw"
import { decodeShare, shareSeenKey } from "@/lib/shareLink"
import type { CompassResult } from "@/lib/mockCompass"
import { track } from "@vercel/analytics"

export default function SharedBriefPage() {
  const router = useRouter()
  const vw = useVw()
  const [status, setStatus] = useState<"loading" | "ready">("loading")
  const [result, setResult] = useState<CompassResult | null>(null)

  useEffect(() => {
    const hash = window.location.hash || ""
    const encoded = hash.replace(/^#/, "").trim()
    const decoded = encoded ? decodeShare(hash) : null

    // Invalid/empty payload, or already opened once on this device → onramp.
    if (!decoded) {
      router.replace("/compass?shared=1")
      return
    }
    const key = shareSeenKey(encoded)
    let seen = false
    try { seen = localStorage.getItem(key) === "1" } catch { seen = false }
    if (seen) {
      router.replace("/compass?shared=1")
      return
    }
    try { localStorage.setItem(key, "1") } catch { /* private mode — still render this once */ }
    setResult(decoded)
    setStatus("ready")
  }, [router])

  if (status === "loading" || !result) {
    return (
      <main style={{ minHeight: "100vh", background: surface.bg, color: text.primary, display: "flex", alignItems: "center", justifyContent: "center", padding: "2rem" }}>
        <SequenceLoader title="Recomposing shared bearing…" stages={[{ name: "DECODE" }, { name: "RENDER" }]} footer="Rendering from the link. Nothing is fetched from a server." />
      </main>
    )
  }

  return (
    <main style={{ minHeight: "100vh", background: surface.bg, color: text.primary }}>
      {/* One-time banner — sets the recipient's expectation before they read on. */}
      <div style={{ ...contentContainer(vw), paddingTop: "1.5rem" }}>
        <div style={{ border: `1px solid ${border}`, borderLeft: `2px solid ${signal.gold}`, background: "#0d1117", borderRadius: 6, padding: "0.85rem 1rem", display: "flex", flexWrap: "wrap", alignItems: "center", justifyContent: "space-between", gap: "0.75rem" }}>
        <div style={{ minWidth: 240, flex: 1 }}>
          <div style={{ color: signal.gold, fontFamily: font.mono, fontSize: "0.65rem", letterSpacing: "0.12em", textTransform: "uppercase", marginBottom: "0.25rem" }}>One-time shared bearing</div>
          <div style={{ color: text.secondary, fontSize: "0.8rem", lineHeight: 1.5 }}>
            This link carries the sender&rsquo;s bearing inside the URL itself. Nothing was stored on our servers. It opens <strong style={{ color: text.primary }}>once on this device</strong>, then becomes a sign-in page. Sign in to keep and revisit briefs of your own.
          </div>
        </div>
        <Button variant="gold" size="sm" onClick={() => {
          // "Keep" = persist post-auth. Stash the recomposed bearing exactly the
          // way the ephemeral receipt page does (arcs_pending_save), so the
          // root-layout ClaimAnonymousReceipts consumer saves it after sign-in
          // and lands the user ON their own /receipt/<id> — not the generic
          // dashboard. Without this, "Sign in to keep" kept nothing and dropped
          // the viewer at app.arcs.care. The shared payload carries no prep;
          // /api/receipts/save handles a null prep context fine.
          track("receipt_save_clicked", { source: "brief_share" })
          try { localStorage.setItem("arcs_pending_save", JSON.stringify({ savedAt: Date.now(), bearing: result })) } catch {}
          router.push("/compass?shared=1")
        }}>Sign in to keep</Button>
        </div>
      </div>

      <Brief
        result={result}
        situationFraming={undefined}
        onBack={() => router.push("/compass?shared=1")}
        onNewQuestion={() => router.push("/dashboard")}
        onTributary={(prompt) => router.push(`/dashboard?q=${encodeURIComponent(prompt)}`)}
      />
    </main>
  )
}
