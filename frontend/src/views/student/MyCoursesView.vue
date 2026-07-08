<template>
  <main class="page-shell">
    <nav class="app-nav">
      <RouterLink class="brand-link" to="/">
        <span class="brand-mark">WHU</span>
        <span>在线教育平台</span>
      </RouterLink>
      <div class="nav-actions">
        <RouterLink to="/student/dashboard">学生首页</RouterLink>
        <RouterLink to="/courses">发现课程</RouterLink>
      </div>
    </nav>

    <section class="my-shell">
      <div class="my-heading momentum-ribbon">
        <div>
          <p class="eyebrow">My courses</p>
          <h1>你的课程进度板</h1>
          <p>回到已加入课程，继续上次的学习进度。每门课程都会显示当前完成度。</p>
        </div>
        <el-button type="primary" size="large" @click="$router.push('/courses')">发现新课程</el-button>
      </div>

      <section class="surface filter-panel">
        <div class="toolbar">
          <el-select v-model="state" clearable placeholder="学习状态" @change="loadCourses(1)">
            <el-option label="学习中" value="learning" />
            <el-option label="已完成" value="completed" />
          </el-select>
          <el-button type="primary" :loading="loading" @click="loadCourses(1)">刷新</el-button>
        </div>
      </section>

      <div v-loading="loading" class="my-grid">
        <article v-for="item in courses" :key="item.id" class="my-card">
          <div class="course-cover momentum-ribbon">
            <img v-if="courseOf(item).cover_url" :src="courseOf(item).cover_url" :alt="courseOf(item).title" />
            <span v-else>{{ (courseOf(item).title || '课').slice(0, 1) }}</span>
          </div>
          <div class="my-content">
            <div class="meta-row">
              <el-tag effect="light">{{ levelText(courseOf(item).level) }}</el-tag>
              <span>{{ courseOf(item).category || '未分类' }}</span>
            </div>
            <h2>{{ courseOf(item).title }}</h2>
            <p>{{ courseOf(item).description || '暂无课程简介' }}</p>
            <el-progress :percentage="progressOf(item)" :stroke-width="10" />
            <div class="card-footer">
              <span>{{ progressOf(item) }}% 已完成</span>
              <el-button type="primary" @click="$router.push(`/student/learn/${courseOf(item).id}`)">继续学习</el-button>
            </div>
          </div>
        </article>
      </div>

      <div v-if="!loading && courses.length === 0" class="empty-state">还没有加入课程。去课程列表找到第一门想完成的课。</div>

      <PaginationBar :total="total" :page="page" :page-size="pageSize" @change="loadCourses" />
    </section>
  </main>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { ElMessage } from 'element-plus'
import PaginationBar from '../../components/PaginationBar.vue'
import { fetchMyCourses } from '../../api/course'
import { getCommonErrorMessage } from '../../utils/errorMessage'

const loading = ref(false)
const courses = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const state = ref('')

const levelMap = {
  beginner: '初级',
  intermediate: '中级',
  advanced: '高级'
}

function levelText(level) {
  return levelMap[level] || '初级'
}

function courseOf(item) {
  return item.course || item.course_detail || item
}

function progressOf(item) {
  const value = item.progress ?? item.course_progress ?? courseOf(item).progress ?? 0
  return Math.max(0, Math.min(100, Math.round(Number(value) || 0)))
}

async function loadCourses(nextPage = page.value) {
  loading.value = true
  try {
    const data = await fetchMyCourses({
      page: nextPage,
      page_size: pageSize.value,
      state: state.value || undefined
    })
    courses.value = data?.results || []
    total.value = data?.count || courses.value.length
    page.value = data?.page || nextPage
    pageSize.value = data?.page_size || pageSize.value
  } catch (error) {
    ElMessage.error(getCommonErrorMessage(error, '我的课程加载失败'))
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadCourses(1)
})
</script>

<style scoped>
.my-shell {
  max-width: 1180px;
  margin: 54px auto 0;
}

.my-heading {
  position: relative;
  display: flex;
  gap: 24px;
  align-items: end;
  justify-content: space-between;
  padding: 30px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid rgba(99, 102, 241, 0.12);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-soft);
}

.my-heading > * {
  position: relative;
  z-index: 1;
}

.my-heading h1 {
  margin: 0;
  font-size: clamp(36px, 5vw, 54px);
}

.my-heading p:last-child {
  max-width: 660px;
  color: var(--slate-600);
  line-height: 1.75;
}

.filter-panel {
  margin-top: 18px;
  padding: 16px;
}

.my-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
  min-height: 180px;
  margin-top: 18px;
}

.my-card {
  display: grid;
  grid-template-columns: 150px minmax(0, 1fr);
  overflow: hidden;
  background: var(--white);
  border: 1px solid rgba(99, 102, 241, 0.12);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
}

.course-cover {
  display: grid;
  place-items: center;
  min-height: 220px;
  overflow: hidden;
  color: var(--brand-indigo);
  background: var(--gradient-warm);
  font-size: 48px;
  font-weight: 900;
}

.course-cover img {
  position: relative;
  z-index: 1;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.course-cover span {
  position: relative;
  z-index: 1;
}

.my-content {
  display: grid;
  gap: 12px;
  padding: 22px;
}

.meta-row,
.card-footer {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
  justify-content: space-between;
  color: var(--slate-500);
  font-weight: 700;
}

h2 {
  margin: 0;
  font-size: 22px;
}

.my-content p {
  margin: 0;
  color: var(--slate-600);
  line-height: 1.7;
}

@media (max-width: 980px) {
  .my-grid,
  .my-card {
    grid-template-columns: 1fr;
  }

  .my-heading {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
