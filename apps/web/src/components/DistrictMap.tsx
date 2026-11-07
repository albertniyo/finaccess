import { useMemo } from 'react'
import type { GeoCollection, GeoFeature } from '../api/types'

const WIDTH = 600

type Props = {
  geo: GeoCollection
  fill: (district: string) => string
  label: (district: string) => string
  selected: string | null
  dimmed?: (district: string) => boolean
  onSelect: (district: string) => void
}

function rings(feature: GeoFeature): number[][][] {
  return feature.geometry.type === 'Polygon' ? feature.geometry.coordinates : feature.geometry.coordinates.flat()
}

/** Equirectangular projection with cos(latitude) correction — accurate enough for Rwanda's extent. */
function useProjection(geo: GeoCollection) {
  return useMemo(() => {
    let minX = Infinity
    let maxX = -Infinity
    let minY = Infinity
    let maxY = -Infinity
    for (const f of geo.features) {
      for (const ring of rings(f)) {
        for (const [x, y] of ring) {
          minX = Math.min(minX, x)
          maxX = Math.max(maxX, x)
          minY = Math.min(minY, y)
          maxY = Math.max(maxY, y)
        }
      }
    }
    const k = Math.cos((((minY + maxY) / 2) * Math.PI) / 180)
    const scale = WIDTH / ((maxX - minX) * k)
    const height = (maxY - minY) * scale
    const project = ([x, y]: number[]) => [((x - minX) * k * scale).toFixed(1), ((maxY - y) * scale).toFixed(1)]
    const paths = geo.features.map((f) => ({
      district: f.properties.district,
      d: rings(f)
        .map((ring) => `M${ring.map((pt) => project(pt).join(',')).join('L')}Z`)
        .join(''),
    }))
    return { paths, height }
  }, [geo])
}

export function DistrictMap({ geo, fill, label, selected, dimmed, onSelect }: Props) {
  const { paths, height } = useProjection(geo)
  return (
    <svg
      className="district-map"
      viewBox={`-4 -4 ${WIDTH + 8} ${height + 8}`}
      role="group"
      aria-label="Map of Rwanda's 30 districts"
    >
      {paths.map((p) => {
        const isSelected = p.district === selected
        return (
          <path
            key={p.district}
            d={p.d}
            fill={fill(p.district)}
            className={`district${isSelected ? ' selected' : ''}${dimmed?.(p.district) ? ' dimmed' : ''}`}
            tabIndex={0}
            role="button"
            aria-pressed={isSelected}
            aria-label={label(p.district)}
            onClick={() => onSelect(p.district)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault()
                onSelect(p.district)
              }
            }}
          >
            <title>{label(p.district)}</title>
          </path>
        )
      })}
    </svg>
  )
}
