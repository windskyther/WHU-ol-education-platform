<template>
  <main class="page-shell">
    <nav class="app-nav">
      <RouterLink class="brand-link" to="/">
        <span class="brand-mark">WHU</span>
        <span>在线教育平台</span>
      </RouterLink>
      <div class="nav-actions">
        <RouterLink to="/courses">课程列表</RouterLink>
        <el-button v-if="canManage" type="primary" @click="$router.push(`/teacher/courses/${courseId}/chapters`)">管理章节</el-button>
      </div>
    </nav>

    <section v-loading="loading" class="detail-shell">
      <template v-if="course">
        <div class="detail-hero">
          <div>
            <p class="eyebrow">Course detail</p>
            <h1>{{ course.title }}</h1>
            <p>{{ course.description || '暂无课程简介' }}</p>
            <div class="meta-row">
              <el-tag effect="light">{{ levelText }}</el-tag>
              <span>{{ course.category || '未分类' }}</span>
              <span>{{ course.teacher?.username || '教师未命名' }}</span>
              <span>{{ course.chapter_count || chapters.length }} 章</span>
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
              <p class="eyebrow">Growth track</p>
              <h2>章节目录</h2>
            </div>
            <el-tag :type="course.is_published ? 'success' : 'warning'" effect="light">
              {{ course.is_published ? '已发布' : '草稿' }}
            </el-tag>
          </div>

          <div v-if="chapters.length" class="growth-track">
            <article v-for="chapter in orderedChapters" :key="chapter.id" class="growth-node chapter-item">
              <strong>{{ chapter.order }}. {{ chapter.title }}</strong>
              <p>{{ chapter.description || '暂无章节简介' }}</p>
              <div class="asset-row">
                <span>{{ chapter.video ? '已上传视频' : '未上传视频' }}</span>
                <span>{{ chapter.material ? '已上传资料' : '未上传资料' }}</span>
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
import { RouterLink, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { fetchChapters, fetchCourseDetail } from '../../api/course'
import { useUserStore } from '../../stores/user'
import { getCommonErrorMessage } from '../../utils/errorMessage'

const route = useRoute()
const userStore = useUserStore()
const courseId = computed(() => route.params.id)
const loading = ref(false)
const course = ref(null)
const chapters = ref([])

const levelMap = {
  beginner: '初级',
  intermediate: '中级',
  advanced: '高级'
}

const levelText = computed(() => levelMap[course.value?.level] || '初级')
const orderedChapters = computed(() => [...chapters.value].sort((a, b) => (a.order || 0) - (b.order || 0)))
const canManage = computed(() => ['teacher', 'admin'].includes(userStore.role))

async function loadDetail() {
  loading.value = true
  try {
    const [courseData, chapterData] = await Promise.all([fetchCourseDetail(courseId.value), fetchChapters(courseId.value)])
    course.value = courseData
    chapters.value = Array.isArray(chapterData) ? chapterData : []
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
.nav-actions {
  display: flex;
  gap: 14px;
  align-items: center;
}

.nav-actions a {
  color: var(--ink-900);
  font-weight: 700;
  text-decoration: none;
}

.detail-shell {
  max-width: 1120px;
  min-height: 380px;
  margin: 54px auto 0;
}

.detail-hero {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 320px;
  gap: 28px;
  align-items: stretch;
}

.detail-hero h1 {
  margin: 0;
  font-size: 48px;
  line-height: 1.08;
}

.detail-hero p {
  color: var(--slate-600);
  font-size: 17px;
  line-height: 1.8;
}

.meta-row,
.asset-row,
.panel-title {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
}

.meta-row,
.asset-row {
  color: var(--slate-500);
}

.panel-title {
  justify-content: space-between;
  margin-bottom: 18px;
}

.panel-title h2 {
  margin: 0;
}

.cover {
  display: grid;
  place-items: center;
  min-height: 240px;
  overflow: hidden;
  color: var(--green-700);
  background: var(--green-100);
  font-size: 72px;
  font-weight: 800;
}

.cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.chapters-panel {
  margin-top: 28px;
  padding: 24px;
}

.chapter-item {
  padding: 14px 16px;
  background: var(--mint-050);
  border: 1px solid var(--border-soft);
  border-radius: 8px;
}

.chapter-item p {
  margin: 8px 0;
  color: var(--slate-600);
}

@media (max-width: 860px) {
  .detail-hero {
    grid-template-columns: 1fr;
  }
}
</style>
