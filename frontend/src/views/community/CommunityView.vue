<template>
  <main class="page-shell">
    <AppNav />

    <section class="community-shell">
      <header class="list-heading">
        <div>
          <p class="eyebrow">社区中心</p>
          <h1>社区中心</h1>
        </div>
        <p>在这里发帖交流、分享学习资料，管理自己的发布和收藏。</p>
      </header>

      <CommunityNav />

      <RouterView />
    </section>
  </main>
</template>

<script setup>
import { RouterView } from 'vue-router'
import AppNav from '../../components/AppNav.vue'
import CommunityNav from '../../components/community/CommunityNav.vue'
</script>

<style scoped>
.community-shell {
  max-width: 1080px;
  padding: 48px 24px 96px;
  margin: 0 auto;
}
</style>
