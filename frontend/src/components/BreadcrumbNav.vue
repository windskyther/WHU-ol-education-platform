<template>
  <nav v-if="items.length" class="breadcrumb-nav" aria-label="面包屑导航">
    <template v-for="(item, index) in items" :key="`${item.label}-${index}`">
      <span v-if="index > 0" class="breadcrumb-separator" aria-hidden="true">/</span>
      <RouterLink v-if="item.to && index < items.length - 1" :to="item.to">{{ item.label }}</RouterLink>
      <span v-else class="breadcrumb-current">{{ item.label }}</span>
    </template>
  </nav>
</template>

<script setup>
import { RouterLink } from 'vue-router'

defineProps({
  items: {
    type: Array,
    default: () => []
  }
})
</script>
