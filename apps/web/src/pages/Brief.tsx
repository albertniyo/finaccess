import { useState, type FormEvent } from 'react'
import { createBrief } from '../api/client'

export function Brief() {
  const [geo, setGeo] = useState('Kigali')
  const [result, setResult] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  async function onSubmit(event: FormEvent) {
    event.preventDefault()
    setBusy(true)
    setError(null)
    setResult(null)
    try {
      const brief = await createBrief({ geo })
      setResult(
        `Brief stub for ${brief.geo} (${brief.status}). Sections ready once data is processed.`,
      )
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to generate brief')
    } finally {
      setBusy(false)
    }
  }

  return (
    <section className="page">
      <h1>Policy Brief Generator</h1>
      <p className="lede">
        Produce a meeting-ready brief with findings, evidence, priority explanation, next steps,
        and limitations — clearly separating observed facts from recommendations.
      </p>
      <form className="brief-form" onSubmit={onSubmit}>
        <label>
          Geography
          <input value={geo} onChange={(e) => setGeo(e.target.value)} required />
        </label>
        <button type="submit" className="cta primary" disabled={busy}>
          {busy ? 'Generating…' : 'Generate brief'}
        </button>
      </form>
      {error && (
        <p className="banner error" role="alert">
          {error}
        </p>
      )}
      {result && <p className="banner">{result}</p>}
    </section>
  )
}