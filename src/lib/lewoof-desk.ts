// Le Woof Desk logic (lewoof.arcs.care/desk). Pure functions only, so the rules Hila
// depends on (who is due today, who is never contacted again, when a group passes)
// are unit-tested without a database. The route in src/app/api/lewoof/desk wires these
// to Prisma. Sending stays manual: nothing here sends mail or places a call.
import { z } from "zod"

export const RESULTS = ["strong", "medium", "weak", "no_reply", "order", "opted_out"] as const
export type Result = (typeof RESULTS)[number]
export const KINDS = ["call", "email", "note"] as const

export type DeskAccount = {
  id: string
  section: string
  rank: number
  name: string
  website: string | null
  contactPage: string | null
  flags: string | null
  score: number
  contactName: string | null
  contactTitle: string | null
  email: string | null
  phone: string | null
  phoneNote: string | null
  hook: string | null
  notes: string | null
  stage: string
  touches: number
  lastResult: string | null
  nextTouch: Date | null
}

export const touchSchema = z.object({
  accountId: z.string().min(1).max(64),
  kind: z.enum(KINDS),
  result: z.enum(RESULTS),
  note: z.string().max(500).optional(),
})
export type TouchInput = z.infer<typeof touchSchema>

const DAY = 24 * 60 * 60 * 1000
const startOfDay = (d: Date) => new Date(Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate()))

/** Days until the next touch after a result. Opt-outs and orders are handled separately. */
export function nextTouchDays(result: Result, touches: number): number | null {
  if (result === "opted_out") return null
  if (result === "order") return 42 // reorder nudge about six weeks out
  if (touches >= 7) return 35 // past seven touches: slow monthly check-in, never announced
  if (result === "strong") return 2
  if (result === "medium") return 4
  return result === "no_reply" ? 3 : 7
}

export function nextStage(stage: string, result: Result): string {
  if (result === "opted_out") return "opted_out"
  if (result === "order") return "ordered"
  if (result === "strong") return stage === "ordered" ? "ordered" : "replied"
  if (result === "medium") return stage === "new" ? "touched" : stage
  return stage === "new" ? "touched" : stage
}

export function applyTouch(acct: Pick<DeskAccount, "stage" | "touches">, result: Result, now: Date) {
  const touches = acct.touches + 1
  const days = nextTouchDays(result, touches)
  return {
    touches,
    stage: nextStage(acct.stage, result),
    lastResult: result,
    nextTouch: days === null ? null : new Date(startOfDay(now).getTime() + days * DAY),
  }
}

const DEAD = new Set(["opted_out", "lost"])

export type Task = DeskAccount & { why: string; channel: "email" | "call" | "contact_page" | "none" }

function channelFor(a: DeskAccount): Task["channel"] {
  if (a.email) return "email"
  if (a.phone) return "call"
  if (a.contactPage) return "contact_page"
  return "none"
}

/** Follow-ups that are due, then up to `firstTouchCap` new accounts by score. Opted-out is never listed. */
export function todayList(accounts: DeskAccount[], now: Date, firstTouchCap = 5): Task[] {
  const today = startOfDay(now).getTime()
  const live = accounts.filter((a) => !DEAD.has(a.stage))
  const due = live
    .filter((a) => a.stage !== "new" && a.nextTouch && startOfDay(a.nextTouch).getTime() <= today)
    .sort((a, b) => (a.nextTouch!.getTime() - b.nextTouch!.getTime()) || b.score - a.score)
    .map((a) => ({ ...a, why: "Follow up", channel: channelFor(a) }))
  const fresh = live
    .filter((a) => a.stage === "new" && channelFor(a) !== "none")
    .sort((a, b) => b.score - a.score || a.rank - b.rank)
    .slice(0, firstTouchCap)
    .map((a) => ({ ...a, why: "First touch", channel: channelFor(a) }))
  return [...due, ...fresh]
}

export type GroupRow = {
  section: string
  accounts: number
  contacted: number
  strong: number
  medium: number
  weak: number
  orders: number
  verdict: "needs_more_contacts" | "pass" | "tie" | "fail"
}

/** Pass line fixed in advance: judged only after 20 contacts; 12%+ strong passes, 4% to 12% is a tie. */
export function scorecard(accounts: DeskAccount[], results: { accountId: string; result: string }[]): GroupRow[] {
  const bySection = new Map<string, DeskAccount[]>()
  for (const a of accounts) bySection.set(a.section, [...(bySection.get(a.section) ?? []), a])
  const best = new Map<string, number>() // best result rank per account
  const rank: Record<string, number> = { opted_out: 0, no_reply: 1, weak: 1, medium: 2, strong: 3, order: 4 }
  for (const r of results) best.set(r.accountId, Math.max(best.get(r.accountId) ?? 0, rank[r.result] ?? 0))
  return [...bySection.entries()].map(([section, list]) => {
    const contacted = list.filter((a) => a.touches > 0).length
    const level = (a: DeskAccount) => best.get(a.id) ?? 0
    const strong = list.filter((a) => level(a) >= 3).length
    const medium = list.filter((a) => level(a) === 2).length
    const orders = list.filter((a) => level(a) === 4).length
    const weak = Math.max(contacted - strong - medium, 0)
    let verdict: GroupRow["verdict"] = "needs_more_contacts"
    if (contacted >= 20) {
      const rate = strong / contacted
      verdict = rate >= 0.12 ? "pass" : rate >= 0.04 ? "tie" : "fail"
    }
    return { section, accounts: list.length, contacted, strong, medium, weak, orders, verdict }
  })
}
