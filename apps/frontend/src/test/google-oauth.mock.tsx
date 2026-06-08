import React, { ReactNode } from 'react'
import { vi } from 'vitest'

export const mockGoogleCredential = 'mock-google-id-token'
export const googleLoginControls = {
  shouldFail: false,
  credential: mockGoogleCredential,
  missingCredential: false,
}

type MockGoogleOAuthProviderProps = {
  children: ReactNode
}

type MockGoogleLoginProps = {
  onSuccess?: (credentialResponse: { credential?: string }) => void
  onError?: () => void
}

vi.mock('@react-oauth/google', () => ({
  GoogleOAuthProvider: ({ children }: MockGoogleOAuthProviderProps) => <>{children}</>,
  GoogleLogin: ({ onSuccess, onError }: MockGoogleLoginProps) => (
    <button
      type="button"
      onClick={() => {
        if (googleLoginControls.shouldFail) {
          onError?.()
          return
        }

        onSuccess?.({ credential: googleLoginControls.missingCredential ? undefined : googleLoginControls.credential })
      }}
    >
      Continue with Google
    </button>
  ),
}))

vi.mock('jwt-decode', () => ({
  jwtDecode: () => ({
    name: 'Ada Lovelace',
    email: 'ada@example.com',
    picture: 'https://example.com/ada.png',
  }),
}))
