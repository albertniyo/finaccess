/** Thin fetch wrapper for the FastAPI backend (proxied via /api in dev). */

import type {
  BriefResponse,
  GeoCollection,
  IndicatorsResponse,
  Measure,
  MethodResponse,
  PrioritiesResponse,
  ScenarioRequest,
  ScenarioResponse,
  SourcesResponse,
  ValidationResponse,
} from './types'

export const API_BASE = (import.meta.env.VITE_API_BASE ?? '/api').replace(/\/+$/, '')

export class ApiError extends Error {
  readonly status: number

  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

// A sleeping free-tier host can take about a minute to wake; until then its proxy fails without CORS headers.
const RETRY_DELAYS_MS = [2000, 3000, 5000, 8000, 10000, 12000, 15000]
const RETRYABLE_STATUS = new Set([502, 503, 504])

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

async function fetchWithWake(url: string, init: RequestInit): Promise<Response> {
  for (let attempt = 0; ; attempt++) {
    const last = attempt >= RETRY_DELAYS_MS.length
    try {
      const response = await fetch(url, init)
      if (last || !RETRYABLE_STATUS.has(response.status)) return response
    } catch (err) {
      if (last) throw err
    }
    await sleep(RETRY_DELAYS_MS[attempt])
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response
  try {
    response = await fetchWithWake(`${API_BASE}${path}`, {
      ...init,
      headers: { Accept: 'application/json', ...(init?.headers ?? {}) },
    })
  } catch {
    throw new ApiError(0, `Cannot reach the API at ${API_BASE}.`)
  }
  if (!response.ok) {
    let detail = response.statusText
    try {
      const body = (await response.json()) as { detail?: unknown }
      if (typeof body.detail === 'string') detail = body.detail
    } catch {
      /* non-JSON error body */
    }
    throw new ApiError(response.status, `API ${response.status}: ${detail}`)
  }
  return response.json() as Promise<T>
}

export function getSources() {
  return request<SourcesResponse>('/meta/sources')
}

export function getValidation() {
  return request<ValidationResponse>('/meta/validation')
}

export function getMethod() {
  return request<MethodResponse>('/meta/method')
}

export function getIndicators(params?: { province?: string }) {
  const qs = params?.province ? `?province=${encodeURIComponent(params.province)}` : ''
  return request<IndicatorsResponse>(`/indicators${qs}`)
}

export function getGeo() {
  return request<GeoCollection>('/geo/districts')
}

export type AnalysisParams = { povertyWeight: number; measure: Measure }

export function getPriorities({ povertyWeight, measure }: AnalysisParams) {
  const search = new URLSearchParams({
    povertyWeight: String(povertyWeight),
    exclusionWeight: String(+(1 - povertyWeight).toFixed(4)),
    measure,
  })
  return request<PrioritiesResponse>(`/priorities?${search}`)
}

export function createScenario(body: ScenarioRequest) {
  return request<ScenarioResponse>('/scenarios', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
}

export function createBrief(body: { geo: string } & AnalysisParams) {
  return request<BriefResponse>('/briefs', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      geo: body.geo,
      povertyWeight: body.povertyWeight,
      exclusionWeight: +(1 - body.povertyWeight).toFixed(4),
      measure: body.measure,
    }),
  })
}
