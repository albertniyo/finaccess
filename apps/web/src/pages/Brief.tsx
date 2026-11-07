import { Link } from 'react-router-dom'
import { createBrief, getIndicators } from '../api/client'
import type { BriefResponse, Statement } from '../api/types'
import { Badge } from '../components/Badge'
import { ErrorState, Loading } from '../components/Status'
import { analysisQuery, useAnalysisParams } from '../hooks/useAnalysisParams'
import { useApi } from '../hooks/useApi'
import { useDocumentTitle } from '../hooks/useDocumentTitle'

function Statements({ items }: { items: Statement[] }) {
  return (
    <ul className="statements">
      {items.map((s) => (
        <li key={s.text}>
          <Badge kind={s.kind} /> {s.text}
          {s.source && <span className="cite"> [{s.source}]</span>}
        </li>
      ))}
    </ul>
  )
}

function toMarkdown(b: BriefResponse) {
  const list = (items: Statement[]) =>
    items.map((s) => `- **${s.kind.toUpperCase()}** — ${s.text}${s.source ? ` _[${s.source}]_` : ''}`).join('\n')
  return [
    `# ${b.title}`,
    `Generated ${b.generated_on} by FinAccess Compass Rwanda. Weights: poverty ${Math.round(b.weights.poverty * 100)}% / exclusion ${Math.round(b.weights.exclusion * 100)}% (${b.measure.label}).`,
    `## Key findings (observed)\n${list(b.sections.key_findings)}`,
    `## Interpretation\n${list(b.sections.interpretation)}`,
    `## Recommended next steps\n${list(b.sections.next_steps)}`,
    `## Scenario check\n${list(b.sections.scenario)}`,
    `## Methodology\n${b.sections.methodology_notes.map((n) => `- ${n}`).join('\n')}`,
    `## Limitations\n${b.sections.limitations.map((n) => `- ${n}`).join('\n')}`,
    `## Sources\n${b.sections.sources.map((s) => `- ${s.title} — ${s.publisher} (${s.year}). ${s.url}`).join('\n')}`,
  ].join('\n\n')
}

function download(b: BriefResponse) {
  const blob = new Blob([toMarkdown(b)], { type: 'text/markdown' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `finaccess-brief-${b.geo.toLowerCase()}.md`
  a.click()
  URL.revokeObjectURL(url)
}

function BriefDocument({ brief }: { brief: BriefResponse }) {
  const s = brief.summary
  return (
    <article className="brief-doc" aria-labelledby="brief-title">
      <header>
        <p className="eyebrow">Policy brief · {brief.province} · {brief.generated_on}</p>
        <h2 id="brief-title">{brief.title}</h2>
        <p className="small muted">
          Assumptions: poverty weight {Math.round(brief.weights.poverty * 100)}%, exclusion weight{' '}
          {Math.round(brief.weights.exclusion * 100)}% ({brief.measure.label}).
        </p>
      </header>

      <dl className="brief-summary">
        <div>
          <dt>Poverty</dt>
          <dd>{s.poverty_rate.toFixed(1)}%</dd>
        </div>
        <div>
          <dt>Excluded adults</dt>
          <dd>{s.excluded}%</dd>
        </div>
        <div>
          <dt>Combined rank</dt>
          <dd>#{s.rank} / 30</dd>
        </div>
        <div>
          <dt>Poverty-only rank</dt>
          <dd>#{s.baseline_rank} / 30</dd>
        </div>
        <div>
          <dt>Profile</dt>
          <dd className="small">{s.profile.label}</dd>
        </div>
      </dl>

      <section>
        <h3>1. Key findings</h3>
        <Statements items={brief.sections.key_findings} />
      </section>
      <section>
        <h3>2. Interpretation</h3>
        <Statements items={brief.sections.interpretation} />
      </section>
      <section>
        <h3>3. Recommended next steps</h3>
        <Statements items={brief.sections.next_steps} />
      </section>
      <section>
        <h3>4. Scenario check</h3>
        <Statements items={brief.sections.scenario} />
      </section>
      <section>
        <h3>5. Methodology</h3>
        <ul>
          {brief.sections.methodology_notes.map((n) => (
            <li key={n}>{n}</li>
          ))}
        </ul>
      </section>
      <section>
        <h3>6. Limitations</h3>
        <ul>
          {brief.sections.limitations.map((n) => (
            <li key={n}>{n}</li>
          ))}
        </ul>
      </section>
      <section>
        <h3>7. Sources</h3>
        <ol className="sources">
          {brief.sections.sources.map((src) => (
            <li key={src.id}>
              {src.title} — {src.publisher} ({src.year}).{' '}
              <a href={src.url} target="_blank" rel="noreferrer">
                {src.url}
              </a>
            </li>
          ))}
        </ol>
      </section>
      <footer className="small muted">
        FinAccess Compass Rwanda · NISR 2026 Big Data Hackathon. Rankings are hypotheses for investigation, not funding
        decisions.
      </footer>
    </article>
  )
}

export function Brief() {
  const { povertyWeight, measure, district, update } = useAnalysisParams()
  useDocumentTitle(district ? `${district} brief` : 'Policy brief')
  const indicators = useApi('indicators', () => getIndicators())
  const names = (indicators.data?.districts.map((d) => d.district) ?? []).sort()
  const geo = district && names.includes(district) ? district : null
  const brief = useApi(geo ? `brief:${geo}:${povertyWeight.toFixed(2)}:${measure}` : null, () =>
    createBrief({ geo: geo ?? '', povertyWeight, measure }),
  )

  return (
    <section className="page">
      <div className="no-print">
        <p className="eyebrow">Step 3 · Brief</p>
        <h1>Policy Brief Generator</h1>
        <p className="lede">
          A meeting-ready brief for one district: observed findings, our interpretation, suggested next steps and
          limitations — each statement labelled so readers can tell facts from judgement.
        </p>

        {indicators.error ? (
          <ErrorState error={indicators.error} onRetry={indicators.reload} />
        ) : (
          <div className="controls">
            <label>
              District
              <select value={geo ?? ''} onChange={(e) => update({ district: e.target.value || null })}>
                <option value="">Choose a district…</option>
                {names.map((n) => (
                  <option key={n} value={n}>
                    {n}
                  </option>
                ))}
              </select>
            </label>
            <p className="small muted filter-note">
              Using poverty weight {Math.round(povertyWeight * 100)}% and the{' '}
              {measure === 'excluded' ? '“financially excluded”' : '“not formally served”'} measure.{' '}
              <Link to={`/priorities${analysisQuery(povertyWeight, measure, geo ?? undefined)}`}>Change on Priorities</Link>
            </p>
            {brief.data && (
              <div className="cta-row">
                <button type="button" className="cta primary" onClick={() => window.print()}>
                  Print / save as PDF
                </button>
                <button type="button" className="cta" onClick={() => brief.data && download(brief.data)}>
                  Download Markdown
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {!geo && indicators.data && (
        <p className="banner muted">
          Pick a district to generate its brief. Tip: start from a district the Priorities page flags as surfaced by
          the combined score, such as Ngoma or Gakenke.
        </p>
      )}
      {brief.error && <ErrorState error={brief.error} onRetry={brief.reload} />}
      {brief.loading && <Loading label="Assembling evidence for the brief…" />}
      {brief.data && <BriefDocument brief={brief.data} />}
    </section>
  )
}
