"use client"

import { useState, useEffect, useCallback, useRef } from "react"
import { useRouter } from "next/navigation"
import { font, signal, text, surface, border } from "@/ui/tokens"

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
  createdAt: string
}

interface LinkedRef {
  type: "RECEIPT" | "ADR" | "ATG_TRIBUTARY" | "WISDOM"
  id: string
  label: string
}

interface LinkResult {
  type: string
  id: string
  label: string
  meta?: string
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

const CURSORS: Record<string, string> = {
  THOUGHT: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24'%3E%3Ctext y='20' font-size='18'%3E%E2%9C%8F%3C/text%3E%3C/svg%3E") 4 20, text`,
  COMMENT: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24'%3E%3Ctext y='20' font-size='18'%3E%E2%9C%A6%3C/text%3E%3C/svg%3E") 4 20, text`,
  REACTION: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24'%3E%3Ctext y='20' font-size='18'%3E%E2%97%88%3C/text%3E%3C/svg%3E") 4 20, crosshair`,
}

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
  const [layers, setLayers] = useState(defaultLayers ?? { THOUGHT: true, COMMENT: true, REACTION: true })
  const [activeInstrument, setActiveInstrument] = useState<"THOUGHT" | "COMMENT" | "REACTION" | null>(null)
  const [annotations, setAnnotations] = useState<Annotation[]>([])
  const [draft, setDraft] = useState<DraftAnnotation | null>(null)
  const [draftBody, setDraftBody] = useState("")
  const [draftLinkedRef, setDraftLinkedRef] = useState<LinkedRef | null>(null)
  const [expandedChip, setExpandedChip] = useState<ExpandedChip | null>(null)
  const [shavasanaOpen, setShavasanaOpen] = useState(false)
  const [shavasanaIdx, setShavasanaIdx] = useState(0)
  const [shavasanaFilter, setShavasanaFilter] = useState<"ALL" | "THOUGHT" | "COMMENT" | "REACTION">("ALL")
  const [meditateOpen, setMeditateOpen] = useState(false)
  const [meditateLoading, setMeditateLoading] = useState(false)
  const [meditateResult, setMeditateResult] = useState<{ held: string[]; falsified: string[]; elevated: string[] } | null>(null)
  const [linkPickerOpen, setLinkPickerOpen] = useState(false)
  const [linkQuery, setLinkQuery] = useState("")
  const [linkType, setLinkType] = useState<string>("ALL")
  const [linkResults, setLinkResults] = useState<LinkResult[]>([])
  const [narrow, setNarrow] = useState(false)
  // Floating selection picker — appears on any text highlight; dismissed on Escape / click-outside
  const [selectionPicker, setSelectionPicker] = useState<{
    anchorText: string; preContext: string; postContext: string
    x: number; y: number  // viewport coords
  } | null>(null)
  const linkSearchTimer = useRef<ReturnType<typeof setTimeout> | null>(null)
  // Ref mirror so hotkey handler can read selectionPicker without stale closure
  const selectionPickerRef = useRef<typeof selectionPicker>(null)

  // Responsive — collapse margins on narrow viewports
  useEffect(() => {
    const mq = window.matchMedia("(max-width: 760px)")
    const sync = () => setNarrow(mq.matches)
    sync()
    mq.addEventListener("change", sync)
    return () => mq.removeEventListener("change", sync)
  }, [])

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
        setDraft(null)
        setDraftBody("")
        setDraftLinkedRef(null)
        setLinkPickerOpen(false)
        setExpandedChip(null)
        if (shavasanaOpen) setShavasanaOpen(false)
      }
    }
    document.addEventListener("keydown", handler)
    return () => document.removeEventListener("keydown", handler)
  }, [shavasanaOpen])

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
        setDraftLinkedRef(null)
        setSelectionPicker(null)
      } else {
        setHudOpen(true)
        setActiveInstrument((prev) => prev === instrument ? null : instrument)
      }
    }
    document.addEventListener("keydown", handler)
    return () => document.removeEventListener("keydown", handler)
  }, [])

  // Text selection → floating picker. Show picker on any selection ≥ 3 chars
  // when the HUD is open. Instrument pre-arming is no longer required.
  const handleMouseUp = useCallback((e: MouseEvent) => {
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
  }, [hudOpen])

  useEffect(() => {
    document.addEventListener("mouseup", handleMouseUp)
    return () => document.removeEventListener("mouseup", handleMouseUp)
  }, [handleMouseUp])

  // Dismiss picker on mousedown outside it
  useEffect(() => {
    const handler = () => {
      // fired before mouseup; only clear if no new selection will appear
      // (handleMouseUp will re-set it if selection is kept)
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
    setDraftLinkedRef(null)
    setLinkPickerOpen(false)
    selectionPickerRef.current = null
    setSelectionPicker(null)
  }

  // Link search
  useEffect(() => {
    if (!linkPickerOpen) return
    if (linkSearchTimer.current) clearTimeout(linkSearchTimer.current)
    linkSearchTimer.current = setTimeout(() => {
      const params = new URLSearchParams({ q: linkQuery, type: linkType })
      fetch(`/api/annotations/link-search?${params}`)
        .then((r) => r.json())
        .then((d) => { if (d.ok) setLinkResults(d.results) })
        .catch(() => {})
    }, 200)
    return () => { if (linkSearchTimer.current) clearTimeout(linkSearchTimer.current) }
  }, [linkQuery, linkType, linkPickerOpen])

  async function submitAnnotation(reactionBody?: string) {
    if (!draft || !activeInstrument) return
    const body = reactionBody ?? draftBody.trim()
    if (!body) return

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
        linkedRef: draftLinkedRef ?? undefined,
      }),
    })
    const d = await res.json()
    if (d.ok) {
      setAnnotations((prev) => [...prev, d.annotation])
      setDraft(null)
      setDraftBody("")
      setDraftLinkedRef(null)
      setLinkPickerOpen(false)
      window.getSelection()?.removeAllRanges()
    }
  }

  async function deleteAnnotation(id: string) {
    await fetch(`/api/annotations/${id}`, { method: "DELETE" })
    setAnnotations((prev) => prev.filter((a) => a.id !== id))
    setExpandedChip(null)
  }

  async function distillKernel(annotation: Annotation) {
    setExpandedChip((prev) => prev ? { ...prev, distilling: true } : null)
    const res = await fetch(`/api/annotations/${annotation.id}/shavasana`, { method: "POST" })
    const d = await res.json()
    if (d.ok) {
      setAnnotations((prev) => prev.map((a) => a.id === annotation.id ? { ...a, kernel: d.kernel } : a))
      setExpandedChip((prev) => prev ? { ...prev, annotation: { ...prev.annotation, kernel: d.kernel }, distilling: false } : null)
    }
  }

  async function runMeditate() {
    setMeditateLoading(true)
    setMeditateOpen(true)
    setMeditateResult(null)
    try {
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

  const shavasanaAnnotations = annotations.filter((a) =>
    shavasanaFilter === "ALL" ? true : a.type === shavasanaFilter
  )
  const currentShav = shavasanaAnnotations[shavasanaIdx]

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

  return (
    <div style={{ position: "relative", minHeight: "100vh" }}>
      {/* Two-column layout: [300px left rail | content] when HUD open */}
      <div style={{
        display: showRail ? "grid" : "block",
        gridTemplateColumns: showRail ? "300px 1fr" : undefined,
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
                  <span style={{ fontFamily: font.mono, fontSize: 9, fontWeight: 700, letterSpacing: ".12em", color: "rgba(0,240,255,.6)", textTransform: "uppercase" }}>◎ Reflect</span>
                  <span style={{ fontFamily: font.mono, fontSize: 7, color: "rgba(71,85,105,.4)" }}>·</span>
                  <span style={{ fontFamily: font.mono, fontSize: 7, color: "rgba(71,85,105,.5)", letterSpacing: ".06em" }}>{surfaceProp}</span>
                </div>
                <button onClick={() => { setHudOpen(false); setActiveInstrument(null) }} style={{ ...glassBtn(), fontSize: 7, padding: "3px 9px" }}>↓ close</button>
              </div>

              {/* Filter pills */}
              <div style={{ display: "flex", gap: 4, flexWrap: "wrap" }}>
                {([
                  { key: "ALL" as const, label: `All · ${annotations.length}`, color: CYAN },
                  { key: "THOUGHT" as const, label: `${TYPE_ICON.THOUGHT} ${thoughtCount}`, color: CYAN },
                  { key: "COMMENT" as const, label: `${TYPE_ICON.COMMENT} ${commentCount}`, color: GOLD },
                  { key: "REACTION" as const, label: `${TYPE_ICON.REACTION} ${reactionCount}`, color: RED },
                ] as const).map(({ key, label, color }) => {
                  const active = railFilter === key
                  return (
                    <button
                      key={key}
                      onClick={() => setRailFilterAndLayers(key)}
                      style={{
                        fontFamily: font.mono,
                        fontSize: 8,
                        fontWeight: 700,
                        letterSpacing: ".06em",
                        padding: "3px 10px",
                        borderRadius: 20,
                        cursor: "pointer",
                        border: ".5px solid",
                        background: active ? `${color}12` : "rgba(10,15,26,.3)",
                        borderColor: active ? `${color}40` : "rgba(30,41,59,.3)",
                        color: active ? `${color}cc` : "rgba(71,85,105,.5)",
                        textTransform: "uppercase",
                      }}
                    >
                      {label}
                    </button>
                  )
                })}
              </div>

              {/* Hotkey legend */}
              <div style={{ marginTop: 8, fontFamily: font.mono, fontSize: 7, color: "rgba(71,85,105,.35)", letterSpacing: ".04em" }}>
                ~ Thought &nbsp;·&nbsp; ! Comment &nbsp;·&nbsp; @ Reaction
              </div>
            </div>

            {/* Annotations list — or Meditate view */}
            <div style={{ flex: 1, overflowY: "auto", padding: "8px 10px", display: "flex", flexDirection: "column", gap: 8 }}>

              {/* ── Meditate panel (SidelineList grammar from Doc UIKit) ── */}
              {meditateOpen && (
                <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                  {/* Meditate header */}
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 4 }}>
                    <span style={{ fontFamily: font.mono, fontSize: 8, fontWeight: 700, letterSpacing: ".1em", color: "rgba(0,255,157,.7)", textTransform: "uppercase" }}>📿 Meditate</span>
                    <button
                      onClick={() => setMeditateOpen(false)}
                      style={{ fontFamily: font.mono, fontSize: 7, color: "rgba(71,85,105,.5)", background: "none", border: "none", cursor: "pointer", padding: "2px 6px" }}
                    >
                      ← Annotations
                    </button>
                  </div>

                  {meditateLoading && (
                    <div style={{ fontFamily: font.mono, fontSize: 9, color: "rgba(0,255,157,.4)", textAlign: "center", padding: "24px 0", letterSpacing: ".08em" }}>
                      distilling beliefs…
                    </div>
                  )}

                  {!meditateLoading && meditateResult && (
                    <>
                      {/* Held — cyan */}
                      {meditateResult.held.length > 0 && (
                        <div style={{ display: "flex", flexDirection: "column", gap: 5 }}>
                          <div style={{ fontFamily: font.mono, fontSize: 7, fontWeight: 700, letterSpacing: ".1em", color: "rgba(0,240,255,.5)", textTransform: "uppercase", marginBottom: 2 }}>
                            Held under pressure
                          </div>
                          {meditateResult.held.map((item, i) => (
                            <div key={i} style={{
                              padding: "10px 12px",
                              borderRadius: 6,
                              background: "rgba(0,240,255,.04)",
                              border: ".5px solid rgba(0,240,255,.15)",
                              borderLeft: "2.5px solid rgba(0,240,255,.5)",
                            }}>
                              <p style={{ fontFamily: font.sans, fontSize: 12, color: "rgba(226,232,240,.8)", lineHeight: 1.55, margin: 0 }}>{item}</p>
                            </div>
                          ))}
                        </div>
                      )}

                      {/* Falsified — red */}
                      {meditateResult.falsified.length > 0 && (
                        <div style={{ display: "flex", flexDirection: "column", gap: 5, marginTop: 4 }}>
                          <div style={{ fontFamily: font.mono, fontSize: 7, fontWeight: 700, letterSpacing: ".1em", color: "rgba(255,77,109,.5)", textTransform: "uppercase", marginBottom: 2 }}>
                            Challenged
                          </div>
                          {meditateResult.falsified.map((item, i) => (
                            <div key={i} style={{
                              padding: "10px 12px",
                              borderRadius: 6,
                              background: "rgba(255,77,109,.04)",
                              border: ".5px solid rgba(255,77,109,.15)",
                              borderLeft: "2.5px solid rgba(255,77,109,.5)",
                            }}>
                              <p style={{ fontFamily: font.sans, fontSize: 12, color: "rgba(226,232,240,.8)", lineHeight: 1.55, margin: 0 }}>{item}</p>
                            </div>
                          ))}
                        </div>
                      )}

                      {/* Elevated — green */}
                      {meditateResult.elevated.length > 0 && (
                        <div style={{ display: "flex", flexDirection: "column", gap: 5, marginTop: 4 }}>
                          <div style={{ fontFamily: font.mono, fontSize: 7, fontWeight: 700, letterSpacing: ".1em", color: "rgba(0,255,157,.5)", textTransform: "uppercase", marginBottom: 2 }}>
                            Elevated
                          </div>
                          {meditateResult.elevated.map((item, i) => (
                            <div key={i} style={{
                              padding: "10px 12px",
                              borderRadius: 6,
                              background: "rgba(0,255,157,.04)",
                              border: ".5px solid rgba(0,255,157,.15)",
                              borderLeft: "2.5px solid rgba(0,255,157,.5)",
                            }}>
                              <p style={{ fontFamily: font.sans, fontSize: 12, color: "rgba(226,232,240,.8)", lineHeight: 1.55, margin: 0 }}>{item}</p>
                            </div>
                          ))}
                        </div>
                      )}

                      {/* Continue to Shavasana */}
                      <div style={{ marginTop: 8, paddingTop: 8, borderTop: ".5px solid rgba(30,41,59,.3)" }}>
                        <button
                          onClick={() => { setShavasanaOpen(true); setShavasanaIdx(0); setShavasanaFilter("ALL"); setMeditateOpen(false) }}
                          disabled={annotations.length === 0}
                          style={{ ...glassBtn(GREEN), fontSize: 7, padding: "5px 12px", width: "100%", justifyContent: "center" }}
                        >
                          ☽ Continue to Shavasana
                        </button>
                      </div>
                    </>
                  )}
                </div>
              )}

              {!meditateOpen && railAnnotations.length === 0 && (
                <div style={{ fontFamily: font.mono, fontSize: 9, color: "rgba(71,85,105,.3)", textAlign: "center", marginTop: 24, lineHeight: 1.6 }}>
                  {activeInstrument
                    ? `${TYPE_ICON[activeInstrument]} Select text to annotate`
                    : "Select an instrument below\nto begin annotating"}
                </div>
              )}
              {!meditateOpen && railAnnotations.map((a) => {
                const c = TYPE_COLOR[a.type]
                const isExpanded = expandedChip?.annotation.id === a.id
                const kernelText = isExpanded ? expandedChip?.annotation.kernel : a.kernel
                return (
                  <div
                    key={a.id}
                    style={{
                      borderRadius: 5,
                      border: `.5px solid ${c}20`,
                      background: `${c}05`,
                      overflow: "hidden",
                    }}
                  >
                    {/* Card top hairline glow */}
                    <div style={{ height: ".5px", background: `linear-gradient(90deg,transparent,${c}25 30%,${c}25 70%,transparent)` }} />

                    <div style={{ padding: "8px 9px" }}>
                      {/* Type badge + date */}
                      <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 6 }}>
                        <span style={{
                          fontFamily: font.mono, fontSize: 7, fontWeight: 700, letterSpacing: ".08em",
                          color: `${c}aa`, textTransform: "uppercase",
                          background: `${c}0d`, border: `.5px solid ${c}28`,
                          padding: "1px 6px", borderRadius: 10,
                        }}>
                          {TYPE_ICON[a.type]} {a.type === "THOUGHT" ? "TH" : a.type === "COMMENT" ? "CO" : "RE"}
                        </span>
                        <span style={{ fontFamily: font.mono, fontSize: 7, color: "rgba(71,85,105,.4)" }}>
                          {new Date(a.createdAt).toLocaleDateString("en-US", { month: "short", day: "numeric" })}
                        </span>
                        {a.linkedRef && (() => {
                          try {
                            const lr: LinkedRef = JSON.parse(a.linkedRef)
                            return <span style={{ fontFamily: font.mono, fontSize: 6, color: `${GOLD}66`, marginLeft: "auto", border: `.5px solid ${GOLD}22`, borderRadius: 8, padding: "1px 5px" }}>{lr.type.slice(0, 3)}</span>
                          } catch { return null }
                        })()}
                      </div>

                      {/* Anchor quote */}
                      <div style={{
                        borderLeft: `2px solid ${c}35`,
                        paddingLeft: 8, marginBottom: 7,
                        fontFamily: font.mono, fontSize: 8,
                        color: "rgba(71,85,105,.55)", lineHeight: 1.45,
                        fontStyle: "italic",
                      }}>
                        "{a.anchorText.slice(0, 70)}{a.anchorText.length > 70 ? "…" : ""}"
                      </div>

                      {/* Body */}
                      <div style={{ fontSize: 11, color: text.primary, lineHeight: 1.6, marginBottom: 8 }}>
                        {a.body}
                      </div>

                      {/* Kernel block */}
                      {kernelText && (
                        <div style={{
                          marginBottom: 8, paddingTop: 7, borderTop: `.5px solid rgba(30,41,59,.3)`,
                        }}>
                          <div style={{ fontFamily: font.mono, fontSize: 6, fontWeight: 700, letterSpacing: ".12em", color: `${GREEN}44`, textTransform: "uppercase", marginBottom: 4 }}>☽ kernel</div>
                          <div style={{ fontFamily: font.mono, fontSize: 11, color: `${GREEN}cc`, lineHeight: 1.55 }}>{kernelText}</div>
                        </div>
                      )}

                      {/* Actions */}
                      <div style={{ display: "flex", gap: 4, alignItems: "center" }}>
                        {!kernelText && (
                          <button
                            onClick={() => {
                              setExpandedChip({ annotation: a, distilling: true })
                              distillKernel(a)
                            }}
                            style={{ ...glassBtn(GREEN), fontSize: 7, padding: "3px 9px" }}
                          >
                            {expandedChip?.annotation.id === a.id && expandedChip?.distilling ? "…" : "☽ Distill"}
                          </button>
                        )}
                        <div style={{ flex: 1 }} />
                        <button
                          onClick={() => deleteAnnotation(a.id)}
                          style={{ ...glassBtn(RED), fontSize: 7, padding: "3px 8px" }}
                        >
                          ✕
                        </button>
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>

            {/* Rail footer — instrument buttons */}
            <div style={{
              padding: "9px 10px",
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
                        fontFamily: font.mono, fontSize: 8, fontWeight: 700,
                        padding: "6px 4px", borderRadius: 4, cursor: "pointer",
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
                <div style={{ fontFamily: font.mono, fontSize: 7, color: `${TYPE_COLOR[activeInstrument]}66`, textAlign: "center", letterSpacing: ".06em" }}>
                  {TYPE_ICON[activeInstrument]} Select text to annotate · Esc to cancel
                </div>
              )}
              <div style={{ display: "flex", gap: 4 }}>
                <button
                  onClick={runMeditate}
                  disabled={annotations.length === 0 || meditateLoading}
                  style={{ ...glassBtn(GREEN), fontSize: 7, padding: "5px 10px", flex: 1, justifyContent: "center", opacity: annotations.length === 0 ? .3 : 1 }}
                >
                  📿 Meditate
                </button>
                <button
                  onClick={() => { setShavasanaOpen(true); setShavasanaIdx(0); setShavasanaFilter("ALL") }}
                  disabled={annotations.length === 0}
                  style={{ ...glassBtn(GREEN), fontSize: 7, padding: "5px 10px", flex: 1, justifyContent: "center", opacity: annotations.length === 0 ? .3 : 1 }}
                >
                  ☽ Shavasana
                </button>
              </div>
            </div>
          </div>
        )}

        {/* ── Content ── */}
        <div style={{ cursor: activeInstrument ? CURSORS[activeInstrument] : undefined }}>
          {children}
        </div>
      </div>

      {/* ── HUD Strip (collapsed state only — rail handles open state) ── */}
      {!hudOpen && (
        <div style={{
          position: "sticky",
          bottom: 0,
          background: "rgba(6,10,18,.88)",
          borderTop: ".5px solid rgba(30,41,59,.25)",
          zIndex: 40,
        }}>
          <div style={{ padding: "7px 14px", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <button
              onClick={() => reflectUrl ? router.push(reflectUrl) : setHudOpen(true)}
              style={{ ...glassBtn(CYAN), fontSize: 8, padding: "4px 13px", gap: 6 }}
            >
              <span style={{ fontSize: 10 }}>◎</span>
              <span>Reflect</span>
              <span style={{ opacity: .45, marginLeft: 2, fontSize: 8 }}>{reflectUrl ? "→" : "↑"}</span>
            </button>
            <span style={{ fontFamily: font.mono, fontSize: 7, color: "rgba(71,85,105,.4)", letterSpacing: ".06em" }}>
              {annotations.length} annotation{annotations.length !== 1 ? "s" : ""}
            </span>
          </div>
        </div>
      )}

      {/* ── Selection picker — appears on any text highlight when reflect is open ── */}
      {selectionPicker && (
        <div
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
          onMouseDown={(e) => e.stopPropagation()}
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
            left: Math.min(draft.x, window.innerWidth - 240),
            width: 230,
            background: "rgba(8,12,20,.92)",
            border: `.5px solid ${TYPE_COLOR[activeInstrument]}28`,
            borderRadius: 6,
            padding: 10,
            zIndex: 50,
            boxShadow: `0 0 20px rgba(0,0,0,.5)`,
          }}
        >
          {/* Top hairline glow */}
          <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: ".5px", background: `linear-gradient(90deg,transparent,${TYPE_COLOR[activeInstrument]}33 40%,${TYPE_COLOR[activeInstrument]}33 60%,transparent)` }} />

          <div style={{ fontFamily: font.mono, fontSize: 7, fontWeight: 700, letterSpacing: ".1em", color: `${TYPE_COLOR[activeInstrument]}88`, textTransform: "uppercase", marginBottom: 6 }}>
            {TYPE_ICON[activeInstrument]} {activeInstrument}
          </div>
          <div style={{ fontFamily: font.mono, fontSize: 7, color: "rgba(71,85,105,.5)", borderLeft: ".5px solid rgba(30,41,59,.5)", paddingLeft: 7, marginBottom: 8, lineHeight: 1.5 }}>
            "{draft.anchorText.slice(0, 60)}{draft.anchorText.length > 60 ? "…" : ""}"
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
                  background: "rgba(4,7,14,.6)",
                  border: `.5px solid ${border.subtle}`,
                  borderRadius: 4,
                  color: text.primary,
                  fontFamily: font.mono,
                  fontSize: 9,
                  padding: "6px 8px",
                  resize: "none",
                  height: 52,
                  outline: "none",
                  lineHeight: 1.4,
                }}
              />

              {/* Linked artifact */}
              {draftLinkedRef && (
                <div style={{ display: "flex", alignItems: "center", gap: 6, marginTop: 5, background: "rgba(10,15,26,.5)", border: `.5px solid ${border.subtle}`, borderRadius: 3, padding: "4px 7px" }}>
                  <span style={{ fontFamily: font.mono, fontSize: 7, fontWeight: 700, color: GOLD }}>{draftLinkedRef.type.slice(0, 3)}</span>
                  <span style={{ fontSize: 8, color: text.secondary, flex: 1, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{draftLinkedRef.label}</span>
                  <button onClick={() => setDraftLinkedRef(null)} style={{ background: "none", border: "none", color: "rgba(71,85,105,.5)", cursor: "pointer", fontSize: 10, padding: 0 }}>✕</button>
                </div>
              )}

              <div style={{ marginTop: 6, display: "flex", alignItems: "center", gap: 4 }}>
                <button onClick={() => setLinkPickerOpen((p) => !p)} style={{ ...glassBtn(), fontSize: 7, padding: "3px 8px" }}>+ Link</button>
                <div style={{ flex: 1 }} />
                <button onClick={() => { setDraft(null); setDraftBody("") }} style={{ ...glassBtn(), fontSize: 7, padding: "3px 8px" }}>Cancel</button>
                <button onClick={() => submitAnnotation()} disabled={!draftBody.trim()} style={{ ...glassBtn(CYAN), fontSize: 7, padding: "3px 10px", opacity: draftBody.trim() ? 1 : .4 }}>Save →</button>
              </div>

              {/* Link picker dropdown */}
              {linkPickerOpen && (
                <div style={{ position: "absolute", top: "100%", left: 0, right: 0, marginTop: 4, background: "rgba(8,12,20,.96)", border: `.5px solid ${border.subtle}`, borderRadius: 5, zIndex: 60, overflow: "hidden" }}>
                  <div style={{ padding: "5px 8px", borderBottom: `.5px solid rgba(30,41,59,.3)` }}>
                    <input
                      value={linkQuery}
                      onChange={(e) => setLinkQuery(e.target.value)}
                      placeholder="search…"
                      autoFocus
                      style={{ width: "100%", background: "rgba(4,7,14,.5)", border: `.5px solid ${border.subtle}`, borderRadius: 3, color: text.primary, fontFamily: font.mono, fontSize: 8, padding: "3px 7px", outline: "none" }}
                    />
                  </div>
                  <div style={{ display: "flex", gap: 3, padding: "4px 7px", borderBottom: `.5px solid rgba(30,41,59,.2)`, flexWrap: "wrap" }}>
                    {["ALL", "RECEIPT", "ADR", "ATG_TRIBUTARY", "WISDOM"].map((t) => (
                      <button key={t} onClick={() => setLinkType(t)} style={{ ...glassBtn(linkType === t ? CYAN : undefined), fontSize: 6, padding: "2px 6px", borderRadius: 10 }}>{t === "ATG_TRIBUTARY" ? "Tributary" : t.slice(0, 7)}</button>
                    ))}
                  </div>
                  <div style={{ maxHeight: 160, overflowY: "auto" }}>
                    {linkResults.map((r) => (
                      <div
                        key={`${r.type}-${r.id}`}
                        onClick={() => { setDraftLinkedRef({ type: r.type as LinkedRef["type"], id: r.id, label: r.label }); setLinkPickerOpen(false) }}
                        style={{ padding: "5px 9px", borderBottom: `.5px solid rgba(15,21,32,.6)`, cursor: "pointer", display: "flex", gap: 7, alignItems: "flex-start" }}
                      >
                        <span style={{ fontFamily: font.mono, fontSize: 7, fontWeight: 700, color: GOLD, minWidth: 26, paddingTop: 1 }}>{r.type.slice(0, 3)}</span>
                        <div>
                          <div style={{ fontSize: 9, color: text.secondary, lineHeight: 1.3 }}>{r.label.slice(0, 60)}</div>
                          {r.meta && <div style={{ fontFamily: font.mono, fontSize: 7, color: "rgba(71,85,105,.5)", marginTop: 1 }}>{r.meta}</div>}
                        </div>
                      </div>
                    ))}
                    {linkResults.length === 0 && (
                      <div style={{ padding: "8px 9px", fontFamily: font.mono, fontSize: 8, color: "rgba(71,85,105,.4)" }}>No results</div>
                    )}
                  </div>
                </div>
              )}
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
                const lr: LinkedRef = JSON.parse(expandedChip.annotation.linkedRef)
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
                <div style={{ fontFamily: font.mono, fontSize: 7, fontWeight: 700, letterSpacing: ".12em", color: `${GREEN}55`, textTransform: "uppercase", marginBottom: 5 }}>☽ Kernel</div>
                <div style={{ fontFamily: font.mono, fontSize: 12, color: `${GREEN}dd`, lineHeight: 1.55 }}>{expandedChip.annotation.kernel}</div>
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
              <div style={{ flex: 1 }} />
              <button onClick={() => deleteAnnotation(expandedChip.annotation.id)} style={{ ...glassBtn(RED), fontSize: 7, padding: "3px 9px" }}>Delete</button>
              <button onClick={() => setExpandedChip(null)} style={{ ...glassBtn(), fontSize: 7, padding: "3px 9px" }}>Close</button>
            </div>
          </div>
        </div>
      )}

      {/* ── Shavasana Overlay ── */}
      {shavasanaOpen && (
        <div style={{ position: "fixed", inset: 0, background: "rgba(2,4,8,.94)", zIndex: 80, display: "flex", flexDirection: "column", padding: 20, overflowY: "auto" }}>
          {/* Header */}
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
            <span style={{ fontFamily: font.mono, fontSize: 9, fontWeight: 700, letterSpacing: ".14em", color: `${GREEN}70`, textTransform: "uppercase" }}>☽ Shavasana</span>
            <div style={{ flex: 1, height: ".5px", background: `${GREEN}14` }} />
            {/* Filter pills */}
            <div style={{ display: "flex", gap: 4 }}>
              {(["ALL", "THOUGHT", "COMMENT", "REACTION"] as const).map((f) => (
                <button
                  key={f}
                  onClick={() => { setShavasanaFilter(f); setShavasanaIdx(0) }}
                  style={{
                    ...glassBtn(shavasanaFilter === f ? CYAN : undefined),
                    fontSize: 6, padding: "2px 8px", borderRadius: 10,
                  }}
                >
                  {f === "ALL" ? `All (${annotations.length})` : `${TYPE_ICON[f]} ${annotations.filter(a => a.type === f).length}`}
                </button>
              ))}
            </div>
            <div style={{ width: ".5px", height: 14, background: "rgba(30,41,59,.4)" }} />
            <button onClick={() => setShavasanaOpen(false)} style={{ ...glassBtn(), fontSize: 8, padding: "3px 9px" }}>✕</button>
          </div>

          {shavasanaAnnotations.length === 0 ? (
            <div style={{ fontFamily: font.mono, fontSize: 10, color: "rgba(71,85,105,.4)", textAlign: "center", marginTop: 40 }}>No annotations in this layer</div>
          ) : currentShav && (
            <>
              {/* Annotation card */}
              <div style={{
                background: "rgba(8,13,22,.75)",
                border: `.5px solid ${TYPE_COLOR[currentShav.type]}18`,
                borderRadius: 8,
                padding: 16,
                flex: 1,
                maxWidth: 560,
                margin: "0 auto",
                width: "100%",
                position: "relative",
                overflow: "hidden",
              }}>
                <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: ".5px", background: `linear-gradient(90deg,transparent,${TYPE_COLOR[currentShav.type]}25 30%,${TYPE_COLOR[currentShav.type]}25 70%,transparent)` }} />
                <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 10 }}>
                  <span style={{ fontFamily: font.mono, fontSize: 7, fontWeight: 700, letterSpacing: ".1em", color: `${TYPE_COLOR[currentShav.type]}77`, textTransform: "uppercase" }}>
                    {TYPE_ICON[currentShav.type]} {currentShav.type}
                  </span>
                  <span style={{ fontFamily: font.mono, fontSize: 7, color: "rgba(71,85,105,.4)" }}>·</span>
                  <span style={{ fontFamily: font.mono, fontSize: 7, color: "rgba(71,85,105,.4)" }}>{new Date(currentShav.createdAt).toLocaleDateString()}</span>
                  {currentShav.linkedRef && (() => {
                    const lr: LinkedRef = JSON.parse(currentShav.linkedRef)
                    return (
                      <div style={{ marginLeft: "auto", background: `${GOLD}08`, border: `.5px solid ${GOLD}28`, borderRadius: 10, padding: "1px 7px", display: "flex", gap: 4 }}>
                        <span style={{ fontFamily: font.mono, fontSize: 6, fontWeight: 700, color: `${GOLD}80` }}>{lr.type.slice(0, 3)}</span>
                        <span style={{ fontSize: 7, color: `${GOLD}66` }}>{lr.label.slice(0, 28)}</span>
                      </div>
                    )
                  })()}
                </div>
                <div style={{ borderLeft: `.5px solid rgba(30,41,59,.45)`, paddingLeft: 9, marginBottom: 12, fontFamily: font.mono, fontSize: 8, color: "rgba(71,85,105,.5)", lineHeight: 1.5 }}>
                  "{currentShav.anchorText}"
                </div>
                <div style={{ fontSize: 12, color: text.primary, lineHeight: 1.7, marginBottom: 18 }}>
                  {currentShav.body}
                </div>

                {/* Distill / kernel */}
                {currentShav.kernel ? (
                  <div style={{ paddingTop: 14, borderTop: `.5px solid rgba(30,41,59,.35)` }}>
                    <div style={{ fontFamily: font.mono, fontSize: 7, fontWeight: 700, letterSpacing: ".14em", color: `${GREEN}44`, textTransform: "uppercase", marginBottom: 6 }}>☽ Kernel</div>
                    <div style={{ fontFamily: font.mono, fontSize: 16, color: `${GREEN}ee`, lineHeight: 1.6, letterSpacing: ".01em" }}>{currentShav.kernel}</div>
                  </div>
                ) : (
                  <button
                    onClick={async () => {
                      const res = await fetch(`/api/annotations/${currentShav.id}/shavasana`, { method: "POST" })
                      const d = await res.json()
                      if (d.ok) {
                        setAnnotations((prev) => prev.map((a) => a.id === currentShav.id ? { ...a, kernel: d.kernel } : a))
                      }
                    }}
                    style={{ ...glassBtn(GREEN), fontSize: 9, padding: "6px 16px" }}
                  >
                    ☽ Distill →
                  </button>
                )}
              </div>

              {/* Navigation */}
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginTop: 14, maxWidth: 560, margin: "14px auto 0", width: "100%" }}>
                <button
                  onClick={() => setShavasanaIdx((i) => Math.max(0, i - 1))}
                  disabled={shavasanaIdx === 0}
                  style={{ ...glassBtn(), fontSize: 8, padding: "5px 16px", opacity: shavasanaIdx === 0 ? .3 : 1 }}
                >← hold</button>
                <div style={{ flex: 1, display: "flex", justifyContent: "center", alignItems: "center", gap: 6 }}>
                  {shavasanaAnnotations.map((_, i) => (
                    <div
                      key={i}
                      onClick={() => setShavasanaIdx(i)}
                      style={{
                        width: i === shavasanaIdx ? 20 : 6,
                        height: i === shavasanaIdx ? 2 : 6,
                        borderRadius: i === shavasanaIdx ? 1 : "50%",
                        background: i === shavasanaIdx ? `${CYAN}cc` : "rgba(30,41,59,.5)",
                        cursor: "pointer",
                        transition: "all .2s",
                      }}
                    />
                  ))}
                </div>
                <button
                  onClick={() => setShavasanaIdx((i) => Math.min(shavasanaAnnotations.length - 1, i + 1))}
                  disabled={shavasanaIdx === shavasanaAnnotations.length - 1}
                  style={{ ...glassBtn(CYAN), fontSize: 8, padding: "5px 16px", opacity: shavasanaIdx === shavasanaAnnotations.length - 1 ? .3 : 1 }}
                >advance →</button>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  )
}
