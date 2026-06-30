"use client"

import { useState, Suspense } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { surface, text, signal, font } from "@/ui/tokens"
import { Wordmark } from "@/ui/Wordmark"
import { Rule } from "@/ui/Rule"
import { Field } from "@/ui/Field"
import { Button } from "@/ui/Button"
import { Card } from "@/ui/Card"

async function postLead(payload: Record<string, unknown>): Promise<{ ok: boolean }> {
  try {
    const res = await fetch("/api/lead", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    })
    return { ok: res.ok }
  } catch {
    return { ok: false }
  }
}

function WaitlistInner() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const receiptId = searchParams.get("receipt") || undefined

  const [email, setEmail] = useState("")
  const [sent, setSent] = useState(false)
  const [loading, setLoading] = useState(false)

  async function submit(e: React.FormEvent) {
    e.preventDefault()
    if (!email.trim() || loading) return
    setLoading(true)
    const { ok } = await postLead({ email, source: "waitlist", receiptId })
    setLoading(false)
    if (ok) setSent(true)
  }

  return (
    <main style={{ minHeight: "100vh", background: surface.bg, color: text.primary }}>
      <div style={{ maxWidth: 620, margin: "0 auto", padding: "2rem 1.5rem 4rem" }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", paddingBottom: "1rem" }}>
          <Wordmark section="Waitlist" />
          <Button variant="ghost" size="sm" glyph="←" onClick={() => router.push("/")}>ARCS</Button>
        </div>
        <Rule style={{ marginBottom: "2rem" }} />

        <h1 style={{ fontFamily: font.sans, fontSize: "1.6rem", fontWeight: 600, color: text.primary, margin: "0 0 0.5rem", lineHeight: 1.2, letterSpacing: "-0.01em" }}>
          Stay in the loop.
        </h1>
        <p style={{ fontFamily: font.sans, fontSize: "0.9rem", color: text.muted, margin: "0 0 2rem", lineHeight: 1.6 }}>
          Drop your email and we&apos;ll reach out as new access opens up.
        </p>

        <Card>
          {sent ? (
            <div style={{ padding: "1rem", border: `1px solid ${signal.green}`, borderRadius: 8, color: signal.green, fontSize: "0.85rem", fontFamily: font.sans, lineHeight: 1.6 }}>
              You&apos;re on the list. We&apos;ll be in touch as spots open.
            </div>
          ) : (
            <form onSubmit={submit} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
              <Field label="Email" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" />
              <Button type="submit" variant="primary" size="md" glyph={loading ? "~" : "⊕"} disabled={loading || !email.trim()} style={{ width: "100%" }}>
                {loading ? "Adding…" : "Join the waitlist"}
              </Button>
            </form>
          )}
        </Card>

        <p style={{ fontFamily: font.sans, fontSize: "0.8rem", color: text.dimmed, marginTop: "1.5rem", textAlign: "center" }}>
          Need a working session or sprint?{" "}
          <button onClick={() => router.push("/advisory")} style={{ background: "none", border: "none", cursor: "pointer", color: signal.cyan, fontSize: "0.8rem", fontFamily: font.sans, textDecoration: "underline" }}>
            Inquire directly →
          </button>
        </p>
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
