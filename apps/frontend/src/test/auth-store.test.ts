import { beforeEach, describe, expect, test, vi } from 'vitest'

const AUTH_STORAGE_KEY = 'book-ninja.auth'

vi.mock('jwt-decode', () => ({
  jwtDecode: () => ({
    name: 'Ada Lovelace',
    email: 'ada@example.com',
    picture: 'https://example.com/ada.png',
  }),
}))

async function importFreshAuthStore() {
  vi.resetModules()
  return import('../store/useAuthStore')
}

describe('auth store session persistence', () => {
  beforeEach(() => {
    window.localStorage.clear()
  })

  test('persists Google ID token to localStorage when token is set', async () => {
    const { useAuthStore } = await importFreshAuthStore()

    useAuthStore.getState().setToken('google-id-token')

    expect(window.localStorage.getItem(AUTH_STORAGE_KEY)).toBe(JSON.stringify({ token: 'google-id-token' }))
    expect(useAuthStore.getState().user).toMatchObject({ name: 'Ada Lovelace', email: 'ada@example.com' })
  })

  test('hydrates token and user from localStorage on store initialization', async () => {
    window.localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify({ token: 'stored-google-id-token' }))

    const { useAuthStore } = await importFreshAuthStore()

    expect(useAuthStore.getState().token).toBe('stored-google-id-token')
    expect(useAuthStore.getState().user).toMatchObject({ name: 'Ada Lovelace', email: 'ada@example.com' })
  })

  test('clears localStorage session on logout', async () => {
    const { useAuthStore } = await importFreshAuthStore()

    useAuthStore.getState().setToken('google-id-token')
    useAuthStore.getState().clearToken()

    expect(window.localStorage.getItem(AUTH_STORAGE_KEY)).toBeNull()
    expect(useAuthStore.getState().token).toBeNull()
    expect(useAuthStore.getState().user).toBeNull()
  })

  test('ignores corrupt localStorage auth session', async () => {
    window.localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify({ token: 123 }))

    const { useAuthStore } = await importFreshAuthStore()

    expect(useAuthStore.getState().token).toBeNull()
    expect(window.localStorage.getItem(AUTH_STORAGE_KEY)).toBeNull()
  })
})
