import { notFound, redirect } from "next/navigation"
import { auth } from "@/lib/auth"
import { prisma } from "@/lib/db"
import { surface, text, signal, font, contentContainer } from "@/ui/tokens"
import { Wordmark } from "@/ui/Wordmark"
import { Rule } from "@/ui/Rule"
import { SectionLabel } from "@/ui/SectionLabel"
import { Card } from "@/ui/Card"
import { Badge } from "@/ui/Badge"

// Internal review surface for the Lead table (waitlist + advisory captures
// from /waitlist and the homepage). Server-rendered, gated to ADMIN_EMAIL —
// no client fetch, no separate auth UI. Previously the only way to see a
// lead was the per-submission email alert (api/lead/route.ts) or querying
// Supabase directly; this is the persistent review surface for history.
export const dynamic = "force-dynamic"

const ADMIN_EMAIL = process.env.ADMIN_EMAIL ?? "zach.harris@gmail.com"

export default async function AdminLeadsPage() {
  const session = await auth()
  if (!session?.user?.email) redirect("/compass?next=/admin/leads")
  if (session.user.email.toLowerCase() !== ADMIN_EMAIL.toLowerCase()) notFound()

  const leads = await prisma.lead.findMany({ orderBy: { createdAt: "desc" } })

  return (
    <main style={{ minHeight: "100vh", background: surface.bg, color: text.primary }}>
      <div style={{ ...contentContainer(0), paddingTop: "2rem", paddingBottom: "6rem", maxWidth: 860 }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", paddingBottom: "1rem" }}>
          <Wordmark section="Leads" />
          <Badge label={`${leads.length} total`} color={signal.cyan} register="light" />
        </div>
        <Rule style={{ marginBottom: "2rem" }} />

        <SectionLabel style={{ marginBottom: "1.25rem" }}>Waitlist + advisory captures</SectionLabel>

        {leads.length === 0 && (
          <div style={{ fontFamily: font.sans, fontSize: "0.9rem", color: text.dimmed }}>No leads yet.</div>
        )}

        <div style={{ display: "flex", flexDirection: "column", gap: "0.6rem" }}>
          {leads.map((l) => {
            const isAdvisory = l.source === "advisory"
            const accent = isAdvisory ? signal.gold : signal.cyan
            return (
              <Card key={l.id} style={{ padding: "0.9rem 1.1rem", borderLeft: `2px solid ${accent}` }}>
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: "0.75rem", marginBottom: l.name || l.message ? "0.5rem" : 0 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "0.6rem", minWidth: 0 }}>
                    <Badge label={isAdvisory ? "Advisory" : "Waitlist"} color={accent} register="light" />
                    <span style={{ fontFamily: font.sans, fontSize: "0.85rem", color: text.primary, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{l.email}</span>
                  </div>
                  <span style={{ fontFamily: font.mono, fontSize: "0.7rem", color: text.muted, flexShrink: 0 }}>
                    {new Date(l.createdAt).toLocaleDateString()} {new Date(l.createdAt).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                  </span>
                </div>
                {l.name && (
                  <div style={{ fontFamily: font.sans, fontSize: "0.8rem", color: text.secondary, marginBottom: l.message ? "0.3rem" : 0 }}>{l.name}</div>
                )}
                {l.message && (
                  <div style={{ fontFamily: font.sans, fontSize: "0.8rem", color: text.dimmed, lineHeight: 1.5 }}>{l.message}</div>
                )}
                {l.receiptId && (
                  <div style={{ marginTop: "0.5rem" }}>
                    <a href={`/brief/${l.receiptId}`} style={{ fontFamily: font.mono, fontSize: "0.7rem", color: signal.cyan, textDecoration: "underline" }}>View linked receipt →</a>
                  </div>
                )}
              </Card>
            )
          })}
        </div>
      </div>
    </main>
  )
}
