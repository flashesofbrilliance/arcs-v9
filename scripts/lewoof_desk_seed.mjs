// Le Woof Desk seed. Turns the ranked accounts sheet (exported as CSV) into SQL for the
// lewoof_accounts table. It PRINTS SQL; it never connects to a database, so a person
// reviews and runs it. The CSV holds contact details, so it is read from a path you pass
// and is never committed: keep it out of the repo.
//
//   node scripts/lewoof_desk_seed.mjs ~/Downloads/lewoof-accounts.csv > /tmp/lewoof-seed.sql
//
// Only the four account sections are seeded (boutiques, pet brands, clean brands, hotels).
// Onramp, hospitality and retail-access rows are research, not accounts to contact.
// ON CONFLICT DO NOTHING means a re-run never overwrites progress Hila has logged.
import { readFileSync } from "node:fs"
import { fileURLToPath } from "node:url"

export const SECTIONS = {
  "Endemic: pet boutique": ["pet-boutique", "B"],
  "Endemic: pet brand": ["pet-brand", "P"],
  "Non-endemic: clean brand": ["clean-brand", "C"],
  "Non-endemic: hotel": ["hotel", "H"],
}

/** Minimal RFC 4180 parser: quoted fields, doubled quotes, commas and newlines inside quotes. */
export function parseCsv(text) {
  const rows = []
  let row = [], field = "", q = false
  for (let i = 0; i < text.length; i++) {
    const c = text[i]
    if (q) {
      if (c === '"') { if (text[i + 1] === '"') { field += '"'; i++ } else q = false }
      else field += c
    } else if (c === '"') q = true
    else if (c === ",") { row.push(field); field = "" }
    else if (c === "\n" || c === "\r") {
      if (c === "\r" && text[i + 1] === "\n") i++
      row.push(field); field = ""
      if (row.some((x) => x !== "")) rows.push(row)
      row = []
    } else field += c
  }
  if (field !== "" || row.length) { row.push(field); if (row.some((x) => x !== "")) rows.push(row) }
  return rows
}

const lit = (v) => (v == null || v === "" ? "NULL" : "'" + String(v).replace(/'/g, "''") + "'")

/** Rows -> INSERT statements. Phone numbers shown in the sheet are already do-not-call filtered. */
export function toSql(rows) {
  const [head, ...body] = rows
  const ix = Object.fromEntries(head.map((h, i) => [h.trim(), i]))
  const get = (r, k) => (r[ix[k]] ?? "").trim()
  const out = []
  for (const r of body) {
    const sec = SECTIONS[get(r, "Section")]
    if (!sec) continue
    const rank = Number(get(r, "Rank")) || 0
    const id = `LW-${sec[1]}-${String(rank).padStart(3, "0")}`
    const email = get(r, "Email (ZoomInfo)")
    const cols = {
      id, section: sec[0], rank, name: get(r, "Account"),
      website: get(r, "Website"), contactPage: get(r, "Public contact page"), flags: get(r, "Flags (stores / channels)"),
      score: Number(get(r, "Score")) || 0, contactName: get(r, "Contact"), contactTitle: get(r, "Title"),
      email, emailSource: email ? get(r, "Source") : "", phone: get(r, "Phone"), phoneNote: get(r, "Phone note"),
      notes: get(r, "Notes"),
    }
    const keys = Object.keys(cols)
    const vals = keys.map((k) => (typeof cols[k] === "number" ? String(cols[k]) : lit(cols[k])))
    out.push(`INSERT INTO "lewoof_accounts" (${keys.map((k) => `"${k}"`).join(", ")}, "updatedAt") VALUES (${vals.join(", ")}, now()) ON CONFLICT ("id") DO NOTHING;`)
  }
  return out
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const path = process.argv[2]
  if (!path) { console.error("usage: node scripts/lewoof_desk_seed.mjs <accounts.csv>"); process.exit(2) }
  const sql = toSql(parseCsv(readFileSync(path, "utf8")))
  console.log("-- Le Woof Desk seed. Review before running. Safe to re-run (ON CONFLICT DO NOTHING).")
  console.log("BEGIN;"); sql.forEach((s) => console.log(s)); console.log("COMMIT;")
  console.error(`${sql.length} account rows`)
}
