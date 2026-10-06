'use client'
import React from 'react'
import { font, text, contentContainer } from '@/ui/tokens'
import { useVw } from '@/ui/useVw'
import { Wordmark } from '@/ui/Wordmark'
import { Rule } from '@/ui/Rule'
import { Button } from '@/ui/Button'
import { AhmedOrder, MEASURE } from '@/organisms/AhmedOrder'
import { SITUATION_LABEL } from '@/lib/vocabulary'
import type { CompassResult } from '@/lib/mockCompass'

// The brief is the receipt in the Ahmed order plus the brief writer's framing.
// Same slots, same words, same positions as /receipt (src/lib/vocabulary.ts).
export interface BriefProps {
  result: CompassResult
  onBack?: () => void
  onTributary?: (prompt: string) => void
  onNewQuestion?: () => void
  // Brief-writer situation framing (two paragraphs).
  situationFraming?: string
}

export function Brief({ result, onBack, onTributary, onNewQuestion, situationFraming }: BriefProps) {
  const r = result.reasoning || {}
  const vw = useVw()
  const framing = situationFraming?.trim()

  return (
    <div style={{ ...contentContainer(vw), paddingTop: '2rem', paddingBottom: '5rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '0.5rem', flexWrap: 'wrap', marginBottom: '1rem' }}>
        <Wordmark section="Decision Brief" />
        <div style={{ display: 'flex', gap: '0.25rem' }}>
          {onBack && <Button variant="ghost" size="sm" onClick={onBack}>← Ledger</Button>}
          {onNewQuestion && <Button variant="ghost" size="sm" glyph="⊕" onClick={onNewQuestion}>New question</Button>}
        </div>
      </div>
      <Rule style={{ marginBottom: '1.75rem' }} />

      <AhmedOrder
        data={{
          decision: result.question ?? '',
          trueNorth: result.true_north,
          yState: result.y_state,
          renderResolution: result.render_resolution,
          mode: result.decision_mode,
          doorClass: result.door_class,
          stakes: result.stakes,
          horizon: result.horizon,
          reasons: result.why ?? [],
          questions: result.tributaries ?? [],
          paths: r.paths ?? [],
          fated: r.fated,
          court: r.court,
          courtVerdict: r.court_verdict,
          bayesianRiskPct: r.advisors?.bayesian_risk_pct,
          nciScore: result.nci_score,
          coherencePct: result.coherence_pct,
          macroTags: result.macro_tags,
        }}
        onQuestion={onTributary}
        after={framing ? (
          <section aria-labelledby="slot-situation" style={{ marginTop: '2.75rem' }}>
            <h2 id="slot-situation" style={{ fontFamily: font.mono, ...font.tier.t6, textTransform: 'uppercase', color: text.muted, margin: '0 0 0.9rem' }}>{SITUATION_LABEL}</h2>
            {framing.split(/\n\s*\n/).map((para, i) => (
              <p key={i} style={{ fontFamily: font.sans, fontSize: '0.925rem', color: text.secondary, lineHeight: 1.65, margin: i ? '0.9rem 0 0' : 0, maxWidth: MEASURE, textWrap: 'pretty' }}>{para}</p>
            ))}
          </section>
        ) : null}
      />
    </div>
  )
}
