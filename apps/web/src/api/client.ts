/** Thin fetch wrapper for the FastAPI backend (proxied via /api in dev). */

const API_BASE = import.meta.env.VITE_API_BASE ?? '/api'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { Accept: 'application/json', ...(init?.headers ?? {}) },
    ...init,
  })
  if (!response.ok) {
    throw new Error(`API ${response.status}: ${response.statusText}`)
  }
  return response.json() as Promise<T>
}

export function getHealth() {
  return request<{ status: string }>('/health')
}

export function getSources() {
  return request<{ sources: unknown[]; note?: string }>('/meta/sources')
}

export function getIndicators(params?: { geo?: string }) {
  const qs = params?.geo ? `?geo=${encodeURIComponent(params.geo)}` : ''
  return request<{ status: string; series: unknown[] }>(`/indicators${qs}`)
}

export function getPriorities(weights?: { povertyWeight?: number; exclusionWeight?: number }) {
  const search = new URLSearchParams()
  if (weights?.povertyWeight != null) search.set('povertyWeight', String(weights.povertyWeight))
  if (weights?.exclusionWeight != null) search.set('exclusionWeight', String(weights.exclusionWeight))
  const qs = search.toString() ? `?${search}` : ''
  return request<{ status: string; rankings: unknown[]; weights: Record<string, unknown> }>(
    `/priorities${qs}`,
  )
}

export function createBrief(body: { geo: string; povertyWeight?: number; exclusionWeight?: number }) {
  return request<{ status: string; geo: string; sections: Record<string, unknown> }>('/briefs', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
}