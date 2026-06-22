import { ImageResponse } from "next/og"
import { prisma } from "@/lib/db"

export const runtime = "nodejs"
export const size = { width: 1200, height: 630 }
export const contentType = "image/png"

const NCI_COLOR = (s: number) => s >= 70 ? "#00FF9D" : s >= 45 ? "#FFD700" : "#FF4D6D"

const Y_LABEL: Record<string, { label: string; color: string }> = {
  GREEN:   { label: "CLARITY RIDGE",          color: "#00FF9D" },
  YELLOW:  { label: "PRESSURE BAND",          color: "#FFD700" },
  RED:     { label: "CLIFF EDGE · COURT",     color: "#FF4D6D" },
  FORK:    { label: "FORK · PATH SELECTION",  color: "#00F0FF" },
  SCRATCH: { label: "FOG LAYER · ORIENT",     color: "#475569" },
  DELTA:   { label: "CONVICTION SHIFT",       color: "#A78BFA" },
  DRIFT:   { label: "DRIFT · LAND THE PLANE", color: "#FB923C" },
  PARADOX: { label: "PARADOX · CURATOR",      color: "#E879F9" },
}

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
  const yState = receipt?.yState ?? "GREEN"
  const mode = receipt?.mode ?? "PLAN"
  const door = receipt?.doorClass ?? "TWO_WAY"
  const weather = Y_LABEL[yState] ?? Y_LABEL.GREEN

  // Truncate for display
  const shortDecision = decision.length > 90 ? decision.slice(0, 87) + "…" : decision
  const shortNorth = trueNorth.length > 130 ? trueNorth.slice(0, 127) + "…" : trueNorth

  return new ImageResponse(
    (
      <div
        style={{
          width: 1200, height: 630,
          background: "#020408",
          display: "flex", flexDirection: "column",
          padding: "60px 72px",
          fontFamily: "sans-serif",
          position: "relative",
        }}
      >
        {/* Top border accent */}
        <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 3, background: "#00F0FF" }} />

        {/* Header */}
        <div style={{ display: "flex", alignItems: "center", gap: 16, marginBottom: 48 }}>
          <span style={{ fontSize: 11, letterSpacing: "0.15em", color: "#00F0FF", textTransform: "uppercase", fontWeight: 700 }}>
            ARCS FIELD OS
          </span>
          <span style={{ width: 1, height: 14, background: "#1e293b" }} />
          <span style={{ fontSize: 11, letterSpacing: "0.12em", color: "#475569", textTransform: "uppercase" }}>
            Decision Brief
          </span>
          <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: 8 }}>
            <div style={{
              padding: "4px 12px", borderRadius: 6,
              background: `${weather.color}15`,
              border: `1px solid ${weather.color}44`,
            }}>
              <span style={{ fontSize: 10, color: weather.color, fontWeight: 700, letterSpacing: "0.1em", textTransform: "uppercase" }}>
                {weather.label}
              </span>
            </div>
          </div>
        </div>

        {/* Decision */}
        <div style={{ fontSize: 13, color: "#475569", letterSpacing: "0.08em", textTransform: "uppercase", marginBottom: 14 }}>
          Decision under navigation
        </div>
        <div style={{ fontSize: 26, fontWeight: 600, color: "#e2e8f0", lineHeight: 1.35, marginBottom: 40, maxWidth: 900 }}>
          {shortDecision}
        </div>

        {/* True North */}
        <div style={{
          padding: "24px 28px",
          background: "#0d1117",
          border: "1px solid rgba(0,240,255,0.2)",
          borderRadius: 10,
          marginBottom: 40,
          flex: 1,
          display: "flex", flexDirection: "column", justifyContent: "center",
        }}>
          <div style={{ fontSize: 11, color: "#00F0FF", letterSpacing: "0.12em", textTransform: "uppercase", fontWeight: 700, marginBottom: 12 }}>
            True North · {mode} · {door}
          </div>
          <div style={{ fontSize: 22, color: "#e2e8f0", lineHeight: 1.5, fontWeight: 500 }}>
            {shortNorth}
          </div>
        </div>

        {/* Footer metrics */}
        <div style={{ display: "flex", alignItems: "center", gap: 24 }}>
          <div style={{ display: "flex", alignItems: "baseline", gap: 6 }}>
            <span style={{ fontSize: 36, fontWeight: 700, color: NCI_COLOR(nci), lineHeight: 1 }}>{nci}</span>
            <span style={{ fontSize: 14, color: "#475569" }}>/100 NCI</span>
          </div>
          <div style={{ width: 1, height: 28, background: "#1e293b" }} />
          <span style={{ fontSize: 12, color: "#475569" }}>arcs.app/brief/{receiptId.slice(0, 8)}…</span>
          <div style={{ marginLeft: "auto" }}>
            <span style={{ fontSize: 11, color: "#1e293b", letterSpacing: "0.1em" }}>
              Navigate to clarity · Make the decision visible
            </span>
          </div>
        </div>
      </div>
    ),
    { ...size }
  )
}
