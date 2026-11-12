"use client"

import { useEffect, useMemo, useRef, useState } from "react"
import { text, signal, font, border, surface } from "@/ui/tokens"
import { type Flight, type Render, type P3, tierReads, facetsAt, nodeAt, edgeAt, nodePoints, terrace, project, facet, wrapDeg, mmss } from "./flight"

// HUD v2 flight (row hud-atlas-v2-flight, spec 4.5). One arcs.atlas.v2 file, read in this tab only.
// Space: drag (or the arrow keys, or the turn buttons) orbits the ziggurat a full 360 degrees.
// Time: the scrubber plays the call forward and back; only edges cut by then are drawn, so each
// terrace's fidelity grows and shrinks with history. Kairos: a gold ring where a belief moved,
// and a jump list beside the field. Earned: thin tiers render grain and print n; empty ones are flat.

const RENDER: Record<Render, string> = { SHARP: signal.green, DEGRADED: signal.gold, GRAIN: signal.steel, FLAT: signal.steel }
const GRADE = (L?: string) => (L === "A" || L === "B" ? signal.green : L === "C" ? signal.gold : signal.steel)
const W = 600, H = 460, CX = 300, CY = 330, SCALE = 200
const PLAY_SECONDS = 12

type Face = { z: number; pts: string; fill: string; stroke: string; dash?: string; grain?: boolean; op: number; key: string }

export function AtlasFlight({ flight: f, onClose }: { flight: Flight; onClose: () => void }) {
  const [yaw, setYaw] = useState(30)
  const [s, setS] = useState(f.maxS)
  const [dir, setDir] = useState<0 | 1 | -1>(0)
  const [pick, setPick] = useState<string | null>(null)
  const drag = useRef<number | null>(null)
  const closeBtn = useRef<HTMLButtonElement>(null)

  useEffect(() => { closeBtn.current?.focus() }, [])
  useEffect(() => {
    const k = (e: KeyboardEvent) => { if (e.key === "Escape") onClose() }
    window.addEventListener("keydown", k)
    return () => window.removeEventListener("keydown", k)
  }, [onClose])

  // Play forward or back at a pace that crosses the whole call in about PLAY_SECONDS.
  useEffect(() => {
    if (!dir || !f.maxS) return
    let raf = 0, last = performance.now()
    const step = (now: number) => {
      const ds = ((now - last) / 1000) * (f.maxS / PLAY_SECONDS) * dir
      last = now
      setS((cur) => {
        const nx = Math.min(f.maxS, Math.max(0, cur + ds))
        if (nx === 0 || nx === f.maxS) setDir(0)
        return nx
      })
      raf = requestAnimationFrame(step)
    }
    raf = requestAnimationFrame(step)
    return () => cancelAnimationFrame(raf)
  }, [dir, f.maxS])

  const pts = useMemo(() => nodePoints(f), [f])
  const reads = useMemo(() => tierReads(f, s), [f, s])
  const facets = facetsAt(f, s)
  const n = f.tiers.length
  const P = (p: P3) => project(p, yaw, SCALE, CX, CY)
  const poly = (ps: P3[]) => ps.map((p) => { const q = P(p); return `${q.x.toFixed(1)},${q.y.toFixed(1)}` }).join(" ")
  const depth = (ps: P3[]) => ps.reduce((a, p) => a + P(p).z, 0) / ps.length

  // Terraces painted base to apex (each sits inside the one below), flanks far to near, then the lid.
  // Facets go over the stone, far to near, so the proof of work is never hidden by a terrace.
  const faces: Face[] = []
  f.tiers.forEach((_, i) => {
    const { half: h, y, top } = terrace(i, n)
    const r = reads[i], c = RENDER[r.render], flat = r.render === "FLAT"
    const corner: [number, number][] = [[-h, -h], [h, -h], [h, h], [-h, h]]
    const sides: Face[] = []
    corner.forEach(([x0, z0], j) => {
      const [x1, z1] = corner[(j + 1) % 4]
      const side: P3[] = [[x0, y, z0], [x1, y, z1], [x1, top, z1], [x0, top, z0]]
      sides.push({ key: `s${i}${j}`, z: depth(side), pts: poly(side), fill: flat ? "none" : surface.panel, stroke: c, dash: flat ? "4 4" : undefined, op: 1 })
    })
    faces.push(...sides.sort((p, q) => p.z - q.z))
    const lid: P3[] = corner.map(([x, z]) => [x, top, z])
    faces.push({ key: `t${i}`, z: depth(lid) + 0.001, pts: poly(lid), fill: flat ? "none" : surface.elevated, stroke: c, dash: flat ? "4 4" : undefined, grain: r.render === "GRAIN", op: 1 })
  })
  const cuts: Face[] = []
  const tierOf = new Map(f.nodes.map((x) => [x.id, x.tier]))
  for (const e of f.edges) {
    const a = tierOf.get(e.from)!, b = tierOf.get(e.to)!
    if (a === b || !edgeAt(e, s)) continue
    const tri = facet(pts.get(e.from)!, pts.get(e.to)!, terrace(Math.min(a, b), n).half)
    const c = GRADE(e.grade?.letter)
    cuts.push({ key: e.id, z: depth(tri), pts: poly(tri), fill: c, stroke: c, op: 0.24 })
  }
  faces.push(...cuts.sort((x, y) => x.z - y.z))

  const live = f.nodes.filter((x) => nodeAt(x, s))
  const marks = f.kairos.filter((k) => k.s <= s)
  const near = (k: { id: string; s: number }) => pick === k.id || (s - k.s >= 0 && s - k.s < f.maxS / 40)
  const empty = !f.nodes.length && !f.edges.length

  const mono = { fontFamily: font.mono, fontSize: 12, letterSpacing: "0.04em" }
  const btn = { ...mono, minHeight: 44, minWidth: 44, padding: "6px 10px", borderRadius: 3, cursor: "pointer", color: text.primary, background: "rgba(2,5,10,0.85)", border: `1px solid ${border.subtle}` }
  const on = (b: boolean) => (b ? { background: "rgba(0,240,255,0.12)", border: `1px solid rgba(0,240,255,0.55)` } : {})
  const turn = (d: number) => setYaw((y) => wrapDeg(y + d))
  const jump = (id: string, at: number) => { setDir(0); setS(at); setPick(id) }

  return (
    <section role="dialog" aria-modal="true" aria-label={`Atlas flight: ${f.title}`}
      style={{ position: "fixed", inset: 0, zIndex: 1002, overflowY: "auto", background: "rgba(2,4,8,0.97)", color: text.primary, lineHeight: 1.4, textAlign: "left" }}>
      <div style={{ maxWidth: 1200, margin: "0 auto", padding: "16px 16px 32px" }}>
        <header style={{ display: "flex", flexWrap: "wrap", alignItems: "baseline", gap: "8px 16px", marginBottom: 12 }}>
          <h2 style={{ margin: 0, fontSize: font.ramp.headline, fontWeight: 500, flex: "1 1 auto", minWidth: 0, overflowWrap: "anywhere" }}>{f.title}</h2>
          <span style={{ ...mono, color: text.secondary }}>{`${facets} facets cut · ${mmss(s)} of ${mmss(f.maxS)} · yaw ${Math.round(yaw)}°`}</span>
          <button ref={closeBtn} type="button" onClick={onClose} style={btn}>Close</button>
        </header>

        <div style={{ display: "flex", flexWrap: "wrap", gap: 16, alignItems: "flex-start" }}>
          <div style={{ flex: "3 1 480px", minWidth: 0 }}>
            <svg viewBox={`0 0 ${W} ${H}`} role="img" tabIndex={0}
              aria-label={`Ziggurat of ${n} tiers at ${mmss(s)}: ${facets} facets, ${marks.length} kairos marks, orbit ${Math.round(yaw)} degrees. Drag or use the arrow keys to orbit.`}
              onPointerDown={(e) => { drag.current = e.clientX; (e.target as Element).setPointerCapture?.(e.pointerId) }}
              onPointerMove={(e) => { if (drag.current === null) return; turn((e.clientX - drag.current) * 0.6); drag.current = e.clientX }}
              onPointerUp={() => { drag.current = null }} onPointerCancel={() => { drag.current = null }}
              onKeyDown={(e) => { if (e.key === "ArrowLeft") { e.preventDefault(); turn(-15) } if (e.key === "ArrowRight") { e.preventDefault(); turn(15) } }}
              style={{ width: "100%", height: "auto", maxHeight: "72dvh", display: "block", touchAction: "none", cursor: "grab", borderRadius: 6, border: `1px solid ${border.subtle}`, background: surface.bg }}>
              <defs>
                <filter id="flight-grain" x="0" y="0" width="100%" height="100%">
                  <feTurbulence type="fractalNoise" baseFrequency="1.4" numOctaves="1" seed="7" />
                  <feColorMatrix values="0 0 0 0 0.58  0 0 0 0 0.64  0 0 0 0 0.72  0 0 0 0.55 0" />
                  <feComposite in2="SourceGraphic" operator="in" />
                </filter>
              </defs>
              {faces.map((q) => (
                <g key={q.key}>
                  <polygon points={q.pts} fill={q.fill} fillOpacity={q.op} stroke={q.stroke} strokeOpacity={q.op < 1 ? 0.85 : 1} strokeWidth={1.2} strokeDasharray={q.dash} strokeLinejoin="round" />
                  {q.grain && <polygon points={q.pts} fill="#fff" filter="url(#flight-grain)" />}
                </g>
              ))}
              {live.map((x) => { const q = P(pts.get(x.id)!); return <circle key={x.id} cx={q.x} cy={q.y} r={3.5} fill={RENDER[reads[x.tier].render]}><title>{`${x.label} (${x.t ?? "unanchored"})`}</title></circle> })}
              {marks.map((k) => {
                const q = P(pts.get(k.node)!), hot = near(k)
                return (
                  <g key={k.id}>
                    <circle cx={q.x} cy={q.y} r={hot ? 15 : 10} fill="none" stroke={signal.gold} strokeWidth={hot ? 3 : 2} />
                    <text x={q.x + 18} y={q.y + 4} fill={signal.gold} fontFamily={font.mono} fontSize={16}>{k.id}</text>
                  </g>
                )
              })}
              {empty && <text x={CX} y={44} textAnchor="middle" fill={text.primary} fontFamily={font.mono} fontSize={14}>Flat: no nodes, no evidenced edges (n = 0)</text>}
            </svg>

            <div role="group" aria-label="Time and orbit" style={{ display: "flex", flexWrap: "wrap", alignItems: "center", gap: 8, marginTop: 10 }}>
              <button type="button" aria-label="Play backward" aria-pressed={dir === -1} disabled={!f.maxS} onClick={() => { setPick(null); setDir(dir === -1 ? 0 : -1) }} style={{ ...btn, ...on(dir === -1) }}>{"◀"}</button>
              <button type="button" aria-label="Play forward" aria-pressed={dir === 1} disabled={!f.maxS} onClick={() => { setPick(null); if (s >= f.maxS) setS(0); setDir(dir === 1 ? 0 : 1) }} style={{ ...btn, ...on(dir === 1) }}>{"▶"}</button>
              <input type="range" min={0} max={f.maxS} step={1} value={Math.round(s)} aria-label="Time in the call" aria-valuetext={mmss(s)}
                onChange={(e) => { setDir(0); setPick(null); setS(Number(e.target.value)) }}
                style={{ flex: "1 1 160px", minWidth: 120, height: 44, accentColor: signal.cyan }} />
              <span style={{ ...mono, minWidth: 48 }}>{mmss(s)}</span>
              <button type="button" aria-label="Orbit left 15 degrees" onClick={() => turn(-15)} style={btn}>{"⟲"}</button>
              <button type="button" aria-label="Orbit right 15 degrees" onClick={() => turn(15)} style={btn}>{"⟳"}</button>
            </div>
          </div>

          <aside style={{ flex: "1 1 260px", minWidth: 0, display: "grid", gap: 16 }}>
            <div>
              <h3 style={{ ...mono, margin: "0 0 6px", textTransform: "uppercase", color: text.secondary, fontWeight: 400 }}>Kairos</h3>
              {f.kairos.length ? (
                <ol style={{ listStyle: "none", margin: 0, padding: 0, display: "grid", gap: 6 }}>
                  {f.kairos.map((k) => (
                    <li key={k.id}>
                      <button type="button" onClick={() => jump(k.id, k.s)} aria-current={pick === k.id ? "true" : undefined}
                        style={{ ...btn, ...on(pick === k.id), width: "100%", textAlign: "left", display: "grid", gap: 2, fontFamily: font.sans, fontSize: 14, letterSpacing: 0, lineHeight: 1.4 }}>
                        <span style={{ ...mono, color: signal.gold }}>{`${k.id} · ${k.t} · ${k.from ?? "?"} → ${k.to ?? "?"} · ${k.grade?.letter ?? "NS"}`}</span>
                        <span style={{ overflowWrap: "anywhere" }}>{k.what}</span>
                      </button>
                    </li>
                  ))}
                </ol>
              ) : <p style={{ margin: 0, fontSize: 14 }}>No kairos moments: no belief moved by the file&apos;s threshold.</p>}
            </div>

            <div>
              <h3 style={{ ...mono, margin: "0 0 6px", textTransform: "uppercase", color: text.secondary, fontWeight: 400 }}>{`Terraces at ${mmss(s)}`}</h3>
              <ul style={{ listStyle: "none", margin: 0, padding: 0 }}>
                {f.tiers.map((t, i) => ({ t, i })).reverse().map(({ t, i }) => {
                  const r = reads[i]
                  return (
                    <li key={i} style={{ ...mono, display: "flex", justifyContent: "space-between", gap: 8, padding: "6px 0", borderTop: `1px solid ${border.subtle}`, fontWeight: r.render === "SHARP" ? 500 : 300 }}>
                      <span>{`${t.name} · ${r.nodes} nodes`}</span>
                      <span style={{ color: RENDER[r.render] }}>{r.render === "GRAIN" || r.render === "FLAT" ? `${r.render} n = ${r.edges}` : `${r.render} · ${r.edges} edges`}</span>
                    </li>
                  )
                })}
              </ul>
            </div>

            {f.unanchored.length > 0 && (
              <div>
                <h3 style={{ ...mono, margin: "0 0 6px", textTransform: "uppercase", color: text.secondary, fontWeight: 400 }}>Unanchored</h3>
                <ul style={{ margin: 0, paddingLeft: 18, fontSize: 14, display: "grid", gap: 4 }}>
                  {f.unanchored.map((u, i) => <li key={i} style={{ overflowWrap: "anywhere" }}>{u}</li>)}
                </ul>
              </div>
            )}
          </aside>
        </div>
      </div>
    </section>
  )
}
