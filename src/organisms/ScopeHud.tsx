"use client"

import { useCallback, useEffect, useState } from "react"
import { text, signal, font } from "@/ui/tokens"
import universe from "@/data/universe-field.json"

// The survey HUD: instruments laid over the field in full HUD mode.
// Brief: charting instrumentation for uncharted terrain. Map the topography,
// hold orientation, and steer the safest approach to the apex.
//
// Every reading is computed from the field's own geometry, never decorated:
// the terraces are a square ziggurat (Chebyshev rings), so the run across one
// terrace along bearing θ is STEP_W / max(|cos θ|, |sin θ|). The grade of an
// approach is atan(rise / run). Straight up a face is steepest; the diagonal
// ridgelines are the gentlest line. Slope bands follow avalanche practice:
// under 30° is stable, 30 to 45° is the slab band, over 45° is a wall.

type UNode = (typeof universe.nodes)[number]
export type HudRead = { yaw: number; depth: number; fog: number; clear: boolean; nest: number; origin: { u: number; v: number } | null; universe: boolean; node: UNode | null; trail: string[]; holds: Hold[]; bankUp: Hold | null; bankDown: Hold | null
  galaxy: UNode | null
  gps: { here: string; at: string; look: string | null; leg: { from: string; verb: string; to: string } | null } | null }
type Hold = { id: string; label: string; state: "open" | "blocked" | "obscured" }
type Fathom = { n: number; name: string; altitude: string; resolution: string }

const DEG = 180 / Math.PI
const norm = (d: number) => ((d % 360) + 360) % 360
export function gradeAt(bearingDeg: number, stepH: number, stepW: number) {
  const t = bearingDeg / DEG
  const m = Math.max(Math.abs(Math.cos(t)), Math.abs(Math.sin(t)))
  return Math.atan((stepH * m) / stepW) * DEG
}
// The safest approach: scan every bearing, keep the gentlest grade.
function safeBearings(stepH: number, stepW: number) {
  let min = Infinity
  const g: number[] = []
  for (let b = 0; b < 360; b++) { const v = gradeAt(b, stepH, stepW); g.push(v); if (v < min) min = v }
  return { min, bearings: g.flatMap((v, b) => (v - min < 1e-6 ? [b] : [])) }
}
const band = (g: number) => (g < 30 ? { name: "STABLE", color: signal.green } : g < 45 ? { name: "SLAB BAND", color: signal.gold } : { name: "WALL", color: signal.red })

const ink = "#9fb3c8"
const faint = "rgba(159,179,200,0.28)"
const panel: React.CSSProperties = {
  position: "absolute", background: "rgba(6,9,13,0.82)", border: "1px solid #1e293b", borderRadius: 4,
  boxShadow: "inset 0 1px 0 rgba(255,255,255,0.04)", padding: "10px 12px 12px", pointerEvents: "none",
}
const label: React.CSSProperties = { fontFamily: font.mono, ...font.tier.t2, textTransform: "uppercase", color: text.dimmed, whiteSpace: "nowrap" }
// Names keep their own case: lattice labels carry math and Greek that uppercase mangles.
const name: React.CSSProperties = { textTransform: "none", letterSpacing: "0.02em", fontWeight: 600 }
const scroll: React.CSSProperties = { overflowY: "auto", scrollbarWidth: "thin", scrollbarColor: "#1e293b transparent" }
const value: React.CSSProperties = { fontFamily: font.mono, ...font.tier.t5, color: text.primary, fontVariantNumeric: "tabular-nums", whiteSpace: "nowrap" }

// A node's signature: altitude (stratum), resonance (domain mix of its lattice neighbours, one
// bar per domain), frequency (commits on its files). No signal when a node has no mapped files.
const DOM_COLOR: Record<string, string> = { ont: signal.green, epi: signal.cyan, met: signal.gold, ety: "#94a3b8", lib: "#e2e8f0" }
function Signature({ n }: { n: UNode }) {
  const f = n.sig.frequency
  const mix = Object.entries(n.sig.resonance as Record<string, number>)
  const strata = universe.federation.strata as Record<string, string>
  const cell = (k: string, v: React.ReactNode) => (
    <div style={{ display: "flex", justifyContent: "space-between", gap: 12, padding: "3px 0", borderTop: `1px solid ${faint}` }}><span style={label}>{k}</span><span style={{ ...label, color: text.primary }}>{v}</span></div>)
  return (
    <>
      {cell("Altitude", strata[n.sig.altitude] ?? n.sig.altitude)}
      {cell("Resonance", mix.length ? (
        <span style={{ display: "inline-flex", width: 96, height: 6, background: "#0b1016", borderRadius: 1, overflow: "hidden" }} title={mix.map(([k, v]) => `${k} ${Math.round(v * 100)}%`).join(" · ")}>
          {mix.map(([k, v]) => <span key={k} style={{ width: `${v * 100}%`, background: DOM_COLOR[k] }} />)}
        </span>) : "No signal")}
      {cell("Frequency", f.last_change ? `${f.last_28d} / 28d · ${f.last_change}` : "No signal")}
    </>
  )
}

// Four machined screw heads, one per corner.
function Screws() {
  const s = (x: string, y: string): React.CSSProperties => ({ position: "absolute", [x]: 4, [y]: 4, width: 5, height: 5, borderRadius: "50%", background: "#151b23", boxShadow: "inset 0 0 0 1px #2a3442" } as React.CSSProperties)
  return <>{(["left", "right"] as const).flatMap((x) => (["top", "bottom"] as const).map((y) => <span key={x + y} style={s(x, y)} />))}</>
}

// A half dial: 180° sweep, ticks every `minor`, labels every `major`, optional colored bands.
function Dial({ min, max, v, minor, major, bands = [], unit }: { min: number; max: number; v: number; minor: number; major: number; bands?: { from: number; to: number; color: string }[]; unit: string }) {
  const W = 168, R = 66, cx = W / 2, cy = 76
  const ang = (x: number) => Math.PI * (1 - (Math.min(max, Math.max(min, x)) - min) / (max - min))
  const pt = (x: number, r: number) => [cx + r * Math.cos(ang(x)), cy - r * Math.sin(ang(x))]
  const arc = (a: number, b: number, r: number) => { const [x1, y1] = pt(a, r), [x2, y2] = pt(b, r); return `M${x1} ${y1} A${r} ${r} 0 0 1 ${x2} ${y2}` }
  const ticks = []
  for (let x = min; x <= max + 1e-9; x += minor) {
    const big = Math.abs(((x - min) / major) - Math.round((x - min) / major)) < 1e-6
    const [a1, b1] = pt(x, R), [a2, b2] = pt(x, R - (big ? 8 : 4))
    ticks.push(<line key={x} x1={a1} y1={b1} x2={a2} y2={b2} stroke={big ? ink : faint} strokeWidth={big ? 1.2 : 1} />)
    if (big) { const [lx, ly] = pt(x, R - 17); ticks.push(<text key={"l" + x} x={lx} y={ly + 3} fill={text.dimmed} fontSize="8.5" fontFamily={font.mono} textAnchor="middle">{x}</text>) }
  }
  const [nx, ny] = pt(v, R - 4)
  return (
    <svg width={W} height={88} viewBox={`0 0 ${W} 88`} aria-hidden="true" style={{ display: "block" }}>
      {bands.map((b, i) => <path key={i} d={arc(b.from, b.to, R + 4)} stroke={b.color} strokeOpacity={0.7} strokeWidth={2.5} fill="none" />)}
      <path d={arc(min, max, R)} stroke={faint} fill="none" />
      {ticks}
      <line x1={cx} y1={cy} x2={nx} y2={ny} stroke={signal.cyan} strokeWidth={1.6} strokeLinecap="round" />
      <circle cx={cx} cy={cy} r={4} fill="#0b1016" stroke={ink} />
      <text x={cx} y={cy + 11} fill={text.dimmed} fontSize="8" fontFamily={font.mono} textAnchor="middle">{unit}</text>
    </svg>
  )
}

export function ScopeHud({ read, fathoms, stepH, stepW, onSteer, onBack, onHop, onBank }: { read: () => HudRead; onBack: (i: number) => void; onHop: (id: string) => void; onBank: (dir: 1 | -1) => void; fathoms: readonly Fathom[]; stepH: number; stepW: number; onSteer: (deg: number) => void }) {
  // Defaults keep the HUD whole if a reader omits a field (a hot reload can pair a new HUD with an old reader).
  const safeRead = useCallback((): HudRead => ({ yaw: 0, depth: 4, fog: 1, clear: false, nest: 0, origin: null, universe: false, node: null, trail: [], holds: [], bankUp: null, bankDown: null, galaxy: null, gps: null, ...(read() as Partial<HudRead>) }), [read])
  const [r, setR] = useState<HudRead>(safeRead)
  const [vw, setVw] = useState(() => (typeof window === "undefined" ? 1280 : window.innerWidth))
  useEffect(() => { const on = () => setVw(window.innerWidth); window.addEventListener("resize", on); return () => window.removeEventListener("resize", on) }, [])
  const narrow = vw < 760
  useEffect(() => {
    let raf = 0, last = 0
    const tick = (now: number) => { if (now - last > 66) { last = now; setR(safeRead()) } raf = requestAnimationFrame(tick) }
    raf = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(raf)
  }, [safeRead])

  const hdg = norm(r.yaw * DEG)
  const grade = gradeAt(hdg, stepH, stepW)
  const b = band(grade)
  const safe = safeBearings(stepH, stepW)
  const delta = (x: number) => ((x - hdg + 540) % 360) - 180
  const nearest = safe.bearings.reduce((a, x) => (Math.abs(delta(x)) < Math.abs(delta(a)) ? x : a), safe.bearings[0])
  const turn = delta(nearest)
  const vis = Math.round((1 - r.fog) * 100)
  const visState = vis >= 70 ? { name: "Clear", color: signal.green } : vis >= 30 ? { name: "Thinning", color: signal.cyan } : { name: "Fog", color: text.dimmed }
  const deg3 = (x: number) => String(Math.round(norm(x)) % 360).padStart(3, "0")

  // Heading tape: ±60° window, tick every 5°, label every 15°, safe bearings marked.
  // The tape takes the lane between the side columns, never more than 520px.
  const TW = narrow ? vw - 32 : Math.max(280, Math.min(520, vw - 520)), span = 60
  const tx = (d: number) => TW / 2 + (delta(d) / span) * (TW / 2)
  const tape = []
  for (let d = Math.ceil((hdg - span) / 5) * 5; d <= hdg + span; d += 5) {
    const x = tx(d), big = norm(d) % 15 === 0
    tape.push(<line key={d} x1={x} y1={0} x2={x} y2={big ? 10 : 5} stroke={big ? ink : faint} />)
    if (big) tape.push(<text key={"t" + d} x={x} y={22} fill={text.dimmed} fontSize="9" fontFamily={font.mono} textAnchor="middle">{deg3(d)}</text>)
  }


  return (
    <div aria-hidden="true" style={{ position: "absolute", inset: 0, bottom: 38, pointerEvents: "none" }}>
      {/* Phone: one readout strip carries slope, visibility and depth; the dials need room. */}
      {narrow && (
        <div style={{ ...panel, left: 16, right: 16, top: 16, display: "flex", justifyContent: "space-between", gap: 10, padding: "8px 12px" }}>
          <Screws />
          <span style={label}>Slope <span style={{ ...value, color: b.color }}>{grade.toFixed(0)}°</span></span>
          <span style={label}>Vis <span style={{ ...value, color: visState.color }}>{vis}%</span></span>
          <span style={label}>F{Math.round(r.depth)} <span style={value}>{fathoms[Math.max(0, Math.min(fathoms.length - 1, Math.round(r.depth) - 1))].altitude}</span></span>
        </div>
      )}
      {!narrow && (<>
      {/* Slope: the grade of the line you are facing. */}
      <div style={{ ...panel, left: 16, top: 64 }}>
        <Screws />
        <div style={{ display: "flex", justifyContent: "space-between", gap: 12 }}><span style={label}>Slope · on heading</span><span style={{ ...label, color: b.color }}>{b.name}</span></div>
        <Dial min={0} max={60} v={grade} minor={2.5} major={10} unit="DEG" bands={[{ from: 0, to: 30, color: signal.green }, { from: 30, to: 45, color: signal.gold }, { from: 45, to: 60, color: signal.red }]} />
        <div style={{ ...value, textAlign: "center" }}>{grade.toFixed(1)}°</div>
      </div>

      {/* Visibility: how much of the field returns through the fog. */}
      <div style={{ ...panel, right: 16, top: 64 }}>
        <Screws />
        <div style={{ display: "flex", justifyContent: "space-between", gap: 12 }}><span style={label}>Visibility</span><span style={{ ...label, color: visState.color }}>{visState.name}</span></div>
        <Dial min={0} max={100} v={vis} minor={5} major={25} unit="%" />
        <div style={{ ...value, textAlign: "center" }}>{vis}%</div>
      </div>

      {/* Altimeter: the seven fathoms, continuous needle. */}
      <div style={{ ...panel, left: 16, top: 250, width: 192 }}>
        <Screws />
        <div style={{ display: "flex", justifyContent: "space-between", gap: 8 }}><span style={label}>Altimeter</span><span style={{ ...label, color: r.nest ? signal.gold : text.dimmed }}>Nest {r.nest}</span></div>
        <div style={{ position: "relative", marginTop: 8 }}>
          {fathoms.map((x) => (
            <div key={x.n} style={{ display: "flex", justifyContent: "space-between", gap: 8, padding: "3px 0 3px 14px", borderTop: `1px solid ${faint}` }}>
              <span style={{ ...label, color: Math.round(r.depth) === x.n ? text.primary : text.dimmed }}>F{x.n} {x.altitude}</span>
              <span style={{ ...label, color: Math.round(r.depth) === x.n ? signal.cyan : text.dimmed }}>{x.resolution}</span>
            </div>
          ))}
          <span style={{ position: "absolute", left: 0, top: `calc(${((r.depth - 1) / (fathoms.length - 1)) * 80}% + 4px)`, width: 0, height: 0, borderTop: "5px solid transparent", borderBottom: "5px solid transparent", borderLeft: `7px solid ${signal.cyan}` }} />
        </div>
      </div>

      </>)}

      {/* Heading tape with the safest bearings marked, and the steer cue. */}
      <div style={{ position: "absolute", left: "50%", bottom: 18, transform: "translateX(-50%)", width: TW + 24, padding: "8px 12px 6px", background: "rgba(6,9,13,0.82)", border: "1px solid #1e293b", borderRadius: 4, pointerEvents: "auto" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 6 }}>
          <span style={{ ...label, whiteSpace: "normal" }}>{narrow ? "Safe" : "Safe approach"} {safe.bearings.map(deg3).join(" · ")}{narrow ? "" : ` · ${safe.min.toFixed(1)}°`}</span>
          <button
            type="button"
            onClick={() => onSteer(nearest)}
            title="Steer to the nearest safe bearing (S)"
            style={{ ...label, color: Math.abs(turn) < 1 ? signal.green : signal.cyan, background: "rgba(6,9,13,0.82)", border: `1px solid ${Math.abs(turn) < 1 ? signal.green : "rgba(0,240,255,0.5)"}`, borderRadius: 3, padding: "4px 8px", cursor: "pointer" }}
          >
            {Math.abs(turn) < 1 ? "On safe line" : `Steer ${turn > 0 ? "right" : "left"} ${Math.abs(Math.round(turn))}° · S`}
          </button>
        </div>
        <svg width={TW} height={30} viewBox={`0 0 ${TW} 30`} style={{ display: "block", background: "rgba(6,9,13,0.7)", borderTop: `1px solid ${faint}` }}>
          {safe.bearings.filter((x) => Math.abs(delta(x)) <= span).map((x) => <rect key={x} x={tx(x) - 4} y={0} width={8} height={30} fill={signal.green} opacity={0.18} />)}
          {tape}
          <path d={`M${TW / 2 - 5} 0 L${TW / 2 + 5} 0 L${TW / 2} 7 Z`} fill={signal.cyan} />
        </svg>
        <div style={{ ...value, textAlign: "center", marginTop: 4 }}>HDG {deg3(hdg)}°</div>
      </div>

      {/* The universe: eight dimensions from the snapshot, and the node you dove into. */}
      {r.universe && !narrow && (() => {
        const d = universe.dimensions
        const row = (k: string, v: string, c: string = text.primary) => (
          <div key={k} style={{ display: "flex", justifyContent: "space-between", gap: 12, padding: "3px 0", borderTop: `1px solid ${faint}` }}><span style={label}>{k}</span><span style={{ ...label, color: c }}>{v}</span></div>)
        return (
          <div style={{ ...panel, right: 16, top: 250, width: 248, maxHeight: "calc(100% - 350px)", ...scroll, overflowX: "hidden", pointerEvents: "auto" }}>
            <Screws />
            <div style={{ display: "flex", justifyContent: "space-between", gap: 8, marginBottom: 6 }}><span style={label}>Universe</span><span style={label}>lattice {universe.lattice_reviewed}</span></div>
            {r.galaxy && (
              <div style={{ marginBottom: 8, paddingBottom: 6, borderBottom: `1px solid ${signal.gold}66` }}>
                <div style={{ ...label, color: signal.gold, whiteSpace: "normal", marginBottom: 4 }}>Inside galaxy · {r.galaxy.label}</div>
                {Object.entries(r.galaxy.systems ?? {}).map(([k, v]) => row(k, `${v} files`))}
              </div>
            )}
            {row("Corpus", `${d.corpus} files`)}
            {row("Canon", `${d.canon.files} · ${d.canon.tao_proverbs} tao · ${d.canon.adrs} ADR`)}
            {row("Codebase", `${d.codebase} files`)}
            {row("Conviction", "No signal", text.dimmed)}
            {row("Clarity", `${d.clarity.nodes_clear}/${d.clarity.nodes} clear · ${d.clarity.files_fog} fog`, signal.cyan)}
            {row("Coherence", `${d.coherence.diamonds} diamonds · h ${d.coherence.mean_hardness}`, signal.gold)}
            {row("Cohesion", `${Math.round(d.cohesion.ratio * 100)}% cross-domain`)}
            {row("Consonance", `${d.consonance.empirical} empirical of ${d.consonance.tautology + d.consonance.constitutional + d.consonance.empirical}`)}
            {r.node && (
              <div style={{ marginTop: 8, paddingTop: 6, borderTop: `1px solid ${signal.gold}66` }}>
                <div style={{ ...label, color: signal.gold, whiteSpace: "normal" }}>Ø{r.nest} · {r.node.label}</div>
                {row("Stratum · domain", `${universe.federation.strata[r.node.stratum as keyof typeof universe.federation.strata]} · ${universe.federation.domains[r.node.domain as keyof typeof universe.federation.domains]}`)}
                {row("Status", r.node.status + (r.node.invariant ? ` · ${r.node.invariant}` : ""), r.node.status === "ok" ? signal.green : signal.gold)}
                {row("Hardness", `${r.node.hardness}${r.node.diamond ? " · diamond" : ""}`)}
                {row("Open shore", String(r.node.shore_open))}
                {row("Mapped files", String(r.node.files))}
                <Signature n={r.node} />
              </div>
            )}
          </div>
        )
      })()}

      {/* GPS: where you are, what you face, the last leg, and the breadcrumbs to back-track. */}
      {r.universe && r.gps && (
        <div style={{ ...panel, left: narrow ? 16 : "50%", right: narrow ? 16 : undefined, top: narrow ? 64 : 16, transform: narrow ? undefined : "translateX(-50%)", width: narrow ? undefined : Math.max(300, Math.min(560, vw - 560)), pointerEvents: "auto" }}>
          <Screws />
          <div style={{ display: "grid", gridTemplateColumns: "auto 1fr", columnGap: 10, rowGap: 3, alignItems: "baseline" }}>
            <span style={label}>You are at</span>
            <span style={{ ...value, whiteSpace: "normal", color: signal.gold }}>{r.gps.here}{r.gps.at && <span style={{ ...label, marginLeft: 8 }}>{r.gps.at}</span>}</span>
            <span style={label}>Looking at</span>
            <span style={{ ...value, whiteSpace: "normal" }}>{r.gps.look ?? (r.galaxy ? `the systems inside ${r.galaxy.label}` : "your own vantage")}</span>
            <span style={label}>Last leg</span>
            <span style={{ ...value, whiteSpace: "normal", fontWeight: 500 }}>{r.gps.leg ? <>{r.gps.leg.from} <span style={{ color: text.dimmed }}>{r.gps.leg.verb}</span> {r.gps.leg.to}</> : <span style={{ color: text.dimmed }}>none yet: hop, bank or double-click to dive</span>}</span>
          </div>
          {r.trail.length > 0 && (
            <nav aria-label="Vantage trail" style={{ display: "flex", alignItems: "center", gap: 6, flexWrap: "wrap", marginTop: 8, paddingTop: 8, borderTop: `1px solid ${faint}` }}>
              {["origin · Zero-point", ...r.trail].map((name, i) => {
            const here = i === r.trail.length
            return (
              <span key={i} style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
                {i > 0 && <span style={{ ...label, color: text.dimmed }}>›</span>}
                <button
                  type="button"
                  disabled={here}
                  onClick={() => onBack(i)}
                  title={here ? "You are here" : `Back-track to step ${i}`}
                  style={{ ...label, color: here ? signal.gold : text.secondary, background: "rgba(6,9,13,0.82)", border: `1px solid ${here ? signal.gold : "#1e293b"}`, borderRadius: 3, padding: "3px 7px", cursor: here ? "default" : "pointer" }}
                >
                  {i} · {name}
                </button>
              </span>
            )
          })}
            </nav>
          )}
        </div>
      )}

      {/* Holds: every node one edge away, and whether you can hop to it. */}
      {r.universe && (r.holds.length > 0 || r.bankUp || r.bankDown) && (
        <div style={{ ...panel, ...(narrow ? { left: 16, right: 16, bottom: 110, maxHeight: "32%" } : { left: 16, top: 460, width: 228, maxHeight: "calc(100% - 560px)" }), ...scroll, pointerEvents: "auto" }}>
          <Screws />
          <div style={{ display: "flex", justifyContent: "space-between", gap: 8, marginBottom: 6 }}><span style={label}>Holds</span><span style={label}>{r.holds.filter((h) => h.state === "open").length}/{r.holds.length} open</span></div>
          {([[1, r.bankUp], [-1, r.bankDown]] as const).map(([dir, b]) => b && (
            <button
              key={dir}
              type="button"
              disabled={b.state !== "open"}
              onClick={() => onBank(dir)}
              title={b.state === "open" ? `Bank ${dir > 0 ? "up" : "down"} one ring to ${b.label} (Shift ${dir > 0 ? "up" : "down"})` : `Bank ${b.state}`}
              style={{ ...label, display: "flex", justifyContent: "space-between", gap: 8, width: "100%", textAlign: "left", whiteSpace: "normal", background: "none", border: "none", borderTop: `1px solid ${faint}`, padding: "4px 0", cursor: b.state === "open" ? "pointer" : "default", color: b.state === "open" ? text.primary : text.dimmed }}
            >
              <span><span style={{ color: dir > 0 ? signal.gold : signal.cyan }}>{dir > 0 ? "Bank up" : "Bank down"}</span> · <span style={name}>{b.label}</span></span>
              <span style={{ color: b.state === "open" ? signal.green : b.state === "blocked" ? signal.red : text.dimmed, flexShrink: 0 }}>{b.state}</span>
            </button>
          ))}
          {r.holds.filter((h) => h.state === "open").map((h) => (
            <button
              key={h.id}
              type="button"
              disabled={h.state !== "open"}
              onClick={() => onHop(h.id)}
              title={h.state === "open" ? `Hop to ${h.label}` : h.state === "blocked" ? "Blocked: this node is gated" : "Obscured: open questions, visibility under 50%"}
              style={{ ...label, display: "flex", justifyContent: "space-between", gap: 8, width: "100%", textAlign: "left", whiteSpace: "normal", background: "none", border: "none", borderTop: `1px solid ${faint}`, padding: "4px 0", cursor: h.state === "open" ? "pointer" : "default", color: h.state === "open" ? text.primary : text.dimmed }}
            >
              <span style={name}>{h.label}</span>
              <span style={{ color: h.state === "open" ? signal.green : h.state === "blocked" ? signal.red : text.dimmed, flexShrink: 0 }}>{h.state}</span>
            </button>
          ))}
          {(() => {
            const shut = r.holds.filter((h) => h.state !== "open")
            if (!shut.length) return null
            const ob = shut.filter((h) => h.state === "obscured").length, bl = shut.length - ob
            return (
              <div title={shut.map((h) => `${h.label} (${h.state})`).join("\n")} style={{ ...label, borderTop: `1px solid ${faint}`, padding: "4px 0", whiteSpace: "normal" }}>
                {[ob && `${ob} obscured by fog`, bl && `${bl} blocked by a gate`].filter(Boolean).join(" · ")}
              </div>
            )
          })()}
        </div>
      )}

    </div>
  )
}
