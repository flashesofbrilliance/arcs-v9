import type { Metadata } from "next"

// Route title only; the page itself is a client component and cannot export metadata.
// noindex: a share link is meant for the people it was sent to.
export const metadata: Metadata = { title: "Shared brief", robots: { index: false, follow: false }, referrer: "no-referrer" }

export default function Layout({ children }: { children: React.ReactNode }) {
  return children
}
