<template>
  <aside class="learning-path-panel">
    <div class="path-brand">
      <span class="path-logo">WHU</span>
      <span>Online Education</span>
    </div>

    <div class="path-copy">
      <p class="path-eyebrow">Access layer</p>
      <h1>{{ title }}</h1>
      <p>{{ description }}</p>
    </div>

    <div class="path-index" aria-hidden="true">
      <span>01</span>
      <i></i>
      <span>02</span>
      <i></i>
      <span>03</span>
    </div>

    <div class="path-steps">
      <span>Identity</span>
      <span>Courses</span>
      <span>Progress</span>
    </div>
  </aside>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    required: true
  },
  description: {
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
.path-copy,
.path-index,
.path-steps {
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

.path-copy p:last-child {
  max-width: 560px;
  color: rgba(246, 241, 230, 0.7);
  font-size: 20px;
  font-weight: 800;
  line-height: 1.18;
}

.path-index {
  display: flex;
  align-items: center;
  gap: 16px;
  margin: 54px 0;
  color: var(--hot);
  font-weight: 900;
}

.path-index i {
  width: min(16vw, 160px);
  height: 2px;
  background: currentColor;
  opacity: 0.45;
}

.path-steps {
  display: flex;
  flex-wrap: wrap;
  gap: 18px;
  color: rgba(246, 241, 230, 0.64);
  font-size: 12px;
  font-weight: 900;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}
</style>
