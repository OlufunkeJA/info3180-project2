<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();

let msg = ref("Welcome!")
let age = ref(21)
let location = ref("Kingston, Jamaica")
let bio = ref("Sample bio")
let matches = ref([{"name":"Orville", "bio":"A big nerd with an even bigger heart.", "score": 90}, {"name":"Del","bio":"Love me a good Lana concert; avoid me if you don't!", "score": 75}])

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

function edit(){
  router.push('/profile');
}

fetch("/api/profiles", {
  method: 'GET'
})
.then(function (response) {
  return response.json();
})
.then(function (data) { 
  matches.value = data;
})
.catch(function (error) {
  console.log(error);
});

function like(){
  fetch("/api/", {
  method: 'POST'
})
}

function pass(){
  fetch("/api/", {
  method: 'POST'
})
}

function search(){
  let filterForm = document.getElementById('filterForm');
  let form_data = new FormData(filterForm);

  fetch("/api/profiles", {
    method: 'GET',
    body: form_data,
    headers: {
    'X-CSRFToken': csrf_token.value
    }
  })
  .then(function (response) {
    return response.json();
  })
  .then(function (data) { 
    matches.value = data;
  })
  .catch(function (error) {
    console.log(error);
  });
}

function getCsrfToken() {
  fetch('/api/csrf-token')
  .then((response) => response.json())
  .then((data) => { console.log(data);
  csrf_token.value = data.csrf_token;
  })
}

onMounted(() => {
  getCsrfToken()
})

function reset(){
  this.
  this.$refs.filterForm.reset();
}

</script>

<template>
    <div class="container">
      <div class="myCard">
        <img src="../assets/logo.svg">

        <div class="card-right">
          <h1>{{ msg }}</h1>
          <p>Age: {{ age }}</p>
          <p>Location: {{ location }}</p> 
          <p>Bio: {{ bio }}</p>
          <button v-on:click="edit">Edit Profile</button>
        </div>
      </div>

      <div class="matches">
        <h3>Browse Possible Matches</h3>

        <form @submit.prevent="search" id="filterForm" ref="filterForm">
          <input type="text" name="filter" class="filter" placeholder="Search by name or bio.."/>
          <select type="text" name="anyGender" class="anyGender"> 
            <option value="all" selected>All Ages</option>
            <option value="young">18-25</option>
            <option value="mid">25-35</option>
            <option value="older">35-45</option>
            <option value="oldest">45+</option>
          </select>
          <input type="text" name="locFilter" class="filter" placeholder="Filter by location.."/>
        </form>

        <button v-on:click="search" class="search">Show Interest Filters</button>
        <button v-on:click="reset" class="reset">Reset Filters</button>

        <div class="matchCard" v-for="match in matches">
          <img src="../assets/logo.svg">

          <div class="matchCard-right">          
            <div class="text">
              <p class="name">{{ match.name }}</p>
              <p>{{ match.bio }}</p>
              <p class="score">Match Score: {{ match.score }}%</p>
            </div>

            <div class="buttons">
              <button v-on:click="like" class="like">Like</button>
              <button v-on:click="dislike" class="dislike">Dislike</button>
              <button v-on:click="pass" class="pass">Pass</button>
            </div>
          </div>
        </div>
      </div>
    </div>
</template>

<style>
/* Add any component specific styles here */
button{
  border: none;
  color: var(--myBG);
  background-color: var(--myPink);
  border-radius: 3px;
  padding: 3px;
  width: 100%;
}

button.like{
  background-color: var(--darkPink);
  margin: 2px;
  padding: 10px;
}

button.dislike{
  padding: 10px;
  margin: 2px;
  background-color: var(--myPink);
}

button.pass{
  background-color: var(--myBG);
  color: var(--darkPink);
  border: 1px solid var(--darkPink);
  margin: 2px;
  padding: 10px;
}

button.search{
  background-color: var(--darkPink);
  margin: 2px;
}

button.reset{
  background-color: var(--myBG);
  color: var(--darkPink);
  border: 1px solid var(--darkPink);
  margin: 2px;
}

img{
  float: left;
  width: 10%;
}

div.buttons{
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  float: right;
  grid-area: "buttons";
  float: right;
}

div.card-right{
  float: right;
  width: 100%;
  margin-left: 30px;
}

form{
  display: flex;
  flex-direction: row;
  column-gap: 10px;
}

div.myCard, div.matches{
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  padding: 20px;
  border-radius: 2px;
  display: flex;
}

div.myCard{
  margin-bottom: 20px;
}

div.matchCard{
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  padding: 20px;
  border-radius: 2px;
  display: flex;
}

div.matchCard-right{
  width: 100%;
  margin-left: 30px;
  grid-template-areas: "text buttons";
  grid-template-columns: 9fr 1fr;
}

div.matches{
  flex-direction: column;
}

div.text{
  display: flex;
  flex-direction: column;
  grid-area: "text";
  float: left;
}

h1{
  color: var(--myPink);
  font-weight: bold;
  margin: 0px;
}

h3{
  color: var(--myPink)
}

input, select{
  width: 100%;
  border: 1px solid var(--darkPink);
  border-radius: 3px;
  margin-bottom: 2px;
  background-color: var(--myBG);
  color: var(--color-text);
}

p{
  margin: 0px;
}

p.name{
  font-weight: bold;
}

p.score{
  color: var(--myPink)
}

</style>