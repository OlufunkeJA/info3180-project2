<template>
    <div class="control">
        <div class="formDiv">
            <h3>Login</h3>

            <form @submit.prevent="login" id="loginForm">
                <label for="email" class="form-label">Email</label>
                <input type="text" name="email" class="email" placeholder="Example: grp02@gmail.com"/>
                <label for="password" class="form-label">Password</label>
                <input type="text" name="password" class="password" placeholder="Example: pwd123">
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
    import { ref, onMounted } from "vue";
    import { useRouter } from "vue-router";
    const router = useRouter()

    let csrf_token = ref("");
    let show = ref(false);
    let msg = ref("");
    let type = ref("");

    function login(){
        let loginForm = document.getElementById('loginForm');
        let form_data = new FormData(loginForm);

        fetch("/api/login", {
            method: 'POST',
            body: form_data,
            headers: {
                'X-CSRFToken': csrf_token.value
            }
        })
        .then(function (response) {
            if (response.status == 200){
                msg.value = ["Login Successful!"];
                type.value = "success";
            }
            else{
                type.value = "error";
                msg.value = ["Credentials incorrect!"]
            }

            return response.json();
        })
        .catch(function (error) {
            console.log(error);
        });
    }

    function getCsrfToken() {
        fetch('/api/v1/csrf-token')
        .then((response) => response.json())
        .then((data) => { console.log(data);
        csrf_token.value = data.csrf_token;
        })
    }

    onMounted(() => {
        getCsrfToken()
    })

    function signup(){
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
    width: 25%;
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
    width: 120%;
}

form > input.submit{
    margin-top: 15px;
    width: 120%;
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