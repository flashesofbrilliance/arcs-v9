"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { surface, border, signal } from "@/ui/tokens"
import { REASONS, FATES, type FateKey } from "@/lib/lane-outcome"

// Compass Lane — three wired surfaces over the live job-search lane.
// Lane view: the five verb-stages as columns, real counts + rows.
// Sources: the ingest streams + a "run a search" control that files an IngestRequest.
// Debrief: outcome-vs-score + the Wayfinder correction record.
// Inline styles only; AA-clean text (secondary #94a3b8, never muted on this ground).

const mono = "'JetBrains Mono', ui-monospace, monospace"
const fg1 = "#e2e8f0", fg2 = "#94a3b8"
const PANEL = "linear-gradient(160deg,#ffffff0d,#ffffff03 38%,#0000002e), linear-gradient(165deg,#11181f,#0a1016)"
const BEVEL = "inset 0 1px 0 #ffffff1a, inset 0 -2px 8px #00000080, 0 5px 16px #00000073"

export type StageItem = { jobid: string; company: string; title: string; meta?: string; score?: string; tone?: string; stage?: string; manual?: boolean }
export type Stage = { key: string; verb: string; label: string; print: string; sla?: string; count: number; items: StageItem[]; empty?: string }
export type Src = { key: string; label: string; adapter: string; status: string; lastRunAt: string | null; pollWindow: string | null; note: string | null }
export type Req = { fromDate: string | null; toDate: string | null; query: string | null; status: string; rowsAdded: number | null; requestedAt: string; note: string | null }
export type OutcomeRow = { jobid: string; company: string; fate: string; predicted: string; actual: string; honesty: string; reason: string | null }
export type Corr = { learned: string; pattern: string | null; avoid: string | null; logic: string | null }
export type LaneData = { stages: Stage[]; sources: Src[]; requests: Req[]; outcomes: OutcomeRow[]; corrections: Corr[]; live: string }

const TABS = [["lane", "Lane view"], ["sources", "Sources"], ["debrief", "Debrief"]] as const
const ORDER = ["research", "qualify", "apply", "interview", "outcome"] as const
const STAGE_LABEL: Record<string, string> = { research: "Research", qualify: "Qualify", apply: "Apply & screen", interview: "Interview loop", outcome: "Outcome" }
const statusDot: Record<string, string> = { live: signal.green, detected: signal.gold, proposed: fg2, paused: signal.red, queued: signal.cyan, running: signal.cyan, done: signal.green, failed: signal.red }

const card: React.CSSProperties = { border: "1px solid #243042", borderRadius: 4, background: PANEL, boxShadow: BEVEL }
const lab: React.CSSProperties = { fontFamily: mono, fontSize: 11, fontWeight: 700, letterSpacing: ".14em", textTransform: "uppercase", color: fg2 }

export function LaneSurfaces({ data }: { data: LaneData }) {
  const [tab, setTab] = useState<(typeof TABS)[number][0]>("lane")
  return (
    <div style={{ width: "100%", maxWidth: 1280, margin: "0 auto", boxSizing: "border-box", padding: "24px 16px 48px", color: fg1, fontFamily: "Inter, system-ui, sans-serif" }}>
      <div style={{ display: "flex", flexWrap: "wrap", gap: "8px 16px", alignItems: "baseline", marginBottom: 16 }}>
        <span style={{ ...lab, color: signal.cyan }}>Compass Lane</span>
        <span style={{ fontFamily: mono, fontSize: 11, color: fg2, letterSpacing: ".08em" }}>· job search · wired</span>
        <Link href="/jobs" style={{ marginLeft: "auto", color: signal.cyan, fontFamily: mono, fontSize: 11, textDecoration: "none", letterSpacing: ".1em", textTransform: "uppercase" }}>← board</Link>
      </div>

      <div role="tablist" aria-label="Lane surfaces" style={{ display: "inline-flex", gap: 4, padding: 4, borderRadius: 6, background: "linear-gradient(180deg,#090d12,#0c1219)", boxShadow: "inset 0 2px 6px #000000b3", marginBottom: 20 }}>
        {TABS.map(([id, label]) => {
          const on = tab === id
          return <button key={id} role="tab" aria-selected={on} onClick={() => setTab(id)} style={{ minHeight: 36, padding: "0 14px", border: `1px solid ${on ? "#00F0FF55" : "transparent"}`, borderRadius: 5, background: on ? "linear-gradient(180deg,#0d141c,#0f1822)" : "transparent", color: on ? "#b9e8f4" : fg2, cursor: "pointer", fontFamily: mono, fontSize: 11, fontWeight: 600, letterSpacing: ".06em", textTransform: "uppercase" }}>{label}</button>
        })}
      </div>

      {tab === "lane" && <LaneView data={data} />}
      {tab === "sources" && <Sources data={data} />}
      {tab === "debrief" && <Debrief data={data} />}
    </div>
  )
}

function H({ children }: { children: React.ReactNode }) { return <h1 style={{ fontSize: 20, fontWeight: 600, letterSpacing: "-.015em", margin: "0 0 4px" }}>{children}</h1> }
function Lede({ children }: { children: React.ReactNode }) { return <p style={{ margin: "0 0 16px", color: fg2, fontSize: 13, maxWidth: "64ch" }}>{children}</p> }

function StageControls({ it, onMove }: { it: StageItem; onMove: (jobid: string, stage: string | null) => void }) {
  const idx = ORDER.indexOf((it.stage ?? "research") as (typeof ORDER)[number])
  const prev = idx > 0 ? ORDER[idx - 1] : null
  const next = idx >= 0 && idx < ORDER.length - 1 ? ORDER[idx + 1] : null
  const btn: React.CSSProperties = { minHeight: 28, padding: "0 8px", border: `1px solid ${border.subtle}`, borderRadius: 4, background: surface.elevated, color: fg2, cursor: "pointer", fontFamily: mono, fontSize: 10, letterSpacing: ".06em", textTransform: "uppercase" }
  const go = (stage: string | null) => onMove(it.jobid, stage)
  return (
    <div style={{ display: "flex", gap: 6, marginTop: 8, alignItems: "center", flexWrap: "wrap" }}>
      {prev && <button type="button" style={btn} onClick={() => go(prev)} aria-label={`Move ${it.company} back to ${STAGE_LABEL[prev]}`}>←</button>}
      {next && <button type="button" style={{ ...btn, color: "#b9e8f4", borderColor: "#00F0FF3a" }} onClick={() => go(next)} aria-label={`Advance ${it.company} to ${STAGE_LABEL[next]}`}>{next === "apply" ? "mark applied →" : next === "interview" ? "→ interview" : `→ ${STAGE_LABEL[next]}`}</button>}
      {it.manual && <button type="button" style={btn} onClick={() => go(null)} aria-label={`Reset ${it.company} to auto stage`}>auto</button>}
    </div>
  )
}

function LaneView({ data }: { data: LaneData }) {
  const router = useRouter()
  // Optimistic overrides: jobid -> stage, so a drop lands instantly; the server
  // refresh reconciles. Drag-and-drop ported from the 2025 job-tracker prototype.
  const [moved, setMoved] = useState<Record<string, string>>({})
  const [q, setQ] = useState("")
  const [over, setOver] = useState<string | null>(null)
  const [err, setErr] = useState<string | null>(null)
  const all = data.stages.flatMap((s) => s.items.map((it) => ({ ...it, stage: moved[it.jobid] ?? it.stage ?? s.key })))
  const needle = q.trim().toLowerCase()
  const match = (it: StageItem) => !needle || `${it.company} ${it.title}`.toLowerCase().includes(needle)
  // A move into Outcome opens the close form first; nothing moves until it is saved.
  const [closing, setClosing] = useState<{ jobid: string; company: string } | null>(null)
  async function drop(jobid: string, stage: string | null, outcome?: { fate: FateKey; reason: string | null; note: string | null }) {
    const cur = all.find((x) => x.jobid === jobid)
    if (!cur || (stage && cur.stage === stage)) return
    if (stage === "outcome" && !outcome) { setClosing({ jobid, company: cur.company }); return }
    if (stage) setMoved((m) => ({ ...m, [jobid]: stage }))
    setErr(null)
    const r = await fetch("/api/jobs/lane", { method: "PATCH", headers: { "content-type": "application/json" }, body: JSON.stringify({ jobid, laneStage: stage, outcome }) })
    if (!r.ok) {
      const j = await r.json().catch(() => ({}))
      setMoved((m) => { const n = { ...m }; delete n[jobid]; return n })
      setErr(`Move failed (${j.error ?? `HTTP ${r.status}`}); the card went back.`); return
    }
    router.refresh()
  }
  return (<>
    {closing && <CloseForm company={closing.company} onCancel={() => setClosing(null)} onSave={(o) => { const id = closing.jobid; setClosing(null); drop(id, "outcome", o) }} />}
    <H>Lane view</H>
    <Lede>Five stages as columns. A row enters at Research and moves right on decisions and outcomes. Drag a card to another column, or use the arrows. Each column names what it prints and the SLA it holds.</Lede>
    <div style={{ display: "flex", gap: 12, alignItems: "center", flexWrap: "wrap", marginBottom: 12 }}>
      <input type="search" value={q} onChange={(e) => setQ(e.target.value)} placeholder="Filter by company or title" aria-label="Filter cards" style={{ minHeight: 36, minWidth: 260, flex: "0 1 360px", padding: "0 12px", border: `1px solid ${border.subtle}`, borderRadius: 4, background: surface.panel, color: fg1, fontSize: 13 }} />
      {err && <span role="alert" style={{ color: signal.red, fontSize: 12 }}>{err}</span>}
    </div>
    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(224px, 1fr))", gap: 12 }}>
      {data.stages.map((s) => {
        const items = all.filter((it) => it.stage === s.key)
        const shown = items.filter(match)
        const hot = over === s.key
        return (
        <div key={s.key}
          onDragOver={(e) => { e.preventDefault(); e.dataTransfer.dropEffect = "move"; if (over !== s.key) setOver(s.key) }}
          onDragLeave={(e) => { if (!e.currentTarget.contains(e.relatedTarget as Node)) setOver(null) }}
          onDrop={(e) => { e.preventDefault(); setOver(null); const id = e.dataTransfer.getData("text/plain"); if (id) drop(id, s.key) }}
          style={{ ...card, minHeight: 240, display: "flex", flexDirection: "column", outline: hot ? `1px solid ${signal.cyan}88` : "none", boxShadow: hot ? `${BEVEL}, 0 0 16px #00F0FF22` : BEVEL }}>
          <header style={{ padding: "10px 12px", borderBottom: `1px solid ${border.subtle}` }}>
            <span style={{ fontFamily: mono, fontSize: 10.5, fontWeight: 700, letterSpacing: ".14em", textTransform: "uppercase", color: signal.cyan }}>{s.verb}</span>
            <h3 style={{ margin: "2px 0 0", fontSize: 14, fontWeight: 600 }}>{s.label}<span style={{ fontFamily: mono, fontSize: 11, color: fg2, marginLeft: 6 }}>{needle ? `${shown.length}/${items.length}` : items.length}</span></h3>
            <div style={{ fontSize: 12, color: fg2, marginTop: 4 }}>Prints: {s.print}{s.sla ? ` · SLA ${s.sla}` : ""}</div>
          </header>
          <div style={{ padding: 8, display: "flex", flexDirection: "column", gap: 8, flex: 1, maxHeight: 560, overflowY: "auto" }}>
            {shown.length === 0
              ? <div style={{ padding: "16px 10px", textAlign: "center", color: fg2, fontSize: 12 }}>{needle && items.length ? "No match in this column." : s.empty ?? "Nothing here yet."}</div>
              : shown.map((it) => (
                <div key={it.jobid} draggable onDragStart={(e) => { e.dataTransfer.setData("text/plain", it.jobid); e.dataTransfer.effectAllowed = "move" }}
                  style={{ padding: 10, border: `1px solid ${border.subtle}`, borderRadius: 4, background: surface.panel, cursor: "grab" }}>
                  <Link href={`/jobs/${it.jobid}`} draggable={false} style={{ textDecoration: "none", display: "block" }}>
                    <b style={{ display: "block", fontWeight: 500, fontSize: 13, color: fg1 }}>{it.title}</b>
                    <span style={{ fontSize: 12, color: fg2 }}>{it.company}</span>
                    <span style={{ display: "flex", gap: 6, flexWrap: "wrap", marginTop: 6, alignItems: "center" }}>
                      {it.score && <span style={{ fontFamily: mono, fontSize: 12, color: it.tone ?? signal.green }}>{it.score}</span>}
                      {it.meta && <span style={{ fontFamily: mono, fontSize: 10.5, color: fg2, letterSpacing: ".04em" }}>{it.meta}</span>}
                      {(it.manual || moved[it.jobid]) && <span style={{ fontFamily: mono, fontSize: 9, color: signal.cyan, letterSpacing: ".08em", textTransform: "uppercase" }}>moved</span>}
                    </span>
                  </Link>
                  <StageControls it={it} onMove={drop} />
                </div>
              ))}
          </div>
        </div>
      )})}
    </div>
  </>)
}

const FATE_LABEL: Record<FateKey, string> = { offer: "Offer", reject: "Rejected", ghosted: "Ghosted", withdrawn: "Withdrew" }

// The close form: fate, then a reason from the one board taxonomy, then an
// optional note. A loss cannot be saved without a reason (the route refuses it too).
function CloseForm({ company, onCancel, onSave }: { company: string; onCancel: () => void; onSave: (o: { fate: FateKey; reason: string | null; note: string | null }) => void }) {
  const [fate, setFate] = useState<FateKey | null>(null)
  const [reason, setReason] = useState<string | null>(null)
  const [note, setNote] = useState("")
  const needReason = fate !== null && fate !== "offer"
  const ok = fate !== null && (!needReason || reason !== null)
  const chip = (on: boolean, tone: string): React.CSSProperties => ({ minHeight: 32, padding: "0 12px", border: `1px solid ${on ? tone : border.subtle}`, borderRadius: 999, background: on ? `${tone}1f` : surface.panel, color: on ? tone : fg2, cursor: "pointer", fontSize: 12 })
  return (
    <div role="dialog" aria-modal="true" aria-label={`Close ${company}`} onKeyDown={(e) => { if (e.key === "Escape") onCancel() }}
      style={{ position: "fixed", inset: 0, zIndex: 50, background: "#020408cc", display: "grid", placeItems: "center", padding: 16 }}>
      <div style={{ ...card, width: "100%", maxWidth: 440, padding: "18px 20px", background: "linear-gradient(165deg,#11181f,#0a1016)" }}>
        <span style={{ ...lab, color: signal.cyan }}>Close the row</span>
        <h3 style={{ margin: "4px 0 14px", fontSize: 16, fontWeight: 600 }}>{company}</h3>
        <div style={{ fontSize: 12, color: fg2, marginBottom: 6 }}>What happened?</div>
        <div role="group" aria-label="Fate" style={{ display: "flex", flexWrap: "wrap", gap: 6, marginBottom: 14 }}>
          {(Object.keys(FATES) as FateKey[]).map((f) => <button key={f} type="button" autoFocus={f === "offer"} aria-pressed={fate === f} onClick={() => setFate(f)} style={chip(fate === f, f === "offer" ? signal.green : signal.red)}>{FATE_LABEL[f]}</button>)}
        </div>
        <div style={{ fontSize: 12, color: fg2, marginBottom: 6 }}>{fate === "offer" ? "What won it? (optional)" : "Main reason"}</div>
        <div role="group" aria-label="Reason" style={{ display: "flex", flexWrap: "wrap", gap: 6, marginBottom: 14 }}>
          {REASONS.map((r) => <button key={r} type="button" aria-pressed={reason === r} onClick={() => setReason(reason === r ? null : r)} style={chip(reason === r, signal.cyan)}>{r}</button>)}
        </div>
        <label style={{ display: "block", fontSize: 12, color: fg2, marginBottom: 14 }}>Note (optional)
          <input value={note} onChange={(e) => setNote(e.target.value)} maxLength={500} style={{ display: "block", width: "100%", marginTop: 6, minHeight: 36, padding: "0 10px", border: `1px solid ${border.subtle}`, borderRadius: 4, background: surface.panel, color: fg1, fontSize: 13 }} />
        </label>
        <div style={{ display: "flex", gap: 8, justifyContent: "flex-end" }}>
          <button type="button" onClick={onCancel} style={{ minHeight: 36, padding: "0 14px", border: `1px solid ${border.subtle}`, borderRadius: 4, background: "transparent", color: fg2, cursor: "pointer" }}>Cancel</button>
          <button type="button" disabled={!ok} onClick={() => fate && onSave({ fate, reason, note: note.trim() || null })} style={{ minHeight: 36, padding: "0 14px", border: `1px solid ${ok ? "#00F0FF66" : border.subtle}`, borderRadius: 4, background: ok ? "#00F0FF14" : "transparent", color: ok ? "#b9e8f4" : fg2, cursor: ok ? "pointer" : "not-allowed" }}>Close the row</button>
        </div>
      </div>
    </div>
  )
}

function Sources({ data }: { data: LaneData }) {
  const router = useRouter()
  const [sourceKey, setSourceKey] = useState(data.sources[0]?.key ?? "")
  const [from, setFrom] = useState(""); const [to, setTo] = useState(""); const [query, setQuery] = useState(""); const [busy, setBusy] = useState(false)
  const [filed, setFiled] = useState<{ query: string; from: string; to: string } | null>(null)
  async function run() {
    if (!sourceKey) return; setBusy(true); setFiled(null)
    try {
      const r = await fetch("/api/jobs/lane", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ sourceKey, fromDate: from || null, toDate: to || null, query: query.trim() || null }) })
      if (r.ok) { setFiled({ query: query.trim(), from, to }); setQuery(""); router.refresh() }
    } finally { setBusy(false) }
  }
  const ctl: React.CSSProperties = { minHeight: 36, padding: "0 10px", background: "linear-gradient(180deg,#090d12,#0c1219)", border: "1px solid #1c2736", borderRadius: 5, color: fg1, font: "inherit", fontSize: 13 }
  return (<>
    <H>Sources</H>
    <Lede>Every stream the lane ingests, with its last run and its adapter. The date range is a real query window that files an ingest request; the sweep executes it and rows land in Research.</Lede>
    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(340px, 1fr))", gap: 12 }}>
      <div style={card}>
        {data.sources.map((s) => (
          <div key={s.key} style={{ display: "grid", gridTemplateColumns: "1fr auto", gap: 10, padding: "12px 14px", borderBottom: `1px solid ${border.subtle}` }}>
            <div>
              <b style={{ display: "block", fontWeight: 500 }}><span style={{ display: "inline-block", width: 7, height: 7, borderRadius: "50%", marginRight: 6, background: statusDot[s.status] ?? fg2, boxShadow: `0 0 8px 1px ${statusDot[s.status] ?? fg2}` }} />{s.label}</b>
              <span style={{ fontSize: 12, color: fg2 }}>{s.note}</span>
            </div>
            <div style={{ textAlign: "right" }}>
              <span style={{ fontFamily: mono, fontSize: 11, letterSpacing: ".06em", color: fg2, textTransform: "uppercase", display: "block" }}>{s.status}</span>
              <span style={{ fontFamily: mono, fontSize: 11, color: fg2 }}>{s.adapter} · {s.lastRunAt ? new Date(s.lastRunAt).toLocaleDateString() : "never run"}</span>
            </div>
          </div>
        ))}
      </div>
      <div style={{ ...card, padding: "14px 16px", display: "grid", gap: 10, alignContent: "start" }}>
        <span style={lab}>Run a search</span>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 8, alignItems: "center" }}>
          <select aria-label="Source" value={sourceKey} onChange={(e) => setSourceKey(e.target.value)} style={ctl}>{data.sources.map((s) => <option key={s.key} value={s.key}>{s.label}</option>)}</select>
          <input type="search" aria-label="Title or keyword" placeholder="Title or keyword (optional)" value={query} onChange={(e) => setQuery(e.target.value)} onKeyDown={(e) => { if (e.key === "Enter") run() }} style={{ ...ctl, flex: "1 1 180px", minWidth: 160 }} />
          <input type="date" aria-label="From" value={from} onChange={(e) => setFrom(e.target.value)} style={{ ...ctl, colorScheme: "dark" }} />
          <input type="date" aria-label="To" value={to} onChange={(e) => setTo(e.target.value)} style={{ ...ctl, colorScheme: "dark" }} />
          <button type="button" onClick={run} disabled={busy} style={{ ...ctl, minHeight: 36, color: "#b9e8f4", borderColor: "#00F0FF3a", cursor: busy ? "default" : "pointer", opacity: busy ? 0.6 : 1, fontFamily: mono, fontSize: 11, letterSpacing: ".08em", textTransform: "uppercase" }}>{busy ? "filing…" : "Run a search"}</button>
        </div>
        {filed ? (
          <div role="status" style={{ display: "flex", gap: 8, alignItems: "baseline", padding: "8px 10px", borderRadius: 5, border: "1px solid #00FF9d3a", background: "linear-gradient(165deg,#00FF9d0a,#00000030)", fontSize: 12, color: fg1 }}>
            <span style={{ fontFamily: mono, color: "#00FF9d", fontSize: 11 }}>QUEUED</span>
            <span style={{ color: fg2 }}>Filed <b style={{ color: fg1, fontWeight: 500 }}>{filed.query || "all titles"}</b>{filed.from || filed.to ? <> · {filed.from || "…"} → {filed.to || "…"}</> : " · full window"}. The sweep pulls only <b style={{ color: fg1, fontWeight: 500 }}>net-new</b> postings (deduped against the board) into Research.</span>
          </div>
        ) : <span style={{ fontSize: 12, color: fg2 }}>Files an ingest request over that window and title. The sweep picks it up and pulls net-new rows (deduped against the board) into Research.</span>}
        <div style={{ marginTop: 6 }}>
          <span style={{ ...lab, fontSize: 10 }}>Request history</span>
          <ul style={{ listStyle: "none", margin: "8px 0 0", padding: 0 }}>
            {data.requests.length === 0 ? <li style={{ color: fg2, fontSize: 12 }}>none yet</li> : data.requests.map((r, i) => (
              <li key={i} style={{ display: "flex", gap: 10, padding: "6px 0", borderBottom: `1px dashed ${border.subtle}`, fontSize: 12, fontFamily: mono, color: fg2 }}>
                <span style={{ minWidth: 96, color: fg1 }}>{r.fromDate ?? "…"} → {r.toDate ?? "…"}</span>
                {r.query && <span style={{ color: fg1, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", maxWidth: 140 }} title={r.query}>&ldquo;{r.query}&rdquo;</span>}
                <span style={{ color: statusDot[r.status] ?? fg2 }}>{r.status}</span>
                <span style={{ marginLeft: "auto" }}>{r.rowsAdded != null ? `${r.rowsAdded} rows` : ""}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  </>)
}

function Debrief({ data }: { data: LaneData }) {
  // Losses by reason (slice 3): closed:lost and closed:learned rows, counted by the
  // one board taxonomy. Small n is shown as small n, never as a rate.
  const losses = data.outcomes.filter((o) => o.fate !== "closed:won")
  const byReason = REASONS.map((r) => [r, losses.filter((o) => o.reason === r).length] as const).filter(([, n]) => n > 0).sort((a, b) => b[1] - a[1])
  const untagged = losses.filter((o) => !o.reason).length
  return (<>
    <H>Debrief</H>
    <Lede>Filed when a row closes: what happened against what the scan predicted, and a correction record, required on a reject or pivot. Nothing has closed yet, so this fills as outcomes land.</Lede>
    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: 12 }}>
      <div style={{ ...card, padding: "16px 18px", overflowX: "auto" }}>
        <h3 style={{ margin: "0 0 8px", fontSize: 15, fontWeight: 600 }}>Outcome vs the ex-ante score</h3>
        {data.outcomes.length === 0
          ? <p style={{ color: fg2, fontSize: 13 }}>No rows have closed. When one does, its actual outcome is scored against the composite the scan filed, and any honesty gap shows here.</p>
          : <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 12 }}>
              <thead><tr>{["Role", "Predicted", "Actual", "Honesty"].map((h) => <th key={h} style={{ textAlign: "left", fontFamily: mono, fontSize: 10.5, fontWeight: 700, letterSpacing: ".12em", textTransform: "uppercase", color: fg2, padding: "6px 8px", borderBottom: `1px solid ${border.subtle}` }}>{h}</th>)}</tr></thead>
              <tbody>{data.outcomes.map((o) => (
                <tr key={o.jobid}><td style={{ padding: 8, color: fg1, borderBottom: `1px solid ${border.subtle}` }}>{o.company}</td><td style={{ padding: 8, fontFamily: mono, color: fg2, borderBottom: `1px solid ${border.subtle}` }}>{o.predicted}</td><td style={{ padding: 8, fontFamily: mono, color: fg2, borderBottom: `1px solid ${border.subtle}` }}>{o.actual}</td><td style={{ padding: 8, color: fg2, borderBottom: `1px solid ${border.subtle}` }}>{o.honesty}</td></tr>
              ))}</tbody>
            </table>}
      </div>
      <div style={{ ...card, padding: "16px 18px" }}>
        <h3 style={{ margin: "0 0 8px", fontSize: 15, fontWeight: 600 }}>Losses by reason <span style={{ fontFamily: mono, fontSize: 11, color: fg2 }}>n = {losses.length}</span></h3>
        {losses.length === 0
          ? <p style={{ color: fg2, fontSize: 13 }}>No losses closed yet. Dropping a card into Outcome asks for a fate and a reason; they count here.</p>
          : <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
              {byReason.map(([r, n]) => <li key={r} style={{ display: "flex", gap: 10, alignItems: "center", padding: "4px 0", fontSize: 13 }}><span style={{ width: 96, color: fg1 }}>{r}</span><span aria-hidden style={{ height: 8, width: `${(n / losses.length) * 100}%`, maxWidth: 220, minWidth: 8, background: signal.red, opacity: .55, borderRadius: 2 }} /><span style={{ fontFamily: mono, fontSize: 12, color: fg2 }}>{n}</span></li>)}
              {untagged > 0 && <li style={{ fontSize: 12, color: fg2, paddingTop: 4 }}>{untagged} closed before reasons were recorded</li>}
            </ul>}
        {losses.length > 0 && losses.length < 30 && <p style={{ fontSize: 12, color: fg2, margin: "10px 0 0" }}>Counts, not rates: below 30 closed, a pattern here is a hint, not a finding.</p>}
      </div>
      <div style={{ ...card, padding: "16px 18px", overflowX: "auto" }}>
        <h3 style={{ margin: "0 0 8px", fontSize: 15, fontWeight: 600 }}>Correction record</h3>
        {data.corrections.length === 0
          ? <p style={{ color: fg2, fontSize: 13 }}>Filed on a reject or pivot: what you learned, the pattern it fits, what you will avoid, and the decision logic. These are what the learning loop reads.</p>
          : data.corrections.map((c, i) => (
            <dl key={i} style={{ margin: 0 }}>
              {([["today I learned", c.learned], ["recognizes pattern", c.pattern], ["will avoid", c.avoid], ["decision logic", c.logic]] as const).map(([k, v]) => v ? (<div key={k}><dt style={{ fontFamily: mono, fontSize: 10.5, fontWeight: 700, letterSpacing: ".14em", textTransform: "uppercase", color: signal.cyan, marginTop: 10 }}>{k}</dt><dd style={{ margin: "2px 0 0", fontSize: 13, color: fg2 }}>{v}</dd></div>) : null)}
            </dl>
          ))}
      </div>
    </div>
  </>)
}
