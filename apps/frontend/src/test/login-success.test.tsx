import React from 'react'
import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest'
import './google-oauth.mock'
import { mockGoogleCredential } from './google-oauth.mock'
import { act, fireEvent, render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import AppRouter from '../AppRouter'
import { useAuthStore } from '../store/useAuthStore'

describe('login success transition', () => {
  const fetchMock = vi.fn()

  beforeEach(() => {
    vi.stubEnv('VITE_GOOGLE_CLIENT_ID', 'test-client-id.apps.googleusercontent.com')
    vi.stubGlobal('fetch', fetchMock)
    fetchMock.mockReset()
    useAuthStore.setState({ token: null, user: null })
  })

  afterEach(() => {
    vi.useRealTimers()
    vi.unstubAllEnvs()
  })

  test('google login action verifies token with backend before storing session', async () => {
    fetchMock.mockResolvedValueOnce(
      new Response(JSON.stringify({ sub: 'user123', email: 'ada@example.com' }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      })
    )

    render(
      <MemoryRouter future={{ v7_relativeSplatPath: true, v7_startTransition: true }} initialEntries={['/login']}>
        <AppRouter />
      </MemoryRouter>
    )

    fireEvent.click(screen.getByRole('button', { name: /continue with google/i }))

    expect(await screen.findByRole('heading', { name: /login successful/i })).toBeInTheDocument()
    expect(fetchMock).toHaveBeenCalledWith(
      'http://localhost:8000/auth/me',
      expect.objectContaining({
        headers: expect.objectContaining({ Authorization: `Bearer ${mockGoogleCredential}` }),
      })
    )
    expect(useAuthStore.getState().token).toBe(mockGoogleCredential)
    expect(useAuthStore.getState().user).toMatchObject({ name: 'Ada Lovelace', email: 'ada@example.com' })
  })

  test('google login does not store session when backend rejects token', async () => {
    fetchMock.mockResolvedValueOnce(
      new Response(JSON.stringify({ detail: 'Invalid token' }), {
        status: 401,
        headers: { 'Content-Type': 'application/json' },
      })
    )

    render(
      <MemoryRouter future={{ v7_relativeSplatPath: true, v7_startTransition: true }} initialEntries={['/login']}>
        <AppRouter />
      </MemoryRouter>
    )

    fireEvent.click(screen.getByRole('button', { name: /continue with google/i }))

    expect(await screen.findByRole('alert')).toHaveTextContent(/could not verify your google sign-in/i)
    expect(useAuthStore.getState().token).toBeNull()
  })

  test('login-success auto-redirects to /chat', async () => {
    vi.useFakeTimers()
    fetchMock.mockResolvedValueOnce(
      new Response(JSON.stringify({ sub: 'user123', email: 'ada@example.com' }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      })
    )
    useAuthStore.setState({ token: mockGoogleCredential })

    render(
      <MemoryRouter future={{ v7_relativeSplatPath: true, v7_startTransition: true }} initialEntries={['/login-success']}>
        <AppRouter />
      </MemoryRouter>
    )

    act(() => {
      vi.advanceTimersByTime(1300)
    })
    vi.useRealTimers()

    expect(await screen.findByRole('heading', { name: /welcome to book ninja/i })).toBeInTheDocument()
  })
})
