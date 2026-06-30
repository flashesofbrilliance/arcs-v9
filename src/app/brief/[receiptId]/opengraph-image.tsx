import { ImageResponse } from "next/og"
import { prisma } from "@/lib/db"

export const runtime = "nodejs"
export const size = { width: 1200, height: 630 }
export const contentType = "image/png"

const NCI_COLOR = (s: number) => s >= 70 ? "#00FF9D" : s >= 45 ? "#FFD700" : "#FF4D6D"

// Mirrors DebriefCard.tsx — that's the actual hero element rendered on
// /brief/[receiptId] (unconditionally, above everything else), and the SMS
// share button shares exactly that URL. The OG image previously rendered a
// completely different "Decision Brief" layout that never matched what the
// recipient actually lands on — fixed so the link preview IS the card.
export default async function OGImage({
  params,
}: {
  params: Promise<{ receiptId: string }>
}) {
  const { receiptId } = await params
  const receipt = await prisma.receipt.findUnique({ where: { id: receiptId } })

  const decision = receipt?.decision ?? "A decision under navigation"
  const trueNorth = receipt?.trueNorth ?? "Navigate to clarity."
  const nci = receipt?.nciScore ?? 50
  const createdAt = receipt?.createdAt ?? new Date()
  const daysElapsed = Math.max(0, Math.floor((Date.now() - new Date(createdAt).getTime()) / 86400000))

  // Truncate for display — same thresholds as DebriefCard's natural wrap.
  const shortQuestion = decision.length > 140 ? decision.slice(0, 137) + "…" : decision
  const shortNorth = trueNorth.length > 140 ? trueNorth.slice(0, 137) + "…" : trueNorth

  return new ImageResponse(
    (
      <div
        style={{
          width: 1200, height: 630,
          background: "#020408",
          display: "flex", flexDirection: "column",
          padding: "64px 72px",
          fontFamily: "sans-serif",
          position: "relative",
        }}
      >
        {/* Left rail accent — matches DebriefCard's borderLeft cyan accent */}
        <div style={{ position: "absolute", top: 0, bottom: 0, left: 0, width: 4, background: "#00F0FF" }} />

        <div style={{ display: "flex", alignItems: "center", gap: 16, marginBottom: 44 }}>
          <span style={{ fontSize: 11, letterSpacing: "0.15em", color: "#00F0FF", textTransform: "uppercase", fontWeight: 700 }}>
            ARCS FIELD OS
          </span>
          <span style={{ width: 1, height: 14, background: "#1e293b" }} />
          <span style={{ fontSize: 13, letterSpacing: "0.1em", color: "#94a3b8", textTransform: "uppercase" }}>
            The shoe has dropped
          </span>
        </div>

        <div style={{ fontSize: 12, color: "#475569", letterSpacing: "0.08em", textTransform: "uppercase", marginBottom: 10 }}>
          Question
        </div>
        <div style={{ fontSize: 26, fontWeight: 500, color: "#e2e8f0", lineHeight: 1.4, marginBottom: 32, maxWidth: 1000 }}>
          {shortQuestion}
        </div>

        <div style={{ fontSize: 12, color: "#475569", letterSpacing: "0.08em", textTransform: "uppercase", marginBottom: 10 }}>
          True North
        </div>
        <div style={{ fontSize: 26, fontWeight: 500, color: "#00F0FF", lineHeight: 1.4, marginBottom: 44, maxWidth: 1000, flex: 1 }}>
          {shortNorth}
        </div>

        <div style={{ display: "flex", gap: 56 }}>
          <div style={{ display: "flex", flexDirection: "column" }}>
            <span style={{ fontSize: 12, color: "#475569", letterSpacing: "0.08em", textTransform: "uppercase", marginBottom: 6 }}>Conviction</span>
            <span style={{ fontSize: 22, fontWeight: 700, color: NCI_COLOR(nci) }}>{nci}/100</span>
          </div>
          <div style={{ display: "flex", flexDirection: "column" }}>
            <span style={{ fontSize: 12, color: "#475569", letterSpacing: "0.08em", textTransform: "uppercase", marginBottom: 6 }}>Days elapsed</span>
            <span style={{ fontSize: 22, fontWeight: 700, color: "#e2e8f0" }}>{daysElapsed}d</span>
          </div>
        </div>
      </div>
    ),
    { ...size }
  )
}
