<template>
  <aside class="learning-path-panel">
    <div class="path-brand">
      <span class="path-logo">WHU</span>
      <span>在线教育平台</span>
    </div>
    <div class="path-line" aria-hidden="true">
      <span class="path-node is-active"></span>
      <span class="path-rail"></span>
      <span class="path-node"></span>
      <span class="path-rail"></span>
      <span class="path-node"></span>
    </div>
    <div class="path-copy">
      <p class="path-eyebrow">P1 用户认证</p>
      <h1>{{ title }}</h1>
      <p>{{ description }}</p>
    </div>
    <div class="path-steps">
      <span>注册</span>
      <span>登录</span>
      <span>进入学习</span>
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
