"use client"
import { useState, useEffect } from "react"

// SSR-safe viewport width hook. Initializes to 1280 (desktop) so server and
// first client render agree, then syncs to the real width after mount.
// rAF-debounced to avoid render storms during window drag.
export function useVw(): number {
  const [vw, setVw] = useState(1280)
  useEffect(() => {
    let raf = 0
    const sync = () => {
      cancelAnimationFrame(raf)
      raf = requestAnimationFrame(() => setVw(window.innerWidth))
    }
    sync()
    window.addEventListener("resize", sync)
    return () => { cancelAnimationFrame(raf); window.removeEventListener("resize", sync) }
  }, [])
  return vw
}
