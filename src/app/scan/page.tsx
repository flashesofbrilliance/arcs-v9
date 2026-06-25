import { notFound } from 'next/navigation'
import { flags } from '@/lib/flags'
import { ProfileScan } from '@/document/screens/ProfileScan'

// Staging-only surface for scan.arcs.care — see ADR-028. Mock data only;
// no generation pipeline wired yet (that's a separate, not-yet-written spec).
export default function ScanPage() {
  if (!flags.scanEnabled) notFound()

  return (
    <div style={{ background: '#020408', minHeight: '100vh', padding: '40px 0' }}>
      <div style={{ maxWidth: 760, margin: '0 auto', padding: '0 20px' }}>
        <ProfileScan />
      </div>
    </div>
  )
}
