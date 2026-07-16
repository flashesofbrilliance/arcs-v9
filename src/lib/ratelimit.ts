// Interim in-memory sliding-window rate limiter (ledger RL-001).
// Per-serverless-instance only — a determined attacker spread across
// instances exceeds the aggregate limit, but bursts against one instance
// (the realistic wallet-drain shape) are blocked. The durable fix is
// gateway-level limiting + spend caps (ledger GW-002); when that ships,
// this becomes defense-in-depth, not the primary control.

type Bucket = { timestamps: number[] }

const buckets = new Map<string, Bucket>()
const MAX_KEYS = 10_000 // hard cap so the map can't grow unbounded

export function rateLimit(
  key: string,
  { limit, windowMs }: { limit: number; windowMs: number }
): { ok: boolean; retryAfterSec: number } {
  const now = Date.now()
  const cutoff = now - windowMs

  if (!buckets.has(key) && buckets.size >= MAX_KEYS) {
    buckets.clear() // fail open rather than OOM; instance-local anyway
  }
  const bucket = buckets.get(key) ?? { timestamps: [] }
  bucket.timestamps = bucket.timestamps.filter((t) => t > cutoff)

  if (bucket.timestamps.length >= limit) {
    buckets.set(key, bucket)
    const retryAfterSec = Math.ceil(
      (bucket.timestamps[0] + windowMs - now) / 1000
    )
    return { ok: false, retryAfterSec: Math.max(retryAfterSec, 1) }
  }

  bucket.timestamps.push(now)
  buckets.set(key, bucket)
  return { ok: true, retryAfterSec: 0 }
}

export function clientIp(req: Request): string {
  return (
    req.headers.get("x-forwarded-for")?.split(",")[0]?.trim() ||
    req.headers.get("x-real-ip") ||
    "unknown"
  )
}
