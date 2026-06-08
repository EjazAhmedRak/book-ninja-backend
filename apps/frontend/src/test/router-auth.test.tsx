import React from 'react'
import './google-oauth.mock'
import { beforeEach, describe, expect, test, vi } from 'vitest'
import { fireEvent, render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import AppRouter from '../AppRouter'
import { useAuthStore } from '../store/useAuthStore'

describe('router auth guard', () => {
  const fetchMock = vi.fn()

  beforeEach(() => {
    vi.stubGlobal('fetch', fetchMock)
    fetchMock.mockReset()
    useAuthStore.setState({ token: null, user: null })
  })

  test('redirects /chat to /login when token is missing', async () => {
    render(
      <MemoryRouter future={{ v7_relativeSplatPath: true, v7_startTransition: true }} initialEntries={['/chat']}>
        <AppRouter />
      </MemoryRouter>
    )

    expect(await screen.findByRole('heading', { name: /sign in to book ninja/i })).toBeInTheDocument()
  })

  test('verifies stored token before rendering chat page', async () => {
    fetchMock.mockResolvedValueOnce(
      new Response(JSON.stringify({ sub: 'user123', email: 'ada@example.com' }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      })
    )
    useAuthStore.setState({
      token: 'token-123',
      user: { name: 'Ada Lovelace', email: 'ada@example.com', picture: null },
    })

    render(
      <MemoryRouter future={{ v7_relativeSplatPath: true, v7_startTransition: true }} initialEntries={['/chat']}>
        <AppRouter />
      </MemoryRouter>
    )

    expect(screen.getByRole('status')).toHaveTextContent(/verifying session/i)
    expect(await screen.findByRole('heading', { name: /welcome to book ninja/i })).toBeInTheDocument()
    expect(fetchMock).toHaveBeenCalledWith(
      'http://localhost:8000/auth/me',
      expect.objectContaining({
        headers: expect.objectContaining({ Authorization: 'Bearer token-123' }),
      })
    )
  })

  test('clears invalid stored token and redirects to login', async () => {
    fetchMock.mockResolvedValueOnce(
      new Response(JSON.stringify({ detail: 'Invalid token' }), {
        status: 401,
        headers: { 'Content-Type': 'application/json' },
      })
    )
    useAuthStore.setState({
      token: 'expired-token',
      user: { name: 'Ada Lovelace', email: 'ada@example.com', picture: null },
    })

    render(
      <MemoryRouter future={{ v7_relativeSplatPath: true, v7_startTransition: true }} initialEntries={['/chat']}>
        <AppRouter />
      </MemoryRouter>
    )

    expect(await screen.findByRole('heading', { name: /sign in to book ninja/i })).toBeInTheDocument()
    expect(useAuthStore.getState().token).toBeNull()
  })

  test('logout clears token and returns user to login page', async () => {
    fetchMock.mockResolvedValueOnce(
      new Response(JSON.stringify({ sub: 'user123', email: 'ada@example.com' }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      })
    )
    useAuthStore.setState({
      token: 'token-123',
      user: { name: 'Ada Lovelace', email: 'ada@example.com', picture: null },
    })

    render(
      <MemoryRouter future={{ v7_relativeSplatPath: true, v7_startTransition: true }} initialEntries={['/chat']}>
        <AppRouter />
      </MemoryRouter>
    )

    fireEvent.click(await screen.findByRole('button', { name: /logout/i }))

    expect(await screen.findByRole('heading', { name: /sign in to book ninja/i })).toBeInTheDocument()
    expect(useAuthStore.getState().token).toBeNull()
  })
})
