<template>
  <div class="msgContainer">
    <div class="messages">
      <div class="left">
        <p class="section-title">Conversations</p>
        <button
          v-for="conversation in conversations"
          :key="conversation.connection.id"
          class="names"
          :class="{ active: conversation.connection.id === selectedConnectionId }"
          @click="switchChat(conversation)"
        >
          {{ conversation.other_profile?.display_name || 'Conversation' }}
        </button>
      </div>

      <div class="right">
        <div class="top">
          <p v-if="conversations.length === 0" class="bubble">No conversations available yet.</p>
          <p v-else-if="!selectedConnectionId" class="bubble">Select a conversation to view messages.</p>

          <template v-else>
            <div class="conversation-header">
              <h3>{{ selectedConversation.other_profile?.display_name || 'Conversation' }}</h3>
              <div class="conversation-actions">
                <button class="report-button" @click="reportUser">Report</button>
                <button class="block-button" @click="blockUser">Block</button>
              </div>
            </div>
            <div class="message-list">
              <div v-for="message in messages" :key="message.id" class="bubble">
                <strong>{{ message.author_handle }}:</strong>
                <p class="bubble-content">{{ message.content }}</p>
                <span class="message-time">{{ formatTimestamp(message.sent_at) }}</span>
              </div>
            </div>
          </template>
          <p v-if="status" class="status-text">{{ status }}</p>
        </div>

        <div class="bottom">
          <input
            v-model="newMessage"
            type="text"
            name="message"
            class="message"
            placeholder="Type a message.."
            :disabled="!selectedConnectionId"
          />
          <button @click="send" class="send" :disabled="!selectedConnectionId">Send</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRoute } from 'vue-router'
import { requestJson } from '@/services/api'

const route = useRoute()
const conversations = ref([])
const messages = ref([])
const selectedConnectionId = ref(null)
const selectedConversation = ref(null)
const newMessage = ref('')
const status = ref('')

function formatTimestamp(value) {
  if (!value) {
    return ''
  }
  return new Date(value).toLocaleString()
}

async function reportUser() {
  if (!selectedConversation.value || !selectedConversation.value.other_account) {
    status.value = 'No user selected to report.'
    return
  }

  const reason = window.prompt(
    'Enter report reason (spam, harassment, fake, inappropriate, other):'
  )?.trim().toLowerCase()
  if (!reason) {
    return
  }

  const validReasons = [
    'spam',
    'harassment',
    'fake',
    'inappropriate',
    'other',
  ]
  if (!validReasons.includes(reason)) {
    status.value = 'Invalid report reason.'
    return
  }

  const details = window.prompt('Enter any details for the report (optional):') || ''
  const targetId = selectedConversation.value.other_account.id

  const { response, data } = await requestJson(
    `/api/accounts/${targetId}/report`,
    {
      method: 'POST',
      body: { reason, details },
    }
  )

  if (response.ok) {
    status.value = data.message || 'Report submitted.'
  } else {
    status.value = data?.error || 'Report failed.'
  }
}

async function blockUser() {
  if (!selectedConversation.value || !selectedConversation.value.other_account) {
    status.value = 'No user selected to block.'
    return
  }

  const confirmed = window.confirm(
    `Block ${selectedConversation.value.other_account.handle || 'this user'}?`
  )
  if (!confirmed) {
    return
  }

  const targetId = selectedConversation.value.other_account.id
  const { response, data } = await requestJson(
    `/api/accounts/${targetId}/block`,
    { method: 'POST' }
  )

  if (response.ok) {
    status.value = data.message || 'User blocked.'
  } else {
    status.value = data?.error || 'Block failed.'
  }
}

async function loadConversations() {
  const { response, data } = await requestJson('/api/conversations')
  if (response.ok) {
    conversations.value = data.conversations || []
    const routeConnectionId = route.query.connectionId ? Number(route.query.connectionId) : null
    if (routeConnectionId) {
      const conversation = conversations.value.find(
        (item) => item.connection.id === routeConnectionId
      )
      if (conversation) {
        switchChat(conversation)
        return
      }
    }

    if (conversations.value.length) {
      switchChat(conversations.value[0])
    }
  } else {
    status.value = data?.error || 'Unable to load conversations.'
    console.error(status.value)
  }
}

async function loadMessages(connectionId) {
  const { response, data } = await requestJson(`/api/connections/${connectionId}/messages`)
  if (response.ok) {
    messages.value = data.messages || []
  } else {
    status.value = data?.error || 'Unable to load messages.'
    console.error(status.value)
  }
}

function switchChat(conversation) {
  selectedConnectionId.value = conversation.connection.id
  selectedConversation.value = conversation
  loadMessages(conversation.connection.id)
}

async function send() {
  if (!selectedConnectionId.value) {
    status.value = 'No conversation selected to send a message.'
    return
  }

  if (!newMessage.value.trim()) {
    status.value = 'Type a message before sending.'
    return
  }

  const { response, data } = await requestJson(
    `/api/connections/${selectedConnectionId.value}/messages`,
    {
      method: 'POST',
      body: { content: newMessage.value.trim() },
    }
  )

  if (response.ok) {
    const message = data.data
    if (message) {
      messages.value.push(message)
    }
    newMessage.value = ''
    status.value = ''
  } else {
    status.value = data?.errors?.join(', ') || data?.error || 'Unable to send message.'
    console.error(status.value)
  }
}

onMounted(loadConversations)
</script>

<style>
button.names{
  border: none;
  background-color: var(--myBG);
  color: var(--color-text);
  font-weight: bold;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 14px;
  border-radius: 8px;
  text-align: left;
  width: 100%;
  cursor: pointer;
  transition: background 0.18s ease;
}

button.names:hover,
button.names.active {
  background-color: rgba(235, 45, 76, 0.14);
}

button.send{
  background-color: var(--myPink);
  border-radius: 8px;
  color: var(--myBG);
  padding: 12px 18px;
  border: none;
  cursor: pointer;
  width: auto;
}

div.msgContainer{
  width: 100%;
  display: flex;
  justify-content: center;
  padding: 20px;
}

div.messages{
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  padding: 20px;
  border-radius: 12px;
  display: grid;
  grid-template-areas: "left right";
  grid-template-columns: 260px minmax(400px, 1fr);
  gap: 20px;
  width: min(1200px, 100%);
}

div.right{
  grid-area: right;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 16px;
  min-height: 540px;
}

div.left{
  grid-area: left;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  justify-content: flex-start;
  gap: 8px;
  background: rgba(255, 255, 255, 0.95);
  padding: 16px;
  border-radius: 12px;
  border: 1px solid rgba(0, 0, 0, 0.08);
}

.top{
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 12px;
}

.bottom{
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 12px;
}

input{
  width: 100%;
  border-radius: 5px;
  border: 2px solid var(--color-border);
  margin: 0;
  padding: 8px;
}

.message{
  flex: 1;
}

button.send{
  background-color: var(--myPink);
  border-radius: 3px;
  color: var(--myBG);
  padding: 10px 14px;
  border: none;
  cursor: pointer;
  width: auto;
}

.bubble{
  background-color: var(--myPink);
  border-radius: 18px;
  color: var(--myBG);
  padding: 12px 16px;
  margin: 0;
  line-height: 1.5;
  align-self: flex-start;
  max-width: 90%;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
}

.message-list {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 14px;
  max-height: 56vh;
  overflow-y: auto;
  padding-right: 6px;
}

.bubble-content {
  margin: 8px 0 0;
}

.message-time {
  display: block;
  margin-top: 10px;
  font-size: 0.78rem;
  color: rgba(255, 255, 255, 0.85);
}

.conversation-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.conversation-actions {
  display: flex;
  gap: 8px;
}

.report-button,
.block-button {
  border: none;
  border-radius: 4px;
  padding: 6px 10px;
  cursor: pointer;
  color: #fff;
}

.report-button {
  background-color: #f0ad4e;
}

.block-button {
  background-color: #d9534f;
}

.status-text {
  margin-top: 8px;
  color: var(--color-text);
  background: rgba(0, 0, 0, 0.05);
  padding: 8px 10px;
  border-radius: 6px;
  border: 1px solid rgba(0, 0, 0, 0.08);
}

</style>
