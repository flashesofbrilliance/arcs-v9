#!/usr/bin/env node
// scripts/sage_efficacy.js — with-SAGE vs without-SAGE decision quality study
//
// Compares Outcome.matched rate and Outcome.regretScore between receipts where
// the SAGE operator pre-screen fired vs receipts where it didn't (unset,
// unreachable, or non-200). Both groups only include receipts that have a
// logged Outcome — there's no "quality" signal until the user has come back
// and recorded what actually happened.
//
// Gated like the existing OPERATOR20/Observatory analyses in this repo
// (ADR-020/023): below MIN_SAMPLE per group, the comparison is statistically
// meaningless and the script says so rather than printing a misleading delta.
//
// Usage: node scripts/sage_efficacy.js [--min-sample=20]

const { Pool } = require("pg")
const fs = require("fs")
const path = require("path")

const MIN_SAMPLE = Number(
  (process.argv.find((a) => a.startsWith("--min-sample=")) || "").split("=")[1] || 20
)

function loadDatabaseUrl() {
  if (process.env.DATABASE_URL) return process.env.DATABASE_URL
  const envPath = path.join(__dirname, "..", ".env.local")
  const content = fs.readFileSync(envPath, "utf8")
  const match = content.match(/DATABASE_URL="([^"]+)"/)
  if (!match) throw new Error("DATABASE_URL not found in .env.local or environment")
  return match[1]
}

function makePool() {
  const url = new URL(loadDatabaseUrl())
  return new Pool({
    host: url.hostname,
    port: Number(url.port) || 6543,
    database: url.pathname.slice(1),
    user: decodeURIComponent(url.username),
    password: decodeURIComponent(url.password),
    ssl: { rejectUnauthorized: false },
  })
}

function summarize(rows) {
  const n = rows.length
  if (n === 0) return { n: 0, matchRate: null, avgRegret: null }
  const matched = rows.filter((r) => r.matched).length
  const avgRegret = rows.reduce((sum, r) => sum + r.regretScore, 0) / n
  return { n, matchRate: matched / n, avgRegret }
}

async function main() {
  const pool = makePool()
  try {
    const { rows } = await pool.query(`
      SELECT
        o.matched,
        o."regretScore",
        COALESCE(st.fired, false) AS sage_fired
      FROM "Outcome" o
      JOIN "Receipt" r ON r.id = o."receiptId"
      LEFT JOIN "SageTrace" st ON st."receiptId" = r.id
    `)

    const withSage = summarize(rows.filter((r) => r.sage_fired))
    const withoutSage = summarize(rows.filter((r) => !r.sage_fired))

    console.log("=== SAGE Efficacy Study ===\n")
    console.log(`With SAGE:    n=${withSage.n}` + (withSage.n > 0
      ? ` | match rate=${(withSage.matchRate * 100).toFixed(1)}% | avg regret=${withSage.avgRegret.toFixed(2)}`
      : ""))
    console.log(`Without SAGE: n=${withoutSage.n}` + (withoutSage.n > 0
      ? ` | match rate=${(withoutSage.matchRate * 100).toFixed(1)}% | avg regret=${withoutSage.avgRegret.toFixed(2)}`
      : ""))
    console.log("")

    if (withSage.n < MIN_SAMPLE || withoutSage.n < MIN_SAMPLE) {
      console.log(
        `GATED: need >=${MIN_SAMPLE} Outcomes in each group to compare (have ${withSage.n} with-SAGE, ${withoutSage.n} without-SAGE).`
      )
      console.log("This is expected pre-launch — re-run once real Outcomes accumulate.")
      return
    }

    const matchDelta = (withSage.matchRate - withoutSage.matchRate) * 100
    const regretDelta = withSage.avgRegret - withoutSage.avgRegret
    console.log(`Match rate delta (with - without): ${matchDelta >= 0 ? "+" : ""}${matchDelta.toFixed(1)}pp`)
    console.log(`Regret delta (with - without):      ${regretDelta >= 0 ? "+" : ""}${regretDelta.toFixed(2)}`)
    console.log("\n(Positive match delta and negative regret delta both favor SAGE.)")
  } finally {
    await pool.end()
  }
}

main().catch((err) => {
  console.error("Efficacy study failed:", err.message)
  process.exit(1)
})
