"use client"

import { useState, useEffect, useRef, Suspense } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { surface, text, contentContainer, border } from "@/ui/tokens"
import { useVw } from "@/ui/useVw"
import { CompassForm } from "@/organisms/CompassForm"
import { CompassError } from "@/molecules/CompassError"
import { Button } from "@/ui/Button"

// Dashboard — the Compass surface. CompassForm (input) + ResultView (receipt)
// organisms are presentational; this page owns the live L0–L5 pipeline, prep
// context chain, tributary follow-ups, and session tracking (head/body, F4).

type Horizon = "TODAY" | "THIS_WEEK" | "THIS_QUARTER" | "ONE_TO_THREE_YEARS"
type Stakes = "LOW" | "MEDIUM" | "HIGH"

function DashboardInner() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const vw = useVw()

  const [question, setQuestion] = useState(() => searchParams.get("q") ?? "")
  const [inboundPrepId] = useState(() => searchParams.get("prepId") ?? null)
  // Tributary follow-up arriving from a brief: ?parent=<receiptId>&sid=<sessionId>
  const [inboundParent] = useState(() => searchParams.get("parent") ?? null)
  const [inboundSid] = useState(() => searchParams.get("sid") ?? null)
  const [horizon, setHorizon] = useState<Horizon>("THIS_WEEK")
  const [stakes, setStakes] = useState<Stakes>("MEDIUM")
  const [loading, setLoading] = useState(false)
  const [step, setStep] = useState(0)
  const [error, setError] = useState<string | null>(null)

  // Session tracking — preserved across tributary follow-ups
  const [sessionId, setSessionId] = useState<string>("")
  const [parentReceiptId, setParentReceiptId] = useState<string | null>(inboundParent)
  // Continue the brief's session thread if one arrived; otherwise start fresh.
  useEffect(() => { setSessionId(inboundSid ?? crypto.randomUUID()) }, [inboundSid])

  // Animate the L0–L5 step indicator while the pipeline runs
  useEffect(() => {
    if (!loading) { setStep(0); return }
    const t = setInterval(() => setStep((s) => (s < 5 ? s + 1 : s)), 650)
    return () => clearInterval(t)
  }, [loading])

  // ADR-016: claim any pre-auth anonymous receipts once authenticated
  useEffect(() => {
    if (typeof window === "undefined") return
    const stored = localStorage.getItem("arcs_session_id")
    if (!stored) return
    fetch("/api/auth/session")
      .then((r) => r.json())
      .then((s) => {
        if (!s?.user?.id) return
        return fetch("/api/receipts/claim", {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ sessionId: stored }),
        })
      })
      .then((r) => { if (r?.ok) localStorage.removeItem("arcs_session_id") })
      .catch(() => {})
  }, [])

  // ADR-029: nudge a logged-in user who hasn't uploaded or skipped the
  // onboarding profile step yet. 401 (anonymous) is the common case — fail
  // silent, don't show the nudge.
  const [showOnboardingNudge, setShowOnboardingNudge] = useState(false)
  useEffect(() => {
    fetch("/api/onboarding/upload")
      .then((r) => (r.ok ? r.json() : null))
      .then((s) => { if (s && !s.seen) setShowOnboardingNudge(true) })
      .catch(() => {})
  }, [])

  // Returning from /prep with a prepId + question → run the enriched compass once.
  const autoRan = useRef(false)
  useEffect(() => {
    if (autoRan.current || !inboundPrepId || !question.trim()) return
    autoRan.current = true
    runCompass()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [inboundPrepId])

  // Arriving from a brief tributary → run the parented follow-up once the
  // session thread is resolved, so the new receipt joins the same lineage.
  const autoRanParent = useRef(false)
  useEffect(() => {
    if (autoRanParent.current || !inboundParent || !question.trim() || !sessionId) return
    autoRanParent.current = true
    runCompassWith(question, true)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionId])

  async function runCompass(opts: { followUp?: boolean } = {}) {
    if (!question.trim() || loading) return
    return runCompassWith(question, !!opts.followUp)
  }

  // Per Zach's toolbar feedback: the dashboard no longer renders an inline
  // preview carousel after a run — it navigates straight to the receipt page
  // (skips the friction of an intermediary multi-variant view; the receipt
  // page is now the canonical "see your result" surface, tributaries and all).
  async function runCompassWith(q: string, followUp: boolean) {
    if (loading) return
    setLoading(true)
    setError(null)
    try {
      const res = await fetch("/api/compass", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question: q,
          horizon,
          stakes,
          sessionId: followUp ? sessionId : crypto.randomUUID(),
          prepId: inboundPrepId,
          parentReceiptId: followUp ? parentReceiptId : null,
        }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.error ?? "Unknown error")
      if (typeof window !== "undefined") localStorage.setItem("arcs_session_id", data.session_id)
      router.push(`/receipt/${data.receipt_id}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong")
      setLoading(false)
    }
  }

  return (
    <main style={{ minHeight: "100vh", background: surface.bg, color: text.primary }}>
      {showOnboardingNudge && (
        <div style={{ ...contentContainer(vw), paddingTop: "1rem", paddingBottom: 0 }}>
          <div style={{
            display: "flex", alignItems: "center", justifyContent: "space-between", gap: 12,
            border: `1px solid ${border.subtle}`, borderRadius: 10, padding: "10px 16px",
          }}>
            <span style={{ fontSize: 13, color: text.secondary }}>
              Add your LinkedIn profile to enrich your Profile Scan — takes under 30 seconds.
            </span>
            <div style={{ display: "flex", gap: 8, flexShrink: 0 }}>
              <Button variant="ghost" size="sm" onClick={() => setShowOnboardingNudge(false)}>Dismiss</Button>
              <Button variant="primary" size="sm" onClick={() => router.push("/onboarding")}>Set up profile</Button>
            </div>
          </div>
        </div>
      )}

      {error && (
        <div style={{ ...contentContainer(vw), paddingTop: "1rem", paddingBottom: 0 }}>
          <CompassError message={error} onRetry={() => runCompass()} />
        </div>
      )}

      <CompassForm
        question={question}
        horizon={horizon}
        stakes={stakes}
        running={loading}
        step={step}
        onQuestionChange={setQuestion}
        onHorizonChange={(v) => setHorizon(v as Horizon)}
        onStakesChange={(v) => setStakes(v as Stakes)}
        onCalibrate={() => router.push(`/prep?q=${encodeURIComponent(question)}`)}
        onSubmit={() => runCompass()}
        onHistory={() => router.push("/history")}
      />
    </main>
  )
}

export default function DashboardPage() {
  return (
    <Suspense fallback={<main style={{ minHeight: "100vh", background: surface.bg }} />}>
      <DashboardInner />
    </Suspense>
  )
}
