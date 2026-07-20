// ARCS debrief (calibration) email — the §5.6 close-the-loop touchpoint.
//
// A receipt cannot be closed by the session that created it (Book II Part V,
// §5.1). External signal — an outcome — has to arrive after T₀. This email is
// how ARCS convenes that debrief: N days after a call, when the shoe was
// expected to drop, it reflects the original bearing back and asks the only
// question that closes a receipt — "how did it land?"
//
// Email-safe like welcomeEmail.ts: table layout, inline styles, solid colors
// only (no backdrop-filter/blur/background-image), serif/system-font fallbacks.
// Returns { subject, text, html } so the caller can pass either to Resend.

import { darkLockHead } from './darkLock'

export interface DebriefEmailOpts {
  // The sharpened question / decision being debriefed.
  question: string
  // Compass True North at T₀ — the bearing we're checking against reality.
  trueNorth: string
  // Days elapsed between the call and this debrief (the "shoe drop" window).
  daysElapsed: number
  // Conviction (NCI composite, 0–100) recorded at the decision.
  conviction?: number
  // What the navigator said they couldn't afford to lose (prep chips).
  protecting?: string[]
  // CTA target — the brief/receipt surface where the outcome is logged.
  debriefUrl: string
  // Unique fragment (e.g. receipt id tail) — keeps Gmail from threading repeats.
  token?: string
  // True only for a user's first-ever debrief send. The first one is sent
  // unconditionally (the core close-the-loop promise); every later one
  // requires the opt-in click below — progressive disclosure, not an
  // assumed standing subscription. See prisma User.debriefOptIn.
  isFirstDebrief?: boolean
  // One-click link that flips User.debriefOptIn to true. Only rendered when
  // isFirstDebrief is true — there's nothing to opt into on a repeat send,
  // the user already opted in to get it.
  optInUrl?: string
  // One-click link that flips User.debriefOptIn back to false. Only relevant
  // (and only rendered) on a non-first send — that's the only case where the
  // user is actively subscribed to anything.
  optOutUrl?: string
}

const C = {
  bg: '#020408',
  panel: '#0d1117',
  border: '#1e293b',
  cyan: '#00F0FF',
  gold: '#FFD700',
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

// One-row meta cell — label over value, used in the recap strip.
function metaCell(label: string, value: string, valueColor: string, valueClass = ''): string {
  return `<td valign="top" style="padding:0 18px 0 0;">
    <div class="arcs-muted" style="font-family:${C.mono};font-size:9px;letter-spacing:1.6px;text-transform:uppercase;color:${C.muted};padding:0 0 5px 0;">${label}</div>
    <div class="${valueClass}" style="font-family:${C.mono};font-size:13px;font-weight:700;color:${valueColor};">${value}</div>
  </td>`
}

export function debriefEmail(opts: DebriefEmailOpts): { subject: string; text: string; html: string } {
  const { question, trueNorth, daysElapsed, debriefUrl } = opts
  const conviction = typeof opts.conviction === 'number' ? Math.round(opts.conviction) : null
  const protecting = (opts.protecting ?? []).filter(Boolean)
  const stamp = opts.token?.slice(-6) ?? Date.now().toString(36)
  const days = Math.max(1, Math.round(daysElapsed))
  const q = question.trim()
  const qShort = q.length > 60 ? `${q.slice(0, 57)}…` : q
  const showOptIn = Boolean(opts.isFirstDebrief && opts.optInUrl)

  // ── Plain-text fallback (deliverability + non-HTML clients) ──────────────
  const protectingLine = protecting.length ? `\nYOU WERE PROTECTING\n${protecting.join(' · ')}\n` : ''
  const convictionLine = conviction != null ? `  ·  conviction ${conviction}/100` : ''
  const text =
`You made this call ${days}d ago${convictionLine}.

THE QUESTION
${q}

TRUE NORTH (the bearing we set)
${trueNorth}
${protectingLine}
The shoe has dropped. A receipt can't close itself. Only the outcome can.
Did it land where the compass pointed?

Log how it landed →
${debriefUrl}
${showOptIn ? `
This is the only check-in we send without asking first. Want future ones like\nit? Turn on reminders →\n${opts.optInUrl}\n` : ''}
---
ARCS Field OS · render through the fog to earned clarity`

  // ── HTML ─────────────────────────────────────────────────────────────────
  const protectingBlock = protecting.length
    ? `<tr><td style="padding:18px 0 0 0;">
         <div class="arcs-muted" style="font-family:${C.mono};font-size:9px;letter-spacing:1.6px;text-transform:uppercase;color:${C.muted};padding:0 0 7px 0;">You were protecting</div>
         <div class="arcs-gold" style="font-family:${C.mono};font-size:12px;color:${C.gold};letter-spacing:0.4px;">${protecting.map(escapeHtml).join(' &nbsp;·&nbsp; ')}</div>
       </td></tr>`
    : ''

  const convictionCell = conviction != null
    ? metaCell('Conviction', `${conviction}<span class="arcs-muted" style="color:${C.muted};font-weight:400;">/100</span>`, C.cyan, 'arcs-cyan')
    : ''

  const html = `<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="dark"><meta name="supported-color-schemes" content="dark">
${darkLockHead(C)}</head>
<body class="arcs-body" style="margin:0;padding:0;background:${C.bg};">
<div style="display:none;max-height:0;overflow:hidden;mso-hide:all;">How did "${escapeHtml(qShort)}" land? · ${stamp}</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" class="arcs-bg" style="background:${C.bg};">
  <tr><td align="center" style="padding:32px 16px;">
    <table role="presentation" width="600" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;">

      <tr><td style="padding:0 0 22px 0;font-family:${C.mono};font-size:12px;letter-spacing:2.4px;text-transform:uppercase;font-weight:700;color:${C.cyan};">
        <span class="arcs-cyan">ARCS</span> <span class="arcs-body" style="color:${C.body};font-weight:400;">FIELD OS</span>
      </td></tr>

      <tr><td class="arcs-panel" style="background:${C.panel};border:1px solid ${C.border};border-radius:16px;padding:34px 32px 28px 32px;">

        <div class="arcs-gold" style="font-family:${C.mono};font-size:11px;letter-spacing:2.4px;text-transform:uppercase;font-weight:700;color:${C.gold};padding:0 0 16px 0;">
          Debrief · the shoe has dropped
        </div>

        <div class="arcs-ink" style="font-family:${C.serif};font-size:32px;line-height:1.14;color:${C.ink};padding:0 0 14px 0;font-weight:400;">
          You set a bearing ${days} day${days === 1 ? '' : 's'} ago.<br><em class="arcs-body" style="color:${C.body};">Did it land</em> where the compass pointed?
        </div>

        <div class="arcs-body" style="font-family:${C.sans};font-size:15px;line-height:1.7;color:${C.body};padding:0 0 24px 0;max-width:430px;">
          A receipt can't close itself. Only the outcome can. Here's the call you logged. Tell ARCS what actually happened, and the loop closes.
        </div>

        <!-- Recap strip: the original bearing -->
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border-top:1px solid ${C.border};border-bottom:1px solid ${C.border};">
          <tr><td style="padding:18px 0 4px 0;">
            <div class="arcs-muted" style="font-family:${C.mono};font-size:9px;letter-spacing:1.6px;text-transform:uppercase;color:${C.muted};padding:0 0 6px 0;">The question</div>
            <div class="arcs-ink" style="font-family:${C.sans};font-size:15px;line-height:1.5;color:${C.ink};">${escapeHtml(q)}</div>
          </td></tr>
          <tr><td style="padding:16px 0 0 0;">
            <div class="arcs-muted" style="font-family:${C.mono};font-size:9px;letter-spacing:1.6px;text-transform:uppercase;color:${C.muted};padding:0 0 6px 0;">True North · the bearing we set</div>
            <div class="arcs-cyan" style="font-family:${C.serif};font-size:17px;line-height:1.45;color:${C.cyan};">${escapeHtml(trueNorth)}</div>
          </td></tr>
          ${protectingBlock}
          ${convictionCell ? `<tr><td style="padding:18px 0 4px 0;"><table role="presentation" cellpadding="0" cellspacing="0"><tr>${convictionCell}${metaCell('Window since', `${days}d`, C.body, 'arcs-body')}</tr></table></td></tr>` : ''}
        </table>

        <table role="presentation" cellpadding="0" cellspacing="0" style="margin:26px 0 0 0;"><tr>
          <td style="border-radius:6px;background:${C.cyan};">
            <a href="${debriefUrl}" style="display:inline-block;font-family:${C.mono};font-size:12px;letter-spacing:1.1px;text-transform:uppercase;font-weight:700;color:#021016;text-decoration:none;padding:14px 24px;">
              Log how it landed →
            </a>
          </td>
        </tr></table>

        <div class="arcs-muted" style="border-top:1px solid ${C.border};margin:26px 0 0 0;padding:14px 0 0 0;font-family:${C.serif};font-style:italic;font-size:14px;color:${C.muted};">
          On track, drifting, or landed. Name it, and the next call starts from clearer ground.
        </div>

        ${showOptIn ? `<div class="arcs-muted" style="margin:18px 0 0 0;padding:14px 16px;border:1px solid ${C.border};border-radius:10px;font-family:${C.sans};font-size:13px;line-height:1.6;color:${C.muted};">
          This is the only check-in ARCS sends without asking first. Want future ones like it?
          <a href="${opts.optInUrl}" style="color:${C.cyan};text-decoration:underline;">Turn on reminders →</a>
        </div>` : ''}

      </td></tr>

      <tr><td style="padding:16px 4px 0 4px;font-family:${C.mono};font-size:10px;letter-spacing:0.6px;color:#334155;">
        arcs.care · <a href="${opts.optOutUrl ?? 'https://app.arcs.care/unsubscribe'}" style="color:#334155;text-decoration:underline;">${opts.optOutUrl ? 'turn off reminders' : 'unsubscribe'}</a>
      </td></tr>

    </table>
  </td></tr>
</table>
</body></html>`

  return {
    subject: `How did it land? "${qShort}" [${stamp}]`,
    text,
    html,
  }
}
