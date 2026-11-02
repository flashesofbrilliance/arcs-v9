// Render through the fog to earned clarity.
"use client"

import { DeadEnd } from "@/molecules/DeadEnd"
import { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { track } from "@vercel/analytics"
import { surface, text, signal, font, getWeather, nciColor, contentContainer } from "@/ui/tokens"
import { useVw } from "@/ui/useVw"
import { Badge } from "@/ui/Badge"
import { Brief } from "@/organisms/Brief"
import { TributariesStack } from "@/molecules/TributariesStack"
import { DebriefCard } from "@/molecules/DebriefCard"
import { SequenceLoader } from "@/molecules/SequenceLoader"
import { Card } from "@/ui/Card"
import { Label } from "@/ui/Label"
import { Button, ButtonLink } from "@/ui/Button"
import type { CompassResult } from "@/lib/mockCompass"
import { toCompassResult } from "@/lib/briefView"
import { ReflectLayer } from "@/organisms/ReflectLayer"

// Brief surface — the shareable cartography report. Fetches the stored brief +
// receipt, maps the DB receipt → CompassResult, renders the Brief organism
// (on-screen) plus the AI situation framing and share row. Page owns data
// (head/body, F4). Doc-kit print/share view + enrich = follow-up.

export default function BriefPage() {
  const params = useParams()
  const router = useRouter()
  const receiptId = String(params.receiptId)
  const vw = useVw()

  const [result, setResult] = useState<CompassResult | null>(null)
  const [receipt, setReceipt] = useState<Record<string, unknown> | null>(null)
  // Lineage position — depth in the reasoning chain + parent for breadcrumb.
  const [depth, setDepth] = useState<number>(0)
  const [parentId, setParentId] = useState<string | null>(null)
  const [framing, setFraming] = useState<string>("")
  const [children, setChildren] = useState<Array<{ id: string; decision: string; trueNorth: string; yState: string; nciScore: number; version: number; createdAt: string }>>([])

  const [error, setError] = useState<string | null>(null)
  // Set when the brief is behind the paywall (402): the Payment Link for this receipt.
  const [paymentUrl, setPaymentUrl] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)
  // null = still checking. Only the owner reaches this page (the API 404s anyone else).
  const [authed, setAuthed] = useState<boolean | null>(null)

  useEffect(() => {
    let cancelled = false
    fetch(`/api/brief/${receiptId}`)
      .then(async (r) => ({ ok: r.ok, status: r.status, data: await r.json() }))
      .then(({ ok, status, data }) => {
        if (cancelled) return
        if (status === 402 && typeof data.paymentUrl === "string") { setPaymentUrl(data.paymentUrl); return }
        if (!ok) { setError(data.error ?? "Could not load brief"); return }
        setReceipt(data.receipt)
        setResult(toCompassResult(data.receipt, data.tributaries ?? []))
        setDepth(Number(data.receipt?.version ?? 0))
        setParentId((data.receipt?.parentId as string) ?? null)
        setFraming(data.brief?.situationFraming ?? "")
        setChildren(data.children ?? [])
      })
      .catch(() => { if (!cancelled) setError("Could not load brief") })
    return () => { cancelled = true }
  }, [receiptId])

  // Resolve auth state; once signed in, claim this browser's anonymous receipts.
  useEffect(() => {
    let cancelled = false
    fetch("/api/auth/session")
      .then((r) => r.json())
      .then((s) => {
        if (cancelled) return
        const isAuthed = !!s?.user?.id
        setAuthed(isAuthed)
      })
      .catch(() => { if (!cancelled) setAuthed(false) })
    return () => { cancelled = true }
  }, [])

  // Follow a tributary → start a new compass round seeded by this tributary's
  // prompt, parented to this receipt (lineage edge) and kept in the same session
  // thread. The dashboard reads ?parent & ?sid and auto-runs the follow-up.
  function followTributary(prompt: string, index: number) {
    track("brief_tributary_followed", { receiptId })
    // ?tributary= names which of the three prompts was followed; the compass
    // persists it as parentTributaryIndex on the child receipt.
    const params = new URLSearchParams({ q: prompt, parent: receiptId, tributary: String(index) })
    router.push(`/dashboard?${params.toString()}`)
  }

  // Raw /brief/<id> links are owner-only, so every share goes through a minted
  // token (POST /api/brief/[id]/share). The token is returned once and kept only in
  // this page's state; the server stores its hash.
  const [shareUrl, setShareUrl] = useState<string | null>(null)
  const [shareMsg, setShareMsg] = useState<string | null>(null)
  async function getShareUrl(): Promise<string | null> {
    if (shareUrl) return shareUrl
    const r = await fetch(`/api/brief/${receiptId}/share`, { method: "POST" })
    const data = await r.json().catch(() => ({}))
    if (!r.ok || typeof data.path !== "string") { setShareMsg(data.error ?? "Could not create a share link"); return null }
    const url = `${window.location.origin}${data.path}`
    setShareUrl(url)
    return url
  }
  async function revokeShares() {
    const r = await fetch(`/api/brief/${receiptId}/share`, { method: "DELETE" })
    setShareUrl(null)
    setShareMsg(r.ok ? "Share links revoked" : "Could not revoke share links")
    setTimeout(() => setShareMsg(null), 2500)
  }

  // Count every share action, split by channel, so we can see how often briefs
  // get sent on. Page-views on /brief/[receiptId] (auto via <Analytics/>) count
  // the other side of the funnel: how often a shared link is opened.
  function trackShare(method: "copy" | "sms" | "x") {
    track("brief_shared", { method, receiptId })
  }

  async function copyLink() {
    const url = await getShareUrl()
    if (!url) return
    await navigator.clipboard.writeText(url)
    trackShare("copy")
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }
  async function shareSms() {
    const url = await getShareUrl()
    if (!url) return
    trackShare("sms")
    window.open(`sms:?body=${encodeURIComponent(`${result?.true_north}\n\nARCS Brief → ${url}`)}`)
  }
  async function shareX() {
    const url = await getShareUrl()
    if (!url) return
    trackShare("x")
    window.open(`https://x.com/intent/tweet?text=${encodeURIComponent((result?.true_north ?? "").slice(0, 220))}&url=${encodeURIComponent(url)}`)
  }

  if (paymentUrl) {
    return (
      <main style={{ minHeight: "100vh", background: "radial-gradient(120% 70% at 50% -5%, #0a1422 0%, #020408 62%)", color: text.primary, display: "flex", alignItems: "center", justifyContent: "center", padding: "2rem" }}>
        <Card style={{ maxWidth: 480, width: "100%" }}>
          <Label>Decision Brief</Label>
          <h1 style={{ fontSize: "1.5rem", margin: "0.75rem 0" }}>Your receipt is ready. The brief is one step away.</h1>
          <p style={{ color: text.secondary, lineHeight: 1.6, margin: "0 0 1.25rem" }}>
            The brief reads the terrain around your decision: situation framing, the people in it, and the paths through. It is written once and kept.
          </p>
          <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap" }}>
            <ButtonLink href={paymentUrl} onClick={() => track("brief_checkout_click", { receiptId })}>Unlock the brief</ButtonLink>
            <Button variant="ghost" onClick={() => router.push(`/receipt/${receiptId}`)}>Back to the receipt</Button>
          </div>
        </Card>
      </main>
    )
  }
  if (error) {
    // Missing or unreadable record: branded dead end with a way back, not a lone red line.
    const missing = /not found/i.test(error)
    return (
      <DeadEnd
        section="Decision Brief"
        title={missing ? "We can't find that brief." : "This brief didn't load."}
        body={missing
          ? "Briefs open only for their owner. If this one is yours, sign in. If someone sent it to you, ask them for a share link."
          : "Something went wrong on our side. Try again in a minute, or start from the compass."}
      />
    )
  }
  if (!result) {
    return (
      <main style={{ minHeight: "100vh", background: "radial-gradient(120% 70% at 50% -5%, #0a1422 0%, #020408 62%)", color: text.primary, display: "flex", alignItems: "center", justifyContent: "center", padding: "2rem" }}>
        <SequenceLoader
          title="Rendering your decision brief…"
          stages={[{ name: "SURVEY" }, { name: "SITUATION FRAMING" }, { name: "ENTITY READ" }, { name: "TERRAIN PATHS" }, { name: "SILKSCREEN" }]}
          footer="Reading the terrain…"
        />
      </main>
    )
  }

  return (
    <ReflectLayer receiptId={receiptId} surface="BRIEF" reflectUrl={`/brief/reflect/${receiptId}`}>
    <main style={{ minHeight: "100vh", background: surface.bg, color: text.primary }}>
      {depth > 0 && (
        <div style={{ ...contentContainer(vw), paddingTop: "1.25rem", paddingBottom: 0, display: "flex", alignItems: "center", gap: "0.75rem", fontFamily: font.mono, fontSize: "0.7rem", letterSpacing: "0.1em", textTransform: "uppercase" }}>
          <span style={{ color: signal.cyan }}>Level {depth}</span>
          <span style={{ color: text.muted }}>·</span>
          {parentId ? (
            <button onClick={() => router.push(`/brief/${parentId}`)} style={{ background: "none", border: "none", padding: 0, cursor: "pointer", color: text.dimmed, fontFamily: font.mono, fontSize: "0.7rem", letterSpacing: "0.1em", textTransform: "uppercase" }}>
              ← Parent brief
            </button>
          ) : (
            <span style={{ color: text.dimmed }}>Reasoning chain</span>
          )}
        </div>
      )}
      <Brief result={result} situationFraming={framing} onBack={() => router.push("/history")} onTributary={followTributary} onNewQuestion={() => router.push("/dashboard")} />

      {/* Sticky share footer */}
      <div style={{ position: "sticky", bottom: 0, zIndex: 30, background: "rgba(2,4,8,0.92)", backdropFilter: "blur(12px)", WebkitBackdropFilter: "blur(12px)", borderTop: `0.5px solid rgba(30,41,59,0.5)` }}>
        <div style={{ ...contentContainer(vw), paddingTop: "0.75rem", paddingBottom: "0.75rem", display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <Label style={{ marginRight: "0.25rem", flexShrink: 0 }}>Share</Label>
          {authed ? (
            <>
              <Button variant="ghost" size="sm" onClick={copyLink}>{copied ? "✓ Copied" : "Copy link"}</Button>
              <Button variant="ghost" size="sm" onClick={shareSms}>SMS</Button>
              <Button variant="ghost" size="sm" onClick={shareX}>Post to X</Button>
              <Button variant="ghost" size="sm" onClick={revokeShares}>Revoke links</Button>
              {shareMsg && <span style={{ fontFamily: font.mono, fontSize: "0.7rem", color: text.muted }}>{shareMsg}</span>}
            </>
          ) : (
            <Button variant="gold" size="sm" glyph="◈" onClick={() => router.push(`/compass?next=${encodeURIComponent(`/brief/${receiptId}`)}`)}>
              Sign in to share
            </Button>
          )}
        </div>
      </div>

      <div style={{ ...contentContainer(vw), paddingTop: 0, paddingBottom: "6rem" }}>
        {receipt && result && (
          <DebriefCard
            receiptId={receiptId}
            question={String(receipt.decision ?? "")}
            trueNorth={String(receipt.trueNorth ?? "")}
            nciScore={Number(receipt.nciScore ?? 0)}
            nciGrade={typeof receipt.nciGrade === "string" ? receipt.nciGrade : undefined}
            createdAt={String(receipt.createdAt ?? new Date().toISOString())}
            protecting={(() => { try { return JSON.parse(receipt.protecting as string) } catch { return [] } })()}
          />
        )}

        {children.length > 0 && (
          <Card style={{ marginBottom: "1.5rem" }}>
            <Label style={{ marginBottom: "0.75rem" }}>Tributary rounds · where this led</Label>
            <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
              {children.map((child) => {
                const w = getWeather(child.yState)
                const c = nciColor(child.nciScore)
                return (
                  <div
                    key={child.id}
                    onClick={() => router.push(`/brief/${child.id}`)}
                    style={{ cursor: "pointer", padding: "0.75rem", borderRadius: 4, border: `1px solid ${signal.cyan}22`, background: "#0a1520", transition: "border-color 0.15s" }}
                    onMouseEnter={(e) => (e.currentTarget.style.borderColor = `${signal.cyan}66`)}
                    onMouseLeave={(e) => (e.currentTarget.style.borderColor = `${signal.cyan}22`)}
                  >
                    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: "0.75rem", marginBottom: "0.35rem" }}>
                      <Badge label={`${w.icon} ${w.label}`} color={w.color} register="light" />
                      <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                        <span style={{ fontFamily: font.mono, fontSize: "0.6875rem", color: text.muted, letterSpacing: "0.08em" }}>L{child.version}</span>
                        <span style={{ fontFamily: font.mono, fontWeight: 700, fontSize: "0.85rem", color: c }}>{child.nciScore}</span>
                      </div>
                    </div>
                    <div style={{ fontFamily: font.sans, fontSize: "0.8rem", color: text.primary, lineHeight: 1.4, marginBottom: "0.25rem" }}>{child.decision}</div>
                    <div style={{ fontFamily: font.sans, fontSize: "0.75rem", color: text.secondary, lineHeight: 1.4 }}>
                      <span style={{ color: signal.cyan }}>True North · </span>{child.trueNorth}
                    </div>
                  </div>
                )
              })}
            </div>
          </Card>
        )}

      </div>
    </main>
    </ReflectLayer>
  )
}
