'use client'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/ui/Button'

// AuthControl — self-contained session widget for app-shell headers. Resolves
// its own auth state (so host organisms stay presentational) and offers Sign in
// (→ /compass) when anonymous, Sign out when authenticated.
export function AuthControl({ next }: { next?: string }) {
  const router = useRouter()
  const [authed, setAuthed] = useState<boolean | null>(null)

  useEffect(() => {
    let cancelled = false
    fetch('/api/auth/session')
      .then((r) => r.json())
      .then((s) => { if (!cancelled) setAuthed(!!s?.user?.id) })
      .catch(() => { if (!cancelled) setAuthed(false) })
    return () => { cancelled = true }
  }, [])

  if (authed === null) return null
  if (authed) {
    return (
      <Button variant="ghost" size="sm" onClick={async () => {
        const { signOut } = await import('next-auth/react')
        signOut({ callbackUrl: '/' })
      }}>Sign out</Button>
    )
  }
  return (
    <Button variant="ghost" size="sm" onClick={() => router.push(next ? `/compass?next=${encodeURIComponent(next)}` : '/compass')}>Sign in</Button>
  )
}
