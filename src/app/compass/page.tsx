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
  const shared = searchParams.get("shared") // set when a one-time shared bearing was consumed
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

      {/* Card — vertically centered on desktop, top-aligned on mobile */}
      <div style={{ flex: 1, display: "flex", alignItems: vw < 640 ? "flex-start" : "center", justifyContent: "center", padding: vw < 640 ? "1.5rem 1rem 6rem" : "2rem 1.5rem 6rem" }}>
        <Card style={{ width: "100%", maxWidth: 420 }}>
          {shared && (
            <div style={{ borderLeft: `2px solid ${signal.gold}`, paddingLeft: "0.85rem", marginBottom: "1.25rem" }}>
              <div style={{ fontFamily: font.mono, fontSize: "0.6rem", letterSpacing: "0.12em", textTransform: "uppercase", color: signal.gold, marginBottom: "0.3rem" }}>Shared bearing viewed</div>
              <div style={{ fontFamily: font.sans, fontSize: "0.8rem", color: text.secondary, lineHeight: 1.55 }}>
                That link was one-time. It opened once and isn&rsquo;t stored anywhere. Sign in to keep your own bearings and revisit their briefs.
              </div>
            </div>
          )}
          <h1 style={{ fontFamily: font.sans, fontSize: "1.4rem", fontWeight: 600, color: text.primary, margin: "0 0 0.5rem", lineHeight: 1.25, letterSpacing: "-0.01em" }}>
            Save receipts. Share briefs.
          </h1>
          <p style={{ fontFamily: font.sans, fontSize: "0.85rem", color: text.muted, margin: "0 0 1.75rem", lineHeight: 1.6 }}>
            One magic link, no password. Your questions, prep, and briefs land under your account, and your shared briefs stay yours.
          </p>

          {sent ? (
            <div style={{ paddingLeft: "1rem", borderLeft: `2px solid ${signal.cyan}`, marginTop: "0.5rem" }}>
              <div style={{ fontFamily: font.mono, fontSize: "0.65rem", letterSpacing: "0.1em", textTransform: "uppercase", color: text.muted, marginBottom: "0.35rem" }}>Link sent</div>
              <div style={{ fontFamily: font.sans, fontSize: "0.9rem", color: text.primary, lineHeight: 1.5 }}>Check your email. Sent to <span style={{ color: signal.cyan }}>{email}</span></div>
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
