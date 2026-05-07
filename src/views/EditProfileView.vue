<template>
    <div class="container">
        <div class="profile">
            <form @submit.prevent="editProfile" id="editForm">
                <p class="current">Current First Name: {{ fName }}</p>
                <label for="fName" class="form-label">First Name</label>
                <input v-model="fName" type="text" name="fName" placeholder="Example: Jane" required />

                <p class="current">Current Last Name: {{ lName }}</p>
                <label for="lName" class="form-label">Last Name</label>
                <input v-model="lName" type="text" name="lName" placeholder="Example: Doe" required />

                <p class="current">Current Date of Birth: {{ dob }}</p>
                <label for="dob" class="form-label">Date of Birth</label>
                <input v-model="dob" type="date" name="dob" required />

                <p class="current">Current Gender: {{ gender }}</p>
                <label for="gender" class="form-label">Gender</label>
                <select v-model="gender" type="text" name="gender" class="gender" required>
                    <option value="female">Female</option>
                    <option value="male">Male</option>
                    <option value="other">Other</option>
                </select>

                <p class="current">Current Looking For: {{ look }}</p>
                <label for="anyGender" class="form-label">Looking For</label>
                <select v-model="look" type="text" name="anyGender" class="anyGender">
                    <option value="any">Any</option>
                    <option value="female">Female</option>
                    <option value="male">Male</option>
                </select>

                <label for="about" class="form-label">About Me</label>
                <textarea v-model="bio" name="about" placeholder="Tell others about yourself"></textarea>

                <label class="form-label">Profile Image</label>
                <div class="avatar-row">
                  <input
                    ref="avatarInput"
                    type="file"
                    name="profile_picture"
                    accept="image/*"
                    @change="onAvatarSelected"
                  />
                  <img v-if="avatarPreview" :src="avatarPreview" alt="Current avatar" class="avatar-preview" />
                </div>

                <label for="parish" class="form-label">Parish</label>
                <input v-model="parish" type="text" name="parish" placeholder="Example: Kingston" />

                <label for="city" class="form-label">City</label>
                <input v-model="city" type="text" name="city" placeholder="Example: Kingston" />

                <label for="country" class="form-label">Country</label>
                <input v-model="country" type="text" name="country" placeholder="Example: Jamaica" />

                <label for="job" class="form-label">Job Title</label>
                <input v-model="job" type="text" name="job" placeholder="Example: Developer" />

                <label for="schooling" class="form-label">Schooling</label>
                <input v-model="schooling" type="text" name="schooling" placeholder="Example: Bachelor's" />

                <label for="minAge" class="form-label">Minimum Interested Age</label>
                <input v-model="minAge" type="number" name="minAge" min="18" max="99" />

                <label for="maxAge" class="form-label">Maximum Interested Age</label>
                <input v-model="maxAge" type="number" name="maxAge" min="18" max="99" />

                <label for="visible" class="form-label">Visible</label>
                <select v-model="visible" name="visible">
                    <option value="true">Yes</option>
                    <option value="false">No</option>
                </select>

                <input type="submit" name="submit" class="submit" value="Submit Changes">
            </form>

            <div :class="type" class="alert" v-if="show">
                <div v-for="line in msg" :key="line">{{ line }}</div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { requestJson } from '@/services/api'

const fName = ref("")
const lName = ref("")
const dob = ref("")
const gender = ref("")
const look = ref("any")
const bio = ref("")
const parish = ref("")
const city = ref("")
const country = ref("Jamaica")
const job = ref("")
const schooling = ref("")
const minAge = ref(18)
const maxAge = ref(99)
const visible = ref('true')

const avatarFile = ref(null)
const avatarPreview = ref('')
const show = ref(false)
const type = ref('')
const msg = ref([])

function onAvatarSelected(event) {
  const file = event.target.files?.[0]
  if (file) {
    avatarFile.value = file
    avatarPreview.value = URL.createObjectURL(file)
  }
}

async function loadProfile() {
  const { response, data } = await requestJson('/api/profile')

  if (response.ok && data.profile) {
    const profile = data.profile
    fName.value = profile.first_name || ''
    lName.value = profile.surname || ''
    dob.value = profile.birthdate || ''
    gender.value = profile.gender || ''
    look.value = profile.seeking || 'any'
    bio.value = profile.about_me || ''
    parish.value = profile.parish || ''
    city.value = profile.city || ''
    country.value = profile.country || 'Jamaica'
    job.value = profile.job_title || ''
    schooling.value = profile.schooling || ''
    minAge.value = profile.min_age || 18
    maxAge.value = profile.max_age || 99
    visible.value = profile.visible ? 'true' : 'false'
    avatarPreview.value = profile.avatar_url || ''
  } else {
    console.error(data?.error || 'Unable to load profile.')
  }
}

async function editProfile() {
  const formData = new FormData()
  formData.append('first_name', fName.value)
  formData.append('surname', lName.value)
  formData.append('birthdate', dob.value)
  formData.append('gender', gender.value)
  formData.append('seeking', look.value)
  formData.append('about_me', bio.value)
  formData.append('parish', parish.value)
  formData.append('city', city.value)
  formData.append('country', country.value)
  formData.append('job_title', job.value)
  formData.append('schooling', schooling.value)
  formData.append('min_age', String(minAge.value))
  formData.append('max_age', String(maxAge.value))
  formData.append('visible', visible.value)

  if (avatarFile.value) {
    formData.append('profile_picture', avatarFile.value)
  }

  const { response, data } = await requestJson('/api/profile', {
    method: 'PUT',
    body: formData,
  })

  if (response.ok) {
    type.value = 'success'
    msg.value = ['Profile updated successfully.']
  } else {
    type.value = 'error'
    msg.value = data?.errors || [data?.error || 'Unable to update profile.']
  }

  show.value = true
}

onMounted(loadProfile)
</script>

<style>
input.submit{
    border: none;
    color: var(--color-text);
    background-color: var(--myPink);
    padding: 8px;
    margin: 10px;
    border-radius: 3px;
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

form{
    display: flex;
    flex-direction: column;
    padding: 20px;
}

h2{
    color: var(--myPink);
}

img{
    border-radius: 1000px;
    border: 1px solid black;
    width: 15%;
}

label, input, select, textarea {
    margin: 0px;
    background-color: var(--color-background);
    color: var(--color-text);
    border: none;
}

input, select, textarea {
    border: 1px solid var(--color-text);
    border-radius: 3px;
}

.avatar-row {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 12px;
}

.avatar-preview {
    width: 64px;
    height: 64px;
    object-fit: cover;
    border-radius: 50%;
    border: 1px solid var(--color-border);
}

p.current{
    margin: 0px;
    color: var(--myPink);
    font-weight: bold;
    margin-top: 20px;
}

</style>