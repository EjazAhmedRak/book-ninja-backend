import React from 'react'
import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest'
import './google-oauth.mock'
import { mockGoogleCredential } from './google-oauth.mock'
import { act, fireEvent, render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import AppRouter from '../AppRouter'
import { useAuthStore } from '../store/useAuthStore'

describe('login success transition', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    vi.stubEnv('VITE_GOOGLE_CLIENT_ID', 'test-client-id.apps.googleusercontent.com')
    useAuthStore.setState({ token: null, user: null })
  })

  afterEach(() => {
    vi.useRealTimers()
    vi.unstubAllEnvs()
  })

  test('google login action sets token, user, and navigates to login-success', () => {
    render(
      <MemoryRouter future={{ v7_relativeSplatPath: true, v7_startTransition: true }} initialEntries={['/login']}>
        <AppRouter />
      </MemoryRouter>
    )

    fireEvent.click(screen.getByRole('button', { name: /continue with google/i }))

    expect(screen.getByRole('heading', { name: /login successful/i })).toBeInTheDocument()
    expect(useAuthStore.getState().token).toBe(mockGoogleCredential)
    expect(useAuthStore.getState().user).toMatchObject({ name: 'Ada Lovelace', email: 'ada@example.com' })
  })

  test('login-success auto-redirects to /chat', () => {
    useAuthStore.setState({ token: mockGoogleCredential })

    render(
      <MemoryRouter future={{ v7_relativeSplatPath: true, v7_startTransition: true }} initialEntries={['/login-success']}>
        <AppRouter />
      </MemoryRouter>
    )

    act(() => {
      vi.advanceTimersByTime(1300)
    })

    expect(screen.getByRole('heading', { name: /welcome to book ninja/i })).toBeInTheDocument()
  })
})
