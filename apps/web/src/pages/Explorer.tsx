import { useMemo, useState } from 'react'
import { getGeo, getIndicators } from '../api/client'
import type { DistrictRow, IndicatorId } from '../api/types'
import { Badge } from '../components/Badge'
import { DistrictMap } from '../components/DistrictMap'
import { EvidencePanel } from '../components/EvidencePanel'
import { GapScatter } from '../components/GapScatter'
import { ProfileSummary } from '../components/ProfileSummary'
import { ErrorState, Loading } from '../components/Status'
import { StrandBar } from '../components/StrandBar'
import { WhoIsExcluded } from '../components/WhoIsExcluded'
import { useAnalysisParams } from '../hooks/useAnalysisParams'
import { useApi } from '../hooks/useApi'
import { useDocumentTitle } from '../hooks/useDocumentTitle'
import { CONCERN_GRADIENT, concernColor, formatCi, formatEstimate } from '../lib/format'

type SortKey = 'district' | IndicatorId

export function Explorer() {
  useDocumentTitle('Explore gaps')
  const indicators = useApi('indicators', () => getIndicators())
  const geo = useApi('geo', getGeo)
  const { povertyWeight, measure, district: selected, update } = useAnalysisParams()
  const [indicatorId, setIndicatorId] = useState<IndicatorId>('poverty_rate')
  const [province, setProvince] = useState('')
  const [sort, setSort] = useState<{ key: SortKey; desc: boolean }>({ key: 'poverty_rate', desc: true })

  const data = indicators.data
  const meta = data?.indicators.find((i) => i.id === indicatorId)
  const byName = useMemo(() => new Map(data?.districts.map((d) => [d.district, d]) ?? []), [data])
  const visible = useMemo(
    () => (data?.districts ?? []).filter((d) => !province || d.province === province),
    [data, province],
  )
  const sorted = useMemo(() => {
    const rows = [...visible]
    rows.sort((a, b) => {
      const cmp =
        sort.key === 'district' ? a.district.localeCompare(b.district) : a[sort.key].value - b[sort.key].value
      return sort.desc ? -cmp : cmp
    })
    return rows
  }, [visible, sort])

  if (indicators.error) return <ErrorState error={indicators.error} onRetry={indicators.reload} />
  if (!data || !meta) return <Loading />

  const values = data.districts.map((d) => d[indicatorId].value)
  const min = Math.min(...values)
  const max = Math.max(...values)
  const select = (name: string | null) => update({ district: name === selected ? null : name })
  const gapDistricts = data.districts.filter((d) => d.profile.type === 'access_gap').map((d) => d.district)

  const sortHeader = (key: SortKey, label: string) => (
    <th scope="col" aria-sort={sort.key === key ? (sort.desc ? 'descending' : 'ascending') : 'none'}>
      <button
        type="button"
        className="sort-btn"
        onClick={() => setSort((s) => ({ key, desc: s.key === key ? !s.desc : key !== 'district' }))}
      >
        {label}
        {sort.key === key ? (sort.desc ? ' ▼' : ' ▲') : ''}
      </button>
    </th>
  )

  return (
    <section className="page">
      <p className="eyebrow">Step 1 · Explore</p>
      <h1>Intervention Gap Explorer</h1>
      <p className="lede">
        Where do high poverty and weak financial access overlap — and where does one appear without the
        other? District aggregates from two separate official surveys, compared side by side.
      </p>

      <div className="controls" role="group" aria-label="Explorer filters">
        <label>
          Map indicator
          <select value={indicatorId} onChange={(e) => setIndicatorId(e.target.value as IndicatorId)}>
            {(
              [
                ['core', 'Poverty & financial access'],
                ['context', 'Context'],
              ] as const
            ).map(([group, label]) => (
              <optgroup key={group} label={label}>
                {data.indicators
                  .filter((i) => i.group === group)
                  .map((i) => (
                    <option key={i.id} value={i.id}>
                      {i.label}
                    </option>
                  ))}
              </optgroup>
            ))}
          </select>
        </label>
        <label>
          Province
          <select value={province} onChange={(e) => setProvince(e.target.value)}>
            <option value="">All provinces</option>
            {data.filters.available.province.map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>
        </label>
        <p className="small muted filter-note">
          Urban/rural, sex and age splits are not published at district level for both surveys, so they are not
          offered here.
        </p>
      </div>

      <div className="indicator-card">
        <p>
          <Badge kind="observed" /> <strong>{meta.label}</strong> ({meta.unit}) — {meta.definition}
        </p>
        <p className="small muted">
          Source: {meta.survey}, {meta.reference}. Geographic level: district. Uncertainty: {meta.uncertainty}.
        </p>
      </div>

      <div className="explore-grid">
        <div className="map-wrap">
          {geo.error ? (
            <ErrorState error={geo.error} onRetry={geo.reload} />
          ) : geo.data ? (
            <DistrictMap
              geo={geo.data}
              selected={selected}
              onSelect={select}
              dimmed={(name) => !!province && byName.get(name)?.province !== province}
              fill={(name) => {
                const row = byName.get(name)
                return row ? concernColor(row[indicatorId].value, min, max, meta) : '#ddd'
              }}
              label={(name) => {
                const row = byName.get(name)
                return row ? `${name}: ${meta.label} ${formatEstimate(row[indicatorId], indicatorId)}` : name
              }}
            />
          ) : (
            <Loading label="Loading district boundaries…" />
          )}
          <div className="map-legend">
            <span>{formatEstimate({ value: meta.higher_is_worse ? min : max, uncertainty: 'published' }, indicatorId)}</span>
            <span className="ramp" style={{ background: CONCERN_GRADIENT }} aria-hidden="true" />
            <span>{formatEstimate({ value: meta.higher_is_worse ? max : min, uncertainty: 'published' }, indicatorId)}</span>
            <span className="small muted">darker = more concern</span>
          </div>
          <p className="small muted">Boundaries: geoBoundaries ADM2 (CC BY 4.0). Click a district for its evidence.</p>
        </div>

        {selected && byName.has(selected) ? (
          <EvidencePanel
            data={data}
            district={selected}
            povertyWeight={povertyWeight}
            measure={measure}
            onClose={() => select(null)}
          />
        ) : (
          <aside className="evidence placeholder">
            <h2>Gap candidates</h2>
            <p>
              <strong>{gapDistricts.length} districts</strong> have financial exclusion above the national{' '}
              {data.national.excluded.value}% while poverty is at or below the national{' '}
              {data.national.poverty_rate.value.toFixed(1)}%:
            </p>
            <ul className="chip-list">
              {gapDistricts.map((d) => (
                <li key={d}>
                  <button type="button" className="chip" onClick={() => select(d)}>
                    {d}
                  </button>
                </li>
              ))}
            </ul>
            <p className="small muted">
              Poverty-only targeting would rank these low. Select any district on the map, chart or table to see
              its evidence, sources and confidence.
            </p>
          </aside>
        )}
      </div>

      <h2>Poverty vs financial exclusion</h2>
      <div className="scatter-grid">
        <GapScatter
          districts={visible}
          nationalPoverty={data.national.poverty_rate.value}
          nationalExclusion={data.national.excluded.value}
          selected={selected}
          onSelect={select}
        />
        <ProfileSummary districts={visible} typology={data.typology} selected={selected} onSelect={select} />
      </div>

      <h2>District table</h2>
      <div className="table-scroll">
        <table className="data-table">
          <caption className="small muted">
            {visible.length} districts{province ? ` in ${province}` : ''}. Poverty intervals are published 95% CIs;
            FinScope intervals are approximate.
          </caption>
          <thead>
            <tr>
              {sortHeader('district', 'District')}
              {sortHeader('poverty_rate', 'Poverty')}
              <th scope="col">95% CI</th>
              {sortHeader('excluded', 'Excluded')}
              {sortHeader('not_formally_served', 'Not formal')}
              {sortHeader('banked', 'Banked')}
              {sortHeader('poverty_decrease', 'Poverty fall')}
              {sortHeader('smartphone_households', 'Smartphone')}
              <th scope="col">Access strand</th>
              <th scope="col">Profile & flags</th>
            </tr>
          </thead>
          <tbody>
            {sorted.map((d: DistrictRow) => (
              <tr key={d.district} className={d.district === selected ? 'selected' : undefined}>
                <th scope="row">
                  <button type="button" className="link-btn" onClick={() => select(d.district)}>
                    {d.district}
                  </button>
                  <span className="def">{d.province}</span>
                </th>
                <td className="num">{formatEstimate(d.poverty_rate, 'poverty_rate')}</td>
                <td className="num small">{formatCi(d.poverty_rate)}</td>
                <td className="num">{formatEstimate(d.excluded, 'excluded')}</td>
                <td className="num">{formatEstimate(d.not_formally_served, 'not_formally_served')}</td>
                <td className="num">{formatEstimate(d.banked, 'banked')}</td>
                <td className="num">{formatEstimate(d.poverty_decrease, 'poverty_decrease')}</td>
                <td className="num">{formatEstimate(d.smartphone_households, 'smartphone_households')}</td>
                <td className="strand-cell">
                  <StrandBar strand={d.access_strand} compact />
                </td>
                <td>
                  <span className={`profile-dot profile-${d.profile.type}`} aria-hidden="true" /> {d.profile.label}
                  <span className="def">
                    {d.profile.flags.map((f) => (
                      <span key={f.id} className="flag-chip" title={f.detail}>
                        {f.label}
                      </span>
                    ))}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <h2>Who is excluded nationally?</h2>
      <p className="small muted">
        {data.who_is_excluded.highlights.join(' · ')}. {data.who_is_excluded.provenance.note}
      </p>
      <WhoIsExcluded data={data.who_is_excluded} nationalExcluded={data.national.excluded.value} />

      <details className="caveats">
        <summary>Data notes & known discrepancies</summary>
        <ul>
          {data.provenance.known_discrepancies.map((k) => (
            <li key={k.item}>
              <strong>{k.item}:</strong> {k.detail}
            </li>
          ))}
          <li>{data.provenance.uncertainty_assumptions.note}</li>
          <li>{data.provenance.linkage}</li>
        </ul>
      </details>
    </section>
  )
}
