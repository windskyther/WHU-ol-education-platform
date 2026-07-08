<template>
  <main class="page-shell">
    <nav class="app-nav">
      <RouterLink class="brand-link" to="/">
        <span class="brand-mark">WHU</span>
        <span>在线教育平台</span>
      </RouterLink>
      <div class="nav-actions">
        <RouterLink to="/student/courses">我的课程</RouterLink>
        <RouterLink :to="`/courses/${courseId}`">课程详情</RouterLink>
      </div>
    </nav>

    <section v-loading="loading" class="learn-shell">
      <template v-if="course">
        <header class="learn-header momentum-ribbon">
          <div>
            <p class="eyebrow">Learning room</p>
            <h1>{{ course.title }}</h1>
            <p>{{ course.description || '选择章节开始学习，系统会自动保存观看进度。' }}</p>
          </div>
          <div class="progress-card">
            <span>课程进度</span>
            <strong>{{ overallProgress }}%</strong>
            <el-progress :percentage="overallProgress" :stroke-width="10" />
          </div>
        </header>

        <div class="learn-layout">
          <aside class="surface chapter-sidebar">
            <div class="sidebar-title">
              <h2>章节</h2>
              <span>{{ orderedChapters.length }} 章</span>
            </div>
            <button
              v-for="chapter in orderedChapters"
              :key="chapter.id"
              class="chapter-button"
              :class="{ 'is-active': selectedChapter?.id === chapter.id }"
              type="button"
              @click="selectChapter(chapter)"
            >
              <span class="chapter-no">{{ chapterOrder(chapter) }}</span>
              <span>
                <strong>{{ chapter.title }}</strong>
                <small>{{ chapterProgress(chapter).percent }}% · {{ chapterProgress(chapter).is_completed ? '已完成' : '学习中' }}</small>
              </span>
            </button>
          </aside>

          <section class="surface player-panel">
            <template v-if="selectedChapter">
              <div class="player-heading">
                <div>
                  <p class="eyebrow">Now learning</p>
                  <h2>{{ selectedChapter.title }}</h2>
                  <p>{{ selectedChapter.description || '暂无章节简介' }}</p>
                </div>
                <span class="status-pill" :class="{ 'is-done': currentProgress.is_completed }">
                  {{ currentProgress.is_completed ? '已完成' : `${currentProgress.percent}%` }}
                </span>
              </div>

              <div class="video-box">
                <video
                  v-if="selectedVideoUrl"
                  ref="videoRef"
                  :key="selectedChapter.id"
                  controls
                  playsinline
                  :src="selectedVideoUrl"
                  @loadedmetadata="handleLoadedMetadata"
                  @timeupdate="handleTimeUpdate"
                  @play="startProgressTimer"
                  @pause="submitCurrentProgress"
                  @ended="handleEnded"
                ></video>
                <div v-else class="empty-video">本章暂未上传视频</div>
              </div>

              <div class="chapter-tools">
                <el-progress :percentage="currentProgress.percent" :stroke-width="10" />
                <div class="tool-actions">
                  <el-button :loading="submitting" @click="submitCurrentProgress">保存进度</el-button>
                  <el-button type="primary" :loading="submitting" @click="markCompleted">标记完成</el-button>
                  <el-button v-if="selectedMaterialId" plain :loading="downloading" @click="handleDownloadMaterial">下载资料</el-button>
                </div>
              </div>
            </template>
            <div v-else class="empty-state">暂无可学习章节</div>
          </section>
        </div>
      </template>
    </section>
  </main>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { RouterLink, onBeforeRouteLeave, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { downloadMaterial, fetchChapters, fetchCourseDetail, fetchCourseProgress, updateLearningProgress } from '../../api/course'
import { getCommonErrorMessage } from '../../utils/errorMessage'

const route = useRoute()
const courseId = computed(() => route.params.courseId)
const loading = ref(false)
const submitting = ref(false)
const downloading = ref(false)
const course = ref(null)
const chapters = ref([])
const selectedChapter = ref(null)
const videoRef = ref(null)
const progressMap = reactive({})
const maxWatchedMap = reactive({})
let progressTimer = null

const orderedChapters = computed(() => [...chapters.value].sort((a, b) => chapterOrder(a) - chapterOrder(b)))
const currentProgress = computed(() => (selectedChapter.value ? chapterProgress(selectedChapter.value) : { percent: 0, watched_seconds: 0, is_completed: false }))
const overallProgress = computed(() => {
  const raw = course.value?.progress ?? course.value?.course_progress ?? progressMap.__course__?.progress ?? progressMap.__course__?.percent ?? 0
  return Math.max(0, Math.min(100, Math.round(Number(raw) || 0)))
})
const selectedVideoUrl = computed(() => (selectedChapter.value ? chapterVideoUrl(selectedChapter.value) : ''))
const selectedMaterialId = computed(() => (selectedChapter.value ? materialId(selectedChapter.value) : ''))

function chapterOrder(chapter) {
  return chapter.order ?? chapter.order_no ?? 0
}

function chapterVideoUrl(chapter) {
  const video = chapter.video
  return chapter.video_url || video?.url || video?.file_url || video?.video_url || (typeof video === 'string' ? video : '')
}

function materialId(chapter) {
  const material = chapter.material || chapter.materials?.[0]
  return chapter.material_id || material?.id || ''
}

function materialName(chapter) {
  const material = chapter.material || chapter.materials?.[0]
  return material?.original_name || material?.file_name || material?.name || `${chapter.title || '学习资料'}`
}

function chapterProgress(chapter) {
  const data = progressMap[chapter.id] || {}
  return {
    watched_seconds: Math.max(Number(data.watched_seconds) || 0, maxWatchedMap[chapter.id] || 0),
    percent: Math.max(0, Math.min(100, Math.round(Number(data.percent) || 0))),
    is_completed: Boolean(data.is_completed)
  }
}

function applyProgressData(data) {
  const courseProgress = data?.course || data?.course_progress || data?.enrollment || data
  progressMap.__course__ = {
    progress: courseProgress?.progress ?? courseProgress?.percent ?? data?.progress ?? 0
  }

  const chapterItems = data?.chapters || data?.chapter_progress || data?.results || []
  chapterItems.forEach((item) => {
    const chapterId = item.chapter_id || item.chapter?.id || item.id
    if (!chapterId) return
    progressMap[chapterId] = {
      watched_seconds: item.watched_seconds || 0,
      percent: item.percent || 0,
      is_completed: item.is_completed || false
    }
    maxWatchedMap[chapterId] = Math.max(maxWatchedMap[chapterId] || 0, Number(item.watched_seconds) || 0)
  })
}

async function loadPage() {
  loading.value = true
  try {
    const [courseData, chapterData, progressData] = await Promise.all([
      fetchCourseDetail(courseId.value),
      fetchChapters(courseId.value),
      fetchCourseProgress(courseId.value)
    ])
    course.value = courseData
    chapters.value = Array.isArray(chapterData) ? chapterData : chapterData?.results || []
    applyProgressData(progressData || {})
    selectedChapter.value = orderedChapters.value[0] || null
    await nextTick()
    restoreVideoPosition()
  } catch (error) {
    ElMessage.error(getCommonErrorMessage(error, '学习页加载失败'))
  } finally {
    loading.value = false
  }
}

async function selectChapter(chapter) {
  await submitCurrentProgress()
  selectedChapter.value = chapter
  await nextTick()
  restoreVideoPosition()
}

function restoreVideoPosition() {
  if (!videoRef.value || !selectedChapter.value) return
  const watched = chapterProgress(selectedChapter.value).watched_seconds
  if (watched > 0) {
    videoRef.value.currentTime = watched
  }
}

function handleLoadedMetadata() {
  restoreVideoPosition()
}

function handleTimeUpdate() {
  if (!selectedChapter.value || !videoRef.value) return
  const chapterId = selectedChapter.value.id
  const currentTime = Math.floor(videoRef.value.currentTime || 0)
  maxWatchedMap[chapterId] = Math.max(maxWatchedMap[chapterId] || 0, currentTime)
  const duration = Math.floor(videoRef.value.duration || selectedChapter.value.video_duration || 0)
  const percent = duration > 0 ? Math.min(100, Math.round((maxWatchedMap[chapterId] / duration) * 100)) : chapterProgress(selectedChapter.value).percent
  progressMap[chapterId] = {
    ...chapterProgress(selectedChapter.value),
    watched_seconds: maxWatchedMap[chapterId],
    percent
  }
}

function startProgressTimer() {
  stopProgressTimer()
  progressTimer = window.setInterval(() => {
    submitCurrentProgress()
  }, 20000)
}

function stopProgressTimer() {
  if (progressTimer) {
    window.clearInterval(progressTimer)
    progressTimer = null
  }
}

async function submitCurrentProgress(isCompleted = false) {
  if (!selectedChapter.value) return
  const chapterId = selectedChapter.value.id
  const localProgress = chapterProgress(selectedChapter.value)
  const watchedSeconds = Math.max(localProgress.watched_seconds, maxWatchedMap[chapterId] || 0)
  const duration = Math.floor(videoRef.value?.duration || selectedChapter.value.video_duration || 0)
  const percent = isCompleted ? 100 : duration > 0 ? Math.min(100, Math.round((watchedSeconds / duration) * 100)) : localProgress.percent

  submitting.value = true
  try {
    const result = await updateLearningProgress({
      course_id: Number(courseId.value),
      chapter_id: chapterId,
      watched_seconds: watchedSeconds,
      percent,
      is_completed: isCompleted || percent >= 95 || localProgress.is_completed
    })
    progressMap[chapterId] = {
      watched_seconds: watchedSeconds,
      percent,
      is_completed: isCompleted || percent >= 95 || localProgress.is_completed
    }
    if (result) applyProgressData(result)
  } catch (error) {
    ElMessage.error(getCommonErrorMessage(error, '进度保存失败'))
  } finally {
    submitting.value = false
  }
}

async function handleEnded() {
  stopProgressTimer()
  await submitCurrentProgress(true)
  ElMessage.success('本章已完成')
}

async function markCompleted() {
  await submitCurrentProgress(true)
  ElMessage.success('已标记完成')
}

async function handleDownloadMaterial() {
  if (!selectedMaterialId.value || !selectedChapter.value) return
  downloading.value = true
  try {
    const blob = await downloadMaterial(selectedMaterialId.value)
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = materialName(selectedChapter.value)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  } catch (error) {
    ElMessage.error(getCommonErrorMessage(error, '资料下载失败，请确认已加入课程'))
  } finally {
    downloading.value = false
  }
}

function handleBeforeUnload() {
  if (!selectedChapter.value) return
  submitCurrentProgress()
}

onMounted(() => {
  loadPage()
  window.addEventListener('beforeunload', handleBeforeUnload)
})

onBeforeRouteLeave(async () => {
  stopProgressTimer()
  await submitCurrentProgress()
})

onBeforeUnmount(() => {
  stopProgressTimer()
  window.removeEventListener('beforeunload', handleBeforeUnload)
  submitCurrentProgress()
})
</script>

<style scoped>
.learn-shell {
  max-width: 1220px;
  min-height: 420px;
  margin: 54px auto 0;
}

.learn-header {
  position: relative;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 280px;
  gap: 28px;
  align-items: center;
  padding: 30px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid rgba(99, 102, 241, 0.12);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-soft);
}

.learn-header > * {
  position: relative;
  z-index: 1;
}

.learn-header h1 {
  margin: 0;
  font-size: clamp(34px, 5vw, 52px);
}

.learn-header p:last-child {
  color: var(--slate-600);
  line-height: 1.75;
}

.progress-card {
  display: grid;
  gap: 10px;
  padding: 20px;
  background: var(--white);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-card);
}

.progress-card span {
  color: var(--slate-500);
  font-weight: 800;
}

.progress-card strong {
  font-size: 42px;
}

.learn-layout {
  display: grid;
  grid-template-columns: 320px minmax(0, 1fr);
  gap: 18px;
  margin-top: 18px;
}

.chapter-sidebar,
.player-panel {
  padding: 18px;
}

.sidebar-title,
.player-heading {
  display: flex;
  gap: 14px;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 16px;
}

.sidebar-title h2,
.player-heading h2 {
  margin: 0;
}

.sidebar-title span,
.player-heading p {
  color: var(--slate-500);
}

.chapter-button {
  display: grid;
  grid-template-columns: 42px minmax(0, 1fr);
  gap: 12px;
  width: 100%;
  padding: 12px;
  margin-bottom: 10px;
  text-align: left;
  cursor: pointer;
  background: #fbfaff;
  border: 1px solid rgba(99, 102, 241, 0.1);
  border-radius: var(--radius-md);
}

.chapter-button.is-active {
  border-color: rgba(99, 102, 241, 0.4);
  box-shadow: 0 10px 22px rgba(99, 102, 241, 0.12);
}

.chapter-no {
  display: grid;
  place-items: center;
  width: 36px;
  height: 36px;
  color: var(--white);
  background: var(--gradient-primary);
  border-radius: 10px;
  font-weight: 900;
}

.chapter-button strong,
.chapter-button small {
  display: block;
}

.chapter-button small {
  margin-top: 4px;
  color: var(--slate-500);
}

.video-box {
  overflow: hidden;
  background: #141326;
  border-radius: var(--radius-lg);
}

video,
.empty-video {
  display: block;
  width: 100%;
  aspect-ratio: 16 / 9;
}

.empty-video {
  display: grid;
  place-items: center;
  color: rgba(255, 255, 255, 0.72);
  font-weight: 800;
}

.chapter-tools {
  display: grid;
  gap: 14px;
  margin-top: 18px;
}

.tool-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

@media (max-width: 980px) {
  .learn-header,
  .learn-layout {
    grid-template-columns: 1fr;
  }
}
</style>
