"use client"
import { useState, FormEvent } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { Suspense } from "react"

function UnlockForm() {
  const [pw, setPw] = useState("")
  const [error, setError] = useState(false)
  const [loading, setLoading] = useState(false)
  const router = useRouter()
  const params = useSearchParams()
  const next = params.get("next") ?? "/recoil"

  async function submit(e: FormEvent) {
    e.preventDefault()
    setLoading(true)
    setError(false)
    const res = await fetch("/api/recoil/unlock", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ password: pw }),
    })
    if (res.ok) {
      router.push(next)
    } else {
      setError(true)
      setLoading(false)
      setPw("")
    }
  }

  return (
    <div style={{
      minHeight: "100vh", background: "#020408", display: "flex",
      alignItems: "center", justifyContent: "center", padding: "24px",
    }}>
      <div style={{ width: "100%", maxWidth: 320 }}>
        <div style={{
          fontFamily: "ui-monospace,'SF Mono',monospace", fontSize: 9,
          fontWeight: 700, letterSpacing: "0.18em", textTransform: "uppercase",
          color: "#64748b", marginBottom: 28,
        }}>
          ARCS · PRIVATE ALPHA
        </div>

        <div style={{
          background: "#0d1117", border: `1px solid ${error ? "rgba(255,77,109,0.4)" : "#1e293b"}`,
          borderRadius: 12, padding: "28px 24px",
          transition: "border-color 0.2s",
        }}>
          <div style={{
            fontFamily: "ui-monospace,'SF Mono',monospace", fontSize: 9,
            fontWeight: 700, letterSpacing: "0.14em", textTransform: "uppercase",
            color: error ? "#FF4D6D" : "#00F0FF", marginBottom: 20,
          }}>
            {error ? "ACCESS DENIED" : "RECOIL REPORTS"}
          </div>

          <form onSubmit={submit} style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            <input
              type="password"
              value={pw}
              onChange={e => setPw(e.target.value)}
              placeholder="access key"
              autoFocus
              style={{
                background: "#111820", border: "1px solid #1e293b", borderRadius: 7,
                padding: "10px 14px", color: "#e2e8f0", fontSize: 13,
                fontFamily: "ui-monospace,'SF Mono',monospace", outline: "none",
                letterSpacing: "0.06em",
              }}
            />
            <button
              type="submit"
              disabled={loading || !pw}
              style={{
                background: loading ? "transparent" : "rgba(0,240,255,0.08)",
                border: "1px solid rgba(0,240,255,0.3)", borderRadius: 7,
                padding: "10px 14px", color: loading ? "#475569" : "#00F0FF",
                fontFamily: "ui-monospace,'SF Mono',monospace", fontSize: 11,
                fontWeight: 700, letterSpacing: "0.1em", cursor: loading ? "default" : "pointer",
                transition: "all 0.15s",
              }}
            >
              {loading ? "CHECKING..." : "UNLOCK →"}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}

export default function RecoilUnlockPage() {
  return (
    <Suspense>
      <UnlockForm />
    </Suspense>
  )
}
