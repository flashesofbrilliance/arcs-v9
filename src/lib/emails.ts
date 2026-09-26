// ARCS branded HTML email templates.
// Table-based layout, all inline styles — safe across Gmail, Outlook, Apple Mail.
// Text fallbacks are included in every send via `text` field.

const BG = "#020408"
const SURFACE = "#0d1117"
const BORDER = "#1e293b"
const TEXT = "#e2e8f0"
const MUTED = "#475569"
const DIMMED = "#334155"
const CYAN = "#00F0FF"
const GOLD = "#FFD700"
const MONO = "ui-monospace, 'Cascadia Code', 'Source Code Pro', Menlo, Consolas, monospace"
const SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"

function shell(bodyContent: string): string {
  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<meta name="color-scheme" content="dark" />
<title>ARCS</title>
</head>
<body style="margin:0;padding:0;background-color:${BG};-webkit-text-size-adjust:100%;mso-line-height-rule:exactly;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:${BG};min-height:100vh;">
  <tr>
    <td align="center" style="padding:40px 16px 60px;">
      <table role="presentation" width="100%" style="max-width:560px;">

        <!-- Wordmark -->
        <tr>
          <td style="padding-bottom:20px;">
            <table role="presentation" cellpadding="0" cellspacing="0">
              <tr>
                <td style="font-family:${MONO};font-size:11px;letter-spacing:0.12em;color:${CYAN};font-weight:700;text-transform:uppercase;">ARCS</td>
                <td style="padding:0 8px;color:${DIMMED};font-family:${MONO};font-size:10px;">|</td>
                <td style="font-family:${MONO};font-size:10px;letter-spacing:0.1em;color:${MUTED};text-transform:uppercase;">FIELD OS</td>
              </tr>
            </table>
          </td>
        </tr>

        <!-- Rule -->
        <tr>
          <td style="padding-bottom:28px;">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
              <tr><td height="1" style="background-color:${BORDER};font-size:0;line-height:0;">&nbsp;</td></tr>
            </table>
          </td>
        </tr>

        ${bodyContent}

        <!-- Footer rule -->
        <tr>
          <td style="padding-top:36px;padding-bottom:20px;">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
              <tr><td height="1" style="background-color:${BORDER};font-size:0;line-height:0;">&nbsp;</td></tr>
            </table>
          </td>
        </tr>

        <!-- Footer -->
        <tr>
          <td style="font-family:${MONO};font-size:10px;letter-spacing:0.08em;color:${DIMMED};text-transform:uppercase;line-height:1.8;">
            ARCS · arcs.care<br />
            You're receiving this because you signed up at arcs.care.
          </td>
        </tr>

      </table>
    </td>
  </tr>
</table>
</body>
</html>`
}

export function waitlistEmail(bookingUrl: string | null): string {
  const bookingBlock = bookingUrl ? `
        <!-- CTA -->
        <tr>
          <td style="padding-top:28px;">
            <table role="presentation" cellpadding="0" cellspacing="0">
              <tr>
                <td style="background-color:rgba(0,240,255,0.08);border:1px solid rgba(0,240,255,0.25);border-radius:4px;">
                  <a href="${bookingUrl}" style="display:inline-block;font-family:${MONO};font-size:11px;letter-spacing:0.1em;color:${CYAN};text-transform:uppercase;text-decoration:none;padding:10px 18px;">Book a 30-min session &nbsp;→</a>
                </td>
              </tr>
            </table>
          </td>
        </tr>
        <tr>
          <td style="padding-top:14px;font-family:${SANS};font-size:12px;color:${MUTED};line-height:1.6;">
            One session. No commitment. We'll map the terrain together.
          </td>
        </tr>` : ""

  return shell(`
        <!-- Section label -->
        <tr>
          <td style="padding-bottom:12px;">
            <span style="font-family:${MONO};font-size:10px;letter-spacing:0.12em;color:${GOLD};text-transform:uppercase;font-weight:700;">Waitlist confirmed</span>
          </td>
        </tr>

        <!-- Headline -->
        <tr>
          <td style="padding-bottom:20px;">
            <h1 style="margin:0;font-family:${SANS};font-size:24px;font-weight:600;color:${TEXT};line-height:1.25;letter-spacing:-0.02em;">
              You're on the list.
            </h1>
          </td>
        </tr>

        <!-- Body copy -->
        <tr>
          <td style="font-family:${SANS};font-size:15px;color:#94a3b8;line-height:1.7;">
            We'll reach out as full-service access opens. In the meantime, the compass is live. You can run it anytime at <a href="https://arcs.care" style="color:${CYAN};text-decoration:none;">arcs.care</a>.
          </td>
        </tr>

        <!-- Instrument card -->
        <tr>
          <td style="padding-top:28px;padding-bottom:4px;">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:${SURFACE};border:1px solid ${BORDER};border-radius:6px;">
              <tr>
                <td style="padding:20px 24px;">
                  <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
                    <tr>
                      <td style="padding-bottom:14px;">
                        <span style="font-family:${MONO};font-size:9px;letter-spacing:0.14em;color:${MUTED};text-transform:uppercase;">What ARCS does</span>
                      </td>
                    </tr>
                    <tr>
                      <td style="padding-bottom:10px;border-bottom:1px solid ${BORDER};">
                        <table role="presentation" cellpadding="0" cellspacing="0">
                          <tr>
                            <td style="padding-right:10px;font-family:${MONO};font-size:10px;color:${CYAN};letter-spacing:0.08em;text-transform:uppercase;white-space:nowrap;">01</td>
                            <td style="font-family:${SANS};font-size:13px;color:#94a3b8;line-height:1.55;">Names the real fork, not the symptom you brought in</td>
                          </tr>
                        </table>
                      </td>
                    </tr>
                    <tr><td style="height:10px;"></td></tr>
                    <tr>
                      <td style="padding-bottom:10px;border-bottom:1px solid ${BORDER};">
                        <table role="presentation" cellpadding="0" cellspacing="0">
                          <tr>
                            <td style="padding-right:10px;font-family:${MONO};font-size:10px;color:${CYAN};letter-spacing:0.08em;text-transform:uppercase;white-space:nowrap;">02</td>
                            <td style="font-family:${SANS};font-size:13px;color:#94a3b8;line-height:1.55;">Stress-tests it: strongest case against your instinct, hidden constraints, ruin risk</td>
                          </tr>
                        </table>
                      </td>
                    </tr>
                    <tr><td style="height:10px;"></td></tr>
                    <tr>
                      <td>
                        <table role="presentation" cellpadding="0" cellspacing="0">
                          <tr>
                            <td style="padding-right:10px;font-family:${MONO};font-size:10px;color:${CYAN};letter-spacing:0.08em;text-transform:uppercase;white-space:nowrap;">03</td>
                            <td style="font-family:${SANS};font-size:13px;color:#94a3b8;line-height:1.55;">Returns one clear direction, graded by conviction, with the full map</td>
                          </tr>
                        </table>
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>
            </table>
          </td>
        </tr>
${bookingBlock}`)
}

export function advisoryEmail(name: string | null, bookingUrl: string | null): string {
  const greeting = name ? `${name.split(" ")[0]},` : "Thanks,"
  const bookingBlock = bookingUrl ? `
        <!-- CTA -->
        <tr>
          <td style="padding-top:28px;">
            <table role="presentation" cellpadding="0" cellspacing="0">
              <tr>
                <td style="background-color:rgba(255,215,0,0.08);border:1px solid rgba(255,215,0,0.3);border-radius:4px;">
                  <a href="${bookingUrl}" style="display:inline-block;font-family:${MONO};font-size:11px;letter-spacing:0.1em;color:${GOLD};text-transform:uppercase;text-decoration:none;padding:10px 18px;">Book your session &nbsp;→</a>
                </td>
              </tr>
            </table>
          </td>
        </tr>
        <tr>
          <td style="padding-top:14px;font-family:${SANS};font-size:12px;color:${MUTED};line-height:1.6;">
            30 minutes. We'll map the format: sprint, session, or something else entirely.
          </td>
        </tr>` : ""

  return shell(`
        <!-- Section label -->
        <tr>
          <td style="padding-bottom:12px;">
            <span style="font-family:${MONO};font-size:10px;letter-spacing:0.12em;color:${GOLD};text-transform:uppercase;font-weight:700;">Advisory request received</span>
          </td>
        </tr>

        <!-- Headline -->
        <tr>
          <td style="padding-bottom:20px;">
            <h1 style="margin:0;font-family:${SANS};font-size:24px;font-weight:600;color:${TEXT};line-height:1.25;letter-spacing:-0.02em;">
              ${greeting} we got it.
            </h1>
          </td>
        </tr>

        <!-- Body copy -->
        <tr>
          <td style="font-family:${SANS};font-size:15px;color:#94a3b8;line-height:1.7;">
            We received your request for an ARCS-powered advisory session. We'll review what you're working on and reach out to figure out the right format: one-day sprint, multi-day workshop, or a focused session.
          </td>
        </tr>
${bookingBlock}`)
}
