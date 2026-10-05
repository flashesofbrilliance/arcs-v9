// Job Factory slice 4 (2026-10-05): the autonomy dial, as flags with no UI.
// Each station of the line is Off, Ask, or Auto. The morning task reads the
// effective flags from GET /api/jobs/autonomy and obeys them. Autonomy is earned
// one station at a time, by receipt, never by decree; LOCKED stations can never
// move, whatever is stored (the server refuses the write and ignores a bad row).
//
// Locked, per the spec after the gauntlet:
//   send          Off   the system never sends anything for Zach
//   go_public     Ask   a page goes public only at Send, after the PII gate
//   rubric_update Ask   corrections propose a rubric diff; Zach approves it
//   inbox_read    Ask   a reply is surfaced for Zach to tag; it never moves a row
//   outcome       Off   a receipt cannot close itself (the lane route already refuses the pipeline token)

export const MODES = ["off", "ask", "auto"] as const
export type Mode = (typeof MODES)[number]

export const STATIONS = {
  find:          { label: "Find: re-pull alerts, post rows",       default: "auto", locked: false },
  score:         { label: "Read + score",                           default: "auto", locked: false },
  cut_t12:       { label: "Cut: tiers 1 and 2 (edit from seed)",    default: "auto", locked: false },
  cut_t3:        { label: "Cut: tier 3",                            default: "ask",  locked: false },
  full_forge:    { label: "Cut: full forge (unseeded shape)",       default: "ask",  locked: false },
  prose:         { label: "Prose: cover letter + answers drafts",   default: "ask",  locked: false },
  send:          { label: "Send",                                   default: "off",  locked: true },
  go_public:     { label: "Go public (host a page)",                default: "ask",  locked: true },
  rubric_update: { label: "Rubric update from corrections",         default: "ask",  locked: true },
  inbox_read:    { label: "Inbox read (tag replies)",               default: "ask",  locked: true },
  outcome:       { label: "Close a row's outcome",                  default: "off",  locked: true },
} as const satisfies Record<string, { label: string; default: Mode; locked: boolean }>
export type Station = keyof typeof STATIONS

export const SETTING_KEY = "autonomy"

// Effective flags: defaults, overlaid by stored values for UNLOCKED stations only.
// A locked station's stored value is ignored, so a hand-edited row cannot unlock it.
export function effective(stored: string | null | undefined): Record<Station, { mode: Mode; locked: boolean; label: string; changed: boolean }> {
  let raw: Record<string, unknown> = {}
  try { const v = stored ? JSON.parse(stored) : {}; if (v && typeof v === "object" && !Array.isArray(v)) raw = v as Record<string, unknown> } catch { raw = {} }
  const out = {} as Record<Station, { mode: Mode; locked: boolean; label: string; changed: boolean }>
  for (const [k, s] of Object.entries(STATIONS) as [Station, (typeof STATIONS)[Station]][]) {
    const want = raw[k]
    const ok = !s.locked && typeof want === "string" && (MODES as readonly string[]).includes(want)
    const mode = (ok ? want : s.default) as Mode
    out[k] = { mode, locked: s.locked, label: s.label, changed: mode !== s.default }
  }
  return out
}

// Validate a write. Locked stations refuse ANY change (even to their own default,
// so the stored row never carries them). Returns the merged stored object or an error.
export function applyChange(stored: string | null | undefined, change: unknown): { next: Record<string, Mode> } | { error: string } {
  if (!change || typeof change !== "object" || Array.isArray(change)) return { error: "autonomy must be an object of station: mode" }
  let cur: Record<string, Mode> = {}
  try { const v = stored ? JSON.parse(stored) : {}; if (v && typeof v === "object" && !Array.isArray(v)) cur = v } catch { cur = {} }
  const next: Record<string, Mode> = {}
  for (const [k, v] of Object.entries(cur)) if (k in STATIONS && !STATIONS[k as Station].locked) next[k] = v
  for (const [k, v] of Object.entries(change as Record<string, unknown>)) {
    if (!(k in STATIONS)) return { error: `unknown station: ${k}` }
    if (STATIONS[k as Station].locked) return { error: `${k} is locked (${STATIONS[k as Station].default}); it cannot be changed` }
    if (typeof v !== "string" || !(MODES as readonly string[]).includes(v)) return { error: `${k}: mode must be one of ${MODES.join(", ")}` }
    next[k] = v as Mode
  }
  return { next }
}
