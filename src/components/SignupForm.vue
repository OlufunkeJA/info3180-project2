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
                    <option value="Female">Female</option>
                    <option value="Male">Male</option>
                </select>

                <label for="anyGender" class="form-label">Looking For</label>
                <select type="text" name="anyGender" class="anyGender"> 
                    <option value="any" selected>Any</option>
                    <option value="Female">Female</option>
                    <option value="Male">Male</option>
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
    import { ref, onMounted } from "vue";
    import { useRouter } from "vue-router";

    const router = useRouter();

    let csrf_token = ref("");
    let show = ref(false);
    let msg = ref("");
    let type = ref("");

    function signup(){
        let signupForm = document.getElementById('signupForm');
        let form_data = new FormData(signupForm);

        fetch("/api/register", {
            method: 'POST',
            body: form_data,
            headers: {
                'X-CSRFToken': csrf_token.value
            }
        })
        .then(function (response) {
            if (response.status == 200){
                msg.value = ["Signup Successful!"];
                type.value = "success";
                router.push('/dashboard');
            }
            else{
                type.value = "error";
            }

            return response.json();
        })
        .then(function (data) {
            // display a success message
            if (type.value == "error"){
                msg.value = data;
                console.log(msg);
            }

            show.value = true;
            console.log(data);
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

    function login(){
        router.push('/login');
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
    width: 120%;
}
</style>