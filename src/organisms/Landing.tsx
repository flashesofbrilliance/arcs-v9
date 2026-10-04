"use client"

import { useState } from "react"
import Link from "next/link"
import { surface, text, signal, font, border } from "@/ui/tokens"
import { Wordmark } from "@/ui/Wordmark"
import { Rule } from "@/ui/Rule"
import { Field } from "@/ui/Field"
import { Button } from "@/ui/Button"
import { Card } from "@/ui/Card"
import { AuthControl } from "@/molecules/AuthControl"
import { Scope } from "@/organisms/Scope"

// The front door, and the waitlist. Both are the WORLD.md first build: one
// terrain tile, fog densities, a navigator, a true-north bearing. Fidelity is
// earned: the fog thins as you lean toward a move (hovering the compass, a
// valid address) and only clears once the server has written the row.
//
// variant "home": the compass is the move, the waitlist is the second one.
// variant "waitlist": the form leads, for links that are about the list.
// Writes go to POST /api/lead (Lead table, source "waitlist").

type Phase = "idle" | "sending" | "done" | "error" | "limited"
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

const PROMISES = [
  { title: "What we keep", body: "Your email address and the time you joined, plus the brief that sent you here if there was one. It is stored in our database, and each new signup is emailed to the ARCS team so a person reads it. Like any website, our host keeps request logs, including IP address, for 30 days." },
  { title: "What we send", body: "One confirmation, delivered through Resend, our email provider. It includes an optional link to book a session. Joining again does not send another. After that, we write when access opens." },
  { title: "What we never do", body: "Sell the list, share it, or add you to a campaign you did not ask for. The full data inventory is on the privacy page." },
]

function zoneFor(fog: number, phase: Phase): { label: string; color: string } {
  if (phase === "done") return { label: "Clarity ridge", color: signal.green }
  if (fog >= 0.9) return { label: "Outer fog layer", color: text.dimmed }
  return { label: "Pressure band", color: signal.gold }
}

const sans = font.sans
const monoLink: React.CSSProperties = { fontFamily: font.mono, ...font.tier.t3, textTransform: "uppercase", color: text.secondary, textDecoration: "none", whiteSpace: "nowrap" }

export interface LandingProps {
  variant: "home" | "waitlist"
  receiptId?: string
  exampleBriefHref?: string
}

export function Landing({ variant, receiptId, exampleBriefHref }: LandingProps) {
  const home = variant === "home"
  const [email, setEmail] = useState("")
  const [website, setWebsite] = useState("") // honeypot
  const [phase, setPhase] = useState<Phase>("idle")
  const [leaning, setLeaning] = useState(false) // pointer or focus on the compass CTA

  const valid = EMAIL_RE.test(email.trim())
  const fog =
    phase === "done" ? 0
    : phase === "sending" ? 0.42
    : valid ? 0.58
    : leaning ? 0.66
    : email.trim() ? 0.8
    : 1
  const zone = zoneFor(fog, phase)

  async function submit(e: React.FormEvent) {
    e.preventDefault()
    if (!valid || phase === "sending") return
    setPhase("sending")
    try {
      const res = await fetch("/api/lead", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email.trim(), source: "waitlist", receiptId, website }),
      })
      setPhase(res.ok ? "done" : res.status === 429 ? "limited" : "error")
    } catch {
      setPhase("error")
    }
  }

  const lean = { onMouseEnter: () => setLeaning(true), onMouseLeave: () => setLeaning(false), onFocus: () => setLeaning(true), onBlur: () => setLeaning(false) }

  const waitlist = (
    <div aria-live="polite">
      {phase === "done" ? (
        <Card accent={signal.green}>
          <div style={{ fontFamily: font.mono, ...font.tier.t2, textTransform: "uppercase", color: signal.green, marginBottom: "0.6rem" }}>On the list</div>
          <p style={{ fontFamily: sans, fontSize: "1rem", lineHeight: 1.65, color: text.primary, margin: home ? 0 : "0 0 1rem" }}>
            We will write to <span style={{ color: signal.cyan, overflowWrap: "anywhere" }}>{email.trim()}</span> when access opens. Until then, the compass is yours to use.
          </p>
          {!home && (
            <Link href="/dashboard" style={{ textDecoration: "none" }}>
              <Button variant="green" size="md" glyph="⊕" tabIndex={-1}>Open the compass</Button>
            </Link>
          )}
        </Card>
      ) : (
        <form onSubmit={submit} noValidate style={{ display: "flex", flexDirection: "column", gap: home ? "0.55rem" : "0.85rem" }}>
          {home ? (
            <div style={{ display: "flex", gap: "0.6rem", flexWrap: "wrap" }}>
              <input
                type="email"
                name="email"
                aria-label="Email for the waitlist"
                autoComplete="email"
                inputMode="email"
                spellCheck={false}
                autoCapitalize="none"
                required
                value={email}
                onChange={(e) => { setEmail(e.target.value); if (phase !== "sending") setPhase("idle") }}
                placeholder="you@example.com"
                style={{
                  flex: "1 1 220px", minWidth: 0, boxSizing: "border-box", height: 42, padding: "0 12px",
                  fontFamily: sans, fontSize: 15, color: text.primary, caretColor: signal.cyan,
                  background: "linear-gradient(180deg, #090d12, #0c1219)", border: `1px solid ${border.subtle}`, borderRadius: 5, outline: "none",
                }}
                onFocus={(e) => { e.currentTarget.style.borderColor = "#00F0FF66" }}
                onBlur={(e) => { e.currentTarget.style.borderColor = border.subtle }}
              />
              <Button type="submit" variant="outline-cyan" size="md" disabled={!valid || phase === "sending"} style={{ height: 42, flex: "0 0 auto" }}>
                {phase === "sending" ? "Writing you in" : "Join the waitlist"}
              </Button>
            </div>
          ) : (
            <>
              <Field
                label="Email"
                type="email"
                required
                value={email}
                onChange={(e) => { setEmail(e.target.value); if (phase !== "sending") setPhase("idle") }}
                placeholder="you@example.com"
                inputProps={{ name: "email", autoComplete: "email", inputMode: "email", spellCheck: false, autoCapitalize: "none" }}
              />
              <Button type="submit" variant="primary" size="lg" glyph={phase === "sending" ? "~" : "⊕"} disabled={!valid || phase === "sending"} style={{ width: "100%" }}>
                {phase === "sending" ? "Writing you in" : "Join the waitlist"}
              </Button>
            </>
          )}
          {/* Honeypot: hidden from people and assistive tech; bots fill it. */}
          <div aria-hidden="true" style={{ position: "absolute", left: "-10000px", width: 1, height: 1, overflow: "hidden" }}>
            <label>Website<input tabIndex={-1} autoComplete="off" value={website} onChange={(e) => setWebsite(e.target.value)} /></label>
          </div>
          {phase === "error" && (
            <p role="alert" style={{ fontFamily: sans, fontSize: "0.875rem", color: signal.red, margin: 0, lineHeight: 1.55 }}>
              That did not go through, and nothing was saved. Try again in a moment.
            </p>
          )}
          {phase === "limited" && (
            <p role="alert" style={{ fontFamily: sans, fontSize: "0.875rem", color: signal.gold, margin: 0, lineHeight: 1.55 }}>
              Too many tries from this connection. Wait a few minutes, then try again.
            </p>
          )}
          <p style={{ fontFamily: sans, fontSize: "0.8125rem", color: text.dimmed, margin: 0, lineHeight: 1.55 }}>
            {home ? "Full-service access opens in stages. " : ""}One confirmation now, then we write only when access opens.{home && (
              <> <Link href="/privacy" style={{ color: text.secondary, textUnderlineOffset: 3 }}>What we keep</Link></>
            )}
          </p>
        </form>
      )}
    </div>
  )

  return (
    <main style={{ minHeight: "100vh", background: surface.bg, color: text.primary }}>
      <div style={{ maxWidth: 1080, margin: "0 auto", padding: "2rem clamp(1rem, 4vw, 1.5rem) 5rem" }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: "1rem", paddingBottom: "1rem" }}>
          <Wordmark section={home ? undefined : "Waitlist"} />
          <nav aria-label="Account" style={{ display: "flex", alignItems: "center", gap: "0.75rem", minHeight: 30 }}>
            {!home && <Link href="/dashboard" style={monoLink}>Open the compass →</Link>}
            <AuthControl next="/dashboard" />
          </nav>
        </div>
        <Rule style={{ marginBottom: "clamp(2rem, 6vw, 3.5rem)" }} />

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(min(100%, 380px), 1fr))", gap: "clamp(2rem, 5vw, 3.5rem)", alignItems: "start", marginBottom: "clamp(3rem, 8vw, 5rem)" }}>
          <div>
            <h1 style={{ fontFamily: sans, fontSize: "clamp(2rem, 4.6vw, 2.9rem)", fontWeight: 600, lineHeight: 1.08, letterSpacing: "-0.03em", color: text.primary, margin: "0 0 1.25rem", textWrap: "balance" }}>
              Every hard decision starts in fog.
            </h1>
            <p style={{ fontFamily: sans, fontSize: "1.0625rem", lineHeight: 1.7, color: text.secondary, margin: "0 0 2rem", textWrap: "pretty" }}>
              {home
                ? "ARCS questions your question first, tests it against what you might be missing, and returns one direction, graded by how much the ground can bear. It shows you the terrain. The decision stays yours."
                : "ARCS questions your question first, tests it against what you might be missing, and returns one direction, graded by how much the ground can bear. The compass is open now. The waitlist is for full-service access as it opens."}
            </p>

            {home ? (
              <>
              <div style={{ display: "flex", alignItems: "center", gap: "1.25rem", flexWrap: "wrap", marginBottom: "1.75rem" }}>
                <Link href="/dashboard" style={{ textDecoration: "none", borderRadius: 6 }} {...lean}>
                  <Button size="lg" glyph="⊕" tabIndex={-1}>Open the compass</Button>
                </Link>
                {exampleBriefHref && (
                  <Link href={exampleBriefHref} style={{ ...monoLink, color: text.secondary, textDecoration: "underline", textUnderlineOffset: 4, textDecorationColor: border.subtle }}>
                    See an example brief
                  </Link>
                )}
              </div>
              {waitlist}
              </>
            ) : waitlist}
          </div>

          <div style={{ width: "100%", maxWidth: 560, justifySelf: "center" }}><Scope fog={fog} clear={phase === "done"} zone={zone.label} zoneColor={zone.color} /></div>
        </div>

        {!home && (
          <>
        <h2 style={{ fontFamily: sans, fontSize: "1.15rem", fontWeight: 600, letterSpacing: "-0.01em", color: text.primary, margin: "0 0 1.25rem" }}>What joining means</h2>
        <dl style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(min(100%, 260px), 1fr))", columnGap: "2.5rem", rowGap: "1.5rem", margin: "0 0 3.5rem" }}>
          {PROMISES.map((p) => (
            <div key={p.title} style={{ borderTop: `1px solid ${border.subtle}`, paddingTop: "1rem" }}>
              <dt style={{ fontFamily: font.mono, ...font.tier.t2, textTransform: "uppercase", color: text.secondary, marginBottom: "0.55rem" }}>{p.title}</dt>
              <dd style={{ fontFamily: sans, fontSize: "0.95rem", color: text.secondary, lineHeight: 1.65, margin: 0 }}>{p.body}</dd>
            </div>
          ))}
        </dl>
          </>
        )}

      </div>
    </main>
  )
}
