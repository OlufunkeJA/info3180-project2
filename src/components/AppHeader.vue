<template>
  <header>
    <nav class="navbar navbar-expand-lg navbar-dark fixed-top">
      <div class="container-fluid">
        <a class="navbar-brand" href="/">Drift Dater</a>
        <button
          class="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#navbarSupportedContent"
          aria-controls="navbarSupportedContent"
          aria-expanded="false"
          aria-label="Toggle navigation"
        >
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarSupportedContent">
          <ul class="navbar-nav me-auto">
            <li class="nav-item">
              <RouterLink to="/" class="nav-link active">Dashboard</RouterLink>
            </li>
            <li class="nav-item">
              <RouterLink class="nav-link" to="/matches">Matches</RouterLink>
            </li>
            <li class="nav-item">
              <RouterLink class="nav-link" to="/messages">Messages</RouterLink>
            </li>
            <li class="nav-item" v-if="true">
              <RouterLink class="nav-link" to="/login">Login</RouterLink>
            </li>
          </ul>
        </div>
      </div>
    </nav>
  </header>
</template>

<script setup>
import { RouterLink } from "vue-router";


</script>

<style>
/* Add any component specific styles here */
:root{
  --myPink: rgb(235, 45, 76);
}

nav{
  background-image: linear-gradient(to right, var(--myPink), rgb(255, 25, 64));
}
</style>