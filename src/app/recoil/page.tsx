// ARCS Recoil Report — Document UIKit pattern
// Layout: left sidebar nav + scrollable document body
// Render resolution: DEGRADED (YELLOW/MEDIUM/WATCH)
"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"

// ─── Tokens ───────────────────────────────────────────────────────────────────

const t = {
  bg:       "#020408",
  sidebar:  "#060a0f",
  surface:  "#0d1117",
  border:   "#1e293b",
  text:     "#e2e8f0",
  muted:    "#475569",
  dimmed:   "#64748b",
  cyan:     "#00F0FF",
  green:    "#00FF9D",
  gold:     "#FFD700",
  red:      "#FF4D6D",
  purple:   "#A78BFA",
  orange:   "#FB923C",
}

// DEGRADED render (YELLOW state)
const res = { opacity: 0.85 as number, fontWeight: 400 as number, letterSpacing: "0.01em" }

// ─── Static receipt ───────────────────────────────────────────────────────────

const SECTIONS = [
  { id: "decision",    label: "D — Decision" },
  { id: "entities",   label: "E — Entities" },
  { id: "window",     label: "W — Window" },
  { id: "ygate",      label: "Y-Gate Shift" },
  { id: "delta",      label: "Signal Delta" },
  { id: "receipt",    label: "Ex-Ante Receipt" },
  { id: "confidence", label: "Confidence" },
  { id: "nextsteps",  label: "Next Steps" },
  { id: "analysis",   label: "Recoil Analysis" },
  { id: "sentinel",   label: "Drift Sentinel" },
]

const ENTITIES = [
  { role: "Candidate",         name: "Zach Harris" },
  { role: "Recruiter",         name: "Ally — Figma (joined Mar 2026, split eng/data)" },
  { role: "Hiring Manager",    name: "Caitlin — 'Code' org lead" },
  { role: "Org Target",        name: "Figma 'Code' — Dev Mode · Code Connect · MCP" },
  { role: "Alt A",             name: "Deloitte FDE — Fortune 100 / frontier tech" },
  { role: "Alt B",             name: "JPMorgan DeFi infra — $10T/day capital" },
]

const SIGNAL_DELTAS = [
  { signal: "Role shape",             expected: "Internal FDE, strategic cross-functional layer",         actual: "✅ Confirmed — Code org spans product/eng/design",              delta: "MATCH",    dc: t.green },
  { signal: "Greenfield opportunity", expected: "Significant — inflection point, not routine",            actual: "✅ 'New things that may not even exist today'",                  delta: "MATCH",    dc: t.green },
  { signal: "HM interest",            expected: "Unknown — cold sourcing",                                actual: "✅ Caitlin proactively sourced LinkedIn before screen",           delta: "SURPRISE", dc: t.cyan  },
  { signal: "Interview process",      expected: "Standard tech screen → case study",                     actual: "⚠️ No-AI coding assessment required — policy in transition",     delta: "MISS",     dc: t.red   },
  { signal: "AI culture",             expected: "Forward-leaning, AI-native",                             actual: "⚠️ AI encouraged on the job; blocked in assessments",            delta: "PARTIAL",  dc: t.gold  },
  { signal: "Senior IC track",        expected: "Available",                                              actual: "🔲 Data science org framing — seniority unclear",               delta: "UNCLEAR",  dc: t.muted },
  { signal: "Strategic latitude",     expected: "High — war room, board-level",                          actual: "✅ Roadmap influence confirmed; 'shape what this looks like'",    delta: "MATCH",    dc: t.green },
]

const CONFIDENCE = [
  { label: "Role fit if I get through",          pct: 82, color: t.green  },
  { label: "Assessment flexibility from HM",     pct: 35, color: t.red    },
  { label: "Alt role found (strategy/ops)",      pct: 55, color: t.gold   },
  { label: "Full process → offer",               pct: 28, color: t.red    },
  { label: "Time well-spent vs. alternatives",   pct: 40, color: t.gold   },
]

const NEXT_STEPS = [
  { n: 1, rev: 10, color: t.green,  label: "WAIT",                   body: "Hold all activity until recruiter returns. Deadline: nudge Jun 16 if no contact. Cost: zero." },
  { n: 2, rev: 9,  color: t.green,  label: "EXPLORE ALT ROLES",      body: "Ask about strategy/ops, Dylan's org, or any roles without rigid assessment. Frame as fit-finding." },
  { n: 3, rev: 7,  color: t.gold,   label: "BUILD CASE STUDY NOW",   body: "Grayscale A/B sprint = perfect experimentation story. ~3–4 hrs. Dual-use for Deloitte too." },
  { n: 4, rev: 6,  color: t.gold,   label: "DECLINE GRACEFULLY",     body: "If assessment stays rigid: warm exit. Keep Caitlin's attention for better timing window." },
  { n: 5, rev: 4,  color: t.muted,  label: "SPEEDRUN W/ AI IF OK",   body: "Only if recruiter confirms AI tools allowed. Offer already made — don't repeat unprompted." },
]

// ─── Micro-components ─────────────────────────────────────────────────────────

function SectionAnchor({ id }: { id: string }) {
  return <div id={id} style={{ scrollMarginTop: "1.5rem" }} />
}

function SectionHead({ label }: { label: string }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", marginBottom: "1.25rem" }}>
      <span style={{ fontSize: "0.58rem", letterSpacing: "0.18em", color: t.cyan, textTransform: "uppercase", fontWeight: 700 }}>{label}</span>
      <div style={{ flex: 1, height: 1, background: t.border }} />
    </div>
  )
}

function Chip({ label, color, solid }: { label: string; color: string; solid?: boolean }) {
  return (
    <span style={{
      display: "inline-block", fontSize: "0.58rem", letterSpacing: "0.12em",
      textTransform: "uppercase", fontWeight: 700,
      padding: "0.2rem 0.55rem", borderRadius: 4,
      background: solid ? color : "transparent",
      border: `1px solid ${color}`,
      color: solid ? t.bg : color,
    }}>{label}</span>
  )
}

function QuoteBlock({ children }: { children: React.ReactNode }) {
  return (
    <div style={{
      position: "relative", paddingLeft: "1.25rem", margin: "1rem 0",
    }}>
      <div style={{ position: "absolute", left: 0, top: 0, bottom: 0, width: 3, borderRadius: 2, background: t.cyan }} />
      <p style={{ fontSize: "0.82rem", color: t.text, lineHeight: 1.7, fontStyle: "italic", ...res }}>
        {children}
      </p>
    </div>
  )
}

function AsideBox({ color, children }: { color: string; children: React.ReactNode }) {
  return (
    <div style={{
      background: `${color}0d`, border: `1px solid ${color}28`,
      borderRadius: 6, padding: "0.875rem 1rem 0.875rem 1.125rem",
      position: "relative", overflow: "hidden",
    }}>
      <div style={{ position: "absolute", left: 0, top: 0, bottom: 0, width: 3, background: color, borderRadius: "6px 0 0 6px" }} />
      {children}
    </div>
  )
}

function ConfidenceBar({ label, pct, color }: { label: string; pct: number; color: string }) {
  return (
    <div style={{ marginBottom: "0.875rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.35rem" }}>
        <span style={{ fontSize: "0.73rem", color: t.text, ...res }}>{label}</span>
        <span style={{ fontSize: "0.73rem", color, fontWeight: 600 }}>{pct}%</span>
      </div>
      <div style={{ height: 2, background: t.border, borderRadius: 2 }}>
        <div style={{ height: 2, width: `${pct}%`, background: color, borderRadius: 2 }} />
      </div>
    </div>
  )
}

// ─── Page ─────────────────────────────────────────────────────────────────────

export default function RecoilPage() {
  const router = useRouter()
  const [active, setActive] = useState("decision")

  return (
    <div style={{ minHeight: "100vh", background: t.bg, color: t.text, fontFamily: "'Inter', -apple-system, sans-serif", display: "flex", flexDirection: "column" }}>

      {/* ── Top bar ──────────────────────────────────────────────────────────── */}
      <div style={{ borderBottom: `1px solid ${t.border}`, padding: "0 1.5rem", height: 44, display: "flex", alignItems: "center", justifyContent: "space-between", flexShrink: 0 }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.625rem" }}>
          <span style={{ fontSize: "0.58rem", letterSpacing: "0.18em", color: t.cyan, textTransform: "uppercase", fontWeight: 700 }}>ARCS FIELD OS</span>
          <span style={{ width: 1, height: 10, background: t.border }} />
          <span style={{ fontSize: "0.58rem", letterSpacing: "0.14em", color: t.muted, textTransform: "uppercase" }}>Recoil Report</span>
          <span style={{ width: 1, height: 10, background: t.border }} />
          <Chip label="CONVERSATION_DEBRIEF" color={t.gold} />
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
          <span style={{ fontSize: "0.62rem", color: t.dimmed }}>Jun 8, 2026 · 2:30 PM EDT</span>
          <button onClick={() => router.push("/dashboard")} style={{ background: "transparent", border: `1px solid ${t.border}`, borderRadius: 5, color: t.muted, fontSize: "0.68rem", padding: "0.25rem 0.625rem", cursor: "pointer" }}>
            ← Compass
          </button>
        </div>
      </div>

      {/* ── Body: sidebar + content ──────────────────────────────────────────── */}
      <div style={{ display: "flex", flex: 1, overflow: "hidden" }}>

        {/* Sidebar */}
        <aside style={{
          width: 200, flexShrink: 0, background: t.sidebar,
          borderRight: `1px solid ${t.border}`,
          display: "flex", flexDirection: "column",
          padding: "1.5rem 0",
          overflowY: "auto",
        }}>
          {/* Receipt ID */}
          <div style={{ padding: "0 1rem 1.25rem", borderBottom: `1px solid ${t.border}`, marginBottom: "1.25rem" }}>
            <div style={{ fontSize: "0.55rem", letterSpacing: "0.1em", color: t.muted, textTransform: "uppercase", marginBottom: "0.35rem" }}>Receipt</div>
            <div style={{ fontSize: "0.62rem", color: t.dimmed, lineHeight: 1.5, wordBreak: "break-all" }}>
              ARCS-ORIENT<br />2026-06-08<br />figma-r001
            </div>
          </div>

          {/* Gate status */}
          <div style={{ padding: "0 1rem 1.25rem", borderBottom: `1px solid ${t.border}`, marginBottom: "1.25rem" }}>
            <div style={{ display: "flex", flexDirection: "column", gap: "0.4rem" }}>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span style={{ fontSize: "0.6rem", color: t.muted }}>Y-Gate</span>
                <Chip label="YELLOW" color={t.gold} />
              </div>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span style={{ fontSize: "0.6rem", color: t.muted }}>NCI</span>
                <span style={{ fontSize: "0.68rem", color: t.red }}>72 → 58</span>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span style={{ fontSize: "0.6rem", color: t.muted }}>Render</span>
                <span style={{ fontSize: "0.62rem", color: t.gold }}>DEGRADED</span>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span style={{ fontSize: "0.6rem", color: t.muted }}>Verdict</span>
                <Chip label="HOLD" color={t.gold} solid />
              </div>
            </div>
          </div>

          {/* Nav */}
          <nav style={{ padding: "0 0.5rem" }}>
            {SECTIONS.map((sec) => (
              <a
                key={sec.id}
                href={`#${sec.id}`}
                onClick={() => setActive(sec.id)}
                style={{
                  display: "flex", alignItems: "center", gap: "0", position: "relative",
                  padding: "0.45rem 0.75rem",
                  borderRadius: 5, marginBottom: "0.15rem",
                  background: active === sec.id ? `${t.cyan}0d` : "transparent",
                  textDecoration: "none",
                  cursor: "pointer",
                }}
              >
                {active === sec.id && (
                  <div style={{ position: "absolute", left: 0, top: "20%", bottom: "20%", width: 2, borderRadius: 1, background: t.cyan }} />
                )}
                <span style={{
                  fontSize: "0.7rem",
                  color: active === sec.id ? t.cyan : t.muted,
                  fontWeight: active === sec.id ? 600 : 400,
                  letterSpacing: "0.02em",
                  paddingLeft: "0.5rem",
                }}>
                  {sec.label}
                </span>
              </a>
            ))}
          </nav>
        </aside>

        {/* Main document */}
        <main style={{ flex: 1, overflowY: "auto", padding: "2rem 2.5rem 4rem" }}>

          {/* Cover block */}
          <div style={{ marginBottom: "2.5rem" }}>
            <div style={{ display: "flex", gap: "0.5rem", marginBottom: "1rem", flexWrap: "wrap" }}>
              <Chip label="YELLOW" color={t.gold} solid />
              <Chip label="MEDIUM" color={t.gold} />
              <Chip label="WATCH" color={t.gold} />
              <Chip label="DEGRADED" color={t.muted} />
            </div>
            <h1 style={{ fontSize: "1.5rem", fontWeight: 500, lineHeight: 1.3, color: t.text, marginBottom: "0.5rem", ...res }}>
              Figma Recruiter Screen
            </h1>
            <p style={{ fontSize: "0.8rem", color: t.dimmed, marginBottom: "1.25rem" }}>
              A cartographic update. Signal delta, conviction shift, ex-ante receipt, survivable next steps. Not a debrief.
            </p>
            <div style={{ display: "flex", gap: "0.625rem" }}>
              <button style={{ background: t.cyan, border: "none", borderRadius: 6, color: t.bg, fontSize: "0.72rem", fontWeight: 700, padding: "0.5rem 1.1rem", cursor: "pointer", letterSpacing: "0.04em" }}>
                HOLD · Wait for HM feedback
              </button>
              <button style={{ background: "transparent", border: `1px solid ${t.border}`, borderRadius: 6, color: t.muted, fontSize: "0.72rem", padding: "0.5rem 1rem", cursor: "pointer" }}>
                NCI Δ −14
              </button>
            </div>
          </div>

          <div style={{ height: 1, background: t.border, marginBottom: "2rem" }} />

          {/* ── D — Decision ──────────────────────────────────────────────── */}
          <SectionAnchor id="decision" />
          <SectionHead label="D — Decision" />
          <p style={{ fontSize: "0.9rem", lineHeight: 1.7, color: t.text, marginBottom: "0.75rem", ...res }}>
            Should I invest further time in Figma's interview process given the no-AI coding assessment constraint, my active pipeline, and the confirmed role shape?
          </p>
          <p style={{ fontSize: "0.75rem", color: t.dimmed, fontStyle: "italic", marginBottom: "2rem" }}>
            Atomic form: Proceed, hold, or redirect — and at what cost?
          </p>

          {/* ── E — Entities ──────────────────────────────────────────────── */}
          <SectionAnchor id="entities" />
          <SectionHead label="E — Entities" />
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))", gap: "0.75rem", marginBottom: "2rem" }}>
            {ENTITIES.map((e, i) => (
              <AsideBox key={i} color={i < 4 ? t.cyan : t.gold}>
                <div style={{ fontSize: "0.55rem", letterSpacing: "0.1em", color: t.muted, textTransform: "uppercase", marginBottom: "0.3rem" }}>{e.role}</div>
                <div style={{ fontSize: "0.78rem", color: t.text, lineHeight: 1.4, ...res }}>{e.name}</div>
              </AsideBox>
            ))}
          </div>

          {/* ── W — Window ────────────────────────────────────────────────── */}
          <SectionAnchor id="window" />
          <SectionHead label="W — Window" />
          <div style={{ display: "flex", gap: "0.75rem", marginBottom: "2rem", flexWrap: "wrap" }}>
            {[
              { label: "Acute", detail: "3–7 days — wait for recruiter/HM feedback", color: t.red },
              { label: "Medium", detail: "2–4 weeks — assessment + case study if proceeding", color: t.gold },
              { label: "Hard constraint", detail: "Deloitte + JPMorgan pipelines active now", color: t.muted },
            ].map((w, i) => (
              <AsideBox key={i} color={w.color}>
                <div style={{ fontSize: "0.58rem", letterSpacing: "0.1em", color: w.color, textTransform: "uppercase", fontWeight: 700, marginBottom: "0.3rem" }}>{w.label}</div>
                <div style={{ fontSize: "0.73rem", color: t.text, lineHeight: 1.4, ...res }}>{w.detail}</div>
              </AsideBox>
            ))}
          </div>

          {/* ── Y-Gate ────────────────────────────────────────────────────── */}
          <SectionAnchor id="ygate" />
          <SectionHead label="Y-Gate · Conviction Shift" />
          <div style={{ display: "flex", gap: "1rem", marginBottom: "1.25rem", flexWrap: "wrap" }}>
            <AsideBox color={t.green}>
              <div style={{ fontSize: "0.58rem", color: t.muted, textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: "0.3rem" }}>Pre-call</div>
              <div style={{ fontSize: "0.82rem", color: t.green, fontWeight: 600 }}>GREEN / HIGH / STABLE</div>
              <div style={{ fontSize: "0.72rem", color: t.dimmed }}>NCI 72</div>
            </AsideBox>
            <AsideBox color={t.gold}>
              <div style={{ fontSize: "0.58rem", color: t.muted, textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: "0.3rem" }}>Post-call</div>
              <div style={{ fontSize: "0.82rem", color: t.gold, fontWeight: 600 }}>YELLOW / MEDIUM / WATCH</div>
              <div style={{ fontSize: "0.72rem", color: t.dimmed }}>NCI 58 · Δ −14</div>
            </AsideBox>
          </div>
          <p style={{ fontSize: "0.78rem", color: t.dimmed, lineHeight: 1.6, marginBottom: "0.5rem" }}>
            <strong style={{ color: t.text, ...res }}>What moved the gate down:</strong> No-AI assessment is a genuine blocker. Role sits formally in data science — strategic latitude may be bounded. Recruiter openly uncertain about path forward. Two active alternatives at stronger pipeline stages.
          </p>
          <p style={{ fontSize: "0.78rem", color: t.dimmed, lineHeight: 1.6, marginBottom: "2rem" }}>
            <strong style={{ color: t.text, ...res }}>What held it from RED:</strong> Caitlin's proactive sourcing is a real signal. Recruiter committed to HM consult + alt role exploration.
          </p>

          {/* ── Signal Delta ──────────────────────────────────────────────── */}
          <SectionAnchor id="delta" />
          <SectionHead label="Signal Delta — Expected vs. Actual" />
          <div style={{ overflowX: "auto", marginBottom: "2rem" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.76rem" }}>
              <thead>
                <tr style={{ borderBottom: `1px solid ${t.border}` }}>
                  {["Signal", "Expected", "Actual", "Δ"].map((h, i) => (
                    <th key={i} style={{ padding: "0.5rem 1rem 0.5rem " + (i === 0 ? "0" : "1rem"), textAlign: "left", fontSize: "0.56rem", letterSpacing: "0.14em", color: t.muted, textTransform: "uppercase", fontWeight: 600, whiteSpace: "nowrap" }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {SIGNAL_DELTAS.map((row, i) => (
                  <tr key={i} style={{ borderBottom: `1px solid ${t.border}` }}>
                    <td style={{ padding: "0.7rem 1rem 0.7rem 0", color: t.text, fontWeight: 500, whiteSpace: "nowrap", ...res }}>{row.signal}</td>
                    <td style={{ padding: "0.7rem 1rem", color: t.dimmed, lineHeight: 1.5, maxWidth: 200 }}>{row.expected}</td>
                    <td style={{ padding: "0.7rem 1rem", color: t.text, lineHeight: 1.5, maxWidth: 240, ...res }}>{row.actual}</td>
                    <td style={{ padding: "0.7rem 0 0.7rem 1rem", whiteSpace: "nowrap" }}><Chip label={row.delta} color={row.dc} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* ── Ex-Ante Receipt ───────────────────────────────────────────── */}
          <SectionAnchor id="receipt" />
          <SectionHead label="Ex-Ante Receipt" />
          <div style={{ background: t.surface, border: `1px solid ${t.gold}`, borderRadius: 8, padding: "1.5rem", marginBottom: "2rem" }}>
            <div style={{ display: "flex", gap: "0.5rem", marginBottom: "1rem", alignItems: "center" }}>
              <Chip label="HOLD" color={t.gold} solid />
              <span style={{ fontSize: "0.7rem", color: t.dimmed }}>Zero-cost option preservation</span>
            </div>
            <p style={{ fontSize: "0.85rem", color: t.text, lineHeight: 1.7, marginBottom: "1rem", ...res }}>
              The bet on the table: 8–15 hours in Figma's assessment + case study pipeline vs. redirecting energy to Deloitte/JPMorgan which are further along and frictionless.
            </p>
            <p style={{ fontSize: "0.78rem", color: t.dimmed, lineHeight: 1.6, marginBottom: "1.25rem" }}>
              Do not invest assessment bandwidth until recruiter returns with HM's position on coding assessment flexibility and whether alternative roles exist outside data science.
            </p>
            <div style={{ borderTop: `1px solid ${t.border}`, paddingTop: "1rem" }}>
              <div style={{ fontSize: "0.58rem", letterSpacing: "0.12em", color: t.muted, textTransform: "uppercase", marginBottom: "0.625rem" }}>Unlock conditions</div>
              <div style={{ display: "flex", flexDirection: "column", gap: "0.4rem" }}>
                {["HM's position on coding assessment flexibility (AI tools or structure change)", "Whether alternative roles exist outside data science (strategy/ops, Dylan's team)"].map((c, i) => (
                  <div key={i} style={{ display: "flex", gap: "0.5rem" }}>
                    <span style={{ color: t.gold, fontSize: "0.7rem", marginTop: "0.1rem" }}>◇</span>
                    <span style={{ fontSize: "0.77rem", color: t.text, lineHeight: 1.5, ...res }}>{c}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* ── Confidence Scores ─────────────────────────────────────────── */}
          <SectionAnchor id="confidence" />
          <SectionHead label="Confidence Scores" />
          <div style={{ marginBottom: "2rem" }}>
            {CONFIDENCE.map((c, i) => <ConfidenceBar key={i} {...c} />)}
            <AsideBox color={t.red}>
              <p style={{ fontSize: "0.72rem", color: t.red, lineHeight: 1.5 }}>
                40% confidence on "time well-spent vs. alternatives" is below the HOLD threshold. The bet does not clear the survivability bar at current information state.
              </p>
            </AsideBox>
          </div>

          {/* ── Survivable Next Steps ─────────────────────────────────────── */}
          <SectionAnchor id="nextsteps" />
          <SectionHead label="Survivable Next Steps" />
          <div style={{ display: "flex", flexDirection: "column", gap: "0.875rem", marginBottom: "2rem" }}>
            {NEXT_STEPS.map((step) => (
              <div key={step.n} style={{ display: "flex", gap: "1rem", alignItems: "flex-start" }}>
                <div style={{ flexShrink: 0, width: 32, height: 32, borderRadius: "50%", border: `1px solid ${step.color}`, display: "flex", alignItems: "center", justifyContent: "center" }}>
                  <span style={{ fontSize: "0.68rem", color: step.color, fontWeight: 700 }}>{step.n}</span>
                </div>
                <div style={{ flex: 1, paddingTop: "0.25rem" }}>
                  <div style={{ display: "flex", gap: "0.5rem", alignItems: "center", marginBottom: "0.3rem" }}>
                    <span style={{ fontSize: "0.65rem", letterSpacing: "0.1em", color: step.color, fontWeight: 700 }}>{step.label}</span>
                    <span style={{ fontSize: "0.58rem", color: t.muted }}>rev {step.rev}/10</span>
                  </div>
                  <p style={{ fontSize: "0.78rem", color: t.text, lineHeight: 1.5, ...res }}>{step.body}</p>
                </div>
              </div>
            ))}
          </div>

          {/* ── Recoil Analysis ───────────────────────────────────────────── */}
          <SectionAnchor id="analysis" />
          <SectionHead label="Recoil Analysis" />
          <p style={{ fontSize: "0.85rem", color: t.text, lineHeight: 1.75, marginBottom: "1rem", ...res }}>
            The call confirmed the role shape hypothesis almost exactly. The "Code" org as a net-new cross-functional layer — straddling product, engineering, design, and roadmap influence across Dev Mode, Code Connect, and MCP — is precisely the kind of inflection-point surface worth engaging. Caitlin's proactive LinkedIn sourcing is not noise; it means the fit signal is real from the hiring side.
          </p>
          <p style={{ fontSize: "0.85rem", color: t.text, lineHeight: 1.75, marginBottom: "1rem", ...res }}>
            The process friction is the only genuine blocker. The recruiter acknowledged it directly:
          </p>
          <QuoteBlock>
            "We're at this crossroads where we don't allow AI tools in the interview process and yet we talk to so many people who say this is my everyday."
          </QuoteBlock>
          <p style={{ fontSize: "0.85rem", color: t.text, lineHeight: 1.75, marginBottom: "1rem", ...res }}>
            That sentence means the policy is in transition — not a fixed wall. The risk is investing 8–15 hours in a traditional coding assessment that produces a false negative for both sides.
          </p>
          <p style={{ fontSize: "0.85rem", color: t.text, lineHeight: 1.75, marginBottom: "1rem", ...res }}>
            Secondary watch: formal data science org placement may constrain strategic latitude. A strategy/ops path or different team might be a stronger surface match — worth surfacing explicitly in the follow-up.
          </p>
          <AsideBox color={t.gold}>
            <p style={{ fontSize: "0.82rem", color: t.gold, lineHeight: 1.65, fontWeight: 500 }}>
              At 40% confidence on "time well-spent vs. alternatives," the answer is HOLD. Not reject, not proceed. Wait for the information that changes the probability tree.
            </p>
          </AsideBox>
          <div style={{ height: "2rem" }} />

          {/* ── Drift Sentinel ────────────────────────────────────────────── */}
          <SectionAnchor id="sentinel" />
          <SectionHead label="Drift Sentinel" />
          <div style={{ display: "flex", gap: "1rem", marginBottom: "2rem", flexWrap: "wrap" }}>
            <AsideBox color={t.green}>
              <div style={{ display: "flex", gap: "0.5rem", alignItems: "center", marginBottom: "0.3rem" }}>
                <span style={{ width: 7, height: 7, borderRadius: "50%", background: t.green, display: "inline-block" }} />
                <span style={{ fontSize: "0.72rem", color: t.green, fontWeight: 700, letterSpacing: "0.08em" }}>CLEAR</span>
              </div>
              <p style={{ fontSize: "0.7rem", color: t.dimmed }}>1 session · 1 new artifact. No spin cycle.</p>
            </AsideBox>
            <AsideBox color={t.muted}>
              <div style={{ fontSize: "0.58rem", color: t.muted, textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: "0.3rem" }}>Open Questions</div>
              <div style={{ display: "flex", flexDirection: "column", gap: "0.3rem" }}>
                {["Will Caitlin approve AI tools or restructure the assessment?", "Are there open recs outside data science?", "What does Figma's senior IC path look like in Code?"].map((q, i) => (
                  <div key={i} style={{ display: "flex", gap: "0.4rem" }}>
                    <span style={{ color: t.gold, fontSize: "0.65rem" }}>?</span>
                    <span style={{ fontSize: "0.7rem", color: t.text, lineHeight: 1.4, ...res }}>{q}</span>
                  </div>
                ))}
              </div>
            </AsideBox>
          </div>

          {/* Footer */}
          <div style={{ borderTop: `1px solid ${t.border}`, paddingTop: "1.25rem", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span style={{ fontSize: "0.58rem", color: t.dimmed, letterSpacing: "0.08em" }}>ARCS FIELD OS · ORIENT SURFACE · ARCS-ORIENT-2026-06-08T14:30:00Z-figma-r001</span>
            <span style={{ fontSize: "0.58rem", color: t.dimmed, letterSpacing: "0.08em" }}>W: ACUTE · Jun 8–16, 2026</span>
          </div>

        </main>
      </div>
    </div>
  )
}
