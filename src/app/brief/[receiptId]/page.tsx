// Render through the fog to earned clarity.
"use client"

import { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"

// ─── Share helpers ─────────────────────────────────────────────────────────────

function briefUrl(receiptId: string) {
  return `${window.location.origin}/brief/${receiptId}`
}

function shareViaSMS(receiptId: string, trueNorth: string) {
  const url = briefUrl(receiptId)
  const body = `${trueNorth}\n\nARCS Cartography Brief → ${url}`
  window.open(`sms:?body=${encodeURIComponent(body)}`)
}

function shareViaX(receiptId: string, trueNorth: string) {
  const url = briefUrl(receiptId)
  const text = `${trueNorth.slice(0, 220)}\n\n`
  window.open(`https://x.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(url)}`)
}

async function copyLink(receiptId: string, setCopied: (v: boolean) => void) {
  await navigator.clipboard.writeText(briefUrl(receiptId))
  setCopied(true)
  setTimeout(() => setCopied(false), 2000)
}

// ─── Types ────────────────────────────────────────────────────────────────────

interface Brief {
  id: string
  receiptId: string
  situationFraming: string
  createdAt: string
}

interface Receipt {
  id: string
  decision: string
  trueNorth: string
  whyBullets: string
  nciScore: number
  coherencePct: number | null
  isSatoshi: boolean
  mode: string
  doorClass: string
  yState: string
  yConviction: string
  yStability: string
  renderResolution: string
  gradientMagnitude: number | null
  gradientDirection: string | null
  flowTopology: string | null
  manifoldCurvature: string | null
  entity: string | null
  window: string
  stakes: string
  protecting: string
  fated: string | null
  paths: string | null
  court: string | null
  courtVerdict: string | null
  macroTags: string
  nciScore_parent?: number | null
  createdAt: string
}

interface Tributary {
  type: "meta" | "challenge" | "adjacent"
  label: string
  prompt: string
}

interface EntityAnalysis {
  role: string
  leverage_theirs: string
  leverage_yours: string
  alignment: "ALIGNED" | "NEUTRAL" | "MISALIGNED" | "ADVERSARIAL"
  alignment_read: string
  signal_to_watch: string
  risk_surface: string
}

interface BriefResponse {
  ok: boolean
  brief: Brief
  receipt: Receipt
  tributaries?: Tributary[]
  entityAnalysis?: EntityAnalysis | null
}

// ─── Constants ────────────────────────────────────────────────────────────────

const Y_WEATHER: Record<string, { label: string; icon: string; color: string }> = {
  GREEN:   { label: "CLARITY RIDGE",          icon: "▲", color: "#00FF9D" },
  YELLOW:  { label: "PRESSURE BAND",          icon: "◈", color: "#FFD700" },
  RED:     { label: "CLIFF EDGE · COURT",     icon: "✕", color: "#FF4D6D" },
  FORK:    { label: "FORK · PATH SELECTION",  icon: "⊕", color: "#00F0FF" },
  SCRATCH: { label: "FOG LAYER · ORIENT",     icon: "~", color: "#475569" },
  DELTA:   { label: "CONVICTION SHIFT",       icon: "△", color: "#A78BFA" },
  DRIFT:   { label: "DRIFT · LAND THE PLANE", icon: "⟳", color: "#FB923C" },
  PARADOX: { label: "PARADOX · CURATOR",      icon: "∞", color: "#E879F9" },
}

const RESOLUTION_STYLES: Record<string, { opacity: number; fontWeight: number; letterSpacing: string }> = {
  SHARP:    { opacity: 1.0,  fontWeight: 500, letterSpacing: "0" },
  DEGRADED: { opacity: 0.85, fontWeight: 400, letterSpacing: "0.01em" },
  GRAIN:    { opacity: 0.70, fontWeight: 300, letterSpacing: "0.02em" },
  MOIRE:    { opacity: 0.60, fontWeight: 300, letterSpacing: "0.03em" },
}

const NCI_COLOR = (s: number) => s >= 70 ? "#00FF9D" : s >= 45 ? "#FFD700" : "#FF4D6D"
const VERDICT_COLOR = (v: string) => v === "PASS" ? "#00FF9D" : v === "TENSION" ? "#FFD700" : "#FF4D6D"
const ALIGNMENT_COLOR: Record<string, string> = {
  ALIGNED: "#00FF9D", NEUTRAL: "#64748b", MISALIGNED: "#FFD700", ADVERSARIAL: "#FF4D6D",
}

const FATED_LABELS: Record<string, string> = {
  facts: "Facts",
  assumptions: "Assumptions",
  tradeoffs: "Tradeoffs",
  emotions: "Emotions",
  direction: "Direction",
}

const HORIZON_LABELS: Record<string, string> = {
  TODAY: "Today",
  THIS_WEEK: "This week",
  THIS_QUARTER: "This quarter",
  ONE_TO_THREE_YEARS: "1–3 years",
}

const CONVICTION_LABELS: Record<string, string> = {
  HIGH:       "Strong — clear lean",
  CONTESTED:  "Split — could go either way",
  LOW:        "Weak — no real lean yet",
  EPHEMERAL:  "Fading — conviction is slipping",
  COLLAPSED:  "Gone — back to zero",
}

const STABILITY_LABELS: Record<string, string> = {
  LOCKED:    "Holding steady",
  DRIFTING:  "Slowly shifting",
  VOLATILE:  "Unstable — changing fast",
}

const MODE_LABELS: Record<string, string> = {
  COURT:      "Full deliberation",
  PLAN:       "Structured plan",
  QUICKMOVE:  "Quick move",
}

const DOOR_LABELS: Record<string, { label: string; color: string }> = {
  ONE_WAY: { label: "Hard to undo",        color: "#FF4D6D" },
  TWO_WAY: { label: "Can course-correct",  color: "#00FF9D" },
}

// ─── Skeleton ─────────────────────────────────────────────────────────────────

function SkeletonBlock({ height, width = "100%" }: { height: number; width?: string }) {
  return (
    <div style={{
      height, width, borderRadius: 6,
      background: "linear-gradient(90deg, #0d1117 25%, #1e293b 50%, #0d1117 75%)",
      backgroundSize: "200% 100%",
      animation: "shimmer 1.6s infinite",
    }} />
  )
}

// ─── Component ────────────────────────────────────────────────────────────────

export default function BriefPage() {
  const { receiptId } = useParams<{ receiptId: string }>()
  const router = useRouter()

  const [data, setData] = useState<BriefResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [generating, setGenerating] = useState(true)
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    if (!receiptId) return
    let cancelled = false

    async function load() {
      setGenerating(true)
      try {
        const res = await fetch(`/api/brief/${receiptId}`)
        const json = await res.json()
        if (!cancelled) {
          if (!res.ok) setError(json.error ?? "Failed to load brief")
          else setData(json)
        }
      } catch (err) {
        if (!cancelled) setError(err instanceof Error ? err.message : "Unknown error")
      } finally {
        if (!cancelled) setGenerating(false)
      }
    }

    load()
    return () => { cancelled = true }
  }, [receiptId])

  const s = {
    bg:      "#020408",
    surface: "#0d1117",
    border:  "#1e293b",
    text:    "#e2e8f0",
    muted:   "#475569",
    dimmed:  "#64748b",
    cyan:    "#00F0FF",
    green:   "#00FF9D",
    gold:    "#FFD700",
    red:     "#FF4D6D",
  }

  // ─── Loading skeleton ──────────────────────────────────────────────────────
  if (generating) {
    return (
      <main style={{ minHeight: "100vh", background: s.bg, color: s.text, fontFamily: "'Inter', sans-serif" }}>
        <style>{`@keyframes shimmer { 0%{background-position:200% 0} 100%{background-position:-200% 0} }`}</style>
        <div style={{ maxWidth: 1000, margin: "0 auto", padding: "2.5rem 1.5rem" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", marginBottom: "2rem" }}>
            <span style={{ fontSize: "0.65rem", letterSpacing: "0.15em", color: s.cyan, textTransform: "uppercase", fontWeight: 600 }}>ARCS FIELD OS</span>
            <span style={{ width: 1, height: 12, background: s.border }} />
            <span style={{ fontSize: "0.65rem", letterSpacing: "0.12em", color: s.muted, textTransform: "uppercase" }}>Cartography Brief · Generating</span>
          </div>
          <div style={{ display: "flex", gap: "1.5rem" }}>
            <div style={{ flex: 2, display: "flex", flexDirection: "column", gap: "1rem" }}>
              <SkeletonBlock height={18} width="40%" />
              <SkeletonBlock height={120} />
              <SkeletonBlock height={18} width="30%" />
              <SkeletonBlock height={80} />
              <SkeletonBlock height={18} width="35%" />
              <SkeletonBlock height={60} />
            </div>
            <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: "1rem" }}>
              <SkeletonBlock height={90} />
              <SkeletonBlock height={70} />
              <SkeletonBlock height={90} />
            </div>
          </div>
          <div style={{ marginTop: "1.5rem", fontSize: "0.75rem", color: s.muted, letterSpacing: "0.06em" }}>
            Rendering situation framing…
          </div>
        </div>
      </main>
    )
  }

  // ─── Error ─────────────────────────────────────────────────────────────────
  if (error) {
    return (
      <main style={{ minHeight: "100vh", background: s.bg, color: s.text, fontFamily: "'Inter', sans-serif", display: "flex", alignItems: "center", justifyContent: "center" }}>
        <div style={{ textAlign: "center" }}>
          <div style={{ color: s.red, fontSize: "0.875rem", marginBottom: "1rem" }}>{error}</div>
          <button onClick={() => router.push("/dashboard")} style={{ background: "transparent", border: `1px solid ${s.border}`, borderRadius: 8, color: s.muted, fontSize: "0.8rem", padding: "0.5rem 1rem", cursor: "pointer" }}>
            ← Back to compass
          </button>
        </div>
      </main>
    )
  }

  if (!data) return null

  const { brief, receipt, entityAnalysis } = data

  // Parse JSON strings from receipt
  const why: string[] = (() => { try { return JSON.parse(receipt.whyBullets) } catch { return [] } })()
  const fated: Record<string, string> | null = (() => { try { return receipt.fated ? JSON.parse(receipt.fated) : null } catch { return null } })()
  const paths: Array<{ id: string; title: string; detail: string; tag: string; status: string }> = (() => { try { return receipt.paths ? JSON.parse(receipt.paths) : [] } catch { return [] } })()
  const court: Array<{ name: string; verdict: string; detail: string }> = (() => { try { return receipt.court ? JSON.parse(receipt.court) : [] } catch { return [] } })()
  const macroTags: string[] = (() => { try { return JSON.parse(receipt.macroTags) } catch { return [] } })()
  const protecting: string[] = (() => { try { return JSON.parse(receipt.protecting) } catch { return [] } })()

  const resolution = receipt.renderResolution ?? "SHARP"
  const resStyle = RESOLUTION_STYLES[resolution] ?? RESOLUTION_STYLES.SHARP
  const weather = Y_WEATHER[receipt.yState] ?? Y_WEATHER.GREEN

  const issuedAt = new Date(receipt.createdAt).toLocaleDateString("en-US", {
    month: "short", day: "numeric", year: "numeric", hour: "2-digit", minute: "2-digit",
  })

  return (
    <main style={{ minHeight: "100vh", background: s.bg, color: s.text, fontFamily: "'Inter', sans-serif" }}>
      <style>{`@keyframes shimmer { 0%{background-position:200% 0} 100%{background-position:-200% 0} }`}</style>

      <div style={{ maxWidth: 1000, margin: "0 auto", padding: "2.5rem 1.5rem" }}>

        {/* Header bar */}
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "2rem" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
            <span style={{ fontSize: "0.65rem", letterSpacing: "0.15em", color: s.cyan, textTransform: "uppercase", fontWeight: 600 }}>ARCS FIELD OS</span>
            <span style={{ width: 1, height: 12, background: s.border }} />
            <span style={{ fontSize: "0.65rem", letterSpacing: "0.12em", color: s.muted, textTransform: "uppercase" }}>Cartography Brief</span>
            {receipt.isSatoshi && (
              <>
                <span style={{ width: 1, height: 12, background: s.border }} />
                <span style={{ fontSize: "0.65rem", letterSpacing: "0.1em", color: s.gold, textTransform: "uppercase", fontWeight: 600 }}>Satoshi Move</span>
              </>
            )}
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <span style={{ fontSize: "0.65rem", color: s.muted, marginRight: "0.25rem" }}>{issuedAt}</span>
            <button
              onClick={() => shareViaSMS(receipt.id, receipt.trueNorth)}
              title="Share via SMS"
              style={{ background: "transparent", border: `1px solid ${s.border}`, borderRadius: 6, color: s.muted, fontSize: "0.75rem", padding: "0.375rem 0.625rem", cursor: "pointer" }}
            >
              SMS
            </button>
            <button
              onClick={() => shareViaX(receipt.id, receipt.trueNorth)}
              title="Share on X"
              style={{ background: "transparent", border: `1px solid ${s.border}`, borderRadius: 6, color: s.muted, fontSize: "0.75rem", padding: "0.375rem 0.625rem", cursor: "pointer" }}
            >
              𝕏
            </button>
            <button
              onClick={() => copyLink(receipt.id, setCopied)}
              style={{ background: "transparent", border: `1px solid ${copied ? s.green : s.border}`, borderRadius: 6, color: copied ? s.green : s.muted, fontSize: "0.75rem", padding: "0.375rem 0.625rem", cursor: "pointer", transition: "color 0.2s, border-color 0.2s" }}
            >
              {copied ? "✓ Copied" : "Copy link"}
            </button>
            <button onClick={() => router.push("/dashboard")} style={{
              background: "transparent", border: `1px solid ${s.border}`,
              borderRadius: 6, color: s.muted, fontSize: "0.75rem",
              padding: "0.375rem 0.75rem", cursor: "pointer",
            }}>
              ← Compass
            </button>
          </div>
        </div>

        {/* Decision title */}
        <div style={{ marginBottom: "1.75rem" }}>
          <div style={{ fontSize: "0.65rem", color: s.muted, letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: "0.5rem" }}>Decision Under Navigation</div>
          <h1 style={{ fontSize: "1.25rem", fontWeight: 600, color: s.text, margin: 0, lineHeight: 1.4 }}>
            {receipt.decision}
          </h1>
          {receipt.entity && (
            <div style={{ marginTop: "0.5rem", fontSize: "0.8rem", color: s.dimmed }}>
              Entity: <span style={{ color: s.text }}>{receipt.entity}</span>
            </div>
          )}
        </div>

        {/* Two-column layout */}
        <div style={{ display: "flex", gap: "1.5rem", alignItems: "flex-start" }}>

          {/* ── Left column: Brief content ─────────────────────────────────── */}
          <div style={{ flex: 2, minWidth: 0, display: "flex", flexDirection: "column", gap: "1.25rem" }}>

            {/* Situation Framing */}
            <div style={{ padding: "1.5rem", background: s.surface, border: `1px solid ${s.border}`, borderRadius: 10 }}>
              <div style={{ fontSize: "0.65rem", color: s.muted, letterSpacing: "0.12em", textTransform: "uppercase", marginBottom: "1rem", fontWeight: 600 }}>
                Situation Framing
              </div>
              <div style={{ ...resStyle, lineHeight: 1.75, fontSize: "0.9375rem", color: "#cbd5e1", whiteSpace: "pre-wrap" }}>
                {brief.situationFraming}
              </div>
            </div>

            {/* True North — always SHARP, conclusion earned regardless of NCI */}
            <div style={{ padding: "1.25rem 1.5rem", background: s.surface, border: `1px solid ${s.cyan}33`, borderRadius: 10 }}>
              <div style={{ fontSize: "0.65rem", color: s.cyan, letterSpacing: "0.12em", textTransform: "uppercase", marginBottom: "0.75rem", fontWeight: 600 }}>
                True North · {MODE_LABELS[receipt.mode] ?? receipt.mode} · {DOOR_LABELS[receipt.doorClass]?.label ?? receipt.doorClass}
              </div>
              <p style={{ fontSize: "1.0625rem", lineHeight: 1.6, color: s.text, margin: 0, fontWeight: 500 }}>
                {receipt.trueNorth}
              </p>
              {why.length > 0 && (
                <ul style={{
                  marginTop: "0.875rem", paddingLeft: "1.25rem", lineHeight: 1.7, margin: "0.875rem 0 0",
                  ...resStyle, color: "#94a3b8", fontSize: "0.875rem"
                }}>
                  {why.map((w, i) => <li key={i}>{w}</li>)}
                </ul>
              )}
            </div>

            {/* FATED Leverage */}
            {fated && (
              <div style={{ padding: "1.25rem 1.5rem", background: s.surface, border: `1px solid ${s.border}`, borderRadius: 10, ...resStyle }}>
                <div style={{ fontSize: "0.65rem", color: s.muted, letterSpacing: "0.12em", textTransform: "uppercase", marginBottom: "1rem", fontWeight: 600 }}>
                  FATED Decomposition
                </div>
                <div style={{ display: "flex", flexDirection: "column", gap: "0.625rem" }}>
                  {Object.entries(fated).filter(([, v]) => v).map(([k, v]) => (
                    <div key={k} style={{ display: "flex", gap: "0.75rem", fontSize: "0.8rem" }}>
                      <span style={{ color: s.dimmed, textTransform: "uppercase", fontSize: "0.65rem", letterSpacing: "0.08em", minWidth: 88, paddingTop: "0.1rem", flexShrink: 0 }}>
                        {FATED_LABELS[k] ?? k}
                      </span>
                      <span style={{ color: "#94a3b8", lineHeight: 1.5 }}>{v}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Paths */}
            {paths.length > 0 && (
              <div style={{ padding: "1.25rem 1.5rem", background: s.surface, border: `1px solid ${s.border}`, borderRadius: 10, ...resStyle }}>
                <div style={{ fontSize: "0.65rem", color: s.muted, letterSpacing: "0.12em", textTransform: "uppercase", marginBottom: "1rem", fontWeight: 600 }}>
                  Terrain Paths
                </div>
                <div style={{ display: "flex", flexDirection: "column", gap: "0.875rem" }}>
                  {paths.map(p => (
                    <div key={p.id} style={{
                      paddingLeft: "0.875rem",
                      borderLeft: `2px solid ${p.status === "selected" ? s.cyan : p.status === "blocked" ? `${s.red}44` : s.border}`,
                    }}>
                      <div style={{ fontSize: "0.875rem", fontWeight: 600, color: p.status === "selected" ? s.text : s.muted }}>
                        {p.title}
                        <span style={{ fontWeight: 400, fontSize: "0.7rem", color: s.dimmed, marginLeft: "0.5rem" }}>({p.tag})</span>
                      </div>
                      <div style={{ fontSize: "0.8rem", color: s.dimmed, marginTop: "0.25rem", lineHeight: 1.5 }}>{p.detail}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Court */}
            {court.length > 0 && (
              <div style={{ padding: "1.25rem 1.5rem", background: s.surface, border: `1px solid ${s.border}`, borderRadius: 10, ...resStyle }}>
                <div style={{ fontSize: "0.65rem", color: s.muted, letterSpacing: "0.12em", textTransform: "uppercase", marginBottom: "1rem", fontWeight: 600 }}>
                  Constitutional Court
                </div>
                <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
                  {court.map((c, i) => (
                    <div key={i} style={{ display: "flex", gap: "0.75rem", fontSize: "0.8rem" }}>
                      <span style={{ color: VERDICT_COLOR(c.verdict), fontWeight: 700, minWidth: 64, flexShrink: 0 }}>{c.verdict}</span>
                      <span style={{ color: "#94a3b8" }}>
                        <strong style={{ color: s.text }}>{c.name}</strong> — {c.detail}
                      </span>
                    </div>
                  ))}
                </div>
                {receipt.courtVerdict && (
                  <div style={{ marginTop: "0.875rem", paddingTop: "0.875rem", borderTop: `1px solid ${s.border}`, fontSize: "0.8rem", color: s.dimmed, fontStyle: "italic" }}>
                    {receipt.courtVerdict}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* ── Right column: Terrain status ───────────────────────────────── */}
          <div style={{ flex: 1, minWidth: 220, display: "flex", flexDirection: "column", gap: "0.875rem", position: "sticky", top: "2rem" }}>

            {/* Entity panel */}
            {entityAnalysis && receipt.entity && (() => {
              const aColor = ALIGNMENT_COLOR[entityAnalysis.alignment] ?? "#64748b"
              const rows: { label: string; value: string; color?: string }[] = [
                { label: "Role",          value: entityAnalysis.role },
                { label: "Their leverage",value: entityAnalysis.leverage_theirs },
                { label: "Your leverage", value: entityAnalysis.leverage_yours },
                { label: "Signal",        value: entityAnalysis.signal_to_watch },
                { label: "Risk surface",  value: entityAnalysis.risk_surface, color: "#FF4D6D" },
              ]
              return (
                <div style={{ padding: "1rem 1.25rem", background: `${aColor}08`, border: `1px solid ${aColor}33`, borderRadius: 10 }}>
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "0.75rem" }}>
                    <div style={{ fontSize: "0.6rem", color: s.muted, letterSpacing: "0.1em", textTransform: "uppercase", fontWeight: 600 }}>
                      Entity
                    </div>
                    <span style={{
                      fontSize: "0.55rem", fontWeight: 700, letterSpacing: "0.08em",
                      color: aColor, textTransform: "uppercase",
                      padding: "0.15rem 0.4rem", borderRadius: 4,
                      background: `${aColor}18`, border: `1px solid ${aColor}44`,
                    }}>
                      {entityAnalysis.alignment}
                    </span>
                  </div>
                  <div style={{ fontSize: "0.8rem", fontWeight: 600, color: s.text, marginBottom: "0.75rem", lineHeight: 1.3 }}>
                    {receipt.entity}
                  </div>
                  <div style={{ fontSize: "0.7rem", color: "#94a3b8", lineHeight: 1.55, marginBottom: "0.875rem", fontStyle: "italic" }}>
                    {entityAnalysis.alignment_read}
                  </div>
                  <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
                    {rows.map(r => (
                      <div key={r.label}>
                        <div style={{ fontSize: "0.55rem", color: s.muted, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: "0.15rem" }}>{r.label}</div>
                        <div style={{ fontSize: "0.75rem", color: r.color ?? "#94a3b8", lineHeight: 1.45 }}>{r.value}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )
            })()}

            {/* Y state terrain weather */}
            <div style={{
              padding: "1rem 1.25rem",
              background: `${weather.color}0D`,
              border: `1px solid ${weather.color}33`,
              borderRadius: 10,
            }}>
              <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.75rem" }}>
                <span style={{ color: weather.color, fontWeight: 700, fontSize: "1rem" }}>{weather.icon}</span>
                <span style={{ fontSize: "0.6rem", letterSpacing: "0.12em", color: weather.color, textTransform: "uppercase", fontWeight: 600 }}>
                  {weather.label}
                </span>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.7rem", color: s.muted }}>
                <span>Conviction</span>
                <span style={{ color: s.text, fontWeight: 600 }}>{CONVICTION_LABELS[receipt.yConviction] ?? receipt.yConviction}</span>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.7rem", color: s.muted, marginTop: "0.375rem" }}>
                <span>Stability</span>
                <span style={{ color: s.text, fontWeight: 600 }}>{STABILITY_LABELS[receipt.yStability] ?? receipt.yStability}</span>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.7rem", color: s.muted, marginTop: "0.375rem" }}>
                <span>Resolution</span>
                <span style={{ color: s.dimmed, fontWeight: 500, fontSize: "0.65rem" }}>{resolution}</span>
              </div>
            </div>

            {/* NCI score */}
            <div style={{ padding: "1rem 1.25rem", background: s.surface, border: `1px solid ${s.border}`, borderRadius: 10 }}>
              <div style={{ fontSize: "0.6rem", color: s.muted, letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: "0.5rem" }}>
                Confidence Score
              </div>
              <div style={{ display: "flex", alignItems: "baseline", gap: "0.25rem" }}>
                <span style={{ fontSize: "2.25rem", fontWeight: 700, color: NCI_COLOR(receipt.nciScore), lineHeight: 1 }}>
                  {receipt.nciScore}
                </span>
                <span style={{ fontSize: "0.875rem", color: s.muted }}>/100</span>
              </div>
              <div style={{ marginTop: "0.375rem", fontSize: "0.72rem", color: s.muted, lineHeight: 1.4 }}>
                {receipt.nciScore >= 75 ? "High confidence — clear path forward" :
                 receipt.nciScore >= 55 ? "Moderate — key unknowns remain" :
                 receipt.nciScore >= 35 ? "Low — significant uncertainty in play" :
                 "Very low — this needs more information before moving"}
              </div>
              {receipt.coherencePct !== null && (
                <div style={{ marginTop: "0.375rem", fontSize: "0.7rem", color: s.dimmed }}>
                  Question clarity: <span style={{ color: s.muted, fontWeight: 600 }}>{receipt.coherencePct}%</span>
                  {receipt.coherencePct < 70 && <span style={{ color: s.gold }}> — consider sharpening the question</span>}
                </div>
              )}
            </div>

            {/* Kinematic field — internal plumbing, not surfaced to user */}

            {/* Decision context — plain English */}
            <div style={{ padding: "1rem 1.25rem", background: s.surface, border: `1px solid ${s.border}`, borderRadius: 10 }}>
              <div style={{ fontSize: "0.6rem", color: s.muted, letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: "0.75rem" }}>Decision Context</div>
              <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.7rem" }}>
                  <span style={{ color: s.muted }}>Approach</span>
                  <span style={{ color: s.text, fontWeight: 600 }}>
                    {MODE_LABELS[receipt.mode] ?? receipt.mode}
                  </span>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.7rem" }}>
                  <span style={{ color: s.muted }}>Reversibility</span>
                  <span style={{ color: DOOR_LABELS[receipt.doorClass]?.color ?? s.text, fontWeight: 600 }}>
                    {DOOR_LABELS[receipt.doorClass]?.label ?? receipt.doorClass}
                  </span>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.7rem" }}>
                  <span style={{ color: s.muted }}>Timeframe</span>
                  <span style={{ color: s.text, fontWeight: 600 }}>{HORIZON_LABELS[receipt.window] ?? receipt.window}</span>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.7rem" }}>
                  <span style={{ color: s.muted }}>Downside if wrong</span>
                  <span style={{ color: receipt.stakes === "HIGH" ? s.red : receipt.stakes === "MEDIUM" ? s.gold : s.green, fontWeight: 600 }}>
                    {receipt.stakes === "HIGH" ? "Severe / hard to recover" : receipt.stakes === "MEDIUM" ? "Significant but survivable" : "Low — learn and move on"}
                  </span>
                </div>
              </div>
            </div>

            {/* Protecting */}
            {protecting.length > 0 && (
              <div style={{ padding: "1rem 1.25rem", background: s.surface, border: `1px solid ${s.border}`, borderRadius: 10, ...resStyle }}>
                <div style={{ fontSize: "0.6rem", color: s.muted, letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: "0.625rem" }}>
                  Protecting
                </div>
                <div style={{ display: "flex", gap: "0.375rem", flexWrap: "wrap" }}>
                  {protecting.map(p => (
                    <span key={p} style={{ fontSize: "0.7rem", padding: "0.2rem 0.5rem", borderRadius: 4, background: "#00FF9D15", border: "1px solid #00FF9D33", color: "#00FF9D", fontWeight: 600 }}>
                      {p}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Macro tags */}
            {macroTags.length > 0 && (
              <div style={{ padding: "1rem 1.25rem", background: s.surface, border: `1px solid ${s.border}`, borderRadius: 10, ...resStyle }}>
                <div style={{ fontSize: "0.6rem", color: s.muted, letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: "0.625rem" }}>
                  Macro Tags
                </div>
                <div style={{ display: "flex", gap: "0.375rem", flexWrap: "wrap" }}>
                  {macroTags.map(t => (
                    <span key={t} style={{ fontSize: "0.7rem", padding: "0.2rem 0.5rem", borderRadius: 4, background: "#1e293b", color: "#94a3b8", fontWeight: 600 }}>
                      {t}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Prep Guide CTA */}
            <button
              onClick={() => router.push(`/guide/${receipt.id}`)}
              style={{
                width: "100%", padding: "0.625rem", borderRadius: 8, marginBottom: "0.5rem",
                background: "transparent", border: `1px solid ${s.cyan}44`,
                color: s.cyan, fontSize: "0.75rem",
                cursor: "pointer", letterSpacing: "0.04em",
              }}
            >
              ⊕ Generate Prep Guide
            </button>

            {/* Re-run CTA */}
            <button
              onClick={() => router.push("/dashboard")}
              style={{
                width: "100%", padding: "0.625rem", borderRadius: 8,
                background: "transparent", border: `1px solid ${s.gold}44`,
                color: s.gold, fontSize: "0.75rem",
                cursor: "pointer", letterSpacing: "0.04em",
              }}
            >
              ↑ Re-run with calibration
            </button>
          </div>
        </div>

        {/* ATG — Tributaries */}
        {data.tributaries && data.tributaries.length > 0 && (
          <div style={{ marginTop: "2rem", paddingTop: "1.5rem", borderTop: `1px solid ${s.border}` }}>
            <div style={{ fontSize: "0.6rem", color: s.muted, letterSpacing: "0.12em", textTransform: "uppercase", marginBottom: "0.875rem" }}>
              Tributaries · Navigate next
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
              {data.tributaries.map((t, i) => {
                const tColor = t.type === "meta" ? s.cyan : t.type === "challenge" ? s.red : s.gold
                return (
                  <button
                    key={i}
                    onClick={() => router.push(`/dashboard?q=${encodeURIComponent(t.prompt)}`)}
                    style={{
                      width: "100%", padding: "0.75rem 1rem", borderRadius: 8, textAlign: "left",
                      background: `${tColor}08`, border: `1px solid ${tColor}33`, cursor: "pointer",
                      display: "flex", flexDirection: "column", gap: "0.25rem",
                    }}
                  >
                    <span style={{ fontSize: "0.6rem", color: tColor, letterSpacing: "0.1em", textTransform: "uppercase", fontWeight: 600 }}>{t.label}</span>
                    <span style={{ fontSize: "0.8rem", color: "#94a3b8", lineHeight: 1.5 }}>{t.prompt}</span>
                  </button>
                )
              })}
            </div>
          </div>
        )}

        {/* Receipt ID footer */}
        <div style={{ marginTop: "2rem", paddingTop: "1rem", borderTop: `1px solid ${s.border}`, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <span style={{ fontSize: "0.65rem", color: s.muted, fontFamily: "monospace", letterSpacing: "0.04em" }}>
            {receipt.id}
          </span>
          <span style={{ fontSize: "0.65rem", color: s.muted, letterSpacing: "0.06em", textTransform: "uppercase" }}>
            ARCS · Cartography Receipt
          </span>
        </div>
      </div>
    </main>
  )
}
