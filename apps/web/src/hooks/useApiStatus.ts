import { useCallback, useEffect, useRef, useState } from 'react'
import { getHealth, type HealthResponse } from '../api/client'

export type ApiState = 'checking' | 'waking' | 'online' | 'offline'

export type ApiStatus = {
  state: ApiState
  health: HealthResponse | null
  latencyMs: number | null
  recheck: () => void
}

const WAKING_AFTER_MS = 4_000

/** Checks /health once per page load; a failed check can be retried manually. */
export function useApiStatus(): ApiStatus {
  const [state, setState] = useState<ApiState>('checking')
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [latencyMs, setLatencyMs] = useState<number | null>(null)
  const inFlight = useRef(false)

  const check = useCallback(async () => {
    if (inFlight.current) return
    inFlight.current = true
    setState('checking')
    const started = performance.now()
    const wakeTimer = setTimeout(() => setState('waking'), WAKING_AFTER_MS)
    try {
      setHealth(await getHealth())
      setLatencyMs(Math.round(performance.now() - started))
      setState('online')
    } catch {
      setState('offline')
    } finally {
      clearTimeout(wakeTimer)
      inFlight.current = false
    }
  }, [])

  useEffect(() => {
    const first = setTimeout(() => void check(), 0)
    return () => clearTimeout(first)
  }, [check])

  return { state, health, latencyMs, recheck: () => void check() }
}
