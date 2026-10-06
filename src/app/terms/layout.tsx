import type { Metadata } from "next"

// Route title only; the page itself is a client component and cannot export metadata.
export const metadata: Metadata = { title: "Terms of Service" }

export default function Layout({ children }: { children: React.ReactNode }) {
  return children
}
