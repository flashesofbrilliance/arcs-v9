// Pointer-type probe — a tiny on-screen diagnostic for verifying the Reflect
// stylus gate on real devices (where a JS console isn't handy).
//
// Enable by appending ?ptdebug to any URL (works on preview/prod), or it shows
// automatically in development. On every pointerup it reports the pointerType
// (mouse | pen | touch), the current selection length, and whether Reflect WOULD
// raise its picker for that input. On an iPad: finger should read "touch · ✕"
// (native iOS menu owns it), Apple Pencil should read "pen · ✓".
"use client"

import { useEffect, useState } from "react"
import { font } from "@/ui/tokens"

export function PointerTypeProbe() {
  const [enabled, setEnabled] = useState(false)
  const [info, setInfo] = useState<{ type: string; len: number; fires: boolean } | null>(null)

  useEffect(() => {
    const flagged = window.location.search.includes("ptdebug") || process.env.NODE_ENV !== "production"
    if (!flagged) return
    // One-time mount gate. Done in an effect (not at render) so the server and
    // first client paint agree on "null" — avoids a hydration mismatch for this
    // debug-only overlay. Intentional, hence the disable.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setEnabled(true)
    const onUp = (e: PointerEvent) => {
      const len = (window.getSelection()?.toString().trim().length) ?? 0
      // Mirror ReflectLayer's gate: precise pointer + a real selection.
      const fires = e.pointerType !== "touch" && len >= 3
      setInfo({ type: e.pointerType || "—", len, fires })
    }
    document.addEventListener("pointerup", onUp)
    return () => document.removeEventListener("pointerup", onUp)
  }, [])

  if (!enabled) return null

  const color = info?.type === "pen" ? "#00FF9D" : info?.type === "mouse" ? "#00F0FF" : info?.type === "touch" ? "#FF4D6D" : "#475569"

  return (
    <div style={{
      position: "fixed", left: 10, bottom: 10, zIndex: 99999,
      fontFamily: font.mono, fontSize: 11, lineHeight: 1.5,
      background: "rgba(2,4,8,.92)", color: "#e2e8f0",
      border: `.5px solid ${color}`, borderRadius: 6,
      padding: "7px 10px", letterSpacing: ".04em", pointerEvents: "none",
      boxShadow: `0 0 10px ${color}33`,
    }}>
      <div style={{ color: "#64748b", fontSize: 9, letterSpacing: ".12em", textTransform: "uppercase", marginBottom: 3 }}>pointer probe</div>
      <div>type: <strong style={{ color }}>{info?.type ?? "—"}</strong></div>
      <div>selection: {info?.len ?? 0} chars</div>
      <div>reflect picker: <strong style={{ color: info?.fires ? "#00FF9D" : "#FF4D6D" }}>{info ? (info.fires ? "✓ fires" : "✕ native") : "—"}</strong></div>
    </div>
  )
}
