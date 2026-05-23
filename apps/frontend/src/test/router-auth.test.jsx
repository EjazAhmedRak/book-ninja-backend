import React from 'react'
import { beforeEach, describe, expect, test } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import AppRouter from '../AppRouter'
import { useAuthStore } from '../store/useAuthStore'

describe('router auth guard', () => {
  beforeEach(() => {
    useAuthStore.setState({ token: null })
  })

  test('redirects /chat to /login when token is missing', async () => {
    render(
      <MemoryRouter initialEntries={['/chat']}>
        <AppRouter />
      </MemoryRouter>
    )

    expect(await screen.findByRole('heading', { name: /sign in to book ninja/i })).toBeInTheDocument()
  })

  test('renders chat page when token exists', async () => {
    useAuthStore.setState({ token: 'token-123' })

    render(
      <MemoryRouter initialEntries={['/chat']}>
        <AppRouter />
      </MemoryRouter>
    )

    expect(await screen.findByRole('heading', { name: /welcome to book ninja/i })).toBeInTheDocument()
  })
})
