<template>
  <main class="page-shell my-page">
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

    <section class="my-workspace">
      <header class="learning-board">
        <div>
          <p class="eyebrow">Learning dashboard</p>
          <h1>我的学习进度</h1>
          <p>继续推进已经加入的课程，优先回到最需要完成的学习内容。</p>
        </div>
        <el-button type="primary" size="large" @click="$router.push('/courses')">发现新课程</el-button>
      </header>

      <section class="summary-strip">
        <div>
          <span>已加入课程</span>
          <strong>{{ total }}</strong>
        </div>
        <div>
          <span>平均完成度</span>
          <strong>{{ averageProgress }}%</strong>
        </div>
        <div>
          <span>本页课程</span>
          <strong>{{ courses.length }}</strong>
        </div>
      </section>

      <section class="course-toolbar">
        <el-select v-model="state" clearable placeholder="学习状态" @change="loadCourses(1)">
          <el-option label="学习中" value="learning" />
          <el-option label="已完成" value="completed" />
        </el-select>
        <el-button type="primary" :loading="loading" @click="loadCourses(1)">刷新</el-button>
      </section>

      <section v-loading="loading" class="course-list">
        <article v-for="item in courses" :key="item.id" class="learning-row">
          <div class="row-cover">
            <img v-if="coverUrl(courseOf(item))" :src="coverUrl(courseOf(item))" :alt="courseOf(item).title" />
            <span v-else>{{ (courseOf(item).title || '课').slice(0, 1) }}</span>
          </div>
          <div class="row-main">
            <div class="row-meta">
              <el-tag effect="light">{{ levelText(courseOf(item).level) }}</el-tag>
              <span>{{ courseOf(item).category || '未分类' }}</span>
              <span>{{ courseOf(item).teacher?.username || courseOf(item).teacher_name || '教师未命名' }}</span>
            </div>
            <h2>{{ courseOf(item).title }}</h2>
            <p>{{ courseOf(item).description || '暂无课程简介' }}</p>
            <el-progress :percentage="progressOf(item)" :stroke-width="10" />
          </div>
          <div class="row-action">
            <strong>{{ progressOf(item) }}%</strong>
            <span>{{ progressOf(item) >= 100 ? '已完成' : '继续学习' }}</span>
            <el-button type="primary" @click="$router.push(`/student/learn/${courseOf(item).id}`)">进入学习</el-button>
          </div>
        </article>
      </section>

      <div v-if="!loading && courses.length === 0" class="empty-state">还没有加入课程。去课程列表找到第一门想完成的课。</div>

      <PaginationBar :total="total" :page="page" :page-size="pageSize" @change="loadCourses" />
    </section>
  </main>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { ElMessage } from 'element-plus'
import PaginationBar from '../../components/PaginationBar.vue'
import { fetchMyCourses } from '../../api/course'
import { getCommonErrorMessage } from '../../utils/errorMessage'
import { normalizeMediaUrl } from '../../utils/mediaUrl'

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

const averageProgress = computed(() => {
  if (!courses.value.length) return 0
  const totalProgress = courses.value.reduce((sum, item) => sum + progressOf(item), 0)
  return Math.round(totalProgress / courses.value.length)
})

function levelText(level) {
  return levelMap[level] || '初级'
}

function courseOf(item) {
  return item.course || item.course_detail || item
}

function coverUrl(course) {
  return normalizeMediaUrl(course?.cover_url || '')
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
.my-page {
  background:
    radial-gradient(circle at 18% 8%, rgba(99, 102, 241, 0.18), transparent 30%),
    linear-gradient(180deg, #ffffff 0, #f6f5ff 360px, #fafafa 100%);
}

.my-workspace {
  max-width: 1180px;
  margin: 46px auto 0;
}

.learning-board {
  display: flex;
  gap: 24px;
  align-items: flex-end;
  justify-content: space-between;
  padding: 34px;
  color: var(--white);
  background:
    linear-gradient(135deg, rgba(99, 102, 241, 0.96), rgba(139, 92, 246, 0.9)),
    #6366f1;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-soft);
}

.learning-board .eyebrow {
  color: rgba(255, 255, 255, 0.78) !important;
}

.learning-board h1 {
  margin: 0;
  font-size: clamp(38px, 5vw, 58px);
  line-height: 1.06;
}

.learning-board p:last-child {
  max-width: 620px;
  margin: 14px 0 0;
  color: rgba(255, 255, 255, 0.84);
  font-size: 17px;
  line-height: 1.7;
}

.summary-strip {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
  margin-top: 18px;
}

.summary-strip div {
  display: grid;
  gap: 8px;
  padding: 22px;
  background: rgba(255, 255, 255, 0.96);
  border: 1px solid rgba(99, 102, 241, 0.12);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-card);
}

.summary-strip span {
  color: var(--slate-500);
  font-weight: 800;
}

.summary-strip strong {
  color: var(--ink-900);
  font-size: 34px;
  line-height: 1;
}

.course-toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
  margin-top: 18px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid rgba(99, 102, 241, 0.1);
  border-radius: var(--radius-md);
}

.course-list {
  display: grid;
  gap: 14px;
  min-height: 180px;
  margin-top: 18px;
}

.learning-row {
  display: grid;
  grid-template-columns: 156px minmax(0, 1fr) 150px;
  gap: 18px;
  align-items: stretch;
  padding: 14px;
  background: var(--white);
  border: 1px solid rgba(99, 102, 241, 0.12);
  border-radius: var(--radius-lg);
  box-shadow: 0 1px 0 rgba(23, 22, 41, 0.03);
  transition:
    border-color 0.2s ease,
    box-shadow 0.2s ease,
    transform 0.2s ease;
}

.learning-row:hover {
  border-color: rgba(99, 102, 241, 0.3);
  box-shadow: var(--shadow-hover);
  transform: translateY(-2px);
}

.row-cover {
  display: grid;
  place-items: center;
  min-height: 150px;
  overflow: hidden;
  color: var(--brand-indigo);
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.13), rgba(245, 158, 11, 0.18));
  border-radius: var(--radius-md);
  font-size: 48px;
  font-weight: 900;
}

.row-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.row-main {
  display: grid;
  gap: 10px;
  align-content: center;
}

.row-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
  color: var(--slate-500);
  font-size: 13px;
  font-weight: 800;
}

.row-main h2 {
  margin: 0;
  font-size: 24px;
  line-height: 1.25;
}

.row-main p {
  display: -webkit-box;
  margin: 0;
  overflow: hidden;
  color: var(--slate-600);
  line-height: 1.7;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.row-action {
  display: grid;
  gap: 8px;
  align-content: center;
  justify-items: end;
  padding-left: 14px;
  border-left: 1px solid rgba(99, 102, 241, 0.12);
}

.row-action strong {
  color: var(--brand-indigo);
  font-size: 38px;
  line-height: 1;
}

.row-action span {
  color: var(--slate-500);
  font-weight: 800;
}

@media (max-width: 900px) {
  .learning-board {
    align-items: flex-start;
    flex-direction: column;
  }

  .summary-strip,
  .learning-row {
    grid-template-columns: 1fr;
  }

  .row-action {
    justify-items: start;
    padding-left: 0;
    border-left: 0;
  }
}
</style>
