// fc-derisk-write-path-probe. WRITES to the node it is pointed at (devnet: FC_NETWORK=devnet; mainnet only with Zach's go and a throwaway account).
// Verified API names for @farcaster/core 0.20.0 (read from its type declarations 2026-10-19): makeKeyAddBody, makeKeyAdd, makeCastAdd, getFarcasterTime, NobleEd25519Signer, ViemLocalEip712Signer.
// getGaslessSignedKeyRequestMetadata does NOT exist in 0.20.0 (earlier draft was wrong). Needs: npm i @farcaster/core@0.20.0 viem @noble/curves (use '@noble/curves/ed25519.js'; v2 dropped the extensionless subpath).
import fs from "node:fs";
import crypto from "node:crypto";
import { requireThrowaway, checkArgv } from "./guard.mjs";
import { classifyWrite, EXIT } from "./classify.mjs";
checkArgv();
const fx = process.argv.indexOf("--fixture");
if (fx > 0) { const v = classifyWrite(JSON.parse(fs.readFileSync(process.argv[fx + 1], "utf8"))); console.log(JSON.stringify(v)); process.exit(EXIT[v.verdict]); }
const { nodeUrl, key, fid } = requireThrowaway();
const core = await import("@farcaster/core");
const { privateKeyToAccount } = await import("viem/accounts");
const { ed25519 } = await import("@noble/curves/ed25519.js");
const network = process.env.FC_NETWORK === "devnet" ? core.FarcasterNetwork.DEVNET : core.FarcasterNetwork.MAINNET;
const hex = (u) => "0x" + Buffer.from(u).toString("hex");
const must = (r, w) => { if (r.isErr()) { console.error(`FAIL ${w}: ${String(r.error)}`); process.exit(EXIT.fallback); } return r.value; };
const submit = async (m) => { const r = await fetch(`${nodeUrl}/v1/submitMessage`, { method: "POST", headers: { "content-type": "application/octet-stream" }, body: core.Message.encode(m).finish() }); return { status: r.status, error: r.ok ? undefined : (await r.text()).slice(0, 120) }; };

const info = await (await fetch(`${nodeUrl}/v1/signersByFid?fid=${fid}`)).json();
const priv = crypto.randomBytes(32), pub = ed25519.getPublicKey(priv);
const custody = new core.ViemLocalEip712Signer(privateKeyToAccount(key));
const body = must(await core.makeKeyAddBody({ fid: BigInt(fid), key: pub, scopes: [core.MessageType.CAST_ADD, core.MessageType.REACTION_ADD, core.MessageType.LINK_ADD], ttl: 7 * 24 * 3600, nonce: (info.currentUserNonce ?? 0) + 1, deadline: must(core.getFarcasterTime(), "time") + 600 }, custody), "makeKeyAddBody");
const keyadd = await submit(must(await core.makeKeyAdd(body, { fid, network }, new core.NobleEd25519Signer(priv)), "makeKeyAdd"));
console.log("KEY_ADD status:", keyadd.status);
// KEY_ADD is asynchronous: 200 means accepted, not merged. A cast signed before the key is merged is rejected ("signer not authorized"; observed on devnet 2026-10-19).
let keyMergedAfterS = null; const tk = Date.now();
for (let i = 0; i < 15 && keyadd.status === 200 && keyMergedAfterS === null; i++) {
  const sg = await (await fetch(`${nodeUrl}/v1/signersByFid?fid=${fid}`)).json();
  if ((sg.signers ?? []).some((x) => x.key === hex(pub))) keyMergedAfterS = Math.round((Date.now() - tk) / 1000); else await new Promise((r) => setTimeout(r, 2000));
}
console.log("key visible in signersByFid after (s):", keyMergedAfterS);
const cast = must(await core.makeCastAdd({ text: `probe ${new Date().toISOString()}`, embeds: [], embedsDeprecated: [], mentions: [], mentionsPositions: [] }, { fid, network }, new core.NobleEd25519Signer(priv)), "makeCastAdd");
const castRes = keyadd.status === 200 ? await submit(cast) : { status: 0 };
const h = hex(cast.hash);
let readback = false, mergeEvent = false;
for (let i = 0; i < 12 && !(readback && mergeEvent); i++) {
  await new Promise((r) => setTimeout(r, 5000));
  readback = readback || (await fetch(`${nodeUrl}/v1/castById?fid=${fid}&hash=${h}`)).ok;
  for (const sh of [1, 2]) {
    const r = await fetch(`${nodeUrl}/v1/events?shard_index=${sh}&reverse=true&pageSize=300`);
    if (r.ok) mergeEvent = mergeEvent || JSON.stringify((await r.json()).events ?? []).includes(h);
  }
  console.log(`poll ${i}: readback=${readback} mergeEvent=${mergeEvent}`);
}
const v = classifyWrite({ keyadd, cast: castRes, readback, merge_event: mergeEvent });
console.log(JSON.stringify(v));
process.exit(EXIT[v.verdict]);
