// Canonical reflect surface for a receipt.
// URL: /receipt/reflect/[id]                 → all layers on
//      /receipt/reflect/[id]/thoughts         → thoughts only
//      /receipt/reflect/[id]/thoughts+comments → composable
"use client"

import { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { surface, text, signal, font, getWeather, nciColor } from "@/ui/tokens"
import { FatedGrid } from "@/molecules/FatedGrid"
import { TerrainPaths } from "@/molecules/TerrainPaths"
import { ConvictionSidebar } from "@/molecules/ConvictionSidebar"
import { SequenceLoader } from "@/molecules/SequenceLoader"
import { ReflectLayer, parseLayerSegment } from "@/organisms/ReflectLayer"
import type { CompassResult } from "@/lib/mockCompass"

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

  const compassResult: CompassResult = {
    receipt_id: receipt.id, question: receipt.decision, true_north: receipt.trueNorth,
    why, nci_score: receipt.nciScore, coherence_pct: receipt.coherencePct,
    is_satoshi: false, decision_mode: receipt.mode, door_class: receipt.doorClass,
    y_state: receipt.yState, render_resolution: "SHARP", nci_delta: null,
    macro_tags: macroTags, tributaries: [],
    reasoning: {
      fated: fated as unknown as CompassResult["reasoning"]["fated"],
      paths: paths as unknown as CompassResult["reasoning"]["paths"],
      court_verdict: receipt.courtVerdict,
    },
  }

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
          <div style={{ maxWidth: 960, margin: "0 auto", padding: "0.6rem 1.5rem", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
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

        <div style={{ maxWidth: 960, margin: "0 auto", padding: "2rem 1.5rem 6rem" }}>
          <div style={{ marginBottom: "2rem" }}>
            <div style={{ fontFamily: font.mono, fontSize: "0.6rem", letterSpacing: "0.14em", color: signal.cyan, textTransform: "uppercase", marginBottom: "0.5rem" }}>True North</div>
            <div style={{ fontFamily: font.sans, fontSize: "clamp(1.1rem, 2.5vw, 1.5rem)", fontWeight: 600, color: text.primary, lineHeight: 1.35 }}>{receipt.trueNorth}</div>
          </div>

          <div style={{ marginBottom: "2rem", padding: "1rem 1.25rem", background: "rgba(13,17,23,0.6)", border: `0.5px solid ${signal.steel}33`, borderRadius: 6 }}>
            <div style={{ fontFamily: font.mono, fontSize: "0.6rem", letterSpacing: "0.12em", color: text.dimmed, textTransform: "uppercase", marginBottom: "0.4rem" }}>Decision</div>
            <div style={{ fontFamily: font.sans, fontSize: "0.9rem", color: text.secondary, lineHeight: 1.6 }}>{receipt.decision}</div>
          </div>

          {why.length > 0 && (
            <div style={{ marginBottom: "2rem" }}>
              <div style={{ fontFamily: font.mono, fontSize: "0.6rem", letterSpacing: "0.12em", color: text.dimmed, textTransform: "uppercase", marginBottom: "0.75rem" }}>Why This</div>
              <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
                {why.map((bullet, i) => (
                  <div key={i} style={{ display: "flex", gap: "0.75rem", alignItems: "flex-start" }}>
                    <span style={{ fontFamily: font.mono, fontSize: "0.7rem", color: signal.cyan, fontWeight: 700, flexShrink: 0, marginTop: "0.15rem" }}>{String(i + 1).padStart(2, "0")}</span>
                    <span style={{ fontFamily: font.sans, fontSize: "0.875rem", color: text.secondary, lineHeight: 1.6 }}>{bullet}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div style={{ display: "grid", gridTemplateColumns: "1fr auto", gap: "1.5rem", marginBottom: "2rem", alignItems: "start" }}>
            <div>
              {Object.keys(fated).length > 0 && <div style={{ marginBottom: "1.5rem" }}><FatedGrid fated={fated} /></div>}
              {paths.length > 0 && <TerrainPaths paths={paths as Parameters<typeof TerrainPaths>[0]["paths"]} />}
            </div>
            <ConvictionSidebar result={compassResult} />
          </div>

          <div style={{ borderTop: `0.5px solid ${signal.steel}22`, paddingTop: "1.25rem", display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
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
