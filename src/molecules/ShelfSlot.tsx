import React from "react"
import Link from "next/link"
import { font, text, signal, space, border, resStyle } from "@/ui/tokens"
import { Card } from "@/ui/Card"

// ShelfSlot  - one slot on the Desk's shelf (brief §5/§6). A built tenant is a link; an
// unbuilt one is a labeled slot ("unbuilt", muted mono), never a link, never styled as if
// it had contents. Freshness is a dated mono stamp, a measurement, not a status pill.

export interface ShelfSlotProps {
  tenant: string
  question: string
  work: string
  built: boolean
  href?: string
  graded: string     // "YYYY-MM-DD" or "unknown"
  dirty: boolean
}

const stamp: React.CSSProperties = {
  fontFamily: font.mono,
  ...font.tier.t4,
  color: text.muted,
  textTransform: "lowercase",
  whiteSpace: "normal",
  overflowWrap: "anywhere",
}

export function ShelfSlot({ question, work, built, href, graded, dirty }: ShelfSlotProps) {
  const body = (
    <>
      <div style={{
        fontFamily: font.sans,
        fontSize: font.size.base,
        ...(built ? resStyle.SHARP : resStyle.GRAIN),  // earned-fidelity render scale (WORLD.md), not hand-rolled
        color: built ? text.primary : text.dimmed,
        lineHeight: 1.35,
        overflowWrap: "anywhere",
      }}>
        {question}
      </div>
      <div style={{ display: "flex", flexWrap: "wrap", gap: space[3], marginTop: space[3], alignItems: "baseline" }}>
        <span style={{ ...stamp, textTransform: "none", color: built ? text.secondary : text.muted }}>{work}</span>
        {!built && <span style={stamp}>unbuilt</span>}
        <span style={stamp}>graded {graded}{dirty ? " stale" : ""}</span>
      </div>
    </>
  )

  if (built && href) {
    return (
      <Link href={href} style={{ textDecoration: "none", display: "block", color: "inherit" }}>
        <Card padding="compact" style={{ borderLeft: `2px solid ${signal.cyan}`, opacity: dirty ? 0.85 : 1 }}>
          {body}
        </Card>
      </Link>
    )
  }
  return (
    <Card padding="compact" style={{ background: "transparent", boxShadow: "none", borderStyle: "dashed", borderColor: border.subtle }}>
      {body}
    </Card>
  )
}
