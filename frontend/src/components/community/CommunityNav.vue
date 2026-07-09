<template>
  <nav class="community-subnav">
    <RouterLink
      v-for="link in links"
      :key="link.to"
      :to="link.to"
      class="community-subnav-link"
      :class="{ 'is-active': route.path.startsWith(link.to) }"
    >
      {{ link.label }}
    </RouterLink>
  </nav>
</template>

<script setup>
import { computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const route = useRoute()

const links = computed(() => [
  { label: t('community.nav.forum'), to: '/community/forum' },
  { label: t('community.nav.resources'), to: '/community/resources' },
  { label: t('community.nav.myPosts'), to: '/community/mine' },
  { label: t('community.nav.myFavorites'), to: '/community/favorites' }
])
</script>

<style scoped>
.community-subnav {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 6px;
  margin-bottom: 22px;
  background: rgba(255, 250, 240, 0.7);
  border: 2px solid var(--line);
  border-radius: 999px;
  width: fit-content;
}

.community-subnav-link {
  padding: 9px 20px;
  color: var(--muted);
  font-size: 14px;
  font-weight: 900;
  border-radius: 999px;
  transition: background 220ms var(--ease), color 220ms var(--ease);
}

.community-subnav-link:hover {
  color: var(--ink);
}

.community-subnav-link.is-active {
  color: var(--ink);
  background: var(--acid);
}

@media (max-width: 680px) {
  .community-subnav {
    width: 100%;
  }
}
</style>
