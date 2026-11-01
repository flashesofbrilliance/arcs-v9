// Grid snapping for HUD widgets. Pure, no DOM. Cells are CELL px square per orientation.
export type Orientation = 'landscape' | 'portrait'
export interface Cell { col: number; row: number }

export const GRID: Record<Orientation, { cell: number; cols: number; rows: number }> = {
  landscape: { cell: 96, cols: 24, rows: 12 },
  portrait: { cell: 80, cols: 8, rows: 16 },
}

// Lockup sizes in cells (cols x rows): chip 1x1, one-sheet 2x3 landscape / 3x2 portrait.
export const SHEET: Record<Orientation, { cols: number; rows: number }> = {
  landscape: { cols: 2, rows: 3 },
  portrait: { cols: 3, rows: 2 },
}

export function orientationOf(vw: number, vh: number): Orientation {
  return Number.isFinite(vw) && Number.isFinite(vh) && vh > vw ? 'portrait' : 'landscape'
}

const clamp = (v: number, lo: number, hi: number) => Math.max(lo, Math.min(hi, v))

// Non-finite input returns null (never NaN); out-of-range input clamps to the grid.
export function snap(x: number, y: number, orientation: Orientation): Cell | null {
  if (!Number.isFinite(x) || !Number.isFinite(y)) return null
  const g = GRID[orientation] ?? GRID.landscape
  return {
    col: clamp(Math.floor(x / g.cell), 0, g.cols - 1),
    row: clamp(Math.floor(y / g.cell), 0, g.rows - 1),
  }
}

export function cellToPx(c: Cell, orientation: Orientation): { x: number; y: number } {
  const g = GRID[orientation] ?? GRID.landscape
  return { x: c.col * g.cell, y: c.row * g.cell }
}

// Keep a cell (widget top-left, widget spans wc x wr cells) inside the real viewport.
// A zero-size viewport yields cell 0,0.
export function fitCell(c: Cell, vw: number, vh: number, orientation: Orientation, wc = 1, wr = 1): Cell {
  const g = GRID[orientation] ?? GRID.landscape
  const maxCol = Math.max(0, Math.min(g.cols, Math.floor((Number.isFinite(vw) ? vw : 0) / g.cell)) - wc)
  const maxRow = Math.max(0, Math.min(g.rows, Math.floor((Number.isFinite(vh) ? vh : 0) / g.cell)) - wr)
  return { col: clamp(Number.isFinite(c.col) ? c.col : 0, 0, maxCol), row: clamp(Number.isFinite(c.row) ? c.row : 0, 0, maxRow) }
}
