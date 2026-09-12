#!/usr/bin/env node
// forge_cover_factcheck.mjs — mechanical honesty scan for generated cover letters.
// A cover may only carry claims consistent with the bundle résumé + the seed cover. This
// flags every capitalized product / company / tool token in the letter that appears in
// NEITHER the résumé ATS text NOR the seed cover, split by whether it appears in the JD
// (then it is probably a legitimate mention of THEIR stack; still verify it is not phrased
// as his experience) or nowhere (likely fabricated). Judgment stays human; this is the
// tripwire. Usage: node scripts/forge_cover_factcheck.mjs [--seed-cover <md>] [dirs...]
import fs from "node:fs"; import path from "node:path"
const arg = (k, d) => { const i = process.argv.indexOf(k); return i >= 0 ? (process.argv[i + 1] ?? true) : d }
const seedCover = fs.readFileSync(arg("--seed-cover", "_ARTIFACTS/forge-bridge-operator-seed/cover-letter-bridge-seed.md"), "utf8")
const dirs = process.argv.slice(2).filter((a) => !a.startsWith("--") && a !== arg("--seed-cover", null))
const STOP = new Set(["I","A","The","This","That","These","Those","Here","Most","At","In","On","When","What","Where","Which","Who","Why","How","And","But","So","If","Not","No","Yes","Hi","Re","Your","You","We","Our","It","Its","My","Me","Zach","Harris","Happy","One","Two","Three","Four","Five","Ten","First","Second","Then","There","They","Their","Every","Each","For","From","With","Without","Because","After","Before","Over","Under","Between","Across","Into","Out","Up","Down","Now","Today","New","York","City","Team","Hi,","Sincerely","Best","Thanks","Thank","Everything","Nothing","Something","Anything","Both","Either","Neither","Instead","Still","Also","Even","Only","Just","Right","Left","Same","Different","Real","True","Plain","Short","Long","Quiet","Quieter","Senior","Director","Manager","Lead","Head","Product","Operations","Revenue","Systems","Engineer","Analyst","Architect","Strategist","Business","Development","Enablement","Solutions","Platform","Marketplace","AI","LLM","MCP","SEC","FINRA","HIPAA","GDPR","CRM","CDP","KPI","KPIs","API","APIs","SQL","GTM","RevOps","ARCS","Claude","Q1","Q2","Q3","Q4","PhD","BA","US","NYC","EMEA","APAC","OTT","ARR","AUM","CPQ","ERP","SaaS","B2B","B2C","PE","QA","MVP","UX","UI","HR","IT","PM","PMs","SDR","AE","AEs","CS","CSM","CSMs","Deal","Desk","Process","Improvement","Search","Data","Agent","Fleet","Lifecycle","Management","Bits","Builder","Post","Sales","Pre","Channel","Partnerships","Discoverability","Scheduling","Programs","Marketing","Tax","Vendor","Intelligence","Command","Notebooks","Health","Group","Lucie","Member","Coverage","Support","Time","Global","Contractor","Foundations","Insurance","Emerging","Innovation","Commercial","Software","Design","Research","Scientist","Machine","Learning","Associate","Strategy","Enterprise","Transformation","Programs","Add","Roadmap","Draft","Plain","Hook","Short","Cover","Letter"])
const toks = (s) => new Set((s.match(/\b[A-Z][A-Za-z0-9+.-]{1,}\b/g) || []).filter((t) => !STOP.has(t)))
let flagged = 0
for (const d of dirs) {
  const dir = d.startsWith("_ARTIFACTS") ? d : path.join("_ARTIFACTS", d)
  const cover = fs.readdirSync(dir).find((f) => /^cover-.*\.md$/.test(f)); if (!cover) continue
  const letter = fs.readFileSync(path.join(dir, cover), "utf8").split("## Short version")[0]
  const ats = fs.readdirSync(dir).find((f) => /-ats\.txt$/.test(f)); const resume = ats ? fs.readFileSync(path.join(dir, ats), "utf8") : ""
  const jd = fs.existsSync(path.join(dir, "jd-full.txt")) ? fs.readFileSync(path.join(dir, "jd-full.txt"), "utf8") : ""
  const allowed = new Set([...toks(resume), ...toks(seedCover)])
  const company = path.basename(dir).replace(/^forge-/, "").split("-")[0]
  const unknown = [...toks(letter)].filter((t) => !allowed.has(t) && !t.toLowerCase().startsWith(company))
  const inJD = unknown.filter((t) => jd.includes(t)), nowhere = unknown.filter((t) => !jd.includes(t))
  if (unknown.length) flagged++
  console.log(`${path.basename(dir)}\n  in JD only (their stack; check phrasing): ${inJD.join(", ") || "-"}\n  NOWHERE (verify or cut): ${nowhere.join(", ") || "-"}`)
  // sentences that pair an unknown token with a first-person claim verb
  for (const t of unknown) { const m = letter.match(new RegExp(`[^.]*\\b(I|I've|I have|I built|I owned|I ran|I led|my)\\b[^.]*\\b${t.replace(/[.+-]/g, "\\$&")}\\b[^.]*\\.`, "i")); if (m) console.log(`  CLAIM? "${m[0].trim().slice(0, 160)}"`) }
}
console.log(`\n${flagged}/${dirs.length} letters carry tokens outside the résumé + seed vocabulary`)
