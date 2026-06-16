// ARCS welcome email — dependency-free, email-safe (table layout + inline styles,
// solid colors only; no backdrop-filter/blur/background-image so it renders in
// Gmail/Outlook/Apple Mail). Returns { subject, html } so it can be passed to
// Auth.js sendVerificationRequest or any Resend send. Not wired into auth here.
//
// Fonts: custom webfonts don't load reliably in email, so the hero falls back to
// Georgia (serif) and body to a system sans — the cockpit register still reads.

import { darkLockHead } from './darkLock'

export interface WelcomeEmailOpts {
  ctaUrl?: string
  ctaLabel?: string
  // Unique token fragment (last 6 chars of the magic-link token) prevents
  // Gmail from threading and collapsing repeated magic-link emails.
  token?: string
}

const C = {
  bg: '#020408',
  panel: '#0d1117',
  border: '#1e293b',
  cyan: '#00F0FF',
  ink: '#eafcff',
  body: '#94a3b8',
  muted: '#475569',
  serif: "Georgia, 'Times New Roman', serif",
  sans: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif",
  mono: "'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace",
}

export function welcomeEmail(opts: WelcomeEmailOpts = {}): { subject: string; html: string } {
  const ctaUrl = opts.ctaUrl ?? 'https://app.arcs.care/dashboard'
  const ctaLabel = opts.ctaLabel ?? 'Ask your first question →'
  const stamp = opts.token?.slice(-6) ?? Date.now().toString(36)

  const html = `<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="dark"><meta name="supported-color-schemes" content="dark">
${darkLockHead(C)}</head>
<body class="arcs-body" style="margin:0;padding:0;background:${C.bg};">
<div style="display:none;max-height:0;overflow:hidden;mso-hide:all;">${stamp}</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" class="arcs-bg" style="background:${C.bg};">
  <tr><td align="center" style="padding:32px 16px;">
    <table role="presentation" width="600" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;">

      <tr><td style="padding:0 0 22px 0;font-family:${C.mono};font-size:12px;letter-spacing:2.4px;text-transform:uppercase;font-weight:700;color:${C.cyan};">
        <span class="arcs-cyan">ARCS</span> <span class="arcs-body" style="color:${C.body};font-weight:400;">FIELD OS</span>
      </td></tr>

      <tr><td class="arcs-panel" style="background:${C.panel};border:1px solid ${C.border};border-radius:16px;padding:34px 32px 28px 32px;">

        <div class="arcs-cyan" style="font-family:${C.mono};font-size:11px;letter-spacing:2.4px;text-transform:uppercase;font-weight:700;color:${C.cyan};padding:0 0 16px 0;">
          Welcome, navigator
        </div>

        <div class="arcs-ink" style="font-family:${C.serif};font-size:34px;line-height:1.12;color:${C.ink};padding:0 0 16px 0;font-weight:400;">
          The map is blank<br><em class="arcs-body" style="color:${C.body};">until you name</em> the fork.
        </div>

        <div class="arcs-body" style="font-family:${C.sans};font-size:15px;line-height:1.7;color:${C.body};padding:0 0 26px 0;max-width:420px;">
          You're in. Nothing's been decided yet — that's the point. Bring the one decision that won't wait, and the compass renders your first bearing.
        </div>

        <table role="presentation" cellpadding="0" cellspacing="0"><tr>
          <td style="border-radius:6px;background:${C.cyan};">
            <a href="${ctaUrl}" style="display:inline-block;font-family:${C.mono};font-size:12px;letter-spacing:1.1px;text-transform:uppercase;font-weight:700;color:#021016;text-decoration:none;padding:14px 24px;">
              ${ctaLabel}
            </a>
          </td>
        </tr></table>

        <div class="arcs-muted" style="border-top:1px solid ${C.border};margin:26px 0 0 0;padding:14px 0 0 0;font-family:${C.serif};font-style:italic;font-size:14px;color:${C.muted};">
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

  return { subject: `You're in. Navigate to clarity. [${stamp}]`, html }
}
