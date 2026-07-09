<template>
  <main class="page-shell my-page">
    <AppNav />

    <section class="my-workspace">
      <header class="learning-board kinetic-panel">
        <div>
          <p class="eyebrow">{{ t('student.myCourses.eyebrow') }}</p>
          <h1>{{ t('student.myCourses.heading') }}</h1>
          <p>{{ t('student.myCourses.description') }}</p>
        </div>
        <el-button type="primary" size="large" @click="$router.push('/courses')">{{ t('student.myCourses.discoverButton') }}</el-button>
      </header>

      <section class="summary-strip">
        <div>
          <span>{{ t('student.myCourses.statEnrolled') }}</span>
          <strong>{{ total }}</strong>
        </div>
        <div>
          <span>{{ t('student.myCourses.statAvgProgress') }}</span>
          <strong>{{ averageProgress }}%</strong>
        </div>
        <div>
          <span>{{ t('student.myCourses.statPageCount') }}</span>
          <strong>{{ courses.length }}</strong>
        </div>
      </section>

      <section class="surface course-toolbar">
        <el-select v-model="state" clearable :placeholder="t('student.myCourses.stateFilterPlaceholder')" @change="loadCourses(1)">
          <el-option :label="t('student.myCourses.stateLearning')" value="learning" />
          <el-option :label="t('student.myCourses.stateCompleted')" value="completed" />
        </el-select>
        <el-button type="primary" :loading="loading" @click="loadCourses(1)">{{ t('student.myCourses.refreshButton') }}</el-button>
      </section>

      <section v-loading="loading" class="course-list">
        <article v-for="item in courses" :key="item.id" class="learning-row">
          <div class="row-cover">
            <img v-if="coverUrl(courseOf(item))" :src="coverUrl(courseOf(item))" :alt="courseOf(item).title" />
            <span v-else>{{ (courseOf(item).title || t('student.myCourses.coverFallbackChar')).slice(0, 1) }}</span>
          </div>
          <div class="row-main">
            <div class="row-meta">
              <span>{{ levelText(courseOf(item).level) }}</span>
              <span>{{ courseOf(item).category || t('student.myCourses.uncategorized') }}</span>
              <span>{{ courseOf(item).teacher?.username || courseOf(item).teacher_name || t('student.myCourses.unknownTeacher') }}</span>
            </div>
            <h2>{{ courseOf(item).title }}</h2>
            <p>{{ courseOf(item).description || t('student.myCourses.noDescription') }}</p>
            <el-progress :percentage="progressOf(item)" :stroke-width="10" />
          </div>
          <div class="row-action">
            <strong>{{ progressOf(item) }}%</strong>
            <span>{{ progressOf(item) >= 100 ? t('student.myCourses.statusCompleted') : t('student.myCourses.statusContinue') }}</span>
            <el-button type="primary" @click="$router.push(`/student/learn/${courseOf(item).id}`)">{{ t('student.myCourses.enterCourse') }}</el-button>
          </div>
        </article>
      </section>

      <div v-if="!loading && courses.length === 0" class="empty-state">{{ t('student.myCourses.empty') }}</div>

      <PaginationBar :total="total" :page="page" :page-size="pageSize" @change="loadCourses" />
    </section>
  </main>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useI18n } from 'vue-i18n'
import AppNav from '../../components/AppNav.vue'
import PaginationBar from '../../components/PaginationBar.vue'
import { fetchMyCourses } from '../../api/course'
import { getCommonErrorMessage } from '../../utils/errorMessage'
import { normalizeMediaUrl } from '../../utils/mediaUrl'

const { t } = useI18n()
const loading = ref(false)
const courses = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const state = ref('')

function levelText(level) {
  const map = {
    beginner: t('student.myCourses.levelBeginner'),
    intermediate: t('student.myCourses.levelIntermediate'),
    advanced: t('student.myCourses.levelAdvanced')
  }
  return map[level] || t('student.myCourses.levelBeginner')
}

const averageProgress = computed(() => {
  if (!courses.value.length) return 0
  const totalProgress = courses.value.reduce((sum, item) => sum + progressOf(item), 0)
  return Math.round(totalProgress / courses.value.length)
})

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
    ElMessage.error(getCommonErrorMessage(error, t('student.myCourses.loadError')))
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadCourses(1)
})
</script>

<style scoped>
.my-workspace {
  margin: 64px auto 0;
}

.learning-board {
  display: flex;
  gap: 24px;
  align-items: flex-end;
  justify-content: space-between;
  min-height: 420px;
  padding: 42px;
}

.learning-board h1,
.learning-board p {
  color: var(--paper);
}

.learning-board p:not(.eyebrow) {
  max-width: 620px;
  color: rgba(246, 241, 230, 0.72);
}

.summary-strip {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  margin-top: 18px;
}

.summary-strip div {
  display: grid;
  gap: 10px;
  padding: 22px;
  background: rgba(255, 250, 240, 0.88);
  border: 2px solid var(--line);
  border-radius: var(--radius-md);
}

.summary-strip span,
.row-meta,
.row-action span {
  color: var(--muted);
  font-size: 12px;
  font-weight: 900;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.summary-strip strong {
  font-size: 54px;
  font-weight: 900;
  line-height: 0.85;
  letter-spacing: -0.07em;
}

.course-toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
  margin-top: 18px;
  padding: 16px;
}

.course-list {
  display: grid;
  gap: 14px;
  min-height: 180px;
  margin-top: 18px;
}

.learning-row {
  display: grid;
  grid-template-columns: 180px minmax(0, 1fr) 160px;
  gap: 22px;
  align-items: stretch;
  padding: 14px;
  background: rgba(255, 250, 240, 0.88);
  border: 2px solid var(--line);
  border-radius: var(--radius-md);
}

.row-cover {
  display: grid;
  place-items: center;
  min-height: 170px;
  overflow: hidden;
  color: var(--ink);
  background: linear-gradient(135deg, var(--hot), var(--pink));
  font-size: 72px;
  font-weight: 900;
  letter-spacing: -0.1em;
}

.row-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.row-main {
  display: grid;
  gap: 12px;
  align-content: center;
}

.row-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.row-main h2 {
  margin: 0;
  font-size: clamp(34px, 5vw, 70px);
  font-weight: 900;
  line-height: 0.84;
  letter-spacing: -0.075em;
}

.row-main p {
  margin: 0;
  color: var(--muted);
  font-weight: 800;
}

.row-action {
  display: grid;
  gap: 10px;
  align-content: center;
  justify-items: end;
}

.row-action strong {
  font-size: 50px;
  font-weight: 900;
  line-height: 0.85;
  letter-spacing: -0.07em;
}

@media (max-width: 980px) {
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
  }
}
</style>
