<template>
    <div class="container">
        <h2>{{ msg }}</h2>

        <div class="profile">
            <div class="top">
                <img src="../assets/logo.svg">
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
import { ref } from "vue";

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