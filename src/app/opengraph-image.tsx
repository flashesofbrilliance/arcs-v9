import { ImageResponse } from "next/og"

export const runtime = "nodejs"
export const size = { width: 1200, height: 630 }
export const contentType = "image/png"
export const alt = "ARCS — Navigate to clarity"

// Static brand card for the landing page. Mirrors the styling idiom of
// brief/[receiptId]/opengraph-image.tsx (cyan left rail, obsidian bg) but
// deliberately touches no DB — the apex share card must never depend on a
// pinned receipt existing.
export default function OGImage() {
  return new ImageResponse(
    (
      <div
        style={{
          width: 1200, height: 630,
          background: "#020408",
          display: "flex", flexDirection: "column", justifyContent: "space-between",
          padding: "72px 80px",
          fontFamily: "sans-serif",
          position: "relative",
        }}
      >
        <div style={{ position: "absolute", top: 0, bottom: 0, left: 0, width: 4, background: "#00F0FF" }} />

        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          <span style={{ fontSize: 13, letterSpacing: "0.15em", color: "#00F0FF", textTransform: "uppercase", fontWeight: 700 }}>
            ARCS
          </span>
          <span style={{ width: 1, height: 14, background: "#1e293b" }} />
          <span style={{ fontSize: 13, letterSpacing: "0.1em", color: "#94a3b8", textTransform: "uppercase" }}>
            Question Compass
          </span>
        </div>

        <div style={{ display: "flex", flexDirection: "column" }}>
          <div style={{ fontSize: 64, fontWeight: 600, color: "#e2e8f0", lineHeight: 1.15, letterSpacing: "-0.02em" }}>
            What are you really
          </div>
          <div style={{ fontSize: 64, fontWeight: 600, color: "#e2e8f0", lineHeight: 1.15, letterSpacing: "-0.02em" }}>
            trying to decide?
          </div>
        </div>

        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <span style={{ fontSize: 20, color: "#64748b" }}>
            One clear direction — with the reasoning, the tradeoffs, and what to watch next.
          </span>
          <span style={{ fontSize: 14, letterSpacing: "0.1em", color: "#00F0FF", textTransform: "uppercase", fontWeight: 700 }}>
            arcs.care
          </span>
        </div>
      </div>
    ),
    size
  )
}
