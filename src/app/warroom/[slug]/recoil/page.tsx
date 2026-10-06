import { notFound, redirect } from "next/navigation"
import fs from "node:fs"
import path from "node:path"
import { auth } from "@/lib/auth"
import { isAdmin } from "@/lib/admin"
import { RecoilReportFromData, type RecoilReportRaw } from "@/document/screens/RecoilReport"
import { warroomToRecoilReport, type WarroomAudience } from "@/document/adapters/warroomToRecoilReport"

// War-room SSOT rendered through the RecoilReport screen. The sibling
// route.ts serves the hand-built HTML at /warroom/<slug>; this page renders
// runtime/recoil/generated/<slug>.json (the 6-tab template) via the pure
// adapter. Only the adapter's output reaches the client component, so the
// gate passcode and untranslated internal nodes never enter the payload.
// ?audience=external previews the counterpart-safe cut (nodes tagged `both`).
export const dynamic = "force-dynamic"

function loadSsot(slug: string): unknown | null {
  const safe = slug.replace(/[^a-zA-Z0-9_-]/g, "")
  const file = path.join(process.cwd(), "runtime", "recoil", "generated", `${safe}.json`)
  if (!fs.existsSync(file)) return null
  try {
    return JSON.parse(fs.readFileSync(file, "utf-8"))
  } catch {
    return null
  }
}

export default async function WarroomRecoilPage({
  params,
  searchParams,
}: {
  params: Promise<{ slug: string }>
  searchParams: Promise<{ audience?: string }>
}) {
  const { slug } = await params
  // Same identity gate as the sibling route.ts: prod fail-closed, dev pass-through.
  if (process.env.NODE_ENV !== "development") {
    const session = await auth()
    if (!session?.user?.email) redirect(`/compass?next=/warroom/${encodeURIComponent(slug)}/recoil`)
    if (!isAdmin(session)) notFound()
  }

  const ssot = loadSsot(slug)
  if (!ssot) notFound()

  const audience: WarroomAudience = (await searchParams).audience === "external" ? "external" : "internal"
  const data = warroomToRecoilReport(ssot, { audience }) as RecoilReportRaw

  return (
    <div style={{ background: "#020408", minHeight: "100vh", padding: "40px 0" }}>
      <div style={{ maxWidth: 760, margin: "0 auto", padding: "0 20px" }}>
        <RecoilReportFromData data={data} />
      </div>
    </div>
  )
}
