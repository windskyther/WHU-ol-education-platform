/**
 * Best-effort normalization for user-entered URLs.
 * Users often paste a domain without a scheme (e.g. "www.example.com"),
 * which the backend's strict URLField validator rejects. Auto-prepend
 * "https://" when no scheme is present so the common case just works.
 */
export function normalizeUrl(value) {
  const trimmed = (value || '').trim()
  if (!trimmed) return ''
  if (/^https?:\/\//i.test(trimmed)) return trimmed
  return `https://${trimmed}`
}
