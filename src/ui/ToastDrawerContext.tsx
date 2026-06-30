'use client'

import { createContext, useContext, useState, type ReactNode } from 'react'

type Ctx = { open: boolean; setOpen: (v: boolean | ((p: boolean) => boolean)) => void }

const ToastDrawerContext = createContext<Ctx>({ open: false, setOpen: () => {} })

// Lets any page's sticky footer react to the EyebrowToast drawer opening —
// footer fades to legal-links-only while the covenant drawer is up.
export function ToastDrawerProvider({ children }: { children: ReactNode }) {
  const [open, setOpen] = useState(false)
  return <ToastDrawerContext.Provider value={{ open, setOpen }}>{children}</ToastDrawerContext.Provider>
}

export function useToastDrawer() {
  return useContext(ToastDrawerContext)
}
