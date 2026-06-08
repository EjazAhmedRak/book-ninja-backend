import React from 'react'
import { AuthUser, useAuthStore } from '../store/useAuthStore'

function getInitials(name: string): string {
  return name
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase())
    .join('')
}

const fallbackUser: AuthUser = {
  name: 'Book Ninja Reader',
  email: 'reader@bookninja.local',
  picture: null,
}

export default function UserProfileButton() {
  const user = useAuthStore((state) => state.user) ?? fallbackUser
  const initials = getInitials(user.name) || 'BN'

  return (
    <button
      type="button"
      aria-label={`User profile for ${user.name}`}
      style={{
        alignItems: 'center',
        background: '#ffffff',
        border: '1px solid #dbeafe',
        borderRadius: '999px',
        boxShadow: '0 12px 28px rgba(15, 23, 42, 0.08)',
        color: '#0f172a',
        cursor: 'pointer',
        display: 'inline-flex',
        gap: '0.65rem',
        padding: '0.45rem 0.85rem 0.45rem 0.45rem',
      }}
    >
      {user.picture ? (
        <img
          src={user.picture}
          alt=""
          aria-hidden="true"
          data-testid="user-profile-photo"
          referrerPolicy="no-referrer"
          style={{ borderRadius: '999px', height: 36, objectFit: 'cover', width: 36 }}
        />
      ) : (
        <span
          aria-hidden="true"
          style={{
            alignItems: 'center',
            background: 'linear-gradient(135deg, #ff8500, #19a7de)',
            borderRadius: '999px',
            color: '#ffffff',
            display: 'inline-flex',
            fontSize: '0.82rem',
            fontWeight: 900,
            height: 36,
            justifyContent: 'center',
            letterSpacing: '0.04em',
            width: 36,
          }}
        >
          {initials}
        </span>
      )}
      <span style={{ display: 'grid', lineHeight: 1.1, textAlign: 'left' }}>
        <span style={{ fontSize: '0.9rem', fontWeight: 800 }}>{user.name}</span>
        <span style={{ color: '#64748b', fontSize: '0.72rem' }}>{user.email}</span>
      </span>
    </button>
  )
}
