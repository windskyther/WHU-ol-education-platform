import { createI18n } from 'vue-i18n'
import zhCN from './locales/zh-CN'
import enUS from './locales/en-US'
import courseZh from './locales/course.zh'
import courseEn from './locales/course.en'
import teacherZh from './locales/teacher.zh'
import teacherEn from './locales/teacher.en'
import studentZh from './locales/student.zh'
import studentEn from './locales/student.en'
import communityZh from './locales/community.zh'
import communityEn from './locales/community.en'
import miscZh from './locales/misc.zh'
import miscEn from './locales/misc.en'

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
    'zh-CN': { ...zhCN, ...courseZh, ...teacherZh, ...studentZh, ...communityZh, ...miscZh },
    'en-US': { ...enUS, ...courseEn, ...teacherEn, ...studentEn, ...communityEn, ...miscEn }
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
