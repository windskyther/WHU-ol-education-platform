import request from '../utils/request'

export function fetchCourses(params = {}) {
  return request.get('/courses/', { params })
}

export function fetchCourseDetail(courseId) {
  return request.get(`/courses/${courseId}/`)
}

export function createCourse(payload) {
  return request.post('/courses/', payload)
}

export function updateCourse(courseId, payload) {
  return request.patch(`/courses/${courseId}/`, payload)
}

export function deleteCourse(courseId) {
  return request.delete(`/courses/${courseId}/`)
}

export function publishCourse(courseId, isPublished) {
  return request.post(`/courses/${courseId}/publish/`, { is_published: isPublished })
}

export function fetchChapters(courseId) {
  return request.get(`/courses/${courseId}/chapters/`)
}

export function createChapter(courseId, payload) {
  return request.post(`/courses/${courseId}/chapters/`, payload)
}

export function updateChapter(chapterId, payload) {
  return request.patch(`/chapters/${chapterId}/`, payload)
}

export function deleteChapter(chapterId) {
  return request.delete(`/chapters/${chapterId}/`)
}

export function uploadChapterVideo(chapterId, file) {
  const formData = new FormData()
  formData.append('file', file)
  return request.post(`/chapters/${chapterId}/upload-video/`, formData)
}

export function uploadChapterMaterial(chapterId, file) {
  const formData = new FormData()
  formData.append('file', file)
  return request.post(`/chapters/${chapterId}/upload-material/`, formData)
}
