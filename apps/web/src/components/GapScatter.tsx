import type { DistrictRow } from '../api/types'
import { PROFILE_COLORS } from '../lib/format'

const W = 560
const H = 340
const PAD = { left: 48, right: 16, top: 16, bottom: 42 }

type Props = {
  districts: DistrictRow[]
  nationalPoverty: number
  nationalExclusion: number
  selected: string | null
  onSelect: (district: string) => void
}

type Placement = { dx: number; dy: number; anchor: 'start' | 'end' }

const PLACEMENTS: Placement[] = [
  { dx: 8, dy: -6, anchor: 'start' },
  { dx: -8, dy: -6, anchor: 'end' },
  { dx: 8, dy: 15, anchor: 'start' },
  { dx: -8, dy: 15, anchor: 'end' },
]

/** Greedy label placement: notable districts get a label only where it does not collide. */
function placeLabels(
  points: { name: string; px: number; py: number; priority: number; force: boolean }[],
): Map<string, Placement> {
  const boxes: [number, number, number, number][] = []
  const placed = new Map<string, Placement>()
  for (const p of [...points].sort((a, b) => b.priority - a.priority)) {
    const w = p.name.length * 6.3
    for (const pl of PLACEMENTS) {
      const x0 = pl.anchor === 'start' ? p.px + pl.dx : p.px + pl.dx - w
      const y0 = p.py + pl.dy - 10
      const box: [number, number, number, number] = [x0, y0, x0 + w, y0 + 12]
      const clash = boxes.some((b) => box[0] < b[2] && box[2] > b[0] && box[1] < b[3] && box[3] > b[1])
      const outside = box[0] < PAD.left || box[2] > W - PAD.right || box[1] < 0
      if ((!clash && !outside) || (p.force && pl === PLACEMENTS[PLACEMENTS.length - 1])) {
        boxes.push(box)
        placed.set(p.name, pl)
        break
      }
    }
  }
  return placed
}

/** Poverty (EICV7) vs financial exclusion (FinScope) with national reference lines. */
export function GapScatter({ districts, nationalPoverty, nationalExclusion, selected, onSelect }: Props) {
  const xMax = Math.ceil(Math.max(...districts.map((d) => d.poverty_rate.value), nationalPoverty) / 10) * 10
  const yMax = Math.max(12, ...districts.map((d) => d.excluded.value + 1))
  const x = (v: number) => PAD.left + (v / xMax) * (W - PAD.left - PAD.right)
  const y = (v: number) => H - PAD.bottom - (v / yMax) * (H - PAD.top - PAD.bottom)
  const xTicks = Array.from({ length: xMax / 10 + 1 }, (_, i) => i * 10)
  const yTicks = Array.from({ length: Math.floor(yMax / 2) + 1 }, (_, i) => i * 2)
  const labels = placeLabels(
    districts
      .filter((d) => d.district === selected || d.excluded.value > nationalExclusion || d.poverty_rate.value >= 40)
      .map((d) => ({
        name: d.district,
        px: x(d.poverty_rate.value),
        py: y(d.excluded.value),
        force: d.district === selected,
        priority: (d.district === selected ? 1000 : 0) + d.excluded.value * 3 + d.poverty_rate.value / 10,
      })),
  )

  return (
    <figure className="scatter">
      <svg viewBox={`0 0 ${W} ${H}`} role="group" aria-label="Scatter plot of poverty against financial exclusion by district">
        <rect
          x={x(nationalPoverty)}
          y={PAD.top}
          width={x(xMax) - x(nationalPoverty)}
          height={y(nationalExclusion) - PAD.top}
          className="quadrant-hot"
        />
        {xTicks.map((t) => (
          <g key={`x${t}`}>
            <line x1={x(t)} x2={x(t)} y1={PAD.top} y2={H - PAD.bottom} className="grid" />
            <text x={x(t)} y={H - PAD.bottom + 16} textAnchor="middle" className="tick">
              {t}%
            </text>
          </g>
        ))}
        {yTicks.map((t) => (
          <g key={`y${t}`}>
            <line x1={PAD.left} x2={W - PAD.right} y1={y(t)} y2={y(t)} className="grid" />
            <text x={PAD.left - 8} y={y(t) + 4} textAnchor="end" className="tick">
              {t}%
            </text>
          </g>
        ))}
        <line x1={x(nationalPoverty)} x2={x(nationalPoverty)} y1={PAD.top} y2={H - PAD.bottom} className="ref" />
        <line x1={PAD.left} x2={W - PAD.right} y1={y(nationalExclusion)} y2={y(nationalExclusion)} className="ref" />
        <text x={x(nationalPoverty) + 4} y={PAD.top + 12} className="ref-label">
          national poverty {nationalPoverty.toFixed(1)}%
        </text>
        <text x={PAD.left + 4} y={y(nationalExclusion) - 6} className="ref-label">
          national exclusion {nationalExclusion}%
        </text>
        <text x={(W + PAD.left) / 2} y={H - 6} textAnchor="middle" className="axis-label">
          Headcount poverty (EICV7 2023/24)
        </text>
        <text transform={`translate(14 ${(H - PAD.bottom + PAD.top) / 2}) rotate(-90)`} textAnchor="middle" className="axis-label">
          Financially excluded adults (FinScope 2024)
        </text>
        {districts.map((d) => {
          const isSel = d.district === selected
          const label = labels.get(d.district)
          return (
            <g
              key={d.district}
              className={`pt${isSel ? ' selected' : ''}`}
              tabIndex={0}
              role="button"
              aria-label={`${d.district}: poverty ${d.poverty_rate.value.toFixed(1)}%, excluded ${d.excluded.value}%`}
              onClick={() => onSelect(d.district)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault()
                  onSelect(d.district)
                }
              }}
            >
              <circle cx={x(d.poverty_rate.value)} cy={y(d.excluded.value)} r={isSel ? 7 : 5} fill={PROFILE_COLORS[d.profile.type]} />
              {label && (
                <text
                  x={x(d.poverty_rate.value) + label.dx}
                  y={y(d.excluded.value) + label.dy}
                  textAnchor={label.anchor}
                  className={`pt-label${isSel ? ' sel' : ''}`}
                >
                  {d.district}
                </text>
              )}
              <title>{`${d.district} — ${d.profile.label}`}</title>
            </g>
          )
        })}
      </svg>
      <figcaption>
        Shaded area: above the national rate on both. Exclusion values are whole percentages with about ±1–2 points
        of sampling error, so points on the same row are not meaningfully different.
      </figcaption>
    </figure>
  )
}
