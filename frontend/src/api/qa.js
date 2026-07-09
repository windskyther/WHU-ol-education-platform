import request from '../utils/request'

export function fetchCourseQuestions(courseId, params = {}) {
  return request.get(`/courses/${courseId}/questions/`, { params })
}

export function createCourseQuestion(courseId, payload) {
  return request.post(`/courses/${courseId}/questions/`, payload)
}

export function answerCourseQuestion(questionId, payload) {
  return request.post(`/course-questions/${questionId}/answer/`, payload)
}

export function resolveCourseQuestion(questionId) {
  return request.post(`/course-questions/${questionId}/resolve/`)
}
