<template>
  <div class="container">
    <h2>Your Matches</h2>

    <div class="match-filters">
      <div class="filter-row">
        <label>
          Location
          <input v-model="locationFilter" type="text" placeholder="City, parish, or country" />
        </label>
        <label>
          Age
          <div class="age-inputs">
            <input v-model.number="minAgeFilter" type="number" min="18" placeholder="Min" />
            <span>–</span>
            <input v-model.number="maxAgeFilter" type="number" min="18" placeholder="Max" />
          </div>
        </label>
        <label>
          Interests
          <input v-model="interestsFilter" type="text" placeholder="Comma-separated interests" />
        </label>
      </div>

      <div class="filter-row">
        <label>
          Job title
          <input v-model="jobFilter" type="text" placeholder="Job title" />
        </label>
        <label>
          Schooling
          <input v-model="schoolingFilter" type="text" placeholder="Education" />
        </label>
        <label>
          Sort by
          <select v-model="sortOption">
            <option value="newest">Newest match</option>
            <option value="similar">Most similar</option>
          </select>
        </label>
      </div>

      <div class="filter-actions">
        <button type="button" @click="resetFilters">Reset</button>
      </div>
    </div>

    <div class="matches">
        <p v-if="filteredMatches.length === 0">No matches found for the selected filters.</p>
        <div class="matchCard" v-for="match in filteredMatches" :key="match.id || match.other_profile?.id">
          <img :src="match.other_profile?.avatar_url || '/src/assets/logo.svg'" :alt="match.other_profile?.display_name || 'Match avatar'">

          <div class="matchCard-right">  
            <p class="name">{{ match.other_profile?.display_name || 'Unknown' }}, {{ match.other_profile?.age ?? 'N/A' }}</p>
            <p>{{ match.other_profile?.about_me || 'No bio yet.' }}</p>
            <p class="match-meta">
              <span v-if="match.match_score != null">Match score: {{ match.match_score }}</span>
              <span v-if="match.connection?.formed_at">Connected: {{ new Date(match.connection.formed_at).toLocaleDateString() }}</span>
            </p>
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
import { computed, ref, onMounted } from "vue";
import { useRouter } from 'vue-router'
import { requestJson } from '@/services/api'

const router = useRouter()
const currentProfile = ref(null)
const matches = ref([])
const errorMessage = ref('')
const locationFilter = ref('')
const minAgeFilter = ref(18)
const maxAgeFilter = ref(99)
const interestsFilter = ref('')
const jobFilter = ref('')
const schoolingFilter = ref('')
const sortOption = ref('newest')

function normalize(value) {
  return String(value || '').toLowerCase().trim()
}

function computeMatchScore(baseProfile, candidate) {
  if (!baseProfile || !candidate) {
    return 0
  }

  let score = 0
  const baseInterests = new Set((baseProfile.likes || []).map((interest) => normalize(interest)))
  const candidateInterests = new Set((candidate.likes || []).map((interest) => normalize(interest)))
  const sharedInterests = [...baseInterests].filter((interest) => candidateInterests.has(interest))

  if (sharedInterests.length) {
    score += Math.min(sharedInterests.length * 10, 30)
  }

  if (baseProfile.job_title && candidate.job_title && normalize(baseProfile.job_title) === normalize(candidate.job_title)) {
    score += 10
  }

  if (baseProfile.schooling && candidate.schooling && normalize(baseProfile.schooling) === normalize(candidate.schooling)) {
    score += 10
  }

  const age = candidate.age
  if (age != null && baseProfile.min_age <= age && age <= baseProfile.max_age) {
    score += 15
  }

  if (candidate.min_age != null && candidate.max_age != null && baseProfile.age != null && candidate.min_age <= baseProfile.age && baseProfile.age <= candidate.max_age) {
    score += 15
  }

  const locationValue = normalize(locationFilter.value)
  if (locationValue && [candidate.city, candidate.parish, candidate.country].some((part) => normalize(part).includes(locationValue))) {
    score += 10
  }

  return score
}

const filteredMatches = computed(() => {
  return matches.value
    .filter((match) => {
      const profile = match.other_profile
      if (!profile) {
        return false
      }

      if (locationFilter.value) {
        const search = normalize(locationFilter.value)
        if (![profile.city, profile.parish, profile.country].some((part) => normalize(part).includes(search))) {
          return false
        }
      }

      if (minAgeFilter.value && profile.age != null && profile.age < minAgeFilter.value) {
        return false
      }

      if (maxAgeFilter.value && profile.age != null && profile.age > maxAgeFilter.value) {
        return false
      }

      if (interestsFilter.value) {
        const queryInterests = interestsFilter.value
          .split(',')
          .map((interest) => normalize(interest))
          .filter(Boolean)

        if (!queryInterests.some((interest) => (profile.likes || []).some((like) => normalize(like).includes(interest)))) {
          return false
        }
      }

      if (jobFilter.value && profile.job_title && !normalize(profile.job_title).includes(normalize(jobFilter.value))) {
        return false
      }

      if (schoolingFilter.value && profile.schooling && !normalize(profile.schooling).includes(normalize(schoolingFilter.value))) {
        return false
      }

      return true
    })
    .map((match) => ({
      ...match,
      match_score: computeMatchScore(currentProfile.value, match.other_profile),
    }))
    .sort((a, b) => {
      if (sortOption.value === 'similar') {
        return b.match_score - a.match_score
      }
      return new Date(b.connection.formed_at) - new Date(a.connection.formed_at)
    })
})

async function loadMatches() {
  const [connectionsResponse, profileResponse] = await Promise.all([
    requestJson('/api/connections'),
    requestJson('/api/profile'),
  ])

  if (profileResponse.response.ok) {
    currentProfile.value = profileResponse.data.profile
  }

  if (connectionsResponse.response.ok && connectionsResponse.data.connections) {
    matches.value = connectionsResponse.data.connections || []
  } else {
    errorMessage.value = connectionsResponse.data?.error || 'Unable to load matches.'
  }
}

function resetFilters() {
  locationFilter.value = ''
  minAgeFilter.value = 18
  maxAgeFilter.value = 99
  interestsFilter.value = ''
  jobFilter.value = ''
  schoolingFilter.value = ''
  sortOption.value = 'newest'
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

  .match-filters {
    margin-bottom: 20px;
    padding: 16px;
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.95);
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08);
  }

  .filter-row {
    display: flex;
    flex-wrap: wrap;
    gap: 16px;
    margin-bottom: 12px;
  }

  .filter-row label {
    display: flex;
    flex-direction: column;
    flex: 1 1 220px;
    gap: 8px;
    font-weight: 600;
  }

  .filter-row input,
  .filter-row select {
    width: 100%;
    padding: 10px;
    border-radius: 8px;
    border: 1px solid var(--color-border);
  }

  .age-inputs {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .filter-actions {
    display: flex;
    justify-content: flex-end;
  }

  .filter-actions button {
    padding: 10px 16px;
    border: none;
    border-radius: 8px;
    background: var(--myPink);
    color: white;
    cursor: pointer;
  }

  .match-meta {
    margin: 12px 0 8px;
    font-size: 0.9rem;
    color: var(--color-muted, #555);
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
  }
</style>
