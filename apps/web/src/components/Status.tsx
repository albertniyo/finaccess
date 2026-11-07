import { useEffect, useState, type ReactNode } from 'react'
import { API_BASE } from '../api/client'

const WAKE_HINT_AFTER_MS = 5000

export function Loading({ label = 'Loading evidence…' }: { label?: string }) {
  const [slow, setSlow] = useState(false)
  useEffect(() => {
    const t = setTimeout(() => setSlow(true), WAKE_HINT_AFTER_MS)
    return () => clearTimeout(t)
  }, [])
  return (
    <p className="banner loading" role="status" aria-live="polite">
      <span className="spinner" aria-hidden="true" />
      <span>
        {label}
        {slow && <span className="def">The API is waking up after a quiet period — this can take up to a minute.</span>}
      </span>
    </p>
  )
}

export function ErrorState({ error, onRetry }: { error: string; onRetry?: () => void }) {
  return (
    <div className="banner error" role="alert">
      <p>{error}</p>
      <p className="muted small">
        API: <code>{API_BASE}</code>. Check your connection, then retry.
      </p>
      {onRetry && (
        <button type="button" className="cta" onClick={onRetry}>
          Retry
        </button>
      )}
    </div>
  )
}

export function Empty({ children }: { children: ReactNode }) {
  return <p className="banner muted">{children}</p>
}
