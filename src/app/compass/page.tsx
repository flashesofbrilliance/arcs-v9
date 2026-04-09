"use client"

import { useState } from "react"

export default function CompassPage() {
  const [email, setEmail] = useState("")
  const [sent, setSent] = useState(false)
  const [loading, setLoading] = useState(false)

  async function handleMagicLink(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    const { signIn } = await import("next-auth/react")
    await signIn("resend", { email, callbackUrl: "/dashboard", redirect: false })
    setSent(true)
    setLoading(false)
  }

  return (
    <main style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: "#020408", color: "#e2e8f0", fontFamily: "sans-serif" }}>
      <div style={{ width: 380, padding: "2rem" }}>
        <h1 style={{ fontSize: "1.5rem", marginBottom: "0.5rem", color: "#00F0FF" }}>ARCS Question Compass</h1>
        <p style={{ fontSize: "0.875rem", color: "#94a3b8", marginBottom: "2rem" }}>
          Type what you are really trying to decide. Get your next move.
        </p>

        {sent ? (
          <div style={{ padding: "1rem", border: "1px solid #00FF9D", borderRadius: 8, color: "#00FF9D", fontSize: "0.875rem" }}>
            Check your email — magic link sent to <strong>{email}</strong>
          </div>
        ) : (
          <form onSubmit={handleMagicLink}>
            <label style={{ display: "block", fontSize: "0.75rem", color: "#94a3b8", marginBottom: "0.5rem", textTransform: "uppercase", letterSpacing: "0.05em" }}>
              Email
            </label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              style={{ width: "100%", padding: "0.625rem 0.75rem", background: "#0d1117", border: "1px solid #1e293b", borderRadius: 6, color: "#e2e8f0", fontSize: "0.875rem", boxSizing: "border-box", marginBottom: "1rem", outline: "none" }}
            />
            <button
              type="submit"
              disabled={loading}
              style={{ width: "100%", padding: "0.625rem", background: "#00F0FF", color: "#020408", fontWeight: 600, fontSize: "0.875rem", border: "none", borderRadius: 6, cursor: loading ? "not-allowed" : "pointer", opacity: loading ? 0.7 : 1 }}
            >
              {loading ? "Sending…" : "Send magic link →"}
            </button>
          </form>
        )}
      </div>
    </main>
  )
}
