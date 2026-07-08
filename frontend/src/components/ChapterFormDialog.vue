<template>
  <el-dialog v-model="visible" :title="chapter?.id ? '编辑章节' : '创建章节'" width="560px" destroy-on-close>
    <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
      <el-form-item label="章节标题" prop="title">
        <el-input v-model.trim="form.title" placeholder="例如：第 1 章 认识课程" />
      </el-form-item>
      <el-form-item label="章节简介" prop="description">
        <el-input v-model.trim="form.description" type="textarea" :rows="3" placeholder="说明本章内容" />
      </el-form-item>
      <el-form-item label="排序" prop="order">
        <el-input-number v-model="form.order" :min="1" :step="1" />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="handleSubmit">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue'

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

const rules = {
  title: [{ required: true, message: '请输入章节标题', trigger: 'blur' }],
  order: [{ required: true, message: '请输入章节排序', trigger: 'change' }]
}

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
