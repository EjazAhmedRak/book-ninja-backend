import React from 'react'
import ChatWindow from '../components/ChatWindow'
import WelcomeBanner from '../components/WelcomeBanner'

export default function ChatPage() {
  return (
    <main style={{ background: '#f8fafc', minHeight: '100vh', padding: 'clamp(1rem, 4vw, 2rem)' }}>
      <div style={{ margin: '0 auto', maxWidth: 960 }}>
        <WelcomeBanner />
        <ChatWindow />
      </div>
    </main>
  )
}
