"use client"

import { useSearchParams } from "next/navigation"
import { Landing } from "@/organisms/Landing"

// useSearchParams needs a client boundary under Suspense (see page.tsx).
export function WaitlistClient() {
  const receiptId = useSearchParams().get("receipt") || undefined
  return <Landing variant="waitlist" receiptId={receiptId} />
}
