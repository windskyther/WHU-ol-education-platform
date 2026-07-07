import request from '../utils/request'

export function sendEmailCode(payload) {
  return request.post('/auth/email-code/send/', payload)
}

export function register(payload) {
  return request.post('/auth/register/', payload)
}

export function login(payload) {
  return request.post('/auth/login/', payload)
}

export function refreshToken(payload) {
  return request.post('/auth/refresh/', payload)
}

export function logout() {
  return request.post('/auth/logout/')
}

export function fetchMe() {
  return request.get('/users/me/')
}
