// Offline classifiers shared by both probes. verdict: proven | fallback | killed.
export function classifyEvents(obs) {
  const reasons = [];
  const shards = obs.shards ?? {};
  for (const s of obs.expected_shards ?? [0, 1, 2]) if (!(s in shards)) reasons.push(`shard ${s} missing`);
  if (reasons.length) return { verdict: "killed", reasons };
  let dup = false, empty = false;
  for (const [s, sh] of Object.entries(shards)) {
    const ids = (sh.pages ?? []).flat();
    const pg = sh.pages ?? [];
    // an empty page AFTER data is the node being at head (fine); empty with no data, or empty BEFORE data, is inconclusive
    const firstData = pg.findIndex((p) => p.length > 0);
    if (!ids.length || pg.slice(0, Math.max(firstData, 0)).some((p) => p.length === 0) || pg.slice(firstData).some((p, i, a) => p.length === 0 && a.slice(i + 1).some((q) => q.length > 0))) empty = true;
    // IDs are block-based and NOT contiguous across blocks (Snapchain events API doc), so a +1 rule is wrong.
    // Completeness is checked with BLOCK_CONFIRMED.totalEvents when the probe supplies it; order must be strictly increasing.
    for (let i = 1; i < ids.length; i++) if (ids[i] < ids[i - 1]) reasons.push(`shard ${s}: cursor gap/order break ${ids[i - 1]} -> ${ids[i]}`);
    for (const b of sh.blocks ?? []) if (b.seen !== b.total) reasons.push(`shard ${s}: cursor gap: block reported ${b.total} events, saw ${b.seen}`);
    if (new Set(ids).size !== ids.length) { dup = true; reasons.push(`shard ${s}: duplicate event id`); }
  }
  if (reasons.some((r) => r.includes("gap") || r.includes("order break"))) return { verdict: "killed", reasons };
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

// Build a classifier observation from raw event pages (real API shape: events[] with type/id). Pure; used by the live path and by the offline test.
export function observeShard(pages) {
  const ids = pages.map((p) => p.map((e) => Number(e.id)));
  const blocks = []; let seen = 0, open = false;
  for (const e of pages.flat()) {
    if (e.type === "HUB_EVENT_TYPE_BLOCK_CONFIRMED") {
      // BLOCK_CONFIRMED.totalEvents counts the block's events; the confirm event itself is the first event of its block in the doc example
      if (open) blocks.push({ total: blocks.cur, seen });
      blocks.cur = e.blockConfirmedBody?.totalEvents; seen = 1; open = true;
    } else if (open) seen++;
  }
  if (open) blocks.push({ total: blocks.cur, seen, partial: true });
  return { pages: ids, blocks: blocks.filter((b) => !b.partial) };
}
