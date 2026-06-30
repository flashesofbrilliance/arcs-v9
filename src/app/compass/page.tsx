"use client"

import { useState, Suspense } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { surface, text, signal, font, contentContainer } from "@/ui/tokens"
import { useVw } from "@/ui/useVw"
import { Wordmark } from "@/ui/Wordmark"
import { Rule } from "@/ui/Rule"
import { Field } from "@/ui/Field"
import { Button } from "@/ui/Button"
import { Card } from "@/ui/Card"

// Sign-in surface — magic link (Auth.js v5 + Resend). Honors ?next= so a gated
// action (sharing a brief, opening history) returns the user where they started
// after authenticating. Page owns the signIn call (head/body, F4).

function CompassInner() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const next = searchParams.get("next") || "/dashboard"
  const vw = useVw()
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
    <main style={{ minHeight: "100vh", background: surface.bg, color: text.primary, display: "flex", flexDirection: "column" }}>
      {/* Top nav — same 960px container as every other page */}
      <div style={{ ...contentContainer(vw), paddingTop: "2rem", paddingBottom: "1rem" }}>
        <button onClick={() => router.push("/")} style={{ background: "none", border: "none", cursor: "pointer", padding: 0 }}>
          <Wordmark section="Sign in" />
        </button>
        <Rule style={{ marginTop: "1rem" }} />
      </div>

      {/* Card — vertically centered in remaining space, max 420 inside the 960 container */}
      <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", padding: "2rem 1.5rem 6rem" }}>
        <Card style={{ width: "100%", maxWidth: 420 }}>
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
      </div>

      {/* Sticky footer — same 960px container as home/waitlist */}
      <div style={{ position: "fixed", bottom: 0, left: 0, right: 0, zIndex: 50, borderTop: `1px solid ${signal.gold}25`, background: "rgba(2,4,8,0.92)", backdropFilter: "blur(12px)" }}>
        <div style={{ ...contentContainer(vw), padding: "0.75rem 1.5rem", display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: "1rem" }}>
          <span style={{ fontFamily: font.sans, fontSize: "0.75rem", lineHeight: 1.4, color: text.dimmed }}>
            Need a working session or sprint?
          </span>
          <Button variant="gold" size="sm" onClick={() => router.push("/advisory")}>
            Inquire directly&nbsp;<span style={{ fontFamily: font.sans, fontWeight: 400, opacity: 0.55 }}>→</span>
          </Button>
        </div>
      </div>
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
