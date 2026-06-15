// Canonical reflect surface for a brief.
// URL: /brief/reflect/[id]                   → all layers on
//      /brief/reflect/[id]/thoughts           → thoughts only
//      /brief/reflect/[id]/thoughts+comments  → composable
//
// Layer toggles update the URL via router.replace — each state is bookmarkable
// and shareable. Base brief (/brief/[id]) has a ◎ Reflect → pill that pushes here.
"use client"

import { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { track } from "@vercel/analytics"
import { surface, text, signal, font, getWeather, nciColor } from "@/ui/tokens"
import { Badge } from "@/ui/Badge"
import { Brief } from "@/organisms/Brief"
import { TributariesStack } from "@/molecules/TributariesStack"
import { SequenceLoader } from "@/molecules/SequenceLoader"
import { Card } from "@/ui/Card"
import { Label } from "@/ui/Label"
import { Button } from "@/ui/Button"
import { ReflectLayer, parseLayerSegment } from "@/organisms/ReflectLayer"
import type { CompassResult } from "@/lib/mockCompass"

function safeParse<T>(v: unknown, fallback: T): T {
  if (typeof v !== "string") return (v as T) ?? fallback
  try { return JSON.parse(v) as T } catch { return fallback }
}

function toCompassResult(receipt: Record<string, unknown>, tributaries: unknown[]): CompassResult {
  const raw = safeParse<Record<string, unknown>>(receipt.rawResponse, {})
  const rawReasoning = (raw.reasoning ?? {}) as Record<string, unknown>
  return {
    receipt_id: String(receipt.id ?? ""),
    question: String(receipt.decision ?? ""),
    true_north: String(receipt.trueNorth ?? ""),
    why: safeParse<string[]>(receipt.whyBullets, []),
    nci_score: Number(receipt.nciScore ?? 50),
    coherence_pct: (receipt.coherencePct as number) ?? undefined,
    is_satoshi: Boolean(receipt.isSatoshi),
    decision_mode: String(receipt.mode ?? ""),
    door_class: String(receipt.doorClass ?? "TWO_WAY"),
    y_state: String(receipt.yState ?? "GREEN"),
    render_resolution: String(receipt.renderResolution ?? "SHARP"),
    nci_delta: null,
    macro_tags: safeParse<string[]>(receipt.macroTags, []),
    tributaries: tributaries as CompassResult["tributaries"],
    reasoning: {
      fated: safeParse(receipt.fated, undefined),
      paths: safeParse(receipt.paths, undefined),
      court: safeParse(receipt.court, undefined),
      court_verdict: (receipt.courtVerdict as string) ?? undefined,
      advisors: (rawReasoning.advisors as CompassResult["reasoning"]["advisors"]) ?? undefined,
    },
  } as CompassResult
}

export default function BriefReflectPage() {
  const params = useParams()
  const router = useRouter()
  const receiptId = String(params.receiptId)
  // [[...layers]] comes in as string[] or undefined
  const layersParam = Array.isArray(params.layers) ? params.layers[0] : (params.layers as string | undefined)
  const defaultLayers = parseLayerSegment(layersParam)
  const layerUrlBase = `/brief/reflect/${receiptId}`

  const [result, setResult] = useState<CompassResult | null>(null)
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [depth, setDepth] = useState<number>(0)
  const [parentId, setParentId] = useState<string | null>(null)
  const [framing, setFraming] = useState<string>("")
  const [children, setChildren] = useState<Array<{ id: string; decision: string; trueNorth: string; yState: string; nciScore: number; version: number; createdAt: string }>>([])
  const [error, setError] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)
  const [authed, setAuthed] = useState<boolean | null>(null)

  useEffect(() => {
    let cancelled = false
    fetch(`/api/brief/${receiptId}`)
      .then(async (r) => ({ ok: r.ok, data: await r.json() }))
      .then(({ ok, data }) => {
        if (cancelled) return
        if (!ok) { setError(data.error ?? "Could not load brief"); return }
        setResult(toCompassResult(data.receipt, data.tributaries ?? []))
        setSessionId((data.receipt?.sessionId as string) ?? null)
        setDepth(Number(data.receipt?.version ?? 0))
        setParentId((data.receipt?.parentId as string) ?? null)
        setFraming(data.brief?.situationFraming ?? "")
        setChildren(data.children ?? [])
      })
      .catch(() => { if (!cancelled) setError("Could not load brief") })
    return () => { cancelled = true }
  }, [receiptId])

  useEffect(() => {
    let cancelled = false
    fetch("/api/auth/session")
      .then((r) => r.json())
      .then(async (s) => {
        if (cancelled) return
        const isAuthed = !!s?.user?.id
        setAuthed(isAuthed)
        if (isAuthed && typeof window !== "undefined") {
          const stored = localStorage.getItem("arcs_session_id")
          if (stored) {
            const r = await fetch("/api/receipts/claim", {
              method: "PATCH",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ sessionId: stored }),
            })
            if (r.ok) localStorage.removeItem("arcs_session_id")
          }
        }
      })
      .catch(() => { if (!cancelled) setAuthed(false) })
    return () => { cancelled = true }
  }, [])

  function followTributary(prompt: string) {
    track("brief_tributary_followed", { receiptId })
    const p = new URLSearchParams({ q: prompt, parent: receiptId })
    if (sessionId) p.set("sid", sessionId)
    router.push(`/dashboard?${p.toString()}`)
  }

  const briefUrl = () => `${window.location.origin}/brief/${receiptId}`

  async function copyLink() {
    await navigator.clipboard.writeText(window.location.href)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }
  function shareSms() {
    window.open(`sms:?body=${encodeURIComponent(`${result?.true_north}\n\nARCS Brief → ${briefUrl()}`)}`)
  }
  function shareX() {
    window.open(`https://x.com/intent/tweet?text=${encodeURIComponent((result?.true_north ?? "").slice(0, 220))}&url=${encodeURIComponent(briefUrl())}`)
  }

  if (error) {
    return (
      <main style={{ minHeight: "100vh", background: surface.bg, color: text.primary, display: "flex", alignItems: "center", justifyContent: "center" }}>
        <div style={{ fontFamily: font.sans, color: signal.red, fontSize: "0.9rem" }}>{error}</div>
      </main>
    )
  }
  if (!result) {
    return (
      <main style={{ minHeight: "100vh", background: "radial-gradient(120% 70% at 50% -5%, #0a1422 0%, #020408 62%)", color: text.primary, display: "flex", alignItems: "center", justifyContent: "center", padding: "2rem" }}>
        <SequenceLoader
          title="Rendering cartography brief…"
          stages={[{ name: "SURVEY" }, { name: "SITUATION FRAMING" }, { name: "ENTITY READ" }, { name: "TERRAIN PATHS" }, { name: "SILKSCREEN" }]}
          footer="Rendering through the fog…"
        />
      </main>
    )
  }

  return (
    <ReflectLayer
      receiptId={receiptId}
      surface="BRIEF"
      defaultHudOpen={true}
      defaultLayers={defaultLayers}
      layerUrlBase={layerUrlBase}
    >
      <main style={{ minHeight: "100vh", background: surface.bg, color: text.primary }}>
        {/* Reflect surface breadcrumb */}
        <div style={{ borderBottom: `0.5px solid rgba(0,240,255,0.12)`, background: "rgba(0,240,255,0.03)" }}>
          <div style={{ maxWidth: 880, margin: "0 auto", padding: "0.6rem 1.5rem", display: "flex", alignItems: "center", gap: "0.75rem" }}>
            <button onClick={() => router.push("/history")} style={{ background: "none", border: "none", cursor: "pointer", fontFamily: font.mono, fontSize: "0.6rem", letterSpacing: "0.1em", color: text.dimmed, textTransform: "uppercase", padding: 0 }}>Ledger</button>
            <span style={{ color: text.dimmed, fontFamily: font.mono, fontSize: "0.6rem" }}>·</span>
            <button onClick={() => router.push(`/brief/${receiptId}`)} style={{ background: "none", border: "none", cursor: "pointer", fontFamily: font.mono, fontSize: "0.6rem", letterSpacing: "0.1em", color: text.dimmed, textTransform: "uppercase", padding: 0 }}>Brief</button>
            <span style={{ color: signal.cyan, fontFamily: font.mono, fontSize: "0.6rem" }}>·</span>
            <span style={{ fontFamily: font.mono, fontSize: "0.6rem", letterSpacing: "0.1em", color: signal.cyan, textTransform: "uppercase" }}>◎ Reflect</span>
          </div>
        </div>

        {depth > 0 && (
          <div style={{ maxWidth: 880, margin: "0 auto", padding: "1.25rem 1.5rem 0", display: "flex", alignItems: "center", gap: "0.75rem", fontFamily: font.mono, fontSize: "0.7rem", letterSpacing: "0.1em", textTransform: "uppercase" }}>
            <span style={{ color: signal.cyan }}>Level {depth}</span>
            <span style={{ color: text.muted }}>·</span>
            {parentId ? (
              <button onClick={() => router.push(`/brief/reflect/${parentId}`)} style={{ background: "none", border: "none", padding: 0, cursor: "pointer", color: text.dimmed, fontFamily: font.mono, fontSize: "0.7rem", letterSpacing: "0.1em", textTransform: "uppercase" }}>
                ← Parent brief
              </button>
            ) : (
              <span style={{ color: text.dimmed }}>Reasoning chain</span>
            )}
          </div>
        )}

        <Brief result={result} onBack={() => router.push("/history")} onTributary={followTributary} />

        <div style={{ maxWidth: 880, margin: "0 auto", padding: "0 1.5rem 6rem" }}>
          {result.tributaries?.length > 0 && children.length === 0 && (
            <Card style={{ marginBottom: "1.5rem" }}>
              <TributariesStack tributaries={result.tributaries} onTributary={followTributary} />
            </Card>
          )}

          {children.length > 0 && (
            <Card style={{ marginBottom: "1.5rem" }}>
              <Label style={{ marginBottom: "0.75rem" }}>Tributary rounds · where this led</Label>
              <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
                {children.map((child) => {
                  const w = getWeather(child.yState)
                  const c = nciColor(child.nciScore)
                  return (
                    <div
                      key={child.id}
                      onClick={() => router.push(`/brief/reflect/${child.id}`)}
                      style={{ cursor: "pointer", padding: "0.75rem", borderRadius: 4, border: `1px solid ${signal.cyan}22`, background: "#0a1520" }}
                    >
                      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: "0.75rem", marginBottom: "0.35rem" }}>
                        <Badge label={`${w.icon} ${w.label}`} color={w.color} register="light" />
                        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                          <span style={{ fontFamily: font.mono, fontSize: "0.65rem", color: text.muted, letterSpacing: "0.08em" }}>L{child.version}</span>
                          <span style={{ fontFamily: font.mono, fontWeight: 700, fontSize: "0.85rem", color: c }}>{child.nciScore}</span>
                        </div>
                      </div>
                      <div style={{ fontFamily: font.sans, fontSize: "0.8rem", color: text.primary, lineHeight: 1.4, marginBottom: "0.25rem" }}>{child.decision}</div>
                      <div style={{ fontFamily: font.sans, fontSize: "0.75rem", color: text.secondary, lineHeight: 1.4 }}>
                        <span style={{ color: signal.cyan }}>True North · </span>{child.trueNorth}
                      </div>
                    </div>
                  )
                })}
              </div>
            </Card>
          )}

          {framing && (
            <Card style={{ marginBottom: "1.5rem" }}>
              <Label style={{ marginBottom: "0.75rem" }}>Situation Framing</Label>
              <p style={{ fontFamily: font.sans, fontSize: "0.9rem", color: text.secondary, lineHeight: 1.7, margin: 0, whiteSpace: "pre-wrap" }}>{framing}</p>
            </Card>
          )}

          <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", alignItems: "center" }}>
            <Label style={{ marginRight: "0.25rem" }}>Share</Label>
            {authed ? (
              <>
                <Button variant="ghost" size="sm" onClick={copyLink}>{copied ? "✓ Copied reflect link" : "Copy reflect link"}</Button>
                <Button variant="ghost" size="sm" onClick={shareSms}>SMS</Button>
                <Button variant="ghost" size="sm" onClick={shareX}>Post to X</Button>
              </>
            ) : (
              <Button variant="gold" size="sm" glyph="◈" onClick={() => router.push(`/compass?next=${encodeURIComponent(`/brief/reflect/${receiptId}`)}`)}>
                Sign in to share
              </Button>
            )}
          </div>
        </div>
      </main>
    </ReflectLayer>
  )
}
