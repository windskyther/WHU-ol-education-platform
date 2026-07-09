<template>
  <main class="page-shell">
    <AppNav />

    <section class="community-shell">
      <header class="list-heading">
        <div>
          <p class="eyebrow">{{ t('community.hub.eyebrow') }}</p>
          <h1>{{ t('community.hub.title') }}</h1>
        </div>
        <p>{{ t('community.hub.subtitle') }}</p>
      </header>

      <CommunityNav />

      <RouterView />
    </section>
  </main>
</template>

<script setup>
import { RouterView } from 'vue-router'
import { useI18n } from 'vue-i18n'
import AppNav from '../../components/AppNav.vue'
import CommunityNav from '../../components/community/CommunityNav.vue'

const { t } = useI18n()
</script>

<style scoped>
.community-shell {
  max-width: 1080px;
  padding: 48px 24px 96px;
  margin: 0 auto;
}
</style>
