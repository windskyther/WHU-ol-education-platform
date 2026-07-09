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
          <span class="corner corner-tl"></span>
          <span class="corner corner-tr"></span>
          <span class="corner corner-bl"></span>
          <span class="corner corner-br"></span>

          <div class="certificate-seal">🎖️</div>
          <p class="certificate-eyebrow">CERTIFICATE OF EXCELLENCE</p>
          <h1 class="certificate-title">优秀学员证书</h1>
          <div class="certificate-divider"><span></span></div>

          <p class="certificate-body">
            兹证明 <strong class="highlight">{{ certificate.student_name }}</strong> 同学
            在课程《<strong>{{ certificate.course_title }}</strong>》的
            <strong>{{ certificate.exam_title }}</strong> 中
            取得 <strong class="highlight">{{ certificate.score }}</strong> 分的优异成绩
            （优秀线 {{ certificate.excellent_score }} 分），特发此证，以资鼓励。
          </p>

          <div class="certificate-meta-row">
            <div class="certificate-meta-item">
              <span class="value">{{ certificate.teacher_name }}</span>
              <span class="signature-line"></span>
              <span class="label">授课教师</span>
            </div>
            <div class="certificate-meta-item">
              <span class="value">{{ formatDate(certificate.issued_at) }}</span>
              <span class="signature-line"></span>
              <span class="label">颁发日期</span>
            </div>
          </div>

          <div class="certificate-footer">
            <span>证书编号：{{ certificate.cert_no }}</span>
            <span class="brand">WHU 在线教育平台</span>
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
  background: linear-gradient(135deg, var(--green-100, #e8f6ee), var(--mint-050, #f6fbf8));
  border-radius: 10px;
  padding: 16px;
  box-shadow: 0 16px 40px rgba(47, 111, 78, 0.12);
}

.certificate-border {
  position: relative;
  border: 2px solid var(--green-500, #5ca982);
  border-radius: 6px;
  padding: 64px 56px;
  text-align: center;
  background:
    radial-gradient(circle at 50% 0%, rgba(92, 169, 130, 0.06), transparent 60%),
    repeating-linear-gradient(45deg, rgba(92, 169, 130, 0.035) 0 2px, transparent 2px 18px),
    #fffefb;
}

.corner {
  position: absolute;
  width: 28px;
  height: 28px;
  border: 3px solid var(--green-500, #5ca982);
}

.corner-tl {
  top: 10px;
  left: 10px;
  border-right: none;
  border-bottom: none;
}

.corner-tr {
  top: 10px;
  right: 10px;
  border-left: none;
  border-bottom: none;
}

.corner-bl {
  bottom: 10px;
  left: 10px;
  border-right: none;
  border-top: none;
}

.corner-br {
  bottom: 10px;
  right: 10px;
  border-left: none;
  border-top: none;
}

.certificate-seal {
  font-size: 44px;
  margin-bottom: 4px;
  filter: drop-shadow(0 4px 8px rgba(47, 111, 78, 0.25));
}

.certificate-eyebrow {
  letter-spacing: 5px;
  font-size: 12px;
  font-weight: 800;
  color: var(--green-500, #5ca982);
  margin: 0 0 10px;
}

.certificate-title {
  font-size: 36px;
  font-weight: 900;
  font-family: 'Songti SC', 'STSong', serif;
  color: var(--ink-900, #10251a);
  margin: 0;
  letter-spacing: 4px;
}

.certificate-divider {
  display: flex;
  justify-content: center;
  margin: 18px 0 32px;
}

.certificate-divider span {
  width: 120px;
  height: 3px;
  border-radius: 2px;
  background: linear-gradient(90deg, transparent, var(--green-500, #5ca982), transparent);
}

.certificate-body {
  font-size: 16px;
  line-height: 2.1;
  color: var(--ink-900, #10251a);
  max-width: 620px;
  margin: 0 auto 44px;
}

.certificate-body .highlight {
  color: var(--green-700, #2f6f4e);
  font-size: 19px;
}

.certificate-meta-row {
  display: flex;
  justify-content: center;
  gap: 96px;
  margin-bottom: 40px;
}

.certificate-meta-item {
  display: grid;
  gap: 8px;
  justify-items: center;
}

.certificate-meta-item .value {
  font-size: 17px;
  font-weight: 900;
  color: var(--ink-900, #10251a);
  font-family: 'Songti SC', 'STSong', serif;
}

.signature-line {
  width: 140px;
  height: 1px;
  background: var(--green-300, #a8d8bc);
}

.certificate-meta-item .label {
  font-size: 12px;
  color: var(--muted);
  font-weight: 700;
}

.certificate-footer {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--muted);
  border-top: 1px dashed var(--green-300, #a8d8bc);
  padding-top: 16px;
}

.certificate-footer .brand {
  font-weight: 800;
  color: var(--green-500, #5ca982);
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
    box-shadow: none;
    padding: 0;
  }

  .certificate-border {
    border: 2px solid #2f6f4e;
    background: #fff;
  }
}
</style>
