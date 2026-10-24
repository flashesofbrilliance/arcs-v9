// Daily anonymous-call counter, LOG ONLY (compass anti-distillation ruling 3,
// 2026-10-20). It records a bare count per UTC day and never blocks, delays or
// alters a response: the spend ceiling until data exists is the Anthropic key
// usage limit. No IP, header or content is read or kept (ruling 10: no
// app-level hashed-IP counter). The per-instance count is a floor; the durable
// total is the number of `[ANON_CALL]` lines in the Vercel runtime logs per UTC
// day. After a week of log data, propose a limit as a stated multiple (default
// 3x) of the observed peak and record both in the receipt. Never guess one.

const counts = new Map<string, number>()

export function utcDay(now: number = Date.now()): string {
  return new Date(now).toISOString().slice(0, 10)
}

export function noteAnonymousCall(now: number = Date.now()): { day: string; instanceCount: number } {
  const day = utcDay(now)
  for (const k of counts.keys()) if (k !== day) counts.delete(k)
  const instanceCount = (counts.get(day) ?? 0) + 1
  counts.set(day, instanceCount)
  return { day, instanceCount }
}

export function logAnonymousCall(now: number = Date.now()): void {
  const { day, instanceCount } = noteAnonymousCall(now)
  console.log(`[ANON_CALL] day=${day} instance_count=${instanceCount}`)
}
