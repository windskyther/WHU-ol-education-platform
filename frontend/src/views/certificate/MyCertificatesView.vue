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
            <div class="certificate-card-badge">🏆</div>
            <h3>{{ cert.course_title }}</h3>
            <p class="certificate-card-exam">{{ cert.exam_title }}</p>
            <div class="certificate-card-meta">
              <span>分数 {{ cert.score }}</span>
              <span>{{ formatTime(cert.issued_at) }}</span>
            </div>
            <div class="certificate-card-no">{{ cert.cert_no }}</div>
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
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 16px;
  min-height: 120px;
}

.certificate-card {
  display: grid;
  gap: 6px;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid var(--green-300, #a8d8bc);
  background: var(--mint-050, #f6fbf8);
  text-decoration: none;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.certificate-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(47, 111, 78, 0.12);
}

.certificate-card-badge {
  font-size: 28px;
}

.certificate-card h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 900;
  color: var(--ink-900, #10251a);
}

.certificate-card-exam {
  margin: 0;
  color: var(--muted);
  font-size: 13px;
  font-weight: 700;
}

.certificate-card-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--green-700, #2f6f4e);
  font-weight: 800;
}

.certificate-card-no {
  font-size: 11px;
  color: var(--muted);
  letter-spacing: 0.5px;
}
</style>
