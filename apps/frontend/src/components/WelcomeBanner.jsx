import React from 'react'

export default function WelcomeBanner() {
  return (
    <section
      aria-label="Welcome banner"
      style={{
        background: 'linear-gradient(135deg, #e0f2fe 0%, #dcfce7 52%, #fef3c7 100%)',
        border: '1px solid #86efac',
        borderRadius: '18px',
        boxShadow: '0 20px 50px rgba(15, 23, 42, 0.08)',
        marginBottom: '1rem',
        padding: '1.25rem',
      }}
    >
      <p style={{ color: '#166534', fontSize: '0.78rem', fontWeight: 700, letterSpacing: '0.12em', margin: 0 }}>
        BOOK NINJA CHAT
      </p>
      <h1 style={{ color: '#0f172a', fontSize: 'clamp(2rem, 5vw, 3.5rem)', lineHeight: 1, margin: '0.35rem 0' }}>
        Welcome to Book Ninja
      </h1>
      <p style={{ color: '#334155', margin: 0, maxWidth: 640 }}>
        You are signed in. Start a chat to discover your next read, format, or purchase path.
      </p>
    </section>
  )
}
