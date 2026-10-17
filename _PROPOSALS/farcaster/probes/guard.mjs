// Shared refusal logic. Written, NOT RUN. Refuses anything that looks like a main wallet.
export function requireThrowaway(env = process.env) {
  const key = env.FC_CUSTODY_KEY ?? "";
  const refuse = (why) => { console.error("REFUSING: " + why); process.exit(2); };
  if (!env.FC_NODE_URL) refuse("FC_NODE_URL not set");
  if (/\s/.test(key.trim()) || key.trim().split(/\s+/).length > 1) refuse("value looks like a seed phrase; never put a mnemonic in this probe");
  if (!/^0x[0-9a-fA-F]{64}$/.test(key)) refuse("FC_CUSTODY_KEY must be a 0x + 64 hex throwaway private key");
  if (env.FC_ACK_THROWAWAY !== "this-key-holds-under-15-usd-and-is-disposable") refuse("set FC_ACK_THROWAWAY to the exact acknowledgement string");
  if (!env.FC_FID) refuse("FC_FID not set (the throwaway account's fid)");
  if (env.FC_DENY_FIDS && env.FC_DENY_FIDS.split(",").includes(env.FC_FID)) refuse("FID is on the deny list (main account)");
  return { nodeUrl: env.FC_NODE_URL.replace(/\/$/, ""), key, fid: Number(env.FC_FID) };
}
