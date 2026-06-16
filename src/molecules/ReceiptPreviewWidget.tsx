"use client"
// Receipt Preview Widget — three layout variants for the dashboard's first
// look at a result, before the user dives into the full Brief/Receipt.
//
// Variant A — Instrument Cluster: gauge grid + True North glow card
// Variant B — The Read:           synthesis block (cyan left-rail) + queue bullets
// Variant C — Verdict Artifact:   underlit LED receipt card (F05 fix from audit)
//
// All primitives pulled from the arcs.care Surface Audit atomic compositions.
import React from "react"
import { signal, text, font, border, nciColor, getWeather } from "@/ui/tokens"
import { CoverBlock } from "@/document/patterns/CoverBlock"
import type { CompassResult } from "@/lib/mockCompass"

export type PreviewVariant = "cluster" | "read" | "artifact"

// ── Shared palette (from audit :root) ──────────────────────────────────────
const HAIR = "rgba(22,30,43,0.8)"

// ── Gauge — the instrument cluster atom ────────────────────────────────────
function Gauge({ label, value, sub, sparkPct, color }: {
  label: string; value: string; sub?: string; sparkPct?: number; color: string
}) {
  return (
    <div style={{
      position: "relative", borderRadius: 8, padding: "16px 18px 17px", overflow: "hidden",
      border: `1px solid ${border.subtle}`,
      background: "linear-gradient(160deg,rgba(255,255,255,.045),rgba(255,255,255,.008) 40%,rgba(0,0,0,.2)),linear-gradient(165deg,#10171f,#0a0f15)",
      boxShadow: "inset 0 1px 0 rgba(255,255,255,.06),0 6px 18px rgba(0,0,0,.45)",
    }}>
      <div style={{ fontFamily: font.mono, fontSize: "0.6rem", fontWeight: 700, letterSpacing: ".13em", textTransform: "uppercase", color: text.muted, marginBottom: 12, display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <span>{label}</span>
      </div>
      <div style={{ fontFamily: font.mono, fontWeight: 800, fontSize: "2.25rem", lineHeight: .9, letterSpacing: "-.01em", color }}>{value}</div>
      {sub && <div style={{ fontFamily: font.mono, fontSize: "0.65rem", color: text.muted, marginTop: 9, letterSpacing: ".02em" }}>{sub}</div>}
      {sparkPct != null && (
        <div style={{ marginTop: 13, height: 4, borderRadius: 2, background: "#0a1018", overflow: "hidden", boxShadow: "inset 0 1px 2px rgba(0,0,0,.6)" }}>
          <div style={{ display: "block", height: "100%", width: `${Math.min(100, Math.max(0, sparkPct))}%`, borderRadius: 2, background: `linear-gradient(90deg, ${color}66, ${color})` }} />
        </div>
      )}
    </div>
  )
}

// ── Variant A — Instrument Cluster ─────────────────────────────────────────
function VariantCluster({ result, onOpenBrief, onOpenReceipt }: WidgetProps) {
  const nc = nciColor(result.nci_score)
  const w = getWeather(result.y_state)
  const coherence = result.coherence_pct ?? 0

  return (
    <div>
      {/* 3-col gauge grid */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 12, marginBottom: 16 }}>
        <Gauge label="Conviction" value={String(result.nci_score)} sub="/ 100 NCI" sparkPct={result.nci_score} color={nc} />
        <Gauge label="Coherence" value={`${coherence}%`} sub={`${result.decision_mode} · ${result.door_class?.replace(/_/g," ")}`} sparkPct={coherence} color={signal.gold} />
        <Gauge label="Y-State" value={w.icon} sub={`${w.label} · ${result.render_resolution}`} color={w.color} />
      </div>

      {/* True North glow card */}
      <div style={{
        border: `1px solid rgba(0,240,255,.3)`, borderRadius: 10, padding: "22px 24px 24px",
        background: "linear-gradient(165deg,rgba(0,240,255,.07),rgba(10,16,24,.7))",
        boxShadow: "inset 0 1px 0 rgba(0,240,255,.18),0 0 28px rgba(0,240,255,.06)",
        marginBottom: 16,
      }}>
        <div style={{ fontFamily: font.mono, fontSize: "0.6rem", fontWeight: 700, letterSpacing: ".16em", textTransform: "uppercase", color: signal.cyan, marginBottom: 12 }}>True North</div>
        <div style={{ fontFamily: font.sans, fontSize: "clamp(1rem,2vw,1.3rem)", fontWeight: 600, letterSpacing: "-.02em", lineHeight: 1.45, color: text.primary }}>{result.true_north}</div>
      </div>

      <CTARow onOpenBrief={onOpenBrief} onOpenReceipt={onOpenReceipt} />
    </div>
  )
}

// ── Variant B — The Read (synthesis block + why queue) ─────────────────────
function VariantRead({ result, onOpenBrief, onOpenReceipt }: WidgetProps) {
  const nc = nciColor(result.nci_score)
  const w = getWeather(result.y_state)

  return (
    <div>
      {/* Kicker row */}
      <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 14 }}>
        <span style={{ fontFamily: font.mono, fontSize: "0.6rem", fontWeight: 700, letterSpacing: ".13em", textTransform: "uppercase", color: text.muted }}>Decision Receipt</span>
        <div style={{ flex: 1, height: 1, background: border.subtle }} />
        <span style={{ fontFamily: font.mono, fontSize: "0.65rem", fontWeight: 800, color: nc }}>{result.nci_score}</span>
        <span style={{ fontFamily: font.mono, fontSize: "0.55rem", color: text.muted }}>NCI</span>
        <div style={{ width: 1, height: 13, background: border.subtle }} />
        <span style={{ fontFamily: font.mono, fontSize: "0.6rem", color: w.color }}>{w.icon} {w.label}</span>
      </div>

      {/* Synthesis block — cyan left-rail */}
      <div style={{
        border: `1px solid ${border.subtle}`, borderLeft: `3px solid ${signal.cyan}`, borderRadius: 9, padding: "22px 24px",
        background: "linear-gradient(165deg,rgba(0,240,255,.05),rgba(10,18,26,.6))",
        marginBottom: 14,
      }}>
        <div style={{ fontFamily: font.mono, fontSize: "0.55rem", fontWeight: 700, letterSpacing: ".14em", textTransform: "uppercase", color: signal.cyan, marginBottom: 10 }}>True North</div>
        <div style={{ fontFamily: font.sans, fontSize: "clamp(1rem,2vw,1.25rem)", fontWeight: 600, lineHeight: 1.5, color: text.primary, marginBottom: result.why?.length ? 16 : 0 }}>
          {result.true_north}
        </div>

        {/* Why queue — compact */}
        {result.why?.slice(0,3).map((w, i) => (
          <div key={i} style={{ display: "flex", gap: 12, alignItems: "flex-start", paddingTop: i === 0 ? 0 : 6, borderTop: i === 0 ? "none" : `1px solid ${HAIR}` }}>
            <span style={{ fontFamily: font.mono, fontSize: "0.6rem", fontWeight: 800, color: `${signal.cyan}88`, flexShrink: 0, marginTop: 3 }}>{String(i+1).padStart(2,"0")}</span>
            <span style={{ fontFamily: font.sans, fontSize: "0.82rem", color: text.secondary, lineHeight: 1.62 }}>{w}</span>
          </div>
        ))}
      </div>

      <div style={{ display: "flex", gap: 8, marginBottom: 14, flexWrap: "wrap" }}>
        {[result.decision_mode, result.door_class?.replace(/_/g," ")].filter(Boolean).map(t => (
          <span key={t} style={{ display: "inline-flex", alignItems: "center", height: 23, padding: "0 11px", borderRadius: 4, fontFamily: font.mono, fontSize: "0.6rem", fontWeight: 700, letterSpacing: ".1em", textTransform: "uppercase", color: signal.cyan, background: "rgba(0,240,255,.1)", border: `1px solid rgba(0,240,255,.28)` }}>{t}</span>
        ))}
      </div>

      <CTARow onOpenBrief={onOpenBrief} onOpenReceipt={onOpenReceipt} />
    </div>
  )
}

// ── Variant C — Verdict Artifact (CoverBlock document grammar) ──────────────
// Renders the receipt as a document cover: Y-state + mode badges, True North as
// the hero title, the decision as subtitle, the instrument readout as the meta
// strip, and the brief/receipt CTAs as cover actions.
function VariantArtifact({ result, onOpenBrief, onOpenReceipt }: WidgetProps) {
  const w = getWeather(result.y_state)
  const door = result.door_class?.replace(/_/g, " ")
  const meta = [
    `NCI ${result.nci_score} / 100`,
    result.decision_mode && `MODE ${result.decision_mode}`,
    door && `DOOR ${door}`,
    result.coherence_pct != null && `COHERENCE ${result.coherence_pct}%`,
  ].filter(Boolean).join("  ·  ")

  return (
    <div style={{
      borderRadius: 12, overflow: "hidden", padding: "0 22px",
      background: `linear-gradient(180deg,rgba(14,22,38,.5),rgba(9,14,24,.66))`,
      boxShadow: `inset 0 -3px 20px ${signal.cyan}18, 0 0 0 0.5px ${signal.cyan}22`,
    }}>
      <CoverBlock
        accent={w.color}
        badges={[`${w.icon} ${w.label}`, result.decision_mode].filter(Boolean) as string[]}
        title={result.true_north}
        subtitle={result.question}
        meta={meta}
        actions={["Open Cartography Brief →", "Receipt"]}
        onAction={(i) => (i === 0 ? onOpenBrief?.() : onOpenReceipt?.())}
      />
    </div>
  )
}

// ── Shared CTA row ──────────────────────────────────────────────────────────
function CTARow({ onOpenBrief, onOpenReceipt }: { onOpenBrief?: () => void; onOpenReceipt?: () => void }) {
  const btn = (primary: boolean): React.CSSProperties => ({
    fontFamily: font.mono, fontSize: "0.65rem", fontWeight: 700, letterSpacing: ".06em", textTransform: "uppercase",
    padding: "8px 18px", borderRadius: 20, cursor: "pointer", border: ".5px solid",
    display: "inline-flex", alignItems: "center", gap: 6,
    ...(primary
      ? { background: `${signal.cyan}14`, borderColor: `${signal.cyan}55`, color: signal.cyan, boxShadow: `0 0 10px ${signal.cyan}14` }
      : { background: "rgba(15,21,32,.5)", borderColor: "rgba(71,85,105,.28)", color: text.muted }),
  })
  return (
    <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
      <button style={btn(true)} onClick={onOpenBrief}>Open Cartography Brief →</button>
      <button style={btn(false)} onClick={onOpenReceipt}>Receipt</button>
    </div>
  )
}

// ── Tab selector ────────────────────────────────────────────────────────────
const VARIANTS: { id: PreviewVariant; label: string }[] = [
  { id: "cluster", label: "⊕ Cluster" },
  { id: "read",    label: "◈ The Read" },
  { id: "artifact",label: "◆ Artifact" },
]

// ── Root export ─────────────────────────────────────────────────────────────
interface WidgetProps {
  result: CompassResult
  onOpenBrief?: () => void
  onOpenReceipt?: () => void
}

export function ReceiptPreviewWidget({
  result,
  onOpenBrief,
  onOpenReceipt,
  defaultVariant = "read",
}: WidgetProps & { defaultVariant?: PreviewVariant }) {
  const startIdx = Math.max(0, VARIANTS.findIndex(v => v.id === defaultVariant))
  const [idx, setIdx] = React.useState(startIdx)
  const active = VARIANTS[idx].id
  const go = (dir: number) => setIdx(i => (i + dir + VARIANTS.length) % VARIANTS.length)

  const arrow: React.CSSProperties = {
    display: "inline-flex", alignItems: "center", justifyContent: "center",
    width: 30, height: 30, borderRadius: 16, cursor: "pointer", flexShrink: 0,
    border: `.5px solid rgba(71,85,105,.28)`, background: "rgba(10,15,26,.5)",
    color: text.muted, fontFamily: font.mono, fontSize: "0.95rem", lineHeight: 1,
    transition: "all .12s",
  }

  return (
    <div>
      {/* Variant carousel — ‹ label › with dot indicators */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 10, marginBottom: 18, borderBottom: `0.5px solid ${border.subtle}`, paddingBottom: 14 }}>
        <button aria-label="Previous view" onClick={() => go(-1)} style={arrow}>‹</button>

        <div style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", gap: 8 }}>
          <span style={{
            fontFamily: font.mono, fontSize: "0.72rem", fontWeight: 700, letterSpacing: ".12em",
            textTransform: "uppercase", color: signal.cyan, textShadow: `0 0 10px ${signal.cyan}33`,
          }}>
            {VARIANTS[idx].label}
          </span>
          <div style={{ display: "flex", gap: 5 }}>
            {VARIANTS.map((v, i) => (
              <button
                key={v.id}
                aria-label={v.label}
                onClick={() => setIdx(i)}
                style={{
                  width: i === idx ? 18 : 5, height: 5, borderRadius: i === idx ? 3 : "50%",
                  background: i === idx ? `${signal.cyan}bb` : "rgba(71,85,105,.4)",
                  border: "none", padding: 0, cursor: "pointer", transition: "all .15s",
                }}
              />
            ))}
          </div>
        </div>

        <button aria-label="Next view" onClick={() => go(1)} style={arrow}>›</button>
      </div>

      {active === "cluster"  && <VariantCluster  result={result} onOpenBrief={onOpenBrief} onOpenReceipt={onOpenReceipt} />}
      {active === "read"     && <VariantRead     result={result} onOpenBrief={onOpenBrief} onOpenReceipt={onOpenReceipt} />}
      {active === "artifact" && <VariantArtifact result={result} onOpenBrief={onOpenBrief} onOpenReceipt={onOpenReceipt} />}
    </div>
  )
}
