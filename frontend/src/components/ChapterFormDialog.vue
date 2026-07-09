<template>
  <el-dialog v-model="visible" :title="chapter?.id ? t('teacher.chapters.dialogEditTitle') : t('teacher.chapters.dialogCreateTitle')" width="560px" destroy-on-close>
    <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
      <el-form-item :label="t('teacher.chapters.titleLabel')" prop="title">
        <el-input v-model.trim="form.title" :placeholder="t('teacher.chapters.titlePlaceholder')" />
      </el-form-item>
      <el-form-item :label="t('teacher.chapters.descriptionLabel')" prop="description">
        <el-input v-model.trim="form.description" type="textarea" :rows="3" :placeholder="t('teacher.chapters.descriptionPlaceholder')" />
      </el-form-item>
      <el-form-item :label="t('teacher.chapters.orderLabel')" prop="order">
        <el-input-number v-model="form.order" :min="1" :step="1" />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="visible = false">{{ t('teacher.chapters.cancelBtn') }}</el-button>
      <el-button type="primary" :loading="submitting" @click="handleSubmit">{{ t('teacher.chapters.saveBtn') }}</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  chapter: {
    type: Object,
    default: null
  },
  nextOrder: {
    type: Number,
    default: 1
  },
  submitting: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'submit'])

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const formRef = ref()
const form = reactive({
  title: '',
  description: '',
  order: 1
})

const rules = computed(() => ({
  title: [{ required: true, message: t('teacher.chapters.titleRequired'), trigger: 'blur' }],
  order: [{ required: true, message: t('teacher.chapters.orderRequired'), trigger: 'change' }]
}))

watch(
  () => [props.modelValue, props.chapter, props.nextOrder],
  () => {
    if (!props.modelValue) return
    form.title = props.chapter?.title || ''
    form.description = props.chapter?.description || ''
    form.order = props.chapter?.order || props.nextOrder || 1
  },
  { immediate: true }
)

async function handleSubmit() {
  await formRef.value.validate()
  emit('submit', { ...form })
}
</script>
