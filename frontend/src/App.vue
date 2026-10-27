<!--
  Põhikomponent: päis ja jalus on igal lehel samad.
  <RouterView> asemele paneb Vue Router praeguse aadressi lehe (router.js).
-->
<script setup>
import AppHeader from './components/AppHeader.vue'
</script>

<template>
  <AppHeader />
  <main class="page">
    <RouterView />
  </main>
  <footer class="site-footer">Õppeprojekt: filmid ja kinod on väljamõeldud.</footer>
</template>
