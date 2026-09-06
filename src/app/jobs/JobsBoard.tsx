"use client"

import React, { useCallback, useEffect, useMemo, useState } from "react"
import { surface, border, text, signal, font, radius } from "@/ui/tokens"
import { useVw } from "@/ui/useVw"
import { Wordmark } from "@/ui/Wordmark"
import { Rule } from "@/ui/Rule"
import { SectionLabel } from "@/ui/SectionLabel"
import { Button } from "@/ui/Button"
import { AuthControl } from "@/molecules/AuthControl"
import Link from "next/link"

// The Alert Swipe Board, product edition. Same loop as the artifact version
// (0.58 cutoff, three tiers, swipe right to forge, why-not tags on left,
// score anatomy from the rubric-as-data spec), backed by /api/jobs. Inline
// styles only; responsive branching through useVw (no media queries).

type Swipe = { direction: string; why: string | null; at: string }
type Forge = { status: string; url: string | null; resumeUrl: string | null; hmKind: string | null; hmText: string | null; contactType: string | null; contactDetail: string | null; contactUrl: string | null; notes: string | null; requestedAt: string }
type Row = {
  jobid: string; title: string; company: string; location: string | null; url: string; alertQuery: string | null; source: string
  firstSeen: string; seenCount: number; salary: string | null; composite: number | null; band: string
  dims: string | null; gates: string | null; assessment: string | null; atsClass: string | null; atsName: string | null
  companyType: string | null; compBand: string | null; hmKind: string | null; hmText: string | null
  contactType: string | null; contactDetail: string | null; contactUrl: string | null; nextStep: string | null; unscoredWhy: string | null
  swipe: Swipe | null; forge: Forge | null
}
type Spec = {
  version: string
  quads: { id: string; label: string; headline: string; dims: string[] }[]
  rubric: { dims: { key: string; label: string; weight: number; anchor0: string; anchor3: string }[]; max: number; board_cutoff: number; tiers: { t1: number; t2: number; t3: number } }
}
type Payload = { rows: Row[]; settings: Record<string, string>; spec: Spec | null }

const WHY = ["comp", "location", "role shape", "seniority", "culture", "company", "timing", "other"]
const ARCH: Record<string, string> = { "forward deployed engineer": "forward deployed", "applied ai engineer": "applied AI", "ai solutions engineer": "AI solutions", "product lead": "product lead", manual: "by hand" }
const COTYPE: Record<string, string> = { startup: "startup", scaleup: "scale-up", enterprise: "enterprise" }
const STAGES: Record<string, [string, number]> = { queued: ["generating", 0], gathering: ["gathering", 25], grading: ["grading", 50], rendering: ["rendering", 75], built: ["built, awaiting deploy", 90], live: ["live", 100] }
const TIER_LABEL: Record<number, [string, string]> = { 1: ["Tier 1", "0.80 and up · generate on swipe"], 2: ["Tier 2", "0.70 to 0.79 · manual trigger"], 3: ["Tier 3", "0.58 to 0.69 · watch"] }

const mono = font.mono
const sans = font.sans
const fg1 = text.primary, fg2 = text.secondary, fg3 = text.dimmed, fg4 = text.muted
const GLASS_CARD = "linear-gradient(160deg, rgba(255,255,255,.05), rgba(255,255,255,.01) 38%, rgba(0,0,0,.18)), linear-gradient(165deg, #11181f, #0a1016)"
const GLASS_BEVEL = "inset 0 1px 0 rgba(255,255,255,.10), inset 0 -2px 8px rgba(0,0,0,.5), 0 5px 16px rgba(0,0,0,.45)"
const SCREEN = "linear-gradient(180deg, #090d12, #0c1219)"
const SCREEN_INSET = "inset 0 2px 5px rgba(0,0,0,.55), inset 0 -1px 0 rgba(255,255,255,.04)"

const labelStyle: React.CSSProperties = { fontFamily: mono, fontSize: 10, fontWeight: 700, letterSpacing: "0.14em", textTransform: "uppercase", color: fg4 }
const smallLabel: React.CSSProperties = { fontFamily: mono, fontSize: 10, fontWeight: 700, letterSpacing: "0.12em", textTransform: "uppercase", color: fg4 }
const ctl: React.CSSProperties = { minHeight: 36, padding: "0 12px", background: SCREEN, border: `1px solid #1c2736`, borderRadius: 5, color: fg1, fontFamily: sans, fontSize: 13, boxShadow: SCREEN_INSET }

function tierOf(c: number | null, spec: Spec | null): 1 | 2 | 3 | null {
  if (c == null) return null
  const t = spec?.rubric.tiers ?? { t1: 0.8, t2: 0.7, t3: 0.58 }
  return c >= t.t1 ? 1 : c >= t.t2 ? 2 : c >= t.t3 ? 3 : null
}
function parse<T>(s: string | null, fb: T): T { try { return s ? (JSON.parse(s) as T) : fb } catch { return fb } }
function salNum(s: string | null): number { const m = (s ?? "").match(/\$(\d+)K?/g); return m ? Math.max(...m.map((x) => parseInt(x.replace(/\D/g, ""), 10))) : 0 }

function Pill({ children, tone }: { children: React.ReactNode; tone?: "old" | "new" | "unk" }) {
  const c = tone === "old" ? signal.gold : tone === "new" ? signal.green : fg3
  return <span style={{ display: "inline-block", padding: "2px 9px", border: `1px solid ${c}40`, borderStyle: tone === "unk" ? "dashed" : "solid", borderRadius: 6, fontFamily: mono, fontSize: 10, fontWeight: 500, letterSpacing: "0.06em", textTransform: "uppercase", color: tone ? c : fg2, opacity: 0.92, lineHeight: 1.4, overflowWrap: "anywhere" }}>{children}</span>
}
function Tag({ children }: { children: React.ReactNode }) {
  return <span style={{ display: "inline-block", padding: "0 5px", border: `1px solid ${border.subtle}`, borderRadius: radius.xs, fontSize: 10, color: fg3, whiteSpace: "nowrap" }}>{children}</span>
}
function Progress({ pct, indeterminate, done }: { pct: number; indeterminate?: boolean; done?: boolean }) {
  const c = done ? signal.green : signal.cyan
  return (
    <span style={{ display: "block", marginTop: 5, height: 6, width: "100%", maxWidth: 120, background: SCREEN, borderRadius: 999, overflow: "hidden", position: "relative", boxShadow: "inset 0 2px 4px rgba(0,0,0,.65), inset 0 -1px 0 rgba(255,255,255,.04)" }} role="progressbar" aria-valuenow={pct} aria-valuemin={0} aria-valuemax={100}>
      <span style={{ position: "absolute", top: 0, bottom: 0, left: 0, width: indeterminate ? "34%" : `${pct}%`, borderRadius: 999, background: indeterminate ? `linear-gradient(90deg, transparent, ${c}, transparent)` : `linear-gradient(90deg, #1ec3d4, ${c})`, boxShadow: `0 0 8px -1px ${c}`, animation: indeterminate ? "arcs-indet 1.35s cubic-bezier(.4,0,.2,1) infinite" : undefined }} />
    </span>
  )
}

export function JobsBoard() {
  const vw = useVw()
  const phone = vw < 640
  const tablet = vw < 1100
  const [data, setData] = useState<Payload | null>(null)
  const [err, setErr] = useState<string | null>(null)
  const [f, setF] = useState({ tier: "all", swipe: "all", ats: "all", arch: "all", co: "all", q: "", from: "", to: "" })
  const [sort, setSort] = useState<{ key: "score" | "company"; dir: "asc" | "desc" }>({ key: "score", dir: "desc" })
  const [open, setOpen] = useState<Record<string, boolean>>({})
  const [adding, setAdding] = useState(false)
  const [unsOpen, setUnsOpen] = useState(false)
  const [usort, setUsort] = useState<"sal" | "why" | "seen">("sal")
  const [busy, setBusy] = useState<string | null>(null)

  const load = useCallback(async () => {
    try {
      const r = await fetch("/api/jobs", { cache: "no-store" })
      if (r.status === 401) { setErr("Sign in with your admin email to use the board."); return }
      if (!r.ok) throw new Error(`HTTP ${r.status}`)
      setData(await r.json())
    } catch (e) { setErr(e instanceof Error ? e.message : "Failed to load") }
  }, [])
  useEffect(() => { load() }, [load])

  const spec = data?.spec ?? null
  const cap = Number(data?.settings?.cap ?? 5)
  const DIMS = spec?.rubric.dims ?? []
  const MAX = spec?.rubric.max ?? 72

  const scored = useMemo(() => (data?.rows ?? []).filter((r) => tierOf(r.composite, spec) !== null), [data, spec])
  const unscored = useMemo(() => (data?.rows ?? []).filter((r) => r.band === "UNSCORED"), [data])

  const visible = useMemo(() => {
    const q = f.q.trim().toLowerCase()
    return scored.filter((r) => {
      const t = tierOf(r.composite, spec)
      const sw = r.swipe?.direction ?? "none"
      if (f.tier !== "all" && t !== Number(f.tier)) return false
      if (f.swipe !== "all" && sw !== f.swipe) return false
      if (f.ats !== "all" && (r.atsClass ?? "unk") !== f.ats) return false
      if (f.arch !== "all" && (r.alertQuery ?? "manual") !== f.arch) return false
      if (f.co !== "all" && r.companyType !== f.co) return false
      if (q && !(r.title + " " + r.company).toLowerCase().includes(q)) return false
      const seen = r.firstSeen.slice(0, 10)
      if (f.from && seen < f.from) return false
      if (f.to && seen > f.to) return false
      return true
    }).sort((a, b) => {
      const d = sort.dir === "asc" ? 1 : -1
      if (sort.key === "company") return d * a.company.localeCompare(b.company) || (b.composite ?? 0) - (a.composite ?? 0)
      return d * ((a.composite ?? 0) - (b.composite ?? 0)) || a.company.localeCompare(b.company)
    })
  }, [scored, f, sort, spec])

  const rights = useMemo(() => scored.filter((r) => r.swipe?.direction === "r").sort((a, b) => (a.swipe!.at < b.swipe!.at ? -1 : 1)), [scored])
  const swipes = useMemo(() => scored.filter((r) => r.swipe).sort((a, b) => (a.swipe!.at > b.swipe!.at ? -1 : 1)), [scored])

  async function post(path: string, method: string, body: unknown, key?: string) {
    setBusy(key ?? path)
    try {
      const r = await fetch(path, { method, headers: { "content-type": "application/json" }, body: JSON.stringify(body) })
      if (!r.ok) { const j = await r.json().catch(() => ({})); setErr(j.error ?? `HTTP ${r.status}`); return null }
      await load()
      return await r.json().catch(() => null)
    } finally { setBusy(null) }
  }
  const swipe = (row: Row, dir: "r" | "l") => post("/api/jobs/swipe", "POST", { jobid: row.jobid, direction: row.swipe?.direction === dir ? null : dir, why: dir === "l" ? row.swipe?.why ?? null : null }, row.jobid)
  const why = (row: Row, w: string) => post("/api/jobs/swipe", "POST", { jobid: row.jobid, direction: "l", why: row.swipe?.why === w ? null : w }, row.jobid)
  const unswipe = (row: Row) => post("/api/jobs/swipe", "POST", { jobid: row.jobid, direction: null }, row.jobid)

  function pts(r: Row) { const d = parse<Record<string, number>>(r.dims, {}); return DIMS.reduce((t, x) => t + (d[x.key] ?? 0) * x.weight, 0) }

  function anatomy(r: Row, nxt: Row | undefined) {
    const d = parse<Record<string, number>>(r.dims, {}); const total = pts(r); const gates = parse<string[]>(r.gates, [])
    return (
      <div style={{ display: "grid", gridTemplateColumns: phone ? "1fr" : "minmax(280px,1.2fr) minmax(220px,.8fr)", gap: "16px 40px", paddingTop: 12 }}>
        <div>
          <div style={{ ...smallLabel, marginBottom: 8 }}>How the score is built</div>
          <div style={{ fontFamily: mono, fontSize: 12, color: fg2, marginBottom: 8 }}><b style={{ color: fg1 }}>{total}</b> of {MAX} points = <b style={{ color: fg1 }}>{(total / MAX).toFixed(3)}</b> · each dimension is scored 0 to 3, then multiplied by its weight</div>
          {DIMS.map((x) => { const sc = d[x.key] ?? 0; const max = x.weight * 3; return (
            <div key={x.key} title={`${x.anchor0} to ${x.anchor3}`} style={{ display: "grid", gridTemplateColumns: phone ? "118px 1fr 44px" : "150px 1fr 44px", gap: 8, alignItems: "center", padding: "3px 0" }}>
              <span style={{ fontSize: 12, color: fg2, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{x.label}<small style={{ color: fg4, fontFamily: mono, fontSize: 10, marginLeft: 4 }}>×{x.weight}</small></span>
              <span style={{ position: "relative", height: 8, background: SCREEN, borderRadius: 999, overflow: "hidden", boxShadow: "inset 0 2px 4px rgba(0,0,0,.65), inset 0 -1px 0 rgba(255,255,255,.04)" }}>
                <i style={{ position: "absolute", left: 0, top: 0, bottom: 0, width: sc === 0 ? 3 : `${(sc / 3) * 100}%`, background: sc === 0 ? signal.red : `linear-gradient(90deg, #1ec3d4, ${signal.cyan})`, borderRadius: 999, boxShadow: sc === 0 ? undefined : `0 0 8px -1px ${signal.cyan}, inset 0 1px 0 rgba(255,255,255,.35)` }} />
              </span>
              <span style={{ fontFamily: mono, fontSize: 12, color: fg1, textAlign: "right", fontVariantNumeric: "tabular-nums" }}>{sc * x.weight}<small style={{ color: fg4 }}>/{max}</small></span>
            </div>) })}
          {spec && <div style={{ fontSize: 12, color: fg2, marginTop: 8 }}><b style={{ color: fg1, fontWeight: 500 }}>Differentiators it loads on:</b> {spec.quads.map((q) => { let p = 0, m = 0; q.dims.forEach((dk) => { const dd = DIMS.find((x) => x.key === dk); if (dd) { p += (d[dk] ?? 0) * dd.weight; m += 3 * dd.weight } }); return <span key={q.id} style={{ display: "inline-block", margin: "2px 10px 0 0", whiteSpace: "nowrap" }}><b style={{ color: signal.cyan }}>{q.id}</b> {q.label} <span style={{ fontFamily: mono, color: fg3, fontSize: 10 }}>{p}/{m}</span></span> })}</div>}
          <div style={{ fontSize: 12, color: fg2, marginTop: 8 }}><b style={{ color: fg1, fontWeight: 500 }}>Hard gates:</b> {gates.length ? gates.join(", ") : "none fired"}</div>
        </div>
        <div>
          {nxt ? (() => { const nd = parse<Record<string, number>>(nxt.dims, {}); const nt = pts(nxt); const diffs = DIMS.map((x) => [x.label, (d[x.key] ?? 0) * x.weight - (nd[x.key] ?? 0) * x.weight, d[x.key] ?? 0, nd[x.key] ?? 0] as const).filter((x) => x[1] !== 0); return (<>
            <div style={{ ...smallLabel, marginBottom: 8 }}>Versus the next row · {nxt.company}</div>
            <div style={{ fontFamily: mono, fontSize: 12, color: fg2, marginBottom: 8 }}><b style={{ color: fg1 }}>{total}</b> vs <b style={{ color: fg1 }}>{nt}</b> points</div>
            {diffs.length === 0 ? <p style={{ margin: 0, fontSize: 12, color: fg2 }}>Identical on every dimension. The tie is a judgment call, not arithmetic; the read below is the tie-break.</p>
              : <ul style={{ listStyle: "none", margin: 0, padding: 0, fontSize: 12, color: fg2 }}>{diffs.map((x) => <li key={x[0]} style={{ display: "flex", justifyContent: "space-between", gap: 8, padding: "3px 0", borderBottom: `1px dashed ${border.subtle}` }}><span>{x[0]} · {x[2]} vs {x[3]}</span><span style={{ fontFamily: mono, color: x[1] > 0 ? signal.green : signal.red, whiteSpace: "nowrap" }}>{x[1] > 0 ? "+" : ""}{x[1]}</span></li>)}</ul>}
          </>) })() : <div style={{ ...smallLabel, marginBottom: 8 }}>Last row in this view</div>}
          <p style={{ margin: "8px 0 0", fontSize: 12, color: fg2, textWrap: "pretty" }}><b style={{ color: fg1, fontWeight: 500 }}>Read:</b> {r.assessment ?? "no assessment recorded"}</p>
        </div>
      </div>
    )
  }

  function forgeCell(r: Row) {
    const fz = r.forge; const sw = r.swipe?.direction
    if (fz) { const st = STAGES[fz.status] ?? [fz.status, 50]; return (<>
      {fz.url && fz.status === "live" ? <a href={fz.url} target="_blank" rel="noopener" style={{ color: signal.cyan }}>{fz.url.replace(/^https?:\/\//, "")}</a>
        : fz.url && fz.status === "built" ? <a href={fz.url} target="_blank" rel="noopener" style={{ color: signal.cyan }}>open bundle</a>
        : <><span style={{ ...smallLabel, color: fg3 }}>{st[0]}</span><Progress pct={st[1]} indeterminate={fz.status === "queued"} done={fz.status === "live"} /></>}
      {fz.resumeUrl && <><br /><a href={fz.resumeUrl} target="_blank" rel="noopener" style={{ color: signal.cyan }}>tailored resume</a></>}
    </>) }
    if (sw === "r") return <><span style={{ ...smallLabel, color: fg3 }}>generating</span><Progress pct={0} indeterminate /></>
    return <span style={{ color: fg3 }}>Generate on swipe →</span>
  }

  function hmCell(r: Row) {
    const kind = r.forge?.hmKind ?? r.hmKind ?? "unknown"; const txt = r.forge?.hmText ?? r.hmText
    const kc = kind === "explicit" ? signal.green : kind === "implicit" ? signal.cyan : fg4
    const ct = r.forge?.contactType ?? r.contactType; const cd = r.forge?.contactDetail ?? r.contactDetail; const cu = r.forge?.contactUrl ?? r.contactUrl
    const lab: Record<string, string> = { portal: "ATS portal", form: "Form on site", email: "Email a human", referral: "Referral path", unverified: "Apply path" }
    return (<>
      <span style={{ ...smallLabel, color: kc, display: "block", marginBottom: 2 }}>{r.swipe?.direction === "r" && kind === "unknown" && !txt ? "generating" : kind}</span>
      <span style={{ fontSize: 13, color: fg1 }}>{txt ?? (kind === "unknown" ? "Generate on swipe →" : "")}</span>
      {ct && <span style={{ display: "block", marginTop: 4, fontSize: 12, color: fg3 }}><b style={{ color: fg2, fontWeight: 500 }}>{lab[ct] ?? ct}</b>{cd ? <> · {cu ? <a href={cu} target="_blank" rel="noopener" style={{ color: signal.cyan, overflowWrap: "anywhere" }}>{cd}</a> : cd}</> : null}</span>}
    </>)
  }

  const th = (label: string, key?: "score" | "company") => (
    <th style={{ ...smallLabel, textAlign: "left", padding: "8px 12px", background: surface.elevated, borderBottom: `1px solid ${border.subtle}`, whiteSpace: "nowrap", position: "sticky", top: 0 }}>
      {key ? <button onClick={() => setSort((s) => s.key === key ? { key, dir: s.dir === "asc" ? "desc" : "asc" } : { key, dir: key === "score" ? "desc" : "asc" })} style={{ background: "none", border: 0, padding: 0, color: sort.key === key ? fg1 : "inherit", cursor: "pointer", font: "inherit", letterSpacing: "inherit", textTransform: "inherit" }}>{label}{sort.key === key ? (sort.dir === "desc" ? " ▾" : " ▴") : ""}</button> : label}
    </th>
  )
  const seg = (name: keyof typeof f, opts: [string, string][]) => (
    <div role="group" style={{ display: "inline-flex", gap: 4, padding: 4, borderRadius: 6, background: SCREEN, boxShadow: "inset 0 2px 6px rgba(0,0,0,.7), inset 0 -1px 0 rgba(255,255,255,.04)" }}>
      {opts.map(([v, l]) => { const on = f[name] === v; return <button key={v} aria-pressed={on} onClick={() => setF({ ...f, [name]: v })} style={{ minHeight: phone ? 36 : 28, padding: "0 12px", border: `1px solid ${on ? "#00F0FF55" : "transparent"}`, borderRadius: 5, background: on ? "linear-gradient(180deg, #0d141c, #0f1822)" : "transparent", color: on ? "#b9e8f4" : fg3, cursor: "pointer", fontFamily: mono, fontWeight: 600, fontSize: 11, letterSpacing: "0.05em", whiteSpace: "nowrap", boxShadow: on ? "inset 0 2px 4px rgba(0,0,0,.5), inset 0 -7px 11px -7px #00F0FF40" : undefined }}>{l}</button> })}
    </div>
  )

  const rowCell: React.CSSProperties = { padding: 12, verticalAlign: "top", fontSize: 13, overflowWrap: "anywhere" }

  return (
    <main style={{ minHeight: "100vh", background: surface.bg, color: fg1, fontFamily: sans, fontSize: 14, lineHeight: 1.5 }}>
      <style>{`@keyframes arcs-indet{0%{left:-34%}100%{left:100%}} @media (prefers-reduced-motion:reduce){*{animation:none!important}}`}</style>
      <div style={{ maxWidth: 1280, margin: "0 auto", padding: phone ? "16px 12px 40px" : "24px 16px 40px" }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", paddingBottom: 12 }}>
          <Wordmark section="Job search" />
          <AuthControl />
        </div>
        <Rule />
        <header style={{ padding: "16px 0", display: "flex", flexWrap: "wrap", gap: "8px 16px", alignItems: "baseline" }}>
          <h1 style={{ fontSize: 20, fontWeight: 600, letterSpacing: "-0.015em", margin: 0, textWrap: "balance" }}>Alert Swipe Board</h1>
          <p style={{ margin: 0, flexBasis: "100%", maxWidth: "64ch", fontSize: 13, color: fg2, textWrap: "pretty" }}>Every LinkedIn alert, scored once against the target-role rubric and stack-ranked above a <b style={{ color: fg1, fontFamily: mono }}>{spec?.rubric.board_cutoff ?? 0.58}</b> cutoff. You decide. Nothing runs until you swipe right.</p>
          <p style={{ margin: 0, flexBasis: "100%", display: "flex", flexWrap: "wrap", gap: "4px 16px", fontSize: 13, color: fg2 }}>
            {[[String((data?.rows ?? []).length), "rows in"], [String(scored.length + (data?.rows ?? []).filter((r) => r.band !== "UNSCORED" && tierOf(r.composite, spec) === null).length), "scored"], [String(scored.length), "on the board"], [String(unscored.length), "waiting on a JD read"], [String(rights.length), "swiped right"]].map(([n, l]) => <span key={l} style={{ whiteSpace: "nowrap" }}><b style={{ color: fg1, fontFamily: mono, fontWeight: 600 }}>{n}</b> {l}</span>)}
          </p>
        </header>
        {err && <div style={{ padding: 12, border: `1px solid ${signal.red}55`, borderRadius: 4, color: fg1, marginBottom: 12 }}>{err} {err.includes("Sign in") && <a href="/compass?next=/jobs" style={{ color: signal.cyan }}>Sign in</a>}</div>}

        {/* toolbar */}
        <div style={{ display: "flex", flexWrap: "wrap", gap: 8, alignItems: "center", padding: "8px 0 12px" }}>
          {seg("tier", [["all", "All tiers"], ["1", "≥ 0.80"], ["2", "0.70–0.79"], ["3", "0.58–0.69"]])}
          {seg("swipe", [["all", "Any"], ["none", "Unswiped"], ["r", "Right"], ["l", "Left"]])}
          <select aria-label="ATS" value={f.ats} onChange={(e) => setF({ ...f, ats: e.target.value })} style={ctl}><option value="all">Any ATS</option><option value="old">Old school (Workday)</option><option value="new">New school (Ashby, Greenhouse)</option><option value="unk">Unverified</option></select>
          <select aria-label="Saved search" value={f.arch} onChange={(e) => setF({ ...f, arch: e.target.value })} style={ctl}><option value="all">Any search</option>{Object.entries(ARCH).map(([k, v]) => <option key={k} value={k}>{v}</option>)}</select>
          <select aria-label="Company type" value={f.co} onChange={(e) => setF({ ...f, co: e.target.value })} style={ctl}><option value="all">Any company</option>{Object.entries(COTYPE).map(([k, v]) => <option key={k} value={k}>{v}</option>)}</select>
          <input type="search" placeholder="Search role or company" aria-label="Search" value={f.q} onChange={(e) => setF({ ...f, q: e.target.value })} style={{ ...ctl, flex: "1 1 160px", minWidth: 160 }} />
          <label style={{ display: "inline-flex", alignItems: "center", gap: 4, fontSize: 12, color: fg3, flexBasis: phone ? "100%" : undefined }}>Seen <input type="date" aria-label="Seen from" value={f.from} onChange={(e) => setF({ ...f, from: e.target.value })} style={{ ...ctl, padding: "0 8px", colorScheme: "dark" }} /> to <input type="date" aria-label="Seen to" value={f.to} onChange={(e) => setF({ ...f, to: e.target.value })} style={{ ...ctl, padding: "0 8px", colorScheme: "dark" }} /></label>
          <span style={{ flex: 1 }} />
          <span style={{ fontSize: 13, color: fg3, whiteSpace: "nowrap" }}>{visible.length} of {scored.length}</span>
          <button onClick={() => setF({ tier: "all", swipe: "all", ats: "all", arch: "all", co: "all", q: "", from: "", to: "" })} style={{ background: "none", border: 0, color: signal.cyan, cursor: "pointer", fontSize: 13 }}>Reset</button>
          <Button variant="ghost" size="sm" onClick={() => setAdding((a) => !a)} aria-expanded={adding}>{adding ? "Close" : "+ Add a row"}</Button>
        </div>
        {adding && <form onSubmit={async (e) => { e.preventDefault(); const fd = new FormData(e.currentTarget); const c = fd.get("composite"); await post("/api/jobs", "POST", { url: fd.get("url"), title: fd.get("title"), company: fd.get("company"), composite: c ? Number(c) : null }); setAdding(false) }}
          onKeyDown={(e) => { if (e.key === "Escape") setAdding(false) }}
          style={{ display: "flex", flexWrap: "wrap", gap: 8, alignItems: "center", padding: 12, marginBottom: 12, border: `1px dashed #2c3a50`, borderRadius: 4, background: surface.panel }}>
          <input name="url" type="url" required placeholder="Posting URL" style={{ ...ctl, flex: "1 1 150px" }} /><input name="title" required placeholder="Role" style={{ ...ctl, flex: "1 1 150px" }} /><input name="company" required placeholder="Company" style={{ ...ctl, flex: "1 1 150px" }} /><input name="composite" type="number" step="0.001" min={0} max={1} placeholder="Score, if graded" style={{ ...ctl, flex: "0 1 150px" }} />
          <Button size="sm" type="submit">Add</Button><button type="button" onClick={() => setAdding(false)} style={{ background: "none", border: 0, color: signal.cyan, cursor: "pointer" }}>Cancel</button>
          <span style={{ fontSize: 12, color: fg3 }}>Without a score it waits in the unscored list until the scorer runs. Esc closes.</span>
        </form>}

        {/* board */}
        <div style={{ border: `1px solid #243042`, borderRadius: 4, background: GLASS_CARD, boxShadow: GLASS_BEVEL, overflow: "clip" }}>
          {!data ? <div style={{ padding: 40, textAlign: "center", color: fg3 }}>{err ? "" : "Loading the board…"}</div> : visible.length === 0 ? <div style={{ padding: 40, textAlign: "center", color: fg3 }}><b style={{ display: "block", color: fg1, fontWeight: 500 }}>Nothing matches.</b>Loosen a filter, or reset.</div> :
          phone ? (
            <div>{visible.map((r, i) => { const t = tierOf(r.composite, spec)!; const prev = visible[i - 1]; const head = sort.key === "score" && (!prev || tierOf(prev.composite, spec) !== t); return (
              <div key={r.jobid}>
                {head && <div style={{ ...labelStyle, padding: "4px 12px", background: surface.elevated, borderBottom: `1px solid ${border.subtle}` }}><b style={{ color: fg1, fontFamily: sans, letterSpacing: 0, textTransform: "none", fontSize: 13, marginRight: 8 }}>{TIER_LABEL[t][0]}</b>{TIER_LABEL[t][1]}</div>}
                <div style={{ display: "grid", gridTemplateColumns: "auto 1fr", columnGap: 12, rowGap: 8, padding: 12, borderBottom: `1px solid ${border.subtle}`, boxShadow: r.swipe ? `inset 2px 0 0 ${r.swipe.direction === "r" ? signal.green : signal.red}` : undefined, opacity: r.swipe?.direction === "l" ? 0.5 : t === 3 ? 0.85 : 1 }}>
                  <div style={{ fontFamily: mono, fontWeight: 600, fontSize: 16, color: r.swipe?.direction === "r" ? signal.green : fg1 }}>{r.composite!.toFixed(3)}<small style={{ display: "block", fontWeight: 400, fontSize: 10, color: fg3 }}>T{t}</small></div>
                  <div><b style={{ display: "block", fontWeight: 500, color: fg1 }}><Link href={`/jobs/${r.jobid}`} style={{ color: fg1, textDecoration: "none" }} title="Open the Role Scan">{r.title}</Link></b><span style={{ color: fg2, fontSize: 12 }}>{r.company} · {r.location ?? ""}{r.compBand ? ` · ${r.compBand}` : ""}</span><div style={{ display: "flex", flexWrap: "wrap", gap: 4, marginTop: 4 }}>{r.companyType && <Tag>{COTYPE[r.companyType] ?? r.companyType}</Tag>}<Tag>{ARCH[r.alertQuery ?? "manual"] ?? r.alertQuery}</Tag></div>{r.dims && <button onClick={() => setOpen({ ...open, [r.jobid]: !open[r.jobid] })} style={{ marginTop: 4, background: "none", border: 0, padding: 0, color: signal.cyan, fontSize: 12, cursor: "pointer" }}>{open[r.jobid] ? "Hide the score" : "Why this score"}</button>}</div>
                  <div style={{ gridColumn: "1 / -1", display: "flex", flexWrap: "wrap", gap: 8, alignItems: "center" }}><Pill tone={(r.atsClass as "old" | "new" | "unk") ?? "unk"}>{r.atsName ?? "unverified"}</Pill><a href={r.url} target="_blank" rel="noopener" style={{ color: signal.cyan }}>Posting</a></div>
                  <div style={{ gridColumn: "1 / -1", fontSize: 12, color: fg2 }}>{forgeCell(r)}</div>
                  <div style={{ gridColumn: "1 / -1" }}>{hmCell(r)}</div>
                  {r.nextStep && <div style={{ gridColumn: "1 / -1", fontSize: 12, color: fg2, textWrap: "pretty" }}>{r.nextStep}</div>}
                  <div style={{ gridColumn: "1 / -1" }}>{swipeButtons(r)}</div>
                  {open[r.jobid] && <div style={{ gridColumn: "1 / -1", background: surface.elevated, padding: "0 12px 16px", margin: "0 -12px", borderTop: `1px solid ${border.subtle}` }}>{anatomy(r, visible[i + 1])}</div>}
                </div>
              </div>) })}</div>
          ) : (
            <div style={{ overflowX: "auto" }}>
              <table style={{ borderCollapse: "collapse", width: "100%", tableLayout: "fixed" }}>
                <colgroup><col style={{ width: 72 }} /><col /><col style={{ width: 132 }} /><col style={{ width: 92 }} />{!tablet && <col style={{ width: 150 }} />}<col style={{ width: 200 }} />{!tablet && <col style={{ width: 230 }} />}<col style={{ width: 158 }} /></colgroup>
                <thead><tr>{th("Score", "score")}{th("Role", "company")}{th("ATS")}{th("Apply")}{!tablet && th("Forge")}{th("Hiring manager")}{!tablet && th("Next step")}{th("Swipe")}</tr></thead>
                <tbody>{visible.map((r, i) => { const t = tierOf(r.composite, spec)!; const prev = visible[i - 1]; const head = sort.key === "score" && (!prev || tierOf(prev.composite, spec) !== t); const left = r.swipe?.direction === "l"; return (
                  <React.Fragment key={r.jobid}>
                    {head && <tr><td colSpan={8} style={{ ...labelStyle, padding: "4px 12px", background: surface.elevated, borderBottom: `1px solid ${border.subtle}` }}><b style={{ color: fg1, fontFamily: sans, letterSpacing: 0, textTransform: "none", fontSize: 13, marginRight: 8 }}>{TIER_LABEL[t][0]}</b>{TIER_LABEL[t][1]}</td></tr>}
                    <tr style={{ borderBottom: `1px solid ${border.subtle}`, opacity: left ? 0.5 : t === 3 ? 0.85 : 1 }}>
                      <td style={{ ...rowCell, fontFamily: mono, fontWeight: 600, fontSize: 14, whiteSpace: "nowrap", color: r.swipe?.direction === "r" ? signal.green : fg1, boxShadow: r.swipe ? `inset 2px 0 0 ${r.swipe.direction === "r" ? signal.green : signal.red}` : undefined }}>{r.composite!.toFixed(3)}<small style={{ display: "block", fontWeight: 400, fontSize: 10, color: fg3, letterSpacing: "0.06em" }}>T{t}</small></td>
                      <td style={rowCell}><b style={{ display: "block", fontWeight: t === 1 ? 500 : 400, color: fg1, textWrap: "pretty" }}><Link href={`/jobs/${r.jobid}`} style={{ color: fg1, textDecoration: "none" }} title="Open the Role Scan">{r.title}</Link></b><span style={{ color: fg2, fontSize: 12 }}>{r.company} · {r.location ?? ""}{r.compBand ? ` · ${r.compBand}` : ""}</span><div style={{ display: "flex", flexWrap: "wrap", gap: 4, marginTop: 4 }}>{r.companyType && <Tag>{COTYPE[r.companyType] ?? r.companyType}</Tag>}<Tag>{ARCH[r.alertQuery ?? "manual"] ?? r.alertQuery}</Tag></div>{r.dims && <button onClick={() => setOpen({ ...open, [r.jobid]: !open[r.jobid] })} aria-expanded={!!open[r.jobid]} style={{ marginTop: 4, background: "none", border: 0, padding: 0, color: signal.cyan, fontSize: 12, cursor: "pointer" }}>{open[r.jobid] ? "Hide the score" : "Why this score"}</button>}</td>
                      <td style={rowCell}><Pill tone={(r.atsClass as "old" | "new" | "unk") ?? "unk"}>{r.atsName ?? "unverified"}</Pill></td>
                      <td style={rowCell}><a href={r.url} target="_blank" rel="noopener" style={{ color: signal.cyan, display: "block" }}>{r.url.includes("linkedin") ? "LinkedIn" : "Posting"}</a></td>
                      {!tablet && <td style={{ ...rowCell, fontSize: 12, color: fg2 }}>{forgeCell(r)}</td>}
                      <td style={rowCell}>{hmCell(r)}</td>
                      {!tablet && <td style={{ ...rowCell, fontSize: 12, color: fg2, textWrap: "pretty" }}>{r.nextStep}</td>}
                      <td style={rowCell}>{swipeButtons(r)}</td>
                    </tr>
                    {open[r.jobid] && <tr><td colSpan={8} style={{ padding: "0 12px 16px", background: surface.elevated, borderBottom: `1px solid ${border.subtle}` }}>{anatomy(r, visible[i + 1])}</td></tr>}
                  </React.Fragment>) })}</tbody>
              </table>
            </div>
          )}
        </div>

        {/* unscored */}
        <section style={{ marginTop: 16 }}>
          <button onClick={() => setUnsOpen((o) => !o)} aria-expanded={unsOpen} style={{ background: "none", border: 0, padding: "8px 0", color: fg1, fontWeight: 500, cursor: "pointer", fontSize: 14, display: "flex", gap: 8, alignItems: "center" }}><span style={{ display: "inline-block", transform: unsOpen ? "rotate(90deg)" : "none", color: fg3 }}>▸</span>Waiting on a JD read <span style={{ color: fg3, fontSize: 13 }}>{unscored.length} rows</span></button>
          {unsOpen && <>
            <div style={{ display: "flex", gap: 12, fontSize: 12, color: fg3, marginBottom: 8 }}>sort by {(["sal", "why", "seen"] as const).map((k) => <button key={k} onClick={() => setUsort(k)} style={{ background: "none", border: 0, padding: 0, color: signal.cyan, cursor: "pointer", textDecoration: usort === k ? "underline" : "none" }}>{k === "sal" ? "salary" : k === "why" ? "reason" : "date"}</button>)}</div>
            <p style={{ fontSize: 13, color: fg2, maxWidth: "64ch", margin: "0 0 12px" }}>Salary is only known where a digest subject carried it. Comp for the rest arrives with the JD read, which is the same step that scores them.</p>
            <div style={{ border: `1px solid #243042`, borderRadius: 4, background: GLASS_CARD, boxShadow: GLASS_BEVEL, overflowX: "auto" }}>
              <table style={{ borderCollapse: "collapse", width: "100%" }}>
                {!phone && <thead><tr>{th("Seen")}{th("Role")}{th("Search")}{th("Salary")}{th("Why not scored")}</tr></thead>}
                <tbody>{[...unscored].sort((a, b) => usort === "sal" ? salNum(b.salary) - salNum(a.salary) || b.firstSeen.localeCompare(a.firstSeen) : usort === "why" ? (a.unscoredWhy ?? "").localeCompare(b.unscoredWhy ?? "") || b.firstSeen.localeCompare(a.firstSeen) : b.firstSeen.localeCompare(a.firstSeen) || a.company.localeCompare(b.company)).map((u) => (
                  <tr key={u.jobid} style={{ borderBottom: `1px solid ${border.subtle}`, opacity: 0.7, display: phone ? "grid" : undefined, gridTemplateColumns: phone ? "auto 1fr" : undefined, gap: phone ? "4px 12px" : undefined, padding: phone ? "8px 12px" : undefined }}>
                    <td style={{ ...rowCell, padding: phone ? 0 : "8px 12px", fontFamily: mono, fontSize: 12, whiteSpace: "nowrap", color: fg2 }}>{u.firstSeen.slice(5, 10)}</td>
                    <td style={{ ...rowCell, padding: phone ? 0 : "8px 12px" }}><b style={{ display: "block", color: fg1, fontWeight: 500 }}><a href={u.url} target="_blank" rel="noopener" style={{ color: signal.cyan }}>{u.title}</a></b><span style={{ fontSize: 12, color: fg2 }}>{u.company}{u.location ? ` · ${u.location}` : ""}</span></td>
                    <td style={{ ...rowCell, padding: phone ? 0 : "8px 12px", gridColumn: phone ? 2 : undefined, fontSize: 12, color: fg2 }}>{ARCH[u.alertQuery ?? "manual"] ?? u.alertQuery}</td>
                    <td style={{ ...rowCell, padding: phone ? 0 : "8px 12px", gridColumn: phone ? 2 : undefined, fontFamily: mono, fontSize: 12, color: u.salary ? fg2 : fg3 }}>{u.salary ?? "unknown"}</td>
                    <td style={{ ...rowCell, padding: phone ? 0 : "8px 12px", gridColumn: phone ? 2 : undefined, fontSize: 12, color: fg2 }}>{u.unscoredWhy}</td>
                  </tr>))}</tbody>
              </table>
            </div>
          </>}
        </section>

        {/* below: what fires + queue */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(340px, 1fr))", gap: 16, marginTop: 24 }}>
          <div style={{ border: `1px solid #243042`, borderRadius: 4, padding: "20px 24px", background: GLASS_CARD, boxShadow: GLASS_BEVEL }}>
            <SectionLabel>What a right swipe fires</SectionLabel>
            <ol style={{ margin: "8px 0 0", paddingLeft: 18, fontSize: 13, color: fg2 }}>
              <li style={{ margin: "4px 0" }}><b style={{ color: fg1, fontWeight: 500 }}>Resume cut.</b> The record of record graded against the posting; two pages is the reference. Runs the moment you swipe right, in a live session watching the queue.</li>
              <li style={{ margin: "4px 0" }}><b style={{ color: fg1, fontWeight: 500 }}>Hiring-manager pull.</b> The reports-to line in the posting, then one people search. Labeled explicit, implicit, or unknown. Never a guessed name. Records the apply path too.</li>
              <li style={{ margin: "4px 0" }}><b style={{ color: fg1, fontWeight: 500 }}>Forge page.</b> Built from the Blacksmith base, staged in the bundle. Hosting is a separate, human-approved step.</li>
            </ol>
            <div style={{ marginTop: 12, padding: 12, background: surface.panel, border: `1px solid ${border.subtle}`, borderLeft: `2px solid ${signal.gold}`, borderRadius: 4, color: fg2, fontSize: 13 }}><b style={{ color: fg1, fontWeight: 500 }}>Gate.</b> The full counterpart forge never fires on a swipe. It fires when a human on their side responds.</div>
          </div>
          <div style={{ border: `1px solid #243042`, borderRadius: 4, padding: "20px 24px", background: GLASS_CARD, boxShadow: GLASS_BEVEL }}>
            <SectionLabel>Generating now</SectionLabel>
            <p style={{ fontSize: 13, color: fg2, margin: "8px 0" }}>Up to <select aria-label="Concurrency cap" value={cap} onChange={(e) => post("/api/jobs/settings", "PATCH", { cap: Number(e.target.value) })} style={{ ...ctl, minHeight: 28, padding: "0 24px 0 8px", display: "inline-block", margin: "0 2px" }}>{[3, 5, 10, 99].map((n) => <option key={n} value={n}>{n === 99 ? "all" : n}</option>)}</select> forges run at a time, the rest hold their place. The cap is a cost bound, not a ranking.</p>
            <ul style={{ listStyle: "none", padding: 0, margin: 0, fontFamily: mono, fontSize: 12 }}>{rights.length === 0 ? <li style={{ color: fg3 }}>none yet</li> : rights.map((r, i) => <li key={r.jobid} style={{ display: "flex", gap: 8, padding: "4px 0", borderBottom: `1px dashed ${border.subtle}` }}><span style={{ width: 44, flex: "none", color: i < cap ? signal.green : fg3, fontWeight: 600 }}>{i < cap ? "NOW" : "NEXT"}</span><span style={{ color: fg1 }}>{r.company} · {r.title}</span></li>)}</ul>
            <details style={{ marginTop: 12 }}>
              <summary style={{ cursor: "pointer", fontSize: 13, color: fg2 }}>Every swipe, with undo <span style={{ color: fg3 }}>{swipes.length ? `(${swipes.length})` : ""}</span></summary>
              <ul style={{ listStyle: "none", padding: 0, margin: "8px 0 0", fontSize: 12 }}>{swipes.length === 0 ? <li style={{ color: fg3 }}>no swipes yet</li> : swipes.map((r) => <li key={r.jobid} style={{ display: "flex", gap: 8, alignItems: "center", padding: "4px 0", borderBottom: `1px dashed ${border.subtle}` }}><span style={{ fontFamily: mono, width: 44, flex: "none", color: r.swipe!.direction === "r" ? signal.green : signal.red }}>{r.swipe!.direction === "r" ? "RIGHT" : "LEFT"}</span><span style={{ flex: 1, color: fg1 }}>{r.company} · {r.title}</span>{r.swipe!.why && <span style={{ color: fg3, whiteSpace: "nowrap" }}>{r.swipe!.why}</span>}<span style={{ color: fg3, whiteSpace: "nowrap" }}>{new Date(r.swipe!.at).toLocaleString([], { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" })}</span><button onClick={() => unswipe(r)} aria-label={`Undo swipe on ${r.company}`} style={{ minHeight: 28, minWidth: 28, border: `1px solid ${border.subtle}`, borderRadius: 3, background: surface.panel, color: fg2, cursor: "pointer" }}>✕</button></li>)}</ul>
            </details>
            <p style={{ marginTop: 12, fontSize: 12, color: fg3 }}>Stored in the ARCS database. Synced on every device, read by the pipeline.</p>
          </div>
        </div>
        <footer style={{ marginTop: 24, fontSize: 12, color: fg4, maxWidth: "64ch" }}>Rubric v{spec?.version ?? "?"} from runtime/specs/target-role-scan.json · <Link href="/jobs/profile" style={{ color: signal.cyan }}>Profile Scan</Link> (who) · <Link href="/jobs/scan" style={{ color: signal.cyan }}>Target Scan</Link> (where to aim) · click any role for its Role Scan (the two overlaid on one posting) · trigger rules in runtime/specs/forge-triggers.json. Unverified ATS rows resolve on swipe.</footer>
      </div>
    </main>
  )

  function swipeButtons(r: Row) {
    const sw = r.swipe?.direction; const b = busy === r.jobid
    const base: React.CSSProperties = { minHeight: phone ? 44 : 36, minWidth: 36, padding: "0 12px", border: "1px solid #2a3647", borderRadius: 5, background: "linear-gradient(160deg, rgba(255,255,255,.06), rgba(255,255,255,.01) 38%, rgba(0,0,0,.18)), linear-gradient(165deg, #141c24, #0b1117)", color: "#cbd5e1", cursor: b ? "wait" : "pointer", fontFamily: mono, fontWeight: 600, fontSize: 11, letterSpacing: "0.085em", textTransform: "uppercase", whiteSpace: "nowrap", boxShadow: "inset 0 1px 0 rgba(255,255,255,.09), inset 0 -2px 7px rgba(0,0,0,.5), 0 4px 12px rgba(0,0,0,.4)", flex: phone ? 1 : undefined, opacity: b ? 0.6 : 1 }
    return (<>
      <div style={{ display: "flex", gap: phone ? 8 : 4 }}>
        <button disabled={b} aria-pressed={sw === "l"} onClick={() => swipe(r, "l")} style={{ ...base, ...(sw === "l" ? { color: "#f6c9d2", borderColor: "#FF4D6D99", boxShadow: base.boxShadow + ", 0 0 14px #FF4D6D2b" } : {}) }}>← Left</button>
        <button disabled={b} aria-pressed={sw === "r"} onClick={() => swipe(r, "r")} style={{ ...base, ...(sw === "r" ? { color: "#bdf2dc", borderColor: "#00FF9D99", boxShadow: base.boxShadow + ", 0 0 20px #00FF9D2b" } : {}) }}>Right →</button>
      </div>
      {sw === "l" && <div role="group" aria-label="Why not a fit" style={{ display: "flex", flexWrap: "wrap", gap: 4, marginTop: 4 }}>{WHY.map((w) => { const on = r.swipe?.why === w; return <button key={w} aria-pressed={on} onClick={() => why(r, w)} style={{ minHeight: phone ? 36 : 28, padding: "0 8px", border: `1px solid ${on ? signal.red : border.subtle}`, borderRadius: 999, background: on ? "#FF4D6D1a" : surface.panel, color: on ? signal.red : fg3, fontSize: 11, cursor: "pointer" }}>{w}</button> })}</div>}
    </>)
  }
}
