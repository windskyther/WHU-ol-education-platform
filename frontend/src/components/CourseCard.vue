<template>
  <article class="course-card" @click="$router.push(`/courses/${course.id}`)">
    <div class="course-poster">
      <img v-if="course.cover_url" :src="course.cover_url" :alt="course.title" />
      <span v-else>{{ coverInitial }}</span>
    </div>
    <div class="course-copy">
      <div class="meta-row">
        <strong>{{ levelText }}</strong>
        <span>{{ course.category || '未分类' }}</span>
      </div>
      <h3>{{ course.title }}</h3>
      <p>{{ course.description || '暂无课程简介' }}</p>
      <div class="footer">
        <span>{{ course.teacher?.username || course.teacher_name || '教师未命名' }}</span>
        <span>{{ course.chapter_count || course.chapters_count || 0 }} 章</span>
      </div>
    </div>
    <div class="course-arrow" aria-hidden="true">
      <span></span>
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
  beginner: 'Beginner',
  intermediate: 'Intermediate',
  advanced: 'Advanced'
}

const levelText = computed(() => levelMap[props.course.level] || 'Beginner')
const coverInitial = computed(() => (props.course.title || '课').slice(0, 1).toUpperCase())
</script>

<style scoped>
.course-card {
  position: relative;
  display: grid;
  grid-template-columns: 180px minmax(0, 1fr) 70px;
  min-height: 220px;
  overflow: hidden;
  cursor: pointer;
  background: rgba(255, 250, 240, 0.88);
  border: 2px solid var(--line);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-hard);
  transition: transform 360ms var(--ease), border-color 360ms var(--ease), background 360ms var(--ease);
}

.course-card:hover {
  background: var(--ink);
  border-color: var(--ink);
  transform: translateY(-6px);
}

.course-poster {
  display: grid;
  place-items: center;
  min-height: 220px;
  overflow: hidden;
  color: var(--ink);
  background:
    linear-gradient(135deg, rgba(243, 167, 72, 0.84), rgba(255, 79, 216, 0.44)),
    var(--hot);
  font-size: 96px;
  font-weight: 900;
  line-height: 0.8;
  letter-spacing: -0.1em;
}

.course-poster img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.course-copy {
  display: grid;
  gap: 14px;
  align-content: center;
  padding: 28px;
}

.meta-row,
.footer {
  display: flex;
  flex-wrap: wrap;
  gap: 10px 18px;
  align-items: center;
  color: var(--muted);
  font-size: 12px;
  font-weight: 900;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

h3 {
  margin: 0;
  color: var(--ink);
  font-size: clamp(36px, 5vw, 72px);
  font-weight: 900;
  line-height: 0.82;
  letter-spacing: -0.075em;
}

p {
  display: -webkit-box;
  max-width: 560px;
  margin: 0;
  overflow: hidden;
  color: var(--muted);
  font-size: 17px;
  font-weight: 800;
  line-height: 1.2;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.course-arrow {
  display: grid;
  place-items: center;
  color: var(--hot);
}

.course-arrow span {
  width: 46px;
  height: 46px;
  border: 3px solid currentColor;
  border-radius: 50%;
}

.course-arrow span::after {
  display: block;
  width: 80px;
  height: 3px;
  margin: 19px 0 0 -24px;
  content: "";
  background: currentColor;
}

.course-card:hover h3,
.course-card:hover p,
.course-card:hover .meta-row,
.course-card:hover .footer {
  color: var(--paper);
}

@media (max-width: 760px) {
  .course-card {
    grid-template-columns: 1fr;
  }

  .course-arrow {
    display: none;
  }
}
</style>
