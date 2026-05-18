"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"

const s = {
  bg: "#020408", surface: "#0d1117", border: "#1e293b",
  text: "#e2e8f0", muted: "#475569", dimmed: "#64748b",
  cyan: "#00F0FF", green: "#00FF9D", gold: "#FFD700", red: "#FF4D6D",
}

const Y_WEATHER: Record<string, { label: string; icon: string; color: string }> = {
  GREEN:   { label: "Clarity Ridge",       icon: "▲", color: "#00FF9D" },
  YELLOW:  { label: "Pressure Band",       icon: "◈", color: "#FFD700" },
  RED:     { label: "Cliff Edge",          icon: "✕", color: "#FF4D6D" },
  FORK:    { label: "Fork",                icon: "⊕", color: "#00F0FF" },
  SCRATCH: { label: "Fog Layer",           icon: "~", color: "#475569" },
  DELTA:   { label: "Conviction Shift",    icon: "△", color: "#A78BFA" },
  DRIFT:   { label: "Drifting",            icon: "⟳", color: "#FB923C" },
  PARADOX: { label: "Paradox",             icon: "∞", color: "#E879F9" },
}

const CONVICTION_LABELS: Record<string, string> = {
  HIGH: "Strong lean", CONTESTED: "Split", LOW: "No lean yet",
  EPHEMERAL: "Fading", COLLAPSED: "Gone",
}

const MODE_LABELS: Record<string, string> = {
  COURT: "Full deliberation", PLAN: "Structured plan", QUICKMOVE: "Quick move",
}

const HORIZON_LABELS: Record<string, string> = {
  TODAY: "Today", THIS_WEEK: "This week",
  THIS_QUARTER: "This quarter", ONE_TO_THREE_YEARS: "1–3 years",
}

interface ReceiptSummary {
  id: string
  decision: string
  trueNorth: string
  nciScore: number
  yState: string
  yConviction: string
  mode: string
  doorClass: string
  window: string
  stakes: string | null
  entity: string | null
  createdAt: string
  sessionId: string
  brief: { id: string } | null
  children: { id: string }[]
}

export default function HistoryPage() {
  const router = useRouter()
  const [receipts, setReceipts] = useState<ReceiptSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [copied, setCopied] = useState<string | null>(null)

  useEffect(() => {
    fetch("/api/history")
      .then(r => r.json())
      .then(d => { setReceipts(d.receipts ?? []); setLoading(false) })
      .catch(() => setLoading(false))
  }, [])

  function copyLink(receiptId: string) {
    navigator.clipboard.writeText(`${window.location.origin}/brief/${receiptId}`)
    setCopied(receiptId)
    setTimeout(() => setCopied(null), 1800)
  }

  function resumeDecision(r: ReceiptSummary) {
    const params = new URLSearchParams({ q: r.decision })
    router.push(`/dashboard?${params}`)
  }

  if (loading) return (
    <div style={{ minHeight: "100vh", background: s.bg, display: "flex", alignItems: "center", justifyContent: "center" }}>
      <div style={{ fontSize: "0.75rem", color: s.muted, letterSpacing: "0.1em" }}>Loading receipts…</div>
    </div>
  )

  return (
    <main style={{ minHeight: "100vh", background: s.bg, color: s.text, fontFamily: "'Inter', sans-serif" }}>
      <div style={{ maxWidth: 800, margin: "0 auto", padding: "2.5rem 1.5rem" }}>

        {/* Header */}
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "2rem" }}>
          <div>
            <div style={{ fontSize: "0.6rem", color: s.cyan, letterSpacing: "0.15em", textTransform: "uppercase", marginBottom: "0.375rem", fontWeight: 700 }}>
              ARCS FIELD OS
            </div>
            <h1 style={{ fontSize: "1.25rem", fontWeight: 600, color: s.text, margin: 0 }}>Decision History</h1>
            <p style={{ fontSize: "0.8rem", color: s.muted, margin: "0.375rem 0 0" }}>
              {receipts.length} receipt{receipts.length !== 1 ? "s" : ""} · alpha questions only
            </p>
          </div>
          <button
            onClick={() => router.push("/")}
            style={{ background: "none", border: `1px solid ${s.border}`, color: s.muted, fontSize: "0.75rem", padding: "0.375rem 0.875rem", borderRadius: 6, cursor: "pointer" }}
          >
            ← Home
          </button>
        </div>

        {/* Empty state */}
        {receipts.length === 0 && (
          <div style={{ textAlign: "center", padding: "4rem 0" }}>
            <div style={{ fontSize: "2rem", marginBottom: "1rem", opacity: 0.3 }}>◎</div>
            <div style={{ fontSize: "0.85rem", color: s.muted }}>No decisions yet.</div>
            <button
              onClick={() => router.push("/dashboard")}
              style={{ marginTop: "1.25rem", padding: "0.625rem 1.25rem", borderRadius: 8, background: s.cyan, color: s.bg, fontWeight: 700, fontSize: "0.8rem", border: "none", cursor: "pointer" }}
            >
              Run the compass →
            </button>
          </div>
        )}

        {/* Receipt cards */}
        <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
          {receipts.map(r => {
            const weather = Y_WEATHER[r.yState] ?? Y_WEATHER.GREEN
            const nciColor = r.nciScore >= 70 ? s.green : r.nciScore >= 45 ? s.gold : s.red
            const date = new Date(r.createdAt).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })

            return (
              <div
                key={r.id}
                style={{
                  background: s.surface, border: `1px solid ${s.border}`, borderRadius: 10,
                  padding: "1rem 1.25rem", display: "flex", flexDirection: "column", gap: "0.625rem",
                  transition: "border-color 0.15s",
                }}
              >
                {/* Top row: date + entity + Y state */}
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: "0.75rem" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "0.625rem", flexWrap: "wrap" }}>
                    <span style={{ fontSize: "0.65rem", color: s.dimmed }}>{date}</span>
                    {r.entity && (
                      <span style={{ fontSize: "0.65rem", color: s.muted, background: s.bg, border: `1px solid ${s.border}`, borderRadius: 4, padding: "0.1rem 0.4rem" }}>
                        {r.entity}
                      </span>
                    )}
                    {r.children.length > 0 && (
                      <span style={{ fontSize: "0.6rem", color: s.cyan, letterSpacing: "0.04em" }}>
                        ⊕ {r.children.length} follow-up{r.children.length !== 1 ? "s" : ""}
                      </span>
                    )}
                  </div>
                  <span style={{ fontSize: "0.65rem", fontWeight: 700, color: weather.color, whiteSpace: "nowrap" }}>
                    {weather.icon} {weather.label}
                  </span>
                </div>

                {/* Decision text */}
                <div style={{ fontSize: "0.875rem", fontWeight: 600, color: s.text, lineHeight: 1.4 }}>
                  {r.decision}
                </div>

                {/* True North */}
                <div style={{ fontSize: "0.78rem", color: s.muted, lineHeight: 1.5, fontStyle: "italic" }}>
                  "{r.trueNorth}"
                </div>

                {/* Meta row: NCI + conviction + approach + timeframe */}
                <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap" }}>
                  <div style={{ display: "flex", gap: "0.25rem", alignItems: "baseline" }}>
                    <span style={{ fontSize: "1rem", fontWeight: 700, color: nciColor }}>{r.nciScore}</span>
                    <span style={{ fontSize: "0.6rem", color: s.dimmed }}>/100</span>
                  </div>
                  <span style={{ fontSize: "0.68rem", color: s.muted }}>{CONVICTION_LABELS[r.yConviction] ?? r.yConviction}</span>
                  <span style={{ fontSize: "0.68rem", color: s.dimmed }}>·</span>
                  <span style={{ fontSize: "0.68rem", color: s.muted }}>{MODE_LABELS[r.mode] ?? r.mode}</span>
                  <span style={{ fontSize: "0.68rem", color: s.dimmed }}>·</span>
                  <span style={{ fontSize: "0.68rem", color: s.muted }}>{HORIZON_LABELS[r.window] ?? r.window}</span>
                </div>

                {/* Actions */}
                <div style={{ display: "flex", gap: "0.5rem", marginTop: "0.25rem" }}>
                  {r.brief && (
                    <button
                      onClick={() => router.push(`/brief/${r.id}`)}
                      style={{ padding: "0.35rem 0.75rem", borderRadius: 5, border: `1px solid ${s.cyan}44`, background: `${s.cyan}0d`, color: s.cyan, fontSize: "0.7rem", fontWeight: 600, cursor: "pointer" }}
                    >
                      View brief
                    </button>
                  )}
                  <button
                    onClick={() => router.push(`/dashboard?q=${encodeURIComponent(r.decision)}`)}
                    style={{ padding: "0.35rem 0.75rem", borderRadius: 5, border: `1px solid ${s.border}`, background: "transparent", color: s.muted, fontSize: "0.7rem", cursor: "pointer" }}
                  >
                    Re-run compass
                  </button>
                  <button
                    onClick={() => copyLink(r.id)}
                    style={{ padding: "0.35rem 0.75rem", borderRadius: 5, border: `1px solid ${s.border}`, background: "transparent", color: copied === r.id ? s.green : s.muted, fontSize: "0.7rem", cursor: "pointer", transition: "color 0.15s" }}
                  >
                    {copied === r.id ? "✓ Copied" : "Copy link"}
                  </button>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </main>
  )
}
