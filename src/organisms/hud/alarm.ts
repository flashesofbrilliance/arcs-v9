import { isGrain, type Reading } from './reading'

export interface TitledReading { title: string; reading: Reading }

// The one line the strip leads with: the single worst gauge, said in words.
// No source beats below-sample; all sharp prints no alarm. Nothing here is invented: it names the reading's own source and n.
export function alarmLine(rs: TitledReading[]): string | null {
  const none = rs.find((r) => r.reading.threshold === null)
  if (none) return `${none.title} has no signal (needs ${none.reading.source})`
  const grain = rs.find((r) => isGrain(r.reading))
  if (grain) return `${grain.title} is below its sample (n = ${grain.reading.n} of ${grain.reading.threshold})`
  return null
}
