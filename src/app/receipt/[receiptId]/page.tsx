"use client"

import { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { surface, text, signal, font, getWeather, nciColor, contentContainer } from "@/ui/tokens"
import { useVw } from "@/ui/useVw"
import { Wordmark } from "@/ui/Wordmark"
import { Rule } from "@/ui/Rule"
import { Button } from "@/ui/Button"
import { FatedGrid } from "@/molecules/FatedGrid"
import { TerrainPaths } from "@/molecules/TerrainPaths"
import { ConvictionSidebar } from "@/molecules/ConvictionSidebar"
import { SequenceLoader } from "@/molecules/SequenceLoader"
import { ReflectLayer } from "@/organisms/ReflectLayer"
import type { CompassResult } from "@/lib/mockCompass"

function safeParse<T>(v: unknown, fallback: T): T {
  if (typeof v !== "string") return (v as T) ?? fallback
  try { return JSON.parse(v) as T } catch { return fallback }
}

interface ReceiptData {
  id: string
  decision: string
  trueNorth: string
  whyBullets: string
  nciScore: number
  coherencePct?: number
  mode: string
  doorClass: string
  yState: string
  fated: string
  paths: string
  macroTags: string
  stakesLevel?: string
  horizon?: string
  version: number
  createdAt: string
  courtVerdict?: string
  sessionId: string
}

export default function ReceiptPage() {
  const params = useParams()
  const router = useRouter()
  const receiptId = String(params.receiptId)
  const vw = useVw()

  // Ephemeral anonymous bearing: never persisted server-side (trust contract
  // — "anonymous sessions: nothing is stored"). The dashboard stashed the
  // compass response in sessionStorage under this minted `eph_` id.
  const isEphemeral = receiptId.startsWith("eph_")

  const [receipt, setReceipt] = useState<ReceiptData | null>(null)
  const [hasBrief, setHasBrief] = useState(false)
  const [error, setError] = useState<string | null>(null)
  // /api/brief/[receiptId] already recovers tributaries from the receipt's
  // stored rawResponse (see that route) — just wasn't read here before.
  const [tributaries, setTributaries] = useState<CompassResult["tributaries"]>([])

  useEffect(() => {
    if (isEphemeral) {
      const raw = sessionStorage.getItem(`arcs_eph_${receiptId}`)
      if (!raw) {
        setError("This bearing wasn't stored — anonymous results live only in the browser tab that ran them. Run the compass again, or sign in first to keep receipts.")
        return
      }
      try {
        const d = JSON.parse(raw)
        setReceipt({
          id: receiptId,
          decision: d.question ?? "",
          trueNorth: d.true_north ?? "",
          whyBullets: JSON.stringify(d.why ?? []),
          nciScore: Number(d.nci_score ?? 0),
          coherencePct: typeof d.coherence_pct === "number" ? d.coherence_pct : undefined,
          mode: d.decision_mode ?? "",
          doorClass: d.door_class ?? "",
          yState: d.y_state ?? "",
          fated: JSON.stringify(d.reasoning?.fated ?? {}),
          paths: JSON.stringify(d.reasoning?.paths ?? []),
          macroTags: JSON.stringify(d.meta?.macro_tags ?? []),
          version: 0,
          createdAt: new Date().toISOString(),
          courtVerdict: typeof d.reasoning?.court_verdict === "string" ? d.reasoning.court_verdict : undefined,
          sessionId: d.session_id ?? "",
        })
        setTributaries(Array.isArray(d.tributaries) ? d.tributaries : [])
        setHasBrief(false)
      } catch {
        setError("Could not read this browser-local bearing.")
      }
      return
    }
    let cancelled = false
    fetch(`/api/brief/${receiptId}`)
      .then(async (r) => ({ ok: r.ok, data: await r.json() }))
      .then(({ ok, data }) => {
        if (cancelled) return
        if (!ok) { setError(data.error ?? "Could not load receipt"); return }
        setReceipt(data.receipt as ReceiptData)
        setHasBrief(!!data.brief)
        setTributaries(Array.isArray(data.tributaries) ? data.tributaries : [])
      })
      .catch(() => { if (!cancelled) setError("Could not load receipt") })
    return () => { cancelled = true }
  }, [receiptId, isEphemeral])

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
        <SequenceLoader
          title="Loading receipt…"
          stages={[{ name: "FETCH" }, { name: "RENDER" }]}
          footer="Loading decision receipt…"
        />
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
    receipt_id: receipt.id,
    question: receipt.decision,
    true_north: receipt.trueNorth,
    why,
    nci_score: receipt.nciScore,
    coherence_pct: receipt.coherencePct,
    is_satoshi: false,
    decision_mode: receipt.mode,
    door_class: receipt.doorClass,
    y_state: receipt.yState,
    render_resolution: "SHARP",
    nci_delta: null,
    macro_tags: macroTags,
    tributaries: tributaries ?? [],
    reasoning: {
      fated: fated as unknown as CompassResult["reasoning"]["fated"],
      paths: paths as unknown as CompassResult["reasoning"]["paths"],
      court_verdict: receipt.courtVerdict,
    },
  }

  const page = (
      <main style={{ minHeight: "100vh", background: surface.bg, color: text.primary }}>
        {/* Header — Wordmark + Rule, matching home/history/brief pattern */}
        <div style={{ ...contentContainer(vw), paddingTop: "2rem", paddingBottom: "1rem", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <Wordmark section="Decision Receipt" />
          <div style={{ display: "flex", alignItems: "center", gap: "0.25rem" }}>
            {isEphemeral
              ? <Button variant="ghost" size="sm" onClick={() => router.push("/dashboard")}>← Compass</Button>
              : <Button variant="ghost" size="sm" onClick={() => router.push("/history")}>← Ledger</Button>}
            {hasBrief && <Button variant="ghost" size="sm" onClick={() => router.push(`/brief/${receiptId}`)}>Brief →</Button>}
          </div>
        </div>
        <div style={{ ...contentContainer(vw), paddingBottom: "1.5rem" }}>
          <Rule />
        </div>

        {/* Ephemeral notice — the trust contract's "nothing is stored" made visible */}
        {isEphemeral && (
          <div style={{ ...contentContainer(vw), paddingBottom: "1.25rem" }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 12, flexWrap: "wrap", border: `0.5px solid ${signal.gold}44`, borderRadius: 6, padding: "0.6rem 1rem", background: `${signal.gold}0d` }}>
              <span style={{ fontFamily: font.mono, fontSize: "0.65rem", letterSpacing: "0.08em", color: text.secondary }}>
                NOT STORED — this bearing lives only in this browser tab, per the trust contract. Save it to your ledger by signing in.
              </span>
              <Button variant="ghost" size="sm" onClick={() => {
                // Opt-in save (ADR-032): stash the bearing in localStorage
                // (sessionStorage is tab-scoped — a magic-link click opens a
                // new tab and would lose it), then route to sign-in. The
                // post-auth consumer (ClaimAnonymousReceipts) persists it.
                const raw = sessionStorage.getItem(`arcs_eph_${receiptId}`)
                if (raw) {
                  try { localStorage.setItem("arcs_pending_save", JSON.stringify({ savedAt: Date.now(), bearing: JSON.parse(raw) })) } catch {}
                }
                router.push("/compass")
              }}>Sign in &amp; save</Button>
            </div>
          </div>
        )}

        {/* Body */}
        <div style={{ ...contentContainer(vw), paddingTop: "1rem", paddingBottom: "6rem" }}>
          {/* Decision — the question, at the top */}
          <div style={{ marginBottom: "2rem", padding: "1rem 1.25rem", background: "rgba(13,17,23,0.6)", border: `0.5px solid ${signal.steel}33`, borderRadius: 6 }}>
            <div style={{ fontFamily: font.mono, fontSize: "0.6rem", letterSpacing: "0.12em", color: text.dimmed, textTransform: "uppercase", marginBottom: "0.4rem" }}>Decision</div>
            <div style={{ fontFamily: font.sans, fontSize: "0.9rem", color: text.secondary, lineHeight: 1.6 }}>{receipt.decision}</div>
          </div>

          {/* True North */}
          <div style={{ marginBottom: "2rem" }}>
            <div style={{ fontFamily: font.mono, fontSize: "0.6rem", letterSpacing: "0.14em", color: signal.cyan, textTransform: "uppercase", marginBottom: "0.5rem" }}>True North</div>
            <div style={{ fontFamily: font.sans, fontSize: "clamp(1.1rem, 2.5vw, 1.5rem)", fontWeight: 600, color: text.primary, lineHeight: 1.35 }}>
              {receipt.trueNorth}
            </div>
          </div>

          {/* Conviction — directly below True North */}
          <div style={{ marginBottom: "2rem" }}>
            <ConvictionSidebar
              result={compassResult}
              onTributary={(prompt) => {
                // Ephemeral bearings have no persisted row — omit `parent` so
                // the follow-up doesn't reference a nonexistent receipt id.
                const params = new URLSearchParams({ q: prompt })
                if (!isEphemeral) params.set("parent", receipt.id)
                if (receipt.sessionId) params.set("sid", receipt.sessionId)
                router.push(`/dashboard?${params.toString()}`)
              }}
            />
          </div>

          {/* Why bullets */}
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

          {/* FATED · Terrain Paths — single-column stack (Conviction lifted to top) */}
          <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem", marginBottom: "2rem" }}>
            {fated && Object.keys(fated).length > 0 && <FatedGrid fated={fated} />}
            {paths && paths.length > 0 && (
              <TerrainPaths paths={paths as Parameters<typeof TerrainPaths>[0]["paths"]} />
            )}
          </div>

          {/* Schema ledger pills */}
          <div style={{ borderTop: `0.5px solid ${signal.steel}22`, paddingTop: "1.25rem", display: "flex", flexWrap: "wrap", gap: "0.5rem", alignItems: "center" }}>
            <Pill label="MODE" value={receipt.mode} color={signal.gold} />
            <Pill label="DOOR" value={receipt.doorClass?.replace(/_/g, " ")} color={signal.steel} />
            {receipt.stakesLevel && <Pill label="STAKES" value={receipt.stakesLevel} color={signal.red} />}
            {receipt.horizon && <Pill label="HORIZON" value={receipt.horizon} color={text.muted} />}
            <Pill label="NCI" value={String(receipt.nciScore)} color={nc} />
            {receipt.coherencePct != null && <Pill label="COHERENCE" value={`${receipt.coherencePct}%`} color={signal.green} />}
            {macroTags.map((tag) => <Pill key={tag} label="MACRO" value={tag} color={text.dimmed} />)}
            <Pill label="Y" value={`${w.icon} ${w.label}`} color={w.color} />
            <Pill label="L" value={`${receipt.version}`} color={text.dimmed} />
            <Pill label="DATE" value={new Date(receipt.createdAt).toLocaleDateString()} color={text.dimmed} />
          </div>
        </div>
      </main>
  )

  // ReflectLayer's endpoints operate on persisted receipts — ephemeral
  // bearings render bare (nothing server-side to reflect against).
  return isEphemeral ? page : (
    <ReflectLayer receiptId={receiptId} surface="RECEIPT" reflectUrl={`/receipt/reflect/${receiptId}`}>
      {page}
    </ReflectLayer>
  )
}

function Pill({ label, value, color }: { label: string; value: string; color: string }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: "0", border: `0.5px solid ${color}44`, borderRadius: 3, overflow: "hidden", fontSize: "0.6rem", fontFamily: "font-mono" }}>
      <span style={{ background: `${color}18`, padding: "0.2rem 0.4rem", color, fontFamily: "monospace", letterSpacing: "0.08em", textTransform: "uppercase" }}>{label}</span>
      <span style={{ padding: "0.2rem 0.5rem", color: "rgb(226,232,240)", fontFamily: "monospace", background: "rgba(13,17,23,0.5)" }}>{value}</span>
    </div>
  )
}
