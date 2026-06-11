'use client'
import React from 'react'
import { T } from '../tokens'
import { Sec } from '../primitives'
import { CoverBlock } from '../patterns/CoverBlock'
import { SmartGrid } from '../patterns/SmartGrid'
import { ProcessSteps } from '../patterns/ProcessSteps'
import { DataTable } from '../patterns/DataTable'
import { AsideBox } from '../patterns/AsideBox'

export interface PrepDocProps { data?: Partial<typeof PREP_SAMPLE> }

export const PREP_SAMPLE = {
  cover: {
    badges: ['Prep Doc', 'Tactical · Walk-In Protocol'],
    title: 'Panel of 2 — Walk-In Protocol',
    subtitle: 'Tactical sequence for the second-round panel. This is the behavioral protocol, not the strategy. The strategy lives in the Brief. This is execution.',
    meta: 'ARCS PREP · Jun 2026 · PANEL OF 2 · 60 MIN',
    actions: ['Simulate', 'Open Brief'],
  },
}

export function PrepDoc({ data }: PrepDocProps = {}) {
  const A = T.orange
  const d = { ...PREP_SAMPLE, ...data }
  return (
    <div>
      <CoverBlock {...d.cover} accent={A} />

      <Sec id="pp-facts" idx="01" label="Key Facts" title="What You Need to Know Cold" accent={A}>
        <SmartGrid cols={3} items={[
          { label: 'Format', color: A, title: 'Panel of 2', body: 'Two interviewers. Unknown who has final-call authority. Treat both as decision-makers.' },
          { label: 'Duration', color: A, title: '60 min', body: 'Likely 5 min intro, 45 min questions, 10 min your questions. Time is compressed versus the screen.' },
          { label: 'Tone', color: A, title: 'Warmer Screen → Harder Panel', body: 'Jon was warm. The panel will be calibrated. Harder clock. Less charitable on verbosity.' },
          { label: 'Fix', color: T.red, title: 'Lead-With-The-Point', body: 'Answer in ≤2 sentences first. Pause. Offer to expand. Do not expand unless asked.' },
          { label: 'Signal', color: T.green, title: 'Builder Archetype', body: '"Opinion earns a seat at the table." Demonstrate this — don\'t claim it. Stack walk worked; repeat the pattern.' },
          { label: 'Ask', color: T.cyan, title: 'One Disambiguating Question', body: '"Is this role defining the measurement strategy, or implementing an existing one?" Her answer locates the scenario.' },
        ]} />
      </Sec>

      <Sec id="pp-protocol" idx="02" label="Protocol" title="Walk-In Sequence" accent={A}>
        <ProcessSteps accent={A} steps={[
          { label: 'Phase 01', title: 'Open at Executive Altitude', body: 'Demonstrate you understand the strategic frame: the design graph, the intent graph, the AI choke point. Don\'t anchor to scope until you\'ve established altitude.', active: true },
          { label: 'Phase 02', title: 'Let the Interviewer Calibrate', body: 'Pause after every substantive answer. Read the signal. Don\'t anchor on the base case before you know if the best case is on the table.' },
          { label: 'Phase 03', title: 'Drop the Disambiguating Question', body: '"Is this role defining the measurement strategy, or implementing an existing one?" Drop it when there\'s natural space — don\'t force it. Her answer tells you which scenario you\'re in.' },
          { label: 'Phase 04', title: 'Land at the Scenario You\'re Actually In', body: 'Map the response to best/base/worst. Adjust depth, altitude, and investment accordingly. Close with the builder sequence — not the strategist sequence.' },
          { label: 'Phase 05', title: 'Close with Conviction', body: 'One clear ask: "I\'d like to understand the timeline for next steps." Don\'t soften it. Don\'t add qualifiers. State it and wait.' },
        ]} />
      </Sec>

      <Sec id="pp-room" idx="03" label="Room Map" title="People in the Room" accent={A}>
        <DataTable
          columns={['Name', 'Role', 'Known Signal', 'Watch For']}
          rows={[
            ['Interviewer A', 'DS Lead or PM', 'Unknown — research before call', 'Calibrate: strategic vs. execution orientation'],
            ['Interviewer B', 'Unknown', 'Unknown', 'May be the real decision-maker — treat symmetrically'],
            ['Jon Smyrl', 'Recruiter (screen)', 'Warm, fast, concision-rewarded', 'Not in the room — his read shaped the invite'],
          ]}
        />
      </Sec>

      <Sec id="pp-watch" idx="04" label="Watch For" title="Behavioral Triggers" accent={A}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          <AsideBox variant="warning" label="Stop Signal">If interviewer interrupts or completes your sentence: that is a hard stop. Not a politeness cue — a behavioral read. Stop immediately.</AsideBox>
          <AsideBox variant="caution" label="Verbosity Trigger">Open prompts (&quot;Tell me about yourself&quot;, &quot;Walk me through&quot;) are the highest-risk moments. Answer in ≤2 sentences first. Full stop. Offer to expand.</AsideBox>
          <AsideBox variant="success" label="Builder Sequence">Stack walk + stateful file system + decision-receipt logic = the sequence that closed the screen warmly. Have it ready. It will close this too.</AsideBox>
        </div>
      </Sec>
    </div>
  )
}
