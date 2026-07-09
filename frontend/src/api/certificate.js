import request from '../utils/request'

export function fetchMyCertificates(params = {}) {
  return request.get('/certificates/mine/', { params })
}

export function fetchCertificateDetail(certNo) {
  return request.get(`/certificates/${certNo}/`)
}
