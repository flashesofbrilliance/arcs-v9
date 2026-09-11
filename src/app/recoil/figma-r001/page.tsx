import { auth } from "@/lib/auth"
import { isAdmin } from "@/lib/admin"
import { notFound, redirect } from "next/navigation"
import FigmaR001 from "./FigmaR001"

// Server gate for the figma-r001 recoil design demo (the component itself is a
// client component). Same identity gate as /recoil/[reportId]: magic-link via
// /compass, then the ADMIN_EMAILS allowlist. Was previously relying on the
// shared RECOIL_PASSWORD proxy gate, now removed.
export default async function Page() {
  if (process.env.NODE_ENV !== "development") {   // fail-closed: unset/test/preview/staging all gate (matches /warroom)
    const session = await auth()
    if (!session?.user?.email) redirect("/compass?next=/recoil/figma-r001")
    if (!isAdmin(session)) notFound()
  }
  return <FigmaR001 />
}
