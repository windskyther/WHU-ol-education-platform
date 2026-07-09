import { createI18n } from 'vue-i18n'
import zhCN from './locales/zh-CN'
import enUS from './locales/en-US'

export const LOCALE_STORAGE_KEY = 'app_locale'
export const SUPPORTED_LOCALES = ['zh-CN', 'en-US']

function readStoredLocale() {
  const stored = localStorage.getItem(LOCALE_STORAGE_KEY)
  return SUPPORTED_LOCALES.includes(stored) ? stored : 'zh-CN'
}

const i18n = createI18n({
  legacy: false,
  globalInjection: true,
  locale: readStoredLocale(),
  fallbackLocale: 'zh-CN',
  messages: {
    'zh-CN': zhCN,
    'en-US': enUS
  }
})

export function getLocale() {
  return i18n.global.locale.value
}

export function setLocale(locale) {
  if (!SUPPORTED_LOCALES.includes(locale)) return
  i18n.global.locale.value = locale
  localStorage.setItem(LOCALE_STORAGE_KEY, locale)
  document.documentElement.setAttribute('lang', locale)
}

export function toggleLocale() {
  setLocale(getLocale() === 'zh-CN' ? 'en-US' : 'zh-CN')
}

export default i18n
