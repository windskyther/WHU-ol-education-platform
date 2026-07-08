<template>
  <main class="page-shell">
    <nav class="app-nav">
      <RouterLink class="brand-link" to="/">
        <span class="brand-mark">WHU</span>
        <span>在线教育平台</span>
      </RouterLink>
      <div class="nav-actions">
        <RouterLink to="/courses">课程列表</RouterLink>
        <RouterLink v-if="userStore.role === 'student'" to="/student/courses">我的课程</RouterLink>
        <el-button v-if="canManage" type="primary" @click="$router.push(`/teacher/courses/${courseId}/chapters`)">管理章节</el-button>
      </div>
    </nav>

    <section v-loading="loading" class="detail-shell">
      <template v-if="course">
        <div class="detail-hero momentum-ribbon">
          <div class="detail-copy">
            <p class="eyebrow">Course detail</p>
            <h1>{{ course.title }}</h1>
            <p>{{ course.description || '暂无课程简介' }}</p>
            <div class="meta-row">
              <el-tag effect="light">{{ levelText }}</el-tag>
              <span>{{ course.category || '未分类' }}</span>
              <span>{{ course.teacher?.username || course.teacher_name || '教师未命名' }}</span>
              <span>{{ course.chapter_count || chapters.length }} 章</span>
            </div>
            <div class="actions">
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
          </div>
          <div class="cover surface">
            <img v-if="course.cover_url" :src="course.cover_url" :alt="course.title" />
            <span v-else>{{ (course.title || '课').slice(0, 1) }}</span>
          </div>
        </div>

        <section class="surface chapters-panel">
          <div class="panel-title">
            <div>
              <p class="eyebrow">Chapter map</p>
              <h2>章节目录</h2>
            </div>
            <el-tag :type="course.is_published ? 'success' : 'warning'" effect="light">
              {{ course.is_published ? '已发布' : '草稿' }}
            </el-tag>
          </div>

          <div v-if="!canViewChapters" class="empty-state">加入学习后查看章节内容</div>
          <div v-else-if="chapters.length" class="chapter-list">
            <article v-for="chapter in orderedChapters" :key="chapter.id" class="chapter-item">
              <div class="chapter-index">{{ chapterOrder(chapter) }}</div>
              <div>
                <strong>{{ chapter.title }}</strong>
                <p>{{ chapter.description || '暂无章节简介' }}</p>
              </div>
              <div class="asset-row">
                <span class="status-pill" :class="{ 'is-done': chapterVideo(chapter) }">{{ chapterVideo(chapter) ? '有视频' : '无视频' }}</span>
                <span class="status-pill is-warm" :class="{ 'is-done': chapterMaterial(chapter) }">{{ chapterMaterial(chapter) ? '有资料' : '无资料' }}</span>
              </div>
            </article>
          </div>
          <div v-else class="empty-state">暂无章节</div>
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
import { useUserStore } from '../../stores/user'
import { getCommonErrorMessage } from '../../utils/errorMessage'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const courseId = computed(() => route.params.id)
const loading = ref(false)
const enrolling = ref(false)
const course = ref(null)
const chapters = ref([])

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

    if (canViewChapters.value) {
      const chapterData = await fetchChapters(courseId.value)
      chapters.value = Array.isArray(chapterData) ? chapterData : chapterData?.results || []
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
.detail-shell {
  max-width: 1180px;
  min-height: 380px;
  margin: 54px auto 0;
}

.detail-hero {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 330px;
  gap: 24px;
  align-items: stretch;
  padding: 26px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(99, 102, 241, 0.12);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-soft);
}

.detail-hero > * {
  position: relative;
  z-index: 1;
}

.detail-copy {
  display: grid;
  align-content: center;
}

.detail-hero h1 {
  margin: 0;
  font-size: clamp(38px, 5vw, 56px);
  line-height: 1.06;
}

.detail-hero p {
  max-width: 720px;
  color: var(--slate-600);
  font-size: 17px;
  line-height: 1.8;
}

.meta-row,
.asset-row,
.panel-title,
.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
}

.actions {
  margin-top: 8px;
}

.meta-row {
  color: var(--slate-500);
  font-weight: 700;
}

.asset-row {
  justify-content: flex-end;
}

.panel-title {
  justify-content: space-between;
  margin-bottom: 18px;
}

.panel-title h2 {
  margin: 0;
  font-size: 24px;
}

.cover {
  display: grid;
  place-items: center;
  min-height: 242px;
  overflow: hidden;
  color: var(--brand-indigo);
  background: var(--gradient-warm);
  font-size: 76px;
  font-weight: 900;
}

.cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.chapters-panel {
  margin-top: 24px;
  padding: 24px;
}

.chapter-list {
  display: grid;
  gap: 12px;
}

.chapter-item {
  display: grid;
  grid-template-columns: 48px minmax(0, 1fr) auto;
  gap: 16px;
  align-items: center;
  padding: 16px;
  background: #fbfaff;
  border: 1px solid rgba(99, 102, 241, 0.1);
  border-radius: var(--radius-md);
}

.chapter-index {
  display: grid;
  place-items: center;
  width: 42px;
  height: 42px;
  color: var(--white);
  background: var(--gradient-primary);
  border-radius: 12px;
  font-weight: 900;
}

.chapter-item p {
  margin: 8px 0 0;
  color: var(--slate-600);
}

@media (max-width: 860px) {
  .detail-hero,
  .chapter-item {
    grid-template-columns: 1fr;
  }

  .asset-row {
    justify-content: flex-start;
  }
}
</style>
