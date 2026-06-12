"use client"

import { useState, Suspense } from "react"
import { useSearchParams } from "next/navigation"
import { surface, text, signal, font } from "@/ui/tokens"
import { Wordmark } from "@/ui/Wordmark"
import { Rule } from "@/ui/Rule"
import { Field } from "@/ui/Field"
import { Button } from "@/ui/Button"
import { Card } from "@/ui/Card"

// Sign-in surface — magic link (Auth.js v5 + Resend). Honors ?next= so a gated
// action (sharing a brief, opening history) returns the user where they started
// after authenticating. Page owns the signIn call (head/body, F4).

function CompassInner() {
  const searchParams = useSearchParams()
  const next = searchParams.get("next") || "/dashboard"
  const [email, setEmail] = useState("")
  const [sent, setSent] = useState(false)
  const [loading, setLoading] = useState(false)

  async function handleMagicLink(e: React.FormEvent) {
    e.preventDefault()
    if (!email.trim() || loading) return
    setLoading(true)
    const { signIn } = await import("next-auth/react")
    await signIn("resend", { email, callbackUrl: next, redirect: false })
    setSent(true)
    setLoading(false)
  }

  return (
    <main style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: surface.bg, color: text.primary, padding: "1.5rem" }}>
      <Card style={{ width: "100%", maxWidth: 420 }}>
        <Wordmark section="Sign in" />
        <Rule style={{ margin: "1rem 0 1.5rem" }} />

        <h1 style={{ fontFamily: font.sans, fontSize: "1.4rem", fontWeight: 600, color: text.primary, margin: "0 0 0.5rem", lineHeight: 1.25, letterSpacing: "-0.01em" }}>
          Save your receipts. Share your briefs.
        </h1>
        <p style={{ fontFamily: font.sans, fontSize: "0.85rem", color: text.muted, margin: "0 0 1.75rem", lineHeight: 1.6 }}>
          One magic link — no password. Your questions, prep, and briefs land under your account, and your shared briefs stay yours.
        </p>

        {sent ? (
          <div style={{ padding: "1rem", border: `1px solid ${signal.green}`, borderRadius: 8, color: signal.green, fontSize: "0.85rem", fontFamily: font.sans, lineHeight: 1.5 }}>
            Check your email — magic link sent to <strong>{email}</strong>.
          </div>
        ) : (
          <form onSubmit={handleMagicLink} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
            <Field label="Email" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" />
            <Button type="submit" variant="primary" size="lg" glyph={loading ? "~" : "→"} disabled={loading || !email.trim()} style={{ width: "100%" }}>
              {loading ? "Sending…" : "Send magic link"}
            </Button>
          </form>
        )}
      </Card>
    </main>
  )
}

export default function CompassPage() {
  return (
    <Suspense fallback={<main style={{ minHeight: "100vh", background: surface.bg }} />}>
      <CompassInner />
    </Suspense>
  )
}
