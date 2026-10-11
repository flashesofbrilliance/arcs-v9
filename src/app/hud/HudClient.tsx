"use client"

import { useState } from "react"
import dynamic from "next/dynamic"
import { ZigguratLoader } from "./ZigguratLoader"

// Client only: pinned full HUD sizes itself from the window on first paint, which the
// server cannot know, so server HTML would never match.
const Scope = dynamic(() => import("@/organisms/Scope").then((m) => m.Scope), { ssr: false })

// Full-screen field. Fog starts cleared enough to read the terrain; nothing here
// writes a row, so `clear` stays false and the bearing to true north is not drawn.
export function HudClient({ admin }: { admin: boolean }) {
  const [fog] = useState(0.35)
  return (
    <main style={{ position: "fixed", inset: 0, background: "#02050a", overflow: "hidden" }}>
      <h1 style={{ position: "absolute", width: 1, height: 1, overflow: "hidden", clip: "rect(0 0 0 0)", whiteSpace: "nowrap" }}>ARCS field HUD</h1>
      <Scope fog={fog} clear={false} zone="Field" zoneColor="#00F0FF" pinned barSlot={admin ? <ZigguratLoader /> : null} />
    </main>
  )
}
