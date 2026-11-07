import { Link } from 'react-router-dom'
import { getIndicators, getPriorities } from '../api/client'
import { Badge } from '../components/Badge'
import { AlertIcon, BriefIcon, MapIcon, RankIcon } from '../components/Icons'
import { ErrorState, Loading } from '../components/Status'
import { DEFAULT_MEASURE, DEFAULT_POVERTY_WEIGHT } from '../hooks/useAnalysisParams'
import { useApi } from '../hooks/useApi'
import { useDocumentTitle } from '../hooks/useDocumentTitle'

export function Home() {
  useDocumentTitle('')
  const indicators = useApi('indicators', () => getIndicators())
  const priorities = useApi(`priorities:${DEFAULT_POVERTY_WEIGHT.toFixed(2)}:${DEFAULT_MEASURE}`, () =>
    getPriorities({ povertyWeight: DEFAULT_POVERTY_WEIGHT, measure: DEFAULT_MEASURE }),
  )
  const data = indicators.data
  const nat = data?.national
  const cmp = priorities.data?.comparison.top10
  const poorest = data?.districts.reduce((a, b) => (a.poverty_rate.value > b.poverty_rate.value ? a : b))
  const excl = data?.districts.map((d) => d.excluded.value) ?? []
  const mobileMoney = data?.who_is_excluded.products.find((p) => p.product === 'Mobile money')

  return (
    <section className="page home">
      <p className="eyebrow">Decision support · Rwanda · 30 districts</p>
      <h1>Where should limited resources go first — and who is poverty targeting missing?</h1>
      <p className="lede">
        For financial-inclusion and social-protection planners. NISR's EICV7 poverty estimates sit next to the FinScope
        2024 access strand for every district, ranked with a transparent score you can re-weight, then written up as a
        caveated brief for the planning meeting.
      </p>

      {cmp && poorest && (
        <div className="finding">
          <p className="eyebrow">
            <Badge kind="estimate" /> The finding
          </p>
          <h2>
            Poverty-only targeting misses {cmp.entered.length} of the 10 districts a combined poverty + exclusion score
            would prioritise.
          </h2>
          <p>
            At equal weights, <strong>{cmp.entered.map((m) => m.district).join(', ')}</strong> enter the top 10 because
            their financial exclusion is among the highest in Rwanda. Meanwhile {poorest.district}, the poorest district
            ({poorest.poverty_rate.value.toFixed(1)}%), has only {poorest.excluded.value}% of adults excluded — a poverty
            problem more than an access problem.
          </p>
          <p className="small muted">
            Weight-sensitive: only {priorities.data!.sensitivity.robust_top5.join(', ') || 'no district'} stays in the
            top 5 across all mixed weightings — so the tool shows the sensitivity, not just a ranking.
          </p>
          <div className="cta-row">
            <Link className="cta" to="/priorities">
              See the ranking
            </Link>
          </div>
        </div>
      )}

      {indicators.error ? (
        <ErrorState error={indicators.error} onRetry={indicators.reload} />
      ) : nat && data ? (
        <dl className="headline-stats">
          <div>
            <span className="stat-icon coral" aria-hidden="true">
              <AlertIcon />
            </span>
            <dt>
              Headcount poverty <Badge kind="observed" />
            </dt>
            <dd>{nat.poverty_rate.value.toFixed(1)}%</dd>
            <p className="small muted">
              EICV7 2023/24 · down from {nat.poverty_2017_modelled.toFixed(1)}% in 2017 (modelled)
            </p>
          </div>
          <div>
            <span className="stat-icon" aria-hidden="true">
              <MapIcon />
            </span>
            <dt>
              Financially excluded adults <Badge kind="observed" />
            </dt>
            <dd>{nat.excluded.value}%</dd>
            <p className="small muted">
              FinScope 2024 · {Math.min(...excl)}–{Math.max(...excl)}% across districts
            </p>
          </div>
          <div>
            <span className="stat-icon sage" aria-hidden="true">
              <RankIcon />
            </span>
            <dt>
              Mobile-money accounts <Badge kind="observed" />
            </dt>
            <dd>{mobileMoney?.percent_adults ?? '—'}%</dd>
            <p className="small muted">FinScope 2024 · adults 16+ with an account in own name</p>
          </div>
          <div>
            <span className="stat-icon amber" aria-hidden="true">
              <BriefIcon />
            </span>
            <dt>
              VUP beneficiaries who are poor <Badge kind="observed" />
            </dt>
            <dd>{data.who_is_excluded.vup.poverty_rate_beneficiaries}%</dd>
            <p className="small muted">EICV7 VUP survey · vs {data.who_is_excluded.vup.poverty_rate_all}% of all residents</p>
          </div>
        </dl>
      ) : (
        <Loading />
      )}

      <ol className="workflow">
        <li>
          <strong>Explore</strong>
          Map and compare district poverty, financial access and context indicators — each with source, definition and
          margin of error.
          <p>
            <Link to="/explorer">Open the Explorer →</Link>
          </p>
        </li>
        <li>
          <strong>Prioritise</strong>
          Combine them with weights you control; see why each district ranks where it does, how it compares with
          poverty-only targeting, and what would change the answer.
          <p>
            <Link to="/priorities">Open Priorities →</Link>
          </p>
        </li>
        <li>
          <strong>Brief</strong>
          Export findings, interpretation, next steps and limitations for a planning meeting.
          <p>
            <Link to="/brief">Generate a brief →</Link>
          </p>
        </li>
      </ol>

      <p className="small muted">
        What this tool does not do: it does not link households across surveys, predict programme impact, or claim anyone
        will leave poverty. See <Link to="/methodology">Methodology & impact</Link>.
      </p>
    </section>
  )
}
