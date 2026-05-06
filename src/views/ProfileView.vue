<template>
    <h2>{{ message }}</h2>
</template>

<script setup>
import { ref } from "vue";

let msg = ref("Welcome!");
let age = ref(0);
let location = ref("");
let bio = ref("");

fetch("/api/profile", {
  method: 'GET'
})
.then(function (response) {
  return response.json();
})
.then(function (data) {
  msg.value = "Welcome, " + data.fName + data.lName + "!";
  age.value = data.age;
  location.value = data.location;
  bio.value = data.bio;
})
.catch(function (error) {
  console.log(error);
});

</script>

<style>
</style>