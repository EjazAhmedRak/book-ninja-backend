import React from 'react'
import { beforeEach, describe, expect, test } from 'vitest'
import { fireEvent, render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import AppRouter from '../AppRouter'
import { useAuthStore } from '../store/useAuthStore'

describe('router auth guard', () => {
  beforeEach(() => {
    useAuthStore.setState({ token: null })
  })

  test('redirects /chat to /login when token is missing', async () => {
    render(
      <MemoryRouter future={{ v7_relativeSplatPath: true, v7_startTransition: true }} initialEntries={['/chat']}>
        <AppRouter />
      </MemoryRouter>
    )

    expect(await screen.findByRole('heading', { name: /sign in to book ninja/i })).toBeInTheDocument()
  })

  test('renders chat page when token exists', async () => {
    useAuthStore.setState({ token: 'token-123' })

    render(
      <MemoryRouter future={{ v7_relativeSplatPath: true, v7_startTransition: true }} initialEntries={['/chat']}>
        <AppRouter />
      </MemoryRouter>
    )

    expect(await screen.findByRole('heading', { name: /welcome to book ninja/i })).toBeInTheDocument()
  })

  test('logout clears token and returns user to login page', async () => {
    useAuthStore.setState({ token: 'token-123' })

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
