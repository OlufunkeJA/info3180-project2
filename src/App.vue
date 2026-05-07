<script setup>
import { RouterLink, RouterView } from 'vue-router'
import { watch, ref } from 'vue'
import AppHeader from "@/components/AppHeader.vue";
import AppFooter from "@/components/AppFooter.vue";
import { flashMessage, flashType, clearFlash } from '@/services/session'

const currentFlash = flashMessage
const currentFlashType = flashType
let timer = null

watch(currentFlash, (value) => {
  if (value) {
    clearTimeout(timer)
    timer = setTimeout(() => {
      clearFlash()
    }, 4000)
  }
})
</script>

<template>
  <AppHeader />

  <div v-if="currentFlash" :class="['flash', currentFlashType]">
    {{ currentFlash }}
  </div>

  <main>
    <RouterView />
  </main>
  
  <AppFooter />
</template>

<style>
body {
  padding-top: 75px;
}

.flash {
  position: fixed;
  top: 75px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1100;
  min-width: 280px;
  max-width: 90%;
  padding: 12px 18px;
  border-radius: 10px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.12);
  font-weight: 600;
  text-align: center;
}

.flash.success {
  background-color: rgba(16, 185, 129, 0.95);
  color: white;
}

.flash.error {
  background-color: rgba(239, 68, 68, 0.95);
  color: white;
}
</style>