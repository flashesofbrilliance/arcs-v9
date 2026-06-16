// Dark-mode lock for ARCS emails.
//
// The cockpit-register emails are authored dark. Apple Mail / Outlook respect
// the `color-scheme` meta tags, but the Gmail mobile app ignores them and
// force-inverts colors — flipping a dark email to light when the phone is in
// dark mode (and vice versa). Gmail tags every element whose color it rewrote
// with `data-ogsc` (text) / `data-ogsb` (background); re-pinning the palette
// through those attribute selectors is the only reliable way to hold the theme.
//
// Usage: drop `darkLockHead(C)` into <head> (after the meta tags) and apply the
// `arcs-*` classes to the elements whose color must survive inversion:
//   arcs-bg · arcs-panel · arcs-card  (backgrounds)
//   arcs-ink · arcs-cyan · arcs-body · arcs-muted  (text)
//   arcs-gold · arcs-green · arcs-red  (accents, emitted only when in palette)

export interface DarkLockPalette {
  bg: string
  panel: string
  card?: string // inner card bg (defaults to a near-panel tone)
  ink: string
  cyan: string
  body: string
  muted: string
  gold?: string
  green?: string
  red?: string
}

export function darkLockHead(C: DarkLockPalette): string {
  const card = C.card ?? '#0a0f1a'
  // Accent text rules — only for the accents this template actually uses.
  const accents: [string, string | undefined][] = [
    ['arcs-gold', C.gold], ['arcs-green', C.green], ['arcs-red', C.red],
  ]
  const accentInvert = accents
    .filter(([, v]) => v)
    .map(([cls, v]) => `  [data-ogsc] .${cls} { color: ${v} !important; }`)
    .join('\n')
  const accentLight = accents
    .filter(([, v]) => v)
    .map(([cls, v]) => `    .${cls} { color: ${v} !important; }`)
    .join('\n')
  return `<style>
  :root { color-scheme: dark; supported-color-schemes: dark; }
  /* Gmail mobile force-inverts and tags rewritten elements with data-ogsc
     (text) / data-ogsb (background). Re-pin the cockpit palette so the email
     always renders dark, regardless of the phone's light/dark mode. */
  [data-ogsb] .arcs-bg, u + .arcs-body .arcs-bg { background-color: ${C.bg} !important; }
  [data-ogsb] .arcs-panel { background-color: ${C.panel} !important; }
  [data-ogsb] .arcs-card  { background-color: ${card} !important; }
  [data-ogsc] .arcs-ink   { color: ${C.ink} !important; }
  [data-ogsc] .arcs-cyan  { color: ${C.cyan} !important; }
  [data-ogsc] .arcs-body  { color: ${C.body} !important; }
  [data-ogsc] .arcs-muted { color: ${C.muted} !important; }
${accentInvert}
  @media (prefers-color-scheme: light) {
    .arcs-bg { background-color: ${C.bg} !important; }
    .arcs-panel { background-color: ${C.panel} !important; }
    .arcs-card { background-color: ${card} !important; }
    .arcs-ink { color: ${C.ink} !important; }
    .arcs-cyan { color: ${C.cyan} !important; }
    .arcs-body { color: ${C.body} !important; }
    .arcs-muted { color: ${C.muted} !important; }
${accentLight}
  }
</style>`
}
