'use client'

// Recipient view for a stateless anonymous share (ADR-037).
// The bearing arrives in the URL FRAGMENT (#...), decoded + sanitized entirely
// client-side (shareLink.ts) — nothing is fetched from or written to the server.
// One-time on this device: a localStorage flag flips the link to the sign-in onramp
// after the first view. We NEVER read location.hash into analytics/logs.

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { Brief } from "@/organisms/Brief"
import { Button } from "@/ui/Button"
import { SequenceLoader } from "@/molecules/SequenceLoader"
import { surface, text, signal, font, border, contentContainer } from "@/ui/tokens"
import { useVw } from "@/ui/useVw"
import { decodeShare, shareSeenKey } from "@/lib/shareLink"
import type { CompassResult } from "@/lib/mockCompass"

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
        <SequenceLoader title="Recomposing shared bearing…" stages={[{ name: "DECODE" }, { name: "RENDER" }]} footer="Rendering from the link — nothing is fetched from a server." />
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
            This link carries the sender&rsquo;s bearing inside the URL itself — nothing was stored on our servers. It opens <strong style={{ color: text.primary }}>once on this device</strong>, then becomes a sign-in page. Sign in to keep and revisit briefs of your own.
          </div>
        </div>
        <Button variant="gold" size="sm" onClick={() => router.push("/compass?next=/dashboard&shared=1")}>Sign in to keep</Button>
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
