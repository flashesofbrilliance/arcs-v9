"use client"

import { useCallback, useEffect, useRef, useState } from "react"
import { text, signal, font, border } from "@/ui/tokens"

// The field. A sketch of ARCS as terrain: a lidar point cloud of the atlas
// ziggurat (runtime/warroom/terrain-atlas.html, form only), with the product
// laid on its terraces as overlays. Lower terraces are Now, upper are Next,
// the apex is Later. It is a concept map, framed as one.
//
// The blue point is you, one vantage at one moment. Fog is atmospheric:
// returns scatter and drop out in it, it thins as the visitor leans in
// (`fog`), and it clears when the server has written their row (`clear`),
// which walks the navigator to the apex and lays a bearing to true north.
//
// Every waypoint on the field is a droplet: it sends rings across the ground,
// and where two droplets' rings cross they interfere. That moiré is the only
// texture. Adding an overlay drops a fresh, stronger droplet.
//
// Camera is free: drag to orbit and tilt (beneath to overhead), shift-drag to
// pan, Cmd/Ctrl-scroll or pinch to zoom, Option-scroll to dolly, double-click
// or 0 to reset. Plain scroll always belongs to the page.

const S = 400
const TAU = Math.PI * 2
const GRID = 46
const SUMMIT = { u: 0.06, v: -0.04 }
const START = { u: -0.78, v: 0.7 }
const ORBIT_MS = 90_000
const H = 1.0
const HALF = 0.84
const LEVELS = 5
const STEP_W = HALF / LEVELS
const STEP_H = 0.12
const PITCH_MIN = -1.45, PITCH_MAX = 1.52
const DIST_MIN = 1.25, DIST_MAX = 7
const RIPPLE_GAP = 0.05, RIPPLE_REACH = 0.62, RIPPLE_SPEED = 0.045 // world units, per second

export type Tier = "now" | "next" | "later"
export const WAYPOINTS: { id: string; label: string; note: string; tier: Tier; k: number; a: number }[] = [
  { id: "compass", label: "Compass", note: "Ask the real question, get one bearing", tier: "now", k: 1, a: 3.6 },
  { id: "receipt", label: "Receipt", note: "A decision frozen in time", tier: "now", k: 1, a: 0.9 },
  { id: "debrief", label: "Debrief", note: "Log what actually happened against the call", tier: "now", k: 1, a: 5.4 },
  { id: "prep", label: "Prep", note: "Two minutes of calibration first", tier: "now", k: 2, a: 5.2 },
  { id: "brief", label: "Brief", note: "The full map of one decision", tier: "now", k: 2, a: 2.2 },
  { id: "history", label: "History", note: "Every bearing you have taken", tier: "now", k: 2, a: 4.1 },
  { id: "calibration", label: "Calibration", note: "Learn from outcomes how well past calls held", tier: "next", k: 3, a: 1.4 },
  { id: "observatory", label: "Observatory", note: "Replay any decision, scrub to any point", tier: "next", k: 3, a: 4.6 },
  { id: "tributaries", label: "Deeper tributaries", note: "More of the questions beneath the question", tier: "next", k: 4, a: 3.0 },
  { id: "kairos", label: "Kairos", note: "Knowing when, not only what", tier: "later", k: 5, a: 2.4 },
  { id: "governance", label: "L6 to L7", note: "Ecosystem and governance layers", tier: "later", k: 5, a: 5.6 },
]
const TIER_COLOR: Record<Tier, string> = { now: signal.green, next: signal.cyan, later: "#94a3b8" }
const TIER_NAME: Record<Tier, string> = { now: "Now", next: "Next", later: "Later" }
const DEFAULT_ON = WAYPOINTS.filter((w) => w.tier === "now").map((w) => w.id)

function stratumAt(u: number, v: number) {
  const d = Math.max(Math.abs(u - SUMMIT.u), Math.abs(v - SUMMIT.v))
  if (d > HALF) return { k: 0, frac: 0 }
  const t = (HALF - d) / STEP_W
  return { k: Math.min(LEVELS, Math.floor(t) + 1), frac: t - Math.floor(t) }
}
function height(u: number, v: number) {
  const { k } = stratumAt(u, v)
  return k * STEP_H + 0.025 * Math.sin(5 * u + 1) * Math.cos(4 * v) * (k === 0 ? 1 : 0.15)
}
function terracePoint(k: number, a: number) {
  const d = HALF - (k - (k === LEVELS ? 0.15 : 0.5)) * STEP_W
  const c = Math.cos(a), s = Math.sin(a), m = Math.max(Math.abs(c), Math.abs(s))
  return { u: SUMMIT.u + (d * c) / m, v: SUMMIT.v + (d * s) / m }
}

function mulberry32(a: number) {
  return () => {
    a |= 0; a = (a + 0x6d2b79f5) | 0
    let t = Math.imul(a ^ (a >>> 15), 1 | a)
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}

type Pt = { u: number; v: number; h: number; k: number; edge: number; wall: boolean; jy: number; ju: number; jv: number; keep: number }

function buildCloud(): Pt[] {
  const rnd = mulberry32(173)
  const pts: Pt[] = []
  const jit = () => ({ jy: rnd() * 2 - 1, ju: rnd() * 2 - 1, jv: rnd() * 2 - 1, keep: rnd() })
  for (let i = 0; i < GRID; i++) {
    for (let j = 0; j < GRID; j++) {
      const u = -1 + (2 * (i + 0.5 + (rnd() - 0.5) * 0.35)) / GRID
      const v = -1 + (2 * (j + 0.5 + (rnd() - 0.5) * 0.35)) / GRID
      if (u * u + v * v > 1.05) continue
      const { k, frac } = stratumAt(u, v)
      pts.push({ u, v, h: height(u, v), k, edge: k > 0 && frac < 0.16 ? 1 : 0, wall: false, ...jit() })
    }
  }
  for (let k = 1; k <= LEVELS; k++) {
    const d = HALF - (k - 1) * STEP_W
    const n = Math.round((8 * d) / 0.045)
    for (let i = 0; i < n; i++) {
      const p = (i / n) * 8 * d
      const side = Math.floor(p / (2 * d)), o = (p % (2 * d)) - d
      const u = SUMMIT.u + (side === 0 ? o : side === 1 ? d : side === 2 ? -o : -d)
      const v = SUMMIT.v + (side === 0 ? -d : side === 1 ? o : side === 2 ? d : -o)
      for (let r = 0; r < 2; r++) pts.push({ u, v, h: (k - 1) * STEP_H + ((r + 0.5) / 2) * STEP_H, k, edge: 0.6, wall: true, ...jit() })
    }
  }
  return pts
}

function rgba(hex: string, a: number) {
  const n = parseInt(hex.slice(1), 16)
  return `rgba(${(n >> 16) & 255},${(n >> 8) & 255},${n & 255},${Math.max(0, Math.min(1, a)).toFixed(3)})`
}
function mix(a: string, b: string, t: number) {
  const pa = parseInt(a.slice(1), 16), pb = parseInt(b.slice(1), 16)
  const ch = (s: number) => Math.round(((pa >> s) & 255) * (1 - t) + ((pb >> s) & 255) * t)
  return `#${((ch(16) << 16) | (ch(8) << 8) | ch(0)).toString(16).padStart(6, "0")}`
}
const pad = (n: number, w: number) => String(Math.round(Math.abs(n))).padStart(w, "0")
const clamp = (x: number, a: number, b: number) => Math.max(a, Math.min(b, x))

type Cam = { yaw: number; pitch: number; zoom: number; dist: number; pu: number; pv: number }
const HOME_CAM: Cam = { yaw: 0.6, pitch: 0.66, zoom: 1, dist: 2.7, pu: 0, pv: 0 }

export function Scope({ fog, clear, zone, zoneColor }: { fog: number; clear: boolean; zone: string; zoneColor: string }) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const wrapRef = useRef<HTMLDivElement>(null)
  const target = useRef({ fog, clear })
  const tgt = useRef<Cam>({ ...HOME_CAM })
  const control = useRef({
    pausedUntil: 0,
    focused: null as string | null,
    overlays: new Set<string>(DEFAULT_ON),
    // id -> { t: time the droplet landed, gone: time it was removed (rings fade) }
    drops: new Map<string, { t: number; gone: number }>(),
    redraw: () => {},
  })
  const [overlays, setOverlays] = useState<string[]>(DEFAULT_ON)
  const [lastAdded, setLastAdded] = useState<string | null>(null)
  const [ring, setRing] = useState(false)
  const [coarse, setCoarse] = useState(false)
  useEffect(() => { target.current = { fog, clear } }, [fog, clear])
  useEffect(() => { setCoarse(window.matchMedia("(pointer: coarse)").matches) }, [])

  const focusOn = useCallback((id: string | null) => {
    const c = control.current
    c.focused = id
    if (!id) {
      tgt.current = { ...HOME_CAM, yaw: tgt.current.yaw }
      c.pausedUntil = performance.now() + 1500
    } else {
      const w = WAYPOINTS.find((x) => x.id === id)!
      const p = terracePoint(w.k, w.a)
      tgt.current = { ...tgt.current, pu: p.u * 0.9, pv: p.v * 0.9, zoom: 1.5, dist: 2.4, pitch: 0.8 }
      c.pausedUntil = performance.now() + 12000
    }
    c.redraw()
  }, [])

  // Overlays: click to add a waypoint to the field, click again to remove.
  const applyOverlays = useCallback((next: Set<string>) => {
    const c = control.current
    const now = performance.now()
    WAYPOINTS.forEach((w) => {
      const was = c.overlays.has(w.id), is = next.has(w.id)
      if (!was && is) c.drops.set(w.id, { t: now, gone: 0 })
      if (was && !is) { const d = c.drops.get(w.id); c.drops.set(w.id, { t: d?.t ?? now - 4000, gone: now }) }
    })
    c.overlays = next
    if (c.focused && !next.has(c.focused)) c.focused = null
    setOverlays(WAYPOINTS.filter((w) => next.has(w.id)).map((w) => w.id))
    c.redraw()
  }, [])
  const toggleOverlay = useCallback((id: string) => {
    const next = new Set(control.current.overlays)
    const adding = !next.has(id)
    if (adding) next.add(id); else next.delete(id)
    setLastAdded(adding ? id : null)
    applyOverlays(next)
  }, [applyOverlays])
  const toggleTier = useCallback((t: Tier) => {
    const ids = WAYPOINTS.filter((w) => w.tier === t).map((w) => w.id)
    const next = new Set(control.current.overlays)
    const allOn = ids.every((id) => next.has(id))
    ids.forEach((id) => (allOn ? next.delete(id) : next.add(id)))
    setLastAdded(null)
    applyOverlays(next)
  }, [applyOverlays])

  useEffect(() => {
    const canvas = canvasRef.current, wrap = wrapRef.current
    if (!canvas || !wrap) return
    const ctx = canvas.getContext("2d")
    if (!ctx) return

    const cloud = buildCloud()
    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches
    const t0 = performance.now()
    const ctl = control.current
    // The first overlays settle in as droplets, a beat apart.
    DEFAULT_ON.forEach((id, i) => ctl.drops.set(id, { t: t0 + 300 + i * 260, gone: 0 }))
    const cam: Cam = { ...tgt.current }
    const st = { fog: target.current.fog, nav: target.current.clear ? 1 : 0, scale: 1, visible: true, raf: 0, last: 0, hint: 0 }
    const ptr = { x: 0, y: 0, on: false, since: 0, down: false, mode: "orbit" as "orbit" | "pan", lx: 0, ly: 0, moved: 0 }
    const speck = mulberry32(11)
    const markers: { id: string; x: number; y: number }[] = []

    const resize = () => {
      const w = wrap.clientWidth
      const dpr = Math.min(window.devicePixelRatio || 1, 2)
      canvas.width = Math.round(w * dpr)
      canvas.height = Math.round(w * dpr)
      canvas.style.height = `${w}px`
      st.scale = (w * dpr) / S
    }
    resize()
    const ro = new ResizeObserver(() => { resize(); draw(performance.now()) })
    ro.observe(wrap)
    const io = new IntersectionObserver(([e]) => { st.visible = e.isIntersecting })
    io.observe(canvas)

    const local = (ev: { clientX: number; clientY: number }) => {
      const r = canvas.getBoundingClientRect()
      return { x: ((ev.clientX - r.left) / r.width) * S, y: ((ev.clientY - r.top) / r.height) * S }
    }
    const touch = () => { ctl.pausedUntil = Math.max(ctl.pausedUntil, performance.now() + 8000) }
    const panBy = (dx: number, dy: number) => {
      const t = tgt.current
      const k = t.dist / (360 * t.zoom)
      const cy = Math.cos(t.yaw), sy = Math.sin(t.yaw)
      const sp = Math.max(0.35, Math.abs(Math.sin(t.pitch)))
      t.pu = clamp(t.pu - dx * k * cy + (dy * k / sp) * sy, -1.2, 1.2)
      t.pv = clamp(t.pv + dx * k * sy + (dy * k / sp) * cy, -1.2, 1.2)
    }
    const dollyBy = (f: number) => { tgt.current.dist = clamp(tgt.current.dist * f, DIST_MIN, DIST_MAX) }
    const zoomBy = (f: number) => { tgt.current.zoom = clamp(tgt.current.zoom * f, 0.5, 3.5) }

    const onDown = (ev: PointerEvent) => {
      const p = local(ev)
      ptr.down = true; ptr.moved = 0
      ptr.mode = ev.shiftKey || ev.button === 1 || ev.button === 2 ? "pan" : "orbit"
      ptr.lx = p.x; ptr.ly = p.y
      canvas.setPointerCapture(ev.pointerId)
      canvas.style.cursor = "grabbing"
    }
    const onMove = (ev: PointerEvent) => {
      const p = local(ev)
      if (!ptr.on) ptr.since = performance.now()
      ptr.on = true; ptr.x = p.x; ptr.y = p.y
      if (ptr.down) {
        const dx = p.x - ptr.lx, dy = p.y - ptr.ly
        ptr.lx = p.x; ptr.ly = p.y
        ptr.moved += Math.abs(dx) + Math.abs(dy)
        if (ptr.moved > 3) {
          touch()
          if (ptr.mode === "pan") panBy(dx, dy)
          else {
            tgt.current.yaw -= dx * 0.012
            tgt.current.pitch = clamp(tgt.current.pitch + dy * 0.007, PITCH_MIN, PITCH_MAX)
          }
        }
      }
      if (reduced) draw(performance.now())
    }
    const onUp = (ev: PointerEvent) => {
      if (ptr.down && ptr.moved <= 3) {
        const p = local(ev)
        let best: string | null = null, bd = 16 * 16
        for (const m of markers) { const d = (m.x - p.x) ** 2 + (m.y - p.y) ** 2; if (d < bd) { bd = d; best = m.id } }
        if (best) focusOn(ctl.focused === best ? null : best)
      }
      ptr.down = false
      canvas.style.cursor = "grab"
      try { canvas.releasePointerCapture(ev.pointerId) } catch { /* already released */ }
    }
    const onLeave = () => { ptr.on = false; if (reduced) draw(performance.now()) }
    const onWheel = (ev: WheelEvent) => {
      if (ev.altKey) { ev.preventDefault(); touch(); dollyBy(Math.exp(ev.deltaY * 0.0018)) }
      else if (ev.ctrlKey || ev.metaKey) { ev.preventDefault(); touch(); zoomBy(Math.exp(-ev.deltaY * 0.0022)) }
      else { st.hint = performance.now(); return }
      if (reduced) draw(performance.now())
    }
    const onDbl = () => focusOn(null)
    const onKey = (ev: KeyboardEvent) => {
      const t = tgt.current
      let hit = true
      switch (ev.key) {
        case "ArrowLeft": t.yaw += 0.14; break
        case "ArrowRight": t.yaw -= 0.14; break
        case "ArrowUp": t.pitch = clamp(t.pitch + 0.08, PITCH_MIN, PITCH_MAX); break
        case "ArrowDown": t.pitch = clamp(t.pitch - 0.08, PITCH_MIN, PITCH_MAX); break
        case "+": case "=": zoomBy(1.18); break
        case "-": case "_": zoomBy(1 / 1.18); break
        case "0": case "Escape": focusOn(null); break
        default: hit = false
      }
      if (hit) { ev.preventDefault(); touch(); if (reduced) draw(performance.now()) }
    }
    const noMenu = (e: Event) => e.preventDefault()
    canvas.addEventListener("pointerdown", onDown)
    canvas.addEventListener("pointermove", onMove)
    canvas.addEventListener("pointerup", onUp)
    canvas.addEventListener("pointerleave", onLeave)
    canvas.addEventListener("wheel", onWheel, { passive: false })
    canvas.addEventListener("dblclick", onDbl)
    canvas.addEventListener("keydown", onKey)
    canvas.addEventListener("contextmenu", noMenu)

    function draw(now: number) {
      if (!ctx) return
      const dt = st.last ? Math.min(now - st.last, 64) : 16
      st.last = now
      const tg = target.current
      const isClear = tg.clear
      const ease = (ms: number) => (reduced ? 1 : 1 - Math.exp(-dt / ms))
      st.fog += (tg.fog - st.fog) * ease(420)
      st.nav += ((isClear ? 1 : 0) - st.nav) * ease(900)
      const fogv = st.fog, clarity = 1 - fogv
      if (!reduced && now > ctl.pausedUntil) tgt.current.yaw += (dt / ORBIT_MS) * TAU
      const ce = ease(260)
      ;(Object.keys(cam) as (keyof Cam)[]).forEach((k) => { cam[k] += (tgt.current[k] - cam[k]) * ce })

      const cy = Math.cos(cam.yaw), sy = Math.sin(cam.yaw), cp = Math.cos(cam.pitch), sp = Math.sin(cam.pitch)
      const D = cam.dist, F = 360 * cam.zoom * (cam.dist / 2.7), CX = 200, CY = 214
      const proj = (u: number, h: number, v: number) => {
        const uu = u - cam.pu, vv = v - cam.pv
        const x1 = uu * cy - vv * sy
        const z1 = uu * sy + vv * cy
        const Y = h * H
        const zc = z1 * cp - Y * sp
        const yc = z1 * sp + Y * cp
        const d = D + zc
        if (d < 0.25) return null
        return { x: CX + (F * x1) / d, y: CY - (F * yc) / d, d }
      }
      const path = (pts: ({ x: number; y: number } | null)[]) => {
        ctx.beginPath()
        let pen = false
        for (const p of pts) {
          if (!p) { pen = false; continue }
          if (pen) ctx.lineTo(p.x, p.y); else { ctx.moveTo(p.x, p.y); pen = true }
        }
        ctx.stroke()
      }
      const circle = (cu: number, cv: number, h: number, r: number) => {
        const pts = []
        const n = Math.max(24, Math.round(r * 90))
        for (let i = 0; i <= n; i++) { const a = (i / n) * TAU; pts.push(proj(cu + Math.cos(a) * r, h, cv + Math.sin(a) * r)) }
        path(pts)
      }

      ctx.setTransform(st.scale, 0, 0, st.scale, 0, 0)
      ctx.globalCompositeOperation = "source-over"
      ctx.fillStyle = "#02050a"
      ctx.fillRect(0, 0, S, S)
      const vg = ctx.createRadialGradient(CX, CY, 40, CX, CY, 290)
      vg.addColorStop(0, rgba(isClear ? signal.green : signal.cyan, 0.035 + clarity * 0.03))
      vg.addColorStop(1, "rgba(0,0,0,0)")
      ctx.fillStyle = vg
      ctx.fillRect(0, 0, S, S)

      // The ground ruling: fixed world spacing, so zooming between coarse and
      // fine makes it interfere with the terraces and the point grid. The
      // pattern that emerges belongs to none of them (and the form reads as
      // both concave and convex from overhead). Keep it subtle.
      ctx.lineWidth = 0.6
      ctx.strokeStyle = rgba(signal.cyan, 0.05 + clarity * 0.03)
      for (let r = 0.1; r <= 1.08; r += 0.07) circle(0, 0, 0, r)

      // Droplets. Each overlaid waypoint (and you) sends rings across the
      // ground; where families cross, they interfere. In fog the rings are
      // softer and wider; clarity tightens them.
      const gap = RIPPLE_GAP * (1 + fogv * 0.6)
      const sources: { u: number; v: number; color: string; born: number; gone: number }[] = []
      for (const w of WAYPOINTS) {
        const d = ctl.drops.get(w.id)
        if (!d) continue
        if (d.gone && now - d.gone > 2500) { ctl.drops.delete(w.id); continue }
        if (now < d.t) continue
        const p = terracePoint(w.k, w.a)
        sources.push({ u: p.u, v: p.v, color: TIER_COLOR[w.tier], born: d.t, gone: d.gone })
      }
      const nE = 1 - Math.pow(1 - st.nav, 3)
      const nu = START.u + (SUMMIT.u - START.u) * nE, nvv = START.v + (SUMMIT.v - START.v) * nE
      sources.push({ u: nu, v: nvv, color: signal.cyan, born: t0, gone: 0 })
      ctx.lineWidth = 0.6
      const travel = reduced ? 0.3 : ((now - t0) / 1000) * RIPPLE_SPEED
      for (const src of sources) {
        const age = (now - src.born) / 1000
        const fadeOut = src.gone ? Math.max(0, 1 - (now - src.gone) / 2500) : 1
        const fadeIn = Math.min(1, age / 0.6)
        const splash = Math.max(0, 1 - age / 2) // a fresh drop rings brighter
        const base = (0.045 + clarity * 0.035 + splash * 0.12) * fadeIn * fadeOut
        if (base < 0.004) continue
        const reach = Math.min(RIPPLE_REACH, 0.08 + age * 0.35)
        for (let r = (travel % gap) + 0.02; r < reach; r += gap) {
          ctx.strokeStyle = rgba(src.color, base * (1 - r / reach))
          circle(src.u, src.v, 0, r)
        }
      }
      const nLab = proj(0, 0, -1.18)
      ctx.font = `700 8px ${font.mono}`
      ctx.textAlign = "center"; ctx.textBaseline = "middle"
      if (nLab) { ctx.fillStyle = signal.cyan; ctx.fillText("N", nLab.x, nLab.y) }

      // Terrace edges. The apex locks gold once clear.
      for (let k = 1; k <= LEVELS; k++) {
        const d = HALF - (k - 1) * STEP_W, h = k * STEP_H
        const apexGold = k === LEVELS && st.nav > 0.5
        ctx.strokeStyle = apexGold ? rgba(signal.gold, 0.85) : rgba(k >= 5 ? "#94a3b8" : k >= 3 ? signal.cyan : signal.green, 0.12 + clarity * 0.25)
        ctx.lineWidth = k === LEVELS ? 1 : 0.7
        path([[-d, -d], [d, -d], [d, d], [-d, d], [-d, -d]].map(([a, b]) => proj(SUMMIT.u + a, h, SUMMIT.v + b)))
      }

      // Lidar returns, drawn additively so density reads as light.
      ctx.globalCompositeOperation = "lighter"
      const ptColor = mix("#7f97ad", signal.green, Math.max(0, clarity - 0.3) / 0.7)
      const keepBelow = 0.45 + clarity * 0.55
      const shimmerAge = (now - ptr.since) / 1000
      for (const p of cloud) {
        if (p.keep > keepBelow) continue
        const sc = fogv * p.keep
        const s = proj(p.u + p.ju * 0.09 * sc, p.h + p.jy * 0.5 * sc, p.v + p.jv * 0.09 * sc)
        if (!s || s.x < -10 || s.x > S + 10 || s.y < -10 || s.y > S + 10) continue
        const depthFade = 1 - Math.min(1, Math.max(0, (s.d - 1.9) / 1.8)) * (0.3 + fogv * 0.3)
        let a = (0.36 + clarity * 0.2 + p.edge * clarity * 0.3) * depthFade
        let x = s.x, y = s.y
        if (ptr.on && !ptr.down) {
          const dx = x - ptr.x, dy = y - ptr.y, d2 = dx * dx + dy * dy
          if (d2 < 3600) {
            const d = Math.sqrt(d2), f = 1 - d / 60
            const wave = Math.sin(d * 0.35 - shimmerAge * 9)
            x += (dx / (d || 1)) * wave * 1.4 * f
            y += (dy / (d || 1)) * wave * 1.4 * f
            a += f * (0.3 + 0.2 * wave)
          }
        }
        const apex = p.k === LEVELS && st.nav > 0.5
        ctx.fillStyle = apex ? rgba(signal.gold, a * 0.9) : rgba(p.wall ? mix(ptColor, "#9fb3c8", 0.35) : ptColor, a)
        const sz = Math.min(4, (1.4 + clarity * 0.35) * (2.7 / s.d) * Math.sqrt(cam.zoom))
        ctx.fillRect(x - sz / 2, y - sz / 2, sz, sz)
      }
      if (fogv > 0.05 && !reduced) {
        const n = Math.round(260 * fogv)
        for (let i = 0; i < n; i++) {
          ctx.fillStyle = rgba("#9fb3c8", 0.04 + speck() * 0.12 * fogv)
          ctx.fillRect(speck() * S, speck() * S, 0.8, 0.8)
        }
      }
      ctx.globalCompositeOperation = "source-over"

      // Waypoints. Labels never stack: focused first, then nearest; a label
      // that would collide keeps its marker and drops its text.
      markers.length = 0
      ctx.font = `600 7.5px ${font.mono}`
      const placed: { x: number; y: number; w: number; h: number }[] = []
      const order = WAYPOINTS.filter((w) => ctl.overlays.has(w.id)).map((w) => {
        const p = terracePoint(w.k, w.a)
        return { w, base: proj(p.u, height(p.u, p.v), p.v), top: proj(p.u, height(p.u, p.v) + 0.16, p.v) }
      }).sort((a, b) => (ctl.focused === a.w.id ? -1 : ctl.focused === b.w.id ? 1 : (a.top?.d ?? 99) - (b.top?.d ?? 99)))
      for (const { w, base, top } of order) {
        if (!base || !top) continue
        const drop = ctl.drops.get(w.id)
        const grow = drop ? clamp((now - drop.t) / 500, 0, 1) : 1
        if (grow <= 0) continue
        markers.push({ id: w.id, x: top.x, y: top.y })
        const sel = ctl.focused === w.id
        const col = TIER_COLOR[w.tier]
        const al = (sel ? 1 : 0.55 + clarity * 0.45) * grow
        const box = { x: top.x + 5, y: top.y - 6, w: ctx.measureText(w.label.toUpperCase()).width + 4, h: 12 }
        const free = !placed.some((b) => box.x < b.x + b.w && b.x < box.x + box.w && box.y < b.y + b.h && b.y < box.y + box.h)
        if (free) placed.push(box)
        ctx.strokeStyle = rgba(col, al * 0.7); ctx.lineWidth = 0.7
        ctx.beginPath(); ctx.moveTo(base.x, base.y); ctx.lineTo(top.x, top.y); ctx.stroke()
        const r = (sel ? 5 : 3.6) * grow
        ctx.fillStyle = rgba(col, al)
        ctx.beginPath(); ctx.moveTo(top.x, top.y - r); ctx.lineTo(top.x + r, top.y); ctx.lineTo(top.x, top.y + r); ctx.lineTo(top.x - r, top.y); ctx.closePath(); ctx.fill()
        if (sel) { ctx.strokeStyle = rgba(col, 0.6); ctx.beginPath(); ctx.arc(top.x, top.y, 9, 0, TAU); ctx.stroke() }
        if (!free) continue
        ctx.textAlign = "left"; ctx.textBaseline = "middle"
        ctx.fillStyle = rgba(sel ? "#e2e8f0" : col, al)
        ctx.fillText(w.label.toUpperCase(), top.x + 7, top.y)
      }

      // You: the navigator. Climbs the terraces to the apex once the row exists.
      const nh = height(nu, nvv)
      const nb = proj(nu, nh, nvv), nt = proj(nu, nh + 0.42, nvv)
      if (nb && nt) {
        ctx.strokeStyle = rgba(signal.cyan, 0.35 + clarity * 0.45)
        ctx.lineWidth = 0.8
        ctx.beginPath(); ctx.moveTo(nb.x, nb.y); ctx.lineTo(nt.x, nt.y); ctx.stroke()
        const halo = ctx.createRadialGradient(nb.x, nb.y, 0, nb.x, nb.y, 20)
        halo.addColorStop(0, rgba(signal.cyan, 0.3 + clarity * 0.35)); halo.addColorStop(1, rgba(signal.cyan, 0))
        ctx.fillStyle = halo
        ctx.beginPath(); ctx.arc(nb.x, nb.y, 20, 0, TAU); ctx.fill()
        ctx.fillStyle = signal.cyan
        ctx.beginPath(); ctx.moveTo(nt.x, nt.y - 4); ctx.lineTo(nt.x + 3.5, nt.y); ctx.lineTo(nt.x, nt.y + 4); ctx.lineTo(nt.x - 3.5, nt.y); ctx.closePath(); ctx.fill()
        ctx.beginPath(); ctx.arc(nb.x, nb.y, 3, 0, TAU); ctx.fill()
      }
      if (st.nav > 0.6) {
        ctx.strokeStyle = rgba(signal.cyan, 0.85 * ((st.nav - 0.6) / 0.4))
        ctx.setLineDash([3, 3]); ctx.lineWidth = 1
        const bl = []
        for (let i = 0; i <= 40; i++) { const v = SUMMIT.v - (i / 40) * 1.1; bl.push(proj(SUMMIT.u, height(SUMMIT.u, v) + 0.02, v)) }
        path(bl); ctx.setLineDash([])
      }

      // HUD: a frame, a heading, and clarity. Nothing that does not orient you.
      const hud = rgba("#94a3b8", 0.85), dim = rgba("#64748b", 0.9)
      ctx.strokeStyle = rgba("#94a3b8", 0.4); ctx.lineWidth = 1
      ;[[10, 10, 1, 1], [390, 10, -1, 1], [390, 390, -1, -1], [10, 390, 1, -1]].forEach(([x, y, dx, dy]) => {
        ctx.beginPath(); ctx.moveTo(x, y + dy * 14); ctx.lineTo(x, y); ctx.lineTo(x + dx * 14, y); ctx.stroke()
      })
      ctx.font = `600 7.5px ${font.mono}`
      ctx.textBaseline = "alphabetic"
      const hdg = ((-cam.yaw * 180) / Math.PI % 360 + 360) % 360
      ctx.save()
      ctx.beginPath(); ctx.rect(130, 14, 140, 22); ctx.clip()
      for (let dgr = -90; dgr <= 90; dgr += 5) {
        const val = Math.round((hdg + dgr) / 5) * 5
        const x = 200 + (val - hdg) * 1.4
        const major = ((val % 30) + 30) % 30 === 0
        ctx.strokeStyle = rgba("#94a3b8", major ? 0.6 : 0.3)
        ctx.beginPath(); ctx.moveTo(x, 34); ctx.lineTo(x, major ? 27 : 30); ctx.stroke()
        if (major) { ctx.fillStyle = dim; ctx.textAlign = "center"; ctx.fillText(pad(((val % 360) + 360) % 360, 3), x, 23) }
      }
      ctx.restore()
      ctx.fillStyle = signal.cyan
      ctx.beginPath(); ctx.moveTo(200, 37); ctx.lineTo(196.5, 42); ctx.lineTo(203.5, 42); ctx.closePath(); ctx.fill()
      ctx.textAlign = "center"; ctx.fillStyle = hud
      ctx.fillText(`HDG ${pad(hdg, 3)}`, 200, 52)

      const gx = 382, gy0 = 120, gy1 = 300
      ctx.strokeStyle = rgba("#94a3b8", 0.3)
      ctx.strokeRect(gx - 2, gy0, 4, gy1 - gy0)
      const fillTop = gy1 - (gy1 - gy0) * clarity
      ctx.fillStyle = isClear ? signal.green : clarity > 0.1 ? signal.gold : "#64748b"
      ctx.fillRect(gx - 1, fillTop, 2, gy1 - fillTop)
      ctx.save(); ctx.translate(gx - 8, (gy0 + gy1) / 2); ctx.rotate(-Math.PI / 2)
      ctx.textAlign = "center"; ctx.fillStyle = dim; ctx.fillText("CLARITY", 0, 0); ctx.restore()
      ctx.textAlign = "right"; ctx.fillStyle = hud
      ctx.fillText(`${pad(clarity * 100, 2)}%`, 388, gy1 + 13)

      if (now - st.hint < 1400) {
        ctx.textAlign = "center"; ctx.fillStyle = rgba("#e2e8f0", 0.9)
        ctx.fillText("HOLD ⌘ OR CTRL TO ZOOM", 200, 372)
      }

      if (!reduced) st.raf = requestAnimationFrame(loop)
    }
    function loop(now: number) {
      if (st.visible && document.visibilityState === "visible") draw(now)
      else { st.last = 0; st.raf = requestAnimationFrame(loop) }
    }
    ctl.redraw = () => { if (reduced) draw(performance.now()) }
    st.raf = requestAnimationFrame(loop)
    const redraw = reduced ? window.setInterval(() => draw(performance.now()), 300) : 0

    return () => {
      cancelAnimationFrame(st.raf)
      if (redraw) clearInterval(redraw)
      ro.disconnect(); io.disconnect()
      canvas.removeEventListener("pointerdown", onDown)
      canvas.removeEventListener("pointermove", onMove)
      canvas.removeEventListener("pointerup", onUp)
      canvas.removeEventListener("pointerleave", onLeave)
      canvas.removeEventListener("wheel", onWheel)
      canvas.removeEventListener("dblclick", onDbl)
      canvas.removeEventListener("keydown", onKey)
      canvas.removeEventListener("contextmenu", noMenu)
    }
  }, [focusOn])

  const shown = WAYPOINTS.filter((w) => overlays.includes(w.id))
  const added = lastAdded && overlays.includes(lastAdded) ? WAYPOINTS.find((w) => w.id === lastAdded) : null
  const note = added
    ? `${added.label}: ${added.note}.`
    : shown.length
      ? `On the field: ${shown.map((w) => w.label).join(", ")}.`
      : "Add overlays to the field."
  const label = `A sketch of the ARCS field as stepped terrain. Lower terraces hold what exists now, upper terraces what comes next and later. Showing: ${shown.map((w) => w.label).join(", ") || "nothing"}. ${clear ? "Clear; you stand on the apex." : "Under fog; you wait at the edge."} Arrow keys orbit and tilt, plus and minus zoom, 0 resets.`
  const mono: React.CSSProperties = { fontFamily: font.mono, ...font.tier.t3, textTransform: "uppercase", whiteSpace: "nowrap", fontVariantNumeric: "tabular-nums" }

  return (
    <figure style={{ margin: 0, border: `1px solid ${border.subtle}`, borderRadius: 10, background: "#02050a", overflow: "hidden" }}>
      <div ref={wrapRef} style={{ width: "100%", lineHeight: 0 }}>
        <canvas
          ref={canvasRef}
          role="img"
          tabIndex={0}
          aria-label={label}
          onFocus={(e) => setRing(e.currentTarget.matches(":focus-visible"))}
          onBlur={() => setRing(false)}
          style={{ display: "block", width: "100%", cursor: "grab", touchAction: "pan-y", outline: ring ? `1px solid ${signal.cyan}` : "none", outlineOffset: -2 }}
        />
      </div>

      <div style={{ padding: "0.85rem 1rem", borderTop: `1px solid ${border.subtle}`, display: "grid", gap: "0.55rem" }}>
        <div style={{ ...mono, color: text.dimmed }}>A sketch of the field</div>
        {(["now", "next", "later"] as Tier[]).map((t) => {
          const ids = WAYPOINTS.filter((w) => w.tier === t).map((w) => w.id)
          const allOn = ids.every((id) => overlays.includes(id))
          return (
            <div key={t} role="group" aria-label={`${TIER_NAME[t]} overlays`} style={{ display: "flex", alignItems: "center", gap: "0.45rem", flexWrap: "wrap" }}>
              <button
                type="button"
                aria-pressed={allOn}
                onClick={() => toggleTier(t)}
                title={`${allOn ? "Remove" : "Add"} every ${TIER_NAME[t]} overlay`}
                style={{ ...mono, color: TIER_COLOR[t], width: 52, flexShrink: 0, textAlign: "left", background: "none", border: "none", padding: "4px 0", minHeight: 26, cursor: "pointer", textDecoration: allOn ? "underline" : "none", textUnderlineOffset: 4 }}
              >
                {TIER_NAME[t]}
              </button>
              {WAYPOINTS.filter((w) => w.tier === t).map((w) => {
                const on = overlays.includes(w.id)
                return (
                  <button
                    key={w.id}
                    type="button"
                    aria-pressed={on}
                    title={`${on ? "Remove from" : "Add to"} the field: ${w.note}`}
                    onClick={() => toggleOverlay(w.id)}
                    style={{
                      fontFamily: font.mono, ...font.tier.t2, textTransform: "uppercase", whiteSpace: "nowrap",
                      color: on ? text.primary : TIER_COLOR[t],
                      background: on ? `${TIER_COLOR[t]}26` : "transparent",
                      border: `1px solid ${TIER_COLOR[t]}${on ? "cc" : "4d"}`,
                      borderRadius: 3, padding: "4px 8px", minHeight: 26, cursor: "pointer",
                      transition: "background-color .15s, border-color .15s, color .15s",
                    }}
                  >
                    {w.label}
                  </button>
                )
              })}
            </div>
          )
        })}
        <p aria-live="polite" style={{ fontFamily: font.sans, fontSize: "0.8125rem", lineHeight: 1.5, color: text.secondary, margin: "0.1rem 0 0", minHeight: "1.2em" }}>{note}</p>
      </div>

      <figcaption style={{ display: "grid", gridTemplateColumns: "1fr auto", alignItems: "center", gap: "0.35rem 0.75rem", padding: "0.7rem 1rem", borderTop: `1px solid ${border.subtle}` }}>
        <span style={{ ...mono, color: zoneColor, overflow: "hidden", textOverflow: "ellipsis" }}>Zone · {zone}</span>
        <span style={{ ...mono, color: text.secondary }}>Visibility {Math.round((1 - fog) * 100)}%</span>
        <span style={{ ...mono, gridColumn: "1 / -1", color: text.dimmed, whiteSpace: "normal", lineHeight: 1.7 }}>
          {coarse ? "Drag to look around · Tap a waypoint to fly to it" : "Drag to orbit · Shift drag to pan · ⌘ scroll to zoom · Click a waypoint to fly to it"}
        </span>
      </figcaption>
    </figure>
  )
}
