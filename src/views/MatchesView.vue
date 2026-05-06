<template>
  <div class="container">
    <h2>Your Matches</h2>

    <div class="matches">
        <div class="matchCard" v-for="match in matches">
          <img src="../assets/logo.svg">

          <div class="matchCard-right">  
            <p class="name">{{ match.name }}, {{ match.age }}</p>
            <p>{{ match.bio }}</p>
            <button v-on:click="message" class="message">Message</button>
          </div>
        </div>
    </div>
  </div> 
</template>

<script setup>
import { ref } from "vue";

let matches = ref([{"name":"Orville", "bio":"A big nerd with an even bigger heart.", "age": 22}, {"name":"Del","bio":"Love me a good Lana concert; avoid me if you don't!", "age": 23}])

fetch("/api/", {
  method: 'GET'
})
.then(function (response) {
  return response.json();
})
.then(function (data) { 
  matches.value = data;
})
.catch(function (error) {
  //console.log(error);
});

function message(){
  fetch("/api/", {
  method: 'GET'
})
}
</script>

<style>
  h2{
    color: var(--myPink);
  }
</style>
