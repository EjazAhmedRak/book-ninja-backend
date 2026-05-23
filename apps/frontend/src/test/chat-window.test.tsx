import React from 'react'
import { beforeEach, describe, expect, test, vi } from 'vitest'
import { fireEvent, render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import ChatPage from '../pages/ChatPage'
import { useAuthStore } from '../store/useAuthStore'

function renderChatPage() {
  return render(
    <MemoryRouter future={{ v7_relativeSplatPath: true, v7_startTransition: true }}>
      <ChatPage />
    </MemoryRouter>
  )
}

const CHAT_STORAGE_KEY = 'book-ninja.chat.messages'

describe('chat page shell', () => {
  beforeEach(() => {
    window.localStorage.clear()
    useAuthStore.setState({
      token: 'mock-token',
      user: { name: 'Ada Lovelace', email: 'ada@example.com', picture: null },
    })
  })

  test('renders a user profile button in the chat header', () => {
    renderChatPage()

    expect(screen.getByRole('button', { name: /user profile for ada lovelace/i })).toBeInTheDocument()
    expect(screen.getByText('ada@example.com')).toBeInTheDocument()
  })



  test('renders the Google profile photo when available', () => {
    useAuthStore.setState({
      token: 'mock-token',
      user: { name: 'Ada Lovelace', email: 'ada@example.com', picture: 'https://example.com/ada.png' },
    })

    renderChatPage()

    const profilePhoto = screen.getByTestId('user-profile-photo')
    expect(profilePhoto).toHaveAttribute('src', 'https://example.com/ada.png')
    expect(profilePhoto).toHaveAttribute('referrerpolicy', 'no-referrer')
  })


  test('loads existing chat messages from localStorage', () => {
    window.localStorage.setItem(
      CHAT_STORAGE_KEY,
      JSON.stringify([
        { id: 'assistant-1', role: 'assistant', content: 'Stored assistant reply', timestamp: '2026-05-23T00:00:00.000Z' },
        { id: 'user-1', role: 'user', content: 'Stored user question', timestamp: '2026-05-23T00:01:00.000Z' },
      ])
    )

    renderChatPage()

    expect(screen.getByText(/stored assistant reply/i)).toBeInTheDocument()
    expect(screen.getByText(/stored user question/i)).toBeInTheDocument()
  })

  test('persists new chat messages to localStorage', () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2026-05-23T00:02:00.000Z'))

    renderChatPage()

    fireEvent.change(screen.getByLabelText(/message input/i), {
      target: { value: 'Persist this recommendation request' },
    })
    fireEvent.click(screen.getByRole('button', { name: /send/i }))

    const storedMessages = JSON.parse(window.localStorage.getItem(CHAT_STORAGE_KEY) ?? '[]')
    expect(storedMessages).toEqual(
      expect.arrayContaining([
        expect.objectContaining({ role: 'user', content: 'Persist this recommendation request' }),
      ])
    )

    vi.useRealTimers()
  })

  test('ignores invalid localStorage chat history and falls back to seeded message', () => {
    window.localStorage.setItem(CHAT_STORAGE_KEY, JSON.stringify([{ role: 'user', content: 42 }]))

    renderChatPage()

    expect(
      screen.getByText(/i can help you search books, recommend titles, and find ebook, audiobook, or purchase options/i)
    ).toBeInTheDocument()
  })

  test('renders welcome banner and seeded assistant message', () => {
    renderChatPage()

    expect(screen.getByRole('heading', { name: /welcome to book ninja/i })).toBeInTheDocument()
    expect(
      screen.getByText(/i can help you search books, recommend titles, and find ebook, audiobook, or purchase options/i)
    ).toBeInTheDocument()
  })

  test('appends user message when input is non-empty', () => {
    renderChatPage()

    fireEvent.change(screen.getByLabelText(/message input/i), {
      target: { value: 'Find me sci-fi books by Asimov' },
    })
    fireEvent.click(screen.getByRole('button', { name: /send/i }))

    expect(screen.getByText('Find me sci-fi books by Asimov')).toBeInTheDocument()
  })

  test('does not append empty messages', () => {
    renderChatPage()

    fireEvent.change(screen.getByLabelText(/message input/i), {
      target: { value: '   ' },
    })
    fireEvent.click(screen.getByRole('button', { name: /send/i }))

    const userMessages = screen.queryAllByTestId('user-message')
    expect(userMessages).toHaveLength(0)
  })
})
