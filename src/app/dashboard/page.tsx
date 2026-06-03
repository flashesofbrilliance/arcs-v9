"use client"

import { useState, useEffect, Suspense } from "react"
import { useRouter, useSearchParams } from "next/navigation"

// ─── Types ────────────────────────────────────────────────────────────────────

type Horizon = "TODAY" | "THIS_WEEK" | "THIS_QUARTER" | "ONE_TO_THREE_YEARS"
type Stakes  = "LOW" | "MEDIUM" | "HIGH"

interface CompassResult {
  ok: boolean
  receipt_id: string
  session_id: string
  session_version: number
  true_north: string
  why: string[]
  nci_score: number
  coherence_pct?: number
  is_satoshi?: boolean
  door_class: string
  decision_mode: string
  y_state: string
  y_conviction: string
  render_resolution: string
  nci_delta: number | null
  meta?: { macro_tags?: string[] }
  tributaries?: { type: "meta" | "challenge" | "adjacent"; label: string; prompt: string }[]
  reasoning?: {
    court?: { name: string; verdict: string; detail: string }[]
    court_verdict?: string
    advisors?: { loki_challenge: string; loki_counter: string; bayesian_risk_pct: number; bayesian_rationale: string }
    fated?: { facts: string; assumptions: string; tradeoffs: string; emotions: string; direction: string }
    paths?: { id: string; title: string; detail: string; tag: string; status: string }[]
  }
}

// ─── Constants ────────────────────────────────────────────────────────────────

const PROTECTION_CHIPS = ["Cash", "Time", "Reputation", "Relationship", "Health", "Optionality"]

const Y_WEATHER: Record<string, { label: string; icon: string; color: string }> = {
  GREEN:   { label: "CLARITY RIDGE",         icon: "▲", color: "#00FF9D" },
  YELLOW:  { label: "PRESSURE BAND",         icon: "◈", color: "#FFD700" },
  FORK:    { label: "FORK · PATH SELECTION", icon: "⊕", color: "#00F0FF" },
  SCRATCH: { label: "FOG LAYER · ORIENT",    icon: "~", color: "#475569" },
  DELTA:   { label: "CONVICTION SHIFT",      icon: "△", color: "#A78BFA" },
  PARADOX: { label: "PARADOX · CURATOR",     icon: "∞", color: "#E879F9" },
  LOCKED:  { label: "KAIROS LOCK · LOCKED",  icon: "◆", color: "#00F0FF" },
}

const RESOLUTION_STYLES: Record<string, { opacity: number; fontWeight: number; letterSpacing: string }> = {
  SHARP:    { opacity: 1.0,  fontWeight: 500, letterSpacing: "0" },
  DEGRADED: { opacity: 0.85, fontWeight: 400, letterSpacing: "0.01em" },
  GRAIN:    { opacity: 0.70, fontWeight: 300, letterSpacing: "0.02em" },
  MOIRE:    { opacity: 0.60, fontWeight: 300, letterSpacing: "0.03em" },
}

const HORIZON_LABELS: Record<Horizon, string> = {
  TODAY: "Today", THIS_WEEK: "This week",
  THIS_QUARTER: "This quarter", ONE_TO_THREE_YEARS: "1–3 years",
}
const STAKES_LABELS: Record<Stakes, string> = { LOW: "Low", MEDIUM: "Medium", HIGH: "High" }
const STAKES_COLOR: Record<Stakes, string> = { LOW: "#00FF9D", MEDIUM: "#FFD700", HIGH: "#FF4D6D" }

const NCI_COLOR = (s: number) => s >= 70 ? "#00FF9D" : s >= 45 ? "#FFD700" : "#FF4D6D"
const VERDICT_COLOR = (v: string) => v === "PASS" ? "#00FF9D" : v === "TENSION" ? "#FFD700" : "#FF4D6D"

// ─── Component ────────────────────────────────────────────────────────────────

function DashboardInner() {
  const router = useRouter()
  const searchParams = useSearchParams()

  // Compass state
  const [question,  setQuestion]  = useState(() => searchParams.get("q") ?? "")
  const [inboundPrepId] = useState(() => searchParams.get("prepId") ?? null)
  const [horizon,   setHorizon]   = useState<Horizon>("THIS_WEEK")
  const [stakes,    setStakes]    = useState<Stakes>("MEDIUM")
  const [loading,   setLoading]   = useState(false)
  const [result,    setResult]    = useState<CompassResult | null>(null)
  const [baseResult, setBaseResult] = useState<CompassResult | null>(null)
  const [error,     setError]     = useState<string | null>(null)
  const [showReasoning, setShowReasoning] = useState(false)

  // Session tracking — preserved across tributary follow-ups
  const [sessionId,       setSessionId]       = useState<string>("")
  const [parentReceiptId, setParentReceiptId] = useState<string | null>(null)
  const [tributaryMode,   setTributaryMode]   = useState(false) // true = follow-up run
  useEffect(() => { setSessionId(crypto.randomUUID()) }, [])

  // ADR-016: on mount, if user is authenticated, claim any pre-auth anonymous receipts
  useEffect(() => {
    if (typeof window === "undefined") return
    const storedSessionId = localStorage.getItem("arcs_session_id")
    if (!storedSessionId) return
    fetch("/api/auth/session")
      .then(r => r.json())
      .then(s => {
        if (!s?.user?.id) return
        return fetch("/api/receipts/claim", {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ sessionId: storedSessionId }),
        })
      })
      .then(r => { if (r?.ok) localStorage.removeItem("arcs_session_id") })
      .catch(() => { /* silent — claim is best-effort */ })
  }, [])

  // Prep state
  const [prepOpen,    setPrepOpen]    = useState(false)
  const [prepStakes,  setPrepStakes]  = useState<string>("")
  const [prepHorizon, setPrepHorizon] = useState<string>("")
  const [protecting,  setProtecting]  = useState<string[]>([])
  const [confidence,  setConfidence]  = useState(3)
  const [entity,      setEntity]      = useState("")
  const [adversarial, setAdversarial] = useState("")
  const [enriching,   setEnriching]   = useState(false)

  const resolution = result?.render_resolution ?? "SHARP"
  const resStyle   = RESOLUTION_STYLES[resolution] ?? RESOLUTION_STYLES.SHARP
  const weather    = result?.y_state ? (Y_WEATHER[result.y_state] ?? Y_WEATHER.GREEN) : null

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!question.trim()) return
    setLoading(true)
    setError(null)
    setResult(null)
    setBaseResult(null)
    setPrepOpen(false)
    setShowReasoning(false)

    try {
      const res = await fetch("/api/compass", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question, horizon, stakes,
          sessionId: tributaryMode ? sessionId : crypto.randomUUID(),
          prepId: inboundPrepId,
          parentReceiptId: tributaryMode ? parentReceiptId : null,
        }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.error ?? "Unknown error")
      setResult(data)
      setBaseResult(data)
      setSessionId(data.session_id)
      setParentReceiptId(data.receipt_id)
      setTributaryMode(false)
      // ADR-016: store session_id for pre-auth → post-auth receipt claim
      if (typeof window !== "undefined") {
        localStorage.setItem("arcs_session_id", data.session_id)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong")
    } finally {
      setLoading(false)
    }
  }

  async function handleEnrich() {
    if (!result) return
    setEnriching(true)
    setError(null)

    try {
      // Create prep session
      const prepRes = await fetch("/api/prep", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          stakes: prepStakes || null,
          horizon: prepHorizon || null,
          protecting,
          confidence,
          entity: entity || null,
          adversarialInput: adversarial || null,
        }),
      })
      const { prep_id } = await prepRes.json()

      // Re-run compass with enriched context
      const res = await fetch("/api/compass", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question,
          horizon: prepHorizon || horizon,
          stakes: prepStakes || stakes,
          sessionId: result.session_id,
          prepId: prep_id,
          parentReceiptId: result.receipt_id,
        }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.error ?? "Unknown error")
      setResult(data)
      setPrepOpen(false)
      setShowReasoning(false)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Enrichment failed")
    } finally {
      setEnriching(false)
    }
  }

  function toggleProtect(chip: string) {
    setProtecting(p => p.includes(chip) ? p.filter(c => c !== chip) : [...p, chip])
  }

  const s = { // shared inline style tokens
    bg:       "#020408",
    surface:  "#0d1117",
    border:   "#1e293b",
    text:     "#e2e8f0",
    muted:    "#475569",
    dimmed:   "#64748b",
    cyan:     "#00F0FF",
    green:    "#00FF9D",
    gold:     "#FFD700",
    red:      "#FF4D6D",
  }

  return (
    <main style={{ minHeight: "100vh", background: s.bg, color: s.text, fontFamily: "'Inter', sans-serif" }}>
      <div style={{ maxWidth: 740, margin: "0 auto", padding: "2.5rem 1.5rem" }}>

        {/* Header */}
        <div style={{ marginBottom: "2rem" }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "0.5rem" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
              <span style={{ fontSize: "0.65rem", letterSpacing: "0.15em", color: s.cyan, textTransform: "uppercase", fontWeight: 600 }}>ARCS FIELD OS</span>
              <span style={{ width: 1, height: 12, background: s.border }} />
              <span style={{ fontSize: "0.65rem", letterSpacing: "0.12em", color: s.muted, textTransform: "uppercase" }}>Question Compass</span>
            </div>
            <button
              type="button"
              onClick={() => router.push("/history")}
              style={{ background: "none", border: `1px solid ${s.border}`, color: s.muted, fontSize: "0.65rem", padding: "0.25rem 0.625rem", borderRadius: 5, cursor: "pointer", letterSpacing: "0.04em" }}
            >
              History
            </button>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
            <h1 style={{ fontSize: "1.375rem", fontWeight: 600, color: s.text, margin: 0 }}>
              What are you really trying to decide?
            </h1>
            {inboundPrepId && (
              <span style={{
                fontSize: "0.65rem", fontWeight: 700, letterSpacing: "0.1em",
                textTransform: "uppercase", color: s.green,
                padding: "0.2rem 0.6rem", borderRadius: 4,
                background: `${s.green}15`, border: `1px solid ${s.green}33`,
                whiteSpace: "nowrap",
              }}>
                ↑ Calibrated
              </span>
            )}
          </div>
        </div>

        {/* Form */}
        {!result && (
          <form onSubmit={handleSubmit} style={{ marginBottom: "2rem" }}>
            {/* Tributary thread indicator */}
            {tributaryMode && (
              <div style={{
                display: "flex", alignItems: "center", justifyContent: "space-between",
                padding: "0.4rem 0.75rem", marginBottom: "0.5rem",
                background: `${s.cyan}0d`, border: `1px solid ${s.cyan}33`, borderRadius: 6,
              }}>
                <span style={{ fontSize: "0.68rem", color: s.cyan, letterSpacing: "0.06em" }}>
                  ⊕ Follow-up thread — compass has context of your alpha question
                </span>
                <button
                  type="button"
                  onClick={() => { setTributaryMode(false); setParentReceiptId(null); setSessionId(crypto.randomUUID()) }}
                  style={{ background: "none", border: "none", color: s.muted, fontSize: "0.65rem", cursor: "pointer", padding: 0 }}
                >
                  Start fresh ×
                </button>
              </div>
            )}
            <textarea
              value={question}
              onChange={e => setQuestion(e.target.value)}
              placeholder="Describe the decision you're facing…"
              rows={4}
              style={{
                width: "100%", boxSizing: "border-box",
                background: s.surface, border: `1px solid ${s.border}`,
                borderRadius: 8, color: s.text, fontSize: "0.9375rem",
                padding: "0.875rem 1rem", resize: "vertical",
                outline: "none", lineHeight: 1.6,
                fontFamily: "inherit", marginBottom: "1rem",
              }}
            />
            <div style={{ display: "flex", gap: "0.75rem", marginBottom: "1rem", flexWrap: "wrap" }}>
              <div style={{ flex: 1, minWidth: 160 }}>
                <label style={{ display: "block", fontSize: "0.7rem", color: s.muted, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: "0.375rem" }}>Horizon</label>
                <select
                  value={horizon}
                  onChange={e => setHorizon(e.target.value as Horizon)}
                  style={{ width: "100%", background: s.surface, border: `1px solid ${s.border}`, borderRadius: 6, color: s.text, fontSize: "0.875rem", padding: "0.5rem 0.75rem" }}
                >
                  {(Object.keys(HORIZON_LABELS) as Horizon[]).map(h => (
                    <option key={h} value={h}>{HORIZON_LABELS[h]}</option>
                  ))}
                </select>
              </div>
              <div style={{ flex: 1, minWidth: 140 }}>
                <label style={{ display: "block", fontSize: "0.7rem", color: s.muted, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: "0.375rem" }}>Stakes</label>
                <div style={{ display: "flex", gap: "0.375rem" }}>
                  {(Object.keys(STAKES_LABELS) as Stakes[]).map(st => (
                    <button key={st} type="button" onClick={() => setStakes(st)} style={{
                      flex: 1, padding: "0.5rem 0", fontSize: "0.75rem", fontWeight: 600,
                      borderRadius: 6, border: "1px solid",
                      borderColor: stakes === st ? STAKES_COLOR[st] : s.border,
                      background: stakes === st ? "rgba(255,255,255,0.04)" : "transparent",
                      color: stakes === st ? STAKES_COLOR[st] : s.muted,
                      cursor: "pointer",
                    }}>{STAKES_LABELS[st]}</button>
                  ))}
                </div>
              </div>
            </div>
            <button type="submit" disabled={loading || !question.trim()} style={{
              width: "100%", padding: "0.75rem", borderRadius: 8,
              background: loading ? s.border : s.cyan,
              color: loading ? s.muted : s.bg,
              fontWeight: 700, fontSize: "0.875rem", border: "none",
              cursor: loading || !question.trim() ? "not-allowed" : "pointer",
              letterSpacing: "0.04em",
            }}>
              {loading ? "Running L0–L5 pipeline…" : "Get True North →"}
            </button>
          </form>
        )}

        {/* Error */}
        {error && (
          <div style={{ padding: "1rem", border: `1px solid ${s.red}33`, borderRadius: 8, background: `${s.red}0A`, color: s.red, fontSize: "0.875rem", marginBottom: "1.5rem" }}>
            {error}
          </div>
        )}

        {/* Result */}
        {result && (
          <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>

            {/* Terrain weather bar */}
            {weather && (
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "0.625rem 1rem", background: `${weather.color}10`, border: `1px solid ${weather.color}33`, borderRadius: 8 }}>
                <div style={{ display: "flex", alignItems: "center", gap: "0.625rem" }}>
                  <span style={{ color: weather.color, fontWeight: 700, fontSize: "0.875rem" }}>{weather.icon}</span>
                  <span style={{ fontSize: "0.65rem", letterSpacing: "0.12em", color: weather.color, textTransform: "uppercase", fontWeight: 600 }}>
                    {weather.label}
                  </span>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
                  {result.nci_delta !== null && (
                    <span style={{ fontSize: "0.75rem", fontWeight: 700, color: result.nci_delta >= 0 ? s.green : s.red }}>
                      {result.nci_delta >= 0 ? "+" : ""}{result.nci_delta} NCI
                    </span>
                  )}
                  <span style={{ fontSize: "0.65rem", color: s.muted, letterSpacing: "0.08em" }}>
                    {result.render_resolution}
                  </span>
                </div>
              </div>
            )}

            {/* True North */}
            <div style={{ padding: "1.25rem 1.5rem", background: s.surface, border: `1px solid ${s.cyan}33`, borderRadius: 10 }}>
              <div style={{ fontSize: "0.65rem", color: s.cyan, letterSpacing: "0.12em", textTransform: "uppercase", marginBottom: "0.75rem", fontWeight: 600 }}>
                True North · {result.decision_mode} · {result.door_class}
              </div>
              {/* True North always renders SHARP — it's the conclusion, earned regardless of NCI */}
              <p style={{ fontSize: "1.0625rem", lineHeight: 1.6, color: s.text, margin: 0, fontWeight: 500 }}>
                {result.true_north}
              </p>
              {result.why?.length > 0 && (
                <ul style={{
                  marginTop: "0.75rem", paddingLeft: "1.25rem", lineHeight: 1.7, margin: "0.75rem 0 0",
                  ...resStyle, color: "#94a3b8", fontSize: "0.875rem"
                }}>
                  {result.why.map((w, i) => <li key={i}>{w}</li>)}
                </ul>
              )}
            </div>

            {/* NCI + meta */}
            <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap" }}>
              <div style={{ flex: 1, minWidth: 120, padding: "1rem", background: s.surface, border: `1px solid ${s.border}`, borderRadius: 8 }}>
                <div style={{ fontSize: "0.65rem", color: s.muted, letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: "0.5rem" }}>NCI</div>
                <div style={{ fontSize: "2rem", fontWeight: 700, color: NCI_COLOR(result.nci_score), lineHeight: 1 }}>{result.nci_score}</div>
                <div style={{ fontSize: "0.7rem", color: s.muted, marginTop: "0.25rem" }}>/ 100</div>
              </div>
              {result.coherence_pct !== undefined && (
                <div style={{ flex: 1, minWidth: 120, padding: "1rem", background: s.surface, border: `1px solid ${s.border}`, borderRadius: 8 }}>
                  <div style={{ fontSize: "0.65rem", color: s.muted, letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: "0.5rem" }}>Coherence</div>
                  <div style={{ fontSize: "2rem", fontWeight: 700, color: "#94a3b8", lineHeight: 1 }}>{result.coherence_pct}<span style={{ fontSize: "1rem", color: s.muted }}>%</span></div>
                </div>
              )}
              {result.is_satoshi && (
                <div style={{ flex: 1, minWidth: 140, padding: "1rem", background: s.surface, border: `1px solid ${s.gold}33`, borderRadius: 8 }}>
                  <div style={{ fontSize: "0.65rem", color: s.gold, letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: "0.5rem" }}>Satoshi Move</div>
                  <div style={{ fontSize: "0.875rem", color: s.gold }}>Category-defining</div>
                </div>
              )}
              {result.meta?.macro_tags?.length ? (
                <div style={{ flex: 2, minWidth: 180, padding: "1rem", background: s.surface, border: `1px solid ${s.border}`, borderRadius: 8 }}>
                  <div style={{ fontSize: "0.65rem", color: s.muted, letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: "0.5rem" }}>Macro Tags</div>
                  <div style={{ display: "flex", gap: "0.375rem", flexWrap: "wrap" }}>
                    {result.meta.macro_tags.map(t => (
                      <span key={t} style={{ fontSize: "0.7rem", padding: "0.2rem 0.5rem", borderRadius: 4, background: s.border, color: "#94a3b8", fontWeight: 600 }}>{t}</span>
                    ))}
                  </div>
                </div>
              ) : null}
            </div>

            {/* Brief CTA */}
            <button
              onClick={() => router.push(`/brief/${result.receipt_id}`)}
              style={{
                width: "100%", padding: "0.75rem", borderRadius: 8,
                background: "transparent", border: `1px solid ${s.cyan}55`,
                color: s.cyan, fontWeight: 600, fontSize: "0.875rem",
                cursor: "pointer", letterSpacing: "0.04em",
              }}
            >
              Open Cartography Brief →
            </button>

            {/* ATG — Anticipatory Tributary Generator */}
            {result.tributaries && result.tributaries.length > 0 && (
              <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
                <div style={{ fontSize: "0.6rem", color: s.muted, letterSpacing: "0.12em", textTransform: "uppercase", paddingLeft: "0.25rem" }}>
                  Tributaries · Where to navigate next
                </div>
                {result.tributaries.map((t, i) => {
                  const tColor = t.type === "meta" ? s.cyan : t.type === "challenge" ? s.red : s.gold
                  return (
                    <button
                      key={i}
                      onClick={() => {
                        setQuestion(t.prompt)
                        setTributaryMode(true)  // carry session + parent into next run
                        setResult(null)
                        setBaseResult(null)
                        setPrepOpen(false)
                        setShowReasoning(false)
                        window.scrollTo({ top: 0, behavior: "smooth" })
                      }}
                      style={{
                        width: "100%", padding: "0.75rem 1rem", borderRadius: 8, textAlign: "left",
                        background: `${tColor}08`, border: `1px solid ${tColor}33`,
                        cursor: "pointer", display: "flex", flexDirection: "column", gap: "0.25rem",
                      }}
                    >
                      <span style={{ fontSize: "0.6rem", color: tColor, letterSpacing: "0.1em", textTransform: "uppercase", fontWeight: 600 }}>
                        {t.label}
                      </span>
                      <span style={{ fontSize: "0.8rem", color: "#94a3b8", lineHeight: 1.5 }}>{t.prompt}</span>
                    </button>
                  )
                })}
              </div>
            )}

            {/* Dial up resolution CTA */}
            {!prepOpen && result.y_state !== "GREEN" && (
              <button
                onClick={() => setPrepOpen(true)}
                style={{
                  width: "100%", padding: "0.625rem", borderRadius: 8,
                  background: "transparent", border: `1px solid ${s.gold}44`,
                  color: s.gold, fontSize: "0.8rem",
                  cursor: "pointer", letterSpacing: "0.04em",
                }}
              >
                ↑ Dial up resolution — 2 min calibration
              </button>
            )}

            {/* Prep form */}
            {prepOpen && (
              <div style={{ padding: "1.25rem", background: s.surface, border: `1px solid ${s.gold}33`, borderRadius: 10, display: "flex", flexDirection: "column", gap: "1.25rem" }}>
                <div style={{ fontSize: "0.65rem", color: s.gold, letterSpacing: "0.12em", textTransform: "uppercase", fontWeight: 600 }}>
                  ↑ Calibration · Forensic Diagnostic
                </div>

                {/* Stakes */}
                <div>
                  <label style={{ display: "block", fontSize: "0.7rem", color: s.muted, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: "0.5rem" }}>How bad if this goes wrong?</label>
                  <div style={{ display: "flex", gap: "0.375rem" }}>
                    {(["LOW", "MEDIUM", "HIGH"] as Stakes[]).map(st => (
                      <button key={st} type="button" onClick={() => setPrepStakes(prepStakes === st ? "" : st)} style={{
                        flex: 1, padding: "0.5rem 0", fontSize: "0.75rem", fontWeight: 600, borderRadius: 6, border: "1px solid",
                        borderColor: prepStakes === st ? STAKES_COLOR[st] : s.border,
                        background: prepStakes === st ? "rgba(255,255,255,0.04)" : "transparent",
                        color: prepStakes === st ? STAKES_COLOR[st] : s.muted, cursor: "pointer",
                      }}>{STAKES_LABELS[st]}</button>
                    ))}
                  </div>
                </div>

                {/* Horizon */}
                <div>
                  <label style={{ display: "block", fontSize: "0.7rem", color: s.muted, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: "0.5rem" }}>When does this matter?</label>
                  <div style={{ display: "flex", gap: "0.375rem", flexWrap: "wrap" }}>
                    {(Object.keys(HORIZON_LABELS) as Horizon[]).map(h => (
                      <button key={h} type="button" onClick={() => setPrepHorizon(prepHorizon === h ? "" : h)} style={{
                        padding: "0.375rem 0.75rem", fontSize: "0.75rem", borderRadius: 6, border: "1px solid",
                        borderColor: prepHorizon === h ? s.cyan : s.border,
                        background: prepHorizon === h ? `${s.cyan}15` : "transparent",
                        color: prepHorizon === h ? s.cyan : s.muted, cursor: "pointer",
                      }}>{HORIZON_LABELS[h]}</button>
                    ))}
                  </div>
                </div>

                {/* Protecting chips */}
                <div>
                  <label style={{ display: "block", fontSize: "0.7rem", color: s.muted, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: "0.5rem" }}>What can&apos;t you afford to lose? (pick up to 2)</label>
                  <div style={{ display: "flex", gap: "0.375rem", flexWrap: "wrap" }}>
                    {PROTECTION_CHIPS.map(chip => {
                      const active = protecting.includes(chip)
                      const maxed = protecting.length >= 2 && !active
                      return (
                        <button key={chip} type="button" disabled={maxed} onClick={() => toggleProtect(chip)} style={{
                          padding: "0.375rem 0.75rem", fontSize: "0.75rem", borderRadius: 6, border: "1px solid",
                          borderColor: active ? s.green : s.border,
                          background: active ? `${s.green}15` : "transparent",
                          color: active ? s.green : maxed ? s.border : s.muted,
                          cursor: maxed ? "not-allowed" : "pointer",
                        }}>{chip}</button>
                      )
                    })}
                  </div>
                </div>

                {/* Confidence slider */}
                <div>
                  <label style={{ display: "block", fontSize: "0.7rem", color: s.muted, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: "0.5rem" }}>
                    How sure were you before you asked? &nbsp;<span style={{ color: s.text, fontWeight: 600 }}>{confidence}/5</span>
                  </label>
                  <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
                    <span style={{ fontSize: "0.65rem", color: s.muted }}>Lost</span>
                    <input type="range" min={1} max={5} value={confidence} onChange={e => setConfidence(Number(e.target.value))}
                      style={{ flex: 1, accentColor: s.cyan }} />
                    <span style={{ fontSize: "0.65rem", color: s.muted }}>Confirming</span>
                  </div>
                </div>

                {/* Entity */}
                <div>
                  <label style={{ display: "block", fontSize: "0.7rem", color: s.muted, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: "0.375rem" }}>Who else is in this? (optional)</label>
                  <input value={entity} onChange={e => setEntity(e.target.value)} placeholder="person, company, stakeholder…"
                    style={{ width: "100%", boxSizing: "border-box", background: s.bg, border: `1px solid ${s.border}`, borderRadius: 6, color: s.text, fontSize: "0.875rem", padding: "0.5rem 0.75rem", outline: "none", fontFamily: "inherit" }} />
                </div>

                {/* Adversarial */}
                <div>
                  <label style={{ display: "block", fontSize: "0.7rem", color: s.muted, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: "0.375rem" }}>Strongest case against your instinct</label>
                  <input value={adversarial} onChange={e => setAdversarial(e.target.value)} placeholder="One sentence. The Loki vector."
                    style={{ width: "100%", boxSizing: "border-box", background: s.bg, border: `1px solid ${s.border}`, borderRadius: 6, color: s.text, fontSize: "0.875rem", padding: "0.5rem 0.75rem", outline: "none", fontFamily: "inherit" }} />
                </div>

                <div style={{ display: "flex", gap: "0.75rem" }}>
                  <button onClick={handleEnrich} disabled={enriching} style={{
                    flex: 1, padding: "0.625rem", borderRadius: 8,
                    background: enriching ? s.border : s.gold,
                    color: enriching ? s.muted : s.bg,
                    fontWeight: 700, fontSize: "0.8rem", border: "none",
                    cursor: enriching ? "not-allowed" : "pointer",
                  }}>
                    {enriching ? "Re-running…" : "Re-run with calibration →"}
                  </button>
                  <button onClick={() => setPrepOpen(false)} style={{
                    padding: "0.625rem 1rem", borderRadius: 8, background: "transparent",
                    border: `1px solid ${s.border}`, color: s.muted, fontSize: "0.8rem", cursor: "pointer",
                  }}>Cancel</button>
                </div>
              </div>
            )}

            {/* Deep reasoning */}
            {result.reasoning && (
              <>
                <button onClick={() => setShowReasoning(v => !v)} style={{
                  background: "transparent", border: `1px solid ${s.border}`, borderRadius: 8,
                  color: s.muted, fontSize: "0.8rem", padding: "0.625rem 1rem", cursor: "pointer", textAlign: "left",
                }}>
                  {showReasoning ? "▲ Hide reasoning" : "▼ Show full reasoning (L0–L5)"}
                </button>

                {showReasoning && (
                  <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem", ...resStyle }}>

                    {result.reasoning.court?.length ? (
                      <div style={{ padding: "1rem 1.25rem", background: s.surface, border: `1px solid ${s.border}`, borderRadius: 8 }}>
                        <div style={{ fontSize: "0.65rem", color: s.muted, letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: "0.75rem" }}>Constitutional Court</div>
                        {result.reasoning.court.map((c, i) => (
                          <div key={i} style={{ display: "flex", gap: "0.75rem", marginBottom: "0.5rem", fontSize: "0.8rem" }}>
                            <span style={{ color: VERDICT_COLOR(c.verdict), fontWeight: 700, minWidth: 56 }}>{c.verdict}</span>
                            <span style={{ color: "#94a3b8" }}><strong style={{ color: s.text }}>{c.name}</strong> — {c.detail}</span>
                          </div>
                        ))}
                        {result.reasoning.court_verdict && (
                          <div style={{ marginTop: "0.75rem", paddingTop: "0.75rem", borderTop: `1px solid ${s.border}`, fontSize: "0.8rem", color: s.dimmed, fontStyle: "italic" }}>
                            {result.reasoning.court_verdict}
                          </div>
                        )}
                      </div>
                    ) : null}

                    {result.reasoning.fated && (
                      <div style={{ padding: "1rem 1.25rem", background: s.surface, border: `1px solid ${s.border}`, borderRadius: 8 }}>
                        <div style={{ fontSize: "0.65rem", color: s.muted, letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: "0.75rem" }}>FATED Decomposition</div>
                        {Object.entries(result.reasoning.fated).map(([k, v]) => (
                          <div key={k} style={{ marginBottom: "0.5rem", fontSize: "0.8rem" }}>
                            <span style={{ color: s.dimmed, textTransform: "uppercase", fontSize: "0.65rem", letterSpacing: "0.08em" }}>{k} </span>
                            <span style={{ color: "#94a3b8" }}>{v}</span>
                          </div>
                        ))}
                      </div>
                    )}

                    {result.reasoning.paths?.length ? (
                      <div style={{ padding: "1rem 1.25rem", background: s.surface, border: `1px solid ${s.border}`, borderRadius: 8 }}>
                        <div style={{ fontSize: "0.65rem", color: s.muted, letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: "0.75rem" }}>Paths</div>
                        {result.reasoning.paths.map(p => (
                          <div key={p.id} style={{ marginBottom: "0.75rem", paddingLeft: "0.75rem", borderLeft: `2px solid ${p.status === "selected" ? s.cyan : p.status === "blocked" ? `${s.red}33` : s.border}` }}>
                            <div style={{ fontSize: "0.8rem", fontWeight: 600, color: p.status === "selected" ? s.text : s.muted }}>{p.title} <span style={{ fontWeight: 400, fontSize: "0.7rem", color: s.dimmed }}>({p.tag})</span></div>
                            <div style={{ fontSize: "0.78rem", color: s.dimmed, marginTop: "0.2rem" }}>{p.detail}</div>
                          </div>
                        ))}
                      </div>
                    ) : null}

                    {result.reasoning.advisors && (
                      <div style={{ padding: "1rem 1.25rem", background: s.surface, border: `1px solid ${s.border}`, borderRadius: 8 }}>
                        <div style={{ fontSize: "0.65rem", color: s.muted, letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: "0.75rem" }}>Advisors</div>
                        <div style={{ fontSize: "0.8rem", color: "#94a3b8", marginBottom: "0.5rem" }}>
                          <span style={{ color: s.red, fontWeight: 600 }}>Loki: </span>{result.reasoning.advisors.loki_challenge}
                        </div>
                        <div style={{ fontSize: "0.8rem", color: "#94a3b8", marginBottom: "0.5rem" }}>
                          <span style={{ color: s.green, fontWeight: 600 }}>Counter: </span>{result.reasoning.advisors.loki_counter}
                        </div>
                        <div style={{ fontSize: "0.8rem", color: "#94a3b8" }}>
                          <span style={{ color: s.dimmed }}>Bayesian risk: </span>
                          <span style={{ color: s.gold, fontWeight: 600 }}>{result.reasoning.advisors.bayesian_risk_pct}%</span>
                          {" — "}{result.reasoning.advisors.bayesian_rationale}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </>
            )}

            {/* Reset */}
            <button onClick={() => { setResult(null); setBaseResult(null); setQuestion(""); setPrepOpen(false); setShowReasoning(false) }}
              style={{ background: "transparent", border: "none", color: s.muted, fontSize: "0.8rem", cursor: "pointer", padding: "0.25rem 0", textAlign: "left" }}>
              ← New question
            </button>
          </div>
        )}
      </div>
    </main>
  )
}

export default function DashboardPage() {
  return (
    <Suspense>
      <DashboardInner />
    </Suspense>
  )
}
