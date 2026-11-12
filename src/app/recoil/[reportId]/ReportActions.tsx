"use client"

import { useState } from "react"

// Export / share bar for a recoil report. Two copies, never confused:
// - internal: this page's own URL; only ADMIN_EMAILS members can open it.
// - share: the counterpart-safe twin (public/recoil-ext/<id>.html, built by
//   scripts/recoil_ext_build.sh). Shown only when the twin exists.
// The gated URL was once the only "COPY LINK" and was emailed to a counterpart
// (2026-11-11), who hit a sign-in wall. scripts/share_control_gate.py fails the
// commit if a share control copies the page URL without an internal label.
const t = {
  gold: "#C9A227",
  line: "#1e293b",
  muted: "#64748b",
  case: "#020408",
}

// sharePath: undefined = this surface has no share version (scan pages), so no
// share slot; null = a recoil report without a twin yet; string = the twin path.
export default function ReportActions({ sharePath }: { sharePath?: string | null }) {
  const [copied, setCopied] = useState<"internal" | "share" | null>(null)
  const copy = async (which: "internal" | "share") => {
    try {
      const url = which === "share" && sharePath ? `${window.location.origin}${sharePath}` : window.location.href // share-gate: internal
      await navigator.clipboard.writeText(url)
      setCopied(which)
      setTimeout(() => setCopied(null), 1600)
    } catch {
      /* clipboard blocked; no-op */
    }
  }
  const btn: React.CSSProperties = {
    background: "none",
    border: `1px solid ${t.line}`,
    color: t.muted,
    fontFamily: "ui-monospace, SF Mono, monospace",
    fontSize: 11,
    letterSpacing: "0.12em",
    padding: "7px 13px",
    borderRadius: 100,
    cursor: "pointer",
  }
  return (
    <div
      data-print="hide"
      style={{ display: "flex", gap: 8, justifyContent: "flex-end", marginBottom: 14, flexWrap: "wrap" }}
    >
      <button type="button" style={btn} onClick={() => copy("internal")} title="Only admins can open this link">
        {copied === "internal" ? "INTERNAL LINK COPIED ✓" : "⧉ COPY INTERNAL LINK · ADMINS ONLY"}
      </button>
      {sharePath ? (
        <button type="button" style={{ ...btn, borderColor: "rgba(0,255,157,.4)", color: "#00FF9D" }} onClick={() => copy("share")} title="Counterpart-safe version, opens without sign-in">
          {copied === "share" ? "SHARE LINK COPIED ✓" : "⧉ COPY SHARE LINK"}
        </button>
      ) : sharePath === null ? (
        <span style={{ ...btn, cursor: "default", borderStyle: "dashed" }} title="Build one with scripts/recoil_ext_build.sh <id>">
          NO SHARE VERSION YET
        </span>
      ) : null}
      <button
        type="button"
        style={{ ...btn, borderColor: "rgba(201,162,39,.4)", color: t.gold }}
        onClick={() => window.print()}
      >
        ⤓ EXPORT · SAVE AS PDF
      </button>
      {/* Print sheet for the report (inline styles cannot reach @page or the root).
          Dark page, edge to edge: the root background paints the page margins, and
          color-adjust keeps the dark tokens when "background graphics" is off.
          Break rules live inline on the blocks (WarRoomReport, primitives). */}
      <style>{`@media print {
  @page { size: letter; margin: 14mm 0; background: ${t.case} }
  html, body { background: ${t.case} !important; -webkit-print-color-adjust: exact; print-color-adjust: exact }
}`}</style>
    </div>
  )
}
