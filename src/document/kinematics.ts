// Belief-trajectory kinematics, shared by the war-room screen and the
// war-room -> RecoilReport adapter. Central difference, identical to
// scripts/recoil_brief.py's stdlib fallback (and arcs_kinematics.py's D1-D3).

export function grad(f: number[], dt: number): number[] {
  const n = f.length
  if (n < 2) return f.map(() => 0)
  return f.map((_, i) => (i === 0 ? (f[1] - f[0]) / dt : i === n - 1 ? (f[n - 1] - f[n - 2]) / dt : (f[i + 1] - f[i - 1]) / (2 * dt)))
}

export const r3 = (x: number) => Math.round(x * 1000) / 1000

/** D1 peak/terminal, D2 terminal, D3 terminal for one series. */
export function derivatives(points: number[], dt: number) {
  const v = grad(points, dt), a = grad(v, dt), j = grad(a, dt)
  return {
    d1Peak: r3(Math.max(...v.map(Math.abs))),
    d1Term: r3(v[v.length - 1]),
    d2Term: r3(a[a.length - 1]),
    d3Term: r3(j[j.length - 1]),
  }
}

export const kinematicsNote = (n: number) =>
  `n=${n} points: D1-D2 valid, D3 marginal, D4+ undersampled. Central difference, same as scripts/recoil_brief.py.`
