import type { AccessStrand } from '../api/types'

const SEGMENTS: { key: keyof AccessStrand; label: string }[] = [
  { key: 'banked', label: 'Banked' },
  { key: 'other_formal', label: 'Other formal (non-bank)' },
  { key: 'informal_only', label: 'Informal only' },
  { key: 'excluded', label: 'Excluded' },
]

/** FinScope access strand as a single stacked bar (segments are mutually exclusive). */
export function StrandBar({ strand, compact = false }: { strand: AccessStrand; compact?: boolean }) {
  const total = SEGMENTS.reduce((s, seg) => s + strand[seg.key], 0) || 1
  return (
    <div className={`strand${compact ? ' compact' : ''}`}>
      <div className="strand-bar" role="img" aria-label={SEGMENTS.map((s) => `${s.label} ${strand[s.key]}%`).join(', ')}>
        {SEGMENTS.map((seg) => (
          <span
            key={seg.key}
            className={`seg seg-${seg.key}`}
            style={{ width: `${(strand[seg.key] / total) * 100}%` }}
            title={`${seg.label}: ${strand[seg.key]}%`}
          >
            {!compact && strand[seg.key] >= 4 ? strand[seg.key] : ''}
          </span>
        ))}
      </div>
      {!compact && (
        <ul className="legend-list">
          {SEGMENTS.map((seg) => (
            <li key={seg.key}>
              <span className={`swatch seg-${seg.key}`} aria-hidden="true" />
              {seg.label} {strand[seg.key]}%
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
