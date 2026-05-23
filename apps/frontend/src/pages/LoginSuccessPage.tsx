import React, { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

export default function LoginSuccessPage() {
  const navigate = useNavigate()

  useEffect(() => {
    const timer = setTimeout(() => {
      navigate('/chat', { replace: true })
    }, 1200)

    return () => clearTimeout(timer)
  }, [navigate])

  return (
    <main style={{ padding: '2rem', textAlign: 'center' }}>
      <h1>Login successful</h1>
      <p>Preparing your Book Ninja chat...</p>
    </main>
  )
}
