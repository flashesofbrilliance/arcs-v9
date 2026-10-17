// fc-derisk-write-path-probe. Written, NOT RUN. Spends no money by design (gasless KEY_ADD) but WRITES to mainnet:
// run only against a throwaway account with Zach's go. Helper names are as documented for @farcaster/core 0.20.0;
// if any import is missing or its signature differs, the probe fails loudly at import/call time: that IS a finding.
import { requireThrowaway } from "./guard.mjs";
import * as core from "@farcaster/core";           // 0.20.0
import { privateKeyToAccount } from "viem/accounts"; // peer of core's ViemLocalEip712Signer
import { ed25519 } from "@noble/curves/ed25519";
const { nodeUrl, key, fid } = requireThrowaway();
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
console.log("KEY_ADD submit:", await submit(keyAdd));

// 2. one cast signed by the new app key
const appSigner = new core.NobleEd25519Signer(appPriv);
const text = `probe ${new Date().toISOString()} (throwaway)`;
const cast = must(await core.makeCastAdd({ text, embeds: [], embedsDeprecated: [], mentions: [], mentionsPositions: [] }, { fid, network }, appSigner), "makeCastAdd");
const hashHex = "0x" + Buffer.from(cast.hash).toString("hex");
console.log("CAST submit:", await submit(cast), hashHex);

// 3. read it back, and watch events for the merge
let found = false;
for (let i = 0; i < 12 && !found; i++) {
  await new Promise((r) => setTimeout(r, 5000));
  const g = await fetch(`${nodeUrl}/v1/castById?fid=${fid}&hash=${hashHex}`);
  const ev = await fetch(`${nodeUrl}/v1/events?shard_index=0&from_event_id=0&pageSize=1`);
  found = g.ok; console.log(`poll ${i}: castById=${g.status} events=${ev.status}`);
}
console.log(found ? "PASS: cast readable on node (merge event still needs events-probe cross-check)" : "FAIL: cast not readable within 60s");
process.exit(found ? 0 : 1);
