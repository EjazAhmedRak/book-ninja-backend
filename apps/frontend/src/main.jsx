import React from 'react'
import { createRoot } from 'react-dom/client'

function App() {
  return (
    <main style={{ fontFamily: 'system-ui', padding: '2rem' }}>
      <h1>Book Ninja Frontend</h1>
      <p>Monorepo scaffold is ready.</p>
    </main>
  )
}

createRoot(document.getElementById('root')).render(<App />)
