import { create } from 'zustand'

const demoUser = {
  name: 'Book Ninja Reader',
  email: 'reader@bookninja.local',
}

export const useAuthStore = create((set) => ({
  token: null,
  user: null,
  setToken: (token) => set({ token, user: demoUser }),
  clearToken: () => set({ token: null, user: null }),
}))
