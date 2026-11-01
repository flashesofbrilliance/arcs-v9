'use client'
import React, { useCallback, useEffect, useRef, useState } from 'react'
import { ChipToggle } from '@/ui/ChipToggle'
import { CloseButton } from '@/ui/CloseButton'
import { font } from '@/ui/tokens'
import type { FieldSource } from './reading'
import { GRID, cellToPx, fitCell, orientationOf, snap, type Cell, type Orientation } from './snap'
import { FidelityView } from './fidelity'
import { ConvictionView } from './conviction'
import { ClarityView } from './clarity'
import { CoherenceView } from './coherence'
import { ConsonanceView } from './consonance'

// Admin-only widget layer over the field HUD. Sticky (fixed, above the canvas), closable (CloseButton +
// ChipToggle tray), draggable with pointer capture, arrow keys move one cell, Escape restores.
// Layout is per viewer in localStorage (try/catch; empty or corrupt renders the default).
const KEY = 'arcs.hud.widgets.v1'
const IDS = ['fidelity', 'conviction', 'clarity', 'coherence', 'consonance'] as const
type Id = (typeof IDS)[number]
type Item = { cell: Cell; closed: boolean }
type Layout = Record<Id, Item>
const W = 2 // widget width in cells
const TRAY = 48 // px kept clear for the chip tray
const H = 2 // widget height in cells (the tallest face is about 1.5 cells)

export function defaultLayout(): Layout {
  const l = {} as Layout
  IDS.forEach((id, i) => { l[id] = { cell: { col: i * 2, row: 99 }, closed: false } }) // row 99 clamps to the bottom row
  return l
}

export function parseLayout(raw: string | null): Layout {
  const d = defaultLayout()
  if (!raw) return d
  try {
    const o = JSON.parse(raw)
    for (const id of IDS) {
      const it = o?.[id]
      if (it && Number.isInteger(it.cell?.col) && Number.isInteger(it.cell?.row) && typeof it.closed === 'boolean') d[id] = { cell: { col: it.cell.col, row: it.cell.row }, closed: it.closed }
    }
  } catch { /* corrupt: default */ }
  return d
}

const TITLES: Record<Id, string> = { fidelity: 'Fidelity', conviction: 'Conviction', clarity: 'Clarity', coherence: 'Coherence', consonance: 'Consonance' }

function View({ id, field }: { id: Id; field: FieldSource }) {
  switch (id) {
    case 'fidelity': return <FidelityView source={field} />
    case 'conviction': return <ConvictionView source={field} />
    case 'clarity': return <ClarityView source={field} />
    case 'coherence': return <CoherenceView source={field} />
    case 'consonance': return <ConsonanceView source={null} />
  }
}

export function HudWidgets({ field }: { field: FieldSource }) {
  const [layout, setLayout] = useState<Layout>(defaultLayout)
  const [vp, setVp] = useState({ w: 1280, h: 800 })
  const [drag, setDrag] = useState<{ id: Id; x: number; y: number } | null>(null)
  const [reduce, setReduce] = useState(true)
  const origin = useRef<{ id: Id; cell: Cell } | null>(null)
  const grab = useRef<{ dx: number; dy: number; from: Cell } | null>(null)
  const ori: Orientation = orientationOf(vp.w, vp.h)

  useEffect(() => {
    // Read after mount: localStorage is client-only, so reading during render would mismatch hydration.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    try { setLayout(parseLayout(window.localStorage.getItem(KEY))) } catch { /* default */ }
    setReduce(window.matchMedia?.('(prefers-reduced-motion: reduce)').matches ?? true)
    const on = () => setVp({ w: window.innerWidth, h: window.innerHeight })
    on()
    window.addEventListener('resize', on)
    return () => window.removeEventListener('resize', on)
  }, [])

  const commit = useCallback((next: Layout) => {
    setLayout(next)
    try { window.localStorage.setItem(KEY, JSON.stringify(next)) } catch { /* storage blocked */ }
  }, [])
  const place = (id: Id, c: Cell) => commit({ ...layout, [id]: { ...layout[id], cell: fitCell(c, vp.w, vp.h - TRAY, ori, W, H) } })

  const onKey = (id: Id, e: React.KeyboardEvent) => {
    const c = fitCell(layout[id].cell, vp.w, vp.h - TRAY, ori, W, H)
    const d: Record<string, Cell> = { ArrowLeft: { col: c.col - 1, row: c.row }, ArrowRight: { col: c.col + 1, row: c.row }, ArrowUp: { col: c.col, row: c.row - 1 }, ArrowDown: { col: c.col, row: c.row + 1 } }
    if (e.key === 'Escape') {
      if (drag) { setDrag(null); grab.current = null; e.preventDefault(); return }
      if (origin.current?.id === id) { place(id, origin.current.cell); e.preventDefault() }
    } else if (d[e.key]) {
      e.preventDefault()
      if (origin.current?.id !== id) origin.current = { id, cell: layout[id].cell } // focus event can be missed
      place(id, d[e.key])
    }
  }

  const down = (id: Id, e: React.PointerEvent<HTMLDivElement>) => {
    if ((e.target as HTMLElement).closest('button')) return
    const px = cellToPx(fitCell(layout[id].cell, vp.w, vp.h - TRAY, ori, W, H), ori)
    e.currentTarget.setPointerCapture(e.pointerId)
    grab.current = { dx: e.clientX - px.x, dy: e.clientY - px.y, from: layout[id].cell }
    origin.current = { id, cell: layout[id].cell }
    setDrag({ id, x: px.x, y: px.y })
  }
  const move = (e: React.PointerEvent<HTMLDivElement>) => {
    if (!drag || !grab.current) return
    setDrag({ id: drag.id, x: e.clientX - grab.current.dx, y: e.clientY - grab.current.dy })
  }
  const up = (e: React.PointerEvent<HTMLDivElement>) => {
    if (!drag || !grab.current) return
    const g = GRID[ori].cell
    const c = snap(drag.x + g / 2, drag.y + g / 2, ori)
    const id = drag.id
    setDrag(null); grab.current = null
    if (e.currentTarget.hasPointerCapture(e.pointerId)) e.currentTarget.releasePointerCapture(e.pointerId)
    if (c) place(id, c)
  }

  const g = GRID[ori].cell
  return (
    <>
      {IDS.filter((id) => !layout[id].closed).map((id) => {
        const px = drag?.id === id ? { x: drag.x, y: drag.y } : cellToPx(fitCell(layout[id].cell, vp.w, vp.h - TRAY, ori, W, H), ori)
        return (
          <div
            key={id}
            role="group"
            aria-label={`${TITLES[id]} widget. Arrow keys move one cell, Escape restores.`}
            tabIndex={0}
            onFocus={() => { origin.current = { id, cell: layout[id].cell } }}
            onKeyDown={(e) => onKey(id, e)}
            onPointerDown={(e) => down(id, e)}
            onPointerMove={move}
            onPointerUp={up}
            onPointerCancel={() => { setDrag(null); grab.current = null }}
            style={{ position: 'fixed', zIndex: 1100, left: px.x, top: px.y, width: W * g, minHeight: g, boxSizing: 'border-box', padding: 4,
              touchAction: 'none', cursor: drag?.id === id ? 'grabbing' : 'grab', userSelect: 'none',
              transition: drag?.id === id || reduce ? 'none' : 'left .15s, top .15s' }}
          >
            <div style={{ position: 'absolute', top: 0, right: 0, zIndex: 2 }}>
              <CloseButton label={`Close ${TITLES[id]} widget`} size={10} style={{ width: 32, height: 32 }} onClick={() => commit({ ...layout, [id]: { ...layout[id], closed: true } })} />
            </div>
            <View id={id} field={field} />
          </div>
        )
      })}
      <div role="toolbar" aria-label="HUD widgets" style={{ position: 'fixed', zIndex: 1101, left: 8, bottom: 8, display: 'flex', flexWrap: 'wrap', gap: 6, maxWidth: 'calc(100vw - 16px)', fontFamily: font.mono }}>
        {IDS.map((id) => (
          <ChipToggle key={id} label={TITLES[id]} selected={!layout[id].closed} onClick={() => commit({ ...layout, [id]: { ...layout[id], closed: !layout[id].closed } })} />
        ))}
      </div>
    </>
  )
}
