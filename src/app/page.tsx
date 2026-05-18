"use client"

import { useRouter } from "next/navigation"

const STEPS = [
  {
    n: "01",
    title: "State the decision",
    body: "Type what you're actually trying to decide — not the symptom, the real fork. Set horizon and stakes.",
  },
  {
    n: "02",
    title: "Compass runs L0–L5",
    body: "Six pipeline layers in parallel: activation filter, adversarial challenge, Bayesian validation, Kintsugi immune check, NCI scoring, synthesis.",
  },
  {
    n: "03",
    title: "Receive True North",
    body: "One actionable sentence. Conviction grade. Render resolution calibrated to how certain the terrain actually is.",
  },
  {
    n: "04",
    title: "Cartography brief",
    body: "Situation framing, FATED decomposition, terrain paths, and tributaries — the full map of where you stand.",
  },
]

const s = {
  bg: "#020408", surface: "#0d1117", border: "#1e293b",
  text: "#e2e8f0", muted: "#475569", dimmed: "#64748b",
  cyan: "#00F0FF", green: "#00FF9D", gold: "#FFD700", red: "#FF4D6D",
}

export default function HomePage() {
  const router = useRouter()

  return (
    <main style={{ minHeight: "100vh", background: s.bg, color: s.text, fontFamily: "'Inter', sans-serif" }}>
      <div style={{ maxWidth: 740, margin: "0 auto", padding: "4rem 1.5rem" }}>

        {/* Nav */}
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "5rem" }}>
          <span style={{ fontSize: "0.65rem", letterSpacing: "0.15em", color: s.cyan, textTransform: "uppercase", fontWeight: 600 }}>
            ARCS FIELD OS
          </span>
          <div style={{ display: "flex", gap: "0.5rem" }}>
            <button
              onClick={() => router.push("/prep")}
              style={{ background: "transparent", border: `1px solid ${s.border}`, borderRadius: 6, color: s.muted, fontSize: "0.75rem", padding: "0.375rem 0.875rem", cursor: "pointer" }}
            >
              Calibrate first
            </button>
            <button
              onClick={() => router.push("/dashboard")}
              style={{ background: "transparent", border: `1px solid ${s.cyan}55`, borderRadius: 6, color: s.cyan, fontSize: "0.75rem", padding: "0.375rem 0.875rem", cursor: "pointer" }}
            >
              Open compass →
            </button>
          </div>
        </div>

        {/* Hero */}
        <div style={{ marginBottom: "5rem" }}>
          <div style={{ fontSize: "0.65rem", color: s.muted, letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: "1.25rem" }}>
            Navigate to clarity · Render through the fog
          </div>
          <h1 style={{ fontSize: "clamp(2rem, 5vw, 3rem)", fontWeight: 600, lineHeight: 1.15, color: s.text, margin: "0 0 1.5rem", letterSpacing: "-0.02em" }}>
            What are you really<br />trying to decide?
          </h1>
          <p style={{ fontSize: "1.0625rem", color: s.dimmed, lineHeight: 1.75, maxWidth: 520, margin: "0 0 2.5rem" }}>
            ARCS is a boardroom-grade decision intelligence layer. It maps the terrain, grades conviction, and renders clarity at the fidelity the data actually deserves.
          </p>
          <div style={{ display: "flex", gap: "0.875rem", flexWrap: "wrap" }}>
            <button
              onClick={() => router.push("/dashboard")}
              style={{ padding: "0.75rem 1.75rem", borderRadius: 8, background: s.cyan, color: s.bg, fontWeight: 700, fontSize: "0.875rem", border: "none", cursor: "pointer", letterSpacing: "0.04em" }}
            >
              Run the compass →
            </button>
            <button
              onClick={() => document.getElementById("how")?.scrollIntoView({ behavior: "smooth" })}
              style={{ padding: "0.75rem 1.5rem", borderRadius: 8, background: "transparent", border: `1px solid ${s.border}`, color: s.muted, fontSize: "0.875rem", cursor: "pointer" }}
            >
              How it works
            </button>
          </div>
        </div>

        {/* Demo receipt */}
        <div style={{ padding: "1.5rem", background: s.surface, border: `1px solid ${s.border}`, borderRadius: 12, marginBottom: "5rem" }}>
          <div style={{ fontSize: "0.6rem", color: s.muted, letterSpacing: "0.12em", textTransform: "uppercase", marginBottom: "1rem" }}>
            Example · Decision Receipt
          </div>
          <div style={{ fontSize: "0.75rem", color: s.dimmed, marginBottom: "0.5rem", textTransform: "uppercase", letterSpacing: "0.08em" }}>Decision under navigation</div>
          <div style={{ fontSize: "0.9375rem", color: s.text, marginBottom: "1.25rem", lineHeight: 1.5 }}>
            Should I take the Series A now or extend runway another 6 months and grow into a higher valuation?
          </div>
          <div style={{ padding: "1rem 1.25rem", background: "#020408", border: `1px solid ${s.cyan}33`, borderRadius: 8, marginBottom: "1rem" }}>
            <div style={{ fontSize: "0.6rem", color: s.cyan, letterSpacing: "0.12em", textTransform: "uppercase", marginBottom: "0.5rem", fontWeight: 600 }}>True North · COURT · ONE_WAY</div>
            <div style={{ fontSize: "0.9375rem", color: s.text, lineHeight: 1.6, fontWeight: 500 }}>
              Extend runway — the valuation delta at your current growth rate outweighs the optionality cost of 6 months.
            </div>
          </div>
          <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap" }}>
            <div style={{ padding: "0.5rem 0.875rem", background: "#00FF9D15", border: "1px solid #00FF9D33", borderRadius: 6 }}>
              <span style={{ fontSize: "0.6rem", color: s.muted, textTransform: "uppercase", letterSpacing: "0.08em" }}>NCI </span>
              <span style={{ fontSize: "0.875rem", fontWeight: 700, color: s.green }}>74</span>
            </div>
            <div style={{ padding: "0.5rem 0.875rem", background: "#00FF9D0D", border: "1px solid #00FF9D22", borderRadius: 6 }}>
              <span style={{ fontSize: "0.6rem", color: s.green, textTransform: "uppercase", letterSpacing: "0.08em", fontWeight: 600 }}>▲ CLARITY RIDGE</span>
            </div>
            <div style={{ padding: "0.5rem 0.875rem", background: s.border, borderRadius: 6 }}>
              <span style={{ fontSize: "0.65rem", color: s.dimmed, fontWeight: 600 }}>KKL</span>
            </div>
            <div style={{ padding: "0.5rem 0.875rem", background: s.border, borderRadius: 6 }}>
              <span style={{ fontSize: "0.65rem", color: s.dimmed, fontWeight: 600 }}>ONE_WAY</span>
            </div>
          </div>
        </div>

        {/* How it works */}
        <div id="how" style={{ marginBottom: "5rem" }}>
          <div style={{ fontSize: "0.65rem", color: s.muted, letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: "2rem" }}>
            How it works
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
            {STEPS.map(step => (
              <div key={step.n} style={{ display: "flex", gap: "1.25rem", alignItems: "flex-start" }}>
                <div style={{ fontSize: "0.65rem", color: s.cyan, fontWeight: 700, letterSpacing: "0.1em", minWidth: 24, paddingTop: "0.1rem" }}>
                  {step.n}
                </div>
                <div>
                  <div style={{ fontSize: "0.875rem", fontWeight: 600, color: s.text, marginBottom: "0.25rem" }}>{step.title}</div>
                  <div style={{ fontSize: "0.825rem", color: s.dimmed, lineHeight: 1.65 }}>{step.body}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* CTA footer */}
        <div style={{ paddingTop: "2rem", borderTop: `1px solid ${s.border}`, display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: "1rem" }}>
          <span style={{ fontSize: "0.8rem", color: s.muted }}>Render through the fog to earned clarity.</span>
          <button
            onClick={() => router.push("/dashboard")}
            style={{ padding: "0.625rem 1.5rem", borderRadius: 8, background: "transparent", border: `1px solid ${s.cyan}55`, color: s.cyan, fontSize: "0.8rem", fontWeight: 600, cursor: "pointer", letterSpacing: "0.04em" }}
          >
            Open compass →
          </button>
        </div>

      </div>
    </main>
  )
}
