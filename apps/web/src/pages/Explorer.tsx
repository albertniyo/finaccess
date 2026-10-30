import { useEffect, useState } from 'react'
import { getIndicators } from '../api/client'

export function Explorer() {
  const [status, setStatus] = useState<string>('loading')
  const [note, setNote] = useState<string>('')
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    getIndicators()
      .then((data) => {
        if (cancelled) return
        setStatus(data.status)
        setNote(
          data.status === 'awaiting_processed_data'
            ? 'Processed district aggregates are not loaded yet. Download Priority A sources, then run the ETL scripts.'
            : `${data.series.length} indicator rows loaded.`,
        )
      })
      .catch((err: unknown) => {
        if (!cancelled) setError(err instanceof Error ? err.message : 'Failed to load indicators')
      })
    return () => {
      cancelled = true
    }
  }, [])

  return (
    <section className="page">
      <h1>Intervention Gap Explorer</h1>
      <p className="lede">
        Compare poverty and financial-access indicators at a defensible geographic level. Every
        chart will cite source, year, definition, and limitations.
      </p>
      {error ? (
        <p className="banner error" role="alert">
          {error}. Is the API running on port 8000?
        </p>
      ) : (
        <p className="banner" data-kind="estimate">
          Status: {status}. {note}
        </p>
      )}
      <p className="muted">
        Filters (province, urban/rural, sex, age) appear only where the dataset supports them.
      </p>
    </section>
  )
}