import { jwtDecode } from 'jwt-decode'
import { create } from 'zustand'

const AUTH_STORAGE_KEY = 'book-ninja.auth'

export type AuthUser = {
  name: string
  email: string
  picture: string | null
}

type GoogleCredentialPayload = {
  name?: string
  given_name?: string
  email?: string
  picture?: string
}

type StoredAuthSession = {
  token: string
}

type AuthState = {
  token: string | null
  user: AuthUser | null
  setToken: (token: string) => void
  clearToken: () => void
}

const fallbackUser: AuthUser = {
  name: 'Book Ninja Reader',
  email: 'reader@bookninja.local',
  picture: null,
}

function userFromCredential(credential: string | null | undefined): AuthUser {
  if (!credential) {
    return fallbackUser
  }

  try {
    const payload = jwtDecode<GoogleCredentialPayload>(credential)
    return {
      name: payload.name || payload.given_name || fallbackUser.name,
      email: payload.email || fallbackUser.email,
      picture: payload.picture || null,
    }
  } catch {
    return fallbackUser
  }
}

function isStoredAuthSession(value: unknown): value is StoredAuthSession {
  if (!value || typeof value !== 'object') {
    return false
  }

  return typeof (value as Partial<StoredAuthSession>).token === 'string'
}

function loadStoredToken(): string | null {
  try {
    const rawSession = window.localStorage.getItem(AUTH_STORAGE_KEY)
    if (!rawSession) {
      return null
    }

    const parsedSession: unknown = JSON.parse(rawSession)
    if (!isStoredAuthSession(parsedSession)) {
      window.localStorage.removeItem(AUTH_STORAGE_KEY)
      return null
    }

    return parsedSession.token
  } catch {
    window.localStorage.removeItem(AUTH_STORAGE_KEY)
    return null
  }
}

function persistToken(token: string) {
  window.localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify({ token }))
}

function clearStoredToken() {
  window.localStorage.removeItem(AUTH_STORAGE_KEY)
}

const storedToken = loadStoredToken()

export const useAuthStore = create<AuthState>((set) => ({
  token: storedToken,
  user: storedToken ? userFromCredential(storedToken) : null,
  setToken: (token) => {
    persistToken(token)
    set({ token, user: userFromCredential(token) })
  },
  clearToken: () => {
    clearStoredToken()
    set({ token: null, user: null })
  },
}))
