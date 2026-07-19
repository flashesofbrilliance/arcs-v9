'use client'
import { useRouter } from 'next/navigation'
import { surface, text, signal, font, border } from '@/ui/tokens'
import { Wordmark } from '@/ui/Wordmark'
import { Rule } from '@/ui/Rule'

const mono = font.mono
const sans = font.sans

const chip = (icon: string, label: string, body: string) => (
  { icon, label, body }
)

const CHIPS = [
  chip('lock', 'Storage', 'Nothing stored without sign-in'),
  chip('forbid', 'Training', 'Input never trains a model'),
  chip('user-check', 'Autonomy', 'You decide. ARCS doesn\'t.'),
  chip('code', 'Source', 'Repo is public and forkable'),
]

const GRADES = [
  { key: 'GREEN', color: signal.green, body: 'Coherent, well-supported bearing. Move — but stay alert to new information.' },
  { key: 'YELLOW', color: signal.gold, body: 'Contested terrain. Cross-check your assumptions before committing.' },
  { key: 'SCRATCH / FORK', color: text.muted, body: "Ground isn't stable. Don't decide yet — probe the terrain first." },
  { key: 'PARADOX', color: signal.red, body: 'Premature. The question needs more time or a different framing.' },
]

export default function TrustPage() {
  const router = useRouter()

  return (
    <main style={{ minHeight: '100vh', background: surface.bg, color: text.primary }}>
      <div style={{ maxWidth: 700, margin: '0 auto', padding: '2rem 1.5rem 5rem' }}>

        {/* Nav */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingBottom: '1rem' }}>
          <button onClick={() => router.push('/')} style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 0 }}>
            <Wordmark section="Trust Contract" />
          </button>
        </div>
        <Rule style={{ marginBottom: '2rem' }} />

        {/* Lede */}
        <p style={{ fontFamily: mono, fontSize: '0.8125rem', color: text.muted, lineHeight: 1.6, margin: '0 0 1.75rem', letterSpacing: '0.01em' }}>
          Before you run the compass — what you're agreeing to, what we store, and what we won't do. Plain language. No buried terms.
        </p>

        <h1 style={{ fontFamily: sans, fontSize: '1.6rem', fontWeight: 600, color: text.primary, margin: '0 0 0.5rem', lineHeight: 1.15, letterSpacing: '-0.02em' }}>
          What you're entering into
        </h1>
        <p style={{ fontFamily: sans, fontSize: '0.9375rem', color: text.secondary, margin: '0 0 2.25rem', lineHeight: 1.5 }}>
          Eight commitments. Read them once. They don't change without notice.
        </p>

        {/* Chips */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: 10, marginBottom: '2.5rem' }}>
          {CHIPS.map(c => (
            <div key={c.label} style={{ background: surface.panel, border: `0.5px solid ${border.subtle}`, borderRadius: 8, padding: '0.85rem 1rem' }}>
              <div style={{ fontFamily: mono, fontSize: '0.625rem', textTransform: 'uppercase', letterSpacing: '0.1em', color: text.muted, marginBottom: '0.35rem' }}>{c.label}</div>
              <div style={{ fontFamily: sans, fontSize: '0.8125rem', color: text.primary, fontWeight: 500, lineHeight: 1.3 }}>{c.body}</div>
            </div>
          ))}
        </div>

        {/* Sections */}
        {[
          {
            n: '§ 01', title: 'What we store and what we don\'t',
            body: <>
              Anonymous sessions: <strong style={{ color: text.primary }}>nothing is stored.</strong> Your question and the bearing live only in your browser tab and disappear when you close it. Want to keep one? Sign in and save it — the write happens only after you authenticate. If you sign in, your receipts are stored so you can return to them. System logs don't contain your decision content — only request metadata (timestamps, response codes).
              <span style={{ display: 'block', marginTop: '0.75rem', fontSize: '0.85em', opacity: 0.85 }}>
                <strong style={{ color: text.primary }}>Sharing an anonymous bearing:</strong> if you create a one-time share link, the bearing is encoded <em>inside the link itself</em> (in the URL fragment, which browsers never send to a server) — still nothing on ours. The link opens once on the recipient's device, then becomes a sign-in page. Because the content rides in the link, treat it like any message you send: anyone you give it to can read it.
              </span>
              <span style={{ display: 'block', marginTop: '0.75rem', fontSize: '0.85em', opacity: 0.85 }}>
                <strong style={{ color: text.primary }}>Repair seam (2026-07-13), kept visible on purpose:</strong> until this date, a defect stored anonymous receipts server-side, contrary to this section — 48 existed when found. Fixed the same day (commit 8b486e8; the repo is public, so this is verifiable, not just claimed). The pre-fix receipts were kept rather than deleted because shared receipt links reference them; they carry no account identity. Sign in from the same browser to claim yours, or request deletion via the inquiry link below.
              </span>
            </>,
          },
          {
            n: '§ 02', title: 'We don\'t train on your input',
            body: <>
              ARCS runs through the Anthropic API. Per Anthropic's API terms, inputs are not used to train models. Your questions are not data collection — they're compass queries.
            </>,
          },
          {
            n: '§ 03', title: 'Export and delete',
            body: <>
              <strong style={{ color: text.primary }}>Delete:</strong> request within 30 days, one-way — receipts are gone, history can't be restored.{' '}
              <strong style={{ color: text.primary }}>Export:</strong> on the roadmap, not yet live. If you need your data before export is built, reach out directly.
            </>,
          },
          {
            n: '§ 04', title: 'You can run this yourself',
            body: <>
              The source is public at{' '}
              <a href="https://github.com/flashesofbrilliance/arcs-v9" target="_blank" rel="noopener noreferrer" style={{ color: signal.cyan, textDecoration: 'none' }}>
                github.com/flashesofbrilliance/arcs-v9
              </a>
              . Local-first mode is on the roadmap. If you want to run it without any data touching our infrastructure, that path will exist.
            </>,
          },
        ].map((s, i, arr) => (
          <div key={s.n}>
            <div style={{ marginBottom: '1.75rem' }}>
              <div style={{ fontFamily: mono, fontSize: '0.625rem', color: text.muted, letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: '0.3rem' }}>{s.n}</div>
              <div style={{ fontFamily: sans, fontSize: '0.9375rem', fontWeight: 500, color: text.primary, marginBottom: '0.5rem' }}>{s.title}</div>
              <div style={{ fontFamily: sans, fontSize: '0.875rem', color: text.secondary, lineHeight: 1.7 }}>{s.body}</div>
            </div>
            {i < arr.length - 1 && <div style={{ height: 1, background: border.subtle, marginBottom: '1.75rem' }} />}
          </div>
        ))}

        {/* Section 5 — for/not for */}
        <div style={{ height: 1, background: border.subtle, marginBottom: '1.75rem' }} />
        <div style={{ marginBottom: '1.75rem' }}>
          <div style={{ fontFamily: mono, fontSize: '0.625rem', color: text.muted, letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: '0.3rem' }}>§ 05</div>
          <div style={{ fontFamily: sans, fontSize: '0.9375rem', fontWeight: 500, color: text.primary, marginBottom: '0.75rem' }}>What ARCS is and isn't for</div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
            {[
              { head: 'Designed for', items: ['Decisions with real consequences', 'Forks you haven\'t mapped yet', 'High-pressure, time-sensitive calls', 'Multi-party decisions'] },
              { head: 'Not designed for', items: ['Rationalizing a decision already made', 'Professional legal or medical advice', 'Trivial choices with no real stakes', 'A replacement for human judgment'] },
            ].map(col => (
              <div key={col.head} style={{ background: surface.panel, border: `0.5px solid ${border.subtle}`, borderRadius: 8, padding: '0.75rem 0.9rem' }}>
                <div style={{ fontFamily: mono, fontSize: '0.625rem', textTransform: 'uppercase', letterSpacing: '0.1em', color: text.muted, marginBottom: '0.5rem' }}>{col.head}</div>
                {col.items.map(item => (
                  <div key={item} style={{ fontFamily: sans, fontSize: '0.8rem', color: text.secondary, lineHeight: 1.5, paddingBottom: '0.2rem' }}>
                    <span style={{ color: text.muted }}>· </span>{item}
                  </div>
                ))}
              </div>
            ))}
          </div>
        </div>

        {/* Section 6 — Conviction grades */}
        <div style={{ height: 1, background: border.subtle, marginBottom: '1.75rem' }} />
        <div style={{ marginBottom: '1.75rem' }}>
          <div style={{ fontFamily: mono, fontSize: '0.625rem', color: text.muted, letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: '0.3rem' }}>§ 06</div>
          <div style={{ fontFamily: sans, fontSize: '0.9375rem', fontWeight: 500, color: text.primary, marginBottom: '0.5rem' }}>How much weight to put on the output</div>
          <div style={{ fontFamily: sans, fontSize: '0.875rem', color: text.secondary, lineHeight: 1.7, marginBottom: '0.75rem' }}>
            NCI (Navigational Conviction Index) is a proxy, not ground truth. It reflects pattern coherence, not outcome probability. Here's how to read the grades:
          </div>
          <div style={{ border: `0.5px solid ${border.subtle}`, borderRadius: 8, overflow: 'hidden' }}>
            {GRADES.map((g, i) => (
              <div key={g.key} style={{ display: 'grid', gridTemplateColumns: '120px 1fr', borderBottom: i < GRADES.length - 1 ? `0.5px solid ${border.subtle}` : 'none' }}>
                <div style={{ padding: '0.65rem 0.85rem', fontFamily: mono, fontSize: '0.6875rem', fontWeight: 700, letterSpacing: '0.06em', color: g.color, display: 'flex', alignItems: 'center', borderRight: `0.5px solid ${border.subtle}` }}>{g.key}</div>
                <div style={{ padding: '0.65rem 0.9rem', fontFamily: sans, fontSize: '0.8rem', color: text.secondary, display: 'flex', alignItems: 'center', lineHeight: 1.4 }}>{g.body}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Section 7 — Autonomy */}
        <div style={{ height: 1, background: border.subtle, marginBottom: '1.75rem' }} />
        <div style={{ marginBottom: '1.75rem' }}>
          <div style={{ fontFamily: mono, fontSize: '0.625rem', color: text.muted, letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: '0.3rem' }}>§ 07</div>
          <div style={{ fontFamily: sans, fontSize: '0.9375rem', fontWeight: 500, color: text.primary, marginBottom: '0.5rem' }}>Your autonomy is the point</div>
          <div style={{ fontFamily: sans, fontSize: '0.875rem', color: text.secondary, lineHeight: 1.7, marginBottom: '0.75rem' }}>
            The governing rule of ARCS is called NOTOMATION: scaffold and sequence cognition. Never compress, replace, or overrule it.
          </div>
          <div style={{ borderLeft: `2px solid ${signal.cyan}40`, paddingLeft: '1rem' }}>
            <div style={{ fontFamily: sans, fontSize: '0.9375rem', color: text.primary, fontWeight: 500, lineHeight: 1.4 }}>ARCS does not make decisions. You do.</div>
            <div style={{ fontFamily: sans, fontSize: '0.8125rem', color: text.muted, marginTop: '0.25rem' }}>The compass shows terrain. The navigator chooses the line.</div>
          </div>
        </div>

        {/* Section 8 — Honest limits */}
        <div style={{ height: 1, background: border.subtle, marginBottom: '1.75rem' }} />
        <div style={{ marginBottom: '2rem' }}>
          <div style={{ fontFamily: mono, fontSize: '0.625rem', color: text.muted, letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: '0.3rem' }}>§ 08</div>
          <div style={{ fontFamily: sans, fontSize: '0.9375rem', fontWeight: 500, color: text.primary, marginBottom: '0.5rem' }}>How ARCS catches you at the fork</div>
          <div style={{ fontFamily: sans, fontSize: '0.875rem', color: text.secondary, lineHeight: 1.7, marginBottom: '0.75rem' }}>
            You might expect the system to detect when you're about to override a clear signal. Here's what's honest:
          </div>
          <div style={{ background: surface.panel, border: `0.5px solid ${border.subtle}`, borderRadius: 8, padding: '0.9rem 1.1rem' }}>
            <div style={{ fontFamily: mono, fontSize: '0.625rem', letterSpacing: '0.1em', textTransform: 'uppercase', color: text.muted, marginBottom: '0.4rem' }}>Current state</div>
            <div style={{ fontFamily: sans, fontSize: '0.8125rem', color: text.secondary, lineHeight: 1.65 }}>
              Kairos detection — the system that flags momentum building toward a decision point — is on the roadmap, not live yet.{' '}
              <strong style={{ color: text.primary }}>Right now, ARCS surfaces the terrain. You bring the awareness of where you are in the decision arc.</strong>{' '}
              The compass can't yet tell you "you're about to override a YELLOW with no new data." That's a gap we're naming, not hiding.
            </div>
          </div>
        </div>

        {/* Footer links */}
        <div style={{ height: 1, background: border.subtle, marginBottom: '1.5rem' }} />
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.75rem' }}>
          <span style={{ fontFamily: mono, fontSize: '0.75rem', color: text.muted }}>Trust contract v1.1 · last updated 2026-06-23</span>
          <div style={{ display: 'flex', gap: '1.25rem' }}>
            <button onClick={() => router.push('/privacy')} style={{ background: 'none', border: 'none', cursor: 'pointer', fontFamily: mono, fontSize: '0.75rem', color: text.muted, textDecoration: 'underline', padding: 0 }}>Privacy policy</button>
            <button onClick={() => router.push('/terms')} style={{ background: 'none', border: 'none', cursor: 'pointer', fontFamily: mono, fontSize: '0.75rem', color: text.muted, textDecoration: 'underline', padding: 0 }}>Terms of service</button>
            <button onClick={() => router.push('/dashboard')} style={{ background: 'none', border: 'none', cursor: 'pointer', fontFamily: mono, fontSize: '0.75rem', color: signal.cyan, padding: 0 }}>Open the compass →</button>
          </div>
        </div>
      </div>
    </main>
  )
}
