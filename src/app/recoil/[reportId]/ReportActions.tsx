"use client"

import { useState } from "react"

// Export / share bar for a recoil report. Internal share = copy the stable,
// magic-link-gated URL (only other ADMIN_EMAILS members can open it); export =
// browser print-to-PDF. No new deps, no server write. For a counterpart-facing
// share, generate a sanitized public variant instead (never this gated URL).
const t = {
  gold: "#C9A227",
  line: "#1e293b",
  muted: "#64748b",
  case: "#020408",
}

export default function ReportActions() {
  const [copied, setCopied] = useState(false)
  const copy = async () => {
    try {
      await navigator.clipboard.writeText(window.location.href)
      setCopied(true)
      setTimeout(() => setCopied(false), 1600)
    } catch {
      /* clipboard blocked; no-op */
    }
  }
  const btn: React.CSSProperties = {
    background: "none",
    border: `1px solid ${t.line}`,
    color: t.muted,
    fontFamily: "ui-monospace, SF Mono, monospace",
    fontSize: 10,
    letterSpacing: "0.12em",
    padding: "7px 13px",
    borderRadius: 100,
    cursor: "pointer",
  }
  return (
    <div
      className="no-print"
      style={{ display: "flex", gap: 8, justifyContent: "flex-end", marginBottom: 14, flexWrap: "wrap" }}
    >
      <button type="button" style={btn} onClick={copy}>
        {copied ? "LINK COPIED ✓" : "⧉ COPY LINK"}
      </button>
      <button
        type="button"
        style={{ ...btn, borderColor: "rgba(201,162,39,.4)", color: t.gold }}
        onClick={() => window.print()}
      >
        ⤓ EXPORT · SAVE AS PDF
      </button>
      <style>{`@media print { .no-print { display: none !important } }`}</style>
    </div>
  )
}
