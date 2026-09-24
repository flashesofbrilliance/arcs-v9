"use client"

import { useMemo, useState } from "react"

export type CloseRow = {
  id: string
  question: string
  trueNorth: string
  nci: number
  render: string
  createdAt: string
}

const T = {
  bg: "#020408",
  surface: "#0d1117",
  border: "#1e293b",
  text: "#e2e8f0",
  muted: "#475569",
  dimmed: "#64748b",
  cyan: "#00F0FF",
  green: "#00FF9D",
  gold: "#FFD700",
  red: "#FF4D6D",
}

const RENDER_COLOR: Record<string, string> = {
  SHARP: T.green,
  DEGRADED: T.gold,
  GRAIN: T.dimmed,
  MOIRE: T.cyan,
}

type Draft = { matched: boolean | null; regret: number; what: string; learning: string }
type Status = "open" | "saving" | "done" | { error: string }

const emptyDraft = (): Draft => ({ matched: null, regret: 0, what: "", learning: "" })

export function CloseList({ rows }: { rows: CloseRow[] }) {
  const [drafts, setDrafts] = useState<Record<string, Draft>>({})
  const [status, setStatus] = useState<Record<string, Status>>({})

  const draft = (id: string) => drafts[id] ?? emptyDraft()
  const set = (id: string, patch: Partial<Draft>) =>
    setDrafts((d) => ({ ...d, [id]: { ...draft(id), ...patch } }))

  // Live tally of what's been closed this session, so you can aim for a
  // distribution the calibration study can use (matched AND drifted across
  // Y-states) rather than a lopsided all-matched pile.
  const tally = useMemo(() => {
    const done = rows.filter((r) => status[r.id] === "done")
    const matched = done.filter((r) => drafts[r.id]?.matched === true).length
    const drifted = done.filter((r) => drafts[r.id]?.matched === false).length
    const byRender: Record<string, number> = {}
    for (const r of done) byRender[r.render] = (byRender[r.render] ?? 0) + 1
    return { total: done.length, matched, drifted, byRender }
  }, [rows, status, drafts])

  async function close(id: string) {
    const d = draft(id)
    if (typeof d.matched !== "boolean") {
      setStatus((s) => ({ ...s, [id]: { error: "pick Landed or Drifted" } }))
      return
    }
    if (!d.what.trim()) {
      setStatus((s) => ({ ...s, [id]: { error: "what actually happened is required" } }))
      return
    }
    setStatus((s) => ({ ...s, [id]: "saving" }))
    try {
      const res = await fetch(`/api/receipts/${id}/outcome`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          what: d.what.trim(),
          matched: d.matched,
          regretScore: d.regret,
          learning: d.learning.trim() || undefined,
        }),
      })
      const body = (await res.json().catch(() => ({}))) as { error?: string }
      if (!res.ok) {
        setStatus((s) => ({ ...s, [id]: { error: body.error || `HTTP ${res.status}` } }))
        return
      }
      setStatus((s) => ({ ...s, [id]: "done" }))
    } catch (err) {
      setStatus((s) => ({ ...s, [id]: { error: err instanceof Error ? err.message : "network error" } }))
    }
  }

  const label: React.CSSProperties = { fontSize: 11, color: T.dimmed, textTransform: "uppercase", letterSpacing: "0.04em" }
  const input: React.CSSProperties = {
    background: T.bg, color: T.text, border: `1px solid ${T.border}`,
    borderRadius: 6, padding: "6px 8px", fontSize: 13, width: "100%", fontFamily: "inherit",
  }

  return (
    <main style={{ background: T.bg, color: T.text, minHeight: "100vh", padding: "32px 16px", fontFamily: "ui-sans-serif, system-ui, sans-serif" }}>
      <div style={{ maxWidth: 820, margin: "0 auto" }}>
        <h1 style={{ fontSize: 22, fontWeight: 600, margin: "0 0 4px" }}>Close the loop</h1>
        <p style={{ color: T.muted, fontSize: 14, margin: "0 0 6px", maxWidth: 620 }}>
          Seed the calibration corpus by closing your own open receipts. Every close is human-supplied
          (§5.1) — nothing is inferred. Aim for a spread: both <span style={{ color: T.green }}>Landed</span>{" "}
          and <span style={{ color: T.red }}>Drifted</span> across render states beats a lopsided pile.
        </p>
        <p style={{ color: T.dimmed, fontSize: 12, margin: "0 0 20px", maxWidth: 620 }}>
          Note: you have no <span style={{ color: T.green }}>SHARP / green</span> open receipts, so this can’t
          test the high-conviction cell — that needs a few genuine high-conviction decisions created, then closed.
        </p>

        <div style={{ display: "flex", gap: 16, flexWrap: "wrap", padding: "10px 14px", background: T.surface, border: `1px solid ${T.border}`, borderRadius: 8, marginBottom: 24, fontSize: 13 }}>
          <span><strong style={{ color: T.cyan }}>{tally.total}</strong> closed this session</span>
          <span style={{ color: T.green }}>{tally.matched} landed</span>
          <span style={{ color: T.red }}>{tally.drifted} drifted</span>
          <span style={{ color: T.dimmed }}>
            {Object.entries(tally.byRender).map(([r, n]) => `${r} ${n}`).join(" · ") || "—"}
          </span>
          <span style={{ marginLeft: "auto", color: T.muted }}>{rows.length} open eligible</span>
        </div>

        {rows.length === 0 && <p style={{ color: T.muted }}>No open eligible receipts. All closed.</p>}

        {rows.map((r) => {
          const st = status[r.id]
          const d = draft(r.id)
          const done = st === "done"
          const saving = st === "saving"
          const err = st && typeof st === "object" ? st.error : null
          return (
            <div
              key={r.id}
              style={{
                background: T.surface, border: `1px solid ${done ? T.green : T.border}`,
                borderRadius: 10, padding: 16, marginBottom: 14, opacity: done ? 0.55 : 1,
                transition: "opacity 0.2s",
              }}
            >
              <div style={{ display: "flex", alignItems: "baseline", gap: 10, marginBottom: 8, flexWrap: "wrap" }}>
                <span style={{ fontSize: 11, fontWeight: 700, color: RENDER_COLOR[r.render] ?? T.dimmed, letterSpacing: "0.05em" }}>{r.render}</span>
                <span style={{ fontSize: 11, color: T.dimmed }}>NCI {r.nci}</span>
                <span style={{ fontSize: 11, color: T.dimmed }}>{r.createdAt}</span>
                {done && <span style={{ marginLeft: "auto", fontSize: 12, color: T.green, fontWeight: 600 }}>✓ closed</span>}
              </div>
              <div style={{ fontSize: 15, fontWeight: 500, marginBottom: r.trueNorth ? 4 : 12 }}>{r.question}</div>
              {r.trueNorth && <div style={{ fontSize: 13, color: T.muted, marginBottom: 12 }}>↳ {r.trueNorth}</div>}

              {!done && (
                <div style={{ display: "grid", gap: 12 }}>
                  <div style={{ display: "flex", gap: 10, alignItems: "center", flexWrap: "wrap" }}>
                    <div style={{ display: "flex", gap: 6 }}>
                      <button
                        type="button" onClick={() => set(r.id, { matched: true })}
                        style={{ ...pill, borderColor: d.matched === true ? T.green : T.border, color: d.matched === true ? T.green : T.dimmed, background: d.matched === true ? "rgba(0,255,157,0.08)" : "transparent" }}
                      >Landed</button>
                      <button
                        type="button" onClick={() => set(r.id, { matched: false })}
                        style={{ ...pill, borderColor: d.matched === false ? T.red : T.border, color: d.matched === false ? T.red : T.dimmed, background: d.matched === false ? "rgba(255,77,109,0.08)" : "transparent" }}
                      >Drifted</button>
                    </div>
                    <label style={{ display: "flex", alignItems: "center", gap: 6, marginLeft: "auto" }}>
                      <span style={label}>Regret</span>
                      <select value={d.regret} onChange={(e) => set(r.id, { regret: Number(e.target.value) })}
                        style={{ ...input, width: 64 }}>
                        {Array.from({ length: 11 }, (_, i) => <option key={i} value={i}>{i}</option>)}
                      </select>
                    </label>
                  </div>
                  <div>
                    <div style={{ ...label, marginBottom: 4 }}>What actually happened *</div>
                    <input value={d.what} onChange={(e) => set(r.id, { what: e.target.value })}
                      placeholder="one line — the real outcome" style={input} maxLength={2000} />
                  </div>
                  <div>
                    <div style={{ ...label, marginBottom: 4 }}>Learning (optional)</div>
                    <input value={d.learning} onChange={(e) => set(r.id, { learning: e.target.value })}
                      placeholder="what you'd tell past-you" style={input} maxLength={2000} />
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                    <button type="button" onClick={() => close(r.id)} disabled={saving}
                      style={{ ...cta, opacity: saving ? 0.6 : 1 }}>
                      {saving ? "Saving…" : "Close loop"}
                    </button>
                    {err && <span style={{ color: T.red, fontSize: 12 }}>{err}</span>}
                  </div>
                </div>
              )}
            </div>
          )
        })}
      </div>
    </main>
  )
}

const pill: React.CSSProperties = {
  border: "1px solid", borderRadius: 6, padding: "6px 12px", fontSize: 13,
  cursor: "pointer", fontFamily: "inherit", fontWeight: 600,
}
const cta: React.CSSProperties = {
  background: "#00F0FF", color: "#020408", border: "none", borderRadius: 6,
  padding: "8px 18px", fontSize: 13, fontWeight: 700, cursor: "pointer", fontFamily: "inherit",
}
