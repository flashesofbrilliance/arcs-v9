// Reading: what every HUD widget's pure read() returns. No hidden inputs, no network.
// grain is 0 (sharp) to 1 (flat), derived from n against the widget's threshold.
export interface Reading {
  id: string
  value: number | null     // null = no signal
  n: number                // sample size behind the value
  threshold: number | null // n needed to render sharp; null = never until a source exists
  grain: number            // 0 sharp .. 1 grain
  asOf: string | null
  source: string
}

export function grainOf(n: number, threshold: number | null): number {
  if (threshold === null) return 1
  if (!Number.isFinite(n) || n <= 0) return 1
  return Math.max(0, Math.min(1, 1 - n / threshold))
}

export function isGrain(r: Reading): boolean {
  return r.value === null || r.threshold === null || r.n < r.threshold
}

export function num(x: unknown): number | null {
  return typeof x === 'number' && Number.isFinite(x) ? x : null
}

// The slice of universe-field.json the widgets read (passed in by the server page, admin only).
export interface FieldSource {
  as_of_date?: string | null
  nodes?: Array<{ files?: number; sig?: { frequency?: { last_28d?: number } } }>
  dimensions?: {
    conviction?: { signal?: number | null }
    clarity?: { nodes_clear?: number; nodes?: number }
    coherence?: { diamonds?: number; mean_hardness?: number }
  }
}
