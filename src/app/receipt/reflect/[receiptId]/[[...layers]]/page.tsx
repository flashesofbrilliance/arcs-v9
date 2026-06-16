// Canonical reflect surface for a receipt.
// URL: /receipt/reflect/[id]                 → all layers on
//      /receipt/reflect/[id]/thoughts         → thoughts only
//      /receipt/reflect/[id]/thoughts+comments → composable
"use client"

import { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { surface, text, signal, border, font, getWeather, nciColor, contentContainer } from "@/ui/tokens"
import { useVw } from "@/ui/useVw"
import { FatedGrid } from "@/molecules/FatedGrid"
import { TerrainPaths } from "@/molecules/TerrainPaths"
import { SequenceLoader } from "@/molecules/SequenceLoader"
import { ReflectLayer, parseLayerSegment } from "@/organisms/ReflectLayer"

function safeParse<T>(v: unknown, fallback: T): T {
  if (typeof v !== "string") return (v as T) ?? fallback
  try { return JSON.parse(v) as T } catch { return fallback }
}

interface ReceiptData {
  id: string; decision: string; trueNorth: string; whyBullets: string
  nciScore: number; coherencePct?: number; mode: string; doorClass: string
  yState: string; fated: string; paths: string; macroTags: string
  stakesLevel?: string; horizon?: string; version: number
  createdAt: string; courtVerdict?: string
}

function Pill({ label, value, color }: { label: string; value: string; color: string }) {
  return (
    <div style={{ display: "flex", alignItems: "center", border: `0.5px solid ${color}44`, borderRadius: 3, overflow: "hidden", fontSize: "0.6rem" }}>
      <span style={{ background: `${color}18`, padding: "0.2rem 0.4rem", color, fontFamily: "monospace", letterSpacing: "0.08em", textTransform: "uppercase" }}>{label}</span>
      <span style={{ padding: "0.2rem 0.5rem", color: "rgb(226,232,240)", fontFamily: "monospace", background: "rgba(13,17,23,0.5)" }}>{value}</span>
    </div>
  )
}

export default function ReceiptReflectPage() {
  const params = useParams()
  const router = useRouter()
  const receiptId = String(params.receiptId)
  const vw = useVw()
  const layersParam = Array.isArray(params.layers) ? params.layers[0] : (params.layers as string | undefined)
  const defaultLayers = parseLayerSegment(layersParam)
  const layerUrlBase = `/receipt/reflect/${receiptId}`

  const [receipt, setReceipt] = useState<ReceiptData | null>(null)
  const [hasBrief, setHasBrief] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    fetch(`/api/brief/${receiptId}`)
      .then(async (r) => ({ ok: r.ok, data: await r.json() }))
      .then(({ ok, data }) => {
        if (cancelled) return
        if (!ok) { setError(data.error ?? "Could not load receipt"); return }
        setReceipt(data.receipt as ReceiptData)
        setHasBrief(!!data.brief)
      })
      .catch(() => { if (!cancelled) setError("Could not load receipt") })
    return () => { cancelled = true }
  }, [receiptId])

  if (error) {
    return (
      <main style={{ minHeight: "100vh", background: surface.bg, color: text.primary, display: "flex", alignItems: "center", justifyContent: "center" }}>
        <div style={{ fontFamily: font.sans, color: signal.red, fontSize: "0.9rem" }}>{error}</div>
      </main>
    )
  }
  if (!receipt) {
    return (
      <main style={{ minHeight: "100vh", background: surface.bg, color: text.primary, display: "flex", alignItems: "center", justifyContent: "center", padding: "2rem" }}>
        <SequenceLoader title="Loading receipt…" stages={[{ name: "FETCH" }, { name: "RENDER" }]} footer="Loading decision receipt…" />
      </main>
    )
  }

  const why = safeParse<string[]>(receipt.whyBullets, [])
  const fated = safeParse<Record<string, unknown>>(receipt.fated, {})
  const paths = safeParse<unknown[]>(receipt.paths, [])
  const macroTags = safeParse<string[]>(receipt.macroTags, [])
  const w = getWeather(receipt.yState)
  const nc = nciColor(receipt.nciScore)

  return (
    <ReflectLayer
      receiptId={receiptId}
      surface="RECEIPT"
      defaultHudOpen={true}
      defaultLayers={defaultLayers}
      layerUrlBase={layerUrlBase}
    >
      <main style={{ minHeight: "100vh", background: surface.bg, color: text.primary }}>
        {/* Header */}
        <div style={{ borderBottom: `0.5px solid rgba(0,240,255,0.12)`, background: "rgba(0,240,255,0.03)" }}>
          <div style={{ ...contentContainer(vw), paddingTop: "0.6rem", paddingBottom: "0.6rem", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
              <button onClick={() => router.push("/history")} style={{ background: "none", border: "none", cursor: "pointer", fontFamily: font.mono, fontSize: "0.6rem", letterSpacing: "0.1em", color: text.dimmed, textTransform: "uppercase", padding: 0 }}>Ledger</button>
              <span style={{ color: text.dimmed, fontFamily: font.mono, fontSize: "0.6rem" }}>·</span>
              <button onClick={() => router.push(`/receipt/${receiptId}`)} style={{ background: "none", border: "none", cursor: "pointer", fontFamily: font.mono, fontSize: "0.6rem", letterSpacing: "0.1em", color: text.dimmed, textTransform: "uppercase", padding: 0 }}>Receipt</button>
              <span style={{ color: signal.cyan, fontFamily: font.mono, fontSize: "0.6rem" }}>·</span>
              <span style={{ fontFamily: font.mono, fontSize: "0.6rem", letterSpacing: "0.1em", color: signal.cyan, textTransform: "uppercase" }}>◎ Reflect</span>
            </div>
            {hasBrief && (
              <button onClick={() => router.push(`/brief/reflect/${receiptId}`)} style={{ background: `${signal.cyan}11`, border: `0.5px solid ${signal.cyan}44`, borderRadius: 4, padding: "0.3rem 0.7rem", cursor: "pointer", fontFamily: font.mono, fontSize: "0.6rem", color: signal.cyan, textTransform: "uppercase" }}>
                Brief reflect →
              </button>
            )}
          </div>
        </div>

        <div style={{ ...contentContainer(vw), paddingTop: "3rem", paddingBottom: "6rem" }}>
          {/* Status line — fog fidelity */}
          <div style={{ fontFamily: font.mono, fontSize: "0.6rem", letterSpacing: "0.12em", color: w.color, textTransform: "uppercase", marginBottom: "1rem" }}>{w.icon} {w.label} · {receipt.yState}</div>

          {/* Decision — the question, at the top (mirrors the brief pattern) */}
          <div style={{ marginBottom: "1.75rem", padding: "1.25rem 1.5rem", background: "rgba(13,17,23,0.6)", border: `0.5px solid ${border.subtle}`, borderRadius: 6 }}>
            <div style={{ fontFamily: font.mono, fontSize: "0.6rem", letterSpacing: "0.12em", color: text.dimmed, textTransform: "uppercase", marginBottom: "0.4rem" }}>Decision</div>
            <div style={{ fontFamily: font.sans, fontSize: "0.9rem", color: text.secondary, lineHeight: 1.85 }}>{receipt.decision}</div>
          </div>

          {/* True North */}
          <div style={{ marginBottom: "1.75rem" }}>
            <div style={{ fontFamily: font.mono, fontSize: "0.6rem", letterSpacing: "0.14em", color: signal.cyan, textTransform: "uppercase", marginBottom: "0.5rem" }}>True North</div>
            <div style={{ fontFamily: font.sans, fontSize: "clamp(1.1rem, 2.5vw, 1.5rem)", fontWeight: 600, color: text.primary, lineHeight: 2.0 }}>{receipt.trueNorth}</div>
          </div>

          {/* Conviction — full-width strip, right below True North */}
          <div style={{ display: "flex", alignItems: "center", gap: "1.5rem", padding: "1.25rem 1.5rem", background: "rgba(13,17,23,0.6)", border: `0.5px solid ${border.subtle}`, borderRadius: 6, marginBottom: "1.75rem", flexWrap: "wrap" }}>
            <div style={{ flexShrink: 0 }}>
              <div style={{ fontFamily: font.mono, fontSize: "0.55rem", letterSpacing: "0.12em", color: text.dimmed, textTransform: "uppercase", marginBottom: "0.2rem" }}>Conviction</div>
              <div style={{ fontFamily: font.sans, fontSize: "2.25rem", fontWeight: 700, color: nc, lineHeight: 1, textShadow: `0 0 12px ${nc}55` }}>{receipt.nciScore}</div>
              <div style={{ fontFamily: font.mono, fontSize: "0.55rem", color: text.dimmed, marginTop: "0.2rem", letterSpacing: "0.06em" }}>/ 100</div>
            </div>
            <div style={{ width: "0.5px", height: 44, background: border.subtle, flexShrink: 0 }} />
            <div style={{ display: "flex", gap: "1.5rem", flexWrap: "wrap" }}>
              {([
                ["Mode", receipt.mode],
                ["Door", receipt.doorClass?.replace(/_/g, " ")],
                ["Coherence", receipt.coherencePct != null ? `${receipt.coherencePct}%` : "—"],
              ] as [string, string][]).map(([k, v]) => (
                <div key={k}>
                  <div style={{ fontFamily: font.mono, fontSize: "0.55rem", letterSpacing: "0.1em", color: text.muted, textTransform: "uppercase", marginBottom: "0.2rem" }}>{k}</div>
                  <div style={{ fontFamily: font.mono, fontSize: "0.75rem", color: text.secondary }}>{v}</div>
                </div>
              ))}
            </div>
          </div>

          {why.length > 0 && (
            <div style={{ marginBottom: "1.75rem" }}>
              <div style={{ fontFamily: font.mono, fontSize: "0.6rem", letterSpacing: "0.12em", color: text.dimmed, textTransform: "uppercase", marginBottom: "0.75rem" }}>Why This</div>
              <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
                {why.map((bullet, i) => (
                  <div key={i} style={{ display: "flex", gap: "0.75rem", alignItems: "flex-start" }}>
                    <span style={{ fontFamily: font.mono, fontSize: "0.7rem", color: signal.cyan, fontWeight: 700, flexShrink: 0, marginTop: "0.15rem" }}>{String(i + 1).padStart(2, "0")}</span>
                    <span style={{ fontFamily: font.sans, fontSize: "0.875rem", color: text.secondary, lineHeight: 1.85 }}>{bullet}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Terrain Paths — single column, directly under Why */}
          {paths.length > 0 && (
            <div style={{ marginBottom: "1.75rem" }}>
              <TerrainPaths paths={paths as Parameters<typeof TerrainPaths>[0]["paths"]} />
            </div>
          )}

          {/* FATED Decomposition — single column */}
          {Object.keys(fated).length > 0 && (
            <div style={{ marginBottom: "1.75rem" }}>
              <FatedGrid fated={fated} />
            </div>
          )}

          {/* Court Verdict — standalone card, same atom as Decision */}
          {receipt.courtVerdict && (
            <div style={{ marginBottom: "1.75rem", padding: "1.25rem 1.5rem", background: "rgba(13,17,23,0.6)", border: `0.5px solid ${border.subtle}`, borderRadius: 6 }}>
              <div style={{ fontFamily: font.mono, fontSize: "0.6rem", letterSpacing: "0.12em", color: text.dimmed, textTransform: "uppercase", marginBottom: "0.4rem" }}>Court Verdict</div>
              <div style={{ fontFamily: font.sans, fontSize: "0.9rem", color: text.secondary, lineHeight: 1.85 }}>{receipt.courtVerdict}</div>
            </div>
          )}

          <div style={{ borderTop: `0.5px solid ${border.subtle}`, paddingTop: "1.25rem", display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
            <Pill label="MODE" value={receipt.mode} color={signal.gold} />
            <Pill label="DOOR" value={receipt.doorClass?.replace(/_/g, " ")} color={signal.steel} />
            {receipt.stakesLevel && <Pill label="STAKES" value={receipt.stakesLevel} color={signal.red} />}
            {receipt.horizon && <Pill label="HORIZON" value={receipt.horizon} color={text.muted} />}
            <Pill label="NCI" value={String(receipt.nciScore)} color={nc} />
            {receipt.coherencePct != null && <Pill label="COHERENCE" value={`${receipt.coherencePct}%`} color={signal.green} />}
            {macroTags.map((tag) => <Pill key={tag} label="MACRO" value={tag} color={text.dimmed} />)}
            <Pill label="Y" value={`${w.icon} ${w.label}`} color={w.color} />
            <Pill label="DATE" value={new Date(receipt.createdAt).toLocaleDateString()} color={text.dimmed} />
          </div>
        </div>
      </main>
    </ReflectLayer>
  )
}
