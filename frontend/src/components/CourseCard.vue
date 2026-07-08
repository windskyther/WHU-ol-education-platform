<template>
  <article class="course-card" @click="$router.push(`/courses/${course.id}`)">
    <div class="cover">
      <img v-if="course.cover_url" :src="course.cover_url" :alt="course.title" />
      <span v-else>{{ coverInitial }}</span>
    </div>
    <div class="content">
      <div class="meta-row">
        <el-tag size="small" effect="light">{{ levelText }}</el-tag>
        <span>{{ course.category || '未分类' }}</span>
      </div>
      <h3>{{ course.title }}</h3>
      <p>{{ course.description || '暂无课程简介' }}</p>
      <div class="footer">
        <span>{{ course.teacher?.username || '教师未命名' }}</span>
        <span>{{ course.chapter_count || 0 }} 章</span>
      </div>
    </div>
  </article>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  course: {
    type: Object,
    required: true
  }
})

const levelMap = {
  beginner: '初级',
  intermediate: '中级',
  advanced: '高级'
}

const levelText = computed(() => levelMap[props.course.level] || '初级')
const coverInitial = computed(() => (props.course.title || '课').slice(0, 1))
</script>

<style scoped>
.course-card {
  display: grid;
  grid-template-columns: 148px 1fr;
  min-height: 156px;
  overflow: hidden;
  cursor: pointer;
  background: var(--white);
  border: 1px solid var(--border-soft);
  border-radius: 8px;
  transition:
    border-color 0.2s ease,
    transform 0.2s ease,
    box-shadow 0.2s ease;
}

.course-card:hover {
  border-color: var(--border-green);
  box-shadow: var(--shadow-soft);
  transform: translateY(-2px);
}

.cover {
  display: grid;
  place-items: center;
  min-height: 156px;
  color: var(--green-700);
  background:
    linear-gradient(135deg, rgba(92, 169, 130, 0.24), rgba(232, 246, 238, 0.9)),
    var(--green-100);
  font-size: 42px;
  font-weight: 800;
}

.cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.content {
  display: grid;
  gap: 12px;
  padding: 18px;
}

.meta-row,
.footer {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
  justify-content: space-between;
  color: var(--slate-500);
  font-size: 13px;
}

h3 {
  margin: 0;
  font-size: 20px;
}

p {
  display: -webkit-box;
  min-height: 44px;
  margin: 0;
  overflow: hidden;
  color: var(--slate-600);
  line-height: 1.6;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

@media (max-width: 680px) {
  .course-card {
    grid-template-columns: 1fr;
  }
}
</style>
