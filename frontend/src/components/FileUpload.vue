<template>
  <div class="file-upload">
    <input ref="inputRef" class="file-input" type="file" :accept="accept" @change="handleFileChange" />
    <el-button :loading="uploading" :disabled="disabled" :icon="Upload" @click="inputRef?.click()">
      {{ displayLabel }}
    </el-button>
    <span v-if="hint" class="hint">{{ hint }}</span>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { useI18n } from 'vue-i18n'
import { Upload } from '@element-plus/icons-vue'
import { getCommonErrorMessage } from '../utils/errorMessage'

const props = defineProps({
  label: {
    type: String,
    default: ''
  },
  hint: {
    type: String,
    default: ''
  },
  accept: {
    type: String,
    default: ''
  },
  allowedExtensions: {
    type: Array,
    default: () => []
  },
  maxSizeMb: {
    type: Number,
    default: 20
  },
  uploadFn: {
    type: Function,
    required: true
  },
  disabled: {
    type: Boolean,
    default: false
  }
})

const { t } = useI18n()
const emit = defineEmits(['uploaded'])
const inputRef = ref()
const uploading = ref(false)
const displayLabel = computed(() => props.label || t('shared.uploadFile'))

function getExtension(fileName) {
  const index = fileName.lastIndexOf('.')
  return index >= 0 ? fileName.slice(index).toLowerCase() : ''
}

function validateFile(file) {
  const extension = getExtension(file.name)
  if (props.allowedExtensions.length && !props.allowedExtensions.includes(extension)) {
    ElMessage.error(t('shared.fileTypeError', { extensions: props.allowedExtensions.join(', ') }))
    return false
  }

  const maxBytes = props.maxSizeMb * 1024 * 1024
  if (file.size > maxBytes) {
    ElMessage.error(t('shared.fileSizeError', { maxSize: props.maxSizeMb }))
    return false
  }

  return true
}

async function handleFileChange(event) {
  const file = event.target.files?.[0]
  event.target.value = ''
  if (!file || !validateFile(file)) return

  uploading.value = true
  try {
    const result = await props.uploadFn(file)
    ElMessage.success(t('shared.uploadSuccess'))
    emit('uploaded', result)
  } catch (error) {
    ElMessage.error(getCommonErrorMessage(error, t('shared.uploadError')))
  } finally {
    uploading.value = false
  }
}
</script>

<style scoped>
.file-upload {
  display: inline-flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.file-input {
  display: none;
}

.hint {
  color: var(--slate-500);
  font-size: 12px;
  font-weight: 700;
}
</style>
