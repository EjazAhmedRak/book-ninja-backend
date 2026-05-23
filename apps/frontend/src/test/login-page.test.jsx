import React from 'react'
import { describe, expect, test } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import LoginPage from '../pages/LoginPage'

function renderLoginPage() {
  return render(
    <MemoryRouter future={{ v7_relativeSplatPath: true, v7_startTransition: true }}>
      <LoginPage />
    </MemoryRouter>
  )
}

describe('login page branding', () => {
  test('renders the Book Ninja logo image and brand actions', () => {
    renderLoginPage()

    expect(screen.getByRole('img', { name: /book ninja logo/i })).toBeInTheDocument()
    expect(screen.getByText('SEARCH | READ | DOWNLOAD')).toBeInTheDocument()
  })
})
