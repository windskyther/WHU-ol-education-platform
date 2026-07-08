<template>
  <article class="course-card" @click="$router.push(`/courses/${course.id}`)">
    <div class="cover momentum-ribbon">
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
        <span>{{ course.teacher?.username || course.teacher_name || '教师未命名' }}</span>
        <span>{{ course.chapter_count || course.chapters_count || 0 }} 章</span>
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
  grid-template-columns: 150px minmax(0, 1fr);
  min-height: 168px;
  overflow: hidden;
  cursor: pointer;
  background: var(--white);
  border: 1px solid rgba(99, 102, 241, 0.12);
  border-radius: var(--radius-lg);
  box-shadow: 0 1px 0 rgba(23, 22, 41, 0.03);
  transition:
    border-color 0.2s ease,
    transform 0.2s ease,
    box-shadow 0.2s ease;
}

.course-card:hover {
  border-color: rgba(99, 102, 241, 0.32);
  box-shadow: var(--shadow-hover);
  transform: translateY(-3px);
}

.cover {
  display: grid;
  place-items: center;
  min-height: 168px;
  overflow: hidden;
  color: var(--brand-indigo);
  background:
    linear-gradient(135deg, rgba(99, 102, 241, 0.14), rgba(245, 158, 11, 0.18)),
    #f7f5ff;
  font-size: 46px;
  font-weight: 900;
}

.cover img {
  position: relative;
  z-index: 1;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover span {
  position: relative;
  z-index: 1;
}

.content {
  display: grid;
  gap: 10px;
  align-content: start;
  padding: 20px 20px 18px;
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
  font-weight: 700;
}

h3 {
  margin: 0;
  color: var(--ink-900);
  font-size: 21px;
  line-height: 1.3;
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
