<template>
  <button type="button" class="lang-switch" :title="isZh ? 'Switch to English' : '切换为中文'" @click="toggleLocale">
    {{ isZh ? 'EN' : '中' }}
  </button>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { toggleLocale } from '../i18n'

const { locale } = useI18n()
const isZh = computed(() => locale.value === 'zh-CN')
</script>

<style scoped>
.lang-switch {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 34px;
  height: 34px;
  padding: 0 10px;
  color: var(--ink);
  background: transparent;
  border: 1px solid var(--line);
  border-radius: 999px;
  font-size: 13px;
  font-weight: 900;
  cursor: pointer;
  transition: background 0.15s ease, border-color 0.15s ease;
}

.lang-switch:hover {
  background: rgba(25, 25, 23, 0.06);
  border-color: var(--ink);
}
</style>
