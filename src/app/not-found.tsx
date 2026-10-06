import type { Metadata } from "next"
import { DeadEnd } from "@/molecules/DeadEnd"

// App-wide 404: branded, with a way back (replaces the unbranded framework default).
export const metadata: Metadata = { title: "Not found" }

export default function NotFound() {
  return (
    <DeadEnd
      title="Nothing at this address."
      body="The link may be mistyped, or the page has moved. Your saved receipts are in your ledger."
    />
  )
}
