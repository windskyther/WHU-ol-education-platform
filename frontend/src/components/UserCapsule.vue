<template>
  <button
    class="user-capsule"
    :class="{ 'user-capsule--preview': preview, 'user-capsule--interactive': interactive }"
    :type="interactive ? 'button' : 'button'"
    :disabled="!interactive"
  >
    <span class="user-capsule__avatar">
      <img v-if="avatarUrl" :src="avatarUrl" :alt="displayName" />
      <span v-else>{{ avatarFallback }}</span>
    </span>
    <span class="user-capsule__mood">{{ moodDisplay.emoji }}</span>
    <span class="user-capsule__name">{{ displayName }}</span>
    <span v-if="showCaret" class="user-capsule__caret" aria-hidden="true">▾</span>
  </button>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { getMoodDisplay } from '../constants/userMood'
import { normalizeMediaUrl } from '../utils/mediaUrl'

const { t } = useI18n()

const props = defineProps({
  userInfo: {
    type: Object,
    default: null
  },
  preview: {
    type: Boolean,
    default: false
  },
  interactive: {
    type: Boolean,
    default: true
  },
  showCaret: {
    type: Boolean,
    default: false
  }
})

const displayName = computed(() => props.userInfo?.username || props.userInfo?.email || t('shared.loggedInUser'))
const avatarUrl = computed(() => normalizeMediaUrl(props.userInfo?.avatar_url || ''))
const avatarFallback = computed(() => (displayName.value || '用').slice(0, 1).toUpperCase())
const moodDisplay = computed(() => getMoodDisplay(props.userInfo?.mood || 'happy'))
</script>
