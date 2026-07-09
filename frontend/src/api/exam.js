import request from '../utils/request'

export function fetchCourseExams(courseId, params = {}) {
  return request.get(`/courses/${courseId}/exams/`, { params })
}

export function createCourseExam(courseId, payload) {
  return request.post(`/courses/${courseId}/exams/`, payload)
}

export function fetchExamDetail(examId) {
  return request.get(`/exams/${examId}/`)
}

export function fetchExamQuestions(examId) {
  return request.get(`/exams/${examId}/questions/`)
}

export function createExamQuestion(examId, payload) {
  return request.post(`/exams/${examId}/questions/`, payload)
}

export function updateExamQuestion(questionId, payload) {
  return request.put(`/questions/${questionId}/`, payload)
}

export function deleteExamQuestion(questionId) {
  return request.delete(`/questions/${questionId}/`)
}

export function submitExam(examId, answers) {
  return request.post(`/exams/${examId}/submit/`, { answers })
}

export function fetchMyScores(params = {}) {
  return request.get('/my/scores/', { params })
}

export function fetchExamSubmissions(examId, params = {}) {
  return request.get(`/exams/${examId}/submissions/`, { params })
}
