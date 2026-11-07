import { Link } from 'react-router-dom'
import type { IndicatorMeta, IndicatorsResponse, Measure } from '../api/types'
import { analysisQuery } from '../hooks/useAnalysisParams'
import { formatCi, formatEstimate } from '../lib/format'
import { Badge } from './Badge'
import { StrandBar } from './StrandBar'

type Props = {
  data: IndicatorsResponse
  district: string
  povertyWeight: number
  measure: Measure
  onClose: () => void
}

const GROUP_TITLES: Record<IndicatorMeta['group'], string> = {
  core: 'Poverty & financial access',
  context: 'Context',
}

function shortSource(ind: IndicatorMeta) {
  const survey = ind.survey.split(' ')[0]
  const ref = ind.reference.split(/[,(]/)[0].trim()
  return `${survey} · ${ref}`
}

export function EvidencePanel({ data, district, povertyWeight, measure, onClose }: Props) {
  const row = data.districts.find((d) => d.district === district)
  if (!row) return null
  const province = data.provinces.find((p) => p.province === row.province)
  const typology = data.typology[row.profile.type]

  return (
    <aside className="evidence" aria-labelledby="evidence-title">
      <header className="evidence-head">
        <div>
          <p className="eyebrow">{row.province} Province</p>
          <h2 id="evidence-title">{row.district}</h2>
        </div>
        <button type="button" className="icon-btn" onClick={onClose} aria-label="Close evidence panel">
          ×
        </button>
      </header>

      <p className={`profile-chip profile-${row.profile.type}`}>{row.profile.label}</p>
      <p className="small">
        <Badge kind="estimate" /> {typology.rule}. {typology.response_focus}
      </p>
      <p className="small muted">
        Poverty vs national: {row.profile.confidence.poverty_vs_national}. Exclusion vs national:{' '}
        {row.profile.confidence.exclusion_vs_national}.
      </p>
      {row.profile.flags.map((f) => (
        <p key={f.id} className="small">
          <span className="flag-chip">{f.label}</span> {f.detail}
        </p>
      ))}

      <h3>Financial access strand</h3>
      <StrandBar strand={row.access_strand} />

      <table className="evidence-table stack">
        <thead>
          <tr>
            <th scope="col">Indicator</th>
            <th scope="col">District</th>
            <th scope="col">Province</th>
            <th scope="col">Rwanda</th>
          </tr>
        </thead>
        {(['core', 'context'] as const).map((group) => (
          <tbody key={group}>
            <tr className="ind-group">
              <th scope="colgroup" colSpan={4}>
                {GROUP_TITLES[group]} <Badge kind="observed" />
              </th>
            </tr>
            {data.indicators
              .filter((ind) => ind.group === group)
              .map((ind) => (
                <tr key={ind.id}>
                  <th scope="row" title={`${ind.survey} — ${ind.reference}. ${ind.definition}`}>
                    {ind.label}
                    <span className="def">{shortSource(ind)}</span>
                  </th>
                  <td className="num" data-label={row.district}>
                    <span className="val-stack">
                      <strong>{formatEstimate(row[ind.id], ind.id)}</strong>
                      <span className="def">{formatCi(row[ind.id])}</span>
                    </span>
                  </td>
                  <td className="num" data-label={row.province}>
                    {province ? formatEstimate(province[ind.id], ind.id) : '—'}
                  </td>
                  <td className="num" data-label="Rwanda">
                    {formatEstimate(data.national[ind.id], ind.id)}
                  </td>
                </tr>
              ))}
          </tbody>
        ))}
      </table>
      {row.transcription_note && <p className="small muted">Transcription note: {row.transcription_note}</p>}
      <p className="small muted">{data.provenance.linkage}</p>

      <div className="cta-row">
        <Link className="cta primary" to={`/brief${analysisQuery(povertyWeight, measure, row.district)}`}>
          Brief for {row.district}
        </Link>
        <Link className="cta" to={`/priorities${analysisQuery(povertyWeight, measure, row.district)}`}>
          See its priority rank
        </Link>
      </div>
    </aside>
  )
}
