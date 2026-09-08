import { redirect } from "next/navigation"
import { pageViewerAllowed } from "@/lib/jobs"
import { ChampionsBoard } from "./ChampionsBoard"

// jobs.arcs.care/champions — the Champions lane: best→worst-fit hiring champions
// from Zach's own LinkedIn network, stack-ranked against the champion-fit rubric.
//
// HARD CONSTRAINT: this surface holds real names + LinkedIn URLs from Zach's private
// network (PII). It is gated the SAME way as the roles board — pageViewerAllowed()
// (admin session in production; dev passes through) — and the data itself is served
// only by the gated /api/champions handler, never from /public or a static file.
export const dynamic = "force-dynamic"

export const metadata = { title: "Champions", robots: { index: false, follow: false } }

export default async function ChampionsPage() {
  const ok = await pageViewerAllowed()
  if (!ok) redirect("/compass?next=/jobs/champions")
  return <ChampionsBoard />
}
