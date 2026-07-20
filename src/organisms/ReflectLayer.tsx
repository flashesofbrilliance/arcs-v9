"use client"

import { useState, useEffect, useCallback, useRef } from "react"
import { useRouter } from "next/navigation"
import { font, signal, text, surface, border } from "@/ui/tokens"
import { PointerTypeProbe } from "@/ui/PointerTypeProbe"

// Reflect Layer — acetate overlay annotation system for Brief and Receipt surfaces.
// Three independent layers: THOUGHT (cyan, left margin), COMMENT (gold, right margin),
// REACTION (red, right margin). Bottom HUD strip lifts on reflect mode entry.
// Shavasana distills annotations to a single kernel via Claude Haiku.

interface Annotation {
  id: string
  userId: string | null
  receiptId: string
  surface: string
  anchorText: string
  preContext: string
  postContext: string
  type: "THOUGHT" | "COMMENT" | "REACTION"
  body: string
  linkedRef: string | null
  kernel: string | null
  hardened: boolean
  createdAt: string
}

interface LinkedRef {
  type: "RECEIPT" | "ADR" | "ATG_TRIBUTARY" | "WISDOM"
  id: string
  label: string
}

interface DraftAnnotation {
  anchorText: string
  preContext: string
  postContext: string
  x: number
  y: number
}

interface ExpandedChip {
  annotation: Annotation
  distilling: boolean
}

export interface ReflectLayerProps {
  receiptId: string
  surface: "BRIEF" | "RECEIPT"
  children: React.ReactNode
  // URL-driven reflect pages
  defaultHudOpen?: boolean
  defaultLayers?: { THOUGHT: boolean; COMMENT: boolean; REACTION: boolean }
  // When set, collapsed pill navigates here instead of opening inline
  reflectUrl?: string
  // When set, layer toggles push to this URL base + "/" + joined layer keys
  layerUrlBase?: string
}

const CYAN = signal.cyan
const GOLD = signal.gold
const RED = signal.red
const GREEN = signal.green

const TYPE_COLOR = {
  THOUGHT: CYAN,
  COMMENT: GOLD,
  REACTION: RED,
} as const

const TYPE_ICON = { THOUGHT: "✏", COMMENT: "✦", REACTION: "◈" } as const
const TYPE_LABEL = { THOUGHT: "Thoughts", COMMENT: "Comments", REACTION: "Reactions" } as const

function glassBtn(color?: string): React.CSSProperties {
  const c = color ?? "rgba(71,85,105,.7)"
  const base = color
    ? { background: `${color}0f`, borderColor: `${color}48`, color: c, boxShadow: `0 0 8px ${color}12` }
    : { background: "rgba(15,21,32,.5)", borderColor: "rgba(71,85,105,.25)", color: c }
  return {
    fontFamily: font.mono,
    fontSize: 8,
    fontWeight: 700,
    letterSpacing: "0.06em",
    padding: "4px 12px",
    borderRadius: 20,
    cursor: "pointer",
    border: ".5px solid",
    display: "inline-flex",
    alignItems: "center",
    gap: 4,
    textTransform: "uppercase" as const,
    lineHeight: 1,
    ...base,
  }
}


function hairline(): React.CSSProperties {
  return {
    height: ".5px",
    background: "linear-gradient(90deg,transparent,rgba(30,41,59,.5) 20%,rgba(30,41,59,.5) 80%,transparent)",
    margin: "9px 0",
  }
}

// In reflect mode the cursor is always a flashlight 🔦 — regardless of the
// armed instrument — so dragging over text reads as shining a light on it.
// Hotspot at the beam tip (top-left); falls back to text so selection still works.
const FLASHLIGHT = `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='28' height='28' viewBox='0 0 28 28'%3E%3Ctext y='23' font-size='22'%3E%F0%9F%94%A6%3C/text%3E%3C/svg%3E") 3 3, text`

const REACTIONS = ["◆ Key", "✕ Disagree", "⚑ Flag", "↻ Follow up"]

// Parse "thoughts+comments" → { THOUGHT: true, COMMENT: true, REACTION: false }
export function parseLayerSegment(seg: string | undefined): { THOUGHT: boolean; COMMENT: boolean; REACTION: boolean } {
  if (!seg) return { THOUGHT: true, COMMENT: true, REACTION: true }
  const parts = seg.toLowerCase().split("-")
  return {
    THOUGHT: parts.some((p) => p === "thoughts" || p === "thought"),
    COMMENT: parts.some((p) => p === "comments" || p === "comment"),
    REACTION: parts.some((p) => p === "reactions" || p === "reaction"),
  }
}

// Encode { THOUGHT: true, COMMENT: false, REACTION: true } → "thoughts-reactions"
// Uses hyphen, not plus — + is ambiguous in URL path segments under some routers.
export function encodeLayerSegment(layers: { THOUGHT: boolean; COMMENT: boolean; REACTION: boolean }): string {
  const parts: string[] = []
  if (layers.THOUGHT) parts.push("thoughts")
  if (layers.COMMENT) parts.push("comments")
  if (layers.REACTION) parts.push("reactions")
  return parts.join("-") || "thoughts-comments-reactions"
}

export function ReflectLayer({
  receiptId,
  surface: surfaceProp,
  children,
  defaultHudOpen = false,
  defaultLayers,
  reflectUrl,
  layerUrlBase,
}: ReflectLayerProps) {
  const router = useRouter()
  const [hudOpen, setHudOpen] = useState(defaultHudOpen)
  const [barVisible, setBarVisible] = useState(true)
  const [layers, setLayers] = useState(defaultLayers ?? { THOUGHT: true, COMMENT: true, REACTION: true })
  const [activeInstrument, setActiveInstrument] = useState<"THOUGHT" | "COMMENT" | "REACTION" | null>(null)
  const [annotations, setAnnotations] = useState<Annotation[]>([])
  const [draft, setDraft] = useState<DraftAnnotation | null>(null)
  const [draftBody, setDraftBody] = useState("")
  const [expandedChip, setExpandedChip] = useState<ExpandedChip | null>(null)
  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set())
  const [distillingIds, setDistillingIds] = useState<Set<string>>(new Set())
  const [shavasanaExpanded, setShavasanaExpanded] = useState(false)
  const [shavasanaIdx, setShavasanaIdx] = useState(0)
  const [shavasanaFilter, setShavasanaFilter] = useState<"ALL" | "THOUGHT" | "COMMENT" | "REACTION">("ALL")
  const [meditateLoading, setMeditateLoading] = useState(false)
  const [meditateResult, setMeditateResult] = useState<{ held: string[]; falsified: string[]; elevated: string[] } | null>(null)
  const [meditateExpanded, setMeditateExpanded] = useState(true)
  // Start at desktop width so the server-rendered tree and the first client
  // render agree (no hydration mismatch). The effect below sets the real width
  // after mount, then transitions to the mobile/tablet layout cleanly.
  const [vw, setVw] = useState<number>(1280)
  // Floating selection picker — appears on any text highlight; dismissed on Escape / click-outside
  const [selectionPicker, setSelectionPicker] = useState<{
    anchorText: string; preContext: string; postContext: string
    x: number; y: number  // viewport coords
  } | null>(null)
  // Ref mirror so hotkey handler can read selectionPicker without stale closure
  const selectionPickerRef = useRef<typeof selectionPicker>(null)

  // Responsive — Reflect is a desktop+tablet instrument. Phones (≤760) get a
  // clean read-only brief (gated below). Tablet (761–1024) keeps a narrower rail.
  useEffect(() => {
    let raf = 0
    const sync = () => {
      cancelAnimationFrame(raf)
      raf = requestAnimationFrame(() => setVw(window.innerWidth))
    }
    sync()
    window.addEventListener("resize", sync)
    return () => { cancelAnimationFrame(raf); window.removeEventListener("resize", sync) }
  }, [])
  const mobile = vw <= 760
  const tablet = vw > 760 && vw <= 1024
  const narrow = mobile

  // Fetch annotations on mount
  useEffect(() => {
    fetch(`/api/annotations/by-receipt/${receiptId}`)
      .then((r) => r.json())
      .then((d) => { if (d.ok) setAnnotations(d.annotations) })
      .catch(() => {})
  }, [receiptId])

  // Close overlays on Escape
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setSelectionPicker(null)
        selectionPickerRef.current = null
        setDraft(null)
        setDraftBody("")
        setExpandedChip(null)
        setShavasanaExpanded(false)
      }
    }
    document.addEventListener("keydown", handler)
    return () => document.removeEventListener("keydown", handler)
  }, [])

  // Annotation hotkeys: ` → THOUGHT  ! → REACTION  @ → COMMENT
  // Guards: skip if target is an editable element; if text is selected, open
  // draft immediately; otherwise activate instrument (cursor mode only).
  useEffect(() => {
    const HOTKEYS: Record<string, "THOUGHT" | "COMMENT" | "REACTION"> = {
      "`": "THOUGHT",
      "!": "REACTION",
      "@": "COMMENT",
    }
    const handler = (e: KeyboardEvent) => {
      const key = e.key
      if (!(key in HOTKEYS)) return
      const target = e.target as HTMLElement
      if (
        target instanceof HTMLInputElement ||
        target instanceof HTMLTextAreaElement ||
        target.isContentEditable
      ) return
      const instrument = HOTKEYS[key]
      e.preventDefault()
      // If picker is showing (text selected), hotkey picks that instrument directly
      if (selectionPickerRef.current) {
        pickInstrument(instrument)
        return
      }
      const sel = window.getSelection()
      const selectedText = sel?.toString().trim() ?? ""
      if (selectedText.length >= 3) {
        setHudOpen(true)
        setActiveInstrument(instrument)
        const range = sel!.getRangeAt(0)
        const rect = range.getBoundingClientRect()
        const container = range.commonAncestorContainer.textContent ?? ""
        const offset = container.indexOf(selectedText)
        const preContext = container.slice(Math.max(0, offset - 40), offset)
        const postContext = container.slice(offset + selectedText.length, offset + selectedText.length + 40)
        setDraft({
          anchorText: selectedText,
          preContext,
          postContext,
          x: rect.left + rect.width / 2,
          y: rect.bottom + window.scrollY + 8,
        })
        setDraftBody("")
        setSelectionPicker(null)
      } else {
        setHudOpen(true)
        setActiveInstrument((prev) => prev === instrument ? null : instrument)
      }
    }
    document.addEventListener("keydown", handler)
    return () => document.removeEventListener("keydown", handler)
  }, [])

  // Text selection → floating picker. Fires on pointerup, but only for precise
  // input — mouse, trackpad, or stylus (Apple Pencil). Finger selection
  // (pointerType "touch") is left to the native iOS edit menu; Reflect never
  // overrides it. So on iPad, annotation effectively activates with the Pencil.
  const handleMouseUp = useCallback((e: PointerEvent) => {
    if (e.pointerType === "touch") {
      // Finger → native iOS selection menu, never us. Also clear any picker a
      // prior pen/mouse selection left open so the two menus never co-exist.
      setSelectionPicker(null)
      selectionPickerRef.current = null
      return
    }
    // Don't trigger inside textareas / inputs
    const target = e.target as HTMLElement
    if (
      target instanceof HTMLInputElement ||
      target instanceof HTMLTextAreaElement ||
      target.isContentEditable
    ) return

    const sel = window.getSelection()
    if (!sel || sel.isCollapsed) {
      setSelectionPicker(null)
      return
    }
    const selectedText = sel.toString().trim()
    if (!selectedText || selectedText.length < 3) {
      setSelectionPicker(null)
      return
    }

    if (!hudOpen) return  // picker only relevant in reflect mode

    const range = sel.getRangeAt(0)
    const rect = range.getBoundingClientRect()
    const container = range.commonAncestorContainer.textContent ?? ""
    const offset = container.indexOf(selectedText)
    const preContext = container.slice(Math.max(0, offset - 40), offset)
    const postContext = container.slice(offset + selectedText.length, offset + selectedText.length + 40)

    // Position picker above the selection; clamp to viewport edges
    // Keep ref in sync so hotkey handler can read without stale closure
    const pickerW = 264
    const rawX = rect.left + rect.width / 2 - pickerW / 2
    const x = Math.max(8, Math.min(rawX, window.innerWidth - pickerW - 8))
    const y = rect.top - 72  // above selection; falls back to below if < 0
    const next = {
      anchorText: selectedText,
      preContext,
      postContext,
      x,
      y: y < 8 ? rect.bottom + 8 : y,
    }
    selectionPickerRef.current = next
    setSelectionPicker(next)

    // iPad: a pen selection ALSO triggers the native iOS edit menu, colliding
    // with our picker. We've captured the anchor text + position, so collapse
    // the live selection — the native menu has nothing to attach to and
    // dismisses, leaving only the ARCS picker. Mouse (desktop) keeps its
    // highlight; there's no native menu to fight there.
    if (e.pointerType === "pen") sel.removeAllRanges()
  }, [hudOpen])

  useEffect(() => {
    // pointerup carries pointerType (mouse | pen | touch). The handler ignores
    // touch, so finger selection keeps the native iOS edit menu and only a
    // mouse/trackpad/stylus selection raises the Reflect picker.
    document.addEventListener("pointerup", handleMouseUp)
    return () => document.removeEventListener("pointerup", handleMouseUp)
  }, [handleMouseUp])

  // Dismiss picker on mousedown outside it — skip if click is inside the picker
  const pickerContainerRef = useRef<HTMLDivElement | null>(null)
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (pickerContainerRef.current?.contains(e.target as Node)) return
      setSelectionPicker(null)
      selectionPickerRef.current = null
    }
    document.addEventListener("mousedown", handler)
    return () => document.removeEventListener("mousedown", handler)
  }, [])

  // Pick instrument from the floating picker → arm + open draft immediately
  function pickInstrument(type: "THOUGHT" | "COMMENT" | "REACTION") {
    const sp = selectionPickerRef.current
    if (!sp) return
    setActiveInstrument(type)
    setHudOpen(true)
    setDraft({
      anchorText: sp.anchorText,
      preContext: sp.preContext,
      postContext: sp.postContext,
      x: sp.x + 132,
      y: sp.y + window.scrollY + 72 + 8,
    })
    setDraftBody("")
    selectionPickerRef.current = null
    setSelectionPicker(null)
  }

  async function submitAnnotation(reactionBody?: string) {
    if (!draft || !activeInstrument) return
    const body = reactionBody ?? draftBody.trim()
    if (!body) return

    try {
      const res = await fetch("/api/annotations", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          receiptId,
          surface: surfaceProp,
          anchorText: draft.anchorText,
          preContext: draft.preContext,
          postContext: draft.postContext,
          type: activeInstrument,
          body,
        }),
      })
      const d = await res.json()
      if (d.ok) {
        setAnnotations((prev) => [...prev, d.annotation])
        setDraft(null)
        setDraftBody("")
        window.getSelection()?.removeAllRanges()
      }
    } catch {
      // network failure — draft stays open so user can retry
    }
  }

  async function deleteAnnotation(id: string) {
    await fetch(`/api/annotations/${id}`, { method: "DELETE" })
    setAnnotations((prev) => {
      const next = prev.filter((a) => a.id !== id)
      if (next.length === 0) {
        setHudOpen(false)
      } else {
        // auto-toggle off any layer that now has zero annotations
        setLayers((prevLayers) => ({
          THOUGHT: next.some((a) => a.type === "THOUGHT") ? prevLayers.THOUGHT : false,
          COMMENT: next.some((a) => a.type === "COMMENT") ? prevLayers.COMMENT : false,
          REACTION: next.some((a) => a.type === "REACTION") ? prevLayers.REACTION : false,
        }))
      }
      return next
    })
    setExpandedChip(null)
  }

  async function distillKernel(annotation: Annotation) {
    setDistillingIds((prev) => new Set(prev).add(annotation.id))
    setExpandedChip((prev) => prev ? { ...prev, distilling: true } : null)
    const res = await fetch(`/api/annotations/${annotation.id}/shavasana`, { method: "POST" })
    const d = await res.json()
    if (d.ok) {
      setAnnotations((prev) => prev.map((a) => a.id === annotation.id ? { ...a, kernel: d.kernel } : a))
      setExpandedChip((prev) => prev ? { ...prev, annotation: { ...prev.annotation, kernel: d.kernel }, distilling: false } : null)
    }
    setDistillingIds((prev) => { const s = new Set(prev); s.delete(annotation.id); return s })
  }

  async function hardenKernel(id: string) {
    const res = await fetch(`/api/annotations/${id}/harden`, { method: "POST" })
    if (!res.ok) return
    // Preserve kernel field — only flip hardened flag
    setAnnotations((prev) => prev.map((a) => a.id === id ? { ...a, hardened: true, kernel: a.kernel } : a))
    setExpandedChip((prev) => prev?.annotation.id === id ? { ...prev, annotation: { ...prev.annotation, hardened: true } } : prev)
    // Keep accordion open after harden so user sees the result
    setExpandedIds((prev) => new Set(prev).add(id))
  }

  function toggleExpanded(id: string) {
    setExpandedIds((prev) => {
      const s = new Set(prev)
      s.has(id) ? s.delete(id) : s.add(id)
      return s
    })
  }

  async function runMeditate() {
    setMeditateLoading(true)
    setMeditateExpanded(true)
    setMeditateResult(null)
    try {
      // Auto-distill any annotations that don't have kernels yet
      const undistilled = annotations.filter((a) => !a.kernel)
      if (undistilled.length > 0) {
        await Promise.all(undistilled.map(async (a) => {
          const res = await fetch(`/api/annotations/${a.id}/shavasana`, { method: "POST" })
          const d = await res.json()
          if (d.ok) setAnnotations((prev) => prev.map((x) => x.id === a.id ? { ...x, kernel: d.kernel } : x))
        }))
      }
      const res = await fetch("/api/annotations/meditate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ receiptId }),
      })
      const d = await res.json()
      if (d.ok) setMeditateResult({ held: d.held ?? [], falsified: d.falsified ?? [], elevated: d.elevated ?? [] })
    } finally {
      setMeditateLoading(false)
    }
  }

  function toggleLayer(type: keyof typeof layers) {
    const next = { ...layers, [type]: !layers[type] }
    setLayers(next)
    if (layerUrlBase) {
      const seg = encodeLayerSegment(next)
      router.replace(`${layerUrlBase}/${seg}`, { scroll: false })
    }
  }

  function activateInstrument(type: "THOUGHT" | "COMMENT" | "REACTION") {
    setActiveInstrument((prev) => prev === type ? null : type)
    setDraft(null)
  }

  // Rail filter — "ALL" shows everything; individual type hides the others
  const [railFilter, setRailFilter] = useState<"ALL" | "THOUGHT" | "COMMENT" | "REACTION">("ALL")

  const thoughtCount = annotations.filter((a) => a.type === "THOUGHT").length
  const commentCount = annotations.filter((a) => a.type === "COMMENT").length
  const reactionCount = annotations.filter((a) => a.type === "REACTION").length

  const railAnnotations = annotations.filter((a) =>
    railFilter === "ALL" ? true : a.type === railFilter
  ).sort((a, b) => new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime())



  const showRail = hudOpen && !narrow

  // Sync railFilter → layers for URL-based surfaces
  function setRailFilterAndLayers(f: typeof railFilter) {
    setRailFilter(f)
    if (f === "ALL") {
      const next = { THOUGHT: true, COMMENT: true, REACTION: true }
      setLayers(next)
      if (layerUrlBase) router.replace(`${layerUrlBase}/${encodeLayerSegment(next)}`, { scroll: false })
    } else {
      const next = { THOUGHT: f === "THOUGHT", COMMENT: f === "COMMENT", REACTION: f === "REACTION" }
      setLayers(next)
      if (layerUrlBase) router.replace(`${layerUrlBase}/${encodeLayerSegment(next)}`, { scroll: false })
    }
  }

  // Phones (≤760): Reflect is hidden. Render the brief/receipt read-only so the
  // native iOS text-selection menu is left untouched. Reflect is a desktop+tablet
  // instrument (see AskUserQuestion 2026-06-16).
  if (mobile) return <><PointerTypeProbe />{children}</>

  return (
    <div style={{ position: "relative", minHeight: "100vh" }}>
      <PointerTypeProbe />
      <style>{`::-webkit-scrollbar{width:4px;height:4px}::-webkit-scrollbar-track{background:transparent}::-webkit-scrollbar-thumb{background:rgba(30,41,59,.55);border-radius:2px}::-webkit-scrollbar-thumb:hover{background:rgba(71,85,105,.65)}`}</style>
      {/* Two-column layout: [300px left rail | content] when HUD open */}
      <div style={{
        display: showRail ? "grid" : "block",
        gridTemplateColumns: showRail ? (tablet ? "320px 1fr" : "400px 1fr") : undefined,
        alignItems: "start",
      }}>
        {/* ── Left Rail ── */}
        {showRail && (
          <div style={{
            position: "sticky",
            top: 0,
            height: "100vh",
            display: "flex",
            flexDirection: "column",
            borderRight: ".5px solid rgba(30,41,59,.4)",
            background: "rgba(6,9,16,.6)",
            backdropFilter: "blur(8px)",
            overflow: "hidden",
          }}>
            {/* Rail header */}
            <div style={{
              padding: "12px 12px 10px",
              borderBottom: ".5px solid rgba(30,41,59,.35)",
              flexShrink: 0,
            }}>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 10 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                  <span style={{ fontFamily: font.mono, fontSize: 11, fontWeight: 700, letterSpacing: ".12em", color: "rgba(0,240,255,.6)", textTransform: "uppercase" }}>◎ Reflect</span>
                  <span style={{ fontFamily: font.mono, fontSize: 9, color: "rgba(71,85,105,.4)" }}>·</span>
                  <span style={{ fontFamily: font.mono, fontSize: 9, color: "rgba(71,85,105,.5)", letterSpacing: ".06em" }}>{surfaceProp}</span>
                </div>
                <button onClick={() => { setHudOpen(false); setActiveInstrument(null) }} style={{ ...glassBtn(), fontSize: 9, padding: "4px 11px" }}>↓ close</button>
              </div>

              {/* ScenarioStack-style tabs */}
              <div style={{ display: "flex", gap: 0, borderRadius: 6, overflow: "hidden", border: ".5px solid rgba(30,41,59,.4)" }}>
                {([
                  { key: "THOUGHT" as const, emoji: "💭", label: "Thought", count: thoughtCount, color: CYAN },
                  { key: "COMMENT" as const, emoji: "💬", label: "Comment", count: commentCount, color: GOLD },
                  { key: "REACTION" as const, emoji: "🗯️", label: "React", count: reactionCount, color: RED },
                ] as const).map(({ key, emoji, label, count, color }, i) => {
                  const active = railFilter === key
                  return (
                    <button
                      key={key}
                      onClick={() => setRailFilterAndLayers(key)}
                      style={{
                        flex: 1,
                        fontFamily: font.mono,
                        fontSize: 9,
                        fontWeight: 700,
                        letterSpacing: ".06em",
                        padding: "7px 4px",
                        cursor: "pointer",
                        border: "none",
                        borderRight: i < 2 ? ".5px solid rgba(30,41,59,.4)" : "none",
                        borderBottom: active ? `2px solid ${color}` : "2px solid transparent",
                        background: active ? `${color}10` : "rgba(10,15,26,.4)",
                        color: active ? color : "rgba(71,85,105,.5)",
                        textTransform: "uppercase",
                        display: "flex", flexDirection: "column", alignItems: "center", gap: 3,
                        transition: "all .12s",
                      }}
                    >
                      <span style={{ fontSize: 14 }}>{emoji}</span>
                      <span>{label}</span>
                      {count > 0 && <span style={{ opacity: .6 }}>{count}</span>}
                    </button>
                  )
                })}
              </div>
            </div>

            {/* Annotations list — inline meditate synthesis + accordion cards */}
            <div style={{ flex: 1, overflowY: "auto", padding: "10px 14px", display: "flex", flexDirection: "column", gap: 0 }}>

              {/* ── Meditate synthesis — inline accordion ── */}
              {(meditateLoading || meditateResult) && (
                <div style={{ marginBottom: 2 }}>
                  <button
                    onClick={() => setMeditateExpanded((p) => !p)}
                    style={{ width: "100%", display: "flex", alignItems: "center", justifyContent: "space-between", background: "none", border: "none", cursor: "pointer", padding: "5px 0" }}
                  >
                    <span style={{ fontFamily: font.mono, fontSize: 10, fontWeight: 700, letterSpacing: ".1em", color: `${GREEN}bb`, textTransform: "uppercase" }}>
                      📿 Meditate
                    </span>
                    <span style={{ fontFamily: font.mono, fontSize: 10, color: "rgba(71,85,105,.4)" }}>{meditateExpanded ? "▲" : "▼"}</span>
                  </button>

                  {meditateExpanded && meditateLoading && (
                    <div style={{ fontFamily: font.mono, fontSize: 11, color: `${GREEN}44`, textAlign: "center", padding: "14px 0", letterSpacing: ".08em" }}>distilling…</div>
                  )}

                  {meditateExpanded && !meditateLoading && meditateResult && (
                    <div style={{ display: "flex", flexDirection: "column", gap: 4, paddingBottom: 6 }}>
                      {[
                        { label: "Held", items: meditateResult.held, color: CYAN },
                        { label: "Challenged", items: meditateResult.falsified, color: RED },
                        { label: "Elevated", items: meditateResult.elevated, color: GREEN },
                      ].filter(({ items }) => items.length > 0).map(({ label, items, color }) => (
                        <div key={label}>
                          <div style={{ fontFamily: font.mono, fontSize: 9, fontWeight: 700, letterSpacing: ".1em", color: `${color}55`, textTransform: "uppercase", marginBottom: 3 }}>{label}</div>
                          {items.map((item, i) => (
                            <div key={i} style={{ borderLeft: `2px solid ${color}44`, paddingLeft: 8, marginBottom: 4 }}>
                              <p style={{ fontFamily: font.sans, fontSize: 13, color: text.secondary, lineHeight: 1.6, margin: 0 }}>{item}</p>
                            </div>
                          ))}
                        </div>
                      ))}
                    </div>
                  )}
                  <div style={{ height: ".5px", background: "rgba(30,41,59,.3)" }} />
                </div>
              )}

              {/* ── Shavasana — inline carousel ── */}
              {shavasanaExpanded && (() => {
                const shavList = annotations.filter((a) =>
                  shavasanaFilter === "ALL" ? true : a.type === shavasanaFilter
                )
                const cur = shavList[Math.min(shavasanaIdx, shavList.length - 1)]
                const safeIdx = Math.min(shavasanaIdx, shavList.length - 1)
                return (
                  <div style={{ marginBottom: 2 }}>
                    {/* Header row */}
                    <div style={{ display: "flex", alignItems: "center", gap: 4, padding: "5px 0" }}>
                      <span style={{ fontFamily: font.mono, fontSize: 10, fontWeight: 700, letterSpacing: ".1em", color: `${GREEN}88`, textTransform: "uppercase", flex: 1 }}>
                        ☽ Shavasana · {shavList.length}
                      </span>
                      {/* Filter pills */}
                      {(["ALL", "THOUGHT", "COMMENT", "REACTION"] as const).map((f) => (
                        <button
                          key={f}
                          onClick={() => { setShavasanaFilter(f); setShavasanaIdx(0) }}
                          style={{ ...glassBtn(shavasanaFilter === f ? CYAN : undefined), fontSize: 6, padding: "2px 6px", borderRadius: 10 }}
                        >
                          {f === "ALL" ? "All" : TYPE_ICON[f]}
                        </button>
                      ))}
                      <button onClick={() => setShavasanaExpanded(false)} style={{ ...glassBtn(), fontSize: 7, padding: "2px 6px", marginLeft: 2 }}>✕</button>
                    </div>

                    {shavList.length === 0 ? (
                      <div style={{ fontFamily: font.mono, fontSize: 9, color: "rgba(71,85,105,.3)", padding: "10px 0" }}>No annotations in this layer</div>
                    ) : cur && (
                      <div>
                        {/* Card */}
                        <div style={{ background: "rgba(8,13,22,.6)", border: `.5px solid ${TYPE_COLOR[cur.type]}18`, borderRadius: 6, padding: "10px 12px", marginBottom: 6 }}>
                          <div style={{ fontFamily: font.mono, fontSize: 9, color: `${TYPE_COLOR[cur.type]}66`, textTransform: "uppercase", letterSpacing: ".1em", marginBottom: 6 }}>
                            {TYPE_ICON[cur.type]} {cur.type} · {new Date(cur.createdAt).toLocaleDateString()}
                          </div>
                          <div style={{ borderLeft: `.5px solid rgba(30,41,59,.5)`, paddingLeft: 7, marginBottom: 8, fontFamily: font.mono, fontSize: 10, color: "rgba(71,85,105,.5)", lineHeight: 1.55 }}>
                            "{cur.anchorText}"
                          </div>
                          <div style={{ fontFamily: font.sans, fontSize: 13, color: text.secondary, lineHeight: 1.65, marginBottom: 10 }}>{cur.body}</div>

                          {cur.kernel ? (
                            <div style={{ paddingTop: 8, borderTop: `.5px solid rgba(30,41,59,.3)` }}>
                              <div style={{ fontFamily: font.mono, fontSize: 9, fontWeight: 700, letterSpacing: ".1em", color: cur.hardened ? `${CYAN}44` : `${GREEN}44`, textTransform: "uppercase", marginBottom: 4 }}>
                                {cur.hardened ? "💎 Hardened" : "☽ Kernel"}
                              </div>
                              <div style={{ fontFamily: font.mono, fontSize: 13, color: cur.hardened ? `${CYAN}dd` : `${GREEN}dd`, lineHeight: 1.55 }}>
                                {cur.kernel.replace(/\*\*|#{1,3} /g, "")}
                              </div>
                              {!cur.hardened && (
                                <button onClick={() => hardenKernel(cur.id)} style={{ ...glassBtn(CYAN), fontSize: 7, padding: "3px 9px", marginTop: 6 }}>
                                  💎 Harden
                                </button>
                              )}
                            </div>
                          ) : (
                            <button
                              onClick={async () => {
                                const res = await fetch(`/api/annotations/${cur.id}/shavasana`, { method: "POST" })
                                const d = await res.json()
                                if (d.ok) setAnnotations((prev) => prev.map((a) => a.id === cur.id ? { ...a, kernel: d.kernel } : a))
                              }}
                              style={{ ...glassBtn(GREEN), fontSize: 8, padding: "4px 12px" }}
                            >
                              ☽ Distill →
                            </button>
                          )}
                        </div>

                        {/* Navigation */}
                        {shavList.length > 1 && (
                          <div style={{ display: "flex", alignItems: "center", gap: 6, paddingBottom: 6 }}>
                            <button
                              onClick={() => setShavasanaIdx((i) => Math.max(0, i - 1))}
                              disabled={safeIdx === 0}
                              style={{ ...glassBtn(), fontSize: 7, padding: "3px 10px", opacity: safeIdx === 0 ? .3 : 1 }}
                            >← prev</button>
                            <div style={{ flex: 1, display: "flex", justifyContent: "center", gap: 4 }}>
                              {shavList.map((_, i) => (
                                <div
                                  key={i}
                                  onClick={() => setShavasanaIdx(i)}
                                  style={{ width: i === safeIdx ? 16 : 5, height: 5, borderRadius: i === safeIdx ? 2 : "50%", background: i === safeIdx ? `${CYAN}bb` : "rgba(30,41,59,.45)", cursor: "pointer", transition: "all .15s" }}
                                />
                              ))}
                            </div>
                            <button
                              onClick={() => setShavasanaIdx((i) => Math.min(shavList.length - 1, i + 1))}
                              disabled={safeIdx === shavList.length - 1}
                              style={{ ...glassBtn(CYAN), fontSize: 7, padding: "3px 10px", opacity: safeIdx === shavList.length - 1 ? .3 : 1 }}
                            >next →</button>
                          </div>
                        )}
                      </div>
                    )}
                    <div style={{ height: ".5px", background: "rgba(30,41,59,.3)" }} />
                  </div>
                )
              })()}

              {railAnnotations.length === 0 && (
                <div style={{ fontFamily: font.mono, fontSize: 11, color: "rgba(71,85,105,.3)", textAlign: "center", marginTop: 24, lineHeight: 1.7 }}>
                  {activeInstrument
                    ? `${TYPE_ICON[activeInstrument]} Select text to annotate`
                    : "Select an instrument\nto begin annotating"}
                </div>
              )}

              {railAnnotations.map((a) => {
                const c = TYPE_COLOR[a.type]
                const isOpen = expandedIds.has(a.id)
                const isDistilling = distillingIds.has(a.id)
                const cleanKernel = a.kernel ? a.kernel.replace(/\*\*|#{1,3} /g, "") : null
                return (
                  <div key={a.id} style={{ borderLeft: `3px solid ${c}`, paddingLeft: 14, paddingTop: 10, paddingBottom: 10, marginBottom: 10 }}>
                    {/* Header row — click to expand */}
                    <div
                      onClick={() => toggleExpanded(a.id)}
                      style={{ cursor: "pointer", display: "flex", alignItems: "flex-start", gap: 6 }}
                    >
                      <div style={{ flex: 1 }}>
                        <div style={{ fontFamily: font.sans, fontSize: 14, fontWeight: 500, color: text.primary, lineHeight: 1.6 }}>
                          {a.body}
                        </div>
                        <div style={{ fontFamily: font.mono, fontSize: 10, color: "rgba(71,85,105,.45)", lineHeight: 1.45, marginTop: 4 }}>
                          "{a.anchorText.slice(0, 60)}{a.anchorText.length > 60 ? "…" : ""}" · {new Date(a.createdAt).toLocaleDateString("en-US", { month: "short", day: "numeric" })}
                        </div>
                        {/* Collapsed kernel preview */}
                        {!isOpen && cleanKernel && (
                          <div style={{ fontFamily: font.mono, fontSize: 10, color: a.hardened ? `${CYAN}77` : `${GREEN}66`, lineHeight: 1.45, marginTop: 5 }}>
                            {a.hardened ? "💎 " : "☽ "}{cleanKernel.slice(0, 80)}{cleanKernel.length > 80 ? "…" : ""}
                          </div>
                        )}
                      </div>
                      <span style={{ fontFamily: font.mono, fontSize: 9, color: "rgba(71,85,105,.3)", paddingTop: 2, flexShrink: 0 }}>{isOpen ? "▲" : "▼"}</span>
                    </div>

                    {/* Accordion body */}
                    {isOpen && (
                      <div style={{ marginTop: 8, paddingTop: 8, borderTop: ".5px solid rgba(30,41,59,.3)" }}>
                        {/* Full kernel */}
                        {cleanKernel ? (
                          <div style={{ marginBottom: 8 }}>
                            <div style={{ fontFamily: font.mono, fontSize: 9, fontWeight: 700, letterSpacing: ".1em", color: a.hardened ? `${CYAN}55` : `${GREEN}55`, textTransform: "uppercase", marginBottom: 4 }}>
                              {a.hardened ? "💎 Hardened" : "☽ Kernel"}
                            </div>
                            <div style={{ fontFamily: font.mono, fontSize: 13, color: a.hardened ? `${CYAN}cc` : `${GREEN}bb`, lineHeight: 1.6 }}>{cleanKernel}</div>
                          </div>
                        ) : (
                          <button
                            onClick={(e) => { e.stopPropagation(); distillKernel(a) }}
                            disabled={isDistilling}
                            style={{ ...glassBtn(GREEN), fontSize: 7, padding: "4px 10px", marginBottom: 8, opacity: isDistilling ? .5 : 1 }}
                          >
                            {isDistilling ? "distilling…" : "☽ Distill kernel"}
                          </button>
                        )}
                        {/* Actions */}
                        <div style={{ display: "flex", gap: 4, alignItems: "center" }}>
                          {cleanKernel && !a.hardened && (
                            <button
                              onClick={(e) => { e.stopPropagation(); hardenKernel(a.id) }}
                              style={{ ...glassBtn(CYAN), fontSize: 7, padding: "3px 8px" }}
                            >
                              💎 Harden
                            </button>
                          )}
                          <div style={{ flex: 1 }} />
                          <button
                            onClick={(e) => { e.stopPropagation(); deleteAnnotation(a.id) }}
                            style={{ ...glassBtn(RED), fontSize: 7, padding: "2px 7px" }}
                          >
                            ✕
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                )
              })}
            </div>

            {/* Rail footer — instrument buttons */}
            <div style={{
              padding: "11px 14px",
              borderTop: ".5px solid rgba(30,41,59,.35)",
              flexShrink: 0,
              display: "flex",
              flexDirection: "column",
              gap: 6,
            }}>
              <div style={{ display: "flex", gap: 4 }}>
                {(["THOUGHT", "COMMENT", "REACTION"] as const).map((t) => {
                  const active = activeInstrument === t
                  const c = TYPE_COLOR[t]
                  return (
                    <button
                      key={t}
                      onClick={() => activateInstrument(t)}
                      style={{
                        flex: 1,
                        fontFamily: font.mono, fontSize: 10, fontWeight: 700,
                        padding: "7px 4px", borderRadius: 4, cursor: "pointer",
                        border: `.5px solid ${active ? `${c}50` : "rgba(30,41,59,.25)"}`,
                        background: active ? `${c}12` : "rgba(10,15,26,.4)",
                        color: active ? `${c}cc` : "rgba(71,85,105,.5)",
                        letterSpacing: ".04em",
                        textTransform: "uppercase",
                      }}
                    >
                      {TYPE_ICON[t]}
                    </button>
                  )
                })}
              </div>
              {activeInstrument && (
                <div style={{ fontFamily: font.mono, fontSize: 9, color: `${TYPE_COLOR[activeInstrument]}66`, textAlign: "center", letterSpacing: ".06em" }}>
                  {TYPE_ICON[activeInstrument]} Select text to annotate · Esc to cancel
                </div>
              )}
              {/* Meditate is the action (green, runs a synthesis); Shavasana is a
                  view toggle (neutral, expands the per-annotation kernel carousel).
                  Distinct treatments so they don't read as the same button. */}
              <div style={{ display: "flex", gap: 4, alignItems: "stretch" }}>
                <button
                  onClick={runMeditate}
                  disabled={annotations.length === 0 || meditateLoading}
                  style={{ ...glassBtn(GREEN), fontSize: 9, padding: "6px 12px", flex: 2, justifyContent: "center", opacity: annotations.length === 0 ? .3 : 1 }}
                >
                  📿 {meditateLoading ? "Synthesizing…" : "Meditate"}
                </button>
                <button
                  onClick={() => setShavasanaExpanded((p) => !p)}
                  disabled={annotations.length === 0}
                  aria-expanded={shavasanaExpanded}
                  style={{ ...glassBtn(shavasanaExpanded ? CYAN : undefined), fontSize: 9, padding: "6px 12px", flex: 1, justifyContent: "center", opacity: annotations.length === 0 ? .3 : 1 }}
                >
                  ☽ Shavasana <span style={{ opacity: .6 }}>{shavasanaExpanded ? "▴" : "▾"}</span>
                </button>
              </div>
            </div>
          </div>
        )}

        {/* ── Content ── */}
        {/* In reflect mode ARCS owns the selection experience: suppress the iOS
            long-press callout so a pen selection raises only the ARCS picker. */}
        <div style={{ cursor: hudOpen ? FLASHLIGHT : undefined, WebkitTouchCallout: hudOpen ? "none" : undefined }}>
          {children}
        </div>
      </div>

      {/* ── HUD Strip (collapsed state) ── */}
      {!hudOpen && barVisible && (
        <div style={{
          position: "sticky",
          bottom: 0,
          background: "rgba(6,10,18,.88)",
          borderTop: ".5px solid rgba(30,41,59,.25)",
          zIndex: 40,
        }}>
          <div style={{ padding: "7px 14px", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <button
              onClick={() => reflectUrl ? router.push(reflectUrl) : (setHudOpen(true), setBarVisible(true))}
              style={{ ...glassBtn(CYAN), fontSize: 8, padding: "4px 13px", gap: 6 }}
            >
              <span style={{ fontSize: 10 }}>◎</span>
              <span>Reflect</span>
              <span style={{ opacity: .45, marginLeft: 2, fontSize: 8 }}>{reflectUrl ? "→" : "↑"}</span>
            </button>
            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <span style={{ fontFamily: font.mono, fontSize: 7, color: "rgba(71,85,105,.4)", letterSpacing: ".06em" }}>
                {annotations.length} annotation{annotations.length !== 1 ? "s" : ""}
              </span>
              <button
                onClick={() => { setBarVisible(false); if (reflectUrl) router.back() }}
                style={{ background: "none", border: "none", padding: "2px 4px", cursor: "pointer", fontFamily: font.mono, fontSize: 8, color: "rgba(71,85,105,.5)", lineHeight: 1 }}
                title="Dismiss reflect bar"
              >✕</button>
            </div>
          </div>
        </div>
      )}

      {/* ── Selection picker — appears on any text highlight when reflect is open ── */}
      {selectionPicker && (
        <div
          ref={pickerContainerRef}
          style={{
            position: "fixed",
            top: selectionPicker.y,
            left: selectionPicker.x,
            width: 264,
            zIndex: 60,
            background: "rgba(8,12,20,.95)",
            border: ".5px solid rgba(30,41,59,.5)",
            borderRadius: 8,
            overflow: "hidden",
            boxShadow: "0 4px 24px rgba(0,0,0,.5), 0 0 0 .5px rgba(0,240,255,.06)",
          }}
        >
          {/* Top glow */}
          <div style={{ height: ".5px", background: "linear-gradient(90deg,transparent,rgba(0,240,255,.2) 30%,rgba(0,240,255,.2) 70%,transparent)" }} />

          {/* Anchor quote */}
          <div style={{
            padding: "7px 12px 6px",
            borderBottom: ".5px solid rgba(30,41,59,.3)",
            fontFamily: font.mono, fontSize: 8,
            color: "rgba(71,85,105,.5)", lineHeight: 1.4,
          }}>
            "{selectionPicker.anchorText.slice(0, 48)}{selectionPicker.anchorText.length > 48 ? "…" : ""}"
          </div>

          {/* 3×2 picker grid */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr" }}>
            {([
              { type: "THOUGHT" as const, emoji: "💭", label: "Thought", key: "~", color: CYAN },
              { type: "COMMENT" as const,  emoji: "💬", label: "Comment", key: "!", color: GOLD },
              { type: "REACTION" as const, emoji: "🗯️", label: "React",   key: "@", color: RED },
            ]).map(({ type, emoji, label, key, color }, i) => (
              <button
                key={type}
                onClick={() => pickInstrument(type)}
                style={{
                  background: "transparent",
                  border: "none",
                  borderRight: i < 2 ? ".5px solid rgba(30,41,59,.3)" : "none",
                  cursor: "pointer",
                  padding: "10px 6px 9px",
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  gap: 5,
                  transition: "background .12s",
                }}
                onMouseEnter={(e) => { (e.currentTarget as HTMLButtonElement).style.background = `${color}0c` }}
                onMouseLeave={(e) => { (e.currentTarget as HTMLButtonElement).style.background = "transparent" }}
              >
                {/* Row 1 — emoji */}
                <span style={{ fontSize: 20, lineHeight: 1 }}>{emoji}</span>
                {/* Row 2 — label + hotkey */}
                <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 2 }}>
                  <span style={{ fontFamily: font.mono, fontSize: 8, fontWeight: 700, letterSpacing: ".05em", color: `${color}bb`, textTransform: "uppercase" }}>{label}</span>
                  <span style={{ fontFamily: font.mono, fontSize: 8, color: "rgba(71,85,105,.4)", letterSpacing: ".02em" }}>{key}</span>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* ── Annotation popover ── */}
      {draft && activeInstrument && (
        <div
          style={{
            position: "absolute",
            top: draft.y,
            left: Math.min(draft.x, window.innerWidth - 280),
            width: 268,
            background: "rgba(6,10,18,.97)",
            backdropFilter: "blur(16px)",
            WebkitBackdropFilter: "blur(16px)",
            border: `.5px solid ${TYPE_COLOR[activeInstrument]}40`,
            borderRadius: 8,
            padding: 12,
            zIndex: 50,
            boxShadow: `0 8px 32px rgba(0,0,0,.7), 0 0 0 .5px rgba(0,0,0,.4)`,
          }}
        >
          {/* Top hairline glow */}
          <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: ".5px", background: `linear-gradient(90deg,transparent,${TYPE_COLOR[activeInstrument]}33 40%,${TYPE_COLOR[activeInstrument]}33 60%,transparent)` }} />

          <div style={{ fontFamily: font.mono, fontSize: 9, fontWeight: 700, letterSpacing: ".1em", color: `${TYPE_COLOR[activeInstrument]}cc`, textTransform: "uppercase", marginBottom: 7 }}>
            {TYPE_ICON[activeInstrument]} {activeInstrument}
          </div>
          <div style={{ fontFamily: font.mono, fontSize: 9, color: "rgba(148,163,184,.6)", borderLeft: `.5px solid ${TYPE_COLOR[activeInstrument]}30`, paddingLeft: 8, marginBottom: 10, lineHeight: 1.5 }}>
            "{draft.anchorText.slice(0, 70)}{draft.anchorText.length > 70 ? "…" : ""}"
          </div>

          {activeInstrument === "REACTION" ? (
            // Reaction picker — no text, just chips
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 4 }}>
              {REACTIONS.map((r) => (
                <button
                  key={r}
                  onClick={() => submitAnnotation(r)}
                  style={{
                    fontFamily: font.mono, fontSize: 9, padding: "5px 8px",
                    border: `.5px solid ${border.subtle}`, borderRadius: 3,
                    background: "transparent", color: text.secondary, cursor: "pointer",
                    textAlign: "center",
                  }}
                >
                  {r}
                </button>
              ))}
            </div>
          ) : (
            // Thought / Comment textarea
            <>
              <textarea
                value={draftBody}
                onChange={(e) => setDraftBody(e.target.value)}
                maxLength={400}
                autoFocus
                placeholder={`Your ${activeInstrument.toLowerCase()}…`}
                onKeyDown={(e) => { if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) submitAnnotation() }}
                style={{
                  width: "100%",
                  background: "rgba(10,15,26,.8)",
                  border: `.5px solid ${border.subtle}`,
                  borderRadius: 4,
                  color: "#e2e8f0",
                  fontFamily: font.mono,
                  fontSize: 11,
                  padding: "6px 8px",
                  resize: "none",
                  height: 64,
                  outline: "none",
                  lineHeight: 1.4,
                }}
              />

              <div style={{ marginTop: 6, display: "flex", alignItems: "center", gap: 4 }}>
                <div style={{ flex: 1 }} />
                <button onClick={() => { setDraft(null); setDraftBody("") }} style={{ ...glassBtn(), fontSize: 7, padding: "3px 8px" }}>Cancel</button>
                <button onClick={() => submitAnnotation()} disabled={!draftBody.trim()} style={{ ...glassBtn(CYAN), fontSize: 7, padding: "3px 10px", opacity: draftBody.trim() ? 1 : .4 }}>Save →</button>
              </div>
            </>
          )}
        </div>
      )}

      {/* ── Expanded chip modal ── */}
      {expandedChip && (
        <div
          onClick={(e) => { if (e.target === e.currentTarget) setExpandedChip(null) }}
          style={{ position: "fixed", inset: 0, background: "rgba(2,4,8,.7)", zIndex: 70, display: "flex", alignItems: "center", justifyContent: "center", padding: "1rem" }}
        >
          <div style={{
            background: "rgba(8,13,22,.96)",
            border: `.5px solid ${TYPE_COLOR[expandedChip.annotation.type]}20`,
            borderRadius: 8,
            padding: 16,
            width: "100%",
            maxWidth: 420,
            position: "relative",
            overflow: "hidden",
          }}>
            <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: ".5px", background: `linear-gradient(90deg,transparent,${TYPE_COLOR[expandedChip.annotation.type]}28 30%,${TYPE_COLOR[expandedChip.annotation.type]}28 70%,transparent)` }} />
            <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 8 }}>
              <span style={{ fontFamily: font.mono, fontSize: 7, fontWeight: 700, letterSpacing: ".1em", color: `${TYPE_COLOR[expandedChip.annotation.type]}88`, textTransform: "uppercase" }}>
                {TYPE_ICON[expandedChip.annotation.type]} {expandedChip.annotation.type}
              </span>
              <span style={{ fontFamily: font.mono, fontSize: 7, color: "rgba(71,85,105,.4)" }}>·</span>
              <span style={{ fontFamily: font.mono, fontSize: 7, color: "rgba(71,85,105,.4)" }}>{new Date(expandedChip.annotation.createdAt).toLocaleDateString()}</span>
              {expandedChip.annotation.linkedRef && (() => {
                let lr: LinkedRef | null = null
                try { lr = JSON.parse(expandedChip.annotation.linkedRef) } catch { return null }
                if (!lr) return null
                return (
                  <div style={{ marginLeft: "auto", background: `${GOLD}0a`, border: `.5px solid ${GOLD}33`, borderRadius: 10, padding: "1px 7px", display: "flex", gap: 4 }}>
                    <span style={{ fontFamily: font.mono, fontSize: 6, fontWeight: 700, color: `${GOLD}99` }}>{lr.type.slice(0, 3)}</span>
                    <span style={{ fontSize: 7, color: `${GOLD}77` }}>{lr.label.slice(0, 24)}</span>
                  </div>
                )
              })()}
            </div>
            <div style={{ borderLeft: `.5px solid rgba(30,41,59,.5)`, paddingLeft: 9, marginBottom: 10, fontFamily: font.mono, fontSize: 7, color: "rgba(71,85,105,.5)", lineHeight: 1.5 }}>
              "{expandedChip.annotation.anchorText}"
            </div>
            <div style={{ fontSize: 11, color: text.primary, lineHeight: 1.65, marginBottom: 14 }}>
              {expandedChip.annotation.body}
            </div>
            {expandedChip.annotation.kernel && (
              <div style={{ marginBottom: 12, paddingTop: 10, borderTop: `.5px solid rgba(30,41,59,.35)` }}>
                <div style={{ fontFamily: font.mono, fontSize: 7, fontWeight: 700, letterSpacing: ".12em", color: expandedChip.annotation.hardened ? `${CYAN}55` : `${GREEN}55`, textTransform: "uppercase", marginBottom: 5 }}>
                  {expandedChip.annotation.hardened ? "💎 Hardened" : "☽ Kernel"}
                </div>
                <div style={{ fontFamily: font.mono, fontSize: 12, color: expandedChip.annotation.hardened ? `${CYAN}dd` : `${GREEN}dd`, lineHeight: 1.55 }}>{expandedChip.annotation.kernel}</div>
              </div>
            )}
            <div style={{ display: "flex", gap: 5, alignItems: "center" }}>
              {!expandedChip.annotation.kernel && (
                <button
                  onClick={() => distillKernel(expandedChip.annotation)}
                  disabled={expandedChip.distilling}
                  style={{ ...glassBtn(GREEN), fontSize: 8, padding: "5px 14px", opacity: expandedChip.distilling ? .6 : 1 }}
                >
                  {expandedChip.distilling ? "Distilling…" : "☽ Distill"}
                </button>
              )}
              {expandedChip.annotation.kernel && !expandedChip.annotation.hardened && (
                <button
                  onClick={() => hardenKernel(expandedChip.annotation.id)}
                  style={{ ...glassBtn(CYAN), fontSize: 8, padding: "5px 14px" }}
                >
                  💎 Harden
                </button>
              )}
              <div style={{ flex: 1 }} />
              <button onClick={() => deleteAnnotation(expandedChip.annotation.id)} style={{ ...glassBtn(RED), fontSize: 7, padding: "3px 9px" }}>Delete</button>
              <button onClick={() => setExpandedChip(null)} style={{ ...glassBtn(), fontSize: 7, padding: "3px 9px" }}>Close</button>
            </div>
          </div>
        </div>
      )}

    </div>
  )
}
