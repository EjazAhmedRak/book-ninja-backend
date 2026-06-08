import React, { ReactNode, useEffect, useState } from 'react'
import { Navigate } from 'react-router-dom'
import { verifyAuthToken } from '../api/auth'
import { useAuthStore } from '../store/useAuthStore'

type ProtectedRouteProps = {
  children: ReactNode
}

export default function ProtectedRoute({ children }: ProtectedRouteProps) {
  const token = useAuthStore((state) => state.token)
  const clearToken = useAuthStore((state) => state.clearToken)
  const [verificationStatus, setVerificationStatus] = useState<'idle' | 'checking' | 'valid'>(
    token ? 'checking' : 'idle'
  )

  useEffect(() => {
    let isCurrent = true

    if (!token) {
      setVerificationStatus('idle')
      return () => {
        isCurrent = false
      }
    }

    setVerificationStatus('checking')
    verifyAuthToken(token)
      .then(() => {
        if (isCurrent) {
          setVerificationStatus('valid')
        }
      })
      .catch(() => {
        if (isCurrent) {
          clearToken()
          setVerificationStatus('idle')
        }
      })

    return () => {
      isCurrent = false
    }
  }, [clearToken, token])

  if (!token) {
    return <Navigate to="/login" replace />
  }

  if (verificationStatus !== 'valid') {
    return (
      <main
        role="status"
        style={{
          alignItems: 'center',
          background: '#f8fafc',
          color: '#0f172a',
          display: 'grid',
          minHeight: '100vh',
          padding: '2rem',
          textAlign: 'center',
        }}
      >
        Verifying session...
      </main>
    )
  }

  return children
}
