# Book Ninja - Frontend Development Guide

**Version:** v2.1  
**Author:** Ejaz Ahmed Ansari  
**Date:** 18 May 2026  
**Status:** Draft

---

## 1. Overview

The Book Ninja frontend is a chat-based web and mobile application that allows users to interact with an AI agent to search for books, find purchase options, and locate downloadable ebook and audiobook files. The UI is designed to feel conversational and lightweight, built around a central chat window with a persistent thread history sidebar.

---

## 2. Tech Stack

| Technology | Purpose | Why |
|---|---|---|
| React | UI framework | Component-based, large ecosystem, ideal for dynamic chat interfaces |
| Vite | Build tool | Fast dev server and build times; native ESM; pairs well with React |
| Tailwind CSS | Styling | Utility-first; makes dark mode and responsive layouts straightforward |
| React Query (TanStack Query) | Server state for request/response APIs | Handles thread list, thread messages, health, caching, loading, and refetching |
| Zustand | Client/UI state | Lightweight store for UI state (active thread, sidebar open/closed, theme) |

### Why React Query + Zustand together?

These two tools have non-overlapping responsibilities. **React Query** manages server state for normal request/response endpoints (for example `/latestThreads`, `/threads/{thread_id}/messages`, and `/health`). **Zustand** manages local UI state (active thread, sidebar state, dark mode). `/chat` is a streaming SSE endpoint, so it is handled with a dedicated streaming hook (`useChat`) instead of a standard React Query query.

---

## 3. Project Setup

```bash
npm create vite@latest book-ninja-ui -- --template react
cd book-ninja-ui
npm install
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
npm install @tanstack/react-query zustand
npm install -D vitest @vitest/ui @testing-library/react @testing-library/jest-dom jsdom eslint eslint-plugin-react
```

### Vite config (`vite.config.js`)

```js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    setupFiles: './src/test/setup.js',
    globals: true,
  },
})
```

### Tailwind config (`tailwind.config.js`)

```js
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: { extend: {} },
  plugins: [],
}
```

---

## 4. Folder Structure

```
src/
├── api/
│   ├── client.js
│   ├── chatStream.js
│   └── threads.js
├── components/
│   ├── ChatWindow/
│   ├── MessageBubble/
│   ├── Sidebar/
│   ├── ThreadItem/
│   ├── LoginButton/
│   └── Header/
├── hooks/
│   ├── useChat.js
│   ├── useThreads.js
│   ├── useThreadMessages.js
│   └── useHealth.js
├── store/
│   ├── useUIStore.js
│   └── useAuthStore.js
├── utils/
│   └── validatePrompt.js
├── pages/
│   ├── ChatPage.jsx
│   └── LoginPage.jsx
├── test/
│   └── setup.js
└── main.jsx
```

---

## 5. Authentication - Google OAuth

Book Ninja uses Google OAuth for user authentication. The frontend issues the token; the backend validates it.

### Flow

1. User clicks "Sign in with Google"
2. Google returns an ID token to the frontend
3. The frontend stores the token in Zustand (`useAuthStore`)
4. Authenticated API calls include `Authorization: Bearer <token>` (`/chat`, `/latestThreads`, `/threads/{thread_id}/messages`)
5. The backend validates the token against Google's verification flow

### Implementation

```bash
npm install @react-oauth/google
```

```jsx
// main.jsx
import { GoogleOAuthProvider } from '@react-oauth/google'

<GoogleOAuthProvider clientId={import.meta.env.VITE_GOOGLE_CLIENT_ID}>
  <App />
</GoogleOAuthProvider>
```

```jsx
// components/LoginButton/LoginButton.jsx
import { GoogleLogin } from '@react-oauth/google'
import { useAuthStore } from '../../store/useAuthStore'

export default function LoginButton() {
  const setToken = useAuthStore(s => s.setToken)

  return (
    <GoogleLogin
      onSuccess={({ credential }) => setToken(credential)}
      onError={() => console.error('Login failed')}
    />
  )
}
```

```js
// store/useAuthStore.js
import { create } from 'zustand'

export const useAuthStore = create(set => ({
  token: null,
  user: null,
  setToken: token => set({ token }),
  setUser: user => set({ user }),
  logout: () => set({ token: null, user: null }),
}))
```

**Important:** Never store the token in `localStorage`. Keep it in Zustand memory only.

---

## 6. UI Components

### 6.1 App Layout

The app has a two-panel layout: a fixed sidebar on the left and the main chat area on the right. On mobile (Android), the sidebar collapses behind a hamburger icon.

```jsx
// pages/ChatPage.jsx
export default function ChatPage() {
  const sidebarOpen = useUIStore(s => s.sidebarOpen)

  return (
    <div className="flex h-screen bg-white dark:bg-gray-900">
      <Sidebar open={sidebarOpen} />
      <main className="flex-1 flex flex-col">
        <Header />
        <ChatWindow />
      </main>
    </div>
  )
}
```

### 6.2 Chat Interface

The chat window renders a scrollable list of messages and a fixed input bar at the bottom. User messages are right-aligned; agent responses are left-aligned.

```jsx
// components/ChatWindow/ChatWindow.jsx
import { useRef, useState, useEffect } from 'react'
import { useChat } from '../../hooks/useChat'
import { validatePrompt } from '../../utils/validatePrompt'

export default function ChatWindow() {
  const { messages, sendMessage, isLoading } = useChat()
  const [input, setInput] = useState('')
  const [inputError, setInputError] = useState(null)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = async () => {
    const validationError = validatePrompt(input)
    if (validationError) {
      setInputError(validationError)
      return
    }

    setInputError(null)
    try {
      await sendMessage(input)
      setInput('')
    } catch (err) {
      setInputError(err.message)
    }
  }

  return (
    <div className="flex flex-col flex-1 overflow-hidden">
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.map((msg, i) => <MessageBubble key={i} message={msg} />)}
        {isLoading && <TypingIndicator />}
        <div ref={bottomRef} />
      </div>

      <div className="p-4 border-t dark:border-gray-700 flex gap-2">
        <input
          className="flex-1 rounded-lg border px-4 py-2 dark:bg-gray-800 dark:text-white"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && handleSend()}
          placeholder="Search for a book, ask about genres..."
          inputMode="text"
          maxLength={3000}
          aria-invalid={Boolean(inputError)}
        />
        <button onClick={handleSend} disabled={isLoading}>Send</button>
      </div>

      {inputError && (
        <p className="px-4 pb-3 text-sm text-red-600 dark:text-red-400">{inputError}</p>
      )}
    </div>
  )
}
```

**Note:** `maxLength={3000}` mirrors backend max prompt length.

### 6.3 Sidebar - Thread History

The sidebar shows the 5 most recent threads. Each item displays the first 100 characters of the opening message and its timestamp. Clicking a thread selects it and loads message history via `/threads/{thread_id}/messages`.

```jsx
// components/Sidebar/Sidebar.jsx
export default function Sidebar({ open }) {
  const { data: threads, isLoading } = useThreads()
  const activeThreadId = useUIStore(s => s.activeThreadId)
  const setActiveThread = useUIStore(s => s.setActiveThread)

  return (
    <aside className={`w-64 bg-gray-100 dark:bg-gray-800 transition-all ${open ? '' : '-translate-x-full'}`}>
      <h2 className="p-4 font-semibold text-gray-700 dark:text-gray-200">Recent Chats</h2>
      {isLoading ? <Spinner /> : threads?.map(thread => (
        <ThreadItem
          key={thread.thread_id}
          thread={thread}
          active={thread.thread_id === activeThreadId}
          onClick={() => setActiveThread(thread.thread_id)}
        />
      ))}
      <button className="w-full p-4 text-left text-sm text-blue-500" onClick={() => setActiveThread(null)}>
        + New Chat
      </button>
    </aside>
  )
}
```

```jsx
// components/ThreadItem/ThreadItem.jsx
export default function ThreadItem({ thread, active, onClick }) {
  return (
    <button
      onClick={onClick}
      className={`w-full text-left px-4 py-3 text-sm hover:bg-gray-200 dark:hover:bg-gray-700 ${
        active ? 'bg-gray-200 dark:bg-gray-700 font-medium' : ''
      }`}
    >
      <p className="truncate text-gray-800 dark:text-gray-100">{thread.preview}</p>
      <p className="text-xs text-gray-400 mt-1">{new Date(thread.timestamp).toLocaleDateString()}</p>
    </button>
  )
}
```

### 6.4 Header

```jsx
// components/Header/Header.jsx
export default function Header() {
  const logout = useAuthStore(s => s.logout)
  const { darkMode, toggleDark } = useUIStore()

  return (
    <header className="flex items-center justify-between px-6 py-3 border-b dark:border-gray-700">
      <span className="font-bold text-lg dark:text-white">Book Ninja</span>
      <div className="flex gap-3 items-center">
        <button onClick={toggleDark} title="Toggle dark mode">
          {darkMode ? 'Light' : 'Dark'}
        </button>
        <button onClick={logout} className="text-sm text-red-500 hover:underline">
          Logout
        </button>
      </div>
    </header>
  )
}
```

---

## 7. API Integration

All API calls are centralized in `src/api/`.

### 7.1 API Client

```js
// api/client.js
import { useAuthStore } from '../store/useAuthStore'

const BASE_URL = import.meta.env.VITE_API_BASE_URL

function buildHeaders({ auth, headers, hasBody }) {
  const token = useAuthStore.getState().token
  const nextHeaders = { ...headers }

  if (hasBody && !nextHeaders['Content-Type']) {
    nextHeaders['Content-Type'] = 'application/json'
  }

  if (auth) {
    if (!token) throw new Error('You are not signed in. Please sign in again.')
    nextHeaders.Authorization = `Bearer ${token}`
  }

  return nextHeaders
}

export async function apiRequest(path, options = {}) {
  const { auth = true, headers = {}, ...rest } = options
  const res = await fetch(`${BASE_URL}${path}`, {
    ...rest,
    headers: buildHeaders({ auth, headers, hasBody: Boolean(rest.body) }),
  })

  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || err.error || `HTTP ${res.status}`)
  }

  return res.json()
}

export async function apiRequestRaw(path, options = {}) {
  const { auth = true, headers = {}, ...rest } = options
  const res = await fetch(`${BASE_URL}${path}`, {
    ...rest,
    headers: buildHeaders({ auth, headers, hasBody: Boolean(rest.body) }),
  })

  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || err.error || `HTTP ${res.status}`)
  }

  return res
}
```

### 7.2 `/chat` - Send a Message (SSE)

`/chat` returns `text/event-stream` with `status`, `final`, and `error` events.

```js
// api/chatStream.js
import { apiRequestRaw } from './client'

function parseSseBlock(block) {
  const lines = block.split('\n')
  let event = 'message'
  const dataLines = []

  for (const line of lines) {
    if (line.startsWith('event:')) event = line.slice(6).trim()
    if (line.startsWith('data:')) dataLines.push(line.slice(5).trim())
  }

  if (!dataLines.length) return null

  return {
    event,
    data: JSON.parse(dataLines.join('\n')),
  }
}

export async function sendChatMessageStream({ prompt, thread_id, onStatus, onFinal, onError, signal }) {
  const res = await apiRequestRaw('/chat', {
    method: 'POST',
    auth: true,
    headers: { Accept: 'text/event-stream' },
    body: JSON.stringify({ prompt, thread_id }),
    signal,
  })

  const reader = res.body.getReader()
  const decoder = new TextDecoder('utf-8')
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })

    const blocks = buffer.split('\n\n')
    buffer = blocks.pop() || ''

    for (const block of blocks) {
      const event = parseSseBlock(block)
      if (!event) continue

      if (event.event === 'status') onStatus?.(event.data)
      else if (event.event === 'final') onFinal?.(event.data)
      else if (event.event === 'error') onError?.(event.data)
    }
  }
}
```

```js
// hooks/useChat.js
import { useEffect, useState } from 'react'
import { sendChatMessageStream } from '../api/chatStream'
import { useUIStore } from '../store/useUIStore'
import { useThreadMessages } from './useThreadMessages'

export function useChat() {
  const [messages, setMessages] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const threadId = useUIStore(s => s.activeThreadId)
  const setThreadId = useUIStore(s => s.setActiveThread)
  const { data: threadMessages } = useThreadMessages(threadId)

  useEffect(() => {
    if (!threadId) {
      setMessages([])
      return
    }
    if (threadMessages?.length) setMessages(threadMessages)
  }, [threadId, threadMessages])

  const sendMessage = async (prompt) => {
    setMessages(prev => [...prev, { role: 'user', content: prompt }])
    setIsLoading(true)

    try {
      await sendChatMessageStream({
        prompt,
        thread_id: threadId,
        onStatus: (evt) => {
          // Optional: surface node progress in UI
          // evt shape: { node, thread_id }
        },
        onFinal: (evt) => {
          setMessages(prev => [...prev, { role: 'agent', content: evt.output }])
          if (!threadId && evt.thread_id) setThreadId(evt.thread_id)
        },
        onError: (evt) => {
          setMessages(prev => [...prev, { role: 'error', content: evt.message || 'Request failed' }])
        },
      })
    } catch (err) {
      setMessages(prev => [...prev, { role: 'error', content: err.message }])
      throw err
    } finally {
      setIsLoading(false)
    }
  }

  return { messages, sendMessage, isLoading }
}
```

### 7.3 `/latestThreads` - Load Thread History

Backend response shape is `{ threads: [...] }`. Normalize in the hook so components consume a plain array.

```js
// hooks/useThreads.js
import { useQuery } from '@tanstack/react-query'
import { apiRequest } from '../api/client'

export function useThreads() {
  return useQuery({
    queryKey: ['threads'],
    queryFn: () => apiRequest('/latestThreads', { auth: true }),
    select: (data) => data.threads,
    staleTime: 30_000,
  })
}
```

### 7.4 `/threads/{thread_id}/messages` - Load Selected Thread Messages

This endpoint should be added on the backend to support full thread rehydration when users click a previous thread.

```js
// hooks/useThreadMessages.js
import { useQuery } from '@tanstack/react-query'
import { apiRequest } from '../api/client'

export function useThreadMessages(threadId) {
  return useQuery({
    queryKey: ['threadMessages', threadId],
    enabled: Boolean(threadId),
    queryFn: () => apiRequest(`/threads/${threadId}/messages`, { auth: true }),
    select: (data) => data.messages,
  })
}
```

### 7.5 `/health` - Health Check

`/health` is unauthenticated on backend; call it with `auth: false`.

```js
// hooks/useHealth.js
import { useQuery } from '@tanstack/react-query'
import { apiRequest } from '../api/client'

export function useHealth() {
  return useQuery({
    queryKey: ['health'],
    queryFn: () => apiRequest('/health', { auth: false }),
    refetchInterval: 60_000,
    retry: false,
  })
}
```

---

## 8. State Management

### Zustand UI Store

Initialize `darkMode` from the current DOM class so state and UI are always in sync.

```js
// store/useUIStore.js
import { create } from 'zustand'

const initialDarkMode = document.documentElement.classList.contains('dark')

export const useUIStore = create(set => ({
  sidebarOpen: true,
  activeThreadId: null,
  darkMode: initialDarkMode,
  toggleSidebar: () => set(s => ({ sidebarOpen: !s.sidebarOpen })),
  setActiveThread: id => set({ activeThreadId: id }),
  toggleDark: () =>
    set(s => {
      const next = !s.darkMode
      document.documentElement.classList.toggle('dark', next)
      return { darkMode: next }
    }),
}))
```

---

## 9. Compatibility

### Web
The standard Vite React build targets modern browsers.

### Android
Use **Capacitor** to wrap the React app as a native Android app.

```bash
npm install @capacitor/core @capacitor/cli @capacitor/android
npx cap init
npx cap add android
npm run build && npx cap sync
npx cap open android
```

The chat input should use `inputMode="text"` to trigger the correct mobile keyboard. Test on both small (360px) and large (414px) viewport widths.

---

## 10. Dark Mode

Dark mode is class-based (configured in Tailwind). The initial mode can be set from OS preference in `main.jsx`:

```js
// main.jsx
if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
  document.documentElement.classList.add('dark')
}
```

`useUIStore` must initialize from `document.documentElement.classList` so toggle state is consistent with initial class.

---

## 11. Input Validation (Client-Side)

Client validation is intentionally limited to fast UX checks (empty + max length). Security and prompt-injection filtering remains backend-only.

```js
// utils/validatePrompt.js
export function validatePrompt(input) {
  if (!input || input.trim().length === 0) return 'Message cannot be empty.'
  if (input.length > 3000) return `Message too long (${input.length}/3000 characters).`
  return null
}
```

For backend validation failures (HTTP 400), show `err.detail` inline beneath the input.

---

## 12. Penpot Design Workflow

Penpot is mandatory for UI design in this project.

1. Keep the latest UI source-of-truth in Penpot (single shared project).
2. Name frames using `feature/screen/state` (for example `chat/sidebar/open`).
3. Before implementation, link the exact Penpot frame in the task/PR.
4. For UI PRs, include:
   - Penpot frame link
   - screenshot of implemented screen (desktop + mobile)
   - note of any intentional deviation from design
5. Any UI change without a Penpot reference is considered incomplete.

---

## 13. Environment Variables

```env
# .env.local
VITE_API_BASE_URL=http://localhost:8000
VITE_GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
```

Never prefix secrets with `VITE_` unless they are safe to expose to browsers.

---

## 14. Testing

### Setup

```js
// src/test/setup.js
import '@testing-library/jest-dom'
```

### Running Tests

```bash
npx vitest
npx vitest run
npx vitest run --coverage
```

### Coverage Target
80% across statements, branches, functions, and lines.

### Required Frontend Contract Tests

1. **SSE parsing**
   - Parses `status`, `final`, and `error` events from `/chat`
   - Appends final assistant output from `final.output`
   - Sets active thread from `final.thread_id`

2. **Thread history shape normalization**
   - `useThreads` transforms `{ threads: [...] }` into array data
   - UI works with snake_case thread fields (`thread_id`, `timestamp`, `preview`)

3. **Thread selection rehydration**
   - Clicking a thread triggers `/threads/{thread_id}/messages`
   - Chat window renders persisted messages for selected thread

4. **Auth-aware API client**
   - `/health` calls use `auth: false` and do not attach Authorization header
   - Auth endpoints throw a clear error when token is missing

5. **Dark mode hydration**
   - Store initializes from existing `html.dark` class
   - First toggle changes mode correctly

6. **Validation and error UX**
   - Empty and >3000 input validation errors render inline
   - Backend 400 response detail is shown inline

### Example Tests

```jsx
// components/ChatWindow/ChatWindow.test.jsx
it('enforces max length and inputMode text', () => {
  render(<ChatWindow />)
  const input = screen.getByPlaceholderText(/search for a book/i)
  expect(input).toHaveAttribute('maxLength', '3000')
  expect(input).toHaveAttribute('inputMode', 'text')
})
```

```js
// hooks/useThreads.test.js
it('normalizes latestThreads response to an array', async () => {
  const raw = {
    threads: [{ thread_id: 'u1_abc', preview: 'Dune', timestamp: '2026-05-18T08:00:00Z' }],
  }
  const normalized = raw.threads
  expect(Array.isArray(normalized)).toBe(true)
  expect(normalized[0].thread_id).toBe('u1_abc')
})
```

---

## 15. CI/CD

Handled by GitHub Actions. The frontend pipeline runs on push to `main`/`develop` and on pull requests targeting `main`.

```yaml
# .github/workflows/frontend.yml
name: Frontend CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: npm ci
      - run: npx eslint src/
      - run: npx vitest run --coverage
      - run: npm run build
```

Deployments (Vercel or Netlify) are triggered automatically on merge to `main`.

---

## 16. Deployment

The React app is built as a static bundle and deployed to **Vercel** or **Netlify**.

### Vercel

```bash
npm install -g vercel
vercel --prod
```

Set `VITE_API_BASE_URL` and `VITE_GOOGLE_CLIENT_ID` in project environment settings.

### Netlify

```bash
npm install -g netlify-cli
netlify deploy --prod --dir=dist
```

Configure redirect so React Router handles client routes:

```text
# public/_redirects
/*  /index.html  200
```
