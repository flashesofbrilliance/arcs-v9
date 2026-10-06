'use client'
import { useEffect, useState } from 'react'
import { Button, ButtonLink } from '@/ui/Button'

// AuthControl — self-contained session widget for app-shell headers. Resolves
// its own auth state (so host organisms stay presentational) and offers Sign in
// (→ /compass) when anonymous, Sign out when authenticated.
// showWaitlist: renders a Waitlist button when not signed in (home nav only).
export function AuthControl({ next, showWaitlist }: { next?: string; showWaitlist?: boolean }) {
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
    <>
      {showWaitlist && (
        <ButtonLink variant="ghost" size="sm" href="/waitlist">Waitlist</ButtonLink>
      )}
      <ButtonLink variant="ghost" size="sm" href={next ? `/compass?next=${encodeURIComponent(next)}` : '/compass'}>Sign in</ButtonLink>
    </>
  )
}
