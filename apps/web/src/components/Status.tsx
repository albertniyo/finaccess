import type { ReactNode } from 'react'
import { API_BASE } from '../api/client'

export function Loading({ label = 'Loading evidence…' }: { label?: string }) {
  return (
    <p className="banner loading" role="status" aria-live="polite">
      <span className="spinner" aria-hidden="true" /> {label}
    </p>
  )
}

export function ErrorState({ error, onRetry }: { error: string; onRetry?: () => void }) {
  return (
    <div className="banner error" role="alert">
      <p>{error}</p>
      <p className="muted small">
        API: <code>{API_BASE}</code>. The free-tier backend can take up to a minute to wake up.
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
