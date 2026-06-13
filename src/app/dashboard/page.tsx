"use client"

import { useState, useEffect, useRef, Suspense } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { surface, text } from "@/ui/tokens"
import { CompassForm } from "@/organisms/CompassForm"
import { CompassError } from "@/molecules/CompassError"
import { ResultView } from "@/organisms/ResultView"
import type { CompassResult } from "@/lib/mockCompass"

// Dashboard — the Compass surface. CompassForm (input) + ResultView (receipt)
// organisms are presentational; this page owns the live L0–L5 pipeline, prep
// context chain, tributary follow-ups, and session tracking (head/body, F4).

type Horizon = "TODAY" | "THIS_WEEK" | "THIS_QUARTER" | "ONE_TO_THREE_YEARS"
type Stakes = "LOW" | "MEDIUM" | "HIGH"

function DashboardInner() {
  const router = useRouter()
  const searchParams = useSearchParams()

  const [question, setQuestion] = useState(() => searchParams.get("q") ?? "")
  const [inboundPrepId] = useState(() => searchParams.get("prepId") ?? null)
  // Tributary follow-up arriving from a brief: ?parent=<receiptId>&sid=<sessionId>
  const [inboundParent] = useState(() => searchParams.get("parent") ?? null)
  const [inboundSid] = useState(() => searchParams.get("sid") ?? null)
  const [horizon, setHorizon] = useState<Horizon>("THIS_WEEK")
  const [stakes, setStakes] = useState<Stakes>("MEDIUM")
  const [loading, setLoading] = useState(false)
  const [step, setStep] = useState(0)
  const [result, setResult] = useState<CompassResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  // Session tracking — preserved across tributary follow-ups
  const [sessionId, setSessionId] = useState<string>("")
  const [parentReceiptId, setParentReceiptId] = useState<string | null>(inboundParent)
  const tributaryMode = useRef(false)
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
    tributaryMode.current = true
    runCompassWith(question, true)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionId])

  async function runCompass(opts: { followUp?: boolean } = {}) {
    if (!question.trim() || loading) return
    setLoading(true)
    setError(null)
    if (!opts.followUp) setResult(null)

    try {
      // Calibration is the full /prep form now (true 1–5 confidence + entity +
      // adversarial). Its prepId arrives via ?prepId= and enriches the L0–L5 run.
      const prepId = inboundPrepId

      const res = await fetch("/api/compass", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question,
          horizon,
          stakes,
          sessionId: opts.followUp ? sessionId : crypto.randomUUID(),
          prepId,
          parentReceiptId: opts.followUp ? parentReceiptId : null,
        }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.error ?? "Unknown error")
      setResult({ ...data, question })
      setSessionId(data.session_id)
      setParentReceiptId(data.receipt_id)
      tributaryMode.current = false
      if (typeof window !== "undefined") localStorage.setItem("arcs_session_id", data.session_id)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong")
    } finally {
      setLoading(false)
    }
  }

  function handleTributary(prompt: string) {
    setQuestion(prompt)
    tributaryMode.current = true
    // run as a follow-up on the next tick so `question` is updated
    setTimeout(() => runCompassWith(prompt, true), 0)
  }

  // tributary needs the new question immediately (state not yet flushed)
  async function runCompassWith(q: string, followUp: boolean) {
    if (loading) return
    setLoading(true)
    setError(null)
    try {
      const res = await fetch("/api/compass", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question: q, horizon, stakes,
          sessionId, prepId: inboundPrepId,
          parentReceiptId: followUp ? parentReceiptId : null,
        }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.error ?? "Unknown error")
      setResult({ ...data, question: q })
      setSessionId(data.session_id)
      setParentReceiptId(data.receipt_id)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong")
    } finally {
      setLoading(false)
    }
  }

  return (
    <main style={{ minHeight: "100vh", background: surface.bg, color: text.primary }}>
      {error && (
        <div style={{ maxWidth: 620, margin: "0 auto", padding: "1rem 1.5rem 0" }}>
          <CompassError message={error} onRetry={() => runCompass()} />
        </div>
      )}

      {result ? (
        <ResultView
          result={result}
          onReset={() => { setResult(null); setQuestion("") }}
          onBrief={() => router.push(`/brief/${result.receipt_id}`)}
          onTributary={handleTributary}
        />
      ) : (
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
      )}
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
