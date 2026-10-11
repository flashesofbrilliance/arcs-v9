import type { Metadata } from "next"
import { auth } from "@/lib/auth"
import { isAdmin } from "@/lib/admin"
import { HudClient } from "./HudClient"

// arcs.care/hud: the field HUD (src/organisms/Scope.tsx) pinned full screen, no page
// around it. The ziggurat loader is admin only, decided here on the server
// (fail-closed outside development, matching /recoil and /warroom); a viewer who is not
// an admin never receives the loader in the payload at all. The page itself is public
// (surface-gate: open), so the surface catalog does not list it as admin gated.
export const dynamic = "force-dynamic"

export const metadata: Metadata = {
  title: "ARCS · Field HUD",
  description: "The ARCS field, full screen: seven fathoms over the knowledge lattice.",
}

export default async function HudPage() {
  let admin = process.env.NODE_ENV === "development"
  if (!admin) {
    const session = await auth().catch(() => null)
    admin = isAdmin(session)
  }
  return <HudClient admin={admin} />
}
