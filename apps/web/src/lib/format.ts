import type { Estimate, IndicatorId, IndicatorMeta, ProfileType } from '../api/types'

export const pct = (value: number, digits = 1) => `${value.toFixed(digits)}%`

export const share = (value: number) => `${Math.round(value * 100)}%`

const ONE_DECIMAL: IndicatorId[] = [
  'poverty_rate',
  'mobile_phone_households',
  'smartphone_households',
  'internet_households',
  'health_insurance',
]

export function formatEstimate(est: Estimate, id: IndicatorId) {
  if (id === 'poverty_decrease') return `${est.value.toFixed(1)} pp`
  return pct(est.value, ONE_DECIMAL.includes(id) ? 1 : 0)
}

export function formatCi(est: Estimate) {
  if (est.uncertainty === 'modelled') {
    return est.poverty_2017_modelled != null ? `from ${est.poverty_2017_modelled.toFixed(1)}% (modelled)` : 'modelled'
  }
  if (!est.ci) return ''
  const [lo, hi] = est.ci
  return `${lo.toFixed(1)}–${hi.toFixed(1)}${est.uncertainty === 'approximate' ? ' (approx.)' : ''}`
}

export const rwf = (value: number) =>
  new Intl.NumberFormat('en-RW', {
    style: 'currency',
    currency: 'RWF',
    currencyDisplay: 'code',
    maximumFractionDigits: 0,
  }).format(value)

export const PROFILE_COLORS: Record<ProfileType, string> = {
  compound_gap: '#ef7d7d',
  poverty_led: '#efa95a',
  access_gap: '#8b67f2',
  lower_relative_need: '#8db596',
}

const STOPS = ['#f3effe', '#dcd0fc', '#b9a3f8', '#8b67f2', '#5b3fc4']

function hexToRgb(hex: string) {
  const n = parseInt(hex.slice(1), 16)
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255]
}

/** Sequential lavender scale where darker always means "more concern" for the chosen indicator. */
export function concernColor(value: number, min: number, max: number, meta: IndicatorMeta) {
  let t = max > min ? (value - min) / (max - min) : 0
  if (!meta.higher_is_worse) t = 1 - t
  t = Math.min(1, Math.max(0, t))
  const pos = t * (STOPS.length - 1)
  const i = Math.min(STOPS.length - 2, Math.floor(pos))
  const f = pos - i
  const a = hexToRgb(STOPS[i])
  const b = hexToRgb(STOPS[i + 1])
  const c = a.map((v, k) => Math.round(v + (b[k] - v) * f))
  return `rgb(${c[0]}, ${c[1]}, ${c[2]})`
}

export const CONCERN_GRADIENT = `linear-gradient(90deg, ${STOPS.join(', ')})`
