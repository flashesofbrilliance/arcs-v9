"use client"

import { useRouter } from "next/navigation"
import { font, signal, text } from "@/ui/tokens"
import { Card } from "@/ui/Card"
import { Label } from "@/ui/Label"
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

export function DebriefCard({ receiptId, question, trueNorth, nciScore, nciGrade, createdAt, protecting = [] }: DebriefCardProps) {
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

Conviction: ${nciScore}/100${nciGrade ? `. ${nciGrade}` : ""}
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

  return (
    <Card style={{ marginBottom: "1.5rem", borderLeft: `3px solid ${signal.cyan}` }}>
      <div style={{ marginBottom: "1rem" }}>
        <Label style={{ marginBottom: "0.75rem", display: "block" }}>The shoe has dropped</Label>
        <div style={{ fontFamily: font.sans, fontSize: "0.85rem", color: text.secondary, lineHeight: 1.6, marginBottom: "0.75rem" }}>
          <div style={{ marginBottom: "0.5rem" }}>
            <span style={{ color: text.muted, fontFamily: font.mono, fontSize: "0.75rem", textTransform: "uppercase", letterSpacing: "0.05em" }}>Question</span>
            <div style={{ color: text.primary, fontSize: "0.9rem", marginTop: "0.25rem" }}>{question}</div>
          </div>
          <div style={{ marginBottom: "0.5rem" }}>
            <span style={{ color: text.muted, fontFamily: font.mono, fontSize: "0.75rem", textTransform: "uppercase", letterSpacing: "0.05em" }}>True North</span>
            <div style={{ color: signal.cyan, fontSize: "0.9rem", marginTop: "0.25rem" }}>{trueNorth}</div>
          </div>
          <div style={{ display: "flex", gap: "2rem", fontSize: "0.8rem", color: text.secondary }}>
            <div>
              <span style={{ color: text.muted, fontFamily: font.mono, fontSize: "0.7rem", textTransform: "uppercase", letterSpacing: "0.05em" }}>Conviction</span>
              <div style={{ fontWeight: 700, color: text.primary, marginTop: "0.2rem" }}>{nciScore}/100</div>
              {nciGrade ? (
                <div style={{ color: text.muted, fontSize: "0.65rem", marginTop: "0.15rem", maxWidth: 200, lineHeight: 1.3 }}>{nciGrade}</div>
              ) : null}
            </div>
            <div>
              <span style={{ color: text.muted, fontFamily: font.mono, fontSize: "0.7rem", textTransform: "uppercase", letterSpacing: "0.05em" }}>Days elapsed</span>
              <div style={{ fontWeight: 700, color: text.primary, marginTop: "0.2rem" }}>{daysElapsed}d</div>
            </div>
          </div>
        </div>
      </div>

      <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
        <Button variant="primary" size="sm" onClick={() => router.push(`/debrief/${receiptId}`)}>
          Log how it landed →
        </Button>
        <Button variant="ghost" size="sm" onClick={() => {
          if (typeof window !== "undefined") {
            window.open(buildCalendarLink(), "_blank")
          }
        }}>
          📅 Add reminder
        </Button>
      </div>
    </Card>
  )
}
