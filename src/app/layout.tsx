import type { Metadata } from "next"
import { Inter, Crimson_Pro, JetBrains_Mono } from "next/font/google"
import { Analytics } from "@vercel/analytics/next"
import { VercelToolbarToggle } from "@/components/VercelToolbarToggle"
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
      className={`${inter.variable} ${crimsonPro.variable} ${jetbrainsMono.variable} h-full`}
    >
      <body className="min-h-full flex flex-col bg-obsidian-950 text-ivory-100 antialiased">
        {children}
        <VercelToolbarToggle />
        <Analytics />
      </body>
    </html>
  )
}
