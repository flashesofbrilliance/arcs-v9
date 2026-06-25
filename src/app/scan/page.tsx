import { notFound } from 'next/navigation'
import { flags } from '@/lib/flags'
import { ScanClient } from './ScanClient'

// Staging-only surface for scan.arcs.care — see ADR-028. Real LinkedIn-derived
// content (per-post analytics, Creator Analytics, export ZIP) for Zach Harris,
// hardcoded here as mock data — no generation pipeline wired yet.
export default function ScanPage() {
  if (!flags.scanEnabled) notFound()

  return (
    <div style={{ background: '#020408', minHeight: '100vh', padding: '40px 0' }}>
      <div style={{ maxWidth: 760, margin: '0 auto', padding: '0 20px' }}>
        <ScanClient />
      </div>
    </div>
  )
}
