// Print the signed-out payload /recoil/<id> would ship for one public-shares.json entry.
// Imports the real projection from src/lib/recoilPublicShare.ts (Node strips the types),
// so the gate scans what the page serves, not a copy of its logic.
// Usage: node scripts/recoil_public_share_render.mjs <shares.json> <reportId> <report.json> [lib.ts]
// Exit: 0 printed payload; 3 the entry is not a valid share (the page would refuse it).
import fs from "node:fs"
import path from "node:path"
import { pathToFileURL } from "node:url"

const [shares, id, report, lib = "src/lib/recoilPublicShare.ts"] = process.argv.slice(2)
const mod = await import(pathToFileURL(path.resolve(lib)).href)
const entry = JSON.parse(fs.readFileSync(shares, "utf-8"))[id]
const share = mod.validShare ? mod.validShare(entry) : entry
if (!share) process.exit(3)
const data = JSON.parse(fs.readFileSync(report, "utf-8"))
if (data.meta && typeof data.meta === "object") delete data.meta.gate // loadReport strips passcodes first
process.stdout.write(JSON.stringify(mod.applyPublicShare(data, share)))
