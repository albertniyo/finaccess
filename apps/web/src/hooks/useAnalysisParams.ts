import { useCallback } from 'react'
import { useSearchParams } from 'react-router-dom'
import type { Measure } from '../api/types'

export const DEFAULT_POVERTY_WEIGHT = 0.5
export const DEFAULT_MEASURE: Measure = 'excluded'

/** Weights and measure live in the URL so Priorities → Brief links carry the same assumptions. */
export function useAnalysisParams() {
  const [params, setParams] = useSearchParams()
  const rawWeight = Number(params.get('pw'))
  const povertyWeight =
    params.has('pw') && Number.isFinite(rawWeight) && rawWeight >= 0 && rawWeight <= 1
      ? rawWeight
      : DEFAULT_POVERTY_WEIGHT
  const measure: Measure = params.get('m') === 'not_formally_served' ? 'not_formally_served' : DEFAULT_MEASURE

  const update = useCallback(
    (next: Partial<{ povertyWeight: number; measure: Measure; district: string | null }>) => {
      setParams(
        (prev) => {
          const out = new URLSearchParams(prev)
          if (next.povertyWeight !== undefined) out.set('pw', next.povertyWeight.toFixed(2))
          if (next.measure !== undefined) out.set('m', next.measure)
          if (next.district !== undefined) {
            if (next.district) out.set('d', next.district)
            else out.delete('d')
          }
          return out
        },
        { replace: true },
      )
    },
    [setParams],
  )

  return { povertyWeight, measure, district: params.get('d'), update }
}

export function analysisQuery(povertyWeight: number, measure: Measure, district?: string) {
  const q = new URLSearchParams({ pw: povertyWeight.toFixed(2), m: measure })
  if (district) q.set('d', district)
  return `?${q}`
}
