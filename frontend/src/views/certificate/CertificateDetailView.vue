<template>
  <main class="page-shell certificate-detail-page">
    <AppNav class="no-print" />

    <section class="certificate-detail-workspace">
      <div v-loading="loading" class="detail-actions no-print">
        <el-button text @click="$router.push('/certificates')">返回我的证书</el-button>
        <el-button type="primary" :disabled="!certificate" @click="handlePrint">打印 / 保存为 PDF</el-button>
      </div>

      <section v-if="certificate" class="certificate-sheet">
        <div class="certificate-border">
          <p class="certificate-eyebrow">CERTIFICATE OF EXCELLENCE</p>
          <h1 class="certificate-title">优秀学员证书</h1>
          <p class="certificate-body">
            兹证明 <strong>{{ certificate.student_name }}</strong> 同学
            在课程《<strong>{{ certificate.course_title }}</strong>》的
            <strong>{{ certificate.exam_title }}</strong> 中
            取得 <strong>{{ certificate.score }}</strong> 分的优异成绩
            （优秀线 {{ certificate.excellent_score }} 分），特发此证，以资鼓励。
          </p>

          <div class="certificate-meta-row">
            <div class="certificate-meta-item">
              <span class="label">授课教师</span>
              <span class="value">{{ certificate.teacher_name }}</span>
            </div>
            <div class="certificate-meta-item">
              <span class="label">颁发日期</span>
              <span class="value">{{ formatDate(certificate.issued_at) }}</span>
            </div>
          </div>

          <div class="certificate-footer">
            <span>证书编号：{{ certificate.cert_no }}</span>
            <span>WHU 在线教育平台</span>
          </div>
        </div>
      </section>

      <div v-else-if="!loading" class="empty-state no-print">未找到该证书，或你没有权限查看。</div>
    </section>
  </main>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import AppNav from '../../components/AppNav.vue'
import { fetchCertificateDetail } from '../../api/certificate'
import { getCommonErrorMessage } from '../../utils/errorMessage'

const route = useRoute()
const loading = ref(false)
const certificate = ref(null)

function formatDate(value) {
  if (!value) return '-'
  return new Date(value).toLocaleDateString('zh-CN')
}

function handlePrint() {
  window.print()
}

async function loadCertificate() {
  loading.value = true
  try {
    certificate.value = await fetchCertificateDetail(route.params.certNo)
  } catch (error) {
    certificate.value = null
    ElMessage.error(getCommonErrorMessage(error, '证书加载失败'))
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadCertificate()
})
</script>

<style scoped>
.certificate-detail-workspace {
  margin: 64px auto 0;
  max-width: 860px;
  padding: 0 16px 60px;
}

.detail-actions {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}

.certificate-sheet {
  background: var(--mint-050, #f6fbf8);
  border-radius: 8px;
  padding: 12px;
}

.certificate-border {
  border: 3px double var(--green-500, #5ca982);
  border-radius: 6px;
  padding: 56px 48px;
  text-align: center;
  background: #fff;
}

.certificate-eyebrow {
  letter-spacing: 4px;
  font-size: 12px;
  font-weight: 800;
  color: var(--green-500, #5ca982);
  margin: 0 0 12px;
}

.certificate-title {
  font-size: 32px;
  font-weight: 900;
  color: var(--ink-900, #10251a);
  margin: 0 0 32px;
}

.certificate-body {
  font-size: 16px;
  line-height: 2;
  color: var(--ink-900, #10251a);
  max-width: 620px;
  margin: 0 auto 40px;
}

.certificate-meta-row {
  display: flex;
  justify-content: center;
  gap: 64px;
  margin-bottom: 40px;
}

.certificate-meta-item {
  display: grid;
  gap: 6px;
}

.certificate-meta-item .label {
  font-size: 12px;
  color: var(--muted);
  font-weight: 700;
}

.certificate-meta-item .value {
  font-size: 16px;
  font-weight: 900;
  color: var(--green-700, #2f6f4e);
}

.certificate-footer {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--muted);
  border-top: 1px dashed var(--green-300, #a8d8bc);
  padding-top: 16px;
}

@media print {
  .no-print {
    display: none !important;
  }

  .certificate-detail-workspace {
    margin: 0;
    max-width: none;
    padding: 0;
  }

  .certificate-sheet {
    background: none;
    padding: 0;
  }

  .certificate-border {
    border: 3px double #2f6f4e;
  }
}
</style>
