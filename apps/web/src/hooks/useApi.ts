import { useCallback, useEffect, useRef, useState } from 'react'

const cache = new Map<string, Promise<unknown>>()

export type ApiState<T> = {
  data: T | null
  error: string | null
  loading: boolean
  reload: () => void
}

/**
 * Fetch with a per-key promise cache so navigating between pages does not refetch
 * (the free-tier API can take a while to wake up). Failed requests are evicted.
 */
export function useApi<T>(key: string | null, fetcher: () => Promise<T>): ApiState<T> {
  const [state, setState] = useState<{ key: string | null; data: T | null; error: string | null }>({
    key: null,
    data: null,
    error: null,
  })
  const [attempt, setAttempt] = useState(0)
  const fetcherRef = useRef(fetcher)

  useEffect(() => {
    fetcherRef.current = fetcher
  })

  useEffect(() => {
    if (key === null) return
    let cancelled = false
    let promise = cache.get(key) as Promise<T> | undefined
    if (!promise) {
      promise = fetcherRef.current()
      cache.set(key, promise)
    }
    promise
      .then((data) => {
        if (!cancelled) setState({ key, data, error: null })
      })
      .catch((err: unknown) => {
        cache.delete(key)
        if (!cancelled) {
          setState({ key, data: null, error: err instanceof Error ? err.message : 'Request failed' })
        }
      })
    return () => {
      cancelled = true
    }
  }, [key, attempt])

  const reload = useCallback(() => {
    if (key) cache.delete(key)
    setAttempt((n) => n + 1)
  }, [key])

  const current = state.key === key
  return {
    data: current ? state.data : null,
    error: current ? state.error : null,
    loading: key !== null && (!current || (state.data === null && state.error === null)),
    reload,
  }
}
