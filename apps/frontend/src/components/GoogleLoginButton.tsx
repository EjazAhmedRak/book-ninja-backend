import React, { useState } from 'react'
import { CredentialResponse, GoogleLogin } from '@react-oauth/google'
import GoogleIcon from './GoogleIcon'

type GoogleLoginButtonProps = {
  onCredential: (credential: string) => void
}

export default function GoogleLoginButton({ onCredential }: GoogleLoginButtonProps) {
  const [error, setError] = useState('')
  const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID

  if (!googleClientId) {
    return (
      <p role="alert" style={{ color: '#b91c1c', fontWeight: 800, margin: 0 }}>
        Google sign-in is not configured. Set VITE_GOOGLE_CLIENT_ID to continue.
      </p>
    )
  }

  const handleSuccess = (credentialResponse: CredentialResponse) => {
    const credential = credentialResponse.credential
    if (!credential) {
      setError('Google did not return a sign-in credential. Please try again.')
      return
    }

    setError('')
    onCredential(credential)
  }

  return (
    <div style={{ display: 'grid', gap: '0.75rem', justifyItems: 'center' }}>
      <div
        style={{
          display: 'grid',
          minHeight: 48,
          minWidth: 240,
          position: 'relative',
        }}
      >
        <button
          type="button"
          tabIndex={-1}
          aria-hidden="true"
          style={{
            alignItems: 'center',
            background: '#ffffff',
            border: '1px solid #d1d5db',
            borderRadius: '999px',
            boxShadow: '0 18px 35px rgba(25, 167, 222, 0.16)',
            color: '#111827',
            display: 'inline-flex',
            fontSize: '1rem',
            fontWeight: 900,
            gap: '0.65rem',
            gridArea: '1 / 1',
            justifyContent: 'center',
            padding: '0.85rem 1.3rem',
            pointerEvents: 'none',
          }}
        >
          <GoogleIcon />
          Continue with Google
        </button>
        <div style={{ gridArea: '1 / 1', opacity: 0.02 }}>
          <GoogleLogin onSuccess={handleSuccess} onError={() => setError('Google sign-in failed. Please try again.')} />
        </div>
      </div>
      {error ? (
        <p role="alert" style={{ color: '#b91c1c', fontWeight: 800, margin: 0 }}>
          {error}
        </p>
      ) : null}
    </div>
  )
}
