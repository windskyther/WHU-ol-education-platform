import { defineStore } from 'pinia'
import { changePassword, fetchMe, login, logout, register, updateMe } from '../api/auth'
import { normalizeMediaUrl } from '../utils/mediaUrl'

function normalizeAuthPayload(data) {
  return {
    accessToken: data?.access || data?.access_token || data?.token || '',
    refreshToken: data?.refresh || data?.refresh_token || '',
    userInfo: data?.user || data?.userInfo || data?.profile || null
  }
}

export const useUserStore = defineStore('user', {
  state: () => ({
    accessToken: localStorage.getItem('access_token') || '',
    refreshToken: localStorage.getItem('refresh_token') || '',
    userInfo: null
  }),
  getters: {
    isLoggedIn: (state) => Boolean(state.accessToken),
    role: (state) => state.userInfo?.role || '',
    avatarUrl: (state) => normalizeMediaUrl(state.userInfo?.avatar_url || ''),
    mood: (state) => state.userInfo?.mood || 'happy',
    displayName: (state) => state.userInfo?.username || state.userInfo?.email || '已登录用户'
  },
  actions: {
    setAuth({ accessToken = '', refreshToken = '', userInfo = null }) {
      this.accessToken = accessToken
      this.refreshToken = refreshToken
      this.userInfo = userInfo || this.userInfo

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
    },
    redirectPathByRole(role = this.role) {
      const roleMap = {
        student: '/student/dashboard',
        teacher: '/teacher/dashboard',
        admin: '/admin/dashboard'
      }
      return roleMap[role] || '/'
    },
    async loginUser(payload) {
      const data = await login(payload)
      const auth = normalizeAuthPayload(data)
      this.setAuth(auth)

      if (!this.userInfo && this.accessToken) {
        await this.fetchCurrentUser()
      }

      return this.redirectPathByRole()
    },
    async registerUser(payload) {
      return register(payload)
    },
    async fetchCurrentUser() {
      if (!this.accessToken) return null
      const data = await fetchMe()
      this.userInfo = data?.user || data?.userInfo || data
      return this.userInfo
    },
    async updateProfile(payload) {
      const data = await updateMe(payload)
      this.userInfo = data?.user || data?.userInfo || data
      return this.userInfo
    },
    async changeUserPassword(payload) {
      return changePassword(payload)
    },
    async logoutUser() {
      try {
        if (this.accessToken) {
          await logout()
        }
      } finally {
        this.clearAuth()
      }
    }
  }
})
