"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { surface, border, signal } from "@/ui/tokens"

// Compass Lane — three wired surfaces over the live job-search lane.
// Lane view: the five verb-stages as columns, real counts + rows.
// Sources: the ingest streams + a "run a search" control that files an IngestRequest.
// Debrief: outcome-vs-score + the Wayfinder correction record.
// Inline styles only; AA-clean text (secondary #94a3b8, never muted on this ground).

const mono = "'JetBrains Mono', ui-monospace, monospace"
const fg1 = "#e2e8f0", fg2 = "#94a3b8"
const PANEL = "linear-gradient(160deg,#ffffff0d,#ffffff03 38%,#0000002e), linear-gradient(165deg,#11181f,#0a1016)"
const BEVEL = "inset 0 1px 0 #ffffff1a, inset 0 -2px 8px #00000080, 0 5px 16px #00000073"

export type StageItem = { jobid: string; company: string; title: string; meta?: string; score?: string; tone?: string }
export type Stage = { verb: string; label: string; print: string; sla?: string; count: number; items: StageItem[]; empty?: string }
export type Src = { key: string; label: string; adapter: string; status: string; lastRunAt: string | null; pollWindow: string | null; note: string | null }
export type Req = { fromDate: string | null; toDate: string | null; status: string; rowsAdded: number | null; requestedAt: string; note: string | null }
export type OutcomeRow = { jobid: string; company: string; fate: string; predicted: string; actual: string; honesty: string }
export type Corr = { learned: string; pattern: string | null; avoid: string | null; logic: string | null }
export type LaneData = { stages: Stage[]; sources: Src[]; requests: Req[]; outcomes: OutcomeRow[]; corrections: Corr[]; live: string }

const TABS = [["lane", "Lane view"], ["sources", "Sources"], ["debrief", "Debrief"]] as const
const statusDot: Record<string, string> = { live: signal.green, detected: signal.gold, proposed: fg2, paused: signal.red, queued: signal.cyan, running: signal.cyan, done: signal.green, failed: signal.red }

const card: React.CSSProperties = { border: "1px solid #243042", borderRadius: 4, background: PANEL, boxShadow: BEVEL }
const lab: React.CSSProperties = { fontFamily: mono, fontSize: 11, fontWeight: 700, letterSpacing: ".14em", textTransform: "uppercase", color: fg2 }

export function LaneSurfaces({ data }: { data: LaneData }) {
  const [tab, setTab] = useState<(typeof TABS)[number][0]>("lane")
  return (
    <div style={{ maxWidth: 1280, margin: "0 auto", padding: "24px 16px 48px", color: fg1, fontFamily: "Inter, system-ui, sans-serif" }}>
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

function LaneView({ data }: { data: LaneData }) {
  return (<>
    <H>Lane view</H>
    <Lede>Five stages as columns. A row enters at Research and moves right on decisions and outcomes. Each column names what it prints and the SLA it holds.</Lede>
    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(224px, 1fr))", gap: 12 }}>
      {data.stages.map((s) => (
        <div key={s.label} style={{ ...card, minHeight: 240, display: "flex", flexDirection: "column" }}>
          <header style={{ padding: "10px 12px", borderBottom: `1px solid ${border.subtle}` }}>
            <span style={{ fontFamily: mono, fontSize: 10.5, fontWeight: 700, letterSpacing: ".14em", textTransform: "uppercase", color: signal.cyan }}>{s.verb}</span>
            <h3 style={{ margin: "2px 0 0", fontSize: 14, fontWeight: 600 }}>{s.label}<span style={{ fontFamily: mono, fontSize: 11, color: fg2, marginLeft: 6 }}>{s.count}</span></h3>
            <div style={{ fontSize: 12, color: fg2, marginTop: 4 }}>Prints: {s.print}{s.sla ? ` · SLA ${s.sla}` : ""}</div>
          </header>
          <div style={{ padding: 8, display: "flex", flexDirection: "column", gap: 8, flex: 1 }}>
            {s.items.length === 0
              ? <div style={{ padding: "16px 10px", textAlign: "center", color: fg2, fontSize: 12 }}>{s.empty ?? "Nothing here yet."}</div>
              : s.items.map((it) => (
                <Link key={it.jobid} href={`/jobs/${it.jobid}`} style={{ padding: 10, border: `1px solid ${border.subtle}`, borderRadius: 4, background: surface.panel, textDecoration: "none", display: "block" }}>
                  <b style={{ display: "block", fontWeight: 500, fontSize: 13, color: fg1 }}>{it.title}</b>
                  <span style={{ fontSize: 12, color: fg2 }}>{it.company}</span>
                  <span style={{ display: "flex", gap: 6, flexWrap: "wrap", marginTop: 6, alignItems: "center" }}>
                    {it.score && <span style={{ fontFamily: mono, fontSize: 12, color: it.tone ?? signal.green }}>{it.score}</span>}
                    {it.meta && <span style={{ fontFamily: mono, fontSize: 10.5, color: fg2, letterSpacing: ".04em" }}>{it.meta}</span>}
                  </span>
                </Link>
              ))}
          </div>
        </div>
      ))}
    </div>
  </>)
}

function Sources({ data }: { data: LaneData }) {
  const router = useRouter()
  const [sourceKey, setSourceKey] = useState(data.sources[0]?.key ?? "")
  const [from, setFrom] = useState(""); const [to, setTo] = useState(""); const [busy, setBusy] = useState(false)
  async function run() {
    if (!sourceKey) return; setBusy(true)
    try {
      await fetch("/api/jobs/lane", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ sourceKey, fromDate: from || null, toDate: to || null }) })
      router.refresh()
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
          <input type="date" aria-label="From" value={from} onChange={(e) => setFrom(e.target.value)} style={{ ...ctl, colorScheme: "dark" }} />
          <input type="date" aria-label="To" value={to} onChange={(e) => setTo(e.target.value)} style={{ ...ctl, colorScheme: "dark" }} />
          <button type="button" onClick={run} disabled={busy} style={{ ...ctl, minHeight: 36, color: "#b9e8f4", borderColor: "#00F0FF3a", cursor: busy ? "default" : "pointer", opacity: busy ? 0.6 : 1, fontFamily: mono, fontSize: 11, letterSpacing: ".08em", textTransform: "uppercase" }}>{busy ? "filing…" : "Run a search"}</button>
        </div>
        <span style={{ fontSize: 12, color: fg2 }}>Files an ingest request over that window. The sweep picks it up; new rows appear in Research.</span>
        <div style={{ marginTop: 6 }}>
          <span style={{ ...lab, fontSize: 10 }}>Request history</span>
          <ul style={{ listStyle: "none", margin: "8px 0 0", padding: 0 }}>
            {data.requests.length === 0 ? <li style={{ color: fg2, fontSize: 12 }}>none yet</li> : data.requests.map((r, i) => (
              <li key={i} style={{ display: "flex", gap: 10, padding: "6px 0", borderBottom: `1px dashed ${border.subtle}`, fontSize: 12, fontFamily: mono, color: fg2 }}>
                <span style={{ minWidth: 96, color: fg1 }}>{r.fromDate ?? "…"} → {r.toDate ?? "…"}</span>
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
  return (<>
    <H>Debrief</H>
    <Lede>Filed when a row closes: what happened against what the scan predicted, and a correction record, required on a reject or pivot. Nothing has closed yet, so this fills as outcomes land.</Lede>
    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: 12 }}>
      <div style={{ ...card, padding: "16px 18px" }}>
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
