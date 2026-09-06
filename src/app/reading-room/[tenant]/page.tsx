import React from "react"
import Link from "next/link"
import { notFound } from "next/navigation"
import { surface, text, font, space, border } from "@/ui/tokens"
import { gateDesk, readDesk, readCache, freshnessFor } from "../_desk"

// Tenant frame (/reading-room/[tenant]) — desk -> tenant (full frame) -> back. The tenant's
// own render is served through the gated /api/reading-room/<tenant> handler and framed here,
// not rebuilt. Unknown or unbuilt tenant -> notFound (an unbuilt slot is never a link).
export const dynamic = "force-dynamic"

export default async function TenantFrame({ params }: { params: Promise<{ tenant: string }> }) {
  const { tenant } = await params
  await gateDesk(`/reading-room/${tenant}`)

  const desk = readDesk()
  const slot = desk.shelf.find((s) => s.tenant === tenant)
  if (!slot || !slot.built || !slot.frame) notFound()

  const f = freshnessFor(readCache(), slot.domains)
  const rail: React.CSSProperties = { fontFamily: font.mono, ...font.tier.t4, color: text.muted, overflowWrap: "anywhere" }

  return (
    <main style={{ height: "100dvh", display: "flex", flexDirection: "column", background: surface.bg, color: text.primary, fontFamily: font.sans }}>
      <div style={{
        display: "flex",
        flexWrap: "wrap",
        alignItems: "baseline",
        gap: `${space[1]} ${space[4]}`,
        padding: `${space[3]} ${space[4]}`,
        borderBottom: `1px solid ${border.subtle}`,
      }}>
        <Link href={desk.route} style={{ ...rail, color: text.secondary, textDecoration: "none" }}>back to the desk</Link>
        <span style={{ ...rail, color: text.primary }}>{slot.work}</span>
        <span style={rail}>{slot.question}</span>
        <span style={rail}>graded {f.graded}{f.dirty ? " stale" : ""}</span>
      </div>
      {/* The render is a self-contained document (data inlined, scripts for the Reader, Blob
          export). Sandboxed WITHOUT allow-same-origin: it runs on an opaque origin, so it can
          never read the admin's cookies or storage; downloads stay allowed for per-row export. */}
      <iframe
        title={slot.work}
        src={slot.frame}
        sandbox="allow-scripts allow-downloads allow-popups"
        referrerPolicy="no-referrer"
        style={{ flex: 1, width: "100%", border: "none", background: surface.bg }}
      />
    </main>
  )
}
