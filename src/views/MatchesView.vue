<template>
  <div class="container">
    <h2>Your Matches</h2>

    <div class="matches">
        <div class="matchCard" v-for="match in matches" :key="match.id || match.other_profile?.id">
          <img :src="match.other_profile?.avatar_url || '/src/assets/logo.svg'" :alt="match.other_profile?.display_name || 'Match avatar'">

          <div class="matchCard-right">  
            <p class="name">{{ match.other_profile?.display_name || 'Unknown' }}, {{ match.other_profile?.age ?? 'N/A' }}</p>
            <p>{{ match.other_profile?.about_me || 'No bio yet.' }}</p>
            <button
              @click="message(match.id)"
              class="message"
              :disabled="!match.id"
            >
              Message
            </button>
          </div>
        </div>
    </div>
  </div> 
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from 'vue-router'
import { requestJson } from '@/services/api'

const router = useRouter()
const matches = ref([])
const errorMessage = ref('')

async function loadMatches() {
  const { response, data } = await requestJson('/api/connections')

  if (response.ok && data.connections) {
    matches.value = data.connections || []
  } else {
    errorMessage.value = data?.error || 'Unable to load matches.'
  }
}

function message(connectionId) {
  if (!connectionId) {
    console.error('Cannot open message: missing connection id')
    return
  }
  router.push({ name: 'messages', query: { connectionId } })
}

onMounted(loadMatches)
</script>

<style>
  h2{
    color: var(--myPink);
  }
</style>
