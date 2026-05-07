<template>
  <header>
    <nav class="navbar navbar-expand-lg navbar-dark fixed-top">
      <div class="container-fluid">
        <RouterLink class="navbar-brand" to="/">DriftDating💞</RouterLink>
        <button
          class="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#navbarSupportedContent"
          aria-controls="navbarSupportedContent"
          aria-expanded="false"
          aria-label="Toggle navigation"
        >
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarSupportedContent">
          <ul class="navbar-nav me-auto">
            <li class="nav-item" v-if="isAuthenticated">
              <RouterLink to="/" class="nav-link active">Dashboard</RouterLink>
            </li>
            <li class="nav-item" v-if="isAuthenticated">
              <RouterLink class="nav-link" to="/matches">Matches</RouterLink>
            </li>
            <li class="nav-item" v-if="isAuthenticated">
              <RouterLink class="nav-link" to="/messages">Messages</RouterLink>
            </li>
            <li class="nav-item" v-if="isAuthenticated">
              <RouterLink class="nav-link" to="/notifications">
                Notifications
                <span v-if="notificationsCount > 0" class="badge">{{ notificationsCount }}</span>
              </RouterLink>
            </li>
            <li class="nav-item" v-if="isAuthenticated">
              <RouterLink class="nav-link" to="/profile">Profile</RouterLink>
            </li>
            <li class="nav-item" v-if="!isAuthenticated">
              <RouterLink class="nav-link" to="/login">Login</RouterLink>
            </li>
            <li class="nav-item" v-if="!isAuthenticated">
              <RouterLink class="nav-link" to="/signup">Sign Up</RouterLink>
            </li>
            <li class="nav-item" v-if="isAuthenticated">
              <button class="nav-link logout-button" type="button" @click="logout">Logout</button>
            </li>
          </ul>
        </div>
      </div>
    </nav>
    <button
      class="theme-toggle"
      type="button"
      @click="toggleTheme"
      :title="theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'"
    >
      {{ theme === 'dark' ? '☀' : '🌙' }}
    </button>
  </header>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'

import { currentAccount, loadSession, logoutAccount, sessionReady, setFlash } from '@/services/session'
import { requestJson } from '@/services/api'

const router = useRouter()
const isAuthenticated = computed(() => Boolean(currentAccount.value))
const notificationsCount = ref(0)
const theme = ref('system')

function applyTheme(value) {
  theme.value = value
  document.documentElement.setAttribute('data-theme', value)
  localStorage.setItem('theme', value)
}

function loadTheme() {
  const saved = localStorage.getItem('theme')
  if (saved === 'light' || saved === 'dark' || saved === 'system') {
    applyTheme(saved)
    return
  }

  applyTheme(window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')
}

function toggleTheme() {
  const nextTheme = theme.value === 'dark' ? 'light' : 'dark'
  applyTheme(nextTheme)
}

async function logout() {
  const { response, data } = await logoutAccount()

  if (response.ok) {
    setFlash(data?.message || 'Logout successful.', 'success')
    router.push('/login')
  } else {
    setFlash(data?.error || 'Logout failed.', 'error')
  }
}

async function loadNotificationCount() {
  const { response, data } = await requestJson('/api/notifications/unread-count')
  if (response.ok) {
    notificationsCount.value = data.unread_count || 0
  }
}

onMounted(async () => {
  loadTheme()

  if (!sessionReady.value) {
    await loadSession()
  }

  if (currentAccount.value) {
    loadNotificationCount()
  }
})
</script>

<style>
/* Add any component specific styles here */
:root{
  --myPink: rgb(235, 45, 76);
}

nav{
  background-image: linear-gradient(to right, var(--myPink), rgb(255, 25, 64));
}
.badge {
  display: inline-block;
  margin-left: 6px;
  padding: 2px 6px;
  background-color: yellow;
  color: black;
  border-radius: 999px;
  font-size: 0.8rem;
}
.navbar-brand {
  font-family: 'Brush Script MT', cursive;
  font-size: 1.8em;
  background: linear-gradient(45deg, #ff6ec4, #7873f5);
  padding: 0;
  display: inline-block;
  padding: 5px 10px;
  border-radius: 5px;
}

.theme-toggle {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 2000;
  width: 48px;
  height: 48px;
  border: none;
  border-radius: 50%;
  background-color: var(--myPink);
  color: white;
  font-size: 1.2rem;
  cursor: pointer;
  display: grid;
  place-items: center;
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.18);
}

.theme-toggle:hover {
  transform: translateY(-1px);
}
</style>