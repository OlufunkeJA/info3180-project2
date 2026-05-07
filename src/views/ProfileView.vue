<template>
    <div class="container">
        <div class="profile">
            <div class="top">
                <img :src="avatarUrl || '../assets/logo.svg'" :alt="`${fName} ${lName}`" />
                <h3>{{ fName }} {{ lName }}, {{ age }}</h3>
                <p>Gender: {{ gender }}</p>
                <p>Location: {{location}}</p>
                <p>Bio: {{ bio }}</p>
            </div>

            <div class="bottom">
                <div class="info">
                    <p>Email address: {{ email }}</p>
                    <p>Looking for: {{ look }}</p>
                </div>

                <button v-on:click="editProfile" class="edit">Edit</button>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { requestJson } from '@/services/api'

const router = useRouter();

let fName = ref("");
let lName = ref("");
let age = ref('');
let location = ref("");
let bio = ref("");
let email = ref("");
let look = ref("");
let gender = ref("");
let avatarUrl = ref('')

async function loadProfile() {
  const { response, data } = await requestJson('/api/profile')

  if (response.ok && data.profile) {
    const profile = data.profile
    fName.value = profile.first_name || ''
    lName.value = profile.surname || ''
    age.value = profile.age ?? ''
    location.value = [profile.city, profile.parish, profile.country]
      .filter(Boolean)
      .join(', ')
    bio.value = profile.about_me || ''
    email.value = profile.email_address || ''
    look.value = profile.seeking || ''
    gender.value = profile.gender || ''
    avatarUrl.value = profile.avatar_url || ''
  } else {
    console.error(data?.error || 'Unable to load profile.')
  }
}

function editProfile() {
  router.push('/edit-profile')
}

onMounted(loadProfile)
</script>

<style>
button.edit{
    border: none;
    color: var(--color-text);
    background-color: rgba(235, 45, 76, 0.2);
    padding: 8px;
    margin: 10px;
    border-radius: 3px;
    width: 10%;
}

div.top{
    background-color: rgba(235, 45, 76, 0.2);
    padding: 20px;
    margin: 0px;
    border-radius: 17px 17px 0px 0px;
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}

div.bottom{
    padding: 10px;
    margin: 0px;
    border-radius: 0px 0px 17px 17px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}

div.profile{
    width: 100%;
    overflow: hidden;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

h2{
    color: var(--myPink);
}

img{
    border-radius: 1000px;
    border: 1px solid black;
    width: 15%;
}

p{
    margin: 0px;
    color: var(--color-text);
}

</style>