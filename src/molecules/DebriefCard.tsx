"use client"

import { useRouter } from "next/navigation"
import type React from "react"
import { font, signal, text, border, surface, nciColor } from "@/ui/tokens"
import { Button } from "@/ui/Button"

export interface DebriefCardProps {
  receiptId: string
  question: string
  trueNorth: string
  nciScore: number
  nciGrade?: string
  createdAt: string
  protecting?: string[]
}

export function DebriefCard({ receiptId, question, trueNorth, nciScore, nciGrade, createdAt }: DebriefCardProps) {
  const router = useRouter()
  const now = new Date()
  const created = new Date(createdAt)
  const elapsed = (now.getTime() - created.getTime()) / (1000 * 60 * 60 * 24)
  const daysElapsed = Number.isFinite(elapsed) ? Math.floor(elapsed) : 0

  // Google Calendar link builder
  function buildCalendarLink() {
    const eventDate = new Date(createdAt)
    // Suggest adding the calendar event for "today" or the reminderDate
    const calDate = new Date(now.getFullYear(), now.getMonth(), now.getDate())
    const startTime = calDate.toISOString().replace(/[-:]/g, "").split(".")[0] + "Z"

    const title = `Debrief: Did it land?`
    // Truncate True North to avoid URL length limits (>2000 chars can break on some platforms)
    const tnTruncated = trueNorth.length > 200 ? trueNorth.slice(0, 197) + "…" : trueNorth
    const description = `Original decision: "${question}"

True North: "${tnTruncated}"

NCI (decision coherence): ${nciScore}/100${nciGrade ? `. ${nciGrade}` : ""}
Days elapsed: ${daysElapsed}d

The shoe has dropped. Did it land where the compass pointed? Log your outcome at:
${typeof window !== "undefined" ? window.location.origin : ""}/debrief/${receiptId}`

    const params = new URLSearchParams({
      action: "TEMPLATE",
      text: title,
      details: description,
      dates: `${startTime}/${startTime}`,
    })

    return `https://calendar.google.com/calendar/render?${params.toString()}`
  }

  // Same panel language as VerdictPanel: hairline border, mono kicker, one accent.
  const kicker: React.CSSProperties = { fontFamily: font.mono, ...font.tier.t3, textTransform: "uppercase", color: text.muted, margin: 0 }
  return (
    <section aria-labelledby="debrief-kicker" style={{ marginBottom: "1.5rem", border: `1px solid ${border.subtle}`, borderRadius: 6, background: surface.panel, padding: "clamp(1rem, 3vw, 1.4rem)" }}>
      <div style={{ display: "flex", flexWrap: "wrap", alignItems: "baseline", justifyContent: "space-between", gap: "0.4rem 1rem", marginBottom: "0.75rem" }}>
        <h2 id="debrief-kicker" style={{ ...kicker, color: signal.cyan }}>Close the loop</h2>
        <span style={kicker}>
          Called {daysElapsed === 0 ? "today" : `${daysElapsed}d ago`} · NCI <span style={{ color: nciColor(nciScore) }}>{nciScore}</span>
        </span>
      </div>
      <p style={{ fontFamily: font.sans, fontSize: "0.925rem", color: text.primary, lineHeight: 1.55, margin: "0 0 1rem", textWrap: "pretty" }}>
        When the outcome is in, record whether it landed where the call pointed. Your next brief reads from it.
      </p>
      {nciGrade ? <p style={{ fontFamily: font.sans, fontSize: "0.8rem", color: text.muted, lineHeight: 1.5, margin: "-0.5rem 0 1rem" }}>{nciGrade}</p> : null}
      <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
        <Button variant="primary" size="sm" onClick={() => router.push(`/debrief/${receiptId}`)}>
          Log how it landed →
        </Button>
        <Button variant="ghost" size="sm" onClick={() => {
          if (typeof window !== "undefined") {
            window.open(buildCalendarLink(), "_blank")
          }
        }}>
          Add reminder
        </Button>
      </div>
    </section>
  )
}
