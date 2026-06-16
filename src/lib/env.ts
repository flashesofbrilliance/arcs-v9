export const env = {
  EMAIL_FROM:        process.env.EMAIL_FROM ?? "ARCS <receipts@arcs.so>",
  ANTHROPIC_API_KEY: process.env.ANTHROPIC_API_KEY,
  DATABASE_URL:      process.env.DATABASE_URL ?? "file:./dev.db",
}

// Canonical production origin for all user-facing links (emails, share URLs).
// NEVER fall back to a Vercel preview URL — those rotate and rot. The real
// app lives at app.arcs.care; override only via NEXT_PUBLIC_APP_URL in dev.
export const APP_URL = (process.env.NEXT_PUBLIC_APP_URL ?? "https://app.arcs.care").replace(/\/+$/, "")
