import type { WhoIsExcluded as Data } from '../api/types'
import { Badge } from './Badge'
import { StrandBar } from './StrandBar'

/** National FinScope breakdowns: who is excluded, product uptake, and VUP context. */
export function WhoIsExcluded({ data, nationalExcluded }: { data: Data; nationalExcluded: number }) {
  const dims: string[] = []
  for (const g of data.groups) if (g.dimension !== 'national' && !dims.includes(g.dimension)) dims.push(g.dimension)
  const vup = data.vup
  const trend2020 = data.national_trend.find((t) => t.year === 2020)

  return (
    <div className="context-grid">
      <section className="context-card" aria-labelledby="who-title">
        <h3 id="who-title">
          Access strand by group <Badge kind="observed" />
        </h3>
        <p className="small muted">
          FinScope 2024, national only ({data.provenance.references.groups}). Red pill = share excluded; highlighted when
          above the {nationalExcluded}% national rate.
        </p>
        <div className="group-rows">
          {dims.map((dim) => {
            const rows = data.groups.filter((g) => g.dimension === dim)
            return (
              <div key={dim}>
                <p className="group-dim">{rows[0].dimension_label}</p>
                {rows.map((g) => (
                  <div className="group-row" key={g.group} title={g.transcription_note ?? g.source_figure}>
                    <span>{g.group}</span>
                    <StrandBar strand={g.access_strand} compact />
                    <span className={`excl-pill${g.excluded > nationalExcluded ? ' high' : ''}`}>{g.excluded}%</span>
                  </div>
                ))}
              </div>
            )
          })}
        </div>
        <ul className="legend-list">
          <li>
            <span className="swatch seg-banked" aria-hidden="true" />
            Banked
          </li>
          <li>
            <span className="swatch seg-other_formal" aria-hidden="true" />
            Other formal
          </li>
          <li>
            <span className="swatch seg-informal_only" aria-hidden="true" />
            Informal only
          </li>
          <li>
            <span className="swatch seg-excluded" aria-hidden="true" />
            Excluded
          </li>
        </ul>
      </section>

      <div>
        <section className="context-card" aria-labelledby="products-title">
          <h3 id="products-title">
            Accounts in own name <Badge kind="observed" />
          </h3>
          <p className="small muted">FinScope 2024, adults 16+ ({data.provenance.references.products}).</p>
          <ul className="product-bars">
            {data.products.map((p) => (
              <li key={p.product} title={p.note ?? undefined}>
                <span>{p.product === 'Any financial product account in own name' ? 'Any account' : p.product}</span>
                <span className="bar-track" aria-hidden="true">
                  <span className="bar-fill" style={{ width: `${p.percent_adults}%` }} />
                </span>
                <span className="num">{p.percent_adults}%</span>
              </li>
            ))}
          </ul>
          {trend2020 && (
            <p className="small muted">
              Since 2020, exclusion fell from {trend2020.access_strand.excluded}% to {nationalExcluded}% and informal-only
              reliance from {trend2020.access_strand.informal_only}% (FinScope Figure 5).
            </p>
          )}
        </section>

        <section className="vup-card" aria-labelledby="vup-title">
          <p id="vup-title">
            <Badge kind="observed" /> <strong>Social protection (VUP)</strong>
          </p>
          <p>
            {Math.round(vup.beneficiaries_thousands).toLocaleString()} thousand VUP beneficiaries;{' '}
            <strong>{vup.poverty_rate_beneficiaries}%</strong> of them are poor versus {vup.poverty_rate_all}% of all
            residents. {vup.component_shares['Financial Services']}% receive VUP financial services.
          </p>
          <p className="small muted">{vup.reference}. National only — VUP is not published by district.</p>
        </section>
      </div>
    </div>
  )
}
