import { notFound, redirect } from "next/navigation"
import fs from "node:fs"
import path from "node:path"
import { auth } from "@/lib/auth"
import { isAdmin } from "@/lib/admin"
import { RecoilIndex, type ReportListItem } from "./RecoilIndex"

// Recoil index — the "history as index" ledger for recoil reports, mirroring
// /history but sourced from the filesystem rather than Prisma. Reports are the
// JSONs the /recoil-report skill writes to runtime/recoil/generated/<id>.json;
// this page enumerates them and links each to the existing /recoil/[reportId]
// renderer. Internal surface (see src/lib/admin.ts): behind the recoil_session
// cookie gate (src/proxy.ts) AND an admin identity check.
export const dynamic = "force-dynamic"

const GENERATED_DIR = path.join(process.cwd(), "runtime", "recoil", "generated")
const DATE_RE = /(\d{4}-\d{2}-\d{2})/

function humanize(id: string): string {
  return id.replace(DATE_RE, "").replace(/^[-_]+|[-_]+$/g, "").replace(/[-_]+/g, " ").trim() || id
}

function classify(id: string): string {
  if (id === "demo") return "DEMO"
  if (id.startsWith("precall-")) return "PRE-CALL"
  if (id.startsWith("pilot-")) return "PILOT"
  return "RECOIL"
}

function listReports(): ReportListItem[] {
  let files: string[] = []
  try {
    files = fs.readdirSync(GENERATED_DIR).filter((f) => f.endsWith(".json"))
  } catch {
    return []
  }

  const items: ReportListItem[] = files.map((f) => {
    const id = f.replace(/\.json$/, "")
    const embeddedDate = id.match(DATE_RE)?.[1] ?? null
    try {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const d = JSON.parse(fs.readFileSync(path.join(GENERATED_DIR, f), "utf-8")) as any
      return {
        id,
        title: d?.cover?.title ?? d?.meta?.callTitle ?? humanize(id),
        subtitle: d?.cover?.subtitle ?? d?.meta?.counterpart ?? d?.meta?.counterpartRole ?? "",
        date: d?.meta?.callDate ?? embeddedDate,
        badges: Array.isArray(d?.cover?.badges) ? d.cover.badges.slice(0, 2) : [],
        kind: classify(id),
      }
    } catch {
      return { id, title: humanize(id), subtitle: "", date: embeddedDate, badges: [], kind: classify(id) }
    }
  })

  // Newest first; fall back to filename when a report carries no date.
  return items.sort(
    (a, b) => (b.date ?? "").localeCompare(a.date ?? "") || b.id.localeCompare(a.id),
  )
}

export default async function RecoilIndexPage() {
  // ADR-001 doctrine: prod enforces identity, dev passes through. A signed-in
  // non-admin gets a 404 (don't reveal the surface exists); no session → sign in.
  if (process.env.NODE_ENV === "production") {
    const session = await auth()
    if (!session?.user?.email) redirect("/compass?next=/recoil")
    if (!isAdmin(session)) notFound()
  }

  return <RecoilIndex reports={listReports()} />
}
