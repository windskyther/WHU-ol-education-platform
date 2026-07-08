const DEFAULT_MEDIA_BASE_URL = 'http://127.0.0.1:8080'

function mediaBaseUrl() {
  return (import.meta.env.VITE_MEDIA_BASE_URL || DEFAULT_MEDIA_BASE_URL).replace(/\/$/, '')
}

export function normalizeMediaUrl(url) {
  if (!url || typeof url !== 'string') return ''
  if (url.startsWith('blob:') || url.startsWith('data:')) return url

  if (url.startsWith('/media/')) {
    return `${mediaBaseUrl()}${url}`
  }

  try {
    const parsed = new URL(url)
    if (parsed.pathname.startsWith('/media/')) {
      return `${mediaBaseUrl()}${parsed.pathname}${parsed.search}${parsed.hash}`
    }
  } catch (error) {
    return url
  }

  return url
}
