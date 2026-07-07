import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', {
  state: () => ({
    accessToken: localStorage.getItem('access_token') || '',
    refreshToken: localStorage.getItem('refresh_token') || '',
    userInfo: null
  }),
  getters: {
    isLoggedIn: (state) => Boolean(state.accessToken),
    role: (state) => state.userInfo?.role || ''
  },
  actions: {
    setAuth({ accessToken = '', refreshToken = '', userInfo = null }) {
      this.accessToken = accessToken
      this.refreshToken = refreshToken
      this.userInfo = userInfo

      if (accessToken) {
        localStorage.setItem('access_token', accessToken)
      }
      if (refreshToken) {
        localStorage.setItem('refresh_token', refreshToken)
      }
    },
    clearAuth() {
      this.accessToken = ''
      this.refreshToken = ''
      this.userInfo = null
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    }
  }
})
