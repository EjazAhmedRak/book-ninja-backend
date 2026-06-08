import React from 'react'
import { useNavigate } from 'react-router-dom'
import { verifyAuthToken } from '../api/auth'
import bookNinjaLogo from '../assets/book-ninja-logo.svg'
import GoogleLoginButton from '../components/GoogleLoginButton'
import { useAuthStore } from '../store/useAuthStore'

export default function LoginPage() {
  const navigate = useNavigate()
  const setToken = useAuthStore((state) => state.setToken)
  const [authError, setAuthError] = React.useState('')

  const handleCredential = async (credential: string) => {
    try {
      setAuthError('')
      await verifyAuthToken(credential)
      setToken(credential)
      navigate('/login-success')
    } catch {
      setAuthError('Could not verify your Google sign-in with Book Ninja. Please try again.')
    }
  }

  return (
    <main
      style={{
        alignItems: 'center',
        background:
          'radial-gradient(circle at 15% 20%, rgba(255, 133, 0, 0.18), transparent 28%), radial-gradient(circle at 85% 10%, rgba(25, 167, 222, 0.18), transparent 25%), linear-gradient(135deg, #fff7ed 0%, #f8fafc 50%, #ecfeff 100%)',
        color: '#0f172a',
        display: 'grid',
        minHeight: '100vh',
        padding: 'clamp(1rem, 4vw, 3rem)',
      }}
    >
      <section
        aria-label="Login panel"
        style={{
          background: 'rgba(255, 255, 255, 0.92)',
          border: '1px solid rgba(148, 163, 184, 0.28)',
          borderRadius: '32px',
          boxShadow: '0 32px 90px rgba(15, 23, 42, 0.14)',
          display: 'grid',
          gap: '1.5rem',
          justifyItems: 'center',
          margin: '0 auto',
          maxWidth: 720,
          overflow: 'hidden',
          padding: 'clamp(1.5rem, 5vw, 3.5rem)',
          textAlign: 'center',
          width: '100%',
        }}
      >
        <img
          src={bookNinjaLogo}
          alt="Book Ninja logo"
          style={{ height: 'auto', maxWidth: 360, width: 'min(72vw, 360px)' }}
        />

        <div>
          <p style={{ color: '#19a7de', fontSize: '0.82rem', fontWeight: 900, letterSpacing: '0.18em', margin: 0 }}>
            SEARCH | READ | DOWNLOAD
          </p>
          <h1 style={{ fontSize: 'clamp(2rem, 6vw, 4rem)', lineHeight: 0.95, margin: '0.65rem 0 0.85rem' }}>
            Sign in to Book Ninja
          </h1>
          <p style={{ color: '#475569', fontSize: '1.05rem', margin: '0 auto', maxWidth: 520 }}>
            Continue to access your personalized book assistant for discovery, reading formats, and download paths.
          </p>
        </div>

        <GoogleLoginButton onCredential={handleCredential} />
        {authError ? (
          <p role="alert" style={{ color: '#b91c1c', fontWeight: 800, margin: 0 }}>
            {authError}
          </p>
        ) : null}
      </section>
    </main>
  )
}
