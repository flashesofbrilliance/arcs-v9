// fc-derisk-events-probe. Written, NOT RUN. Read-only. Needs only FC_NODE_URL (key guard is skipped).
// usage: FC_NODE_URL=http://host:3381 node events-probe.mjs [pages=5] [pageSize=100]
import fs from "node:fs";
import { classifyEvents, EXIT } from "./classify.mjs";
import { checkArgv } from "./guard.mjs";
checkArgv();
const fx = process.argv.indexOf("--fixture");
if (fx > 0) { const v = classifyEvents(JSON.parse(fs.readFileSync(process.argv[fx + 1], "utf8"))); console.log(JSON.stringify(v)); process.exit(EXIT[v.verdict]); }
const base = (process.env.FC_NODE_URL ?? "").replace(/\/$/, "");
if (!base) { console.error("REFUSING: FC_NODE_URL not set"); process.exit(2); }
const pages = Number(process.argv[2] ?? 5), pageSize = Number(process.argv[3] ?? 100);
const CURSOR = process.env.FC_CURSOR_FILE ?? "./events-cursor.json";
const get = async (shard, from) => {
  const u = `${base}/v1/events?shard_index=${shard}&from_event_id=${from}&pageSize=${pageSize}`;
  const r = await fetch(u); if (!r.ok) throw new Error(`${r.status} ${u}`); return r.json();
};
const idOf = (e) => Number(e.id ?? e.event_id ?? e.eventId);
const typeOf = (e) => e.type ?? e.event_type ?? e.eventType ?? JSON.stringify(Object.keys(e)).slice(0, 40);
const msgTypeOf = (e) => e.message?.data?.type ?? e.mergeMessageBody?.message?.data?.type ?? e.body?.message?.data?.type ?? null;

async function run(shard, from) {
  const seen = [], pages_ = [], types = {}, msgTypes = {};
  let cur = from;
  for (let p = 0; p < pages; p++) {
    const j = await get(shard, cur);
    const evs = j.events ?? j;
    pages_.push(evs.map(idOf));
    if (!evs.length) break;
    for (const e of evs) { seen.push(idOf(e)); types[typeOf(e)] = (types[typeOf(e)] ?? 0) + 1; const m = msgTypeOf(e); if (m) msgTypes[m] = (msgTypes[m] ?? 0) + 1; }
    cur = Math.max(...evs.map(idOf)) + 1;
  }
  return { seen, pages: pages_, types, msgTypes, next: cur };
}
const saved = fs.existsSync(CURSOR) ? JSON.parse(fs.readFileSync(CURSOR, "utf8")) : {};
const report = {};
for (const shard of [0, 1, 2]) {
  const start = saved[shard]?.next ?? 0;
  const a = await run(shard, start);
  const b = await run(shard, a.next);           // "restart" from the saved cursor
  const ids = [...a.seen, ...b.seen];
  const dups = ids.length - new Set(ids).size;
  let gaps = 0; for (let i = 1; i < ids.length; i++) if (ids[i] > ids[i - 1] + 1) gaps += ids[i] - ids[i - 1] - 1;
  (globalThis.obsShards ??= {})[shard] = { pages: [...a.pages, ...b.pages] };
  report[shard] = { start, firstRun: a.seen.length, afterRestart: b.seen.length, duplicates: dups, gapIds: gaps, eventTypes: { ...a.types }, messageTypes: { ...a.msgTypes, ...b.msgTypes } };
  saved[shard] = { next: b.next };
}
fs.writeFileSync(CURSOR, JSON.stringify(saved));
console.log(JSON.stringify(report, null, 1));
const need = ["MESSAGE_TYPE_CAST_ADD", "MESSAGE_TYPE_LINK_ADD", "MESSAGE_TYPE_REACTION_ADD"];
const found = new Set(Object.values(report).flatMap((r) => Object.keys(r.messageTypes)));
console.log("required types missing from sample:", need.filter((n) => !found.has(n)));

const v = classifyEvents({ expected_shards: [0, 1, 2], shards: globalThis.obsShards });
console.log(JSON.stringify(v));
process.exit(EXIT[v.verdict]);
