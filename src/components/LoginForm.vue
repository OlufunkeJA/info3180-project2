<template>
    <div class="control">
        <div class="formDiv">
            <h3>Login</h3>

            <form @submit.prevent="login" id="loginForm">
                <label for="email" class="form-label">Email</label>
                <input v-model="form.email_address" type="email" name="email_address" class="email" placeholder="Example: grp02@gmail.com" autocomplete="email" required />
                <label for="password" class="form-label">Password</label>
                <input v-model="form.password" type="password" name="password" class="password" placeholder="Example: pwd123" autocomplete="current-password" required>
                <input type="submit" name="submit" class="submit">
            </form>

            <p>Don't have an account?</p>
            <a v-on:click="signup" class="link">Sign up here</a>
        </div>

        <div :class="type" class="alert">
            <div v-if="show" v-for="line in msg">
                {{ line }}
            </div>
        </div>
    </div>
</template>

<script setup>
import { reactive, ref, onMounted} from 'vue'
import { useRouter } from 'vue-router'

import { requestJson } from '@/services/api'
import { setSessionAccount, setFlash } from '@/services/session'

const router = useRouter()

const form = reactive({
  email_address: '',
  password: ''
})

const show = ref(false)
const msg = ref([])
const type = ref('')

async function login() {
  const { response, data } = await requestJson('/api/login', {
    method: 'POST',
    body: form,
  })

  if (response.ok) {
    setSessionAccount(data.account)
    setFlash(data.message || 'Login successful.', 'success')
    router.push('/')
    return
  }

  type.value = 'error'
  msg.value = data?.errors || [data?.error || 'Login failed.']
  show.value = true
}

function signup() {
  router.push('/signup')
}

</script>

<style>
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
    width: 30%;
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
    padding: 20px;
    margin-bottom: 20px;
}

div.control{
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}

form > input.email, input.password{
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

p{
    margin-top: 10px;
    margin-bottom: 0px;
}
</style>