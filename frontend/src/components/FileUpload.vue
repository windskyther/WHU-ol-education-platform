<template>
  <div class="file-upload">
    <input ref="inputRef" class="file-input" type="file" :accept="accept" @change="handleFileChange" />
    <el-button :loading="uploading" :disabled="disabled" :icon="Upload" @click="inputRef?.click()">
      {{ label }}
    </el-button>
    <span v-if="hint" class="hint">{{ hint }}</span>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Upload } from '@element-plus/icons-vue'
import { getCommonErrorMessage } from '../utils/errorMessage'

const props = defineProps({
  label: {
    type: String,
    default: '上传文件'
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

const emit = defineEmits(['uploaded'])
const inputRef = ref()
const uploading = ref(false)

function getExtension(fileName) {
  const index = fileName.lastIndexOf('.')
  return index >= 0 ? fileName.slice(index).toLowerCase() : ''
}

function validateFile(file) {
  const extension = getExtension(file.name)
  if (props.allowedExtensions.length && !props.allowedExtensions.includes(extension)) {
    ElMessage.error(`文件类型不支持，请上传 ${props.allowedExtensions.join('、')}`)
    return false
  }

  const maxBytes = props.maxSizeMb * 1024 * 1024
  if (file.size > maxBytes) {
    ElMessage.error(`文件不能超过 ${props.maxSizeMb} MB`)
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
    ElMessage.success('上传成功')
    emit('uploaded', result)
  } catch (error) {
    ElMessage.error(getCommonErrorMessage(error, '上传失败，请稍后重试'))
  } finally {
    uploading.value = false
  }
}
</script>

<style scoped>
.file-upload {
  display: inline-flex;
  gap: 8px;
  align-items: center;
}

.file-input {
  display: none;
}

.hint {
  color: var(--slate-500);
  font-size: 12px;
}
</style>
