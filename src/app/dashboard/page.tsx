"use client"

import { useState, useEffect, useRef, Suspense } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { surface, text, contentContainer, border, signal } from "@/ui/tokens"
import { useVw } from "@/ui/useVw"
import { CompassForm } from "@/organisms/CompassForm"
import { CompassError } from "@/molecules/CompassError"
import { Button } from "@/ui/Button"

// Dashboard — the Compass surface. CompassForm (input) + ResultView (receipt)
// organisms are presentational; this page owns the live L0–L5 pipeline, prep
// context chain, tributary follow-ups, and session tracking (head/body, F4).

type Horizon = "TODAY" | "THIS_WEEK" | "THIS_QUARTER" | "ONE_TO_THREE_YEARS"
type Stakes = "LOW" | "MEDIUM" | "HIGH"

// Recovery poll: a compass run frequently completes and persists server-side
// even when the client fetch times out or the connection drops (proven in prod
// 2026-09-24 — a receipt + SAGE trace landed while the mobile client showed
// "Load failed"). Before declaring failure, look for a receipt created in THIS
// session and route to it — trust the persisted artifact, not the transient
// fetch outcome. reqSessionId is a fresh UUID per run, so no cross-session
// false positives even when /api/history runs in public (ungated) mode.
// See _QUEUE item compass-mobile-timeout-recover-receipt.
async function pollForRecoveredReceipt(
  reqSessionId: string,
  followUp: boolean,
  tries = 6,
  delayMs = 2500,
): Promise<string | null> {
  for (let i = 0; i < tries; i++) {
    await new Promise((r) => setTimeout(r, delayMs))
    try {
      const res = await fetch("/api/history", { cache: "no-store" })
      if (!res.ok) continue
      const { receipts } = (await res.json()) as {
        receipts?: Array<{ id: string; sessionId?: string; children?: Array<{ id: string }> }>
      }
      const seed = (receipts ?? []).find((r) => r.sessionId === reqSessionId)
      if (seed) {
        // Fresh run → the seed itself; follow-up → its newest child.
        if (followUp) {
          if (seed.children && seed.children.length) return seed.children[seed.children.length - 1].id
        } else {
          return seed.id
        }
      }
    } catch {
      /* keep polling — the run may still be completing */
    }
  }
  return null
}

function DashboardInner() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const vw = useVw()

  const [question, setQuestion] = useState(() => searchParams.get("q") ?? "")
  const [inboundPrepId] = useState(() => searchParams.get("prepId") ?? null)
  // Anonymous prep arrives via sessionStorage instead of a persisted prepId
  // (trust contract — no auth = no write path; see /prep + /api/prep).
  const [inboundInlinePrep] = useState(() => searchParams.get("prep") === "inline")
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
  // silent, don't show the nudge. Per toolbar feedback (DxUNiOM8XDu8): a user
  // who uploaded only the PDF (export still missing) had no way back into
  // the flow — `seen` alone went true on the first upload and the nudge
  // never returned. Re-show it whenever the profile is incomplete and the
  // user hasn't explicitly skipped, with copy that reflects what's missing.
  const [onboardingNudge, setOnboardingNudge] = useState<{ hasPdf: boolean; hasExport: boolean } | null>(null)
  useEffect(() => {
    fetch("/api/onboarding/upload")
      .then((r) => (r.ok ? r.json() : null))
      .then((s) => {
        if (s && !s.skipped && !(s.hasPdf && s.hasExport)) setOnboardingNudge({ hasPdf: s.hasPdf, hasExport: s.hasExport })
      })
      .catch(() => {})
  }, [])

  // Outcome-capture nudge — pull the user toward the receipts most likely to have
  // landed (ripe/route.ts). Dogfood-gated: mounts only when NEXT_PUBLIC_OUTCOME_NUDGE
  // is set, so the draft copy reaches no real user before it clears a Zach bless.
  const outcomeNudgeOn = process.env.NEXT_PUBLIC_OUTCOME_NUDGE === "true"
  const [ripe, setRipe] = useState<{ id: string; question: string; trueNorth: string }[]>([])
  const [ripeDismissed, setRipeDismissed] = useState(false)
  useEffect(() => {
    if (!outcomeNudgeOn) return
    fetch("/api/receipts/ripe")
      .then((r) => (r.ok ? r.json() : null))
      .then((d) => { if (d?.ripe?.length) setRipe(d.ripe) })
      .catch(() => {})
  }, [outcomeNudgeOn])

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
    const reqSessionId = followUp ? sessionId : crypto.randomUUID()
    // Own the timeout so a slow run surfaces an honest message instead of the
    // browser's generic "Load failed" — set just above the server's 60s
    // maxDuration so the server gets its full budget before we give up.
    const controller = new AbortController()
    const timeout = setTimeout(() => controller.abort(), 65_000)
    try {
      // Anonymous prep enrichment: read the inline prep handed off by /prep
      // via sessionStorage (nothing was persisted server-side).
      let inlinePrep: Record<string, unknown> | null = null
      if (inboundInlinePrep) {
        try { inlinePrep = JSON.parse(sessionStorage.getItem("arcs_prep_inline") ?? "null") } catch { inlinePrep = null }
      }
      const res = await fetch("/api/compass", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        signal: controller.signal,
        body: JSON.stringify({
          question: q,
          horizon,
          stakes,
          sessionId: reqSessionId,
          prepId: inboundPrepId,
          prep: inlinePrep ?? undefined,
          parentReceiptId: followUp ? parentReceiptId : null,
        }),
      })
      clearTimeout(timeout)
      const data = await res.json()
      if (!res.ok) throw new Error(data.error ?? "Unknown error")
      if (typeof window !== "undefined") localStorage.setItem("arcs_session_id", data.session_id)
      if (data.receipt_id) {
        router.push(`/receipt/${data.receipt_id}`)
      } else {
        // Anonymous run: nothing was persisted (trust contract). Render the
        // bearing ephemerally — stash the response in sessionStorage under a
        // minted `eph_` id and use the same receipt surface to display it.
        sessionStorage.removeItem("arcs_prep_inline")
        const eid = `eph_${crypto.randomUUID()}`
        // horizon/stakes/prep ride along so the opt-in save flow (ADR-049)
        // can persist a faithful receipt post-auth — /api/compass doesn't
        // echo them back.
        sessionStorage.setItem(`arcs_eph_${eid}`, JSON.stringify({ ...data, question: q, horizon, stakes, prep: inlinePrep }))
        router.push(`/receipt/${eid}`)
      }
    } catch (err) {
      clearTimeout(timeout)
      // The run may have completed and persisted server-side despite this
      // client-side failure (timeout / dropped connection). Recover the saved
      // receipt before showing an error — loading stays true through the poll
      // so the UI keeps its "working" state (the bearing may still be landing).
      const recoveredId = await pollForRecoveredReceipt(reqSessionId, followUp)
      if (recoveredId) {
        if (typeof window !== "undefined") localStorage.setItem("arcs_session_id", reqSessionId)
        router.push(`/receipt/${recoveredId}`)
        return
      }
      const aborted = err instanceof DOMException && err.name === "AbortError"
      setError(
        aborted
          ? "This is taking longer than usual — your bearing may still be landing. Check History in a moment, or re-run."
          : err instanceof Error ? err.message : "Something went wrong",
      )
      setLoading(false)
    }
  }

  return (
    <main style={{ minHeight: "100vh", background: surface.bg, color: text.primary }}>
      {onboardingNudge && (
        <div style={{ ...contentContainer(vw), paddingTop: "1rem", paddingBottom: 0 }}>
          <div style={{
            display: "flex", alignItems: "center", justifyContent: "space-between", gap: 12,
            border: `1px solid ${border.subtle}`, borderRadius: 10, padding: "10px 16px",
          }}>
            <span style={{ fontSize: 13, color: text.secondary }}>
              {onboardingNudge.hasPdf
                ? "Add your full data export to deepen your Profile Scan — takes under 30 seconds."
                : "Add your LinkedIn profile to enrich your Profile Scan — takes under 30 seconds."}
            </span>
            <div style={{ display: "flex", gap: 8, flexShrink: 0 }}>
              <Button variant="ghost" size="sm" onClick={() => setOnboardingNudge(null)}>Dismiss</Button>
              <Button variant="primary" size="sm" onClick={() => router.push("/onboarding")}>
                {onboardingNudge.hasPdf ? "Add export" : "Set up profile"}
              </Button>
            </div>
          </div>
        </div>
      )}

      {outcomeNudgeOn && ripe.length > 0 && !ripeDismissed && (
        <div style={{ ...contentContainer(vw), paddingTop: "1rem", paddingBottom: 0 }}>
          {/* DRAFT COPY — dogfood-gated (NEXT_PUBLIC_OUTCOME_NUDGE). Do not ship
              to real users until Zach blesses the wording. */}
          <div style={{
            display: "flex", alignItems: "center", justifyContent: "space-between", gap: 12,
            border: `1px solid ${border.subtle}`, borderLeft: `3px solid ${signal.cyan}`,
            borderRadius: 10, padding: "10px 16px",
          }}>
            <span style={{ fontSize: 13, color: text.secondary, minWidth: 0 }}>
              The shoe may have dropped on{" "}
              <span style={{ color: text.primary }}>&ldquo;{ripe[0].question}&rdquo;</span>. Did it land where the compass pointed?
              {ripe.length > 1 ? ` (+${ripe.length - 1} more to close)` : ""}
            </span>
            <div style={{ display: "flex", gap: 8, flexShrink: 0 }}>
              <Button variant="ghost" size="sm" onClick={() => setRipeDismissed(true)}>Not yet</Button>
              <Button variant="primary" size="sm" onClick={() => router.push(`/debrief/${ripe[0].id}`)}>
                Log how it landed →
              </Button>
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
