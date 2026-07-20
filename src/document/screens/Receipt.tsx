'use client'
import React from 'react'
import { T } from '../tokens'
import { Sec } from '../primitives'
import { CoverBlock } from '../patterns/CoverBlock'
import { QuoteBlock } from '../patterns/QuoteBlock'
import { TwoColumn } from '../patterns/TwoColumn'
import { SidelineList } from '../patterns/SidelineList'
import { DataTable } from '../patterns/DataTable'
import { AsideBox } from '../patterns/AsideBox'

export interface ReceiptProps { data?: Partial<typeof RECEIPT_SAMPLE> }

export const RECEIPT_SAMPLE = {
  cover: {
    badges: ['Decision Receipt', 'Immutable · QUICKMOVE'],
    title: 'RECEIPT-1713945480-4XK7P',
    subtitle: 'Should we ship the MVP this Friday, or wait one more week for the polish pass? Decision committed Jun 24, 2026 · 16:18 UTC.',
    meta: 'ARCS RECEIPT · QUICKMOVE · IMMUTABLE · DO NOT MODIFY',
    actions: ['Export JSON', 'Reopen as Question'],
  },
}

export function Receipt({ data }: ReceiptProps = {}) {
  const A = T.steel
  const d = { ...RECEIPT_SAMPLE, ...data }
  return (
    <div>
      <CoverBlock {...d.cover} accent={A} />

      <Sec id="rc-decision" idx="01" label="Decision" title="True North" accent={A}>
        <QuoteBlock accent={T.green} attribution="QUICKMOVE · confidence: 0.78">
          Ship Friday. Instrument the live surface so next week&apos;s call is data-driven, not opinion-driven.
        </QuoteBlock>
      </Sec>

      <Sec id="rc-schema" idx="02" label="Schema" title="Prediction vs. Audit" accent={A}>
        <TwoColumn accent={A}
          left={{
            heading: 'Prediction Block',
            items: ['Mode: <b>QUICKMOVE</b>', 'True North: Ship Friday. Instrument the live surface.', 'Confidence: 0.78', 'Horizon: THIS_WEEK', 'Stakes: MEDIUM'],
          }}
          right={{
            heading: 'Audit Block',
            items: ['Cognitive Mass: <b>LOW</b>', 'Semantic Velocity: <b>0.82</b>', 'Clarity: SIMPLE', 'Drift: CLEAN', 'Turns: 3'],
          }}
        />
      </Sec>

      <Sec id="rc-why" idx="03" label="Reasoning" title="Why Bullets" accent={A}>
        <SidelineList items={[
          { label: 'Why 01', accent: T.green, title: 'Reversibility is high', body: 'Stakes read MEDIUM. The surface is instrumented and recoverable inside 48 hours. Reversibility is the key variable, and it\'s favorable.' },
          { label: 'Why 02', accent: T.cyan, title: 'Polish debt vs. ship debt', body: 'The polish Priya wants is observable. Once live data flows you can prioritize the exact pixels that move the needle. Holding a week accrues more opinion-debt than ship-debt.' },
          { label: 'Why 03', accent: T.gold, title: 'Real uncertainty is about signal, not polish', body: 'The team\'s actual question is: what do users do with this surface? That question only answers with live data. No amount of polish resolves it before ship.' },
        ]} />
      </Sec>

      <Sec id="rc-readings" idx="04" label="Signal Readings" title="Full Schema Ledger" accent={A}>
        <DataTable
          columns={['Field', 'Value', 'Block']}
          rows={[
            ['id', 'RECEIPT-1713945480-4XK7P', 'root'],
            ['question', 'Should we ship the MVP this Friday…', 'root'],
            ['horizon', 'THIS_WEEK', 'root'],
            ['stakes', 'MEDIUM', 'root'],
            ['mode', 'QUICKMOVE', 'prediction'],
            ['confidence', '0.78', 'prediction'],
            ['cognitive_mass', 'LOW', 'audit'],
            ['semantic_velocity', '0.82', 'audit'],
            ['clarity', 'SIMPLE', 'audit'],
            ['drift', 'CLEAN', 'audit'],
            ['turns', '3', 'audit'],
            ['jtbd_anchor', 'Ship decision-support users trust under pressure', 'mirror'],
            ['next', 'Announce in #standup, instrument v1 before noon', 'mirror'],
          ]}
        />
      </Sec>

      <Sec id="rc-mirror" idx="05" label="Mirror Block" title="JTBD Anchor + Next" accent={A}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          <AsideBox variant="info" label="JTBD Anchor">Ship a decision-support surface that users trust under pressure.</AsideBox>
          <AsideBox variant="success" label="Next Action">Commit the decision in #standup, publish the receipt, instrument the v1 surface with event beacons before noon.</AsideBox>
          <AsideBox variant="caution" label="Immutability Notice">This receipt is sealed. If the decision was wrong, open a new question and file a correction receipt. Do not modify this record.</AsideBox>
        </div>
      </Sec>
    </div>
  )
}
