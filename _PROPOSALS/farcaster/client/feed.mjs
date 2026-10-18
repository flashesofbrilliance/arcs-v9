// Read-only text feed from recorded events. Prints merged casts, newest last. No network, no keys.
import fs from "node:fs";
import path from "node:path";
const dir = process.argv[2];
if (!dir || process.argv.length !== 3) { console.error("usage: feed.mjs <fixture-dir>"); process.exit(64); }
const rows = [];
for (const sd of fs.readdirSync(dir).filter((d) => d.startsWith("shard"))) {
  for (const f of fs.readdirSync(path.join(dir, sd)).filter((x) => x.endsWith(".json"))) {
    for (const ev of JSON.parse(fs.readFileSync(path.join(dir, sd, f), "utf8")).events ?? []) {
      const m = ev.mergeMessageBody?.message?.data;
      if (ev.type === "HUB_EVENT_TYPE_MERGE_MESSAGE" && m?.type === "MESSAGE_TYPE_CAST_ADD") rows.push({ t: m.timestamp, fid: m.fid, text: m.castAddBody?.text ?? "" });
    }
  }
}
rows.sort((a, b) => a.t - b.t).forEach((r) => console.log(`fid ${r.fid}: ${r.text}`));
