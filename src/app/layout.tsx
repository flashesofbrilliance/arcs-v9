import type { Metadata, Viewport } from "next"
import { Inter, Crimson_Pro, JetBrains_Mono } from "next/font/google"
import { Analytics } from "@vercel/analytics/next"
import { SpeedInsights } from "@vercel/speed-insights/next"
import { VercelToolbarToggle } from "@/components/VercelToolbarToggle"
import { ClaimAnonymousReceipts } from "@/components/ClaimAnonymousReceipts"
import { EyebrowToast } from "@/ui/EyebrowToast"
import { StickyFooter } from "@/ui/StickyFooter"
import { Providers } from "./Providers"
import "./globals.css"

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  display: "swap",
})

const crimsonPro = Crimson_Pro({
  variable: "--font-crimson",
  subsets: ["latin"],
  weight: ["400", "600", "700"],
  style: ["normal", "italic"],
  display: "swap",
})

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-mono",
  subsets: ["latin"],
  display: "swap",
})

export const viewport: Viewport = {
  viewportFit: 'cover',
}

export const metadata: Metadata = {
  title: "ARCS — Navigate to clarity",
  description: "Bring ARCS the decision you're carrying. It stress-tests your framing and hands back one clear direction — reasoning, tradeoffs, and what to watch.",
  openGraph: {
    title: "ARCS — Navigate to clarity",
    description: "Bring ARCS the decision you're carrying. It stress-tests your framing and hands back one clear direction — reasoning, tradeoffs, and what to watch.",
    siteName: "ARCS",
  },
  twitter: {
    card: "summary_large_image",
    title: "ARCS — Navigate to clarity",
    description: "Bring ARCS the decision you're carrying. It stress-tests your framing and hands back one clear direction — reasoning, tradeoffs, and what to watch.",
  },
}

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html
      lang="en"
      className={`${inter.variable} ${crimsonPro.variable} ${jetbrainsMono.variable} h-full`}
    >
      <body className="min-h-full flex flex-col bg-obsidian-950 text-ivory-100 antialiased" style={{ overscrollBehavior: "none" }}>
        <Providers>
          <EyebrowToast />
          {children}
          <StickyFooter message="ARCS-powered decision sprints for teams — run by Mañana." maxWidth={960} />
          <ClaimAnonymousReceipts />
          <VercelToolbarToggle />
          <Analytics />
          <SpeedInsights />
        </Providers>
      </body>
    </html>
  )
}
