import type { Kind } from '../api/types'

const LABELS: Record<Kind, string> = {
  observed: 'Observed',
  estimate: 'Estimate',
  scenario: 'Scenario',
  recommendation: 'Recommendation',
}

const TITLES: Record<Kind, string> = {
  observed: 'Published statistic from NISR / AFR',
  estimate: 'Our calculation from published statistics, under stated assumptions',
  scenario: 'Hypothetical — not a prediction of impact',
  recommendation: 'Suggested next step for investigation, not a finding',
}

export function Badge({ kind }: { kind: Kind }) {
  return (
    <span className={`badge badge-${kind}`} title={TITLES[kind]}>
      {LABELS[kind]}
    </span>
  )
}
