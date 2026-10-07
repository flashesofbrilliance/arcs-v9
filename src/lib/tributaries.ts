// Tributaries for a receipt. Prefer the persisted, sanitized atgTributaries
// column (written by /api/compass as [{type,label,prompt}]); fall back to the
// tributaries array inside rawResponse, stripping the same ```json fences the
// compass route strips before it parses the model reply. Older rows predate the
// column; some newer rows keep a fenced rawResponse that bare JSON.parse rejects.

export const stripFences = (s: string): string =>
  s.replace(/^```(?:json)?\n?/, "").replace(/\n?```$/, "").trim()

const parseArray = (text: string | null | undefined): unknown[] | null => {
  if (typeof text !== "string" || text.length === 0) return null
  try {
    const v = JSON.parse(stripFences(text)) as unknown
    return Array.isArray(v) ? v : null
  } catch { return null }
}

export function tributariesOf(
  receipt: { atgTributaries?: string | null; rawResponse?: string | null } | null | undefined,
): unknown[] {
  if (!receipt) return []
  const atg = parseArray(receipt.atgTributaries)
  if (atg && atg.length > 0) return atg
  if (typeof receipt.rawResponse !== "string" || receipt.rawResponse.length === 0) return []
  try {
    const raw = JSON.parse(stripFences(receipt.rawResponse)) as { tributaries?: unknown }
    return Array.isArray(raw?.tributaries) ? raw.tributaries : []
  } catch { return [] }
}
