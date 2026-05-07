<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { requestJson } from '@/services/api'

const router = useRouter()
const currentProfile = ref(null)
const profiles = ref([])
const loading = ref(true)
const errorMessage = ref('')

const locationFilter = ref('')
const minAgeFilter = ref(18)
const maxAgeFilter = ref(99)
const interestsFilter = ref('')
const genderFilter = ref('')
const jobTitleFilter = ref('')
const schoolingFilter = ref('')
const sortOption = ref('newest')
const bookmarkedOnly = ref(false)
const bookmarkedIds = ref(new Set())

const displayProfiles = computed(() => {
  return profiles.value.filter((profile) => {
    return !bookmarkedOnly.value || bookmarkedIds.value.has(profile.id)
  })
})

function formatLocation(profile) {
  return [profile.city, profile.parish, profile.country].filter(Boolean).join(', ') || 'Location not set'
}

async function loadBookmarks() {
  const { response, data } = await requestJson('/api/bookmarks')

  if (response.ok) {
    bookmarkedIds.value = new Set((data.bookmarks || []).map((profile) => profile.id))
  }
}

function buildProfileQuery() {
  const params = new URLSearchParams()

  if (locationFilter.value) {
    params.append('location', locationFilter.value)
  }

  if (minAgeFilter.value) {
    params.append('min_age', String(minAgeFilter.value))
  }

  if (maxAgeFilter.value) {
    params.append('max_age', String(maxAgeFilter.value))
  }

  if (interestsFilter.value) {
    params.append('interests', interestsFilter.value)
  }

  if (genderFilter.value) {
    params.append('gender', genderFilter.value)
  }

  if (jobTitleFilter.value) {
    params.append('job_title', jobTitleFilter.value)
  }

  if (schoolingFilter.value) {
    params.append('schooling', schoolingFilter.value)
  }

  if (sortOption.value) {
    params.append('sort', sortOption.value)
  }

  return params.toString()
}

async function loadProfiles() {
  loading.value = true
  errorMessage.value = ''

  const query = buildProfileQuery()
  const url = query ? `/api/profiles?${query}` : '/api/profiles'

  const { response, data } = await requestJson(url)

  if (response.ok) {
    profiles.value = data.profiles || []
  } else {
    errorMessage.value = data?.error || 'Unable to load profiles.'
  }

  loading.value = false
}

async function loadDashboard() {
  loading.value = true
  errorMessage.value = ''

  const myProfileResponse = await requestJson('/api/profile')

  if (myProfileResponse.response.ok) {
    currentProfile.value = myProfileResponse.data.profile
  } else if (myProfileResponse.response.status === 404) {
    currentProfile.value = null
    errorMessage.value = 'Create your profile to start browsing.'
  } else {
    errorMessage.value = myProfileResponse.data?.error || 'Unable to load your profile.'
  }

  await loadBookmarks()
  await loadProfiles()

  loading.value = false
}

async function swipe(profileId, action) {
  const { response, data } = await requestJson(`/api/profiles/${profileId}/like`, {
    method: 'POST',
    body: { action }
  })

  if (!response.ok) {
    errorMessage.value = data?.error || 'Unable to record your choice.'
    return
  }

  profiles.value = profiles.value.filter((profile) => profile.acct_id !== profileId)
}

function isBookmarked(profileId) {
  return bookmarkedIds.value.has(profileId)
}

async function toggleBookmark(profile) {
  const targetId = profile.id
  const isSaved = isBookmarked(targetId)
  const method = isSaved ? 'DELETE' : 'POST'
  const { response } = await requestJson(`/api/bookmarks/${targetId}`, { method })

  if (!response.ok) {
    errorMessage.value = 'Unable to update saved profiles.'
    return
  }

  if (isSaved) {
    bookmarkedIds.value.delete(targetId)
  } else {
    bookmarkedIds.value.add(targetId)
  }
}

function resetFilters() {
  locationFilter.value = ''
  minAgeFilter.value = 18
  maxAgeFilter.value = 99
  interestsFilter.value = ''
  genderFilter.value = ''
  jobTitleFilter.value = ''
  schoolingFilter.value = ''
  sortOption.value = 'newest'
  bookmarkedOnly.value = false
  loadProfiles()
}

function edit() {
  router.push('/edit-profile')
}

onMounted(loadDashboard)
</script>

<template>
    <div class="container">
      <div v-if="currentProfile" class="myCard">
        <img :src="currentProfile.avatar_url || '/src/assets/logo.svg'">

        <div class="card-right">
          <h1>Welcome, {{ currentProfile.display_name }}!</h1>
          <p>Age: {{ currentProfile.age ?? 'N/A' }}</p>
          <p>Location: {{ formatLocation(currentProfile) }}</p>
          <p>Bio: {{ currentProfile.about_me || 'Add a short bio in your profile.' }}</p>
          <button type="button" @click="edit">Edit Profile</button>
        </div>
      </div>

      <div v-else class="myCard empty-state">
        <div class="card-right">
          <h1>Welcome!</h1>
          <p>{{ errorMessage || 'Your profile is not set up yet.' }}</p>
          <button type="button" @click="edit">Create Profile</button>
        </div>
      </div>

      <div class="filters">
        <h3>Search & Discovery</h3>

        <div class="filter-grid">
          <label>
            Location
            <input v-model="locationFilter" type="text" placeholder="City, parish, or country" />
          </label>

          <label>
            Age range
            <div class="age-range">
              <input v-model.number="minAgeFilter" type="number" min="18" placeholder="Min" />
              <span>–</span>
              <input v-model.number="maxAgeFilter" type="number" min="18" placeholder="Max" />
            </div>
          </label>

          <label>
            Interests
            <input v-model="interestsFilter" type="text" placeholder="Comma-separated interests" />
          </label>

          <label>
            Gender
            <input v-model="genderFilter" type="text" placeholder="Preferred gender" />
          </label>

          <label>
            Job title
            <input v-model="jobTitleFilter" type="text" placeholder="Job title" />
          </label>

          <label>
            Schooling
            <input v-model="schoolingFilter" type="text" placeholder="Education level" />
          </label>

          <label>
            Sort by
            <select v-model="sortOption">
              <option value="newest">Newest profiles</option>
              <option value="similar">Most similar</option>
            </select>
          </label>

          <label class="checkbox-label">
            <input type="checkbox" v-model="bookmarkedOnly" />
            Bookmarked only
          </label>
        </div>

        <div class="filter-actions">
          <button type="button" @click="loadProfiles" class="search">Apply filters</button>
          <button type="button" @click="resetFilters" class="reset">Reset</button>
        </div>
      </div>

      <div class="matches">
        <h3>Browse Profiles</h3>

        <p v-if="errorMessage" class="status-message">{{ errorMessage }}</p>
        <p v-if="loading">Loading profiles...</p>
        <p v-else-if="displayProfiles.length === 0">No profiles are available right now.</p>

        <div class="matchCard" v-for="match in displayProfiles" :key="match.id">
          <img :src="match.avatar_url || '/src/assets/logo.svg'">

          <div class="matchCard-right">
            <div class="text">
              <p class="name">{{ match.display_name }} <span v-if="match.handle">@{{ match.handle }}</span></p>
              <p>{{ match.about_me || 'No bio yet.' }}</p>
              <p class="score">{{ match.age ? `${match.age} years old` : 'Age not listed' }}</p>
            </div>

            <div class="buttons">
              <button type="button" @click="toggleBookmark(match)" :class="isBookmarked(match.id) ? 'saved' : 'bookmark'">
                {{ isBookmarked(match.id) ? 'Saved' : 'Bookmark' }}
              </button>
              <button type="button" @click="swipe(match.acct_id, 'like')" class="like">Like</button>
              <button type="button" @click="swipe(match.acct_id, 'dislike')" class="dislike">Dislike</button>
              <button type="button" @click="swipe(match.acct_id, 'pass')" class="pass">Pass</button>
            </div>
          </div>
        </div>
      </div>
    </div>
</template>

<style>
/* Add any component specific styles here */
button{
  border: none;
  color: var(--myBG);
  background-color: var(--myPink);
  border-radius: 3px;
  padding: 3px;
  width: 100%;
}

button.like{
  background-color: var(--darkPink);
  margin: 2px;
  padding: 10px;
}

button.dislike{
  padding: 10px;
  margin: 2px;
  background-color: var(--myPink);
}

button.pass{
  background-color: var(--myBG);
  color: var(--darkPink);
  border: 1px solid var(--darkPink);
  margin: 2px;
  padding: 10px;
}

button.search{
  background-color: var(--darkPink);
  margin: 2px;
}

button.reset{
  background-color: var(--myBG);
  color: var(--darkPink);
  border: 1px solid var(--darkPink);
  margin: 2px;
}

button.bookmark,
button.saved {
  min-width: 100px;
  margin: 2px;
  padding: 10px;
}

button.bookmark {
  background-color: rgba(59, 130, 246, 0.9);
  color: white;
}

button.saved {
  background-color: rgba(34, 197, 94, 0.9);
  color: white;
}

.filters {
  margin-bottom: 20px;
  padding: 20px;
  border-radius: 2px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.filter-grid {
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
}

.filter-grid label {
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-weight: 600;
}

.filter-grid input,
.filter-grid select {
  width: 100%;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  padding: 10px;
}

.age-range {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-actions {
  display: flex;
  gap: 10px;
  margin-top: 16px;
  flex-wrap: wrap;
}

.checkbox-label {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
}

img{
  float: left;
  width: 10%;
}

div.buttons{
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  float: right;
  grid-area: "buttons";
  float: right;
}

div.card-right{
  float: right;
  width: 100%;
  margin-left: 30px;
}

form{
  display: flex;
  flex-direction: row;
  column-gap: 10px;
}

div.myCard, div.matches{
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  padding: 20px;
  border-radius: 2px;
  display: flex;
}

div.myCard{
  margin-bottom: 20px;
}

div.matchCard{
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  padding: 20px;
  border-radius: 2px;
  display: flex;
}

div.matchCard-right{
  width: 100%;
  margin-left: 30px;
  grid-template-areas: "text buttons";
  grid-template-columns: 9fr 1fr;
}

div.matches{
  flex-direction: column;
}

div.text{
  display: flex;
  flex-direction: column;
  grid-area: "text";
  float: left;
}

h1{
  color: var(--myPink);
  font-weight: bold;
  margin: 0px;
}

h3{
  color: var(--myPink)
}

input, select{
  width: 100%;
  border: 1px solid var(--darkPink);
  border-radius: 3px;
  margin-bottom: 2px;
  background-color: var(--myBG);
  color: var(--color-text);
}

p{
  margin: 0px;
}

p.name{
  font-weight: bold;
}

p.score{
  color: var(--myPink)
}

</style>