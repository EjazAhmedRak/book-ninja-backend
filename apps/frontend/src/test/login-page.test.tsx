import React from 'react'
import { beforeEach, describe, expect, test, vi } from 'vitest'
import './google-oauth.mock'
import { googleLoginControls } from './google-oauth.mock'
import { fireEvent, render, screen } from '@testing-library/react'
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
  beforeEach(() => {
    vi.stubEnv('VITE_GOOGLE_CLIENT_ID', 'test-client-id.apps.googleusercontent.com')
    googleLoginControls.shouldFail = false
    googleLoginControls.missingCredential = false
  })

  test('renders the Book Ninja logo image, brand actions, and Google sign-in button', () => {
    renderLoginPage()

    expect(screen.getByRole('img', { name: /book ninja logo/i })).toBeInTheDocument()
    expect(screen.getByText('SEARCH | READ | DOWNLOAD')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /continue with google/i })).toBeInTheDocument()
  })

  test('shows a sign-in failure message when Google login fails', () => {
    googleLoginControls.shouldFail = true
    renderLoginPage()

    fireEvent.click(screen.getByRole('button', { name: /continue with google/i }))

    expect(screen.getByRole('alert')).toHaveTextContent(/google sign-in failed/i)
  })
})
