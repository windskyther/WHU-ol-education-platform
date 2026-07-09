<template>
  <main class="page-shell learn-page">
    <AppNav />

    <BreadcrumbNav :items="breadcrumbItems" />

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
                  @pause="handleVideoPause"
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
                  <el-button :disabled="submitting" @click="submitCurrentProgress()">保存进度</el-button>
                  <el-button type="primary" :disabled="submitting" @click="markCompleted">标记完成</el-button>
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
                <h2>Index</h2>
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

        <CourseQuestionPanel
          :course-id="courseId"
          can-ask
          heading="Learning questions"
        />
      </template>
    </section>
  </main>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { onBeforeRouteLeave, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import AppNav from '../../components/AppNav.vue'
import BreadcrumbNav from '../../components/BreadcrumbNav.vue'
import CourseQuestionPanel from '../../components/CourseQuestionPanel.vue'
import { downloadMaterial, fetchChapters, fetchCourseDetail, fetchCourseProgress, updateLearningProgress } from '../../api/course'
import { getCommonErrorMessage } from '../../utils/errorMessage'
import { normalizeMediaUrl } from '../../utils/mediaUrl'

const route = useRoute()
const courseId = String(route.params.courseId || '')
const loading = ref(false)
const submitting = ref(false)
const downloading = ref(false)
const isLeaving = ref(false)
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
  const raw = progressMap.__course__?.progress ?? progressMap.__course__?.percent ?? course.value?.progress ?? course.value?.course_progress ?? 0
  return Math.max(0, Math.min(100, Math.round(Number(raw) || 0)))
})
const selectedVideoUrl = computed(() => (selectedChapter.value ? chapterVideoUrl(selectedChapter.value) : ''))
const selectedMaterialId = computed(() => (selectedChapter.value ? materialId(selectedChapter.value) : ''))

const breadcrumbItems = computed(() => [
  { label: '我的课程', to: '/student/courses' },
  { label: course.value?.title || '课程学习', to: `/courses/${courseId}` },
  { label: '学习' }
])

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
  return chapter.material_id || material?.id || chapter.material?.material_id || material?.material_id || ''
}

function materialName(chapter) {
  const material = chapter.material || chapter.materials?.[0]
  return material?.original_name || material?.file_name || material?.name || material?.filename || `${chapter.title || '学习资料'}`
}

function chapterProgress(chapter) {
  const data = progressMap[chapter.id] || {}
  return {
    watched_seconds: Math.max(Number(data.watched_seconds) || 0, maxWatchedMap[chapter.id] || 0),
    percent: Math.max(0, Math.min(100, Math.round(Number(data.percent) || 0))),
    is_completed: Boolean(data.is_completed)
  }
}

function applyChapterProgressItem(item) {
  const chapterId = item?.chapter_id || item?.chapter?.id || item?.id
  if (!chapterId) return

  progressMap[chapterId] = {
    watched_seconds: item.watched_seconds || 0,
    percent: item.percent || 0,
    is_completed: item.is_completed || false
  }
  maxWatchedMap[chapterId] = Math.max(maxWatchedMap[chapterId] || 0, Number(item.watched_seconds) || 0)
}

function applyProgressData(data) {
  progressMap.__course__ = {
    progress: data?.progress ?? data?.enrollment?.progress ?? data?.course_progress?.progress ?? 0
  }

  const chapterItems = data?.chapter_progress || data?.progress_items || data?.results || data?.chapters || []
  chapterItems.forEach(applyChapterProgressItem)
}

function applyProgressUpdateResult(result, fallbackChapterId) {
  if (!result) return

  if (result.progress !== undefined) {
    progressMap.__course__ = {
      progress: result.progress
    }
  }

  if (result.progress_item) {
    applyChapterProgressItem({
      ...result.progress_item,
      chapter_id: result.progress_item.chapter_id || result.progress_item.chapter?.id || fallbackChapterId
    })
  }

  if (Array.isArray(result.chapter_progress)) {
    result.chapter_progress.forEach(applyChapterProgressItem)
  }
}

async function loadPage() {
  loading.value = true
  try {
    const [courseData, chapterData, progressData] = await Promise.all([
      fetchCourseDetail(courseId),
      fetchChapters(courseId),
      fetchCourseProgress(courseId)
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

async function submitCurrentProgress(isCompleted = false, options = {}) {
  if (submitting.value) return
  if (!selectedChapter.value) return
  const completed = isCompleted === true
  const numericCourseId = Number(courseId)
  if (!Number.isFinite(numericCourseId) || numericCourseId <= 0) return
  const chapterId = selectedChapter.value.id
  const localProgress = chapterProgress(selectedChapter.value)
  const watchedSeconds = Math.max(localProgress.watched_seconds, maxWatchedMap[chapterId] || 0)
  const duration = Math.floor(videoRef.value?.duration || selectedChapter.value.video_duration || 0)
  const percent = completed ? 100 : duration > 0 ? Math.min(100, Math.round((watchedSeconds / duration) * 100)) : localProgress.percent

  submitting.value = true
  try {
    const isProgressCompleted = completed || percent >= 95 || localProgress.is_completed
    const result = await updateLearningProgress({
      course_id: numericCourseId,
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
    applyProgressUpdateResult(result, chapterId)
  } catch (error) {
    if (!options.silent && !isLeaving.value) {
      ElMessage.error(getCommonErrorMessage(error, '进度保存失败'))
    }
  } finally {
    submitting.value = false
  }
}

function handleVideoPause() {
  if (isLeaving.value) return
  submitCurrentProgress()
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
  submitCurrentProgress(false, { silent: true })
}

onMounted(() => {
  loadPage()
  window.addEventListener('beforeunload', handleBeforeUnload)
})

onBeforeRouteLeave(async () => {
  isLeaving.value = true
  stopProgressTimer()
  await submitCurrentProgress(false, { silent: true })
})

onBeforeUnmount(() => {
  stopProgressTimer()
  window.removeEventListener('beforeunload', handleBeforeUnload)
})
</script>

<style scoped>
.learn-workspace {
  min-height: 520px;
  margin: 54px auto 0;
}

.learn-titlebar {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 260px;
  gap: 24px;
  align-items: end;
  padding: 38px;
  background: rgba(255, 250, 240, 0.88);
  border: 2px solid var(--line);
  border-radius: var(--radius-md);
}

.learn-titlebar h1 {
  max-width: 980px;
}

.learn-titlebar p:last-child {
  max-width: 720px;
  margin: 24px 0 0;
  color: var(--muted);
  font-weight: 800;
}

.course-progress {
  display: grid;
  gap: 12px;
  padding: 20px;
  color: var(--paper);
  background: var(--ink);
  border-radius: var(--radius-md);
}

.course-progress span {
  color: rgba(246, 241, 230, 0.68);
  font-size: 12px;
  font-weight: 900;
  text-transform: uppercase;
}

.course-progress strong {
  font-size: 58px;
  font-weight: 900;
  line-height: 0.85;
  letter-spacing: -0.08em;
}

.study-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 340px;
  gap: 18px;
  margin-top: 18px;
}

.player-workbench,
.chapter-rail {
  background: rgba(255, 250, 240, 0.88);
  border: 2px solid var(--line);
  border-radius: var(--radius-md);
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
  padding: 16px 12px 0;
}

.now-row h2 {
  margin: 0;
  font-size: clamp(36px, 5vw, 78px);
  font-weight: 900;
  line-height: 0.84;
  letter-spacing: -0.075em;
}

.now-row p:last-child {
  max-width: 760px;
  margin: 12px 0 0;
  color: var(--muted);
  font-weight: 800;
}

.video-stage {
  overflow: hidden;
  background: #070706;
  border-radius: var(--radius-md);
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
  color: rgba(246, 241, 230, 0.68);
  font-weight: 900;
}

.progress-console {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 18px;
  align-items: center;
  padding: 18px;
  border-top: 2px solid var(--line);
}

.progress-console span {
  display: block;
  margin-bottom: 8px;
  color: var(--muted);
  font-size: 12px;
  font-weight: 900;
  text-transform: uppercase;
}

.tool-actions {
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
  font-size: 58px;
  font-weight: 900;
  line-height: 0.8;
  letter-spacing: -0.08em;
}

.rail-heading > span {
  color: var(--muted);
  font-weight: 900;
}

.chapter-button {
  display: grid;
  grid-template-columns: 48px minmax(0, 1fr);
  gap: 12px;
  width: 100%;
  padding: 12px 0;
  color: var(--ink);
  text-align: left;
  cursor: pointer;
  background: transparent;
  border: 0;
  border-bottom: 2px solid var(--line);
}

.chapter-button:hover,
.chapter-button.is-active {
  color: var(--hot);
}

.chapter-no {
  font-size: 40px;
  font-weight: 900;
  line-height: 0.8;
  letter-spacing: -0.08em;
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
  font-size: 18px;
  font-weight: 900;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.chapter-copy small {
  margin-top: 6px;
  color: var(--muted);
  font-size: 12px;
  font-weight: 900;
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
