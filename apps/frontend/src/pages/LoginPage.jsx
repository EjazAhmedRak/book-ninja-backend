import React from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/useAuthStore'

export default function LoginPage() {
  const navigate = useNavigate()
  const setToken = useAuthStore((state) => state.setToken)

  const handleLogin = () => {
    setToken('demo-token')
    navigate('/login-success')
  }

  return (
    <main style={{ padding: '2rem', maxWidth: 520, margin: '0 auto' }}>
      <h1>Sign in to Book Ninja</h1>
      <p>Continue to access your personalized book assistant.</p>
      <button type="button" onClick={handleLogin}>
        Continue with Google
      </button>
    </main>
  )
}
