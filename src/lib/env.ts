export const env = {
  EMAIL_FROM:        process.env.EMAIL_FROM ?? "ARCS <receipts@arcs.so>",
  ANTHROPIC_API_KEY: process.env.ANTHROPIC_API_KEY,
  DATABASE_URL:      process.env.DATABASE_URL ?? "file:./dev.db",
}
