'use client'

import { ToastDrawerProvider } from '@/ui/ToastDrawerContext'

export function Providers({ children }: { children: React.ReactNode }) {
  return <ToastDrawerProvider>{children}</ToastDrawerProvider>
}
