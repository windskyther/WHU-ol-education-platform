import axios from 'axios'

const request = axios.create({
  baseURL: '/api',
  timeout: 10000
})

const codeMessageMap = {
  4000: '提交信息有误，请检查后重试',
  4001: '登录状态已失效，请重新登录',
  4003: '当前账号没有操作权限',
  4040: '请求的资源不存在',
  4090: '该操作已存在，请勿重复提交',
  5000: '服务器暂时不可用，请稍后重试'
}

const statusMessageMap = {
  400: '提交信息有误，请检查后重试',
  401: '登录状态已失效，请重新登录',
  403: '当前账号没有操作权限',
  404: '请求的资源不存在',
  409: '该操作已存在，请勿重复提交',
  500: '服务器暂时不可用，请稍后重试'
}

function hasReadableChinese(message) {
  return typeof message === 'string' && /[\u4e00-\u9fa5]/.test(message) && !/[锟�]/.test(message)
}

function pickReadableMessage(value) {
  if (!value) return ''
  if (typeof value === 'string') {
    return hasReadableChinese(value) ? value : ''
  }
  if (Array.isArray(value)) {
    for (const item of value) {
      const message = pickReadableMessage(item)
      if (message) return message
    }
    return ''
  }
  if (typeof value === 'object') {
    for (const item of Object.values(value)) {
      const message = pickReadableMessage(item)
      if (message) return message
    }
  }
  return ''
}

function normalizeErrorMessage(error, fallback = '请求失败，请稍后重试') {
  const businessCode = error?.code || error?.response?.data?.code
  const status = error?.response?.status
  const responseData = error?.response?.data
  const rawMessage = responseData?.message || responseData?.detail || responseData?.error || error?.message

  if (error?.message === 'Network Error') {
    return '无法连接后端服务，请确认服务已启动'
  }
  if (error?.code === 'ECONNABORTED' || /timeout/i.test(error?.message || '')) {
    return '请求超时，请稍后重试'
  }
  if (codeMessageMap[businessCode]) {
    return codeMessageMap[businessCode]
  }
  if (statusMessageMap[status]) {
    return statusMessageMap[status]
  }

  const readableMessage = pickReadableMessage(rawMessage || responseData)
  return readableMessage || fallback
}

function attachErrorContext(error, response) {
  const rawData = response?.data
  error.rawData = rawData
  error.status = response?.status
  error.businessCode = rawData?.code || error.code
  return error
}

function markAuthExpired() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  window.dispatchEvent(new CustomEvent('auth:expired'))
}

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

      const error = new Error('业务请求失败')
      error.code = body.code
      error.response = response
      attachErrorContext(error, response)
      error.userMessage = normalizeErrorMessage(error)
      if (body.code === 4001) {
        markAuthExpired()
      }
      return Promise.reject(error)
    }

    return body
  },
  (error) => {
    const status = error.response?.status
    attachErrorContext(error, error.response)
    error.userMessage = normalizeErrorMessage(error)

    if (status === 401) {
      markAuthExpired()
    }

    return Promise.reject(error)
  }
)

export default request
