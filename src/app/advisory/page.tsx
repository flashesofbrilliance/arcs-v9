"use client"

import { useState, Suspense } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { surface, text, signal, font } from "@/ui/tokens"
import { Wordmark } from "@/ui/Wordmark"
import { Rule } from "@/ui/Rule"
import { Field } from "@/ui/Field"
import { Button } from "@/ui/Button"
import { Card } from "@/ui/Card"

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

function AdvisoryInner() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const receiptId = searchParams.get("receipt") || undefined

  const [name, setName] = useState("")
  const [email, setEmail] = useState("")
  const [message, setMessage] = useState("")
  const [sent, setSent] = useState(false)
  const [loading, setLoading] = useState(false)
  const [booking, setBooking] = useState<string | null>(null)

  async function submit(e: React.FormEvent) {
    e.preventDefault()
    if (!email.trim() || loading) return
    setLoading(true)
    const { ok, bookingUrl } = await postLead({ email, name, message, source: "advisory", receiptId })
    setLoading(false)
    if (ok) { setSent(true); setBooking(bookingUrl) }
  }

  return (
    <main style={{ minHeight: "100vh", background: surface.bg, color: text.primary }}>
      <div style={{ maxWidth: 620, margin: "0 auto", padding: "2rem 1.5rem 4rem" }}>
        <div style={{ paddingBottom: "1rem" }}>
          <button onClick={() => router.push("/")} style={{ background: "none", border: "none", cursor: "pointer", padding: 0 }}>
            <Wordmark section="Advisory" />
          </button>
        </div>
        <Rule style={{ marginBottom: "2rem" }} />

        <h1 style={{ fontFamily: font.sans, fontSize: "1.6rem", fontWeight: 600, color: text.primary, margin: "0 0 0.5rem", lineHeight: 1.2, letterSpacing: "-0.01em" }}>
          Bring ARCS into the room.
        </h1>
        <p style={{ fontFamily: font.sans, fontSize: "0.9rem", color: text.muted, margin: "0 0 2rem", lineHeight: 1.6 }}>
          Advisory, fixed-term, and ongoing support available for teams who need more
          hands-on service — available on request.
        </p>

        <Card accent={signal.gold}>
          <p style={{ fontFamily: font.sans, fontSize: "0.85rem", color: text.muted, margin: "0 0 1.25rem", lineHeight: 1.6 }}>
            Tell us what your team is trying to decide. We&apos;ll figure out the right
            format — one-day session, multi-day workshop, or focused sprint — and map
            out the right approach together.
          </p>
          {sent ? (
            <div style={{ padding: "1rem", border: `1px solid ${signal.green}`, borderRadius: 8, color: signal.green, fontSize: "0.85rem", fontFamily: font.sans, lineHeight: 1.6 }}>
              Got it — we&apos;ll be in touch.
              {booking && (
                <>{" "}Prefer to grab a slot now?{" "}
                  <a href={booking} target="_blank" rel="noopener noreferrer" style={{ color: signal.cyan, textDecoration: "underline" }}>Book your session →</a>
                </>
              )}
            </div>
          ) : (
            <form onSubmit={submit} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
              <Field label="Name" value={name} onChange={(e) => setName(e.target.value)} placeholder="Your name" />
              <Field label="Email" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" />
              <Field as="textarea" rows={3} label="What are you deciding?" value={message} onChange={(e) => setMessage(e.target.value)} placeholder="One or two lines on the decision you're bringing." />
              <Button type="submit" variant="gold" size="md" disabled={loading || !email.trim()} style={{ width: "100%" }}>
                {loading ? "Sending…" : "Request a consult"}
              </Button>
            </form>
          )}
        </Card>
      </div>
    </main>
  )
}

export default function AdvisoryPage() {
  return (
    <Suspense fallback={<main style={{ minHeight: "100vh", background: surface.bg }} />}>
      <AdvisoryInner />
    </Suspense>
  )
}
