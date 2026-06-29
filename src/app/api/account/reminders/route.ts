import { NextRequest, NextResponse } from "next/server"
import { prisma } from "@/lib/db"

// One-click opt-in/opt-out for debrief reminders, clicked straight out of an
// email (no session required — magic-link users aren't reliably logged in on
// the device that opens the email). Toggling User.debriefOptIn is a
// non-destructive preference flip, not a sensitive action, so a bare uid in
// the URL is an acceptable tradeoff here (same trust posture as the existing
// debriefUrl/receiptId links elsewhere in this app — see ADR-001).
export async function GET(req: NextRequest) {
  const uid = req.nextUrl.searchParams.get("uid")
  const action = req.nextUrl.searchParams.get("action")

  if (!uid || (action !== "opt-in" && action !== "opt-out")) {
    return NextResponse.json({ error: "missing or invalid uid/action" }, { status: 400 })
  }

  const debriefOptIn = action === "opt-in"
  try {
    await prisma.user.update({ where: { id: uid }, data: { debriefOptIn } })
  } catch {
    // Unknown uid — still show a neutral confirmation rather than leaking
    // whether the id exists.
  }

  const heading = debriefOptIn ? "Reminders turned on" : "Reminders turned off"
  const body = debriefOptIn
    ? "You'll get a debrief email for future receipts too, not just the first one."
    : "You won't get any more debrief check-in emails unless you turn them back on."

  return new NextResponse(
    `<!DOCTYPE html><html><head><meta charset="utf-8"><title>${heading}</title></head>
<body style="background:#020408;color:#e2e8f0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0;">
  <div style="max-width:420px;padding:32px;border:1px solid #1e293b;border-radius:12px;background:#0d1117;">
    <p style="font-family:'JetBrains Mono',monospace;font-size:10px;letter-spacing:2px;text-transform:uppercase;color:#00F0FF;margin:0 0 16px;">ARCS FIELD OS</p>
    <h1 style="font-size:22px;margin:0 0 12px;">${heading}</h1>
    <p style="font-size:15px;line-height:1.6;color:#94a3b8;margin:0;">${body}</p>
  </div>
</body></html>`,
    { headers: { "Content-Type": "text/html; charset=utf-8" } }
  )
}
