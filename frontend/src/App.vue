<template>
  <RallyRibbon />
  <router-view v-slot="{ Component, route }">
    <Transition name="page" mode="out-in">
      <component :is="Component" :key="route.fullPath" />
    </Transition>
  </router-view>
</template>

<script setup>
import RallyRibbon from './components/RallyRibbon.vue'
</script>
