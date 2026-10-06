// Job Factory slice 6 (2026-10-05): the named trust term.
// A role earns a trust chip ONLY when its company matches a company where a NAMED
// person from Zach's champion list works (runtime/data/champion-shortlist-v1.tsv,
// loaded by src/lib/champions.ts). Titles never count: the 2025 prototype added
// trust for any "VP Product" posting, which inflated every director role.
//
// Privacy: the board receives a POINTER (champion ids + a count), never a name. Names
// stay behind the gated Champions surface. Nothing here is copied into jdHits, a
// forge seed, or a staged artifact. The composite is not changed: the chip is
// evidence for Zach's swipe, not a score.

const SUFFIX = /\b(inc|incorporated|llc|ltd|limited|corp|corporation|co|company|plc|gmbh|holdings|group|technologies|technology|labs|hq)\b\.?/g

export function normalizeCompany(c: string | null | undefined): string {
  return (c ?? "").toLowerCase().replace(/&/g, " and ").replace(/[.,'’()]/g, " ").replace(SUFFIX, " ").replace(/\s+/g, " ").trim()
}

export type TrustIndex = Map<string, string[]>

// company (normalized) -> champion ids. Rows with no company are skipped: a name
// without a company cannot vouch for a posting.
export function buildTrustIndex(champions: { id: string; company: string }[]): TrustIndex {
  const idx: TrustIndex = new Map()
  for (const c of champions) {
    const k = normalizeCompany(c.company)
    if (k.length < 2) continue
    idx.set(k, [...(idx.get(k) ?? []), c.id])
  }
  return idx
}

export type Trust = { count: number; ids: string[] } | null

export function trustFor(company: string, idx: TrustIndex): Trust {
  const ids = idx.get(normalizeCompany(company))
  return ids && ids.length ? { count: ids.length, ids } : null
}
