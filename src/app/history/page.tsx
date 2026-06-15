"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { surface, text, signal, font, getWeather, nciColor, normalizeDoorClass, doorMeta } from "@/ui/tokens"
import { Wordmark } from "@/ui/Wordmark"
import { Rule } from "@/ui/Rule"
import { SectionLabel } from "@/ui/SectionLabel"
import { Card } from "@/ui/Card"
import { Badge } from "@/ui/Badge"
import { Button } from "@/ui/Button"
import { AuthControl } from "@/molecules/AuthControl"

// History — cached receipts/briefs ledger. Simple list now (Observatory replay
// later). Each row → its brief. Page owns the fetch (head/body).

interface Row {
  id: string
  decision: string
  trueNorth: string
  nciScore: number
  yState: string
  mode: string
  doorClass: string | null
  createdAt: string
  brief?: { id: string } | null
  children?: { id: string }[]
}

export default function HistoryPage() {
  const router = useRouter()
  const [rows, setRows] = useState<Row[] | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [needsAuth, setNeedsAuth] = useState(false)

  useEffect(() => {
    let cancelled = false
    fetch("/api/history")
      .then(async (r) => ({ ok: r.ok, status: r.status, data: await r.json().catch(() => ({})) }))
      .then(({ ok, status, data }) => {
        if (cancelled) return
        if (status === 401) { setNeedsAuth(true); return }
        if (!ok) { setError(data.error ?? "Could not load history"); return }
        setRows(data.receipts ?? [])
      })
      .catch(() => { if (!cancelled) setError("Could not load history") })
    return () => { cancelled = true }
  }, [])

  return (
    <main style={{ minHeight: "100vh", background: surface.bg, color: text.primary }}>
      <div style={{ maxWidth: 720, margin: "0 auto", padding: "2rem 1.5rem 4rem" }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", paddingBottom: "1rem" }}>
          <Wordmark section="Ledger" />
          <div style={{ display: "flex", alignItems: "center", gap: "0.25rem" }}>
            <Button variant="ghost" size="sm" onClick={() => router.push("/history/reflect")}>◎ Reflect</Button>
            <Button variant="ghost" size="sm" glyph="⊕" onClick={() => router.push("/dashboard")}>New question</Button>
            <AuthControl next="/history" />
          </div>
        </div>
        <Rule style={{ marginBottom: "2rem" }} />

        <SectionLabel style={{ marginBottom: "1.25rem" }}>Receipt history · your cartography atlas</SectionLabel>

        {needsAuth && (
          <Card style={{ padding: "1.5rem 1.75rem" }}>
            <div style={{ fontFamily: font.sans, fontSize: "1rem", fontWeight: 600, color: text.primary, marginBottom: "0.5rem" }}>Sign in to see your atlas</div>
            <p style={{ fontFamily: font.sans, fontSize: "0.85rem", color: text.muted, margin: "0 0 1.25rem", lineHeight: 1.6 }}>
              Your questions, prep, and briefs are saved under your account. One magic link — no password.
            </p>
            <Button variant="primary" size="md" glyph="→" onClick={() => router.push("/compass?next=/history")}>Sign in</Button>
          </Card>
        )}

        {error && <div style={{ fontFamily: font.sans, color: signal.red, fontSize: "0.85rem" }}>{error}</div>}

        {!error && !needsAuth && rows === null && (
          <div style={{ fontFamily: font.mono, fontSize: "0.8rem", color: text.muted, letterSpacing: "0.1em" }}>LOADING LEDGER…</div>
        )}

        {rows !== null && rows.length === 0 && (
          <div style={{ fontFamily: font.sans, fontSize: "0.9rem", color: text.dimmed, lineHeight: 1.6 }}>
            No receipts yet. <span style={{ color: signal.cyan, cursor: "pointer" }} onClick={() => router.push("/dashboard")}>Run the compass →</span>
          </div>
        )}

        <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
          {(rows ?? []).map((r) => {
            const w = getWeather(r.yState)
            const door = doorMeta[normalizeDoorClass(r.doorClass)]
            const c = nciColor(r.nciScore)
            const followUps = r.children?.length ?? 0
            return (
              <Card key={r.id} accent={w.color} style={{ padding: "1rem 1.25rem" }}>
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: "1rem", marginBottom: "0.6rem" }}>
                  <Badge label={`${w.icon} ${w.label}`} color={w.color} register="light" />
                  <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
                    <span style={{ fontFamily: font.mono, fontSize: "0.7rem", color: text.muted }}>{new Date(r.createdAt).toLocaleDateString()}</span>
                    <span style={{ fontFamily: font.mono, fontWeight: 700, fontSize: "1rem", color: c, textShadow: `0 0 10px ${c}55` }}>{r.nciScore}</span>
                  </div>
                </div>
                <div style={{ fontFamily: font.sans, fontSize: "0.875rem", color: text.primary, lineHeight: 1.4, marginBottom: "0.5rem" }}>{r.decision}</div>
                <div style={{ fontFamily: font.sans, fontSize: "0.8rem", color: text.secondary, lineHeight: 1.5, marginBottom: "0.7rem" }}>
                  <span style={{ color: signal.cyan }}>True North · </span>{r.trueNorth}
                </div>
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: "0.75rem", flexWrap: "wrap" }}>
                  <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", alignItems: "center" }}>
                    <Badge label={door.label} color={door.color} register="light" />
                    {r.mode && <Badge label={r.mode} color={signal.gold} register="light" />}
                    {followUps > 0 && <Badge label={`↳ ${followUps} follow-up${followUps > 1 ? "s" : ""}`} color={signal.steel} register="light" />}
                  </div>
                  <div style={{ display: "flex", gap: "0.4rem", flexShrink: 0 }}>
                    <Button variant="ghost" size="sm" onClick={() => router.push(`/receipt/${r.id}`)}>Receipt →</Button>
                    {r.brief && <Button variant="ghost" size="sm" onClick={() => router.push(`/brief/${r.id}`)}>Brief →</Button>}
                  </div>
                </div>
              </Card>
            )
          })}
        </div>
      </div>
    </main>
  )
}
