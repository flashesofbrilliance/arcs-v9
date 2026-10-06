"use client"

// Token-shared brief (Zach, 2026-10-05). The owner mints /shared/brief#<token>
// from /brief/[receiptId]. The token stays in the fragment and is POSTed to
// /api/shared/brief, which returns an allowlisted view: no owner, session, prep,
// raw model output, lineage, or children. Read-only: following a tributary starts
// the viewer's own compass round, unlinked from the owner's receipt.
// Never pass location.hash to analytics or logs.

import { useEffect, useState, useSyncExternalStore } from "react"
import { useRouter } from "next/navigation"
import { DeadEnd } from "@/molecules/DeadEnd"
import { Brief } from "@/organisms/Brief"
import { SequenceLoader } from "@/molecules/SequenceLoader"
import { surface, text } from "@/ui/tokens"
import { toCompassResult } from "@/lib/briefView"
import type { CompassResult } from "@/lib/mockCompass"

function subscribeHash(cb: () => void) {
  window.addEventListener("hashchange", cb)
  return () => window.removeEventListener("hashchange", cb)
}

export default function TokenSharedBriefPage() {
  const router = useRouter()
  const [result, setResult] = useState<CompassResult | null>(null)
  const [framing, setFraming] = useState("")
  const [failed, setFailed] = useState(false)
  // The share token lives in the URL fragment. Read it as an external store
  // (server snapshot null) so no state is set synchronously in an effect.
  const token = useSyncExternalStore(subscribeHash, () => window.location.hash.replace(/^#/, "").trim(), () => null)
  const missing = token === "" || failed

  useEffect(() => {
    if (!token) return
    let cancelled = false
    fetch("/api/shared/brief", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token }),
    })
      .then(async (r) => ({ ok: r.ok, data: await r.json().catch(() => ({})) }))
      .then(({ ok, data }) => {
        if (cancelled) return
        if (!ok || !data.receipt) { setFailed(true); return }
        const rawResponse = JSON.stringify({ reasoning: data.advisors ? { advisors: data.advisors } : {} })
        setResult(toCompassResult({ ...data.receipt, rawResponse }, data.tributaries ?? []))
        setFraming(data.brief?.situationFraming ?? "")
      })
      .catch(() => { if (!cancelled) setFailed(true) })
    return () => { cancelled = true }
  }, [token])

  if (missing) {
    return (
      <DeadEnd
        section="Shared brief"
        title="This share link doesn't open."
        body="It may be mistyped, or its owner revoked it. Ask them for a fresh link, or run your own question through the compass."
      />
    )
  }
  if (!result) {
    return (
      <main style={{ minHeight: "100vh", background: surface.bg, color: text.primary, display: "flex", alignItems: "center", justifyContent: "center", padding: "2rem" }}>
        <SequenceLoader title="Opening the shared brief…" stages={[{ name: "SURVEY" }, { name: "SILKSCREEN" }]} footer="Reading the terrain…" />
      </main>
    )
  }
  return (
    <main style={{ minHeight: "100vh", background: surface.bg, color: text.primary }}>
      <Brief
        result={result}
        situationFraming={framing}
        onBack={() => router.push("/")}
        onNewQuestion={() => router.push("/dashboard")}
        onTributary={(prompt) => router.push(`/dashboard?${new URLSearchParams({ q: prompt }).toString()}`)}
      />
    </main>
  )
}
