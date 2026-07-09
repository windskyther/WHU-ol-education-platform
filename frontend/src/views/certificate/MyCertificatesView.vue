<template>
  <main class="page-shell certificates-page">
    <AppNav />

    <section class="certificates-workspace">
      <header class="manager-heading kinetic-panel">
        <div>
          <p class="eyebrow">Certificate wall</p>
          <h1>我的证书</h1>
          <p>考试成绩达到课程设置的优秀线后，系统会自动为你颁发对应证书。</p>
        </div>
      </header>

      <section class="surface table-panel">
        <div v-loading="loading" class="certificate-grid">
          <RouterLink
            v-for="cert in certificates"
            :key="cert.id"
            :to="`/certificates/${cert.cert_no}`"
            class="certificate-card"
          >
            <div class="certificate-card-inner">
              <span class="certificate-card-seal">🎖️</span>
              <p class="certificate-card-eyebrow">CERTIFICATE OF EXCELLENCE</p>
              <h3 class="certificate-card-course">{{ cert.course_title }}</h3>
              <p class="certificate-card-exam">{{ cert.exam_title }}</p>
              <p class="certificate-card-student">{{ cert.student_name }}</p>
              <div class="certificate-card-meta">
                <span>{{ cert.score }} 分</span>
                <span>{{ formatTime(cert.issued_at) }}</span>
              </div>
              <div class="certificate-card-no">{{ cert.cert_no }}</div>
            </div>
            <div class="certificate-card-hint">点击查看完整证书</div>
          </RouterLink>
        </div>

        <div v-if="!loading && certificates.length === 0" class="empty-state">
          暂无证书，参加课程考试并达到优秀线即可自动获得证书。
        </div>
        <PaginationBar :total="total" :page="page" :page-size="pageSize" @change="loadCertificates" />
      </section>
    </section>
  </main>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import AppNav from '../../components/AppNav.vue'
import PaginationBar from '../../components/PaginationBar.vue'
import { fetchMyCertificates } from '../../api/certificate'
import { getCommonErrorMessage } from '../../utils/errorMessage'

const loading = ref(false)
const certificates = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(12)

function normalizeList(data) {
  if (Array.isArray(data)) return data
  return data?.results || []
}

function formatTime(value) {
  if (!value) return '-'
  return new Date(value).toLocaleDateString('zh-CN')
}

async function loadCertificates(nextPage = page.value) {
  loading.value = true
  try {
    const data = await fetchMyCertificates({ page: nextPage, page_size: pageSize.value })
    certificates.value = normalizeList(data)
    total.value = data?.count || certificates.value.length
    page.value = data?.page || nextPage
    pageSize.value = data?.page_size || pageSize.value
  } catch (error) {
    ElMessage.error(getCommonErrorMessage(error, '证书加载失败'))
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadCertificates(1)
})
</script>

<style scoped>
.certificates-workspace {
  margin: 64px auto 0;
}

.manager-heading {
  display: grid;
  align-content: end;
  min-height: 340px;
  padding: 42px;
}

.manager-heading h1,
.manager-heading p {
  color: var(--paper);
}

.manager-heading p:not(.eyebrow) {
  max-width: 680px;
  color: rgba(246, 241, 230, 0.72);
}

.table-panel {
  margin-top: 18px;
  padding: 18px;
}

.certificate-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 20px;
  min-height: 120px;
}

.certificate-card {
  display: grid;
  gap: 0;
  text-decoration: none;
  border-radius: 8px;
  overflow: hidden;
  background: var(--mint-050, #f6fbf8);
  border: 1px solid var(--green-300, #a8d8bc);
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.certificate-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 24px rgba(47, 111, 78, 0.16);
}

.certificate-card-inner {
  display: grid;
  justify-items: center;
  gap: 4px;
  text-align: center;
  padding: 24px 18px 18px;
  background:
    repeating-linear-gradient(135deg, rgba(92, 169, 130, 0.05) 0 2px, transparent 2px 14px),
    #ffffff;
  border: 2px double var(--green-500, #5ca982);
  margin: 10px;
  border-radius: 4px;
}

.certificate-card-seal {
  font-size: 26px;
  margin-bottom: 2px;
}

.certificate-card-eyebrow {
  margin: 0;
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 2px;
  color: var(--green-500, #5ca982);
}

.certificate-card-course {
  margin: 6px 0 0;
  font-size: 16px;
  font-weight: 900;
  color: var(--ink-900, #10251a);
}

.certificate-card-exam {
  margin: 0;
  color: var(--muted);
  font-size: 12px;
  font-weight: 700;
}

.certificate-card-student {
  margin: 6px 0 0;
  font-size: 14px;
  font-weight: 900;
  color: var(--green-700, #2f6f4e);
}

.certificate-card-meta {
  display: flex;
  justify-content: center;
  gap: 14px;
  margin-top: 8px;
  font-size: 12px;
  color: var(--green-700, #2f6f4e);
  font-weight: 800;
}

.certificate-card-no {
  margin-top: 6px;
  font-size: 10px;
  color: var(--muted);
  letter-spacing: 0.5px;
}

.certificate-card-hint {
  text-align: center;
  padding: 8px 0 12px;
  font-size: 12px;
  font-weight: 700;
  color: var(--green-700, #2f6f4e);
  background: var(--green-100, #e8f6ee);
}
</style>
