// fc-derisk-write-path-probe. Written, NOT RUN. Spends no money by design (gasless KEY_ADD) but WRITES to mainnet:
// run only against a throwaway account with Zach's go. Helper names are as documented for @farcaster/core 0.20.0;
// if any import is missing or its signature differs, the probe fails loudly at import/call time: that IS a finding.
import fs from "node:fs";
import { requireThrowaway } from "./guard.mjs";
import { classifyWrite, EXIT } from "./classify.mjs";
const fx = process.argv.indexOf("--fixture");
if (fx > 0) { const v = classifyWrite(JSON.parse(fs.readFileSync(process.argv[fx + 1], "utf8"))); console.log(JSON.stringify(v)); process.exit(EXIT[v.verdict]); }
const { nodeUrl, key, fid } = requireThrowaway();
const core = await import("@farcaster/core");           // 0.20.0
const { privateKeyToAccount } = await import("viem/accounts");
const { ed25519 } = await import("@noble/curves/ed25519");
const network = core.FarcasterNetwork.MAINNET;
const submit = async (msg) => {
  const bytes = core.Message.encode(msg).finish();
  const r = await fetch(`${nodeUrl}/v1/submitMessage`, { method: "POST", headers: { "content-type": "application/octet-stream" }, body: bytes });
  return { status: r.status, body: await r.text() };
};
const must = (res, what) => { if (res.isErr()) { console.error(`FAIL ${what}:`, res.error); process.exit(1); } return res.value; };

// 1. fresh app key (ed25519) + gasless signed key request metadata, signed by custody key
const appPriv = ed25519.utils.randomPrivateKey();
const appPub = ed25519.getPublicKey(appPriv);
const custody = new core.ViemLocalEip712Signer(privateKeyToAccount(key));
const deadline = Math.floor(Date.now() / 1000) + 3600;
const metadata = must(await core.getGaslessSignedKeyRequestMetadata?.(custody, { requestFid: fid, key: appPub, deadline }) ?? { isErr: () => true, error: "getGaslessSignedKeyRequestMetadata missing" }, "metadata");
const body = must(core.makeKeyAddBody({ key: appPub, keyType: 1, metadata, metadataType: 1 }), "makeKeyAddBody");
const keyAdd = must(await core.makeKeyAdd(body, { fid, network }, custody), "makeKeyAdd");
const lastKeyAdd = await submit(keyAdd); console.log("KEY_ADD status:", lastKeyAdd.status);

// 2. one cast signed by the new app key
const appSigner = new core.NobleEd25519Signer(appPriv);
const text = `probe ${new Date().toISOString()} (throwaway)`;
const cast = must(await core.makeCastAdd({ text, embeds: [], embedsDeprecated: [], mentions: [], mentionsPositions: [] }, { fid, network }, appSigner), "makeCastAdd");
const hashHex = "0x" + Buffer.from(cast.hash).toString("hex");
const lastCast = await submit(cast); console.log("CAST status:", lastCast.status, hashHex);

// 3. read it back, and watch events for the merge
let found = false, mergeSeen = false;
for (let i = 0; i < 12 && !found; i++) {
  await new Promise((r) => setTimeout(r, 5000));
  const g = await fetch(`${nodeUrl}/v1/castById?fid=${fid}&hash=${hashHex}`);
  const ev = await fetch(`${nodeUrl}/v1/events?shard_index=1&from_event_id=0&pageSize=100`);
  const evText = ev.ok ? await ev.text() : "";
  mergeSeen = mergeSeen || evText.toLowerCase().includes(hashHex.slice(2).toLowerCase()) || evText.includes(Buffer.from(cast.hash).toString("base64"));
  found = g.ok; console.log(`poll ${i}: castById=${g.status} events=${ev.status} mergeSeen=${mergeSeen}`);
}
const v = classifyWrite({ keyadd: lastKeyAdd, cast: lastCast, readback: found, merge_event: mergeSeen });
console.log(JSON.stringify(v));
process.exit(EXIT[v.verdict]);
