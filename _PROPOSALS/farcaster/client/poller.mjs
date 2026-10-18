// Offline poller over recorded fixtures. No signer code, no secrets, no network (I8: nothing key-like in argv or URLs).
// usage: node poller.mjs --fixture-dir <dir> [--cursor <file>] [--hook <script>]
import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";
const argv = process.argv.slice(2);
const ALLOWED = new Set(["--fixture-dir", "--cursor", "--hook"]);
for (let i = 0; i < argv.length; i += 2) {
  if (!ALLOWED.has(argv[i]) || argv[i + 1] === undefined || /0x[0-9a-fA-F]{64}|seed|mnemonic|private/i.test(argv[i + 1])) {
    console.error("REFUSING: unexpected argument (keys and seeds are never accepted in argv)"); process.exit(2);
  }
}
const opt = (k, d) => { const i = argv.indexOf(k); return i >= 0 ? argv[i + 1] : d; };
const dir = opt("--fixture-dir"); const curFile = opt("--cursor", "./cursor.json"); const hook = opt("--hook");
if (!dir) { console.error("usage: poller.mjs --fixture-dir <dir> [--cursor f] [--hook s]"); process.exit(64); }
const cursors = fs.existsSync(curFile) ? JSON.parse(fs.readFileSync(curFile, "utf8")) : {};
const out = [];
for (const sd of fs.readdirSync(dir).filter((d) => d.startsWith("shard")).sort()) {
  const shard = sd.slice(5);
  const pages = fs.readdirSync(path.join(dir, sd)).filter((f) => f.endsWith(".json")).sort();
  let last = cursors[shard]?.lastId ?? -1;
  for (const f of pages) {
    for (const ev of JSON.parse(fs.readFileSync(path.join(dir, sd, f), "utf8")).events ?? []) {
      if (ev.id <= last) continue;                    // saved per-shard cursor: skip anything already seen
      last = ev.id; out.push({ shard, ev });
      if (hook) spawnSync(hook, [], { input: JSON.stringify(ev), encoding: "utf8", stdio: ["pipe", "inherit", "inherit"] });
    }
  }
  cursors[shard] = { lastId: last };
}
fs.writeFileSync(curFile, JSON.stringify(cursors));
console.log(JSON.stringify({ delivered: out.length, cursors }));
