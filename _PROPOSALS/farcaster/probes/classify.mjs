// Offline classifiers shared by both probes. verdict: proven | fallback | killed.
export function classifyEvents(obs) {
  const reasons = [];
  const shards = obs.shards ?? {};
  for (const s of obs.expected_shards ?? [0, 1, 2]) if (!(s in shards)) reasons.push(`shard ${s} missing`);
  if (reasons.length) return { verdict: "killed", reasons };
  let dup = false, empty = false;
  for (const [s, sh] of Object.entries(shards)) {
    const ids = (sh.pages ?? []).flat();
    if (!ids.length || (sh.pages ?? []).some((p) => p.length === 0)) empty = true;
    for (let i = 1; i < ids.length; i++) if (ids[i] > ids[i - 1] + 1) reasons.push(`shard ${s}: cursor gap ${ids[i - 1]} -> ${ids[i]}`);
    if (new Set(ids).size !== ids.length) { dup = true; reasons.push(`shard ${s}: duplicate event id`); }
  }
  if (reasons.some((r) => r.includes("gap"))) return { verdict: "killed", reasons };
  if (dup) return { verdict: "fallback", reasons: [...reasons, "dedupe by id downstream"] };
  if (empty) return { verdict: "fallback", reasons: ["empty page: inconclusive, retry or longer sample"] };
  return { verdict: "proven", reasons: ["no gaps, no duplicates, all shards present"] };
}
export function classifyWrite(obs) {
  const k = obs.keyadd ?? {}, c = obs.cast ?? {};
  if (k.status !== 200) {
    const why = String(k.error ?? k.body ?? k.status);
    if (/nonce/i.test(why)) return { verdict: "fallback", reasons: ["KEY_ADD rejected for nonce: refetch nonce and retry"] };
    if (/domain|eip-?712|signature/i.test(why)) return { verdict: "fallback", reasons: ["KEY_ADD rejected, EIP-712 domain/signature mismatch: fix domain"] };
    return { verdict: "killed", reasons: [`KEY_ADD rejected: ${why}`] };
  }
  if (c.status !== 200) return { verdict: "fallback", reasons: [`cast rejected (${c.error ?? c.status}): signer not authorized or scope`] };
  if (!obs.readback || !obs.merge_event) return { verdict: "killed", reasons: ["accepted but never merged/readable: relay path not proven"] };
  return { verdict: "proven", reasons: ["KEY_ADD accepted, cast accepted, readable, merge event seen"] };
}
export const EXIT = { proven: 0, fallback: 10, killed: 11 };
