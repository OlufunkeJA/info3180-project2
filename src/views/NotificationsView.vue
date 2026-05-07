<template>
  <div class="container">
    <div class="notifications-panel">
      <h2>Notifications</h2>

      <button class="mark-all" @click="markAllRead" v-if="notifications.length > 0">
        Mark all as read
      </button>

      <div v-if="notifications.length === 0" class="empty-state">
        No notifications yet.
      </div>

      <ul class="notification-list">
        <li
          v-for="notification in notifications"
          :key="notification.id"
          :class="{ unread: !notification.is_read }"
          class="notification-item"
        >
          <div class="content">
            <strong>{{ notification.title }}</strong>
            <p>{{ notification.message }}</p>
            <small>{{ formatDate(notification.created_at) }}</small>
          </div>
          <button
            v-if="!notification.is_read"
            class="mark-read"
            @click="markRead(notification.id)"
            aria-label="Mark notification read"
          >
            ✕
          </button>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { requestJson } from '@/services/api'

const notifications = ref([])
const status = ref('')

async function loadNotifications() {
  const { response, data } = await requestJson('/api/notifications')
  if (response.ok) {
    notifications.value = data.notifications || []
  } else {
    status.value = data?.error || 'Unable to load notifications.'
  }
}

function formatDate(value) {
  if (!value) {
    return ''
  }
  return new Date(value).toLocaleString()
}

async function markRead(notificationId) {
  const { response } = await requestJson(`/api/notifications/${notificationId}/read`, {
    method: 'PUT',
  })

  if (response.ok) {
    const notification = notifications.value.find((item) => item.id === notificationId)
    if (notification) {
      notification.is_read = true
    }
  } else {
    status.value = 'Unable to mark notification as read.'
  }
}

async function markAllRead() {
  const { response } = await requestJson('/api/notifications/read-all', {
    method: 'PUT',
  })

  if (response.ok) {
    notifications.value.forEach((notification) => {
      notification.is_read = true
    })
  } else {
    status.value = 'Unable to mark all notifications as read.'
  }
}

onMounted(loadNotifications)
</script>

<style>
.container {
  padding: 24px;
}
.notifications-panel {
  max-width: 800px;
  margin: 0 auto;
}
.notification-list {
  list-style: none;
  padding: 0;
  margin: 0;
}
.notification-item {
  display: grid;
  grid-template-columns: 9fr 1fr;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 8px;
  margin-bottom: 12px;
}
.notification-item.unread {
  background: rgba(235, 45, 76, 0.08);
}
.notification-item p {
  margin: 4px 0;
}
.notification-item small {
  color: rgba(0, 0, 0, 0.55);
}
.mark-read,
.mark-all {
  border: none;
  background-color: var(--myPink);
  color: white;
  padding: 8px 12px;
  border-radius: 4px;
  cursor: pointer;
}
.empty-state {
  padding: 16px;
  background-color: rgba(0, 0, 0, 0.03);
  border-radius: 8px;
}
</style>
