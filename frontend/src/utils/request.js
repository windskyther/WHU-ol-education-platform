import axios from 'axios'
import { ElMessage } from 'element-plus'

const request = axios.create({
  baseURL: '/api',
  timeout: 10000
})

request.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

request.interceptors.response.use(
  (response) => {
    const body = response.data
    if (body && typeof body === 'object' && 'code' in body) {
      if (body.code === 0) {
        return body.data
      }

      const error = new Error(body.message || '请求失败')
      error.code = body.code
      error.response = response
      if (body.code === 4001) {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        window.dispatchEvent(new CustomEvent('auth:expired'))
      }
      return Promise.reject(error)
    }

    return body
  },
  (error) => {
    const status = error.response?.status
    const message = error.response?.data?.message || error.message || '请求失败'

    if (status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      window.dispatchEvent(new CustomEvent('auth:expired'))
      ElMessage.warning('登录状态已失效，请重新登录')
    } else if (status) {
      ElMessage.error(message)
    }

    return Promise.reject(error)
  }
)

export default request
