<template>
  <main class="page-shell detail-page">
    <nav class="app-nav">
      <RouterLink class="brand-link" to="/">
        <span class="brand-mark">WHU</span>
        <span>Online Education</span>
      </RouterLink>
      <div class="nav-actions">
        <RouterLink to="/courses">Courses</RouterLink>
        <RouterLink v-if="userStore.role === 'student'" to="/student/courses">My courses</RouterLink>
        <el-button v-if="canManage" type="primary" @click="$router.push(`/teacher/courses/${courseId}/chapters`)">Manage chapters</el-button>
        <el-button v-if="canManage" plain @click="$router.push(`/teacher/courses/${courseId}/exams`)">Manage exams</el-button>
      </div>
    </nav>

    <section v-loading="loading" class="detail-workspace">
      <template v-if="course">
        <header class="detail-intro">
          <div class="intro-copy">
            <p class="eyebrow">Course overview</p>
            <h1>{{ course.title }}</h1>
            <p class="course-summary">{{ course.description || '暂无课程简介' }}</p>
          </div>

          <aside class="join-panel">
            <div class="cover-strip">
              <img v-if="coverUrl" :src="coverUrl" :alt="course.title" />
              <span v-else>{{ (course.title || '课').slice(0, 1) }}</span>
            </div>
            <div class="join-state">
              <span class="status-pill">{{ accessLabel }}</span>
              <strong>{{ isEnrolled || canManage ? 'Content unlocked' : 'Join to unlock' }}</strong>
              <p>{{ isEnrolled || canManage ? '可以查看章节内容并进入学习空间。' : '课程介绍公开可见，章节资源会在加入学习后开放。' }}</p>
            </div>
            <div class="join-actions">
              <el-button v-if="!userStore.isLoggedIn" type="primary" size="large" @click="goLogin">登录后学习</el-button>
              <el-button v-else-if="userStore.role === 'student' && isEnrolled" type="primary" size="large" @click="goLearn">继续学习</el-button>
              <el-button
                v-else-if="userStore.role === 'student'"
                type="primary"
                size="large"
                :loading="enrolling"
                @click="handleEnroll"
              >
                加入学习
              </el-button>
              <el-button v-if="canManage" size="large" plain @click="$router.push(`/teacher/courses/${courseId}/chapters`)">维护内容</el-button>
            </div>
          </aside>
        </header>

        <section class="course-facts">
          <div>
            <span>Level</span>
            <strong>{{ levelText }}</strong>
          </div>
          <div>
            <span>Category</span>
            <strong>{{ course.category || '未分类' }}</strong>
          </div>
          <div>
            <span>Teacher</span>
            <strong>{{ course.teacher?.username || course.teacher_name || '教师未命名' }}</strong>
          </div>
          <div>
            <span>Chapters</span>
            <strong>{{ course.chapter_count || chapters.length }}</strong>
          </div>
          <div>
            <span>Exams</span>
            <strong>{{ exams.length }}</strong>
          </div>
        </section>

        <section class="chapter-access">
          <div class="section-heading">
            <div>
              <p class="eyebrow">Chapter access</p>
              <h2>Content rail</h2>
            </div>
            <el-tag :type="course.is_published ? 'success' : 'warning'" effect="light">
              {{ course.is_published ? '已发布' : '草稿' }}
            </el-tag>
          </div>

          <div v-if="!canViewChapters" class="locked-panel">
            <strong>加入学习后查看章节内容</strong>
            <p>视频与资料地址由后端权限控制，未加入课程时只展示课程介绍。</p>
          </div>

          <div v-else-if="chapters.length" class="chapter-grid">
            <article v-for="chapter in orderedChapters" :key="chapter.id" class="chapter-tile">
              <span class="chapter-order">{{ chapterOrder(chapter) }}</span>
              <div>
                <h3>{{ chapter.title }}</h3>
                <p>{{ chapter.description || '暂无章节简介' }}</p>
              </div>
              <div class="resource-tags">
                <span :class="{ active: chapterVideo(chapter) }">视频</span>
                <span :class="{ active: chapterMaterial(chapter) }">资料</span>
              </div>
            </article>
          </div>

          <div v-else class="empty-state">暂无章节</div>
        </section>

        <section v-if="canViewChapters" class="exam-access">
          <div class="section-heading">
            <div>
              <p class="eyebrow">Exam access</p>
              <h2>Assessment rail</h2>
            </div>
            <el-tag effect="light">{{ exams.length }} 场考试</el-tag>
          </div>

          <div v-if="exams.length" class="exam-grid">
            <article v-for="examItem in exams" :key="examItem.id" class="exam-tile">
              <div>
                <span class="status-pill" :class="{ 'is-done': examItem.is_published }">
                  {{ examItem.is_published ? '已发布' : '草稿' }}
                </span>
                <h3>{{ examItem.title }}</h3>
                <p>{{ examItem.description || '暂无考试说明' }}</p>
              </div>
              <div class="exam-meta">
                <span>{{ examItem.duration || examItem.duration_minutes || '-' }} 分钟</span>
                <span>及格线 {{ examItem.pass_score ?? '-' }}</span>
              </div>
              <div class="table-actions">
                <el-button v-if="userStore.role === 'student'" type="primary" @click="$router.push(`/student/exams/${examItem.id}`)">进入考试</el-button>
                <el-button v-if="canManage" plain @click="$router.push(`/teacher/exams/${examItem.id}/questions`)">维护题目</el-button>
              </div>
            </article>
          </div>

          <div v-else class="empty-state">暂无考试</div>
        </section>
      </template>
    </section>
  </main>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { enrollCourse, fetchChapters, fetchCourseDetail } from '../../api/course'
import { fetchCourseExams } from '../../api/exam'
import { useUserStore } from '../../stores/user'
import { getCommonErrorMessage } from '../../utils/errorMessage'
import { normalizeMediaUrl } from '../../utils/mediaUrl'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const courseId = computed(() => route.params.id)
const loading = ref(false)
const enrolling = ref(false)
const course = ref(null)
const chapters = ref([])
const exams = ref([])

const levelMap = {
  beginner: '初级',
  intermediate: '中级',
  advanced: '高级'
}

const levelText = computed(() => levelMap[course.value?.level] || '初级')
const orderedChapters = computed(() => [...chapters.value].sort((a, b) => chapterOrder(a) - chapterOrder(b)))
const canManage = computed(() => ['teacher', 'admin'].includes(userStore.role))
const isEnrolled = computed(() => Boolean(course.value?.is_enrolled || course.value?.enrolled || course.value?.enrollment))
const canViewChapters = computed(() => canManage.value || isEnrolled.value)
const coverUrl = computed(() => normalizeMediaUrl(course.value?.cover_url || ''))
const accessLabel = computed(() => {
  if (canManage.value) return '教师/管理员'
  if (isEnrolled.value) return '已加入'
  return '未加入'
})

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
    ElMessage.success('已加入课程')
    course.value = {
      ...course.value,
      is_enrolled: true
    }
    goLearn()
  } catch (error) {
    ElMessage.error(getCommonErrorMessage(error, '加入课程失败'))
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
    ElMessage.error(getCommonErrorMessage(error, '课程详情加载失败'))
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
