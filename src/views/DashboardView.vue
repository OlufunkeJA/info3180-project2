<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { requestJson } from '@/services/api'

const router = useRouter()
const currentProfile = ref(null)
const profiles = ref([])
const loading = ref(true)
const errorMessage = ref('')

function formatLocation(profile) {
  return [profile.city, profile.parish, profile.country].filter(Boolean).join(', ') || 'Location not set'
}

async function loadDashboard() {
  loading.value = true
  errorMessage.value = ''

  const [myProfileResponse, profilesResponse] = await Promise.all([
    requestJson('/api/profile'),
    requestJson('/api/profiles')
  ])

  if (myProfileResponse.response.ok) {
    currentProfile.value = myProfileResponse.data.profile
  } else if (myProfileResponse.response.status === 404) {
    currentProfile.value = null
    errorMessage.value = 'Create your profile to start browsing.'
  } else {
    errorMessage.value = myProfileResponse.data?.error || 'Unable to load your profile.'
  }

  if (profilesResponse.response.ok) {
    profiles.value = profilesResponse.data.profiles || []
  } else if (!errorMessage.value) {
    errorMessage.value = profilesResponse.data?.error || 'Unable to load profiles.'
  }

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

      <div class="matches">
        <h3>Browse Profiles</h3>

        <p v-if="errorMessage" class="status-message">{{ errorMessage }}</p>
        <p v-if="loading">Loading profiles...</p>
        <p v-else-if="profiles.length === 0">No profiles are available right now.</p>

        <div class="matchCard" v-for="match in profiles" :key="match.id">
          <img :src="match.avatar_url || '/src/assets/logo.svg'">

          <div class="matchCard-right">
            <div class="text">
              <p class="name">{{ match.display_name }} <span v-if="match.handle">@{{ match.handle }}</span></p>
              <p>{{ match.about_me || 'No bio yet.' }}</p>
              <p class="score">{{ match.age ? `${match.age} years old` : 'Age not listed' }}</p>
            </div>

            <div class="buttons">
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