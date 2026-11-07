import { useState, type FormEvent } from 'react'
import { createScenario } from '../api/client'
import type { AllocationRule, Measure, ScenarioResponse, Strategy } from '../api/types'
import { rwf, share } from '../lib/format'
import { Badge } from './Badge'
import { ErrorState } from './Status'

const STRATEGY_LABELS: Record<Strategy, string> = {
  poverty_only: 'Poverty only',
  exclusion_gap: 'Exclusion gap',
  combined_score: 'Combined score',
}

export function ScenarioPlanner({ povertyWeight, measure }: { povertyWeight: number; measure: Measure }) {
  const [budget, setBudget] = useState(1_000_000_000)
  const [strategy, setStrategy] = useState<Strategy>('combined_score')
  const [topN, setTopN] = useState(10)
  const [allocation, setAllocation] = useState<AllocationRule>('equal')
  const [result, setResult] = useState<ScenarioResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  async function run(event?: FormEvent) {
    event?.preventDefault()
    setBusy(true)
    setError(null)
    try {
      setResult(
        await createScenario({
          budget,
          strategy,
          topN,
          allocation,
          povertyWeight,
          exclusionWeight: +(1 - povertyWeight).toFixed(4),
          measure,
        }),
      )
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Scenario failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <section className="scenario" aria-labelledby="scenario-title">
      <p className="eyebrow">
        <Badge kind="scenario" /> Optional
      </p>
      <h2 id="scenario-title">Hypothetical budget: how do targeting rules differ?</h2>
      <p className="small muted">
        Shows where a budget would be directed — not how many people would leave poverty. No intervention costs or
        causal effects are assumed.
      </p>
      <form className="controls scenario-form" onSubmit={run}>
        <label>
          Budget (RWF)
          <input
            type="number"
            min={1}
            step="any"
            value={budget}
            onChange={(e) => setBudget(Math.max(1, Number(e.target.value)))}
            required
            aria-describedby="budget-readout"
          />
          <span id="budget-readout" className="input-hint">
            {rwf(budget)}
          </span>
        </label>
        <label>
          Targeting rule
          <select value={strategy} onChange={(e) => setStrategy(e.target.value as Strategy)}>
            {(Object.keys(STRATEGY_LABELS) as Strategy[]).map((s) => (
              <option key={s} value={s}>
                {STRATEGY_LABELS[s]}
              </option>
            ))}
          </select>
        </label>
        <label>
          Districts funded
          <input type="number" min={1} max={30} value={topN} onChange={(e) => setTopN(Math.min(30, Math.max(1, Number(e.target.value))))} />
        </label>
        <label>
          Split
          <select value={allocation} onChange={(e) => setAllocation(e.target.value as AllocationRule)}>
            <option value="equal">Equal per district</option>
            <option value="proportional">Proportional to indicator</option>
          </select>
        </label>
        <button type="submit" className="cta primary" disabled={busy}>
          {busy ? 'Running…' : 'Run scenario'}
        </button>
      </form>

      {error && <ErrorState error={error} onRetry={() => run()} />}
      {result && (
        <div className="scenario-result">
          <p className="banner scenario-warning">
            <Badge kind="scenario" /> {result.provenance.warning}
          </p>
          <div className="table-scroll">
            <table className="data-table">
              <caption className="small muted">
                {result.strategy_label} · top {result.top_n} · {result.allocation_label.toLowerCase()}
              </caption>
              <thead>
                <tr>
                  <th scope="col">District</th>
                  <th scope="col">Share</th>
                  <th scope="col">Amount</th>
                  <th scope="col">Poverty</th>
                  <th scope="col">Exclusion</th>
                  <th scope="col">Profile</th>
                </tr>
              </thead>
              <tbody>
                {result.allocations.map((a) => (
                  <tr key={a.district}>
                    <th scope="row">{a.district}</th>
                    <td className="num">{share(a.share)}</td>
                    <td className="num">{rwf(a.amount)}</td>
                    <td className="num">{a.poverty_rate.toFixed(1)}%</td>
                    <td className="num">{a.exclusion}%</td>
                    <td className="small">{a.profile}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <h3>Same budget, three rules</h3>
          <div className="table-scroll">
            <table className="data-table">
              <thead>
                <tr>
                  <th scope="col">Rule</th>
                  <th scope="col">Budget to above-national poverty</th>
                  <th scope="col">Budget to above-national exclusion</th>
                  <th scope="col">Budget to “exclusion gap” districts</th>
                  <th scope="col">Shared with selected rule</th>
                  <th scope="col">Only this rule funds</th>
                </tr>
              </thead>
              <tbody>
                {result.comparison.map((c) => (
                  <tr key={c.strategy} className={c.strategy === result.strategy ? 'selected' : undefined}>
                    <th scope="row">{STRATEGY_LABELS[c.strategy]}</th>
                    <td className="num">{share(c.budget_share_above_national_poverty)}</td>
                    <td className="num">{share(c.budget_share_above_national_exclusion)}</td>
                    <td className="num">{share(c.budget_share_access_gap_districts)}</td>
                    <td className="num">
                      {c.overlap_with_selected}/{result.top_n}
                    </td>
                    <td className="small">{c.only_in_this_strategy.join(', ') || '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <ul className="small muted">
            {result.provenance.assumptions.map((a) => (
              <li key={a}>{a}</li>
            ))}
          </ul>
        </div>
      )}
    </section>
  )
}
