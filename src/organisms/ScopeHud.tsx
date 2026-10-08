"use client"

import { useEffect, useState } from "react"
import { text, signal, font } from "@/ui/tokens"

// The survey HUD: instruments laid over the field in full HUD mode.
// Brief: charting instrumentation for uncharted terrain. Map the topography,
// hold orientation, and steer the safest approach to the apex.
//
// Every reading is computed from the field's own geometry, never decorated:
// the terraces are a square ziggurat (Chebyshev rings), so the run across one
// terrace along bearing θ is STEP_W / max(|cos θ|, |sin θ|). The grade of an
// approach is atan(rise / run). Straight up a face is steepest; the diagonal
// ridgelines are the gentlest line. Slope bands follow avalanche practice:
// under 30° holds, 30 to 45° is the slab band, over 45° is a wall.

export type HudRead = { yaw: number; depth: number; fog: number; clear: boolean; nest: number; origin: { u: number; v: number } | null }
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
const band = (g: number) => (g < 30 ? { name: "HOLDS", color: signal.green } : g < 45 ? { name: "SLAB BAND", color: signal.gold } : { name: "WALL", color: signal.red })

const ink = "#9fb3c8"
const faint = "rgba(159,179,200,0.28)"
const panel: React.CSSProperties = {
  position: "absolute", background: "rgba(6,9,13,0.82)", border: "1px solid #1e293b", borderRadius: 4,
  boxShadow: "inset 0 1px 0 rgba(255,255,255,0.04), 0 8px 24px rgba(0,0,0,0.45)", padding: "10px 12px 12px", pointerEvents: "none",
}
const label: React.CSSProperties = { fontFamily: font.mono, ...font.tier.t2, textTransform: "uppercase", color: text.dimmed, whiteSpace: "nowrap" }
const value: React.CSSProperties = { fontFamily: font.mono, ...font.tier.t5, color: text.primary, fontVariantNumeric: "tabular-nums", whiteSpace: "nowrap" }

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

export function ScopeHud({ read, fathoms, stepH, stepW, levels, onSteer }: { read: () => HudRead; fathoms: readonly Fathom[]; stepH: number; stepW: number; levels: number; onSteer: (deg: number) => void }) {
  const [r, setR] = useState<HudRead>(read)
  useEffect(() => {
    let raf = 0, last = 0
    const tick = (now: number) => { if (now - last > 66) { last = now; setR(read()) } raf = requestAnimationFrame(tick) }
    raf = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(raf)
  }, [read])

  const hdg = norm(r.yaw * DEG)
  const grade = gradeAt(hdg, stepH, stepW)
  const b = band(grade)
  const safe = safeBearings(stepH, stepW)
  const delta = (x: number) => ((x - hdg + 540) % 360) - 180
  const nearest = safe.bearings.reduce((a, x) => (Math.abs(delta(x)) < Math.abs(delta(a)) ? x : a), safe.bearings[0])
  const turn = delta(nearest)
  const vis = Math.round((1 - r.fog) * 100)
  const deg3 = (x: number) => String(Math.round(norm(x)) % 360).padStart(3, "0")

  // Heading tape: ±60° window, tick every 5°, label every 15°, safe bearings marked.
  const TW = 520, span = 60
  const tx = (d: number) => TW / 2 + (delta(d) / span) * (TW / 2)
  const tape = []
  for (let d = Math.ceil((hdg - span) / 5) * 5; d <= hdg + span; d += 5) {
    const x = tx(d), big = norm(d) % 15 === 0
    tape.push(<line key={d} x1={x} y1={0} x2={x} y2={big ? 10 : 5} stroke={big ? ink : faint} />)
    if (big) tape.push(<text key={"t" + d} x={x} y={22} fill={text.dimmed} fontSize="9" fontFamily={font.mono} textAnchor="middle">{deg3(d)}</text>)
  }

  // Approach profile along the current bearing, edge to apex: rise vs run.
  const PW = 196, PH = 64, runPer = stepW / Math.max(Math.abs(Math.cos(hdg / DEG)), Math.abs(Math.sin(hdg / DEG)))
  const runMax = stepW * Math.SQRT2 * levels, sx = PW / runMax, sy = (PH - 8) / (stepH * levels * 1.2)
  let prof = `M0 ${PH}`
  for (let k = 0; k < levels; k++) prof += ` L${(k + 1) * runPer * sx} ${PH - (k + 1) * stepH * sy}`

  return (
    <div aria-hidden="true" style={{ position: "absolute", inset: 0, bottom: 38, pointerEvents: "none" }}>
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
        <div style={{ display: "flex", justifyContent: "space-between", gap: 12 }}><span style={label}>Visibility</span><span style={{ ...label, color: r.clear ? signal.green : signal.cyan }}>{r.clear ? "Clear" : "Fog"}</span></div>
        <Dial min={0} max={100} v={vis} minor={5} major={25} unit="%" />
        <div style={{ ...value, textAlign: "center" }}>{vis}%</div>
      </div>

      {/* Altimeter: the seven fathoms, continuous needle. */}
      <div style={{ ...panel, left: 16, top: 250, width: 192 }}>
        <Screws />
        <div style={{ display: "flex", justifyContent: "space-between", gap: 8 }}><span style={label}>Altimeter</span><span style={{ ...label, color: r.nest ? signal.gold : text.dimmed }}>Ø{r.nest}{r.nest ? ` · ×1e-${9 * r.nest}` : ""}</span></div>
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

      {/* Approach profile: the climb on this bearing, terrace by terrace. */}
      <div style={{ ...panel, right: 16, top: 250 }}>
        <Screws />
        <div style={{ display: "flex", justifyContent: "space-between", gap: 12 }}><span style={label}>Approach profile</span><span style={label}>{deg3(hdg)}°</span></div>
        <svg width={PW} height={PH + 4} viewBox={`0 -2 ${PW} ${PH + 4}`} style={{ display: "block", marginTop: 8 }}>
          {[0.25, 0.5, 0.75].map((y) => <line key={y} x1={0} x2={PW} y1={PH * y} y2={PH * y} stroke={faint} strokeDasharray="2 4" />)}
          <path d={prof} stroke={b.color} strokeWidth={1.5} fill="none" />
        </svg>
        <div style={{ display: "flex", justifyContent: "space-between", gap: 12, marginTop: 6 }}><span style={label}>Run / terrace</span><span style={value}>{(runPer * 1000).toFixed(0)} m</span></div>
      </div>

      {/* Heading tape with the safest bearings marked, and the steer cue. */}
      <div style={{ position: "absolute", left: "50%", bottom: 18, transform: "translateX(-50%)", width: TW, pointerEvents: "auto" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 6 }}>
          <span style={label}>Safe approach {safe.bearings.map(deg3).join(" · ")} · {safe.min.toFixed(1)}°</span>
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

      {/* Status strip. */}
      <div style={{ position: "absolute", left: 16, right: 16, top: 16, display: "flex", justifyContent: "flex-end", gap: 16, pointerEvents: "none" }}>
        {r.origin && <span style={{ ...label, color: signal.gold }}>Nest {r.nest} · origin {r.origin.u.toFixed(3)}, {r.origin.v.toFixed(3)}</span>}
        <span style={label}>Grade bands: &lt;30° holds · 30–45° slab · &gt;45° wall</span>
      </div>
    </div>
  )
}
