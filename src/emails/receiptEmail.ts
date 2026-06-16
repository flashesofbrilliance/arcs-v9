// ARCS receipt email — the T₀ confirmation sent the moment a compass bearing
// locks. Replaces the plain-text "Your compass bearing is locked" send in
// compass/route.ts with a designed, email-safe artifact in the cockpit register.
//
// Email-safe like welcomeEmail.ts / debriefEmail.ts: table layout, inline
// styles, solid colors only (no backdrop-filter/blur/background-image), serif +
// system-font fallbacks. Returns { subject, text, html }.

export interface ReceiptEmailOpts {
  // The sharpened question / decision (drives the subject line).
  question: string
  // Compass True North output — the bearing.
  trueNorth: string
  // The "why" bullets behind the bearing.
  why: string[]
  // Conviction (NCI composite, 0–100).
  nci: number
  // Decision mode: QUICKMOVE | PLAN | COURT.
  mode: string
  // Door class: ONE_WAY | TWO_WAY.
  door?: string
  // CTA target — the cartography brief surface.
  briefUrl: string
  // Unique fragment (receipt id tail) — keeps Gmail from threading repeats.
  token?: string
}

const C = {
  bg: '#020408',
  panel: '#0d1117',
  border: '#1e293b',
  cyan: '#00F0FF',
  green: '#00FF9D',
  gold: '#FFD700',
  red: '#FF4D6D',
  ink: '#eafcff',
  body: '#94a3b8',
  muted: '#475569',
  serif: "Georgia, 'Times New Roman', serif",
  sans: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif",
  mono: "'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace",
}

function escapeHtml(s: string): string {
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

// Conviction → color band (mirrors nciColor in the app's tokens).
function convictionColor(nci: number): string {
  if (nci >= 75) return C.green
  if (nci >= 55) return C.cyan
  if (nci >= 40) return C.gold
  return C.red
}

export function receiptEmail(opts: ReceiptEmailOpts): { subject: string; text: string; html: string } {
  const { question, trueNorth, briefUrl } = opts
  const why = (opts.why ?? []).filter(Boolean)
  const nci = Math.round(opts.nci)
  const mode = (opts.mode ?? '').toUpperCase()
  const door = (opts.door ?? '').toUpperCase()
  const stamp = opts.token?.slice(-6) ?? Date.now().toString(36)
  const cColor = convictionColor(nci)
  const tn = trueNorth.trim()
  const subjLead = tn || question.trim()

  // ── Plain-text fallback ──────────────────────────────────────────────────
  const whyText = why.map((b) => `• ${b}`).join('\n')
  const metaText = [`CONVICTION: ${nci}/100`, mode, door].filter(Boolean).join('  ·  ')
  const text =
`Your compass bearing is locked.

TRUE NORTH
${tn}

WHY
${whyText}

${metaText}

Cartography brief →
${briefUrl}

—
ARCS Field OS · render through the fog to earned clarity`

  // ── HTML ─────────────────────────────────────────────────────────────────
  const whyRows = why.map((b) => `
    <tr>
      <td valign="top" style="font-family:${C.sans};font-size:14px;line-height:1.6;color:${C.cyan};padding:0 8px 0 0;">•</td>
      <td valign="top" style="font-family:${C.sans};font-size:14px;line-height:1.6;color:${C.body};padding:0 0 10px 0;">${escapeHtml(b)}</td>
    </tr>`).join('')

  const metaCells = [
    `<td valign="top" style="padding:0 20px 0 0;">
       <div style="font-family:${C.mono};font-size:9px;letter-spacing:1.6px;text-transform:uppercase;color:${C.muted};padding:0 0 5px 0;">Conviction</div>
       <div style="font-family:${C.mono};font-size:15px;font-weight:700;color:${cColor};">${nci}<span style="color:${C.muted};font-weight:400;">/100</span></div>
     </td>`,
    mode ? `<td valign="top" style="padding:0 20px 0 0;">
       <div style="font-family:${C.mono};font-size:9px;letter-spacing:1.6px;text-transform:uppercase;color:${C.muted};padding:0 0 5px 0;">Mode</div>
       <div style="font-family:${C.mono};font-size:13px;font-weight:700;color:${C.body};">${escapeHtml(mode)}</div>
     </td>` : '',
    door ? `<td valign="top">
       <div style="font-family:${C.mono};font-size:9px;letter-spacing:1.6px;text-transform:uppercase;color:${C.muted};padding:0 0 5px 0;">Door</div>
       <div style="font-family:${C.mono};font-size:13px;font-weight:700;color:${door === 'ONE_WAY' ? C.gold : C.body};">${escapeHtml(door.replace('_', '-'))}</div>
     </td>` : '',
  ].filter(Boolean).join('')

  const html = `<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="dark"><meta name="supported-color-schemes" content="dark"></head>
<body style="margin:0;padding:0;background:${C.bg};">
<div style="display:none;max-height:0;overflow:hidden;mso-hide:all;">Bearing locked · ${escapeHtml(subjLead.slice(0, 48))} · ${stamp}</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:${C.bg};">
  <tr><td align="center" style="padding:32px 16px;">
    <table role="presentation" width="600" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;">

      <tr><td style="padding:0 0 22px 0;font-family:${C.mono};font-size:12px;letter-spacing:2.4px;text-transform:uppercase;font-weight:700;color:${C.cyan};">
        ARCS <span style="color:${C.body};font-weight:400;">FIELD OS</span>
      </td></tr>

      <tr><td style="background:${C.panel};border:1px solid ${C.border};border-radius:16px;padding:34px 32px 28px 32px;">

        <div style="font-family:${C.mono};font-size:11px;letter-spacing:2.4px;text-transform:uppercase;font-weight:700;color:${C.cyan};padding:0 0 16px 0;">
          Compass bearing · locked
        </div>

        <div style="font-family:${C.serif};font-size:30px;line-height:1.16;color:${C.ink};padding:0 0 22px 0;font-weight:400;">
          Your compass bearing<br><em style="color:${C.body};">is locked.</em>
        </div>

        <!-- True North -->
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border-top:1px solid ${C.border};">
          <tr><td style="padding:18px 0 0 0;">
            <div style="font-family:${C.mono};font-size:9px;letter-spacing:1.6px;text-transform:uppercase;color:${C.muted};padding:0 0 7px 0;">True North</div>
            <div style="font-family:${C.serif};font-size:18px;line-height:1.5;color:${C.cyan};">${escapeHtml(tn)}</div>
          </td></tr>
        </table>

        ${why.length ? `<!-- Why -->
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:20px 0 0 0;">
          <tr><td style="padding:0 0 9px 0;font-family:${C.mono};font-size:9px;letter-spacing:1.6px;text-transform:uppercase;color:${C.muted};">Why</td></tr>
          ${whyRows}
        </table>` : ''}

        <!-- Meta strip -->
        <table role="presentation" cellpadding="0" cellspacing="0" style="margin:18px 0 0 0;border-top:1px solid ${C.border};">
          <tr><td style="padding:18px 0 0 0;"><table role="presentation" cellpadding="0" cellspacing="0"><tr>${metaCells}</tr></table></td></tr>
        </table>

        <table role="presentation" cellpadding="0" cellspacing="0" style="margin:26px 0 0 0;"><tr>
          <td style="border-radius:6px;background:${C.cyan};">
            <a href="${briefUrl}" style="display:inline-block;font-family:${C.mono};font-size:12px;letter-spacing:1.1px;text-transform:uppercase;font-weight:700;color:#021016;text-decoration:none;padding:14px 24px;">
              Open cartography brief →
            </a>
          </td>
        </tr></table>

        <div style="border-top:1px solid ${C.border};margin:26px 0 0 0;padding:14px 0 0 0;font-family:${C.serif};font-style:italic;font-size:14px;color:${C.muted};">
          Render through the fog to earned clarity.
        </div>

      </td></tr>

      <tr><td style="padding:16px 4px 0 4px;font-family:${C.mono};font-size:10px;letter-spacing:0.6px;color:#334155;">
        arcs.care · <a href="https://app.arcs.care/unsubscribe" style="color:#334155;text-decoration:underline;">unsubscribe</a>
      </td></tr>

    </table>
  </td></tr>
</table>
</body></html>`

  return {
    subject: `Receipt: ${subjLead.slice(0, 80)}`,
    text,
    html,
  }
}
