import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getPriorities } from '../api/client'
import type { Measure, Mover, PrioritiesResponse, Ranking } from '../api/types'
import { Badge } from '../components/Badge'
import { ScenarioPlanner } from '../components/ScenarioPlanner'
import { ErrorState, Loading } from '../components/Status'
import { analysisQuery, useAnalysisParams } from '../hooks/useAnalysisParams'
import { useApi } from '../hooks/useApi'
import { useDocumentTitle } from '../hooks/useDocumentTitle'
import { share } from '../lib/format'

function useDebounced<T>(value: T, ms: number) {
  const [debounced, setDebounced] = useState(value)
  useEffect(() => {
    const t = setTimeout(() => setDebounced(value), ms)
    return () => clearTimeout(t)
  }, [value, ms])
  return debounced
}

function Shift({ value }: { value: number }) {
  if (value === 0) return <span className="shift same">—</span>
  return (
    <span className={`shift ${value > 0 ? 'up' : 'down'}`}>
      {value > 0 ? '▲' : '▼'} {Math.abs(value)}
    </span>
  )
}

function MoverList({ title, movers, empty }: { title: string; movers: Mover[]; empty: string }) {
  return (
    <div>
      <h3>{title}</h3>
      {movers.length === 0 ? (
        <p className="muted small">{empty}</p>
      ) : (
        <ul className="movers">
          {movers.map((m) => (
            <li key={m.district}>
              <strong>{m.district}</strong> — combined #{m.rank}, poverty-only #{m.baseline_rank}
              <span className="def">
                Poverty {m.poverty_rate.toFixed(1)}% (rank {m.baseline_rank}/30) · exclusion {m.exclusion}% (rank{' '}
                {m.exclusion_rank}/30)
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

function ContributionBar({ r }: { r: Ranking }) {
  return (
    <div className="contrib" title={`Poverty ${r.contributions.poverty.toFixed(3)} + exclusion ${r.contributions.exclusion.toFixed(3)}`}>
      <span className="contrib-p" style={{ width: `${r.contributions.poverty * 100}%` }} />
      <span className="contrib-e" style={{ width: `${r.contributions.exclusion * 100}%` }} />
      <span className="contrib-val">{r.score.toFixed(2)}</span>
    </div>
  )
}

function Results({ data, highlight }: { data: PrioritiesResponse; highlight: string | null }) {
  const [k, setK] = useState<'top5' | 'top10'>('top10')
  const cmp = data.comparison[k]
  const pw = data.weights.poverty
  const m = data.measure.id
  const schemes = data.sensitivity.schemes
  const allNames = Array.from(new Set(schemes.flatMap((s) => s.top5)))

  return (
    <>
      <div className="finding">
        <p className="eyebrow">
          <Badge kind="estimate" /> Baseline comparison
        </p>
        <h2>
          {cmp.entered.length === 0
            ? `At these weights the combined ${k === 'top5' ? 'top 5' : 'top 10'} matches poverty-only targeting.`
            : `${cmp.entered.length} of the combined ${k === 'top5' ? 'top 5' : 'top 10'} would be missed by poverty-only targeting.`}
        </h2>
        <div className="seg-toggle" role="group" aria-label="Compare top set size">
          {(['top5', 'top10'] as const).map((opt) => (
            <button key={opt} type="button" aria-pressed={k === opt} onClick={() => setK(opt)}>
              {opt === 'top5' ? 'Top 5' : 'Top 10'}
            </button>
          ))}
        </div>
        <div className="two-col">
          <MoverList title="Surfaced by the combined score" movers={cmp.entered} empty="None at these weights." />
          <MoverList title="Dropped vs poverty-only" movers={cmp.dropped} empty="None at these weights." />
        </div>
        <p className="small muted">
          Kept in both: {cmp.overlap.join(', ') || 'none'}. Districts move because of the exclusion indicator, not
          because they are less poor than the survey says.
        </p>
      </div>

      <h2>Ranked districts</h2>
      <p className="small muted">
        Score = {Math.round(pw * 100)}% × poverty (min–max) + {Math.round((1 - pw) * 100)}% × {data.measure.label}{' '}
        (min–max). Bars show each indicator's contribution. “In top 5” is the share of simulated draws — re-sampling
        both surveys within their sampling error ({data.provenance.uncertainty.method}) — in which the district stays
        in the top 5.
      </p>
      <div className="table-scroll">
        <table className="data-table rank-table">
          <thead>
            <tr>
              <th scope="col">#</th>
              <th scope="col">District</th>
              <th scope="col">
                Score <span className="legend-inline"><i className="contrib-p" /> poverty <i className="contrib-e" /> exclusion</span>
              </th>
              <th scope="col">Poverty-only #</th>
              <th scope="col">Shift</th>
              <th scope="col">Poverty</th>
              <th scope="col">Exclusion</th>
              <th scope="col" title="Share of simulations in which the district is in the top 5">In top 5</th>
              <th scope="col" title="5th–95th percentile of simulated rank">Rank range (90%)</th>
              <th scope="col" title="Poverty weights at which the district is in the top 5">Top-5 at poverty weight</th>
              <th scope="col">Brief</th>
            </tr>
          </thead>
          <tbody>
            {data.rankings.map((r) => (
              <tr key={r.district} className={r.district === highlight ? 'selected' : undefined}>
                <td>
                  <span className={`rank-pill${r.rank <= 5 ? ' top' : ''}`}>{r.rank}</span>
                </td>
                <th scope="row">
                  {r.district}
                  <span className="def">
                    <span className={`profile-dot profile-${r.profile.type}`} aria-hidden="true" /> {r.profile.label}
                  </span>
                </th>
                <td className="contrib-cell">
                  <ContributionBar r={r} />
                </td>
                <td className="num">{r.baseline_rank}</td>
                <td className="num">
                  <Shift value={r.rank_shift} />
                </td>
                <td className="num">{r.inputs.poverty_rate.toFixed(1)}%</td>
                <td className="num">{r.inputs.exclusion}%</td>
                <td className="num">{share(r.uncertainty.p_top5)}</td>
                <td className="num">
                  {r.uncertainty.rank_interval_90[0]}–{r.uncertainty.rank_interval_90[1]}
                </td>
                <td className="num small">
                  {r.top5_poverty_weight_range
                    ? `${r.top5_poverty_weight_range[0].toFixed(2)}–${r.top5_poverty_weight_range[1].toFixed(2)}`
                    : 'never'}
                </td>
                <td>
                  <Link
                    className="row-action"
                    to={`/brief${analysisQuery(pw, m, r.district)}`}
                    aria-label={`Brief for ${r.district}`}
                  >
                    Brief
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <h2>What would change this recommendation?</h2>
      <p className="small muted">Top 5 under alternative weightings and an alternative exclusion definition.</p>
      <div className="table-scroll">
        <table className="data-table sens-table">
          <thead>
            <tr>
              <th scope="col">District</th>
              {schemes.map((s) => (
                <th scope="col" key={s.label}>
                  {s.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {allNames.map((name) => (
              <tr key={name}>
                <th scope="row">{name}</th>
                {schemes.map((s) => (
                  <td key={s.label} className="sens-cell">
                    {s.top5.includes(name) ? (
                      <span className="in-top" aria-label="in top 5">
                        #{s.top5.indexOf(name) + 1}
                      </span>
                    ) : (
                      <span className="out-top" aria-label="not in top 5" />
                    )}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="banner">
        <Badge kind="estimate" />{' '}
        {data.sensitivity.robust_top5.length > 0 ? (
          <>
            Robust across 75/25, 50/50 and 25/75 weightings: <strong>{data.sensitivity.robust_top5.join(', ')}</strong>.
            The rest of the top 5 depends on how much weight is given to exclusion — a policy choice, not a statistical
            fact.
          </>
        ) : (
          <>No district stays in the top 5 across all mixed weightings — treat the ranking as weight-dependent.</>
        )}
      </p>

      <details className="caveats">
        <summary>Method & limitations</summary>
        <p className="small">
          {data.provenance.formula} — {data.provenance.normalisation}. Uncertainty: {data.provenance.uncertainty.method};
          poverty from {data.provenance.uncertainty.poverty}; {data.provenance.uncertainty.exclusion}
        </p>
        <ul>
          {data.provenance.limitations.map((l) => (
            <li key={l}>{l}</li>
          ))}
        </ul>
      </details>
    </>
  )
}

export function Priorities() {
  useDocumentTitle('Prioritise')
  const { povertyWeight, measure, district, update } = useAnalysisParams()
  const [sliderValue, setSliderValue] = useState(povertyWeight)
  const debouncedWeight = useDebounced(sliderValue, 250)

  useEffect(() => {
    if (debouncedWeight !== povertyWeight) update({ povertyWeight: debouncedWeight })
  }, [debouncedWeight, povertyWeight, update])

  const key = `priorities:${povertyWeight.toFixed(2)}:${measure}`
  const priorities = useApi(key, () => getPriorities({ povertyWeight, measure }))
  const [lastData, setLastData] = useState<PrioritiesResponse | null>(null)
  if (priorities.data && priorities.data !== lastData) setLastData(priorities.data)
  const shown = priorities.data ?? lastData

  return (
    <section className="page">
      <p className="eyebrow">Step 2 · Prioritise</p>
      <h1>Explainable Priority Analysis</h1>
      <p className="lede">
        A transparent score that combines poverty with financial exclusion, compared against poverty-only targeting.
        The weights are a policy choice — move them and watch which districts hold their place.
      </p>

      <div className="controls weights" role="group" aria-label="Scoring assumptions">
        <label className="weight-control">
          <span>
            Poverty weight <strong>{Math.round(sliderValue * 100)}%</strong> · Exclusion weight{' '}
            <strong>{Math.round((1 - sliderValue) * 100)}%</strong>
          </span>
          <input
            type="range"
            min={0}
            max={1}
            step={0.05}
            value={sliderValue}
            onChange={(e) => setSliderValue(Number(e.target.value))}
            aria-valuetext={`Poverty ${Math.round(sliderValue * 100)} percent, exclusion ${Math.round((1 - sliderValue) * 100)} percent`}
          />
          <span className="range-ends small muted">
            <span>Exclusion only</span>
            <span>Poverty only (baseline)</span>
          </span>
        </label>
        <fieldset className="measure-pick">
          <legend>Exclusion indicator</legend>
          {(
            [
              ['excluded', 'Financially excluded (no formal or informal product)'],
              ['not_formally_served', 'Not formally served (informal-only + excluded)'],
            ] as [Measure, string][]
          ).map(([id, label]) => (
            <label key={id}>
              <input type="radio" name="measure" checked={measure === id} onChange={() => update({ measure: id })} />{' '}
              {label}
            </label>
          ))}
        </fieldset>
      </div>

      {priorities.error && !shown ? (
        <ErrorState error={priorities.error} onRetry={priorities.reload} />
      ) : shown ? (
        <div className={priorities.loading ? 'stale' : undefined} aria-busy={priorities.loading}>
          <Results data={shown} highlight={district} />
        </div>
      ) : (
        <Loading label="Scoring 30 districts and running 2,000 uncertainty simulations…" />
      )}

      <ScenarioPlanner povertyWeight={povertyWeight} measure={measure} />
    </section>
  )
}
