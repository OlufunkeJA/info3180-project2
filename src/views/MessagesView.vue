<template>
  <div class="msgContainer">
    <div class="messages">
      <div class="left">
        <button v-for="name in names" class="names" v-on:click="switchChat">{{ name }}</button>
      </div>

      <div class="right">
        <div class="top">
          <p v-for="message in messages" class="bubble">{{ message }}</p>
        </div>

        <div class="bottom">
          <input type="text" name="message" class="message" placeholder="Type a message.."/>
          <button v-on:click="send" class="send">Send</button>
        </div>

      </div>
    </div> 
  </div>
</template>

<script setup>
import { ref } from "vue";

let names = ref(["Del", "Orville", "Olu"]);
let messages= ref(["Hi! How are you?", "I'm good, thanks for asking", "Got plans for today?"]);

function switchChat(){

}

</script>

<style>
button.names{
  border: none;
  background-color: var(--myBG);
  color: var(--color-text);
  font-weight: bold;
  display: flex;
}

button.send{
  background-color: var(--myPink);
  border-radius: 3px;
  color: var(--myBG);
  padding: 3px;
  width: 9%;
  float: right;
  border: none;
}

div.msgContainer{
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 5px;
}

div.messages{
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  padding: 20px;
  border-radius: 2px;
  display: grid;
  grid-template-areas: "left right";
  grid-template-columns: 1fr 4fr;
  width: 80%;
  align-items: center;
}

div.right{
  grid-area: "right";
  width: 100%;
}

div.left{
  grid-area: "left";
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: flex-start;
}

input{
  width: 90%;
  border-radius: 5px;
  border: 2px solid var(--color-border);
  margin: 1px;
}

p.bubble{
  background-color: var(--myPink);
  border-radius: 5px;
  color: var(--myBG);
  padding: 2px;
  margin: 2px;
}

</style>
