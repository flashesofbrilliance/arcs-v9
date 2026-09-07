import { redirect } from "next/navigation"
import { pageViewerAllowed } from "@/lib/jobs"
import { JobsBoard } from "./JobsBoard"

// jobs.arcs.care — the Alert Swipe Board as a real product surface, backed by
// Prisma (JobOpportunity / JobSwipe / ForgeRun / JobBoardSetting). Internal,
// single-user: admin session required in production (src/lib/admin.ts); dev
// passes through. Data comes from /api/jobs; writes go to /api/jobs/*.
export const dynamic = "force-dynamic"

export const metadata = { title: "Alert Swipe Board", robots: { index: false, follow: false } }

export default async function JobsPage() {
  const ok = await pageViewerAllowed()
  if (!ok) redirect("/compass?next=/jobs")
  return <JobsBoard />
}
