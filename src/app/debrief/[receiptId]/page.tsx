// Debrief surface — closes the receipt loop (Book II Part V §5.6).
// Reached from the debrief email's "Log how it landed →" CTA N days after T₀.
// Reflects the original bearing back, then takes the one signal that closes a
// receipt: what actually happened. Writes an Outcome, flips status → LOGGED.
"use client"

import { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { surface, text, signal, font, nciColor, contentContainer } from "@/ui/tokens"
import { useVw } from "@/ui/useVw"
import { Card } from "@/ui/Card"
import { Button } from "@/ui/Button"
import { SectionLabel } from "@/ui/SectionLabel"

interface ReceiptRecap {
  id: string
  question: string
  trueNorth: string
  nci: number
  mode: string
  door: string | null
  protecting: string[]
  createdAt: string
  status: string
  driftState: string | null
}
interface LoggedOutcome {
  what: string
  matched: boolean
  regretScore: number
  learning: string | null
  loggedAt: string
}

// 1–5 regret scale, stored as the integer index.
const REGRET = [
  { v: 1, label: "None" },
  { v: 2, label: "A little" },
  { v: 3, label: "Mixed" },
  { v: 4, label: "A lot" },
  { v: 5, label: "Deep" },
]

function daysSince(iso: string): number {
  return Math.max(1, Math.round((Date.now() - new Date(iso).getTime()) / 86400000))
}

export default function DebriefPage() {
  const params = useParams()
  const router = useRouter()
  const receiptId = String(params.receiptId)
  const vw = useVw()

  const [recap, setRecap] = useState<ReceiptRecap | null>(null)
  const [logged, setLogged] = useState<LoggedOutcome | null>(null)
  const [error, setError] = useState<string | null>(null)

  // form state
  const [matched, setMatched] = useState<boolean | null>(null)
  const [what, setWhat] = useState("")
  const [regret, setRegret] = useState<number | null>(null)
  const [learning, setLearning] = useState("")
  const [submitting, setSubmitting] = useState(false)
  const [done, setDone] = useState<{ driftState: string } | null>(null)

  useEffect(() => {
    let cancelled = false
    fetch(`/api/receipts/${receiptId}/outcome`)
      .then(async (r) => ({ ok: r.ok, data: await r.json() }))
      .then(({ ok, data }) => {
        if (cancelled) return
        if (!ok) { setError(data.error ?? "Could not load receipt"); return }
        setRecap(data.receipt)
        if (data.outcome) setLogged(data.outcome)
      })
      .catch(() => { if (!cancelled) setError("Could not load receipt") })
    return () => { cancelled = true }
  }, [receiptId])

  async function submit() {
    if (matched == null || !what.trim() || regret == null) return
    setSubmitting(true)
    try {
      const res = await fetch(`/api/receipts/${receiptId}/outcome`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ matched, what: what.trim(), regretScore: regret, learning: learning.trim() || null }),
      })
      const d = await res.json()
      if (res.ok && d.ok) setDone({ driftState: d.driftState })
      else setError(d.error ?? "Could not save outcome")
    } catch {
      setError("Could not save outcome")
    } finally {
      setSubmitting(false)
    }
  }

  const shell = (children: React.ReactNode) => (
    <main style={{ minHeight: "100vh", background: surface.bg, color: text.primary }}>
      {/* breadcrumb */}
      <div style={{ borderBottom: `0.5px solid rgba(255,215,0,0.12)`, background: "rgba(255,215,0,0.03)" }}>
        <div style={{ ...contentContainer(vw), paddingTop: "0.6rem", paddingBottom: "0.6rem", display: "flex", alignItems: "center", gap: "0.75rem" }}>
          <button onClick={() => router.push("/history")} style={{ background: "none", border: "none", cursor: "pointer", fontFamily: font.mono, fontSize: "0.6rem", letterSpacing: "0.1em", color: text.dimmed, textTransform: "uppercase", padding: 0 }}>Ledger</button>
          <span style={{ color: text.dimmed, fontFamily: font.mono, fontSize: "0.6rem" }}>·</span>
          <button onClick={() => router.push(`/brief/${receiptId}`)} style={{ background: "none", border: "none", cursor: "pointer", fontFamily: font.mono, fontSize: "0.6rem", letterSpacing: "0.1em", color: text.dimmed, textTransform: "uppercase", padding: 0 }}>Brief</button>
          <span style={{ color: signal.gold, fontFamily: font.mono, fontSize: "0.6rem" }}>·</span>
          <span style={{ fontFamily: font.mono, fontSize: "0.6rem", letterSpacing: "0.1em", color: signal.gold, textTransform: "uppercase" }}>◰ Debrief</span>
        </div>
      </div>
      <div style={{ ...contentContainer(vw), paddingTop: "1.75rem", paddingBottom: "5rem" }}>{children}</div>
    </main>
  )

  if (error) return shell(<div style={{ fontFamily: font.sans, color: signal.red, fontSize: "0.9rem" }}>{error}</div>)
  if (!recap) return shell(<div style={{ fontFamily: font.mono, fontSize: "0.75rem", color: text.dimmed, letterSpacing: "0.08em" }}>Loading the call you logged…</div>)

  const days = daysSince(recap.createdAt)

  // ── Bearing recap (always shown) ──────────────────────────────────────────
  const recapCard = (
    <Card accent={signal.gold} style={{ marginBottom: "1.5rem" }}>
      <div style={{ fontFamily: font.mono, fontSize: "0.6rem", letterSpacing: "0.16em", textTransform: "uppercase", color: text.dimmed, marginBottom: "0.85rem" }}>
        The call you logged · {days} day{days === 1 ? "" : "s"} ago
      </div>
      <div style={{ fontFamily: font.mono, fontSize: "0.55rem", letterSpacing: "0.16em", textTransform: "uppercase", color: text.muted, marginBottom: "0.4rem" }}>The question</div>
      <div style={{ fontFamily: font.sans, fontSize: "0.95rem", color: text.primary, lineHeight: 1.6, marginBottom: "1rem", maxWidth: "100%", wordWrap: "break-word" }}>{recap.question}</div>
      <div style={{ fontFamily: font.mono, fontSize: "0.55rem", letterSpacing: "0.16em", textTransform: "uppercase", color: text.muted, marginBottom: "0.4rem" }}>True North · the bearing we set</div>
      <div style={{ fontFamily: font.sans, fontSize: "1.05rem", color: signal.cyan, lineHeight: 1.6, marginBottom: "1rem", maxWidth: "100%", wordWrap: "break-word" }}>{recap.trueNorth}</div>
      <div style={{ display: "flex", flexWrap: "wrap", gap: "1.25rem", paddingTop: "0.75rem", borderTop: `0.5px solid ${signal.cyan}1a` }}>
        <div>
          <div style={{ fontFamily: font.mono, fontSize: "0.55rem", letterSpacing: "0.14em", textTransform: "uppercase", color: text.muted, marginBottom: "0.25rem" }}>Conviction</div>
          <div style={{ fontFamily: font.mono, fontSize: "1rem", fontWeight: 700, color: nciColor(recap.nci) }}>{recap.nci}<span style={{ color: text.muted, fontWeight: 400 }}>/100</span></div>
        </div>
        {recap.mode && (
          <div>
            <div style={{ fontFamily: font.mono, fontSize: "0.55rem", letterSpacing: "0.14em", textTransform: "uppercase", color: text.muted, marginBottom: "0.25rem" }}>Mode</div>
            <div style={{ fontFamily: font.mono, fontSize: "0.85rem", fontWeight: 700, color: text.secondary }}>{recap.mode}</div>
          </div>
        )}
        {recap.protecting.length > 0 && (
          <div>
            <div style={{ fontFamily: font.mono, fontSize: "0.55rem", letterSpacing: "0.14em", textTransform: "uppercase", color: text.muted, marginBottom: "0.25rem" }}>Protecting</div>
            <div style={{ fontFamily: font.mono, fontSize: "0.85rem", fontWeight: 700, color: signal.gold }}>{recap.protecting.join(" · ")}</div>
          </div>
        )}
      </div>
    </Card>
  )

  // ── Already closed (logged earlier, or just now) ──────────────────────────
  if (logged || done) {
    const o = logged
    const drift = done?.driftState ?? recap.driftState ?? (o?.matched ? "LANDED" : "DRIFTING")
    const driftColor = drift === "LANDED" ? signal.green : signal.gold
    return shell(
      <>
        {recapCard}
        <Card accent={driftColor}>
          <div style={{ fontFamily: font.mono, fontSize: "0.6rem", letterSpacing: "0.16em", textTransform: "uppercase", color: driftColor, marginBottom: "0.85rem" }}>
            ◉ Receipt closed · {drift}
          </div>
          {done && !o ? (
            <div style={{ fontFamily: font.sans, fontSize: "0.95rem", color: text.secondary, lineHeight: 1.6 }}>
              The loop is complete. This call now feeds the pattern layer — the next decision starts from clearer ground.
            </div>
          ) : o ? (
            <>
              <div style={{ fontFamily: font.mono, fontSize: "0.55rem", letterSpacing: "0.16em", textTransform: "uppercase", color: text.muted, marginBottom: "0.4rem" }}>What happened</div>
              <div style={{ fontFamily: font.sans, fontSize: "0.95rem", color: text.primary, lineHeight: 1.6, marginBottom: "1rem" }}>{o.what}</div>
              <div style={{ display: "flex", gap: "1.5rem", marginBottom: o.learning ? "1rem" : 0 }}>
                <div>
                  <div style={{ fontFamily: font.mono, fontSize: "0.55rem", letterSpacing: "0.14em", textTransform: "uppercase", color: text.muted, marginBottom: "0.25rem" }}>Landed?</div>
                  <div style={{ fontFamily: font.mono, fontSize: "0.85rem", fontWeight: 700, color: o.matched ? signal.green : signal.red }}>{o.matched ? "Yes" : "No"}</div>
                </div>
                <div>
                  <div style={{ fontFamily: font.mono, fontSize: "0.55rem", letterSpacing: "0.14em", textTransform: "uppercase", color: text.muted, marginBottom: "0.25rem" }}>Regret</div>
                  <div style={{ fontFamily: font.mono, fontSize: "0.85rem", fontWeight: 700, color: text.secondary }}>{REGRET.find(r => r.v === o.regretScore)?.label ?? o.regretScore}</div>
                </div>
              </div>
              {o.learning && (
                <>
                  <div style={{ fontFamily: font.mono, fontSize: "0.55rem", letterSpacing: "0.16em", textTransform: "uppercase", color: text.muted, marginBottom: "0.4rem" }}>What you learned</div>
                  <div style={{ fontFamily: font.sans, fontSize: "0.95rem", color: text.secondary, lineHeight: 1.6 }}>{o.learning}</div>
                </>
              )}
            </>
          ) : null}
          <div style={{ marginTop: "1.5rem", display: "flex", gap: "0.5rem" }}>
            <Button variant="ghost" size="sm" onClick={() => router.push(`/brief/${receiptId}`)}>View brief</Button>
            <Button variant="ghost" size="sm" onClick={() => router.push("/history")}>Ledger</Button>
          </div>
        </Card>
      </>
    )
  }

  // ── Debrief form ──────────────────────────────────────────────────────────
  const canSubmit = matched != null && what.trim().length > 0 && regret != null && !submitting

  const taStyle: React.CSSProperties = {
    width: "100%", background: "#0a0f1a", border: `0.5px solid ${signal.cyan}22`, borderRadius: 6,
    color: text.primary, fontFamily: font.sans, fontSize: "0.9rem", padding: "0.75rem", resize: "vertical",
    minHeight: 84, outline: "none", lineHeight: 1.5, boxSizing: "border-box",
  }

  return shell(
    <>
      {recapCard}

      <div style={{ fontFamily: font.sans, fontSize: "1.05rem", color: text.primary, lineHeight: 1.55, margin: "0 0 1.5rem", maxWidth: 540 }}>
        The shoe has dropped. A receipt can&apos;t close itself — only the outcome can. Tell ARCS what actually happened.
      </div>

      <Card style={{ marginBottom: "1.25rem" }}>
        <SectionLabel index="01" color={signal.gold} style={{ marginBottom: "0.75rem" }}>Did it land where the compass pointed?</SectionLabel>
        <div style={{ display: "flex", gap: "0.6rem" }}>
          {[
            { v: true, label: "It landed", c: signal.green },
            { v: false, label: "It didn’t", c: signal.red },
          ].map(({ v, label, c }) => {
            const on = matched === v
            return (
              <button key={String(v)} onClick={() => setMatched(v)} style={{
                flex: 1, fontFamily: font.mono, fontSize: "0.75rem", fontWeight: 700, letterSpacing: "0.06em",
                padding: "0.85rem", borderRadius: 6, cursor: "pointer", textTransform: "uppercase",
                border: `0.5px solid ${on ? c : "rgba(71,85,105,0.3)"}`,
                background: on ? `${c}14` : "rgba(10,15,26,0.5)", color: on ? c : text.dimmed, transition: "all .12s",
              }}>{label}</button>
            )
          })}
        </div>
      </Card>

      <Card style={{ marginBottom: "1.25rem" }}>
        <SectionLabel index="02" color={signal.gold} style={{ marginBottom: "0.75rem" }}>What actually happened?</SectionLabel>
        <textarea value={what} onChange={(e) => setWhat(e.target.value)} maxLength={2000} placeholder="The outcome, in your words…" style={taStyle} />
      </Card>

      <Card style={{ marginBottom: "1.25rem" }}>
        <SectionLabel index="03" color={signal.gold} style={{ marginBottom: "0.75rem" }}>Looking back — any regret?</SectionLabel>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: "0.4rem" }}>
          {REGRET.map(({ v, label }) => {
            const on = regret === v
            return (
              <button key={v} onClick={() => setRegret(v)} style={{
                fontFamily: font.mono, fontSize: "0.62rem", fontWeight: 700, letterSpacing: "0.04em",
                padding: "0.7rem 0.25rem", borderRadius: 6, cursor: "pointer", textTransform: "uppercase",
                border: `0.5px solid ${on ? signal.cyan : "rgba(71,85,105,0.3)"}`,
                background: on ? `${signal.cyan}14` : "rgba(10,15,26,0.5)", color: on ? signal.cyan : text.dimmed, transition: "all .12s",
              }}>{label}</button>
            )
          })}
        </div>
      </Card>

      <Card style={{ marginBottom: "1.5rem" }}>
        <SectionLabel index="04" color={signal.gold} style={{ marginBottom: "0.75rem" }}>What did you learn? · optional</SectionLabel>
        <textarea value={learning} onChange={(e) => setLearning(e.target.value)} maxLength={2000} placeholder="The lesson you’d hand to the next version of you…" style={taStyle} />
      </Card>

      <Button variant="primary" size="lg" glyph="◉" disabled={!canSubmit} onClick={submit} style={{ width: "100%" }}>
        {submitting ? "Closing the receipt…" : "Close the receipt →"}
      </Button>
    </>
  )
}
