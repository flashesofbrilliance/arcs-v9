import type { Metadata } from "next"
import { Suspense } from "react"
import { surface } from "@/ui/tokens"
import { WaitlistClient } from "./WaitlistClient"

// /waitlist: public capture for full-service ARCS. Server shell for metadata;
// the form and the terrain live in WaitlistClient. Writes go to POST /api/lead
// (Lead table, source "waitlist"). Review at /admin/leads.
const TITLE = "ARCS waitlist"
const DESCRIPTION = "Every hard decision starts in fog. The ARCS compass is open now; join the waitlist for full-service access."

export const metadata: Metadata = {
  title: TITLE,
  description: DESCRIPTION,
  openGraph: { title: TITLE, description: DESCRIPTION, siteName: "ARCS" },
  twitter: { card: "summary_large_image", title: TITLE, description: DESCRIPTION },
}

export default function WaitlistPage() {
  return (
    <Suspense fallback={<main style={{ minHeight: "100vh", background: surface.bg }} />}>
      <WaitlistClient />
    </Suspense>
  )
}
