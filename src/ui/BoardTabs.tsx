import Link from "next/link"
import { font, signal, text } from "./tokens"

// The two lanes of the board as a tab strip. Roles (postings → jobs.arcs.care) and
// Champions (people from Zach's network → gated). Rendered on both pages so the
// second tab reads as part of one board. Server component: pure links, no state.
const TABS: { href: string; label: string; key: string }[] = [
  { href: "/jobs", label: "Roles", key: "roles" },
  { href: "/jobs/champions", label: "Champions", key: "champions" },
]

export function BoardTabs({ active }: { active: "roles" | "champions" }) {
  const accent = signal.cyan
  return (
    <div role="tablist" aria-label="Board lanes" style={{ display: "flex", gap: 6, padding: "12px 0 0", flexWrap: "wrap" }}>
      {TABS.map((t) => {
        const on = t.key === active
        return (
          <Link key={t.key} href={t.href} role="tab" aria-selected={on} style={{
            display: "inline-flex", alignItems: "center", gap: 7, padding: "8px 15px", borderRadius: 10, textDecoration: "none",
            fontFamily: font.mono, fontSize: 11, fontWeight: 700, letterSpacing: "0.085em", textTransform: "uppercase", whiteSpace: "nowrap",
            color: on ? "#eafcff" : text.dimmed,
            border: `1px solid ${on ? accent + "55" : "#243042"}`,
            background: on
              ? `linear-gradient(160deg, rgba(255,255,255,.06), rgba(255,255,255,.01) 38%, rgba(0,0,0,.18)), linear-gradient(165deg, ${accent}1f, #0a1620)`
              : "linear-gradient(180deg, #0c121a, #0e151e)",
            boxShadow: on
              ? `inset 0 1px 0 ${accent}73, inset 0 -8px 13px -9px ${accent}55, 0 0 11px ${accent}24, 0 4px 12px rgba(0,0,0,.42)`
              : "inset 0 1px 0 rgba(255,255,255,.04), inset 0 2px 4px rgba(0,0,0,.5)",
            transform: on ? "translateY(-1px)" : "none",
          }}>{t.label}</Link>
        )
      })}
    </div>
  )
}
