// Render through the fog to earned clarity.
"use client"

import { useEffect } from "react"
import {
  isVercelToolbarMounted,
  mountVercelToolbar,
  unmountVercelToolbar,
} from "@vercel/toolbar"

// The Vercel Toolbar stays hidden by default — it is never auto-injected, so
// it's invisible to visitors and to us until summoned. ⌘+. (Ctrl+. on
// non-Mac) toggles it on/off, so only the operator who knows the shortcut can
// reveal it. Renders nothing; it only owns the keyboard seam.
export function VercelToolbarToggle() {
  useEffect(() => {
    function onKeydown(e: KeyboardEvent) {
      if ((e.metaKey || e.ctrlKey) && e.key === ".") {
        e.preventDefault()
        if (isVercelToolbarMounted()) unmountVercelToolbar()
        else mountVercelToolbar()
      }
    }
    window.addEventListener("keydown", onKeydown)
    return () => {
      window.removeEventListener("keydown", onKeydown)
      if (isVercelToolbarMounted()) unmountVercelToolbar()
    }
  }, [])

  return null
}
