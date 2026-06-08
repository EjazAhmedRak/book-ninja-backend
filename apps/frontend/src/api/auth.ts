import { apiRequest } from './client'

export type BackendAuthUser = {
  sub: string
  email: string
}

export function verifyAuthToken(token: string) {
  return apiRequest<BackendAuthUser>('/auth/me', {
    method: 'GET',
    token,
  })
}
