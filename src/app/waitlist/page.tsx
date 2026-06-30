"use client"

import { useState, useEffect, Suspense } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { surface, text, signal, font } from "@/ui/tokens"
import { Wordmark } from "@/ui/Wordmark"
import { Rule } from "@/ui/Rule"
import { SectionLabel } from "@/ui/SectionLabel"
import { Field } from "@/ui/Field"
import { Button } from "@/ui/Button"
import { Card } from "@/ui/Card"

// Advisory funnel — full-service ARCS waitlist + 30-min consult contact. Built on
// the cockpit design system for a unified surface with compass/prep/brief. Page
// owns the POST /api/lead (head/body, F4). Scheduling = Cal.com/Calendly link.

async function postLead(payload: Record<string, unknown>): Promise<{ ok: boolean; bookingUrl: string | null }> {
  try {
    const res = await fetch("/api/lead", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    })
    const data = await res.json().catch(() => ({}))
    return { ok: res.ok, bookingUrl: data.bookingUrl ?? null }
  } catch {
    return { ok: false, bookingUrl: null }
  }
}

function Done({ children }: { children: React.ReactNode }) {
  return (
    <div style={{ padding: "1rem", border: `1px solid ${signal.green}`, borderRadius: 8, color: signal.green, fontSize: "0.85rem", fontFamily: font.sans, lineHeight: 1.6 }}>
      {children}
    </div>
  )
}

function WaitlistInner() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const receiptId = searchParams.get("receipt") || undefined
  const [advisoryOnly, setAdvisoryOnly] = useState(false)
  useEffect(() => {
    const p = new URLSearchParams(window.location.search)
    setAdvisoryOnly(p.get("view") === "advisory")
  }, [])

  // Full-service waitlist
  const [wEmail, setWEmail] = useState("")
  const [wSent, setWSent] = useState(false)
  const [wLoading, setWLoading] = useState(false)

  // Advisory consult
  const [aName, setAName] = useState("")
  const [aEmail, setAEmail] = useState("")
  const [aMessage, setAMessage] = useState("")
  const [aSent, setASent] = useState(false)
  const [aLoading, setALoading] = useState(false)
  const [booking, setBooking] = useState<string | null>(null)

  async function submitWaitlist(e: React.FormEvent) {
    e.preventDefault()
    if (!wEmail.trim() || wLoading) return
    setWLoading(true)
    const { ok } = await postLead({ email: wEmail, source: "waitlist", receiptId })
    setWLoading(false)
    if (ok) setWSent(true)
  }

  async function submitAdvisory(e: React.FormEvent) {
    e.preventDefault()
    if (!aEmail.trim() || aLoading) return
    setALoading(true)
    const { ok, bookingUrl } = await postLead({ email: aEmail, name: aName, message: aMessage, source: "advisory", receiptId })
    setALoading(false)
    if (ok) { setASent(true); setBooking(bookingUrl) }
  }

  return (
    <main style={{ minHeight: "100vh", background: surface.bg, color: text.primary }}>
      <div style={{ maxWidth: 620, margin: "0 auto", padding: "2rem 1.5rem 4rem" }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", paddingBottom: "1rem" }}>
          <Wordmark section="Advisory" />
          <Button variant="ghost" size="sm" glyph="←" onClick={() => router.push("/")}>ARCS</Button>
        </div>
        <Rule style={{ marginBottom: "2rem" }} />

        <h1 style={{ fontFamily: font.sans, fontSize: "1.6rem", fontWeight: 600, color: text.primary, margin: "0 0 0.5rem", lineHeight: 1.2, letterSpacing: "-0.01em" }}>
          Bring ARCS into the room.
        </h1>
        <p style={{ fontFamily: font.sans, fontSize: "0.9rem", color: text.muted, margin: "0 0 2rem", lineHeight: 1.6 }}>
          Bespoke, white-glove engagements for teams that want to go deeper than the
          self-serve compass — a one-day bootcamp, a working session with your team, or
          a Mañana sprint built around the decision in front of you right now.
        </p>

        {/* Full-service waitlist — hidden when arriving via advisory CTA */}
        {!advisoryOnly && (
          <Card style={{ marginBottom: "1.5rem" }}>
            <SectionLabel index="01" style={{ marginBottom: "0.75rem" }}>Full-service ARCS · waitlist</SectionLabel>
            {wSent ? (
              <Done>You&apos;re on the list. We&apos;ll reach out as spots open.</Done>
            ) : (
              <form onSubmit={submitWaitlist} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
                <Field label="Email" type="email" required value={wEmail} onChange={(e) => setWEmail(e.target.value)} placeholder="you@example.com" />
                <Button type="submit" variant="primary" size="md" glyph={wLoading ? "~" : "⊕"} disabled={wLoading || !wEmail.trim()} style={{ width: "100%" }}>
                  {wLoading ? "Adding…" : "Join the waitlist"}
                </Button>
              </form>
            )}
          </Card>
        )}

        {/* Advisory consult */}
        <Card id="advisory" accent={signal.gold}>
          <SectionLabel index="02" color={signal.gold} style={{ marginBottom: "0.75rem" }}>Bootcamp, workshop, or sprint · 30-min intro call</SectionLabel>
          <p style={{ fontFamily: font.sans, fontSize: "0.85rem", color: text.muted, margin: "0 0 1.25rem", lineHeight: 1.6 }}>
            Tell us about the decision in front of your team. We'll scope whether a
            one-day bootcamp, a hands-on workshop, or a focused Mañana sprint is the
            right shape — then book a 30-minute call to map it out.
          </p>
          {aSent ? (
            <Done>
              Got it — we&apos;ll be in touch.
              {booking && (
                <>
                  {" "}Prefer to grab a slot now?{" "}
                  <a href={booking} target="_blank" rel="noopener noreferrer" style={{ color: signal.cyan, textDecoration: "underline" }}>Book your session →</a>
                </>
              )}
            </Done>
          ) : (
            <form onSubmit={submitAdvisory} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
              <Field label="Name" value={aName} onChange={(e) => setAName(e.target.value)} placeholder="Your name" />
              <Field label="Email" type="email" required value={aEmail} onChange={(e) => setAEmail(e.target.value)} placeholder="you@example.com" />
              <Field as="textarea" rows={3} label="What are you deciding?" value={aMessage} onChange={(e) => setAMessage(e.target.value)} placeholder="One or two lines on the decision you're bringing." />
              <Button type="submit" variant="gold" size="md" glyph={aLoading ? "~" : "◈"} disabled={aLoading || !aEmail.trim()} style={{ width: "100%" }}>
                {aLoading ? "Sending…" : "Request a consult"}
              </Button>
            </form>
          )}
        </Card>
      </div>
    </main>
  )
}

export default function WaitlistPage() {
  return (
    <Suspense fallback={<main style={{ minHeight: "100vh", background: surface.bg }} />}>
      <WaitlistInner />
    </Suspense>
  )
}
