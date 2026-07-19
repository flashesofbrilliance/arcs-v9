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
  title: "ARCS Field OS",
  description: "Navigate to clarity. Make the decision visible.",
  openGraph: {
    title: "ARCS Field OS",
    description: "Navigate to clarity. Make the decision visible.",
    siteName: "ARCS",
  },
  twitter: {
    card: "summary_large_image",
    title: "ARCS Field OS",
    description: "Navigate to clarity. Make the decision visible.",
  },
}

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html
      lang="en"
      // next/font exposes its CSS variables (--font-inter/--font-crimson/--font-mono)
      // only as generated class names — this is the single sanctioned className in
      // the app (SKILL.md Domain #4). Document base styles live in globals.css.
      className={`${inter.variable} ${crimsonPro.variable} ${jetbrainsMono.variable}`}
    >
      <body style={{ overscrollBehavior: "none" }}>
        <Providers>
          <EyebrowToast />
          {children}
          <StickyFooter message="Interested in ARCS powered sprints by Mañana?" maxWidth={960} />
          <ClaimAnonymousReceipts />
          <VercelToolbarToggle />
          {/* Both inject scripts served by Vercel's edge (/_vercel/*) — off
              Vercel (local prod, CI) those URLs 404 on every page. */}
          {process.env.VERCEL ? <Analytics /> : null}
          {process.env.VERCEL ? <SpeedInsights /> : null}
        </Providers>
      </body>
    </html>
  )
}
