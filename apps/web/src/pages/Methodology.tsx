import { getMethod, getSources, getValidation } from '../api/client'
import { Badge } from '../components/Badge'
import { ErrorState, Loading } from '../components/Status'
import { useApi } from '../hooks/useApi'
import { useDocumentTitle } from '../hooks/useDocumentTitle'

const IMPACT = [
  [
    'Data coverage',
    'All 30 districts, two official surveys, 10 district indicators + national group breakdowns',
    'Achieved',
  ],
  [
    'Analytical reliability',
    'Golden, consistency and transcription checks; Monte Carlo rank uncertainty; weight sensitivity',
    'Achieved',
  ],
  [
    'Decision usefulness',
    'Worked example: combined score surfaces high-exclusion districts that poverty-only targeting ranks 11th–15th',
    'Demonstrated',
  ],
  ['Targeting accuracy (pilot)', 'Share of field-verified priority districts confirmed by district officers', 'Pilot goal'],
  ['Reach (pilot)', 'Change in excluded adults in selected districts at the next FinScope round, vs comparison districts', 'Pilot goal'],
  ['Adoption (pilot)', 'Briefs used in district planning (Imihigo / DDS) meetings', 'Pilot goal'],
]

const CHECK_GROUPS = {
  golden: 'Golden — reproduce figures quoted in the reports',
  consistency: 'Consistency — tables agree with each other',
  transcription: 'Transcription — hand-entered figures match the PDF text layer',
} as const

export function Methodology() {
  useDocumentTitle('Methodology & impact')
  const method = useApi('method', getMethod)
  const validation = useApi('validation', getValidation)
  const sources = useApi('sources', getSources)

  return (
    <section className="page">
      <p className="eyebrow">Evidence</p>
      <h1>Methodology & impact</h1>
      <p className="lede">
        How every number is sourced, combined and checked — and what the tool deliberately does not claim.
      </p>

      <h2>Decision supported</h2>
      <p>
        <strong>User:</strong> a policymaker or programme planner in financial inclusion, social protection or district
        development planning. <strong>Decision:</strong> which districts to investigate first for combined poverty and
        financial-access responses, and what evidence and caveats to bring to the meeting.
      </p>

      <h2>Data and linkage</h2>
      <ul>
        <li>
          <Badge kind="observed" /> EICV7 2023/24 (NISR), read from the official Excel tables with published standard
          errors and 95% CIs: district headcount poverty (Table A9.23); context indicators — household mobile phone
          (A5.18), smartphone (A5.19), internet at home (A5.15) and population health insurance (A3.7); extreme poverty
          and VUP beneficiaries (national).
        </li>
        <li>
          <Badge kind="observed" /> EICV7 Poverty Profile: district poverty in 2017 (NISR modelled estimate on the EICV7
          basis) and the fall to 2024 (Annex B), province values from Table 5.1.
        </li>
        <li>
          <Badge kind="observed" /> FinScope Rwanda 2024 (AFR/NISR): access strand by district (Figure 13), province
          (Figure 12), national (Figure 5) and by area, gender, age, disability, refugee status and livelihood (Figures
          6–11); account uptake by product (p.12). Transcribed from the report and re-verified automatically against the
          PDF text layer.
        </li>
        <li>
          The surveys sample different households and are <strong>never merged at household level</strong>. They are
          compared only as district aggregates, so a high-poverty, high-exclusion district does not mean the same people
          are poor and excluded.
        </li>
      </ul>

      {method.error && <ErrorState error={method.error} onRetry={method.reload} />}
      {method.loading && <Loading />}
      {method.data && (
        <>
          <h2>Priority score</h2>
          <p className="formula">{method.data.formula}</p>
          <ul>
            <li>Min–max normalisation across the 30 districts puts both indicators on 0–1; contributions are additive.</li>
            <li>Weights are normative — the user sets them. Default 50/50.</li>
            <li>
              <strong>Baseline:</strong> poverty-only ranking. Every ranking is shown next to it, with districts that
              enter or drop out explained by their indicator values.
            </li>
            <li>
              <strong>Robustness:</strong> top 5 under {method.data.schemes.map((s) => s.label).join(', ')}, and under an
              alternative exclusion definition (not formally served).
            </li>
            <li>Ties on whole-percent FinScope values are broken by the higher poverty rate.</li>
          </ul>

          <h2>Uncertainty</h2>
          <p>
            <Badge kind="estimate" /> {method.data.uncertainty.note} Ranks are re-computed over{' '}
            {method.data.simulations.toLocaleString()} Monte Carlo draws of both indicators to give the probability of
            being in the top 5/10 and a 90% rank range.
          </p>

          <h2>Exclusion-pattern typology</h2>
          <div className="table-scroll">
          <table className="data-table stack">
            <thead>
              <tr>
                <th scope="col">Profile</th>
                <th scope="col">Rule (district aggregates)</th>
                <th scope="col">Where to look next</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(method.data.typology).map(([k, t]) => (
                <tr key={k}>
                  <th scope="row">
                    <span className={`profile-dot profile-${k}`} aria-hidden="true" /> {t.label}
                  </th>
                  <td data-label="Rule">{t.rule}</td>
                  <td className="small" data-label="Where to look next">
                    {t.response_focus}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          </div>

          <h2>Limitations</h2>
          <ul>
            {method.data.limitations.map((l) => (
              <li key={l}>{l}</li>
            ))}
            <li>District averages can hide sector- and cell-level pockets of need.</li>
            <li>No sex, age or urban/rural split at district level in the published tables used.</li>
          </ul>
        </>
      )}

      <h2>Validation against published figures</h2>
      {validation.error && <ErrorState error={validation.error} onRetry={validation.reload} />}
      {validation.data && (
        <>
          <p>
            <strong>
              {validation.data.passed} of {validation.data.passed + validation.data.failed}
            </strong>{' '}
            automated checks pass. The build fails if any check fails, so the deployed numbers are always the checked ones.
          </p>
          <dl className="check-summary">
            {(Object.keys(CHECK_GROUPS) as (keyof typeof CHECK_GROUPS)[]).map((g) => {
              const items = validation.data!.checks.filter((c) => c.group === g)
              return (
                <div key={g}>
                  <dt>{CHECK_GROUPS[g]}</dt>
                  <dd>
                    {items.filter((c) => c.pass).length}/{items.length}
                  </dd>
                </div>
              )
            })}
          </dl>
          <div className="table-scroll">
            <table className="data-table stack">
              <thead>
                <tr>
                  <th scope="col">Check</th>
                  <th scope="col" className="opt-md">
                    Type
                  </th>
                  <th scope="col">Published / expected</th>
                  <th scope="col">Ours</th>
                  <th scope="col">Result</th>
                  <th scope="col">Reference</th>
                </tr>
              </thead>
              <tbody>
                {validation.data.checks.map((c) => (
                  <tr key={c.check}>
                    <th scope="row">{c.check}</th>
                    <td className="small opt-md" data-label="Type">
                      {c.group}
                    </td>
                    <td className="val" data-label="Published / expected">
                      {Array.isArray(c.expected) ? c.expected.join(', ') : String(c.expected)}
                    </td>
                    <td className="val" data-label="Ours">
                      {Array.isArray(c.observed) ? c.observed.join(', ') : String(c.observed)}
                    </td>
                    <td className={`nowrap ${c.pass ? 'pass' : 'fail'}`} data-label="Result">{c.pass ? '✓ pass' : '✗ fail'}</td>
                    <td className="small" data-label="Reference">
                      {c.reference}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <h3>Known discrepancies in the sources</h3>
          <ul>
            {validation.data.known_discrepancies.map((k) => (
              <li key={k.item}>
                <strong>{k.item}:</strong> {k.detail}
              </li>
            ))}
          </ul>
        </>
      )}

      <h2>Impact framework</h2>
      <p className="small muted">
        What is demonstrated now versus what a pilot would measure. Pilot rows are goals, not achieved outcomes.
      </p>
      <div className="table-scroll">
      <table className="data-table stack">
        <thead>
          <tr>
            <th scope="col">Measure</th>
            <th scope="col">How</th>
            <th scope="col">Status</th>
          </tr>
        </thead>
        <tbody>
          {IMPACT.map(([m, how, status]) => (
            <tr key={m}>
              <th scope="row">{m}</th>
              <td data-label="How">{how}</td>
              <td data-label="Status">
                <span className={`status-pill ${status === 'Pilot goal' ? 'goal' : 'done'}`}>{status}</span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      </div>

      <h2>Sources</h2>
      {sources.error && <ErrorState error={sources.error} onRetry={sources.reload} />}
      {sources.data && (
        <ol className="sources">
          {sources.data.sources.map((s) => (
            <li key={s.id}>
              <a href={s.url} target="_blank" rel="noreferrer">
                {s.title}
              </a>{' '}
              — {s.publisher} ({s.year}). {s.role}.
              {s.sha256 && (
                <span className="def">
                  SHA-256 {s.sha256.slice(0, 16)}…{s.retrieved_at ? ` · retrieved ${s.retrieved_at.slice(0, 10)}` : ''}
                </span>
              )}
            </li>
          ))}
        </ol>
      )}

      <h2>AI disclosure</h2>
      <p>
        We used AI assistants to brainstorm and to understand the challenge — the brief, the judging criteria and the
        survey designs — and as coding assistants while building. The team reviewed and tested everything. No statistic
        was produced by AI: every number comes from the official sources above and passes the checks on this page.
      </p>
      <p className="small muted">No endorsement by NISR or AFR is implied.</p>
    </section>
  )
}
