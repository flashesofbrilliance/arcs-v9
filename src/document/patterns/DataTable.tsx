'use client'
import React from 'react'
import { T } from '../tokens'

export interface DataTableProps {
  columns: React.ReactNode[]
  rows: React.ReactNode[][]
}

export function DataTable({ columns, rows }: DataTableProps) {
  return (
    <div style={{ borderRadius: 10, overflow: 'hidden', border: `1px solid ${T.border}` }}>
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr style={{ background: '#070b10' }}>
            {columns.map((c, i) => <th key={i} style={{ padding: '9px 14px', textAlign: 'left', fontFamily: T.mono, fontSize: 9, fontWeight: 700, color: T.fg4, letterSpacing: '0.1em', textTransform: 'uppercase', borderBottom: `1px solid ${T.border}` }}>{c}</th>)}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={i} style={{ background: i % 2 === 0 ? T.surface : '#090d14' }}>
              {row.map((cell, j) => <td key={j} style={{ padding: '9px 14px', borderTop: `1px solid ${T.border}`, fontFamily: j === 0 ? T.mono : T.sans, fontSize: 13, color: j === 0 ? T.fg3 : T.fg2, lineHeight: 1.5 }}>{cell}</td>)}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
