<template>
  <aside class="learning-path-panel">
    <div class="path-brand">
      <span class="path-logo">WHU</span>
      <span>{{ t('nav.brandSuffix') }}</span>
    </div>

    <div class="path-copy">
      <h1>{{ title }}</h1>
    </div>
  </aside>
</template>

<script setup>
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

defineProps({
  title: {
    type: String,
    required: true
  }
})
</script>

<style scoped>
.learning-path-panel {
  position: relative;
  display: grid;
  align-content: space-between;
  min-height: 100vh;
  padding: 48px;
  overflow: hidden;
  color: var(--paper);
  background: var(--ink);
}

.learning-path-panel::before {
  position: absolute;
  inset: -22%;
  content: "";
  background:
    linear-gradient(112deg, transparent 0 16%, rgba(243, 167, 72, 0.78) 16% 22%, transparent 22% 42%, rgba(255, 79, 216, 0.65) 42% 48%, transparent 48%),
    radial-gradient(circle at 78% 24%, rgba(66, 100, 251, 0.72), transparent 24%);
  transform: rotate(-9deg);
}

.path-brand,
.path-copy {
  position: relative;
  z-index: 1;
}

.path-copy h1 {
  max-width: 620px;
  margin: 0;
  font-size: clamp(58px, 8vw, 126px);
  font-weight: 900;
  line-height: 0.82;
  letter-spacing: -0.08em;
}
</style>
