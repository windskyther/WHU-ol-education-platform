<template>
  <main class="page-shell learn-page">
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

    <section v-loading="loading" class="learn-workspace">
      <template v-if="course">
        <header class="learn-titlebar">
          <div>
            <p class="eyebrow">Learning room</p>
            <h1>{{ course.title }}</h1>
            <p>{{ course.description || '选择章节开始学习，系统会自动保存观看进度。' }}</p>
          </div>
          <div class="course-progress">
            <span>课程进度</span>
            <strong>{{ overallProgress }}%</strong>
            <el-progress :percentage="overallProgress" :stroke-width="10" />
          </div>
        </header>

        <div class="study-grid">
          <section class="player-workbench">
            <template v-if="selectedChapter">
              <div class="now-row">
                <div>
                  <p class="eyebrow">Now playing</p>
                  <h2>{{ selectedChapter.title }}</h2>
                  <p>{{ selectedChapter.description || '暂无章节简介' }}</p>
                </div>
                <span class="status-pill" :class="{ 'is-done': currentProgress.is_completed }">
                  {{ currentProgress.is_completed ? '已完成' : `${currentProgress.percent}%` }}
                </span>
              </div>

              <div class="video-stage">
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
                  @pause="submitCurrentProgress()"
                  @ended="handleEnded"
                ></video>
                <div v-else class="empty-video">本章暂未上传视频</div>
              </div>

              <div class="progress-console">
                <div>
                  <span>本章进度</span>
                  <el-progress :percentage="currentProgress.percent" :stroke-width="10" />
                </div>
                <div class="tool-actions">
                  <el-button :loading="submitting" @click="submitCurrentProgress()">保存进度</el-button>
                  <el-button type="primary" :loading="submitting" @click="markCompleted">标记完成</el-button>
                  <el-button v-if="selectedMaterialId" plain :loading="downloading" @click="handleDownloadMaterial">下载资料</el-button>
                </div>
              </div>
            </template>
            <div v-else class="empty-state">暂无可学习章节</div>
          </section>

          <aside class="chapter-rail">
            <div class="rail-heading">
              <div>
                <p class="eyebrow">Chapter rail</p>
                <h2>章节</h2>
              </div>
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
              <span class="chapter-copy">
                <strong>{{ chapter.title }}</strong>
                <small>{{ chapterProgress(chapter).percent }}% · {{ chapterProgress(chapter).is_completed ? '已完成' : '学习中' }}</small>
              </span>
            </button>
          </aside>
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
import { normalizeMediaUrl } from '../../utils/mediaUrl'

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
  const url = chapter.video_url || video?.url || video?.file_url || video?.video_url || (typeof video === 'string' ? video : '')
  return normalizeMediaUrl(url)
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
  const completed = isCompleted === true
  const chapterId = selectedChapter.value.id
  const localProgress = chapterProgress(selectedChapter.value)
  const watchedSeconds = Math.max(localProgress.watched_seconds, maxWatchedMap[chapterId] || 0)
  const duration = Math.floor(videoRef.value?.duration || selectedChapter.value.video_duration || 0)
  const percent = completed ? 100 : duration > 0 ? Math.min(100, Math.round((watchedSeconds / duration) * 100)) : localProgress.percent

  submitting.value = true
  try {
    const isProgressCompleted = completed || percent >= 95 || localProgress.is_completed
    const result = await updateLearningProgress({
      course_id: Number(courseId.value),
      chapter_id: chapterId,
      watched_seconds: watchedSeconds,
      percent,
      is_completed: isProgressCompleted
    })
    progressMap[chapterId] = {
      watched_seconds: watchedSeconds,
      percent,
      is_completed: isProgressCompleted
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
.learn-page {
  background:
    radial-gradient(circle at 16% 8%, rgba(99, 102, 241, 0.2), transparent 28%),
    radial-gradient(circle at 86% 10%, rgba(139, 92, 246, 0.16), transparent 30%),
    linear-gradient(180deg, #ffffff 0, #f5f4ff 380px, #fafafa 100%);
}

.learn-workspace {
  max-width: 1280px;
  min-height: 520px;
  margin: 38px auto 0;
}

.learn-titlebar {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 280px;
  gap: 24px;
  align-items: stretch;
  padding: 30px;
  color: var(--white);
  background:
    linear-gradient(135deg, rgba(99, 102, 241, 0.96), rgba(139, 92, 246, 0.92)),
    #6366f1;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-soft);
}

.learn-titlebar .eyebrow {
  color: rgba(255, 255, 255, 0.76) !important;
}

.learn-titlebar h1 {
  max-width: 820px;
  margin: 0;
  font-size: clamp(34px, 5vw, 58px);
  line-height: 1.06;
}

.learn-titlebar p:last-child {
  max-width: 760px;
  margin: 14px 0 0;
  color: rgba(255, 255, 255, 0.84);
  line-height: 1.75;
}

.course-progress {
  display: grid;
  gap: 10px;
  align-content: center;
  padding: 22px;
  color: var(--ink-900);
  background: rgba(255, 255, 255, 0.96);
  border-radius: var(--radius-md);
}

.course-progress span {
  color: var(--slate-500);
  font-weight: 900;
}

.course-progress strong {
  font-size: 42px;
  line-height: 1;
}

.study-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 340px;
  gap: 18px;
  margin-top: 18px;
}

.player-workbench,
.chapter-rail {
  background: rgba(255, 255, 255, 0.96);
  border: 1px solid rgba(99, 102, 241, 0.12);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
}

.player-workbench {
  display: grid;
  gap: 18px;
  align-content: start;
  padding: 18px;
}

.now-row {
  display: flex;
  gap: 18px;
  align-items: flex-start;
  justify-content: space-between;
  padding: 10px 8px 0;
}

.now-row h2 {
  margin: 0;
  font-size: 30px;
}

.now-row p:last-child {
  max-width: 780px;
  margin: 8px 0 0;
  color: var(--slate-600);
  line-height: 1.7;
}

.video-stage {
  overflow: hidden;
  background: #111124;
  border-radius: var(--radius-lg);
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.08);
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
  font-weight: 900;
}

.progress-console {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 18px;
  align-items: center;
  padding: 18px;
  background: #fbfaff;
  border: 1px solid rgba(99, 102, 241, 0.1);
  border-radius: var(--radius-md);
}

.progress-console span {
  display: block;
  margin-bottom: 8px;
  color: var(--slate-500);
  font-weight: 900;
}

.tool-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: flex-end;
}

.chapter-rail {
  align-self: start;
  max-height: calc(100vh - 150px);
  padding: 18px;
  overflow: auto;
}

.rail-heading {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 16px;
}

.rail-heading h2 {
  margin: 0;
  font-size: 26px;
}

.rail-heading > span {
  color: var(--slate-500);
  font-weight: 900;
}

.chapter-button {
  display: grid;
  grid-template-columns: 40px minmax(0, 1fr);
  gap: 12px;
  width: 100%;
  padding: 12px;
  margin-bottom: 10px;
  color: var(--ink-900);
  text-align: left;
  cursor: pointer;
  background: #fbfaff;
  border: 1px solid rgba(99, 102, 241, 0.1);
  border-radius: var(--radius-md);
  transition:
    border-color 0.18s ease,
    box-shadow 0.18s ease,
    transform 0.18s ease;
}

.chapter-button:hover,
.chapter-button.is-active {
  border-color: rgba(99, 102, 241, 0.36);
  box-shadow: 0 10px 24px rgba(99, 102, 241, 0.12);
  transform: translateY(-1px);
}

.chapter-button.is-active {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.12), rgba(139, 92, 246, 0.08));
}

.chapter-no {
  display: grid;
  place-items: center;
  width: 36px;
  height: 36px;
  color: var(--white);
  background: var(--gradient-primary);
  border-radius: var(--radius-sm);
  font-weight: 900;
}

.chapter-copy {
  min-width: 0;
}

.chapter-copy strong,
.chapter-copy small {
  display: block;
}

.chapter-copy strong {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.chapter-copy small {
  margin-top: 4px;
  color: var(--slate-500);
  font-weight: 800;
}

@media (max-width: 980px) {
  .learn-titlebar,
  .study-grid,
  .progress-console {
    grid-template-columns: 1fr;
  }

  .chapter-rail {
    max-height: none;
  }

  .tool-actions {
    justify-content: flex-start;
  }
}
</style>
