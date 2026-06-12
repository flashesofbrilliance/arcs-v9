// Render through the fog to earned clarity.
"use client"

import { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { surface, text, signal, font } from "@/ui/tokens"
import { Brief } from "@/organisms/Brief"
import { Card } from "@/ui/Card"
import { Label } from "@/ui/Label"
import { Button } from "@/ui/Button"
import type { CompassResult } from "@/lib/mockCompass"

// Brief surface — the shareable cartography report. Fetches the stored brief +
// receipt, maps the DB receipt → CompassResult, renders the Brief organism
// (on-screen) plus the AI situation framing and share row. Page owns data
// (head/body, F4). Doc-kit print/share view + enrich = follow-up.

function safeParse<T>(v: unknown, fallback: T): T {
  if (typeof v !== "string") return (v as T) ?? fallback
  try { return JSON.parse(v) as T } catch { return fallback }
}

// DB receipt (camelCase, JSON-string fields) → presentational CompassResult
function toCompassResult(receipt: Record<string, unknown>, tributaries: unknown[]): CompassResult {
  const raw = safeParse<Record<string, unknown>>(receipt.rawResponse, {})
  const rawReasoning = (raw.reasoning ?? {}) as Record<string, unknown>
  return {
    receipt_id: String(receipt.id ?? ""),
    question: String(receipt.decision ?? ""),
    true_north: String(receipt.trueNorth ?? ""),
    why: safeParse<string[]>(receipt.whyBullets, []),
    nci_score: Number(receipt.nciScore ?? 50),
    coherence_pct: (receipt.coherencePct as number) ?? undefined,
    is_satoshi: Boolean(receipt.isSatoshi),
    decision_mode: String(receipt.mode ?? ""),
    door_class: String(receipt.doorClass ?? "TWO_WAY"),
    y_state: String(receipt.yState ?? "GREEN"),
    render_resolution: String(receipt.renderResolution ?? "SHARP"),
    nci_delta: null,
    macro_tags: safeParse<string[]>(receipt.macroTags, []),
    tributaries: tributaries as CompassResult["tributaries"],
    reasoning: {
      fated: safeParse(receipt.fated, undefined),
      paths: safeParse(receipt.paths, undefined),
      court: safeParse(receipt.court, undefined),
      court_verdict: (receipt.courtVerdict as string) ?? undefined,
      advisors: (rawReasoning.advisors as CompassResult["reasoning"]["advisors"]) ?? undefined,
    },
  } as CompassResult
}

export default function BriefPage() {
  const params = useParams()
  const router = useRouter()
  const receiptId = String(params.receiptId)

  const [result, setResult] = useState<CompassResult | null>(null)
  const [framing, setFraming] = useState<string>("")
  const [error, setError] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)
  // null = still checking. The brief itself is public; sharing is gated (PLG hook).
  const [authed, setAuthed] = useState<boolean | null>(null)

  useEffect(() => {
    let cancelled = false
    fetch(`/api/brief/${receiptId}`)
      .then(async (r) => ({ ok: r.ok, data: await r.json() }))
      .then(({ ok, data }) => {
        if (cancelled) return
        if (!ok) { setError(data.error ?? "Could not load brief"); return }
        setResult(toCompassResult(data.receipt, data.tributaries ?? []))
        setFraming(data.brief?.situationFraming ?? "")
      })
      .catch(() => { if (!cancelled) setError("Could not load brief") })
    return () => { cancelled = true }
  }, [receiptId])

  // Resolve auth state; once signed in, claim this browser's anonymous receipts.
  useEffect(() => {
    let cancelled = false
    fetch("/api/auth/session")
      .then((r) => r.json())
      .then(async (s) => {
        if (cancelled) return
        const isAuthed = !!s?.user?.id
        setAuthed(isAuthed)
        if (isAuthed && typeof window !== "undefined") {
          const stored = localStorage.getItem("arcs_session_id")
          if (stored) {
            const r = await fetch("/api/receipts/claim", {
              method: "PATCH",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ sessionId: stored }),
            })
            if (r.ok) localStorage.removeItem("arcs_session_id")
          }
        }
      })
      .catch(() => { if (!cancelled) setAuthed(false) })
    return () => { cancelled = true }
  }, [])

  const briefUrl = () => `${window.location.origin}/brief/${receiptId}`

  async function copyLink() {
    await navigator.clipboard.writeText(briefUrl())
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }
  function shareSms() {
    window.open(`sms:?body=${encodeURIComponent(`${result?.true_north}\n\nARCS Brief → ${briefUrl()}`)}`)
  }
  function shareX() {
    window.open(`https://x.com/intent/tweet?text=${encodeURIComponent((result?.true_north ?? "").slice(0, 220))}&url=${encodeURIComponent(briefUrl())}`)
  }

  if (error) {
    return (
      <main style={{ minHeight: "100vh", background: surface.bg, color: text.primary, display: "flex", alignItems: "center", justifyContent: "center" }}>
        <div style={{ fontFamily: font.sans, color: signal.red, fontSize: "0.9rem" }}>{error}</div>
      </main>
    )
  }
  if (!result) {
    return <main style={{ minHeight: "100vh", background: surface.bg, color: text.muted, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: font.mono, fontSize: "0.8rem", letterSpacing: "0.1em" }}>RENDERING BRIEF…</main>
  }

  return (
    <main style={{ minHeight: "100vh", background: surface.bg, color: text.primary }}>
      <Brief result={result} onBack={() => router.push("/dashboard")} />

      <div style={{ maxWidth: 880, margin: "0 auto", padding: "0 1.5rem 3rem" }}>
        {framing && (
          <Card style={{ marginBottom: "1.5rem" }}>
            <Label style={{ marginBottom: "0.75rem" }}>Situation Framing</Label>
            <p style={{ fontFamily: font.sans, fontSize: "0.9rem", color: text.secondary, lineHeight: 1.7, margin: 0, whiteSpace: "pre-wrap" }}>{framing}</p>
          </Card>
        )}

        <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", alignItems: "center" }}>
          <Label style={{ marginRight: "0.25rem" }}>Share</Label>
          {authed ? (
            <>
              <Button variant="ghost" size="sm" onClick={copyLink}>{copied ? "✓ Copied" : "Copy link"}</Button>
              <Button variant="ghost" size="sm" onClick={shareSms}>SMS</Button>
              <Button variant="ghost" size="sm" onClick={shareX}>Post to X</Button>
            </>
          ) : (
            <Button variant="gold" size="sm" glyph="◈" onClick={() => router.push(`/compass?next=${encodeURIComponent(`/brief/${receiptId}`)}`)}>
              Sign in to share
            </Button>
          )}
        </div>
      </div>
    </main>
  )
}
