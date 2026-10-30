import { useEffect, useState } from 'react'
import { getPriorities } from '../api/client'

export function Priorities() {
  const [povertyWeight, setPovertyWeight] = useState(0.5)
  const [status, setStatus] = useState('idle')
  const [error, setError] = useState<string | null>(null)

  const exclusionWeight = 1 - povertyWeight

  useEffect(() => {
    let cancelled = false
    setStatus('loading')
    getPriorities({ povertyWeight, exclusionWeight })
      .then((data) => {
        if (!cancelled) setStatus(data.status)
      })
      .catch((err: unknown) => {
        if (!cancelled) setError(err instanceof Error ? err.message : 'Failed to load priorities')
      })
    return () => {
      cancelled = true
    }
  }, [povertyWeight, exclusionWeight])

  return (
    <section className="page">
      <h1>Explainable Priority Analysis</h1>
      <p className="lede">
        Transparent scoring with a poverty-only baseline. Weights are assumptions — change them
        and see whether the top set moves.
      </p>
      <label className="weight-control">
        Poverty weight: {povertyWeight.toFixed(2)}
        <input
          type="range"
          min={0}
          max={1}
          step={0.05}
          value={povertyWeight}
          onChange={(e) => setPovertyWeight(Number(e.target.value))}
        />
        <span className="muted">
          Exclusion weight: {exclusionWeight.toFixed(2)} (remainder)
        </span>
      </label>
      {error ? (
        <p className="banner error" role="alert">
          {error}
        </p>
      ) : (
        <p className="banner" data-kind="estimate">
          Status: {status}. Rankings will appear once processed indicators exist.
        </p>
      )}
    </section>
  )
}