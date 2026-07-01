"use client"

import { useState, Suspense } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { surface, text, signal, font, border, formContainer } from "@/ui/tokens"
import { useVw } from "@/ui/useVw"
import { Wordmark } from "@/ui/Wordmark"
import { Rule } from "@/ui/Rule"
import { SectionLabel } from "@/ui/SectionLabel"
import { Field } from "@/ui/Field"
import { Picker } from "@/ui/Picker"
import { SegmentedSlider } from "@/ui/SegmentedSlider"
import { CalibrationChips } from "@/molecules/CalibrationChips"
import { Button } from "@/ui/Button"

// Prep — the calibration instrument. Ported to the cockpit design system; keeps
// the /api/prep → /dashboard?prepId contract. Page owns the POST (head/body).

type Stakes = "LOW" | "MEDIUM" | "HIGH"
type Horizon = "TODAY" | "THIS_WEEK" | "THIS_QUARTER" | "ONE_TO_THREE_YEARS"

const STAKE_OPTS = [
  { value: "LOW", label: "Survivable", accent: "green" as const },
  { value: "MEDIUM", label: "Significant", accent: "gold" as const },
  { value: "HIGH", label: "Irreversible", accent: "red" as const },
]
const HORIZON_OPTS = [
  { value: "TODAY", label: "Today" },
  { value: "THIS_WEEK", label: "This week" },
  { value: "THIS_QUARTER", label: "This quarter" },
  { value: "ONE_TO_THREE_YEARS", label: "1–3 years" },
]
const CONF_OPTS = [
  { value: "1", label: "Lost", accent: "red" as const },
  { value: "2", label: "Uncertain", accent: "red" as const },
  { value: "3", label: "Mixed", accent: "gold" as const },
  { value: "4", label: "Leaning", accent: "green" as const },
  { value: "5", label: "Confirming", accent: "green" as const },
]

function PrepInner() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const vw = useVw()
  const [question] = useState(() => searchParams.get("q") ?? "")
  const [stakes, setStakes] = useState<Stakes>("MEDIUM")
  const [horizon, setHorizon] = useState<Horizon>("THIS_WEEK")
  const [protecting, setProtecting] = useState<string[]>([])
  const [confidence, setConfidence] = useState("3")
  const [entity, setEntity] = useState("")
  const [adversarial, setAdversarial] = useState("")
  const [outcomeHorizon, setOutcomeHorizon] = useState("")
  const [loading, setLoading] = useState(false)

  function toggleProtect(chip: string) {
    setProtecting((p) => p.includes(chip) ? p.filter((c) => c !== chip) : p.length < 2 ? [...p, chip] : p)
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    try {
      const res = await fetch("/api/prep", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          stakes, horizon, protecting, confidence: Number(confidence),
          entity: entity.trim() || null,
          adversarialInput: adversarial.trim() || null,
          outcomeHorizon: outcomeHorizon.trim() || null,
        }),
      })
      const { prep_id } = await res.json()
      const q = question.trim() ? `&q=${encodeURIComponent(question)}` : ""
      router.push(`/dashboard?prepId=${prep_id}${q}`)
    } catch {
      setLoading(false)
    }
  }

  const labelStyle = { fontFamily: font.sans, fontSize: "0.825rem", fontWeight: 600, color: text.primary, marginBottom: "0.75rem", display: "block" }

  return (
    <main style={{ minHeight: "100vh", background: surface.bg, color: text.primary }}>
      <div style={{ ...formContainer(vw), paddingTop: "2rem", paddingBottom: "6rem" }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", paddingBottom: "1rem" }}>
          <Wordmark section="Calibrate" />
          <Button variant="ghost" size="sm" glyph="←" onClick={() => router.push(question.trim() ? `/dashboard?q=${encodeURIComponent(question)}` : "/dashboard")}>Compass</Button>
        </div>
        <Rule style={{ marginBottom: "2rem" }} />

        <div style={{ marginBottom: "2rem" }}>
          <h1 style={{ fontFamily: font.sans, fontSize: "1.5rem", fontWeight: 600, color: text.primary, margin: "0 0 0.5rem", lineHeight: 1.25, letterSpacing: "-0.01em" }}>
            2 minutes. Sharper terrain.
          </h1>
          <p style={{ fontFamily: font.sans, fontSize: "0.85rem", color: text.muted, margin: 0, lineHeight: 1.6 }}>
            These signals tell the compass which mode to run, what to protect, and who else is in the terrain.
          </p>
          {question.trim() && (
            <div style={{ marginTop: "1rem", padding: "0.75rem 0.9rem", border: `1px solid ${border.subtle}`, borderRadius: 8, background: surface.elevated }}>
              <span style={{ fontFamily: font.mono, fontSize: "0.6rem", color: signal.gold, letterSpacing: "0.12em", textTransform: "uppercase", fontWeight: 700 }}>Calibrating</span>
              <p style={{ fontFamily: font.sans, fontSize: "0.9rem", color: text.secondary, margin: "0.4rem 0 0", lineHeight: 1.5 }}>{question}</p>
            </div>
          )}
        </div>

        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "1.75rem" }}>
          <div>
            <SectionLabel index="01" style={{ marginBottom: "0.75rem" }}>How bad if this goes wrong?</SectionLabel>
            <SegmentedSlider options={STAKE_OPTS} value={stakes} onChange={(v) => setStakes(v as Stakes)} />
          </div>

          <Picker label="When do you commit?" value={horizon} options={HORIZON_OPTS} onChange={(v) => setHorizon(v as Horizon)} />

          <div>
            <CalibrationChips selected={protecting} onToggle={toggleProtect} />
          </div>

          <div>
            <SectionLabel index="03" style={{ marginBottom: "0.75rem" }}>How sure were you before you came here?</SectionLabel>
            <SegmentedSlider options={CONF_OPTS} value={confidence} onChange={setConfidence} />
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
            <div style={{ flex: 1, height: 1, background: surface.panel }} />
            <span style={{ fontFamily: font.mono, fontSize: "0.6rem", color: text.muted, letterSpacing: "0.12em", textTransform: "uppercase", fontWeight: 700 }}>Optional</span>
            <div style={{ flex: 1, height: 1, background: surface.panel }} />
          </div>

          <Field label="Who else is in this terrain?" value={entity} onChange={(e) => setEntity(e.target.value)} placeholder="person, company, stakeholder, panel…" />
          <Field label="Strongest case against your instinct" value={adversarial} onChange={(e) => setAdversarial(e.target.value)} placeholder="One sentence. The Loki vector." />
          <Field label="When will you know if it worked?" value={outcomeHorizon} onChange={(e) => setOutcomeHorizon(e.target.value)} placeholder="not when you decide — when the outcome shows up: end of Q3, when we close the hire, 30 days…" />

          <div style={{ position: "sticky", bottom: 0, background: surface.bg, borderTop: `0.5px solid ${border.subtle}`, padding: "1rem 0 1.25rem", marginTop: "0.5rem" }}>
            <Button type="submit" variant="primary" size="lg" glyph={loading ? "~" : "⊕"} disabled={loading} style={{ width: "100%" }}>
              {loading ? "Loading terrain…" : <>Enter the compass&nbsp;<span style={{ fontFamily: font.sans, fontWeight: 500, opacity: 0.75 }}>→</span></>}
            </Button>
          </div>
        </form>
      </div>
    </main>
  )
}

export default function PrepPage() {
  return (
    <Suspense fallback={<main style={{ minHeight: "100vh", background: surface.bg }} />}>
      <PrepInner />
    </Suspense>
  )
}
