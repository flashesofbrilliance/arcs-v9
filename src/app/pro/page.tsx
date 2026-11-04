// ARCS Pro: the one paid tier. The Compass stays free; Pro bundles what is already
// built (every brief, full history, follow-up check-ins). Checkout is a Stripe
// Payment Link (STRIPE_PRO_LINK); with no link set the page says so and sells nothing.
import { auth } from "@/lib/auth"
import { prisma } from "@/lib/db"
import { proUrlFor } from "@/lib/paywall"
import { PRO_PRICE } from "@/lib/paywall-copy"
import { surface, text, signal, font, border } from "@/ui/tokens"
import { Wordmark } from "@/ui/Wordmark"
import { ButtonLink } from "@/ui/Button"

export const dynamic = "force-dynamic"

export const metadata = {
  title: "ARCS Pro",
  description: "Every decision brief, your full decision history, and a check-in after each decision. The Compass stays free.",
}

const ROWS: { what: string; free: string; pro: string }[] = [
  { what: "Compass: sharpened question, the people in it, time window, conviction", free: "Yes", pro: "Yes" },
  { what: "Decision brief: situation framing, the people in it, the paths through", free: "One at a time", pro: "Every one" },
  { what: "Decision history", free: "Latest 50", pro: "Up to 500" },
  { what: "Check-in after each decision asks how it went", free: "First one, then opt in", pro: "On from day one" },
  { what: "Delete your data any time", free: "Yes", pro: "Yes" },
]

export default async function ProPage() {
  const session = await auth()
  const userId = session?.user?.id ?? null
  const tier = userId ? (await prisma.user.findUnique({ where: { id: userId }, select: { tier: true } }))?.tier : null
  const isPro = tier === "PRO"
  const checkout = userId ? proUrlFor(userId) : null
  const portal = process.env.STRIPE_PORTAL_LINK ?? null
  const live = !!process.env.STRIPE_PRO_LINK

  const cell: React.CSSProperties = { padding: "0.85rem 0.75rem", borderBottom: `1px solid ${border.subtle}`, verticalAlign: "top" }
  const head: React.CSSProperties = { ...cell, fontFamily: font.mono, fontSize: 12, letterSpacing: "0.08em", textTransform: "uppercase", color: text.muted, textAlign: "left" }

  return (
    <main style={{ minHeight: "100vh", background: "radial-gradient(120% 70% at 50% -5%, #0a1422 0%, #020408 62%)", color: text.primary, fontFamily: font.sans }}>
      <div style={{ maxWidth: 760, margin: "0 auto", padding: "2rem 1rem 4rem" }}>
        <Wordmark section="Pro" />

        <h1 style={{ fontSize: "clamp(1.8rem, 5vw, 2.6rem)", lineHeight: 1.15, margin: "2.5rem 0 1rem", fontWeight: 600 }}>
          See the whole decision before you make it.
        </h1>
        <p style={{ color: text.secondary, lineHeight: 1.65, fontSize: "1.05rem", margin: "0 0 2rem" }}>
          The Compass is free and stays free. Pro is for people who bring it their real decisions: a job offer, a hire, a contract, a move.
          You get the full brief on every one, a record of every decision you have made, and a check-in afterward that asks how it went.
        </p>

        <section style={{ background: surface.panel, border: `1px solid ${border.active}`, borderRadius: 12, padding: "1.5rem", margin: "0 0 2.5rem" }}>
          <div style={{ fontFamily: font.mono, fontSize: 12, letterSpacing: "0.08em", textTransform: "uppercase", color: signal.cyan }}>ARCS Pro</div>
          <div style={{ fontSize: "2rem", fontWeight: 600, margin: "0.5rem 0 0.25rem" }}>{PRO_PRICE}</div>
          <p style={{ color: text.secondary, margin: "0 0 1.25rem", lineHeight: 1.6 }}>Cancel any time. Your receipts and briefs stay yours either way.</p>
          {isPro ? (
            <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap", alignItems: "center" }}>
              <span style={{ color: signal.green, fontFamily: font.mono }}>You are on Pro.</span>
              {portal && <ButtonLink href={portal} variant="ghost">Manage or cancel</ButtonLink>}
            </div>
          ) : !live ? (
            <p style={{ color: text.muted, margin: 0 }}>Pro is not open yet. The Compass is free to use now.</p>
          ) : checkout ? (
            <ButtonLink href={checkout}>Start Pro</ButtonLink>
          ) : (
            <ButtonLink href="/compass?next=/pro">Sign in to start Pro</ButtonLink>
          )}
        </section>

        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.95rem", lineHeight: 1.5 }}>
            <thead>
              <tr><th style={head}>What you get</th><th style={head}>Free</th><th style={{ ...head, color: signal.cyan }}>Pro</th></tr>
            </thead>
            <tbody>
              {ROWS.map((r) => (
                <tr key={r.what}>
                  <td style={cell}>{r.what}</td>
                  <td style={{ ...cell, color: text.secondary }}>{r.free}</td>
                  <td style={{ ...cell, color: text.primary }}>{r.pro}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <h2 style={{ fontSize: "1.25rem", margin: "2.5rem 0 0.75rem", fontWeight: 600 }}>Is it worth it?</h2>
        <p style={{ color: text.secondary, lineHeight: 1.65, margin: "0 0 1rem" }}>
          Do the math with your own numbers. Think of one decision this year where the cost of getting it wrong runs into the thousands: an offer you accept or turn down, a person you hire, a deal you sign.
          If a brief helps you catch one hidden constraint on one of those, Pro has paid for itself many times over. If it does not, cancel.
        </p>
        <p style={{ color: text.secondary, lineHeight: 1.65, margin: 0 }}>
          ARCS never decides for you. It shows the shape of the decision, how solid your conviction is, and where it is hard to undo. The call stays yours.
        </p>

        <p style={{ color: text.muted, fontSize: "0.85rem", margin: "3rem 0 0" }}>
          <a href="/privacy" style={{ color: text.muted }}>Privacy</a> · <a href="/terms" style={{ color: text.muted }}>Terms</a> · <a href="/dashboard" style={{ color: text.muted }}>Open the Compass</a>
        </p>
      </div>
    </main>
  )
}
