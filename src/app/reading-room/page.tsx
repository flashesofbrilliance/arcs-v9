import React from "react"
import Link from "next/link"
import { surface, text, font, space, border } from "@/ui/tokens"
import { ShelfSlot } from "@/molecules/ShelfSlot"
import { gateDesk, readDesk, readCache, freshnessFor, readoutFor } from "./_desk"

// The Desk (/reading-room)  - the reader's intent router for the PRIVATE reading room.
// Brief: _SPECS/desk-shape-brief-v1.md (v1.3, all decisions closed). Hierarchy: the five
// questions ARE the heading (never "what are you here to do?"), the shelf second, one mono
// readout third. NOT a dashboard: no plot. Admin-gated exactly like /recoil, fail-closed.
export const dynamic = "force-dynamic"

const measureVar = { "--measure": "44rem" } as React.CSSProperties

export default async function ReadingRoomDesk() {
  await gateDesk("/reading-room")

  const desk = readDesk()
  const cache = readCache()
  const readout = readoutFor(cache)

  return (
    <main style={{ ...measureVar, minHeight: "100vh", background: surface.bg, color: text.primary, fontFamily: font.sans }}>
      <div style={{ maxWidth: "var(--measure)", margin: "0 auto", padding: `${space[10]} ${space[4]} ${space[12]}` }}>
        <div style={{ fontFamily: font.mono, ...font.tier.t2, color: text.muted, textTransform: "uppercase", marginBottom: space[8] }}>
          reading room
        </div>

        {/* First screen: the questions the room answers, set as type, not buttons. */}
        <h1 style={{ margin: 0, fontWeight: 400, fontSize: "clamp(1.375rem, 2.6vw + 0.5rem, 2rem)", lineHeight: 1.3, letterSpacing: "-0.01em" }}>
          {desk.shelf.map((s) => {
            const line: React.CSSProperties = {
              display: "block",
              overflowWrap: "anywhere",
              color: s.built ? text.primary : text.dimmed,
              fontWeight: s.built ? 400 : 300,
              opacity: s.built ? 1 : 0.7,
              padding: `${space[2]} 0`,
              textDecoration: "none",
            }
            return s.built
              ? <Link key={s.tenant} href={`${desk.route}/${s.tenant}`} style={line}>{s.question}</Link>
              : <span key={s.tenant} style={line}>{s.question}</span>
          })}
        </h1>

        {/* Second: the shelf. */}
        <div style={{ borderTop: `1px solid ${border.subtle}`, margin: `${space[10]} 0 ${space[6]}` }} />
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(15rem, 1fr))", gap: space[3] }}>
          {desk.shelf.map((s) => {
            const f = freshnessFor(cache, s.domains)
            return (
              <ShelfSlot
                key={s.tenant}
                tenant={s.tenant}
                question={s.question}
                work={s.work}
                built={s.built}
                href={s.built ? `${desk.route}/${s.tenant}` : undefined}
                graded={f.graded}
                dirty={f.dirty}
              />
            )
          })}
        </div>

        {/* Third: one mono readout line. No plot. */}
        <div style={{
          marginTop: space[8],
          fontFamily: font.mono,
          ...font.tier.t4,
          color: text.muted,
          display: "flex",
          flexWrap: "wrap",
          gap: `${space[1]} ${space[3]}`,
        }}>
          <span>{readout.nodeCount === null ? "nodes unknown" : `${readout.nodeCount} nodes`}</span>
          <span aria-hidden="true">&middot;</span>
          <span>last graded {readout.lastGraded}</span>
          <span aria-hidden="true">&middot;</span>
          <span>{readout.dirtySlices === null ? "stale slices unknown" : `${readout.dirtySlices} stale ${readout.dirtySlices === 1 ? "slice" : "slices"}`}</span>
          {desk.error && (<><span aria-hidden="true">&middot;</span><span>{desk.error}</span></>)}
        </div>
      </div>
    </main>
  )
}
