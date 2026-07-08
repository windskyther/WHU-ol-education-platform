<template>
  <main class="page-shell detail-page">
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

    <section v-loading="loading" class="detail-workspace">
      <template v-if="course">
        <header class="detail-intro">
          <div class="intro-copy">
            <p class="eyebrow">Course overview</p>
            <h1>{{ course.title }}</h1>
            <p class="course-summary">{{ course.description || '暂无课程简介' }}</p>
            <div class="course-meta">
              <span>{{ levelText }}</span>
              <span>{{ course.category || '未分类' }}</span>
              <span>{{ course.teacher?.username || course.teacher_name || '教师未命名' }}</span>
              <span>{{ course.chapter_count || chapters.length }} 章</span>
            </div>
          </div>

          <aside class="join-panel">
            <div class="cover-strip">
              <img v-if="coverUrl" :src="coverUrl" :alt="course.title" />
              <span v-else>{{ (course.title || '课').slice(0, 1) }}</span>
            </div>
            <div class="join-state">
              <span class="state-label">{{ accessLabel }}</span>
              <strong>{{ isEnrolled || canManage ? '内容已开放' : '先加入，再开始学习' }}</strong>
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

        <section class="chapter-access">
          <div class="section-heading">
            <div>
              <p class="eyebrow">Chapter access</p>
              <h2>章节与资源</h2>
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
import { normalizeMediaUrl } from '../../utils/mediaUrl'

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
.detail-page {
  background:
    radial-gradient(circle at 12% 12%, rgba(99, 102, 241, 0.18), transparent 28%),
    radial-gradient(circle at 86% 4%, rgba(139, 92, 246, 0.16), transparent 30%),
    linear-gradient(180deg, #ffffff 0, #f7f7ff 420px, #fafafa 100%);
}

.detail-workspace {
  max-width: 1180px;
  min-height: 420px;
  margin: 46px auto 0;
}

.detail-intro {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 360px;
  gap: 28px;
  align-items: stretch;
}

.intro-copy {
  display: grid;
  align-content: center;
  min-height: 430px;
  padding: 42px;
  color: var(--white);
  background:
    linear-gradient(135deg, rgba(99, 102, 241, 0.96), rgba(139, 92, 246, 0.92)),
    #6366f1;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-soft);
}

.intro-copy .eyebrow {
  color: rgba(255, 255, 255, 0.78) !important;
}

.intro-copy h1 {
  max-width: 760px;
  margin: 0;
  font-size: clamp(42px, 6vw, 72px);
  line-height: 1.02;
}

.course-summary {
  max-width: 760px;
  margin: 22px 0 0;
  color: rgba(255, 255, 255, 0.86);
  font-size: 18px;
  line-height: 1.8;
}

.course-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 30px;
}

.course-meta span {
  padding: 8px 12px;
  color: rgba(255, 255, 255, 0.9);
  background: rgba(255, 255, 255, 0.14);
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: var(--radius-sm);
  font-weight: 800;
}

.join-panel {
  display: grid;
  grid-template-rows: 170px 1fr auto;
  overflow: hidden;
  background: var(--white);
  border: 1px solid rgba(99, 102, 241, 0.14);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
}

.cover-strip {
  display: grid;
  place-items: center;
  overflow: hidden;
  color: var(--brand-indigo);
  background:
    linear-gradient(135deg, rgba(99, 102, 241, 0.14), rgba(245, 158, 11, 0.18)),
    #f4f2ff;
  font-size: 70px;
  font-weight: 900;
}

.cover-strip img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.join-state {
  display: grid;
  gap: 10px;
  align-content: start;
  padding: 24px;
}

.state-label {
  width: fit-content;
  padding: 6px 10px;
  color: var(--brand-indigo);
  background: rgba(99, 102, 241, 0.1);
  border-radius: 999px;
  font-size: 12px;
  font-weight: 900;
}

.join-state strong {
  font-size: 26px;
  line-height: 1.2;
}

.join-state p {
  margin: 0;
  color: var(--slate-600);
  line-height: 1.7;
}

.join-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  padding: 0 24px 24px;
}

.chapter-access {
  margin-top: 26px;
  padding: 28px;
  background: rgba(255, 255, 255, 0.96);
  border: 1px solid rgba(99, 102, 241, 0.12);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
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
  font-size: 28px;
}

.locked-panel {
  display: grid;
  gap: 8px;
  padding: 34px;
  color: var(--ink-700);
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.08), rgba(245, 158, 11, 0.1));
  border: 1px dashed rgba(99, 102, 241, 0.3);
  border-radius: var(--radius-md);
}

.locked-panel strong {
  font-size: 22px;
}

.locked-panel p {
  margin: 0;
  color: var(--slate-600);
}

.chapter-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.chapter-tile {
  display: grid;
  grid-template-columns: 46px minmax(0, 1fr);
  gap: 14px;
  padding: 18px;
  background: #fbfaff;
  border: 1px solid rgba(99, 102, 241, 0.1);
  border-radius: var(--radius-md);
}

.chapter-order {
  display: grid;
  place-items: center;
  width: 42px;
  height: 42px;
  color: var(--white);
  background: var(--gradient-primary);
  border-radius: var(--radius-sm);
  font-weight: 900;
}

.chapter-tile h3 {
  margin: 0;
  font-size: 18px;
}

.chapter-tile p {
  margin: 8px 0 0;
  color: var(--slate-600);
  line-height: 1.6;
}

.resource-tags {
  display: flex;
  grid-column: 2;
  gap: 8px;
}

.resource-tags span {
  padding: 5px 9px;
  color: var(--slate-500);
  background: rgba(122, 129, 148, 0.1);
  border-radius: 999px;
  font-size: 12px;
  font-weight: 800;
}

.resource-tags span.active {
  color: #047857;
  background: rgba(16, 185, 129, 0.14);
}

@media (max-width: 900px) {
  .detail-intro,
  .chapter-grid {
    grid-template-columns: 1fr;
  }

  .intro-copy {
    min-height: 360px;
    padding: 30px;
  }
}
</style>
