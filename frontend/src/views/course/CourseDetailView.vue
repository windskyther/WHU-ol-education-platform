<template>
  <main class="page-shell detail-page">
    <AppNav>
      <template v-if="canManage" #actions>
        <el-button type="primary" @click="$router.push(`/teacher/courses/${courseId}/chapters`)">{{ t('course.detail.chapterManagement') }}</el-button>
        <el-button plain @click="$router.push(`/teacher/courses/${courseId}/exams`)">{{ t('course.detail.examManagement') }}</el-button>
      </template>
    </AppNav>

    <BreadcrumbNav :items="breadcrumbItems" />

    <section v-loading="loading" class="detail-workspace">
      <template v-if="course">
        <header class="detail-intro">
          <div class="intro-copy">
            <p class="eyebrow">{{ t('course.detail.overviewEyebrow') }}</p>
            <h1>{{ course.title }}</h1>
            <p class="course-summary">{{ course.description || t('course.detail.noDescription') }}</p>
          </div>

          <aside class="join-panel">
            <div class="cover-strip">
              <img v-if="coverUrl" :src="coverUrl" :alt="course.title" />
              <span v-else>{{ (course.title || t('course.card.coverInitial')).slice(0, 1) }}</span>
            </div>
            <div class="join-state">
              <span class="status-pill">{{ accessLabel }}</span>
              <strong>{{ isEnrolled || canManage ? 'Content unlocked' : 'Join to unlock' }}</strong>
              <p>{{ isEnrolled || canManage ? t('course.detail.contentUnlocked') : t('course.detail.contentLocked') }}</p>
            </div>
            <div class="join-actions">
              <el-button v-if="!userStore.isLoggedIn" type="primary" size="large" @click="goLogin">{{ t('course.detail.loginToLearn') }}</el-button>
              <el-button v-else-if="userStore.role === 'student' && isEnrolled" type="primary" size="large" @click="goLearn">{{ t('course.detail.continueLearn') }}</el-button>
              <el-button
                v-else-if="userStore.role === 'student'"
                type="primary"
                size="large"
                :loading="enrolling"
                @click="handleEnroll"
              >
                {{ t('course.detail.joinLearn') }}
              </el-button>
              <el-button v-if="canManage" size="large" plain @click="$router.push(`/teacher/courses/${courseId}/chapters`)">{{ t('course.detail.maintainContent') }}</el-button>
            </div>
          </aside>
        </header>

        <section class="course-facts">
          <div>
            <span>{{ t('course.detail.difficultyLabel') }}</span>
            <strong>{{ levelText }}</strong>
          </div>
          <div>
            <span>{{ t('course.detail.categoryLabel') }}</span>
            <strong>{{ course.category || t('course.detail.uncategorized') }}</strong>
          </div>
          <div>
            <span>{{ t('course.detail.teacherLabel') }}</span>
            <strong>{{ course.teacher?.username || course.teacher_name || t('course.detail.unknownTeacher') }}</strong>
          </div>
          <div>
            <span>{{ t('course.detail.chapterCountLabel') }}</span>
            <strong>{{ course.chapter_count || chapters.length }}</strong>
          </div>
          <div>
            <span>{{ t('course.detail.examCountLabel') }}</span>
            <strong>{{ exams.length }}</strong>
          </div>
        </section>

        <section class="chapter-access">
          <div class="section-heading">
            <div>
              <p class="eyebrow">{{ t('course.detail.chapterEntryEyebrow') }}</p>
              <h2>{{ t('course.detail.chapterListTitle') }}</h2>
            </div>
            <el-tag :type="course.is_published ? 'success' : 'warning'" effect="light">
              {{ course.is_published ? t('course.detail.published') : t('course.detail.draft') }}
            </el-tag>
          </div>

          <div v-if="!canViewChapters" class="locked-panel">
            <strong>{{ t('course.detail.lockedChapterTitle') }}</strong>
            <p>{{ t('course.detail.lockedChapterDesc') }}</p>
          </div>

          <div v-else-if="chapters.length" class="chapter-grid">
            <article v-for="chapter in orderedChapters" :key="chapter.id" class="chapter-tile">
              <span class="chapter-order">{{ chapterOrder(chapter) }}</span>
              <div>
                <h3>{{ chapter.title }}</h3>
                <p>{{ chapter.description || t('course.detail.noChapterDesc') }}</p>
              </div>
              <div class="resource-tags">
                <span :class="{ active: chapterVideo(chapter) }">{{ t('course.detail.videoTag') }}</span>
                <span :class="{ active: chapterMaterial(chapter) }">{{ t('course.detail.materialTag') }}</span>
              </div>
            </article>
          </div>

          <div v-else class="empty-state">{{ t('course.detail.noChapters') }}</div>
        </section>

        <section v-if="canViewChapters" class="exam-access">
          <div class="section-heading">
            <div>
              <p class="eyebrow">{{ t('course.detail.examEntryEyebrow') }}</p>
              <h2>{{ t('course.detail.examListTitle') }}</h2>
            </div>
            <el-tag effect="light">{{ t('course.detail.examCount', { n: exams.length }) }}</el-tag>
          </div>

          <div v-if="exams.length" class="exam-grid">
            <article v-for="examItem in exams" :key="examItem.id" class="exam-tile">
              <div>
                <span class="status-pill" :class="{ 'is-done': examItem.is_published }">
                  {{ examItem.is_published ? t('course.detail.published') : t('course.detail.draft') }}
                </span>
                <h3>{{ examItem.title }}</h3>
                <p>{{ examItem.description || t('course.detail.noExamDesc') }}</p>
              </div>
              <div class="exam-meta">
                <span>{{ t('course.detail.minutes', { n: examItem.duration || examItem.duration_minutes || '-' }) }}</span>
                <span>{{ t('course.detail.passScore', { score: examItem.pass_score ?? '-' }) }}</span>
              </div>
              <div class="table-actions">
                <el-button v-if="userStore.role === 'student'" type="primary" @click="$router.push(`/student/exams/${examItem.id}`)">{{ t('course.detail.enterExam') }}</el-button>
                <el-button v-if="canManage" plain @click="$router.push(`/teacher/exams/${examItem.id}/questions`)">{{ t('course.detail.maintainQuestions') }}</el-button>
              </div>
            </article>
          </div>

          <div v-else class="empty-state">{{ t('course.detail.noExams') }}</div>
        </section>

        <CourseQuestionPanel
          :course-id="courseId"
          :can-ask="canAskQuestions"
          :can-manage="canManage"
          :heading="t('course.question.heading')"
        />
      </template>
    </section>
  </main>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useI18n } from 'vue-i18n'
import { enrollCourse, fetchChapters, fetchCourseDetail } from '../../api/course'
import { fetchCourseExams } from '../../api/exam'
import AppNav from '../../components/AppNav.vue'
import BreadcrumbNav from '../../components/BreadcrumbNav.vue'
import CourseQuestionPanel from '../../components/CourseQuestionPanel.vue'
import { useUserStore } from '../../stores/user'
import { getCommonErrorMessage } from '../../utils/errorMessage'
import { normalizeMediaUrl } from '../../utils/mediaUrl'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const courseId = computed(() => route.params.id)
const loading = ref(false)
const enrolling = ref(false)
const course = ref(null)
const chapters = ref([])
const exams = ref([])

const levelText = computed(() => {
  const map = {
    beginner: t('course.level.beginner'),
    intermediate: t('course.level.intermediate'),
    advanced: t('course.level.advanced')
  }
  return map[course.value?.level] || t('course.level.beginner')
})

const orderedChapters = computed(() => [...chapters.value].sort((a, b) => chapterOrder(a) - chapterOrder(b)))
const canManage = computed(() => ['teacher', 'admin'].includes(userStore.role))
const isEnrolled = computed(() => Boolean(course.value?.is_enrolled || course.value?.enrolled || course.value?.enrollment))
const canViewChapters = computed(() => canManage.value || isEnrolled.value)
const canAskQuestions = computed(() => userStore.role === 'student' && isEnrolled.value)
const coverUrl = computed(() => normalizeMediaUrl(course.value?.cover_url || ''))
const accessLabel = computed(() => {
  if (canManage.value) return t('course.detail.accessTeacher')
  if (isEnrolled.value) return t('course.detail.accessEnrolled')
  return t('course.detail.accessGuest')
})

const breadcrumbItems = computed(() => [
  { label: t('course.detail.breadcrumbCourses'), to: '/courses' },
  { label: course.value?.title || t('course.detail.breadcrumbDetail') }
])

function chapterOrder(chapter) {
  return chapter.order ?? chapter.order_no ?? 0
}

function chapterVideo(chapter) {
  return chapter.video_url || chapter.video?.url || chapter.video?.file_url || chapter.video
}

function chapterMaterial(chapter) {
  return chapter.material_id || chapter.material?.id || chapter.material_url || chapter.material?.url || chapter.material
}

function goLogin() {
  router.push({ path: '/login', query: { redirect: route.fullPath } })
}

function goLearn() {
  router.push(`/student/learn/${courseId.value}`)
}

async function handleEnroll() {
  enrolling.value = true
  try {
    await enrollCourse(courseId.value)
    ElMessage.success(t('course.detail.enrollSuccess'))
    course.value = {
      ...course.value,
      is_enrolled: true
    }
    goLearn()
  } catch (error) {
    ElMessage.error(getCommonErrorMessage(error, t('course.detail.enrollError')))
    await loadDetail()
  } finally {
    enrolling.value = false
  }
}

async function loadDetail() {
  loading.value = true
  try {
    const courseData = await fetchCourseDetail(courseId.value)
    course.value = courseData
    chapters.value = []
    exams.value = []

    if (canViewChapters.value) {
      const [chapterData, examData] = await Promise.all([
        fetchChapters(courseId.value),
        fetchCourseExams(courseId.value)
      ])
      chapters.value = Array.isArray(chapterData) ? chapterData : chapterData?.results || []
      exams.value = Array.isArray(examData) ? examData : examData?.results || []
    }
  } catch (error) {
    ElMessage.error(getCommonErrorMessage(error, t('course.detail.loadError')))
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadDetail()
})
</script>

<style scoped>
.detail-workspace {
  min-height: 420px;
  margin: 64px auto 0;
}

.detail-intro {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 360px;
  gap: 28px;
  align-items: stretch;
}

.intro-copy {
  display: grid;
  align-content: end;
  min-height: 520px;
  padding: 42px;
  background: rgba(255, 250, 240, 0.82);
  border: 2px solid var(--line);
  border-radius: var(--radius-md);
}

.course-summary {
  max-width: 760px;
  margin: 28px 0 0;
}

.join-panel {
  display: grid;
  grid-template-rows: 190px 1fr auto;
  overflow: hidden;
  background: var(--ink);
  color: var(--paper);
  border-radius: var(--radius-md);
}

.cover-strip {
  display: grid;
  place-items: center;
  overflow: hidden;
  color: var(--ink);
  background: linear-gradient(135deg, var(--hot), var(--pink));
  font-size: 96px;
  font-weight: 900;
  letter-spacing: -0.1em;
}

.cover-strip img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.join-state {
  display: grid;
  gap: 14px;
  align-content: start;
  padding: 26px;
}

.join-state strong {
  font-size: 38px;
  font-weight: 900;
  line-height: 0.9;
  letter-spacing: -0.06em;
}

.join-state p {
  margin: 0;
  color: rgba(246, 241, 230, 0.68);
  font-weight: 800;
  line-height: 1.25;
}

.join-actions {
  padding: 0 26px 26px;
}

.course-facts {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
  margin-top: 18px;
}

.course-facts div {
  display: grid;
  gap: 10px;
  padding: 20px;
  background: rgba(255, 250, 240, 0.9);
  border: 2px solid var(--line);
  border-radius: var(--radius-md);
}

.course-facts span {
  color: var(--muted);
  font-size: 12px;
  font-weight: 900;
  text-transform: uppercase;
}

.course-facts strong {
  overflow: hidden;
  font-size: 26px;
  font-weight: 900;
  line-height: 0.95;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.chapter-access,
.exam-access {
  margin-top: 18px;
  padding: 28px;
  background: rgba(255, 250, 240, 0.88);
  border: 2px solid var(--line);
  border-radius: var(--radius-md);
}

.section-heading {
  display: flex;
  gap: 16px;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 22px;
}

.section-heading h2 {
  margin: 0;
  font-size: clamp(38px, 5vw, 72px);
  font-weight: 900;
  line-height: 0.85;
  letter-spacing: -0.07em;
}

.locked-panel,
.chapter-tile {
  padding: 24px;
  border: 2px solid var(--line);
  border-radius: var(--radius-md);
}

.locked-panel strong {
  display: block;
  font-size: 28px;
  font-weight: 900;
}

.chapter-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.exam-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.chapter-tile {
  display: grid;
  grid-template-columns: 58px minmax(0, 1fr);
  gap: 14px;
  background: rgba(255, 255, 255, 0.36);
}

.chapter-order {
  font-size: 48px;
  font-weight: 900;
  line-height: 0.8;
  letter-spacing: -0.08em;
}

.chapter-tile h3 {
  margin: 0;
  font-size: 24px;
  font-weight: 900;
}

.chapter-tile p {
  margin: 8px 0 0;
  color: var(--muted);
  font-weight: 800;
}

.resource-tags {
  display: flex;
  grid-column: 2;
  gap: 8px;
}

.resource-tags span {
  padding: 6px 10px;
  color: var(--muted);
  border: 2px solid var(--line);
  border-radius: 999px;
  font-size: 12px;
  font-weight: 900;
}

.resource-tags span.active {
  color: var(--ink);
  background: var(--acid);
  border-color: var(--acid);
}

.exam-tile {
  display: grid;
  gap: 16px;
  align-content: space-between;
  padding: 24px;
  background: rgba(255, 255, 255, 0.36);
  border: 2px solid var(--line);
  border-radius: var(--radius-md);
}

.exam-tile h3 {
  margin: 12px 0 0;
  font-size: 24px;
  font-weight: 900;
}

.exam-tile p {
  margin: 8px 0 0;
  color: var(--muted);
  font-weight: 800;
}

.exam-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.exam-meta span {
  padding: 7px 10px;
  background: rgba(25, 25, 23, 0.06);
  border-radius: var(--radius-sm);
  font-size: 12px;
  font-weight: 900;
}

@media (max-width: 980px) {
  .detail-intro,
  .course-facts,
  .chapter-grid,
  .exam-grid {
    grid-template-columns: 1fr;
  }
}
</style>
