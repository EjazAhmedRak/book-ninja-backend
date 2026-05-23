import React from 'react'
import { describe, expect, test } from 'vitest'
import { fireEvent, render, screen } from '@testing-library/react'
import ChatPage from '../pages/ChatPage'

describe('chat page shell', () => {
  test('renders welcome banner and seeded assistant message', () => {
    render(<ChatPage />)

    expect(screen.getByRole('heading', { name: /welcome to book ninja/i })).toBeInTheDocument()
    expect(
      screen.getByText(/i can help you search books, recommend titles, and find ebook, audiobook, or purchase options/i)
    ).toBeInTheDocument()
  })

  test('appends user message when input is non-empty', () => {
    render(<ChatPage />)

    fireEvent.change(screen.getByLabelText(/message input/i), {
      target: { value: 'Find me sci-fi books by Asimov' },
    })
    fireEvent.click(screen.getByRole('button', { name: /send/i }))

    expect(screen.getByText('Find me sci-fi books by Asimov')).toBeInTheDocument()
  })

  test('does not append empty messages', () => {
    render(<ChatPage />)

    fireEvent.change(screen.getByLabelText(/message input/i), {
      target: { value: '   ' },
    })
    fireEvent.click(screen.getByRole('button', { name: /send/i }))

    const userMessages = screen.queryAllByTestId('user-message')
    expect(userMessages).toHaveLength(0)
  })
})
