'use client'
import { useRouter } from 'next/navigation'
import { surface, text, signal, font, border } from '@/ui/tokens'
import { Wordmark } from '@/ui/Wordmark'
import { Rule } from '@/ui/Rule'

const mono = font.mono
const sans = font.sans

const ALWAYS = [
  { what: 'Input never trains a model', why: 'Anthropic API terms + architectural separation' },
  { what: 'Anonymous sessions store nothing', why: 'No auth = no write path to DB' },
  { what: 'Delete within 30 days, permanently', why: 'One-way gate: no backups retained after confirmation' },
  { what: 'Source code stays public', why: 'You can verify our architecture claims yourself' },
  { what: '30 days notice before material policy changes', why: 'You decide whether new terms apply before they do' },
]

const SOMETIMES = [
  { what: 'Receipts stored', trigger: 'Only when you sign in' },
  { what: 'A shared bearing travels in the link, not our DB', trigger: 'Only if you create a one-time share link — content is encoded in the URL fragment (never sent to us); a functional flag on the recipient device enforces one view' },
  { what: 'Email contact', trigger: 'Only if you provided an address' },
  { what: 'Legal disclosure of your data', trigger: 'Only under valid legal compulsion — we notify you if permitted' },
  { what: 'Session logs (request metadata, no content)', trigger: 'Standard infra logging — purged after 30 days' },
]

const NEVER = [
  { what: 'Sell or share your decision content', proof: 'No third-party data agreements — verify in source code' },
  { what: 'Use your data for advertising or profiling', proof: 'No ad infrastructure exists in the codebase' },
  { what: 'Hold your data hostage to keep you subscribed', proof: 'Delete is always available regardless of subscription' },
  { what: 'Publish content from your sessions without consent', proof: 'Journalism pipeline requires explicit opt-in per session' },
]

const DATA_INVENTORY = [
  { key: 'Question text', val: 'SESSION ONLY · anonymous / DB · signed-in' },
  { key: 'DEWY receipt (bearing, NCI, Y-gate)', val: 'DB · signed-in only' },
  { key: 'Email address', val: 'DB · only if provided for magic link' },
  { key: 'Request metadata (timestamps, codes)', val: 'INFRA LOGS · 30d TTL · no decision content' },
  { key: 'Prep session (stakes, horizon, protecting)', val: 'DB · signed-in only · linked to receipt' },
]

function SectionHeader({ n, title }: { n: string; title: string }) {
  return (
    <div style={{ marginBottom: '0.6rem' }}>
      <div style={{ fontFamily: mono, fontSize: '0.625rem', color: text.muted, letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: '0.3rem' }}>{n}</div>
      <div style={{ fontFamily: sans, fontSize: '0.9375rem', fontWeight: 500, color: text.primary }}>{title}</div>
    </div>
  )
}

function Divider() {
  return <div style={{ height: 1, background: border.subtle, margin: '1.75rem 0' }} />
}

export default function PrivacyPage() {
  const router = useRouter()

  return (
    <main style={{ minHeight: '100vh', background: surface.bg, color: text.primary }}>
      <div style={{ maxWidth: 700, margin: '0 auto', padding: '2rem 1.5rem 5rem' }}>

        {/* Nav */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingBottom: '1rem' }}>
          <button onClick={() => router.push('/')} style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 0 }}>
            <Wordmark section="Privacy Policy" />
          </button>
        </div>
        <Rule style={{ marginBottom: '2rem' }} />

        <p style={{ fontFamily: mono, fontSize: '0.8125rem', color: text.muted, lineHeight: 1.6, margin: '0 0 1.75rem', letterSpacing: '0.01em' }}>
          ARCS advocates for information access as a right. That obligation runs both ways. This policy tells you exactly what we collect, how long we keep it, who can see it, and what we will never do — receipted, not promised.
        </p>

        <h1 style={{ fontFamily: sans, fontSize: '1.6rem', fontWeight: 600, color: text.primary, margin: '0 0 0.5rem', lineHeight: 1.15, letterSpacing: '-0.02em' }}>
          What happens to your data
        </h1>
        <p style={{ fontFamily: sans, fontSize: '0.9375rem', color: text.secondary, margin: '0 0 2.25rem', lineHeight: 1.5 }}>
          Three categories. Read all three.
        </p>

        {/* Always band */}
        <div style={{ border: `0.5px solid ${border.subtle}`, borderRadius: 10, overflow: 'hidden', marginBottom: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '0.7rem 1rem', background: surface.panel, borderBottom: `0.5px solid ${border.subtle}` }}>
            <div style={{ width: 8, height: 8, borderRadius: '50%', background: signal.green, flexShrink: 0 }} />
            <span style={{ fontFamily: mono, fontSize: '0.6875rem', fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase', color: signal.green }}>Always</span>
            <span style={{ fontFamily: sans, fontSize: '0.8rem', color: text.muted }}>Unconditional. No carve-outs. No exceptions for business reasons.</span>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', borderBottom: `0.5px solid ${border.subtle}` }}>
            <div style={{ padding: '0.45rem 1rem', fontFamily: mono, fontSize: '0.625rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: text.muted, borderRight: `0.5px solid ${border.subtle}` }}>What</div>
            <div style={{ padding: '0.45rem 1rem', fontFamily: mono, fontSize: '0.625rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: text.muted }}>Why it's locked</div>
          </div>
          {ALWAYS.map((row, i) => (
            <div key={row.what} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', borderBottom: i < ALWAYS.length - 1 ? `0.5px solid ${border.subtle}` : 'none' }}>
              <div style={{ padding: '0.6rem 1rem', fontFamily: sans, fontSize: '0.8125rem', color: text.secondary, lineHeight: 1.45, borderRight: `0.5px solid ${border.subtle}` }}>{row.what}</div>
              <div style={{ padding: '0.6rem 1rem', fontFamily: sans, fontSize: '0.8125rem', color: text.secondary, lineHeight: 1.45 }}>{row.why}</div>
            </div>
          ))}
        </div>

        {/* Sometimes band */}
        <div style={{ border: `0.5px solid ${border.subtle}`, borderRadius: 10, overflow: 'hidden', marginBottom: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '0.7rem 1rem', background: surface.panel, borderBottom: `0.5px solid ${border.subtle}` }}>
            <div style={{ width: 8, height: 8, borderRadius: '50%', background: signal.gold, flexShrink: 0 }} />
            <span style={{ fontFamily: mono, fontSize: '0.6875rem', fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase', color: signal.gold }}>Sometimes</span>
            <span style={{ fontFamily: sans, fontSize: '0.8rem', color: text.muted }}>Conditional. You control the trigger. We state the condition clearly.</span>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', borderBottom: `0.5px solid ${border.subtle}` }}>
            <div style={{ padding: '0.45rem 1rem', fontFamily: mono, fontSize: '0.625rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: text.muted, borderRight: `0.5px solid ${border.subtle}` }}>What</div>
            <div style={{ padding: '0.45rem 1rem', fontFamily: mono, fontSize: '0.625rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: text.muted }}>Trigger (you control this)</div>
          </div>
          {SOMETIMES.map((row, i) => (
            <div key={row.what} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', borderBottom: i < SOMETIMES.length - 1 ? `0.5px solid ${border.subtle}` : 'none' }}>
              <div style={{ padding: '0.6rem 1rem', fontFamily: sans, fontSize: '0.8125rem', color: text.secondary, lineHeight: 1.45, borderRight: `0.5px solid ${border.subtle}` }}>{row.what}</div>
              <div style={{ padding: '0.6rem 1rem', fontFamily: sans, fontSize: '0.8125rem', color: text.secondary, lineHeight: 1.45 }}>{row.trigger}</div>
            </div>
          ))}
        </div>

        {/* Never band */}
        <div style={{ border: `0.5px solid ${border.subtle}`, borderRadius: 10, overflow: 'hidden', marginBottom: '2.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '0.7rem 1rem', background: surface.panel, borderBottom: `0.5px solid ${border.subtle}` }}>
            <div style={{ width: 8, height: 8, borderRadius: '50%', background: signal.red, flexShrink: 0 }} />
            <span style={{ fontFamily: mono, fontSize: '0.6875rem', fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase', color: signal.red }}>Never</span>
            <span style={{ fontFamily: sans, fontSize: '0.8rem', color: text.muted }}>Scout's honor. Enforced by architecture and covenant, not just policy.</span>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', borderBottom: `0.5px solid ${border.subtle}` }}>
            <div style={{ padding: '0.45rem 1rem', fontFamily: mono, fontSize: '0.625rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: text.muted, borderRight: `0.5px solid ${border.subtle}` }}>What we won't do</div>
            <div style={{ padding: '0.45rem 1rem', fontFamily: mono, fontSize: '0.625rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: text.muted }}>How we're proving it</div>
          </div>
          {NEVER.map((row, i) => (
            <div key={row.what} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', borderBottom: i < NEVER.length - 1 ? `0.5px solid ${border.subtle}` : 'none' }}>
              <div style={{ padding: '0.6rem 1rem', fontFamily: sans, fontSize: '0.8125rem', color: text.secondary, lineHeight: 1.45, borderRight: `0.5px solid ${border.subtle}` }}>{row.what}</div>
              <div style={{ padding: '0.6rem 1rem', fontFamily: sans, fontSize: '0.8125rem', color: text.secondary, lineHeight: 1.45 }}>{row.proof}</div>
            </div>
          ))}
        </div>

        <Divider />

        {/* Data inventory */}
        <div style={{ marginBottom: '1.75rem' }}>
          <SectionHeader n="§ 01 · What we collect" title="Data types and their paths" />
          <div style={{ border: `0.5px solid ${border.subtle}`, borderRadius: 8, overflow: 'hidden', marginTop: '0.75rem' }}>
            <div style={{ padding: '0.5rem 1rem', background: surface.panel, borderBottom: `0.5px solid ${border.subtle}`, fontFamily: mono, fontSize: '0.625rem', letterSpacing: '0.1em', textTransform: 'uppercase', color: text.muted }}>Data inventory</div>
            {DATA_INVENTORY.map((row, i) => (
              <div key={row.key} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', padding: '0.5rem 1rem', borderBottom: i < DATA_INVENTORY.length - 1 ? `0.5px solid ${border.subtle}` : 'none', flexWrap: 'wrap', gap: '0.5rem' }}>
                <span style={{ fontFamily: sans, fontSize: '0.8rem', color: text.secondary }}>{row.key}</span>
                <span style={{ fontFamily: mono, fontSize: '0.6875rem', color: text.muted }}>{row.val}</span>
              </div>
            ))}
          </div>
        </div>

        <Divider />

        {/* Honest gaps */}
        <div style={{ marginBottom: '1.75rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.6rem' }}>
            <div style={{ fontFamily: mono, fontSize: '0.625rem', color: text.muted, letterSpacing: '0.1em', textTransform: 'uppercase' }}>§ 02</div>
            <span style={{ fontFamily: mono, fontSize: '0.625rem', letterSpacing: '0.08em', color: signal.gold, border: `0.5px solid ${signal.gold}40`, borderRadius: 4, padding: '1px 6px' }}>⚠ NOT BUILT YET</span>
          </div>
          <div style={{ fontFamily: sans, fontSize: '0.9375rem', fontWeight: 500, color: text.primary, marginBottom: '0.5rem' }}>What we don't have yet but should</div>
          <div style={{ fontFamily: sans, fontSize: '0.875rem', color: text.secondary, lineHeight: 1.75 }}>
            <strong style={{ color: text.primary }}>Export</strong> — not yet built. You can delete, but you can't yet download your receipt history in a portable format. This is on the roadmap. Until it ships, contact us directly if you need your data.<br /><br />
            <strong style={{ color: text.primary }}>Audit log</strong> — you can't yet see a log of every time your data was accessed. We log it internally; the user-facing view isn't built. On the roadmap.<br /><br />
            <strong style={{ color: text.primary }}>Consent revocation per-receipt</strong> — if a receipt was used in the journalism pipeline and you later want it removed, the workflow for that isn't formalized yet. Contact us directly.
          </div>
        </div>

        <Divider />

        {/* Journalism pipeline */}
        <div style={{ marginBottom: '1.75rem' }}>
          <SectionHeader n="§ 03 · Journalism pipeline" title="When ARCS produces content from sessions" />
          <div style={{ fontFamily: sans, fontSize: '0.875rem', color: text.secondary, lineHeight: 1.7, marginTop: '0.5rem' }}>
            ARCS operates <strong style={{ color: text.primary }}>@TILbyARCS</strong> as a journalism engine. Content is produced from ARCS's own analysis — not from your sessions. Your compass queries are never published without an explicit, session-specific opt-in — not buried in account settings, not assumed from prior consent. If we ever build a feature where you can voluntarily contribute an anonymized receipt to the journalism corpus, that will be a separate, prominent, reversible consent step.
          </div>
        </div>

        <Divider />

        {/* Rights */}
        <div style={{ marginBottom: '2rem' }}>
          <SectionHeader n="§ 04 · Your rights" title="What you can do, right now" />
          <div style={{ fontFamily: sans, fontSize: '0.875rem', color: text.secondary, lineHeight: 1.8, marginTop: '0.5rem' }}>
            <strong style={{ color: text.primary }}>Delete everything:</strong> Email to request full account deletion. 30-day window, one-way gate.<br />
            <strong style={{ color: text.primary }}>Correct your data:</strong> Email to correct stored information.<br />
            <strong style={{ color: text.primary }}>Question this policy:</strong> If something here conflicts with what you observe in the source code, flag it. We will investigate and correct the discrepancy or the code.<br />
            <strong style={{ color: text.primary }}>Exit without penalty:</strong> No dark patterns, no retention loops, no data held to encourage you to stay.
          </div>
        </div>

        {/* Footer */}
        <div style={{ height: 1, background: border.subtle, marginBottom: '1.5rem' }} />
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.75rem' }}>
          <span style={{ fontFamily: mono, fontSize: '0.75rem', color: text.muted }}>Privacy policy v1.0 · effective 2026-06-30</span>
          <div style={{ display: 'flex', gap: '1.25rem' }}>
            <button onClick={() => router.push('/trust')} style={{ background: 'none', border: 'none', cursor: 'pointer', fontFamily: mono, fontSize: '0.75rem', color: text.muted, textDecoration: 'underline', padding: 0 }}>Trust contract</button>
            <button onClick={() => router.push('/terms')} style={{ background: 'none', border: 'none', cursor: 'pointer', fontFamily: mono, fontSize: '0.75rem', color: text.muted, textDecoration: 'underline', padding: 0 }}>Terms of service</button>
            <button onClick={() => router.push('/dashboard')} style={{ background: 'none', border: 'none', cursor: 'pointer', fontFamily: mono, fontSize: '0.75rem', color: signal.cyan, padding: 0 }}>Open the compass →</button>
          </div>
        </div>
      </div>
    </main>
  )
}
