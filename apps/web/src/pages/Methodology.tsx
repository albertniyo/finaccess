import { useEffect, useState } from 'react'
import { getSources } from '../api/client'

type Source = {
  id: string
  title: string
  publisher: string
  year: string
  url: string
}

export function Methodology() {
  const [sources, setSources] = useState<Source[]>([])
  const [note, setNote] = useState('')

  useEffect(() => {
    getSources()
      .then((data) => {
        setSources((data.sources as Source[]) ?? [])
        setNote(data.note ?? '')
      })
      .catch(() => setNote('Could not reach API for live source list.'))
  }, [])

  return (
    <section className="page">
      <h1>Methodology & impact</h1>
      <p className="lede">
        Scoring formulas, baselines, sensitivity, and limitations live in{' '}
        <code>docs/methodology.md</code>. Below is the live source catalogue from the API.
      </p>
      <ul className="principles">
        <li>No household-level merge of EICV7 and FinScope without a documented linkage key.</li>
        <li>Survey weights and design-aware estimation for population stats.</li>
        <li>No invented statistics; badges for Observed / Estimate / Scenario.</li>
        <li>Benchmark combined scores against a poverty-only baseline.</li>
      </ul>
      {note && <p className="muted">{note}</p>}
      <ul className="source-list">
        {sources.map((s) => (
          <li key={s.id}>
            <a href={s.url} target="_blank" rel="noreferrer">
              {s.title}
            </a>{' '}
            — {s.publisher} ({s.year})
          </li>
        ))}
      </ul>
    </section>
  )
}