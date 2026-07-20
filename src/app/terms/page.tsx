'use client'
import { useRouter } from 'next/navigation'
import { surface, text, signal, font, border } from '@/ui/tokens'
import { Wordmark } from '@/ui/Wordmark'
import { Rule } from '@/ui/Rule'

const mono = font.mono
const sans = font.sans

const COVENANT = [
  {
    group: 'On the product itself',
    rows: [
      {
        arcs: 'Operate the compass to provide genuine directional clarity, not to optimize for engagement, retention, or repeat usage',
        you: 'Use the compass for real decisions with genuine stakes, not to benchmark, scrape, or reverse-engineer the system',
      },
      {
        arcs: "Surface honest limits when the situation doesn't support confidence. ARCS won't fake certainty",
        you: "Bring honest questions. The compass doesn't work if the framing is a rationalization",
      },
      {
        arcs: 'Never design dark patterns that make exiting harder than entering',
        you: "Don't create accounts to abandon them or load test without notice",
      },
    ],
  },
  {
    group: 'On your data',
    rows: [
      {
        arcs: 'Never sell, share, or use your decision content for advertising',
        you: "Don't enter data that puts others at legal risk (confidential third-party info, protected personal data)",
      },
      {
        arcs: 'Delete your data within 30 days of request, permanently, without conditions',
        you: "Understand that deletion is one-way. We can't restore what you asked us to remove",
      },
      {
        arcs: 'Tell you 30 days before any material change to how your data is handled',
        you: 'Make decisions about whether to continue using ARCS before changes take effect',
      },
    ],
  },
  {
    group: 'On the relationship',
    rows: [
      {
        arcs: "Acknowledge when we don't have something built yet instead of implying we do",
        you: 'Report discrepancies between what we claim and what you observe in the source code',
      },
      {
        arcs: 'Not hold you to loyalty we did not earn through reciprocity',
        you: "Not claim ARCS guarantees outcomes. The compass navigates, it doesn't decide",
      },
      {
        arcs: 'Keep the source code public so you can verify our architecture claims yourself',
        you: 'Not use the public source to build a competing service that extracts from the same community',
      },
    ],
  },
]

const BREACH = [
  {
    breach: 'If ARCS breaches: violates the never-list, sells your data, changes terms without notice',
    remedy: 'You are released from these terms immediately. Delete your account. The covenant is void.',
  },
  {
    breach: 'If you breach: scrape the system, load test without notice, misrepresent data to game the compass',
    remedy: "ARCS may terminate access without refund. We'll tell you why. You can appeal.",
  },
  {
    breach: 'Dispute resolution: contact first, mediation second, arbitration only if both agree',
    remedy: 'No class action waiver. No mandatory arbitration. You retain the right to court.',
  },
]

function Divider() {
  return <div style={{ height: 1, background: border.subtle, margin: '1.75rem 0' }} />
}

function SectionHeader({ n, title, flag }: { n: string; title: string; flag?: string }) {
  return (
    <div style={{ marginBottom: '0.6rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.3rem' }}>
        <div style={{ fontFamily: mono, fontSize: '0.625rem', color: text.muted, letterSpacing: '0.1em', textTransform: 'uppercase' }}>{n}</div>
        {flag && <span style={{ fontFamily: mono, fontSize: '0.625rem', letterSpacing: '0.08em', color: signal.gold, border: `0.5px solid ${signal.gold}40`, borderRadius: 4, padding: '1px 6px' }}>{flag}</span>}
      </div>
      <div style={{ fontFamily: sans, fontSize: '0.9375rem', fontWeight: 500, color: text.primary }}>{title}</div>
    </div>
  )
}

export default function TermsPage() {
  const router = useRouter()

  return (
    <main style={{ minHeight: '100vh', background: surface.bg, color: text.primary }}>
      <div style={{ maxWidth: 700, margin: '0 auto', padding: '2rem 1.5rem 5rem' }}>

        {/* Nav */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingBottom: '1rem' }}>
          <button onClick={() => router.push('/')} style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 0 }}>
            <Wordmark section="Terms of Service" />
          </button>
        </div>
        <Rule style={{ marginBottom: '2rem' }} />

        <p style={{ fontFamily: mono, fontSize: '0.8125rem', color: text.muted, lineHeight: 1.6, margin: '0 0 1.75rem', letterSpacing: '0.01em' }}>
          Most terms of service are written to protect the company from you. These are written as a mutual agreement: what ARCS commits to, what you commit to, and what happens when either side breaks the covenant.
        </p>

        <h1 style={{ fontFamily: sans, fontSize: '1.6rem', fontWeight: 600, color: text.primary, margin: '0 0 0.5rem', lineHeight: 1.15, letterSpacing: '-0.02em' }}>
          A covenant, not a liability shield
        </h1>
        <p style={{ fontFamily: sans, fontSize: '0.9375rem', color: text.secondary, margin: '0 0 2.25rem', lineHeight: 1.5 }}>
          Read both columns.
        </p>

        {/* Covenant table */}
        <div style={{ border: `0.5px solid ${border.subtle}`, borderRadius: 10, overflow: 'hidden', marginBottom: '1.75rem' }}>
          {/* Header */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', background: surface.panel, borderBottom: `0.5px solid ${border.subtle}` }}>
            <div style={{ padding: '0.65rem 1rem', fontFamily: mono, fontSize: '0.6875rem', fontWeight: 700, letterSpacing: '0.08em', textTransform: 'uppercase', color: signal.cyan, borderRight: `0.5px solid ${border.subtle}` }}>ARCS commits to you</div>
            <div style={{ padding: '0.65rem 1rem', fontFamily: mono, fontSize: '0.6875rem', fontWeight: 700, letterSpacing: '0.08em', textTransform: 'uppercase', color: text.primary }}>You commit to ARCS</div>
          </div>

          {COVENANT.map((group) => (
            <div key={group.group}>
              {/* Group label */}
              <div style={{ padding: '0.45rem 1rem', fontFamily: mono, fontSize: '0.625rem', letterSpacing: '0.1em', textTransform: 'uppercase', color: text.muted, background: surface.bg, borderBottom: `0.5px solid ${border.subtle}`, borderTop: `0.5px solid ${border.subtle}` }}>
                {group.group}
              </div>
              {group.rows.map((row, i) => (
                <div key={i} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', borderBottom: `0.5px solid ${border.subtle}` }}>
                  <div style={{ padding: '0.65rem 1rem', fontFamily: sans, fontSize: '0.8125rem', color: text.secondary, lineHeight: 1.5, borderRight: `0.5px solid ${border.subtle}` }}>{row.arcs}</div>
                  <div style={{ padding: '0.65rem 1rem', fontFamily: sans, fontSize: '0.8125rem', color: text.secondary, lineHeight: 1.5 }}>{row.you}</div>
                </div>
              ))}
            </div>
          ))}
        </div>

        {/* Axiom */}
        <div style={{ borderLeft: `2px solid ${signal.cyan}40`, paddingLeft: '1rem', marginBottom: '2rem' }}>
          <div style={{ fontFamily: sans, fontSize: '0.9375rem', color: text.primary, fontWeight: 500, lineHeight: 1.4 }}>Loyalty is earned through reciprocity, not demanded through terms.</div>
          <div style={{ fontFamily: sans, fontSize: '0.8125rem', color: text.muted, marginTop: '0.25rem' }}>If ARCS breaks this covenant, you are released from it. If you break it, we may terminate your access. Either side can walk away.</div>
        </div>

        <Divider />

        {/* § 01 What using ARCS means */}
        <div style={{ marginBottom: '1.75rem' }}>
          <SectionHeader n="§ 01 · What using ARCS means" title="The relationship in plain terms" />
          <div style={{ fontFamily: sans, fontSize: '0.875rem', color: text.secondary, lineHeight: 1.75, marginTop: '0.5rem' }}>
            ARCS is a decision navigation instrument. You bring a real question. ARCS produces a directional bearing, a conviction grade, and a set of tributaries: adjacent questions worth asking. <strong style={{ color: text.primary }}>ARCS does not make decisions.</strong> The bearing is an input to your judgment, not a replacement for it. Using ARCS means understanding this distinction.
          </div>
        </div>

        <Divider />

        {/* § 02 Honest limits */}
        <div style={{ marginBottom: '1.75rem' }}>
          <SectionHeader n="§ 02 · Honest limits" title="What ARCS is not responsible for" />
          <div style={{ fontFamily: sans, fontSize: '0.875rem', color: text.secondary, lineHeight: 1.75, marginTop: '0.5rem' }}>
            ARCS is not a licensed advisor. Not legal, financial, medical, or professional. A bearing graded GREEN is a coherence signal, not a guarantee of outcome. The NCI score reflects pattern coherence in the analysis, not outcome probability in the real world.{' '}
            <strong style={{ color: text.primary }}>Decisions with irreversible consequences should be validated against domain expertise, not just the compass.</strong>
          </div>
        </div>

        <Divider />

        {/* § 03 Breach */}
        <div style={{ marginBottom: '1.75rem' }}>
          <SectionHeader n="§ 03 · Breach and remedy" title="What happens when the covenant breaks" />
          <div style={{ border: `0.5px solid ${border.subtle}`, borderRadius: 8, overflow: 'hidden', marginTop: '0.75rem' }}>
            <div style={{ padding: '0.5rem 1rem', background: surface.panel, borderBottom: `0.5px solid ${border.subtle}`, fontFamily: mono, fontSize: '0.625rem', letterSpacing: '0.1em', textTransform: 'uppercase', color: text.muted }}>Breach table</div>
            {BREACH.map((row, i) => (
              <div key={i} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', borderBottom: i < BREACH.length - 1 ? `0.5px solid ${border.subtle}` : 'none' }}>
                <div style={{ padding: '0.65rem 1rem', fontFamily: sans, fontSize: '0.8125rem', color: text.secondary, lineHeight: 1.5, borderRight: `0.5px solid ${border.subtle}` }}>{row.breach}</div>
                <div style={{ padding: '0.65rem 1rem', fontFamily: sans, fontSize: '0.8125rem', color: text.secondary, lineHeight: 1.5 }}>{row.remedy}</div>
              </div>
            ))}
          </div>
        </div>

        <Divider />

        {/* § 04 Sovereignty */}
        <div style={{ marginBottom: '2rem' }}>
          <SectionHeader n="§ 04 · Sovereignty clause" title="You own your expertise. ARCS doesn't." />
          <div style={{ fontFamily: sans, fontSize: '0.875rem', color: text.secondary, lineHeight: 1.75, marginTop: '0.5rem' }}>
            Your professional judgment, your decision logic, your frameworks for solving problems. These are yours before, during, and after using ARCS. ARCS facilitates reasoning. It doesn't claim ownership of the insight that emerges. Receipts stored in your account are records of your thinking process.{' '}
            <strong style={{ color: text.primary }}>They're yours.</strong>
          </div>
        </div>

        {/* Footer */}
        <div style={{ height: 1, background: border.subtle, marginBottom: '1.5rem' }} />
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.75rem' }}>
          <span style={{ fontFamily: mono, fontSize: '0.75rem', color: text.muted }}>Terms of service v1.0 · effective 2026-06-30</span>
          <div style={{ display: 'flex', gap: '1.25rem' }}>
            <button onClick={() => router.push('/trust')} style={{ background: 'none', border: 'none', cursor: 'pointer', fontFamily: mono, fontSize: '0.75rem', color: text.muted, textDecoration: 'underline', padding: 0 }}>Trust contract</button>
            <button onClick={() => router.push('/privacy')} style={{ background: 'none', border: 'none', cursor: 'pointer', fontFamily: mono, fontSize: '0.75rem', color: text.muted, textDecoration: 'underline', padding: 0 }}>Privacy policy</button>
            <button onClick={() => router.push('/dashboard')} style={{ background: 'none', border: 'none', cursor: 'pointer', fontFamily: mono, fontSize: '0.75rem', color: signal.cyan, padding: 0 }}>Open the compass →</button>
          </div>
        </div>
      </div>
    </main>
  )
}
