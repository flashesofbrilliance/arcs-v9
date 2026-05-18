"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"

type Stakes  = "LOW" | "MEDIUM" | "HIGH"
type Horizon = "TODAY" | "THIS_WEEK" | "THIS_QUARTER" | "ONE_TO_THREE_YEARS"

const PROTECT_CHIPS = ["Cash", "Time", "Reputation", "Relationship", "Health", "Optionality"]

const STAKES: { value: Stakes; label: string; color: string }[] = [
  { value: "LOW",    label: "Survivable",   color: "#00FF9D" },
  { value: "MEDIUM", label: "Significant",  color: "#FFD700" },
  { value: "HIGH",   label: "Irreversible", color: "#FF4D6D" },
]

const HORIZONS: { value: Horizon; label: string }[] = [
  { value: "TODAY",              label: "Today" },
  { value: "THIS_WEEK",         label: "This week" },
  { value: "THIS_QUARTER",      label: "This quarter" },
  { value: "ONE_TO_THREE_YEARS",label: "1–3 years" },
]

const s = {
  bg: "#020408", surface: "#0d1117", border: "#1e293b",
  text: "#e2e8f0", muted: "#475569", dimmed: "#64748b",
  cyan: "#00F0FF", green: "#00FF9D", gold: "#FFD700", red: "#FF4D6D",
}

export default function PrepPage() {
  const router = useRouter()

  const [stakes,     setStakes]     = useState<Stakes>("MEDIUM")
  const [horizon,    setHorizon]    = useState<Horizon>("THIS_WEEK")
  const [protecting, setProtecting] = useState<string[]>([])
  const [confidence, setConfidence] = useState(3)
  const [entity,     setEntity]     = useState("")
  const [adversarial,setAdversarial]= useState("")
  const [loading,    setLoading]    = useState(false)

  function toggleProtect(chip: string) {
    setProtecting(p =>
      p.includes(chip) ? p.filter(c => c !== chip)
      : p.length < 2   ? [...p, chip]
      : p
    )
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    try {
      const res = await fetch("/api/prep", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          stakes, horizon, protecting, confidence,
          entity: entity.trim() || null,
          adversarialInput: adversarial.trim() || null,
        }),
      })
      const { prep_id } = await res.json()
      router.push(`/dashboard?prepId=${prep_id}`)
    } catch {
      setLoading(false)
    }
  }

  const activeStake = STAKES.find(s => s.value === stakes)!

  return (
    <main style={{ minHeight: "100vh", background: s.bg, color: s.text, fontFamily: "'Inter', sans-serif" }}>
      <div style={{ maxWidth: 520, margin: "0 auto", padding: "3rem 1.5rem 4rem" }}>

        {/* Header */}
        <div style={{ marginBottom: "2.5rem" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", marginBottom: "1.25rem" }}>
            <button
              onClick={() => router.push("/")}
              style={{ background: "transparent", border: "none", color: s.muted, fontSize: "0.75rem", cursor: "pointer", padding: 0 }}
            >
              ← ARCS
            </button>
          </div>
          <h1 style={{ fontSize: "1.375rem", fontWeight: 600, color: s.text, margin: "0 0 0.5rem", lineHeight: 1.3 }}>
            2 minutes. Sharper terrain.
          </h1>
          <p style={{ fontSize: "0.825rem", color: s.muted, margin: 0, lineHeight: 1.6 }}>
            These signals tell the compass which mode to run, what to protect, and who else is in the terrain.
          </p>
        </div>

        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "2rem" }}>

          {/* Stakes */}
          <div>
            <div style={{ fontSize: "0.825rem", fontWeight: 600, color: s.text, marginBottom: "0.75rem" }}>
              How bad if this goes wrong?
            </div>
            <div style={{ display: "flex", gap: "0.5rem" }}>
              {STAKES.map(st => (
                <button
                  key={st.value}
                  type="button"
                  onClick={() => setStakes(st.value)}
                  style={{
                    flex: 1, padding: "0.625rem 0", fontSize: "0.8rem", fontWeight: 600,
                    borderRadius: 8, border: "1px solid",
                    borderColor: stakes === st.value ? st.color : s.border,
                    background: stakes === st.value ? `${st.color}12` : "transparent",
                    color: stakes === st.value ? st.color : s.muted,
                    cursor: "pointer", transition: "all 0.15s",
                  }}
                >
                  {st.label}
                </button>
              ))}
            </div>
          </div>

          {/* Horizon */}
          <div>
            <div style={{ fontSize: "0.825rem", fontWeight: 600, color: s.text, marginBottom: "0.75rem" }}>
              When does this land?
            </div>
            <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
              {HORIZONS.map(h => (
                <button
                  key={h.value}
                  type="button"
                  onClick={() => setHorizon(h.value)}
                  style={{
                    padding: "0.5rem 0.875rem", fontSize: "0.8rem", borderRadius: 8, border: "1px solid",
                    borderColor: horizon === h.value ? s.cyan : s.border,
                    background: horizon === h.value ? `${s.cyan}12` : "transparent",
                    color: horizon === h.value ? s.cyan : s.muted,
                    cursor: "pointer", transition: "all 0.15s",
                  }}
                >
                  {h.label}
                </button>
              ))}
            </div>
          </div>

          {/* Protecting — fixed 3-col grid so chips never orphan */}
          <div>
            <div style={{ display: "flex", alignItems: "baseline", justifyContent: "space-between", marginBottom: "0.75rem" }}>
              <div style={{ fontSize: "0.825rem", fontWeight: 600, color: s.text }}>
                What can&apos;t you afford to lose?
              </div>
              <div style={{ fontSize: "0.7rem", color: protecting.length === 2 ? s.green : s.muted }}>
                {protecting.length}/2 selected
              </div>
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "0.5rem" }}>
              {PROTECT_CHIPS.map(chip => {
                const active = protecting.includes(chip)
                const maxed  = protecting.length >= 2 && !active
                return (
                  <button
                    key={chip}
                    type="button"
                    disabled={maxed}
                    onClick={() => toggleProtect(chip)}
                    style={{
                      padding: "0.5rem 0", fontSize: "0.775rem", borderRadius: 6, border: "1px solid",
                      borderColor: active ? s.green : maxed ? `${s.border}44` : s.border,
                      background: active ? `${s.green}12` : "transparent",
                      color: active ? s.green : maxed ? `${s.muted}33` : s.muted,
                      cursor: maxed ? "not-allowed" : "pointer", transition: "all 0.15s",
                      textAlign: "center",
                    }}
                  >
                    {chip}
                  </button>
                )
              })}
            </div>
          </div>

          {/* Confidence — discrete 5-step dots below track */}
          <div>
            <div style={{ display: "flex", alignItems: "baseline", justifyContent: "space-between", marginBottom: "0.75rem" }}>
              <div style={{ fontSize: "0.825rem", fontWeight: 600, color: s.text }}>
                How sure were you before you came here?
              </div>
              <div style={{
                fontSize: "0.75rem", fontWeight: 700,
                color: confidence <= 2 ? s.red : confidence >= 4 ? s.green : s.gold,
              }}>
                {["", "Lost", "Uncertain", "Mixed", "Leaning", "Confirming"][confidence]}
              </div>
            </div>
            <input
              type="range" min={1} max={5} value={confidence}
              onChange={e => setConfidence(Number(e.target.value))}
              style={{ width: "100%", accentColor: activeStake.color, marginBottom: "0.5rem" }}
            />
            <div style={{ display: "flex", justifyContent: "space-between", paddingLeft: "2px", paddingRight: "2px" }}>
              {["Lost", "Uncertain", "Mixed", "Leaning", "Confirming"].map((label, i) => (
                <span
                  key={label}
                  onClick={() => setConfidence(i + 1)}
                  style={{
                    fontSize: "0.6rem", color: confidence === i + 1 ? activeStake.color : s.muted,
                    cursor: "pointer", letterSpacing: "0.02em", transition: "color 0.15s",
                    fontWeight: confidence === i + 1 ? 700 : 400,
                  }}
                >
                  {label}
                </span>
              ))}
            </div>
          </div>

          {/* Divider — optional territory */}
          <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
            <div style={{ flex: 1, height: 1, background: s.border }} />
            <span style={{
              fontSize: "0.6rem", color: "#334155", letterSpacing: "0.12em", textTransform: "uppercase",
              fontWeight: 600,
            }}>
              Optional
            </span>
            <div style={{ flex: 1, height: 1, background: s.border }} />
          </div>

          {/* Entity */}
          <div>
            <div style={{ fontSize: "0.825rem", fontWeight: 600, color: s.text, marginBottom: "0.625rem" }}>
              Who else is in this terrain?
            </div>
            <input
              type="text"
              value={entity}
              onChange={e => setEntity(e.target.value)}
              placeholder="person, company, stakeholder, panel…"
              style={{
                width: "100%", boxSizing: "border-box",
                background: s.surface, border: `1px solid ${s.border}`,
                borderRadius: 8, color: s.text, fontSize: "0.875rem",
                padding: "0.625rem 0.875rem", outline: "none", fontFamily: "inherit",
              }}
            />
            {entity.trim() && (
              <div style={{ marginTop: "0.4rem", fontSize: "0.7rem", color: s.muted }}>
                Populates the entity panel in your cartography brief
              </div>
            )}
          </div>

          {/* Adversarial */}
          <div>
            <div style={{ fontSize: "0.825rem", fontWeight: 600, color: s.text, marginBottom: "0.625rem" }}>
              Strongest case against your instinct
            </div>
            <input
              type="text"
              value={adversarial}
              onChange={e => setAdversarial(e.target.value)}
              placeholder="One sentence. The Loki vector."
              style={{
                width: "100%", boxSizing: "border-box",
                background: s.surface, border: `1px solid ${s.border}`,
                borderRadius: 8, color: s.text, fontSize: "0.875rem",
                padding: "0.625rem 0.875rem", outline: "none", fontFamily: "inherit",
              }}
            />
          </div>

          {/* Submit */}
          {/* Submit — sticky so it's always visible */}
          <div style={{
            position: "sticky", bottom: "1.5rem",
            background: `linear-gradient(to top, ${s.bg} 70%, transparent)`,
            paddingTop: "1rem",
          }}>
            <button
              type="submit"
              disabled={loading}
              style={{
                width: "100%", padding: "0.875rem", borderRadius: 10,
                background: loading ? s.border : activeStake.color,
                color: loading ? s.muted : s.bg,
                fontWeight: 700, fontSize: "0.9rem", border: "none",
                cursor: loading ? "not-allowed" : "pointer",
                letterSpacing: "0.04em", transition: "background 0.2s",
                boxShadow: loading ? "none" : `0 0 24px ${activeStake.color}33`,
              }}
            >
              {loading ? "Loading terrain…" : "Enter the compass →"}
            </button>
          </div>

        </form>
      </div>
    </main>
  )
}
