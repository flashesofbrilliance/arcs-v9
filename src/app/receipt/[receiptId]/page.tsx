"use client"

import { useEffect, useMemo, useState, useSyncExternalStore } from "react"
import { useParams, useRouter } from "next/navigation"
import { surface, text, signal, font, border, contentContainer } from "@/ui/tokens"
import { useVw } from "@/ui/useVw"
import { Wordmark } from "@/ui/Wordmark"
import { Rule } from "@/ui/Rule"
import { Button, ButtonLink } from "@/ui/Button"
import { TribunePanel } from "@/molecules/TribunePanel"
import { ProvenanceTag } from "@/molecules/ProvenanceTag"
import { SequenceLoader } from "@/molecules/SequenceLoader"
import { ReflectLayer } from "@/organisms/ReflectLayer"
import type { CompassResult, FatedDecomposition, TerrainPath } from "@/lib/mockCompass"
import { AhmedOrder, resolutionFor } from "@/organisms/AhmedOrder"
import { encodeShare } from "@/lib/shareLink"
import { track } from "@vercel/analytics"

function safeParse<T>(v: unknown, fallback: T): T {
  if (typeof v !== "string") return (v as T) ?? fallback
  try { return JSON.parse(v) as T } catch { return fallback }
}

interface ReceiptData {
  id: string
  decision: string
  trueNorth: string
  whyBullets: string
  nciScore: number
  coherencePct?: number
  mode: string
  doorClass: string
  yState: string
  fated: string
  paths: string
  macroTags: string
  stakes?: string | null
  horizon?: string | null
  renderResolution?: string | null
  version: number
  createdAt: string
  courtVerdict?: string
  sessionId: string
}

const noopSubscribe = () => () => {}

// Ephemeral anonymous bearing stash. Recovery (spec _SPECS/receipt-save-nudge-v1.md
// §6.2): the bearing may be one storage layer over, not lost. "Sign in & save"
// copies it to localStorage (arcs_pending_save, keyed by this eph id) before the
// magic-link tab hop. If the visitor comes back to this URL in a tab whose
// sessionStorage is gone, render from that stash. Never re-run the compass to
// "recover" (client-fetch-failure-is-not-persistence-failure).
function readEphemeralRaw(receiptId: string): string | null {
  let raw: string | null = null
  try { raw = sessionStorage.getItem(`arcs_eph_${receiptId}`) } catch { /* storage blocked */ }
  if (raw) return raw
  try {
    const pending = JSON.parse(localStorage.getItem("arcs_pending_save") ?? "null")
    if (pending?.ephId === receiptId && pending?.bearing && Date.now() - (pending.savedAt ?? 0) < 7 * 86400000) {
      return JSON.stringify(pending.bearing)
    }
  } catch { /* fall through to the honest error */ }
  return null
}

function parseEphemeral(receiptId: string, raw: string | null): { receipt: ReceiptData | null; tributaries: CompassResult["tributaries"]; error: string | null } {
  if (!raw) {
    return { receipt: null, tributaries: [], error: "This bearing wasn't stored. Anonymous results live only in the browser tab that ran them. Run the compass again, or sign in first to keep receipts." }
  }
  try {
    const d = JSON.parse(raw)
    return {
      receipt: {
        id: receiptId,
        decision: d.question ?? "",
        trueNorth: d.true_north ?? "",
        whyBullets: JSON.stringify(d.why ?? []),
        nciScore: Number(d.nci_score ?? 0),
        coherencePct: typeof d.coherence_pct === "number" ? d.coherence_pct : undefined,
        mode: d.decision_mode ?? "",
        doorClass: d.door_class ?? "",
        yState: d.y_state ?? "",
        renderResolution: typeof d.render_resolution === "string" ? d.render_resolution : null,
        horizon: typeof d.horizon === "string" ? d.horizon : null,
        stakes: typeof d.stakes === "string" ? d.stakes : null,
        fated: JSON.stringify(d.reasoning?.fated ?? {}),
        paths: JSON.stringify(d.reasoning?.paths ?? []),
        macroTags: JSON.stringify(d.meta?.macro_tags ?? []),
        version: 0,
        createdAt: new Date().toISOString(),
        courtVerdict: typeof d.reasoning?.court_verdict === "string" ? d.reasoning.court_verdict : undefined,
        sessionId: d.session_id ?? "",
      },
      tributaries: Array.isArray(d.tributaries) ? d.tributaries : [],
      error: null,
    }
  } catch {
    return { receipt: null, tributaries: [], error: "Could not read this browser-local bearing." }
  }
}

export default function ReceiptPage() {
  const params = useParams()
  const router = useRouter()
  const receiptId = String(params.receiptId)
  const vw = useVw()

  // Ephemeral anonymous bearing: never persisted server-side (trust contract
  // — "anonymous sessions: nothing is stored"). The dashboard stashed the
  // compass response in sessionStorage under this minted `eph_` id.
  const isEphemeral = receiptId.startsWith("eph_")

  const [fetched, setFetched] = useState<ReceiptData | null>(null)
  const [hasBrief, setHasBrief] = useState(false)
  const [fetchError, setError] = useState<string | null>(null)
  // /api/brief/[receiptId] already recovers tributaries from the receipt's
  // stored rawResponse (see that route) — just wasn't read here before.
  const [fetchedTributaries, setTributaries] = useState<CompassResult["tributaries"]>([])
  const [shareCopied, setShareCopied] = useState(false)
  // Save-nudge v1.1 (spec _SPECS/receipt-save-nudge-v1.md §6.3), dark by
  // default: OFF renders the July 2026 banner unchanged. Dismiss is scoped to
  // this one bearing (sessionStorage, keyed by eph id) and never carries to the
  // next run; each new bearing is a new consent moment.
  const saveNudgeV11 = process.env.NEXT_PUBLIC_RECEIPT_SAVE_NUDGE_V11 === "true"
  // Lazy read: only consulted once a receipt has rendered (client-side), so the
  // server/client initial values never meet in markup.
  const [saveDismissed, setSaveDismissed] = useState(() => {
    try { return typeof window !== "undefined" && !!sessionStorage.getItem(`arcs_eph_dismiss_${receiptId}`) } catch { return false }
  })

  // Ephemeral bearings are derived, not fetched: read the browser-local stash
  // through an external-store subscription (server snapshot = undefined, so the
  // first paint is the loader and hydration never mismatches).
  const ephRaw = useSyncExternalStore(
    noopSubscribe,
    () => (isEphemeral ? readEphemeralRaw(receiptId) : undefined),
    () => undefined,
  )
  const eph = useMemo(() => (isEphemeral && ephRaw !== undefined ? parseEphemeral(receiptId, ephRaw) : null), [isEphemeral, ephRaw, receiptId])
  const receipt = isEphemeral ? eph?.receipt ?? null : fetched
  const error = isEphemeral ? eph?.error ?? null : fetchError
  const tributaries = isEphemeral ? eph?.tributaries ?? [] : fetchedTributaries

  useEffect(() => {
    if (isEphemeral) return
    let cancelled = false
    fetch(`/api/brief/${receiptId}?generate=0`)
      .then(async (r) => ({ ok: r.ok, data: await r.json() }))
      .then(({ ok, data }) => {
        if (cancelled) return
        if (!ok) { setError(data.error ?? "Could not load receipt"); return }
        setFetched(data.receipt as ReceiptData)
        setHasBrief(!!data.brief)
        setTributaries(Array.isArray(data.tributaries) ? data.tributaries : [])
      })
      .catch(() => { if (!cancelled) setError("Could not load receipt") })
    return () => { cancelled = true }
  }, [receiptId, isEphemeral])

  if (error) {
    return (
      <main style={{ minHeight: "100vh", background: surface.bg, color: text.primary, display: "flex", flexDirection: "column" }}>
        <div style={{ ...contentContainer(vw), paddingTop: "2rem", paddingBottom: "1rem" }}>
          <Wordmark section="Decision Receipt" />
          <Rule style={{ marginTop: "1rem" }} />
        </div>
        <div style={{ flex: 1, display: "flex", alignItems: vw < 640 ? "flex-start" : "center", justifyContent: "center", padding: vw < 640 ? "1.5rem 1rem 6rem" : "2rem 1.5rem 7rem" }}>
          <div style={{ width: "100%", maxWidth: 460, background: surface.panel, border: `1px solid ${border.subtle}`, borderRadius: 10, padding: "1.75rem" }}>
            <div style={{ fontFamily: font.mono, fontSize: "0.62rem", letterSpacing: "0.14em", textTransform: "uppercase", color: isEphemeral ? signal.gold : signal.red, marginBottom: "0.55rem" }}>
              {isEphemeral ? "Nothing was stored, by design" : "Receipt unavailable"}
            </div>
            <h1 style={{ fontFamily: font.sans, fontSize: "1.25rem", fontWeight: 600, color: text.primary, margin: "0 0 0.55rem", lineHeight: 1.3, letterSpacing: "-0.01em" }}>
              {isEphemeral ? "This bearing didn’t travel here" : "Couldn’t load this receipt"}
            </h1>
            <p style={{ fontFamily: font.sans, fontSize: "0.88rem", color: text.secondary, lineHeight: 1.6, margin: "0 0 1.5rem" }}>{error}</p>
            <div style={{ display: "flex", gap: "0.6rem", flexWrap: "wrap" }}>
              <ButtonLink variant="primary" size="sm" href="/dashboard">Run the compass</ButtonLink>
              {isEphemeral
                ? <ButtonLink variant="ghost" size="sm" href="/compass?next=/dashboard">Sign in to keep bearings</ButtonLink>
                : <ButtonLink variant="ghost" size="sm" href="/history">← Your ledger</ButtonLink>}
            </div>
          </div>
        </div>
      </main>
    )
  }

  if (!receipt) {
    return (
      <main style={{ minHeight: "100vh", background: surface.bg, color: text.primary, display: "flex", alignItems: "center", justifyContent: "center", padding: "2rem" }}>
        <SequenceLoader
          title="Loading receipt…"
          stages={[{ name: "FETCH" }, { name: "RENDER" }]}
          footer="Loading decision receipt…"
        />
      </main>
    )
  }

  const why = safeParse<string[]>(receipt.whyBullets, [])
  const fated = safeParse<Record<string, unknown>>(receipt.fated, {})
  const paths = safeParse<unknown[]>(receipt.paths, [])
  const macroTags = safeParse<string[]>(receipt.macroTags, [])
  const resolution = resolutionFor(receipt.yState, receipt.renderResolution)

  const compassResult: CompassResult = {
    receipt_id: receipt.id,
    question: receipt.decision,
    true_north: receipt.trueNorth,
    why,
    nci_score: receipt.nciScore,
    coherence_pct: receipt.coherencePct,
    is_satoshi: false,
    decision_mode: receipt.mode,
    door_class: receipt.doorClass,
    y_state: receipt.yState,
    render_resolution: resolution,
    nci_delta: null,
    macro_tags: macroTags,
    tributaries: tributaries ?? [],
    reasoning: {
      fated: fated as unknown as CompassResult["reasoning"]["fated"],
      paths: paths as unknown as CompassResult["reasoning"]["paths"],
      court_verdict: receipt.courtVerdict,
    },
  }

  // One-time stateless share (ADR-037): encode the bearing into a URL fragment so it
  // recomposes in the recipient's browser with NO server write. Only offered for
  // ephemeral (anonymous) bearings — persisted receipts already have a real /brief link.
  const shareOneTime = async () => {
    try {
      const url = `${window.location.origin}/brief/share#${encodeShare(compassResult)}`
      await navigator.clipboard.writeText(url)
      setShareCopied(true)
      setTimeout(() => setShareCopied(false), 3000)
    } catch { /* clipboard blocked — no-op */ }
  }

  const page = (
      <main style={{ minHeight: "100vh", background: surface.bg, color: text.primary }}>
        {/* Header — Wordmark + Rule, matching home/history/brief pattern */}
        <div style={{ ...contentContainer(vw), paddingTop: "2rem", paddingBottom: "1rem", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <Wordmark section="Decision Receipt" />
          <div style={{ display: "flex", alignItems: "center", gap: "0.25rem" }}>
            {isEphemeral
              ? <ButtonLink variant="ghost" size="sm" href="/dashboard">← Compass</ButtonLink>
              : <ButtonLink variant="ghost" size="sm" href="/history">← Ledger</ButtonLink>}
            {isEphemeral && <Button variant="ghost" size="sm" onClick={shareOneTime}>{shareCopied ? "One-time link copied ✓" : "Share ↗"}</Button>}
            {!isEphemeral && <Button variant="ghost" size="sm" onClick={() => router.push(`/brief/${receiptId}`)}>{hasBrief ? "Brief →" : "Generate brief →"}</Button>}
          </div>
        </div>
        <div style={{ ...contentContainer(vw), paddingBottom: "1.5rem" }}>
          <Rule />
        </div>

        {/* Ephemeral notice — the trust contract's "nothing is stored" made visible */}
        {isEphemeral && !(saveNudgeV11 && saveDismissed) && (
          <div style={{ ...contentContainer(vw), paddingBottom: "1.25rem" }}>
            {/* DRAFT COPY behind NEXT_PUBLIC_RECEIPT_SAVE_NUDGE_V11 (default OFF).
                Zach blesses the v1.1 wording before the flag is flipped for any
                real user. OFF = the ADR-049 banner, byte-for-byte. */}
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 12, flexWrap: "wrap", border: `0.5px solid ${signal.gold}44`, borderRadius: 6, padding: "0.6rem 1rem", background: `${signal.gold}0d` }}>
              <span style={{ fontFamily: font.mono, fontSize: "0.65rem", letterSpacing: "0.08em", color: text.secondary, minWidth: 0 }}>
                {saveNudgeV11
                  ? "NOT STORED. This bearing lives only in this tab and is gone when you close it. Keep it: sign in with a magic link and it lands in your ledger, with a check-in at the horizon you chose."
                  : "NOT STORED. This bearing lives only in this browser tab, per the trust contract. Save it to your ledger by signing in."}
              </span>
              <div style={{ display: "flex", gap: 8, flexShrink: 0 }}>
                {saveNudgeV11 && (
                  <Button variant="ghost" size="sm" onClick={() => {
                    // A real dismiss: hides the banner for THIS bearing only.
                    // Nothing is written server-side; the result stays rendered.
                    track("receipt_save_dismissed", { receiptId })
                    try { sessionStorage.setItem(`arcs_eph_dismiss_${receiptId}`, "1") } catch {}
                    setSaveDismissed(true)
                  }}>Let it go</Button>
                )}
                <Button variant="ghost" size="sm" onClick={() => {
                  // Opt-in save (ADR-049): stash the bearing in localStorage
                  // (sessionStorage is tab-scoped; a magic-link click opens a
                  // new tab and would lose it), then route to sign-in. The
                  // post-auth consumer (ClaimAnonymousReceipts) persists it.
                  // ephId lets this page recover the bearing from the stash if
                  // the visitor returns to this URL in a fresh tab (§6.2).
                  track("receipt_save_clicked", { receiptId })
                  const raw = sessionStorage.getItem(`arcs_eph_${receiptId}`)
                  if (raw) {
                    // Strip the free-text "strongest argument against" before it
                    // touches localStorage: /api/receipts/save never reads it, and
                    // the stash outlives the tab until sign-in or the 7-day TTL.
                    try {
                      const bearing = JSON.parse(raw)
                      if (bearing?.prep && typeof bearing.prep === "object") bearing.prep = { ...bearing.prep, adversarialInput: null }
                      localStorage.setItem("arcs_pending_save", JSON.stringify({ savedAt: Date.now(), ephId: receiptId, bearing }))
                    } catch {}
                  }
                  router.push("/compass")
                }}>{saveNudgeV11 ? "Keep this bearing" : "Sign in & save"}</Button>
              </div>
            </div>
          </div>
        )}

        {/* Body */}
        <div style={{ ...contentContainer(vw), paddingTop: "1rem", paddingBottom: "6rem" }}>
          <AhmedOrder
            data={{
              decision: receipt.decision,
              trueNorth: receipt.trueNorth,
              yState: receipt.yState,
              renderResolution: resolution,
              mode: receipt.mode,
              doorClass: receipt.doorClass,
              stakes: receipt.stakes,
              horizon: receipt.horizon,
              reasons: why,
              questions: tributaries ?? [],
              paths: paths as TerrainPath[],
              fated: fated as Partial<FatedDecomposition>,
              courtVerdict: receipt.courtVerdict,
              nciScore: receipt.nciScore,
              coherencePct: receipt.coherencePct,
              macroTags,
              version: receipt.version,
              createdAt: receipt.createdAt,
            }}
            onQuestion={(prompt, index) => {
              // Ephemeral bearings have no persisted row: omit `parent` so
              // the follow-up doesn't reference a nonexistent receipt id.
              // `tributary` rides with `parent`: which of this receipt's three
              // prompts was followed (persisted as parentTributaryIndex).
              const params = new URLSearchParams({ q: prompt })
              if (!isEphemeral) {
                params.set("parent", receipt.id)
                params.set("tributary", String(index))
              }
              router.push(`/dashboard?${params.toString()}`)
            }}
            after={!isEphemeral ? (
              <>
                {/* Provenance: owner-set real | test tag, persisted receipts only; renders nothing for non-owners */}
                <div style={{ marginTop: "2.75rem" }}>
                  <ProvenanceTag receiptId={receipt.id} />
                </div>
                {/* Tribune: ADR-020 three-phase annotation, owner-only, persisted receipts only */}
                <div style={{ marginTop: "1rem" }}>
                  <TribunePanel receiptId={receipt.id} />
                </div>
              </>
            ) : null}
          />
        </div>
      </main>
  )

  // ReflectLayer's endpoints operate on persisted receipts — ephemeral
  // bearings render bare (nothing server-side to reflect against).
  return isEphemeral ? page : (
    <ReflectLayer receiptId={receiptId} surface="RECEIPT" reflectUrl={`/receipt/reflect/${receiptId}`}>
      {page}
    </ReflectLayer>
  )
}
