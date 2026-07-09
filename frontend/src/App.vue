<template>
  <el-config-provider :locale="elLocale">
    <RallyRibbon />
    <LangSwitch class="global-lang-switch" />
    <router-view v-slot="{ Component, route }">
      <Transition name="page" mode="out-in">
        <component :is="Component" :key="route.fullPath" />
      </Transition>
    </router-view>
  </el-config-provider>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import en from 'element-plus/es/locale/lang/en'
import RallyRibbon from './components/RallyRibbon.vue'
import LangSwitch from './components/LangSwitch.vue'

const { locale } = useI18n()
const elLocale = computed(() => (locale.value === 'en-US' ? en : zhCn))
</script>

<style>
.global-lang-switch {
  position: fixed;
  top: 16px;
  right: 16px;
  z-index: 2000;
  background: var(--mint-050, #fff);
  box-shadow: 0 2px 10px rgba(16, 37, 26, 0.12);
}
</style>
