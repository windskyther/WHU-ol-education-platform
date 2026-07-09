import request from '../utils/request'

export function fetchCategories(target) {
  return request.get('/community/categories/', { params: { target } })
}

export function fetchPosts(params = {}) {
  return request.get('/community/posts/', { params })
}

export function fetchPostDetail(postId) {
  return request.get(`/community/posts/${postId}/`)
}

export function createPost(payload) {
  return request.post('/community/posts/', payload)
}

export function updatePost(postId, payload) {
  return request.patch(`/community/posts/${postId}/`, payload)
}

export function deletePost(postId) {
  return request.delete(`/community/posts/${postId}/`)
}

export function uploadPostAttachments(postId, files) {
  const formData = new FormData()
  files.forEach((file) => formData.append('file', file))
  return request.post(`/community/posts/${postId}/attachments/`, formData)
}

export function fetchResources(params = {}) {
  return request.get('/community/resources/', { params })
}

export function fetchResourceDetail(resourceId) {
  return request.get(`/community/resources/${resourceId}/`)
}

export function createResource(payload) {
  const formData = new FormData()
  Object.entries(payload).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      formData.append(key, value)
    }
  })
  return request.post('/community/resources/', formData)
}

export function updateResource(resourceId, payload) {
  return request.patch(`/community/resources/${resourceId}/`, payload)
}

export function deleteResource(resourceId) {
  return request.delete(`/community/resources/${resourceId}/`)
}

export function fetchComments(targetType, targetId, params = {}) {
  return request.get(`/community/${targetType}/${targetId}/comments/`, { params })
}

export function createComment(targetType, targetId, content) {
  return request.post(`/community/${targetType}/${targetId}/comments/`, { content })
}

export function toggleLike(targetType, targetId) {
  return request.post(`/community/${targetType}/${targetId}/like/`)
}

export function toggleFavorite(targetType, targetId) {
  return request.post(`/community/${targetType}/${targetId}/favorite/`)
}

export function fetchMyPosts(params = {}) {
  return request.get('/community/my/posts/', { params })
}

export function fetchMyResources(params = {}) {
  return request.get('/community/my/resources/', { params })
}

export function fetchMyFavorites(type, params = {}) {
  return request.get('/community/my/favorites/', { params: { ...params, type } })
}
