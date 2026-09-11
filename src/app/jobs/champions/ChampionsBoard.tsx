"use client"

import React, { useCallback, useEffect, useMemo, useState } from "react"
import { surface, border, text, signal, font } from "@/ui/tokens"
import { useVw } from "@/ui/useVw"
import { Wordmark } from "@/ui/Wordmark"
import { Rule } from "@/ui/Rule"
import { SectionLabel } from "@/ui/SectionLabel"
import { Button } from "@/ui/Button"
import { AuthControl } from "@/molecules/AuthControl"
import { BoardTabs } from "@/ui/BoardTabs"

// The Champions lane. Same loop as the postings board (tiered stack-rank, Weight
// Lab live re-rank, swipe with why-tags, "generate on swipe"), a different rubric
// (champion-fit, warm_path DOMINANT) and data source (Zach's network, gated). All
// PII arrives from /api/champions, which is fail-closed; nothing is inlined here.
// Inline styles only; responsive through useVw (no media queries).

type Lane = "EXT-search" | "INT-basin"
type Dim = { key: string; label: string; weight: number; anchor0: string; anchor3: string }
type Spec = {
  version: string
  rubric: { dims: Dim[]; max: number; board_cutoff: number; tiers: { t1: number; t2: number; t3: number } }
  lanes: Record<Lane, { label: string; pitch: string; pattern: string; patternUrl: string }>
}
type Row = { id: string; lane: Lane; name: string; position: string; company: string; url: string; dims: Record<string, number>; composite: number; tags: string[] }
type Swipe = { direction: "r" | "l"; why: string | null; at: string }
type Payload = { rows: Row[]; spec: Spec; swipes: Record<string, Swipe> }

const WHY = ["keyword matcher", "big-agency down-seller", "single-lane filter", "title-flattener", "off-basin", "cold", "timing", "other"]
const TAG_OPTIONS = ["Warm", "Crossover", "Basin", "Founder-led"] as const
const LANE_LABEL: Record<Lane, string> = { "EXT-search": "External search", "INT-basin": "Internal basin" }
const TIER_LABEL: Record<number, [string, string]> = { 1: ["Tier 1", "0.52 and up · work these first"], 2: ["Tier 2", "0.36 to 0.51 · warm queue"], 3: ["Tier 3", "below 0.36 · watch"] }

const mono = font.mono
const sans = font.sans
const MEASURE = 620
const fg1 = text.primary, fg2 = text.secondary, fg3 = text.dimmed, fg4 = text.muted
const GLASS_CARD = "linear-gradient(160deg, rgba(255,255,255,.05), rgba(255,255,255,.01) 38%, rgba(0,0,0,.18)), linear-gradient(165deg, #11181f, #0a1016)"
const GLASS_BEVEL = "inset 0 1px 0 rgba(255,255,255,.10), inset 0 -2px 8px rgba(0,0,0,.5), 0 5px 16px rgba(0,0,0,.45)"
const SCREEN = "linear-gradient(180deg, #090d12, #0c1219)"
const SCREEN_INSET = "inset 0 2px 5px rgba(0,0,0,.55), inset 0 -1px 0 rgba(255,255,255,.04)"

const labelStyle: React.CSSProperties = { fontFamily: mono, fontSize: 10, fontWeight: 700, letterSpacing: "0.14em", textTransform: "uppercase", color: fg4 }
const smallLabel: React.CSSProperties = { fontFamily: mono, fontSize: 10, fontWeight: 700, letterSpacing: "0.12em", textTransform: "uppercase", color: fg4 }
const ctl: React.CSSProperties = { minHeight: 36, padding: "0 12px", background: SCREEN, border: `1px solid #1c2736`, borderRadius: 5, color: fg1, fontFamily: sans, fontSize: 13, boxShadow: SCREEN_INSET }
const rowCell: React.CSSProperties = { padding: 12, verticalAlign: "top", fontSize: 13, overflowWrap: "anywhere" }

function tierOf(c: number, spec: Spec): 1 | 2 | 3 | null {
  const t = spec.rubric.tiers
  return c >= t.t1 ? 1 : c >= t.t2 ? 2 : c >= t.t3 ? 3 : null
}
function Tag({ children }: { children: React.ReactNode }) {
  return <span style={{ display: "inline-block", padding: "1px 7px", borderRadius: 6, border: `1px solid ${signal.cyan}44`, background: `${signal.cyan}12`, color: signal.cyan, fontFamily: mono, fontSize: 10, fontWeight: 600, letterSpacing: ".06em", textTransform: "uppercase" }}>{children}</span>
}

export function ChampionsBoard() {
  const vw = useVw()
  const phone = vw < 640
  const tablet = vw < 1100
  const [data, setData] = useState<Payload | null>(null)
  const [err, setErr] = useState<string | null>(null)
  const [f, setF] = useState({ tier: "all", swipe: "all", lane: "all", tag: "all", q: "" })
  const [sort, setSort] = useState<{ key: "score" | "name" | "warm"; dir: "asc" | "desc" }>({ key: "score", dir: "desc" })
  const [open, setOpen] = useState<Record<string, boolean>>({})
  const [weights, setWeights] = useState<Record<string, number> | null>(null)
  const [labOpen, setLabOpen] = useState(false)
  const [busy, setBusy] = useState<string | null>(null)

  const load = useCallback(async () => {
    try {
      const r = await fetch("/api/champions", { cache: "no-store" })
      if (r.status === 401) { setErr("Sign in with your admin email to use the board."); return }
      if (!r.ok) throw new Error(`HTTP ${r.status}`)
      setData(await r.json())
    } catch (e) { setErr(e instanceof Error ? e.message : "Failed to load") }
  }, [])
  useEffect(() => { load() }, [load])

  const spec = data?.spec ?? null
  const DIMS = spec?.rubric.dims ?? []
  const MAX = spec?.rubric.max ?? 33

  // Weight Lab — recompute composite live from stored 0-3 dim scores against
  // adjustable weights, no server call, nothing written (same as the roles board).
  const effWeight = useCallback((k: string, fb: number) => weights?.[k] ?? fb, [weights])
  const recomposite = useCallback((r: Row): number => {
    if (!weights) return r.composite
    let raw = 0, max = 0
    for (const d of DIMS) { const w = effWeight(d.key, d.weight); raw += (r.dims[d.key] ?? 0) * w; max += 3 * w }
    return max ? +(raw / max).toFixed(3) : r.composite
  }, [weights, DIMS, effWeight])

  const rows = useMemo(() => {
    const src = data?.rows ?? []
    const withSwipe = src.map((r) => ({ ...r, composite: recomposite(r), swipe: data?.swipes[r.id] ?? null }))
    return withSwipe
  }, [data, recomposite])
  type LiveRow = Row & { swipe: Swipe | null }

  const scored = useMemo(() => (rows as LiveRow[]).filter((r) => tierOf(r.composite, spec!) !== null), [rows, spec])

  const visible = useMemo(() => {
    if (!spec) return []
    const q = f.q.trim().toLowerCase()
    return (scored as LiveRow[]).filter((r) => {
      const t = tierOf(r.composite, spec)
      const sw = r.swipe?.direction ?? "none"
      if (f.tier !== "all" && t !== Number(f.tier)) return false
      if (f.swipe !== "all" && sw !== f.swipe) return false
      if (f.lane !== "all" && r.lane !== f.lane) return false
      if (f.tag !== "all" && !r.tags.includes(f.tag)) return false
      if (q && !(r.name + " " + r.company + " " + r.position).toLowerCase().includes(q)) return false
      return true
    }).sort((a, b) => {
      const d = sort.dir === "asc" ? 1 : -1
      if (sort.key === "name") return d * a.name.localeCompare(b.name) || b.composite - a.composite
      if (sort.key === "warm") return d * ((a.dims.warm_path ?? 0) - (b.dims.warm_path ?? 0)) || b.composite - a.composite
      return d * (a.composite - b.composite) || a.name.localeCompare(b.name)
    })
  }, [scored, f, sort, spec])

  const rights = useMemo(() => (scored as LiveRow[]).filter((r) => r.swipe?.direction === "r").sort((a, b) => (a.swipe!.at < b.swipe!.at ? -1 : 1)), [scored])
  const swipesLog = useMemo(() => (scored as LiveRow[]).filter((r) => r.swipe).sort((a, b) => (a.swipe!.at > b.swipe!.at ? -1 : 1)), [scored])

  async function post(body: unknown, key: string) {
    setBusy(key)
    try {
      const r = await fetch("/api/champions/swipe", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) })
      if (!r.ok) { const j = await r.json().catch(() => ({})); setErr(j.error ?? `HTTP ${r.status}`); return }
      await load()
    } finally { setBusy(null) }
  }
  const swipe = (r: LiveRow, dir: "r" | "l") => post({ id: r.id, direction: r.swipe?.direction === dir ? null : dir, why: dir === "l" ? r.swipe?.why ?? null : null }, r.id)
  const why = (r: LiveRow, w: string) => post({ id: r.id, direction: "l", why: r.swipe?.why === w ? null : w }, r.id)
  const unswipe = (r: LiveRow) => post({ id: r.id, direction: null }, r.id)

  function pts(r: Row) { return DIMS.reduce((t, d) => t + (r.dims[d.key] ?? 0) * effWeight(d.key, d.weight), 0) }
  const effMax = weights ? DIMS.reduce((t, d) => t + 3 * effWeight(d.key, d.weight), 0) : MAX

  function anatomy(r: Row) {
    const total = pts(r)
    return (
      <div style={{ paddingTop: 12 }}>
        <div style={{ ...smallLabel, marginBottom: 8 }}>How the fit is built</div>
        <div style={{ fontFamily: mono, fontSize: 12, color: fg2, marginBottom: 8 }}><b style={{ color: fg1 }}>{total}</b> of {effMax} points = <b style={{ color: fg1 }}>{(total / effMax).toFixed(3)}</b> · each dimension 0 to 3, times its weight{weights ? " (Weight Lab active)" : ""}. Warm path leads.</div>
        {DIMS.map((x) => { const sc = r.dims[x.key] ?? 0; const w = effWeight(x.key, x.weight); const max = w * 3; return (
          <div key={x.key} title={`${x.anchor0} → ${x.anchor3}`} style={{ display: "grid", gridTemplateColumns: phone ? "128px 1fr 44px" : "168px 1fr 44px", gap: 8, alignItems: "center", padding: "3px 0" }}>
            <span style={{ fontSize: 12, color: fg2, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{x.label}<small style={{ color: weights && w !== x.weight ? signal.cyan : fg4, fontFamily: mono, fontSize: 10, marginLeft: 4 }}>×{w}</small></span>
            <span style={{ position: "relative", height: 8, background: SCREEN, borderRadius: 999, overflow: "hidden", boxShadow: "inset 0 2px 4px rgba(0,0,0,.65)" }}>
              <i style={{ position: "absolute", left: 0, top: 0, bottom: 0, width: sc === 0 ? 3 : `${(sc / 3) * 100}%`, background: sc === 0 ? signal.red : `linear-gradient(90deg, #1ec3d4, ${signal.cyan})`, borderRadius: 999, boxShadow: sc === 0 ? undefined : `0 0 8px -1px ${signal.cyan}` }} />
            </span>
            <span style={{ fontFamily: mono, fontSize: 12, color: fg1, textAlign: "right", fontVariantNumeric: "tabular-nums" }}>{sc * w}<small style={{ color: fg4 }}>/{max}</small></span>
          </div>) })}
        <p style={{ margin: "10px 0 0", fontSize: 12, color: fg2, maxWidth: MEASURE, textWrap: "pretty" }}><b style={{ color: fg1, fontWeight: 500 }}>On-call test (not scored here):</b> on first contact, do they name the crossover rarity back to you — unprompted, effortlessly, the way Amy did? That is what confirms a champion, not just fit. Capture it as the swipe outcome.</p>
      </div>
    )
  }

  // What a right swipe stages — the ADR-077 pairing, by lane. Not auto-generated:
  // the enablement/forge is a human-approved step (mirrors the roles board's gate).
  function bundleCell(r: LiveRow) {
    if (!spec) return null
    const l = spec.lanes[r.lane]
    if (r.swipe?.direction === "r") return (
      <div style={{ fontSize: 12, color: fg2 }}>
        <span style={{ ...smallLabel, color: signal.green, display: "block", marginBottom: 2 }}>staged · {l.label}</span>
        {l.pitch} <a href={l.patternUrl} target="_blank" rel="noopener" style={{ color: signal.cyan }}>{l.pattern}</a>
      </div>
    )
    return <span style={{ color: fg3, fontSize: 12 }}>Generate on swipe → <span style={{ color: fg4 }}>{r.lane === "EXT-search" ? "recruiter enablement" : "founder forge"}</span></span>
  }

  const th = (label: string, key?: "score" | "name" | "warm") => (
    <th style={{ ...smallLabel, textAlign: "left", padding: "8px 12px", background: surface.elevated, borderBottom: `1px solid ${border.subtle}`, whiteSpace: "nowrap", position: "sticky", top: 0 }}>
      {key ? <button onClick={() => setSort((s) => s.key === key ? { key, dir: s.dir === "asc" ? "desc" : "asc" } : { key, dir: key === "name" ? "asc" : "desc" })} style={{ background: "none", border: 0, padding: 0, color: sort.key === key ? fg1 : "inherit", cursor: "pointer", font: "inherit", letterSpacing: "inherit", textTransform: "inherit" }}>{label}{sort.key === key ? (sort.dir === "desc" ? " ▾" : " ▴") : ""}</button> : label}
    </th>
  )
  const seg = (name: keyof typeof f, opts: [string, string][]) => (
    <div role="group" style={{ display: "inline-flex", gap: 4, padding: 4, borderRadius: 6, background: SCREEN, boxShadow: "inset 0 2px 6px rgba(0,0,0,.7)" }}>
      {opts.map(([v, l]) => { const on = f[name] === v; return <button key={v} aria-pressed={on} onClick={() => setF({ ...f, [name]: v })} style={{ minHeight: phone ? 36 : 28, padding: "0 12px", border: `1px solid ${on ? "#00F0FF55" : "transparent"}`, borderRadius: 5, background: on ? "linear-gradient(180deg, #0d141c, #0f1822)" : "transparent", color: on ? "#b9e8f4" : fg3, cursor: "pointer", fontFamily: mono, fontWeight: 600, fontSize: 11, letterSpacing: "0.05em", whiteSpace: "nowrap" }}>{l}</button> })}
    </div>
  )

  function nameCell(r: LiveRow) {
    return (<>
      <b style={{ display: "block", fontWeight: 500, color: fg1, textWrap: "pretty" }}>{r.name}</b>
      <span style={{ color: fg2, fontSize: 12 }}>{r.position}{r.position ? " · " : ""}{r.company}</span>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 4, marginTop: 4 }}>
        <Tag>{LANE_LABEL[r.lane]}</Tag>
        {r.tags.map((t) => <span key={t} style={{ display: "inline-block", padding: "1px 7px", borderRadius: 6, border: `1px solid ${signal.gold}55`, background: `${signal.gold}14`, color: signal.gold, fontFamily: mono, fontSize: 10, fontWeight: 600, letterSpacing: ".06em", textTransform: "uppercase" }}>{t}</span>)}
      </div>
      <button onClick={() => setOpen({ ...open, [r.id]: !open[r.id] })} aria-expanded={!!open[r.id]} style={{ marginTop: 4, background: "none", border: 0, padding: 0, color: signal.cyan, fontSize: 12, cursor: "pointer" }}>{open[r.id] ? "Hide the score" : "Why this score"}</button>
    </>)
  }

  function swipeButtons(r: LiveRow) {
    const sw = r.swipe?.direction; const b = busy === r.id
    const base: React.CSSProperties = { minHeight: phone ? 44 : 36, minWidth: 36, padding: "0 12px", border: "1px solid #2a3647", borderRadius: 5, background: "linear-gradient(160deg, rgba(255,255,255,.06), rgba(255,255,255,.01) 38%, rgba(0,0,0,.18)), linear-gradient(165deg, #141c24, #0b1117)", color: "#cbd5e1", cursor: b ? "wait" : "pointer", fontFamily: mono, fontWeight: 600, fontSize: 11, letterSpacing: "0.085em", textTransform: "uppercase", whiteSpace: "nowrap", boxShadow: "inset 0 1px 0 rgba(255,255,255,.09), inset 0 -2px 7px rgba(0,0,0,.5), 0 4px 12px rgba(0,0,0,.4)", flex: phone ? 1 : undefined, opacity: b ? 0.6 : 1 }
    return (<>
      <div style={{ display: "flex", gap: phone ? 8 : 4 }}>
        <button disabled={b} aria-pressed={sw === "l"} onClick={() => swipe(r, "l")} style={{ ...base, ...(sw === "l" ? { color: "#f6c9d2", borderColor: "#FF4D6D99" } : {}) }}>← Pass</button>
        <button disabled={b} aria-pressed={sw === "r"} onClick={() => swipe(r, "r")} style={{ ...base, ...(sw === "r" ? { color: "#bdf2dc", borderColor: "#00FF9D99" } : {}) }}>Reach out →</button>
      </div>
      {sw === "l" && <div role="group" aria-label="Why not a champion" style={{ display: "flex", flexWrap: "wrap", gap: 4, marginTop: 4 }}>{WHY.map((w) => { const on = r.swipe?.why === w; return <button key={w} aria-pressed={on} onClick={() => why(r, w)} style={{ minHeight: phone ? 36 : 28, padding: "0 8px", border: `1px solid ${on ? signal.red : border.subtle}`, borderRadius: 999, background: on ? "#FF4D6D1a" : surface.panel, color: on ? signal.red : fg3, fontSize: 11, cursor: "pointer" }}>{w}</button> })}</div>}
    </>)
  }

  const total = data?.rows.length ?? 0
  const ext = (data?.rows ?? []).filter((r) => r.lane === "EXT-search").length
  const int = total - ext

  return (
    <main style={{ minHeight: "100vh", background: surface.bg, color: fg1, fontFamily: sans, fontSize: 14, lineHeight: 1.5 }}>
      <style>{`@media (prefers-reduced-motion:reduce){*{animation:none!important}}`}</style>
      <div style={{ maxWidth: 1280, margin: "0 auto", padding: phone ? "16px 12px 40px" : "24px 16px 40px" }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", paddingBottom: 12 }}>
          <Wordmark section="Job search" />
          <AuthControl />
        </div>
        <Rule />
        <BoardTabs active="champions" />
        <header style={{ padding: "16px 0", display: "flex", flexWrap: "wrap", gap: "8px 16px", alignItems: "baseline" }}>
          <h1 style={{ fontSize: 20, fontWeight: 600, letterSpacing: "-0.015em", margin: 0, textWrap: "balance" }}>Champions</h1>
          <p style={{ margin: 0, flexBasis: "100%", maxWidth: MEASURE, fontSize: 13, color: fg2, textWrap: "pretty" }}>Hiring champions from your own network — recruiters and talent leads who could recognize the rare pair the way Amy did. Scored against the champion-fit rubric with <b style={{ color: fg1, fontFamily: mono }}>warm path</b> leading, stack-ranked, and swipeable. Reach out on a right swipe; nothing is sent until you do.</p>
          <p style={{ margin: 0, flexBasis: "100%", display: "flex", flexWrap: "wrap", gap: "4px 16px", fontSize: 13, color: fg2 }}>
            {[[String(total), "in the shortlist"], [String(ext), "external search"], [String(int), "internal basin"], [String(rights.length), "swiped right"]].map(([n, l]) => <span key={l} style={{ whiteSpace: "nowrap" }}><b style={{ color: fg1, fontFamily: mono, fontWeight: 600 }}>{n}</b> {l}</span>)}
          </p>
          <p style={{ margin: 0, flexBasis: "100%", fontSize: 12, color: fg4 }}>Private — real names and profiles from your connections. Served only behind your session; never public.</p>
        </header>
        {err && <div style={{ padding: 12, border: `1px solid ${signal.red}55`, borderRadius: 4, color: fg1, marginBottom: 12 }}>{err} {err.includes("Sign in") && <a href="/compass?next=/jobs/champions" style={{ color: signal.cyan }}>Sign in</a>}</div>}

        {/* toolbar */}
        <div style={{ display: "flex", flexWrap: "wrap", gap: 8, alignItems: "center", padding: "8px 0 12px" }}>
          {seg("tier", [["all", "All tiers"], ["1", "≥ 0.52"], ["2", "0.36–0.51"], ["3", "< 0.36"]])}
          {seg("swipe", [["all", "Any"], ["none", "Unswiped"], ["r", "Reach out"], ["l", "Passed"]])}
          {seg("lane", [["all", "Both lanes"], ["EXT-search", "External"], ["INT-basin", "Internal"]])}
          <select aria-label="Tag" value={f.tag} onChange={(e) => setF({ ...f, tag: e.target.value })} style={ctl}><option value="all">Any tag</option>{TAG_OPTIONS.map((t) => <option key={t} value={t}>{t}</option>)}</select>
          <select aria-label="Sort by" value={sort.key} onChange={(e) => { const k = e.target.value as "score" | "warm" | "name"; setSort({ key: k, dir: k === "name" ? "asc" : "desc" }) }} style={ctl}><option value="score">Sort: Fit score</option><option value="warm">Sort: Warm path</option><option value="name">Sort: Name</option></select>
          <input type="search" placeholder="Search name, firm, role" aria-label="Search" value={f.q} onChange={(e) => setF({ ...f, q: e.target.value })} style={{ ...ctl, flex: "1 1 160px", minWidth: 160 }} />
          <span style={{ flex: 1 }} />
          <span style={{ fontSize: 13, color: fg3, whiteSpace: "nowrap" }}>{visible.length} of {scored.length}</span>
          <button onClick={() => setF({ tier: "all", swipe: "all", lane: "all", tag: "all", q: "" })} style={{ background: "none", border: 0, color: signal.cyan, cursor: "pointer", fontSize: 13 }}>Reset</button>
          <Button variant="ghost" size="sm" onClick={() => { setLabOpen((o) => { const n = !o; if (n && !weights) setWeights(Object.fromEntries(DIMS.map((d) => [d.key, d.weight]))); return n }) }} aria-expanded={labOpen}>{labOpen ? "Close lab" : weights ? "Weight lab ●" : "Weight lab"}</Button>
        </div>

        {labOpen && spec && (() => {
          const defs = Object.fromEntries(DIMS.map((d) => [d.key, d.weight]))
          const w = weights ?? defs
          const dirty = DIMS.some((d) => (w[d.key] ?? d.weight) !== d.weight)
          const set = (k: string, v: number) => setWeights({ ...(weights ?? defs), [k]: v })
          const PRESETS: [string, string, Record<string, number>][] = [
            ["Warm first", "Weight the warm path hardest — work who you already know", { warm_path: 8, crossover_recognition: 4, domain_fit: 3, shape_over_title: 2, org_design_literacy: 1 }],
            ["Basin first", "Weight domain fit + crossover — chase the rarest-JTBD placements", { domain_fit: 6, crossover_recognition: 6, warm_path: 4, shape_over_title: 3, org_design_literacy: 1 }],
          ]
          return (
            <div style={{ padding: 16, marginBottom: 12, border: `1px solid #2c3a50`, borderRadius: 4, background: surface.panel }}>
              <b style={{ color: fg1, fontWeight: 600, fontSize: 14 }}>Weight Lab</b>
              <p style={{ margin: "4px 0 0", fontSize: 12, color: fg2, maxWidth: MEASURE, textWrap: "pretty" }}>Drag a weight and the whole lane re-ranks live, recomputed from each champion&apos;s stored 0–3 scores. Nothing is written and no model runs. Hand me a setting to make it permanent in the rubric.</p>
              <div style={{ display: "grid", gridTemplateColumns: phone ? "1fr" : "repeat(auto-fit, minmax(280px, 1fr))", gap: "6px 28px", margin: "12px 0" }}>
                {DIMS.map((d) => { const val = w[d.key] ?? d.weight; const chg = val !== d.weight; return (
                  <label key={d.key} title={`${d.anchor0} → ${d.anchor3}`} style={{ display: "grid", gridTemplateColumns: "168px 1fr 30px", gap: 10, alignItems: "center" }}>
                    <span style={{ fontSize: 12, color: fg2, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{d.label}</span>
                    <input type="range" min={0} max={8} step={1} value={val} onChange={(e) => set(d.key, Number(e.target.value))} style={{ width: "100%", accentColor: signal.cyan, cursor: "pointer" }} aria-label={`${d.label} weight`} />
                    <span style={{ fontFamily: mono, fontSize: 12, textAlign: "right", color: chg ? signal.cyan : fg2 }}>{val}<small style={{ color: fg4, display: "block", fontSize: 9 }}>{chg ? `was ${d.weight}` : "spec"}</small></span>
                  </label>) })}
              </div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 8, alignItems: "center" }}>
                {PRESETS.map(([label, tip, wts]) => <button key={label} title={tip} onClick={() => setWeights({ ...defs, ...wts })} style={{ minHeight: 30, padding: "0 12px", border: `1px solid ${signal.cyan}44`, borderRadius: 5, background: `${signal.cyan}12`, color: "#b9e8f4", cursor: "pointer", fontFamily: mono, fontSize: 11, fontWeight: 600 }}>{label}</button>)}
                <button onClick={() => setWeights(defs)} disabled={!dirty} style={{ minHeight: 30, padding: "0 12px", border: `1px solid ${border.subtle}`, borderRadius: 5, background: surface.elevated, color: dirty ? fg2 : fg4, cursor: dirty ? "pointer" : "default", fontSize: 12 }}>Reset to spec</button>
                <button onClick={() => { setWeights(null); setLabOpen(false) }} style={{ minHeight: 30, padding: "0 12px", border: 0, background: "none", color: signal.cyan, cursor: "pointer", fontSize: 12 }}>Turn off · use stored scores</button>
              </div>
            </div>
          )
        })()}

        {/* board */}
        <div style={{ border: `1px solid #243042`, borderRadius: 4, background: GLASS_CARD, boxShadow: GLASS_BEVEL, overflow: "clip" }}>
          {!data ? <div style={{ padding: 40, textAlign: "center", color: fg3 }}>{err ? "" : "Loading the lane…"}</div> : visible.length === 0 ? <div style={{ padding: 40, textAlign: "center", color: fg3 }}><b style={{ display: "block", color: fg1, fontWeight: 500 }}>Nothing matches.</b>Loosen a filter, or reset.</div> :
          phone ? (
            <div>{visible.map((r, i) => { const t = tierOf(r.composite, spec!)!; const prev = visible[i - 1]; const head = sort.key === "score" && (!prev || tierOf(prev.composite, spec!) !== t); return (
              <div key={r.id}>
                {head && <div style={{ ...labelStyle, padding: "4px 12px", background: surface.elevated, borderBottom: `1px solid ${border.subtle}` }}><b style={{ color: fg1, fontFamily: sans, letterSpacing: 0, textTransform: "none", fontSize: 13, marginRight: 8 }}>{TIER_LABEL[t][0]}</b>{TIER_LABEL[t][1]}</div>}
                <div style={{ display: "grid", gridTemplateColumns: "auto 1fr", columnGap: 12, rowGap: 8, padding: 12, borderBottom: `1px solid ${border.subtle}`, boxShadow: r.swipe ? `inset 2px 0 0 ${r.swipe.direction === "r" ? signal.green : signal.red}` : undefined, opacity: r.swipe?.direction === "l" ? 0.5 : t === 3 ? 0.85 : 1 }}>
                  <div style={{ fontFamily: mono, fontWeight: 600, fontSize: 16, color: r.swipe?.direction === "r" ? signal.green : fg1 }}>{r.composite.toFixed(3)}<small style={{ display: "block", fontWeight: 400, fontSize: 10, color: fg3 }}>T{t}</small></div>
                  <div>{nameCell(r)}</div>
                  <div style={{ gridColumn: "1 / -1", display: "flex", flexWrap: "wrap", gap: 8, alignItems: "center" }}><a href={r.url} target="_blank" rel="noopener" style={{ color: signal.cyan }}>LinkedIn</a></div>
                  <div style={{ gridColumn: "1 / -1" }}>{bundleCell(r)}</div>
                  <div style={{ gridColumn: "1 / -1" }}>{swipeButtons(r)}</div>
                  {open[r.id] && <div style={{ gridColumn: "1 / -1", background: surface.elevated, padding: "0 12px 16px", margin: "0 -12px", borderTop: `1px solid ${border.subtle}` }}>{anatomy(r)}</div>}
                </div>
              </div>) })}</div>
          ) : (
            <div style={{ overflowX: "auto" }}>
              <table style={{ borderCollapse: "collapse", width: "100%", tableLayout: "fixed" }}>
                <colgroup><col style={{ width: 72 }} /><col /><col style={{ width: 92 }} />{!tablet && <col style={{ width: 260 }} />}<col style={{ width: 172 }} /></colgroup>
                <thead><tr>{th("Fit", "score")}{th("Champion", "name")}{th("Profile")}{!tablet && th("Bundle on swipe")}{th("Swipe")}</tr></thead>
                <tbody>{visible.map((r, i) => { const t = tierOf(r.composite, spec!)!; const prev = visible[i - 1]; const head = sort.key === "score" && (!prev || tierOf(prev.composite, spec!) !== t); const left = r.swipe?.direction === "l"; return (
                  <React.Fragment key={r.id}>
                    {head && <tr><td colSpan={5} style={{ ...labelStyle, padding: "4px 12px", background: surface.elevated, borderBottom: `1px solid ${border.subtle}` }}><b style={{ color: fg1, fontFamily: sans, letterSpacing: 0, textTransform: "none", fontSize: 13, marginRight: 8 }}>{TIER_LABEL[t][0]}</b>{TIER_LABEL[t][1]}</td></tr>}
                    <tr style={{ borderBottom: `1px solid ${border.subtle}`, opacity: left ? 0.5 : t === 3 ? 0.85 : 1 }}>
                      <td style={{ ...rowCell, fontFamily: mono, fontWeight: 600, fontSize: 14, whiteSpace: "nowrap", color: r.swipe?.direction === "r" ? signal.green : fg1, boxShadow: r.swipe ? `inset 2px 0 0 ${r.swipe.direction === "r" ? signal.green : signal.red}` : undefined }}>{r.composite.toFixed(3)}<small style={{ display: "block", fontWeight: 400, fontSize: 10, color: fg3, letterSpacing: "0.06em" }}>T{t}</small></td>
                      <td style={rowCell}>{nameCell(r)}</td>
                      <td style={rowCell}><a href={r.url} target="_blank" rel="noopener" style={{ color: signal.cyan, display: "block" }}>LinkedIn</a></td>
                      {!tablet && <td style={rowCell}>{bundleCell(r)}</td>}
                      <td style={rowCell}>{swipeButtons(r)}</td>
                    </tr>
                    {open[r.id] && <tr><td colSpan={5} style={{ padding: "0 12px 16px", background: surface.elevated, borderBottom: `1px solid ${border.subtle}` }}>{anatomy(r)}</td></tr>}
                  </React.Fragment>) })}</tbody>
              </table>
            </div>
          )}
        </div>

        {/* below: what a right swipe stages + the log */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(340px, 1fr))", gap: 16, marginTop: 24 }}>
          <div style={{ border: `1px solid #243042`, borderRadius: 4, padding: "20px 24px", background: GLASS_CARD, boxShadow: GLASS_BEVEL }}>
            <SectionLabel>What a right swipe stages</SectionLabel>
            <ol style={{ margin: "8px 0 0", paddingLeft: 18, fontSize: 13, color: fg2 }}>
              <li style={{ margin: "4px 0" }}><b style={{ color: fg1, fontWeight: 500 }}>External search →</b> the two-tier recruiter enablement (open positioning + gated ammo), the <a href="https://recruithaus.arcs.care" target="_blank" rel="noopener" style={{ color: signal.cyan }}>recruithaus.arcs.care</a> pattern, tuned to their register. They re-sell you across roles.</li>
              <li style={{ margin: "4px 0" }}><b style={{ color: fg1, fontWeight: 500 }}>Internal basin →</b> a founder-aimed forge, the <a href="https://blacksmith.arcs.care" target="_blank" rel="noopener" style={{ color: signal.cyan }}>blacksmith.arcs.care</a> pattern, for their company. Converts one basin-central company fast.</li>
              <li style={{ margin: "4px 0" }}><b style={{ color: fg1, fontWeight: 500 }}>Acceptance test.</b> On first contact, did they name the crossover rarity back — unprompted, effortlessly? That confirms a champion, not just a fit.</li>
            </ol>
            <div style={{ marginTop: 12, padding: 12, background: surface.panel, border: `1px solid ${border.subtle}`, borderLeft: `2px solid ${signal.gold}`, borderRadius: 4, color: fg2, fontSize: 13 }}><b style={{ color: fg1, fontWeight: 500 }}>Gate.</b> A right swipe stages the bundle; it does not send. The enablement or forge is built and sent as a separate, human-approved step.</div>
          </div>
          <div style={{ border: `1px solid #243042`, borderRadius: 4, padding: "20px 24px", background: GLASS_CARD, boxShadow: GLASS_BEVEL }}>
            <SectionLabel>Reaching out</SectionLabel>
            <ul style={{ listStyle: "none", padding: 0, margin: "8px 0 0", fontFamily: mono, fontSize: 12 }}>{rights.length === 0 ? <li style={{ color: fg3 }}>none yet</li> : rights.map((r) => <li key={r.id} style={{ display: "flex", gap: 8, padding: "4px 0", borderBottom: `1px dashed ${border.subtle}` }}><span style={{ width: 74, flex: "none", color: signal.green, fontWeight: 600 }}>{LANE_LABEL[r.lane].split(" ")[0].toUpperCase()}</span><span style={{ color: fg1 }}>{r.name} · {r.company}</span></li>)}</ul>
            <details style={{ marginTop: 12 }}>
              <summary style={{ cursor: "pointer", fontSize: 13, color: fg2 }}>Every swipe, with undo <span style={{ color: fg3 }}>{swipesLog.length ? `(${swipesLog.length})` : ""}</span></summary>
              <ul style={{ listStyle: "none", padding: 0, margin: "8px 0 0", fontSize: 12 }}>{swipesLog.length === 0 ? <li style={{ color: fg3 }}>no swipes yet</li> : swipesLog.map((r) => <li key={r.id} style={{ display: "flex", gap: 8, alignItems: "center", padding: "4px 0", borderBottom: `1px dashed ${border.subtle}` }}><span style={{ fontFamily: mono, width: 56, flex: "none", color: r.swipe!.direction === "r" ? signal.green : signal.red }}>{r.swipe!.direction === "r" ? "REACH" : "PASS"}</span><span style={{ flex: 1, color: fg1 }}>{r.name} · {r.company}</span>{r.swipe!.why && <span style={{ color: fg3, whiteSpace: "nowrap" }}>{r.swipe!.why}</span>}<button onClick={() => unswipe(r)} aria-label={`Undo swipe on ${r.name}`} style={{ minHeight: 28, minWidth: 28, border: `1px solid ${border.subtle}`, borderRadius: 3, background: surface.panel, color: fg2, cursor: "pointer" }}>✕</button></li>)}</ul>
            </details>
            <p style={{ marginTop: 12, fontSize: 12, color: fg3 }}>Stored in the ARCS database, synced on every device. Private to your session.</p>
          </div>
        </div>
        <footer style={{ marginTop: 24, fontSize: 12, color: fg4, maxWidth: MEASURE }}>Rubric v{spec?.version ?? "?"} — champion-fit heuristic, warm path dominant · sourced from your LinkedIn connections export, filtered to the Amy-shape shortlist · click any champion for its score anatomy · the on-call dims are the acceptance test, captured after contact.</footer>
      </div>
    </main>
  )
}
