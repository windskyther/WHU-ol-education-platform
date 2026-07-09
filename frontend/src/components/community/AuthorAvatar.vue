<template>
  <button type="button" class="author-avatar-btn" :title="`查看 ${author?.username || '用户'} 的主页`" @click="goToProfile">
    <el-avatar :size="36" :src="author?.avatar_url || undefined" class="author-avatar">
      {{ initials }}
    </el-avatar>
  </button>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElAvatar } from 'element-plus'

const props = defineProps({
  author: {
    type: Object,
    default: null
  }
})

const router = useRouter()

const initials = computed(() => {
  const name = props.author?.username || ''
  return name ? name.trim().charAt(0).toUpperCase() : '?'
})

function goToProfile() {
  if (!props.author?.id) return
  router.push(`/community/author/${props.author.id}`)
}
</script>

<style scoped>
.author-avatar-btn {
  flex-shrink: 0;
  padding: 0;
  border: none;
  background: transparent;
  cursor: pointer;
  border-radius: 50%;
  line-height: 0;
  transition: transform 0.15s ease;
}

.author-avatar-btn:hover {
  transform: scale(1.06);
}

.author-avatar {
  background: var(--acid);
  color: var(--ink);
  font-weight: 900;
  border: 2px solid var(--line);
}
</style>
