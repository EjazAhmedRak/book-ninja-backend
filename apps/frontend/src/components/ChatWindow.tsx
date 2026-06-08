import React, { useEffect, useMemo, useState } from 'react'

const MAX_PROMPT_LENGTH = 3000
const CHAT_STORAGE_KEY = 'book-ninja.chat.messages'

type MessageRole = 'assistant' | 'user'

type ChatMessage = {
  id: string
  role: MessageRole
  content: string
  timestamp: string
}

function createMessage(role: MessageRole, content: string): ChatMessage {
  return {
    id: globalThis.crypto?.randomUUID?.() ?? `${role}-${Date.now()}-${Math.random()}`,
    role,
    content,
    timestamp: new Date().toISOString(),
  }
}

function createSeedMessages(): ChatMessage[] {
  return [
    createMessage(
      'assistant',
      'I can help you search books, recommend titles, and find ebook, audiobook, or purchase options.'
    ),
  ]
}

function isChatMessage(value: unknown): value is ChatMessage {
  if (!value || typeof value !== 'object') {
    return false
  }

  const message = value as Partial<ChatMessage>
  return (
    typeof message.id === 'string' &&
    (message.role === 'assistant' || message.role === 'user') &&
    typeof message.content === 'string' &&
    typeof message.timestamp === 'string'
  )
}

function loadStoredMessages(): ChatMessage[] | null {
  try {
    const rawMessages = window.localStorage.getItem(CHAT_STORAGE_KEY)
    if (!rawMessages) {
      return null
    }

    const parsedMessages: unknown = JSON.parse(rawMessages)
    if (!Array.isArray(parsedMessages) || !parsedMessages.every(isChatMessage)) {
      return null
    }

    return parsedMessages
  } catch {
    return null
  }
}

function persistMessages(messages: ChatMessage[]) {
  try {
    window.localStorage.setItem(CHAT_STORAGE_KEY, JSON.stringify(messages))
  } catch {
    // Chat history persistence is best-effort; the local UI should continue to work.
  }
}

export default function ChatWindow() {
  const initialMessages = useMemo<ChatMessage[]>(() => loadStoredMessages() ?? createSeedMessages(), [])

  const [messages, setMessages] = useState<ChatMessage[]>(initialMessages)
  const [input, setInput] = useState('')

  useEffect(() => {
    persistMessages(messages)
  }, [messages])

  const handleSend = () => {
    const trimmed = input.trim()
    if (!trimmed) {
      return
    }

    setMessages((currentMessages) => [...currentMessages, createMessage('user', trimmed)])
    setInput('')
  }

  return (
    <section
      aria-label="Chat window"
      style={{
        background: '#fffdf7',
        border: '1px solid #e2e8f0',
        borderRadius: '18px',
        boxShadow: '0 18px 60px rgba(15, 23, 42, 0.08)',
        padding: '1rem',
      }}
    >
      <div style={{ display: 'grid', gap: '0.75rem', marginBottom: '1rem', minHeight: '220px' }}>
        {messages.map((message) => (
          <article
            key={message.id}
            data-testid={message.role === 'user' ? 'user-message' : 'assistant-message'}
            style={{
              alignSelf: message.role === 'user' ? 'end' : 'start',
              background: message.role === 'user' ? '#0f172a' : '#eef6ff',
              borderRadius: '16px',
              color: message.role === 'user' ? '#ffffff' : '#0f172a',
              maxWidth: 'min(72ch, 100%)',
              padding: '0.85rem 1rem',
            }}
          >
            <strong>{message.role === 'assistant' ? 'Assistant' : 'You'}:</strong> {message.content}
          </article>
        ))}
      </div>

      <label htmlFor="chat-input" style={{ color: '#334155', display: 'block', fontWeight: 700, marginBottom: '0.5rem' }}>
        Message input
      </label>
      <div style={{ display: 'flex', gap: '0.5rem' }}>
        <input
          id="chat-input"
          aria-label="Message input"
          value={input}
          onChange={(event) => setInput(event.target.value)}
          maxLength={MAX_PROMPT_LENGTH}
          placeholder="Ask about books, genres, or formats"
          style={{
            border: '1px solid #cbd5e1',
            borderRadius: '999px',
            flex: 1,
            font: 'inherit',
            padding: '0.8rem 1rem',
          }}
        />
        <button
          type="button"
          onClick={handleSend}
          style={{
            background: '#16a34a',
            border: 0,
            borderRadius: '999px',
            color: '#ffffff',
            cursor: 'pointer',
            fontWeight: 800,
            padding: '0.8rem 1.2rem',
          }}
        >
          Send
        </button>
      </div>
    </section>
  )
}
