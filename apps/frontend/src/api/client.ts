const DEFAULT_API_BASE_URL = 'http://localhost:8000'

type ApiRequestOptions = Omit<RequestInit, 'headers'> & {
  headers?: Record<string, string>
  token?: string
}

type ErrorResponse = {
  detail?: string
  error?: string
}

export class ApiError extends Error {
  status: number

  constructor(message: string, status: number) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

function getApiBaseUrl() {
  return (import.meta.env.VITE_API_BASE_URL || DEFAULT_API_BASE_URL).replace(/\/+$/, '')
}

function buildApiUrl(path: string) {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`
  return `${getApiBaseUrl()}${normalizedPath}`
}

async function readErrorMessage(response: Response) {
  const body = (await response.json().catch(() => null)) as ErrorResponse | null
  return body?.detail || body?.error || `HTTP ${response.status}`
}

export async function apiRequest<T>(path: string, options: ApiRequestOptions = {}): Promise<T> {
  const { headers = {}, token, body, ...requestOptions } = options
  const nextHeaders: Record<string, string> = { ...headers }

  if (token) {
    nextHeaders.Authorization = `Bearer ${token}`
  }

  if (body && !nextHeaders['Content-Type']) {
    nextHeaders['Content-Type'] = 'application/json'
  }

  const response = await fetch(buildApiUrl(path), {
    ...requestOptions,
    body,
    headers: nextHeaders,
  })

  if (!response.ok) {
    throw new ApiError(await readErrorMessage(response), response.status)
  }

  return response.json() as Promise<T>
}
