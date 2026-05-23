import { jwtDecode } from 'jwt-decode'
import { create } from 'zustand'

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

export const useAuthStore = create<AuthState>((set) => ({
  token: null,
  user: null,
  setToken: (token) => set({ token, user: userFromCredential(token) }),
  clearToken: () => set({ token: null, user: null }),
}))
