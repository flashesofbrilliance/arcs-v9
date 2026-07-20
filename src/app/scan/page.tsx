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
        <div style={{
          display: 'inline-flex', alignItems: 'center', gap: 8, marginBottom: 20,
          fontFamily: "'JetBrains Mono','IBM Plex Mono',monospace", fontSize: 10.5,
          letterSpacing: '0.08em', textTransform: 'uppercase', color: '#FFD700',
          border: '1px solid #FFD70035', borderRadius: 6, padding: '5px 10px',
        }}>
          ◆ Illustrative. Generation pipeline not yet wired (ADR-028)
        </div>
        <ScanClient />
      </div>
    </div>
  )
}
