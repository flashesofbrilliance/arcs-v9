"use client"

import { useRef, useState } from "react"
import { createPortal } from "react-dom"
import { text, signal, font, border } from "@/ui/tokens"
import type { ZigTier } from "@/organisms/Scope"
import { parseAtlas, toZigTiers, type Atlas } from "./atlas"

// Admin-only ziggurat load. Same contract as jobs.arcs.care/atlas
// (_ARTIFACTS/atlas-loader-hud.html): the viewer picks an arcs.atlas.v1 or v2 JSON object
// from their own disk; it is read in this tab only, never uploaded, stored or fetched.
// Loading reshapes the field itself (Scope `ziggurat`): one terrace per tier, base first.
// A v2 file loads its tiers here; its edges, time and kairos belong to the HUD v2 flight view.
// The server decides whether this component is rendered at all (src/app/hud/page.tsx).

const GATE: Record<string, string> = { pass: signal.green, warn: signal.gold, fail: signal.red }
const YG: Record<string, string> = { GREEN: signal.green, YELLOW: signal.gold, RED: signal.red }
const str = (v: unknown, n: number) => (typeof v === "string" ? v.slice(0, n) : "")

export function ZigguratLoader({ onLoad }: { onLoad: (tiers: ZigTier[] | null) => void }) {
  const [open, setOpen] = useState(false)
  const [atlas, setAtlas] = useState<Atlas | null>(null)
  const [err, setErr] = useState("")
  const input = useRef<HTMLInputElement>(null)

  const load = (file: File | undefined) => {
    setErr("")
    if (!file) return
    if (file.size > 5e6) { setErr("File is over 5 MB; not an atlas object."); return }
    const r = new FileReader()
    r.onload = () => {
      const got = parseAtlas(String(r.result))
      if ("error" in got) { setErr(got.error); return }
      setAtlas(got.atlas)
      onLoad(toZigTiers(got.atlas))
    }
    r.onerror = () => setErr("Could not read the file.")
    r.readAsText(file)
  }

  const mono = { fontFamily: font.mono, fontSize: 11, letterSpacing: "0.04em" }
  const btn = { ...mono, minHeight: 32, padding: "6px 12px", borderRadius: 3, cursor: "pointer", color: text.primary, background: "rgba(2,5,10,0.85)", border: `1px solid ${border.subtle}` }

  const tiers = atlas ? atlas.tiers.slice(0, 12) : []
  const W = 800, H = 60 + tiers.length * 64

  return (
    <>
      <button type="button" aria-expanded={open} onClick={() => setOpen((o) => !o)}
        aria-label={open ? "Close ziggurat loader" : "Load ziggurat"} title="Load ziggurat (admin)"
        style={{ ...btn, minHeight: 28, padding: "4px 10px", textTransform: "uppercase", color: open ? text.primary : text.secondary, background: open ? "rgba(0,240,255,0.12)" : "transparent", border: `1px solid ${open ? "rgba(0,240,255,0.55)" : border.subtle}` }}>
        {"\u25B3"}
      </button>
      {open && createPortal(
        <section aria-label="Ziggurat loader" style={{ position: "fixed", zIndex: 1001, top: 16, right: 12, left: 12, maxWidth: 560, marginLeft: "auto", maxHeight: "calc(100dvh - 80px)", lineHeight: 1.4, textAlign: "left", overflowY: "auto", padding: 16, borderRadius: 8, background: "rgba(13,17,23,0.94)", border: `1px solid ${border.subtle}`, color: text.primary }}>
          <p style={{ margin: "0 0 12px", fontSize: 14, lineHeight: 1.5, color: text.secondary }}>
            Load an arcs.atlas.v1 or v2 object from your own disk. It is read in this tab only: nothing is uploaded, stored, or fetched.
          </p>
          <div
            onDragOver={(e) => e.preventDefault()}
            onDrop={(e) => { e.preventDefault(); load(e.dataTransfer.files[0]) }}
            style={{ padding: 16, borderRadius: 6, border: `1px dashed ${border.subtle}`, textAlign: "center" }}>
            <input ref={input} id="zig-file" type="file" accept="application/json,.json" onChange={(e) => load(e.target.files?.[0])}
              style={{ position: "absolute", width: 1, height: 1, opacity: 0 }} />
            <button type="button" onClick={() => input.current?.click()} style={btn}>Choose file</button>
            <div style={{ ...mono, marginTop: 8, color: text.secondary }}>or drop it here</div>
          </div>
          {err && <div role="alert" style={{ ...mono, marginTop: 12, color: signal.red }}>{err}</div>}
          {atlas && (
            <div aria-live="polite" style={{ marginTop: 16 }}>
              <p style={{ margin: "0 0 8px", fontSize: 14, lineHeight: 1.5, color: text.secondary }}>
                The field now stands on these {tiers.length} tiers.
              </p>
              <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label="Atlas ziggurat" style={{ width: "100%", height: "auto", display: "block" }}>
                {tiers.map((t, i) => {
                  const w = W - (i * (W - 240)) / Math.max(tiers.length - 1, 1), y = H - 60 - (i + 1) * 64 + 8
                  const g = t.gate === "fail" ? "fail" : t.gate === "warn" ? "warn" : "pass"
                  const docs = Array.isArray(t.docs) ? t.docs.length : Number(t.docs) || 0
                  return (
                    <g key={i}>
                      <rect x={(W - w) / 2} y={y} width={w} height={56} fill="#0d1117" stroke={GATE[g]} strokeWidth={2} />
                      <text x={W / 2} y={y + 34} textAnchor="middle" fill="#e2e8f0" fontSize={16}>{`${str(t.name, 24)}  ·  ${docs} docs`}</text>
                    </g>
                  )
                })}
              </svg>
              <div style={{ ...mono, marginTop: 8, color: YG[str(atlas.gate, 12)] ?? text.secondary }}>
                {`schema ${str(atlas.schema, 40)} · built ${str(atlas.built, 40)} · gate ${str(atlas.gate, 12)}`}
              </div>
              <button type="button" onClick={() => { setAtlas(null); onLoad(null); if (input.current) input.current.value = "" }} style={{ ...btn, marginTop: 12 }}>
                Restore default field
              </button>
            </div>
          )}
        </section>,
        document.body,
      )}
    </>
  )
}
