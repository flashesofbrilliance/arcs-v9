"use client"

import { useRouter } from "next/navigation"
import { surface, text, signal, font, contentContainer } from "@/ui/tokens"
import { useVw } from "@/ui/useVw"
import { Wordmark } from "@/ui/Wordmark"
import { Rule } from "@/ui/Rule"
import { SectionLabel } from "@/ui/SectionLabel"
import { Card } from "@/ui/Card"
import { Badge } from "@/ui/Badge"
import { Button } from "@/ui/Button"
import { AuthControl } from "@/molecules/AuthControl"

export interface ReportListItem {
  id: string
  title: string
  subtitle: string
  date: string | null
  badges: string[]
  kind: string
}

// kind → tint, so the ledger reads at a glance (pre-call vs recoil vs fixture).
const kindColor: Record<string, string> = {
  RECOIL: signal.cyan,
  "PRE-CALL": signal.gold,
  PILOT: signal.violet,
  DEMO: signal.steel,
}

function fmtDate(d: string | null): string {
  if (!d) return "—"
  // Bare YYYY-MM-DD parses as UTC midnight, which renders as the prior day in
  // any timezone behind UTC (e.g. EDT). Pin the parts to local time instead.
  const ymd = d.match(/^(\d{4})-(\d{2})-(\d{2})/)
  const parsed = ymd
    ? new Date(Number(ymd[1]), Number(ymd[2]) - 1, Number(ymd[3]))
    : new Date(d)
  return isNaN(parsed.getTime()) ? d : parsed.toLocaleDateString()
}

export function RecoilIndex({ reports }: { reports: ReportListItem[] }) {
  const router = useRouter()
  const vw = useVw()

  return (
    <main style={{ minHeight: "100vh", background: surface.bg, color: text.primary }}>
      <div style={{ ...contentContainer(vw), paddingTop: "2rem", paddingBottom: "6rem" }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", paddingBottom: "1rem" }}>
          <Wordmark section="Recoil" />
          <div style={{ display: "flex", alignItems: "center", gap: "0.25rem" }}>
            <Button variant="ghost" size="sm" glyph="▤" onClick={() => router.push("/history")}>Ledger</Button>
            <AuthControl next="/recoil" />
          </div>
        </div>
        <Rule style={{ marginBottom: "2rem" }} />

        <SectionLabel style={{ marginBottom: "1.25rem" }}>Recoil reports · call cartography · internal</SectionLabel>

        {reports.length === 0 && (
          <div style={{ fontFamily: font.sans, fontSize: "0.9rem", color: text.dimmed, lineHeight: 1.6 }}>
            No recoil reports yet. They land here once <span style={{ color: signal.cyan }}>/recoil-report</span> writes to runtime/recoil/generated/.
          </div>
        )}

        <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
          {reports.map((r) => {
            const c = kindColor[r.kind] ?? signal.steel
            return (
              <Card
                key={r.id}
                style={{ padding: "1rem 1.25rem 1rem 1rem", borderLeft: `2px solid ${c}`, cursor: "pointer" }}
                onClick={() => router.push(`/recoil/${r.id}`)}
              >
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: "1rem", marginBottom: "0.6rem" }}>
                  <Badge label={r.kind} color={c} register="light" />
                  <span style={{ fontFamily: font.mono, fontSize: "0.7rem", color: text.muted }}>{fmtDate(r.date)}</span>
                </div>
                <div style={{ fontFamily: font.sans, fontSize: "0.9rem", fontWeight: 600, color: text.primary, lineHeight: 1.4, marginBottom: r.subtitle ? "0.35rem" : "0.6rem" }}>
                  {r.title}
                </div>
                {r.subtitle && (
                  <div style={{ fontFamily: font.sans, fontSize: "0.8rem", color: text.secondary, lineHeight: 1.5, marginBottom: "0.7rem" }}>
                    {r.subtitle}
                  </div>
                )}
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: "0.75rem", flexWrap: "wrap" }}>
                  <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", alignItems: "center" }}>
                    {r.badges.map((b) => (
                      <Badge key={b} label={b} color={text.muted} register="light" />
                    ))}
                    <span style={{ fontFamily: font.mono, fontSize: "0.62rem", color: text.dimmed, letterSpacing: "0.06em" }}>{r.id}</span>
                  </div>
                  <Button variant="ghost" size="sm" onClick={(e) => { e.stopPropagation(); router.push(`/recoil/${r.id}`) }}>Open →</Button>
                </div>
              </Card>
            )
          })}
        </div>
      </div>
    </main>
  )
}
