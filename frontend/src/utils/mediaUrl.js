const DEFAULT_MEDIA_BASE_URL = 'http://127.0.0.1:8080'

function mediaBaseUrl() {
  // Prefer an explicit override, then fall back to the dev proxy target (kept in
  // sync with the backend port used for API calls), and only then the hardcoded
  // default. This avoids rewriting valid absolute media URLs to a stale port.
  const base =
    import.meta.env.VITE_MEDIA_BASE_URL ||
    import.meta.env.VITE_DEV_PROXY_TARGET ||
    DEFAULT_MEDIA_BASE_URL
  return base.replace(/\/$/, '')
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
