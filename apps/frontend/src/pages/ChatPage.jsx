import React from 'react'
import { useNavigate } from 'react-router-dom'
import ChatWindow from '../components/ChatWindow'
import WelcomeBanner from '../components/WelcomeBanner'
import { useAuthStore } from '../store/useAuthStore'

export default function ChatPage() {
  const navigate = useNavigate()
  const clearToken = useAuthStore((state) => state.clearToken)

  const handleLogout = () => {
    clearToken()
    navigate('/login', { replace: true })
  }

  return (
    <main style={{ background: '#f8fafc', minHeight: '100vh', padding: 'clamp(1rem, 4vw, 2rem)' }}>
      <div style={{ margin: '0 auto', maxWidth: 960 }}>
        <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '0.75rem' }}>
          <button
            type="button"
            onClick={handleLogout}
            style={{
              background: '#0f172a',
              border: 0,
              borderRadius: '999px',
              color: '#ffffff',
              cursor: 'pointer',
              fontWeight: 800,
              padding: '0.65rem 1rem',
            }}
          >
            Logout
          </button>
        </div>
        <WelcomeBanner />
        <ChatWindow />
      </div>
    </main>
  )
}
