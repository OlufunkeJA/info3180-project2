<template>
    <div class="container">
        <div class="profile">
            <form @submit.prevent="editProfile" id="editForm">
                <p class="current">Current Email: {{ email }}</p>
                <label for="email" class="form-label">New Email</label>
                <input type="text" name="email" placeholder="Example: grp02@gmail.com"/>

                <p class="current">Current First Name: {{ fName }}</p>
                <label for="fName" class="form-label">New First Name</label>
                <input type="text" name="fName" placeholder="Example: Jane"/>

                <p class="current">Current Last Name: {{ lName }}</p>
                <label for="lName" class="form-label">New Last Name</label>
                <input type="text" name="lName" placeholder="Example: Doe"/>

                <p class="current">Current Date of Birth: {{ dob }}</p>
                <label for="dob" class="form-label">New Date of Birth</label>
                <input type="date" name="dob"/>

                <p class="current">Current Gender: {{ gender }}</p>
                <label for="gender" class="form-label">New Gender</label>
                <select type="text" name="gender" class="gender"> 
                    <option value="select" selected>Select Gender</option>
                    <option value="Female">Female</option>
                    <option value="Male">Male</option>
                </select>

                <p class="current">Current Looking For: {{ look }}</p>
                <label for="anyGender" class="form-label">New Looking For</label>
                <select type="text" name="anyGender" class="anyGender"> 
                    <option value="any" selected>Any</option>
                    <option value="Female">Female</option>
                    <option value="Male">Male</option>
                </select>

                <p class="current">Change Password</p>
                <label for="password" class="form-label">Old Password</label>
                <input type="text" name="password">
                <label for="password" class="form-label">New Password</label>
                <input type="text" name="password" placeholder="Example: pwd123">

                <input type="submit" name="submit" class="submit" value="Submit Changes">
            </form>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from "vue";

let fName = ref("Olufunke");
let lName = ref("Ogunde");
let age = ref(21);
let location = ref("St Andrew, Jamaica");
let bio = ref("Just a girl looking for her fairytale romance ✨💗");
let email = ref("grp02@gmail.com");
let look = ref("A big boy!");
let gender = ref("Female");

fetch("/api/profile", {
  method: 'GET'
})
.then(function (response) {
  return response.json();
})
.then(function (data) {
  fName.value = data.fName;
  lName.value = data.lName
  age.value = data.age;
  location.value = data.location;
  bio.value = data.bio;
  email.value = data.email;
  look.value = data.looking;
  gender.value = data.gender;
})
.catch(function (error) {
  console.log(error);
});

function editProfile(){
    let editForm = document.getElementById('editForm');
    let form_data = new FormData(editForm);

    fetch("/api/profile", {
        method: 'POST',
        body: form_data,
        headers: {
            'X-CSRFToken': csrf_token.value
        }
    })
    .then(function (response) {
        if (response.status == 200){
            msg.value = ["Changes successful"];
            type.value = "success";
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

label, input, select{
    margin: 0px;
}

p.current{
    margin: 0px;
    color: var(--myPink);
    font-weight: bold;
    margin-top: 20px;
}

</style>