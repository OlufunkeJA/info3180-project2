<template>
    <div :class="type" class="alert">
        <div v-if="show" v-for="line in msg">
            {{ line }}
        </div>
    </div>  

    <div class="control">
        <div class="formDiv">
            <h3>Create an Account</h3>

            <form @submit.prevent="signup" id="signupForm">
                <label for="email" class="form-label">Email</label>
                <input type="text" name="email" placeholder="Example: grp02@gmail.com"/>

                <label for="username" class="form-label">Username</label>
                <input type="text" name="username" placeholder="Example: grp02"/>

                <label for="fName" class="form-label">First Name</label>
                <input type="text" name="fName" placeholder="Example: Jane"/>

                <label for="lName" class="form-label">Last Name</label>
                <input type="text" name="lName" placeholder="Example: Doe"/>

                <label for="dob" class="form-label">Date of Birth</label>
                <input type="date" name="dob"/>

                <label for="gender" class="form-label">Gender</label>
                <select type="text" name="gender" class="gender"> 
                    <option value="select" selected>Select Gender</option>
                    <option value="female">Female</option>
                    <option value="male">Male</option>
                </select>

                <label for="anyGender" class="form-label">Looking For</label>
                <select type="text" name="anyGender" class="anyGender"> 
                    <option value="any" selected>Any</option>
                    <option value="female">Female</option>
                    <option value="male">Male</option>
                </select>

                <label for="password" class="form-label">Password</label>
                <input type="text" name="password" placeholder="Example: pwd123">

                <input type="submit" name="submit" class="submit" value="Sign Up">
            </form>

            <p>Already have an account?</p>
            <a v-on:click="login" class="link">Login here</a>
        </div>
    </div>

</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

import { requestJson } from '@/services/api'
import { setSessionAccount } from '@/services/session'

const router = useRouter()

const show = ref(false)
const msg = ref([])
const type = ref('')

async function signup() {
  const signupForm = document.getElementById('signupForm')
  const formData = new FormData(signupForm)
  const payload = {
    handle: String(formData.get('username') || '').trim(),
    email_address: String(formData.get('email') || '').trim(),
    password: String(formData.get('password') || ''),
    confirm_password: String(formData.get('password') || ''),
    first_name: String(formData.get('fName') || '').trim(),
    surname: String(formData.get('lName') || '').trim(),
    birthdate: String(formData.get('dob') || '').trim(),
    gender: String(formData.get('gender') || '').trim(),
    seeking: String(formData.get('anyGender') || 'any').trim(),
  }

  const { response, data } = await requestJson('/api/register', {
    method: 'POST',
    body: payload
  })

  if (response.ok) {
    setSessionAccount(data.account)
    type.value = 'success'
    msg.value = ['Signup successful.']
    show.value = true
    router.push('/')
    return
  }

  type.value = 'error'
  msg.value = data?.errors || [data?.error || 'Signup failed.']
  show.value = true
}

function login() {
  router.push('/login')
}
</script>

<style>
textarea{
    width: 100%;
}
a.link{
    float: right;
    text-decoration: none;
    margin-top: 0px;
}

a:hover{
    cursor: pointer;
    color: var(--myPink);
}

div.alert{
    margin-left: 20px;
    width: 70%;
    padding: 10px;
}

div.success{
    background-color: rgb(0,128,0,0.5);
    border-color: green;
    border-width: 1px;
    color: white;
}

div.error{
    background-color: rgb(255,0,0,0.5);
    border-color: red;
    border-width: 1px;
    color: white;
}

form{
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    border-radius: 5px;
    box-shadow: 10px;
}

div.formDiv{
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    width: 25%;
    padding: 20px;
}

div.control{
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}

form > input{
    margin: 2px;
}

form > input.submit{
    margin-top: 15px;
    text-decoration: none;
    border: none;
    border-radius: 3px;
    background-color: var(--myPink);
    color: white;
    padding: 2px;
}

h3{
    display: flex;
    justify-content: center;
    color: var(--myPink);
    font-weight: bold;
}

input, select{
    margin-top: 0px;
}

label{
    margin: 0px;
    float: left;
}

p{
    margin-top: 10px;
    margin-bottom: 0px;
}

select{
}
</style>