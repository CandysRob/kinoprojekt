<!-- Filmi plakat. Kui plakati aadressi pole (arendusandmetes pole), näidatakse halli kasti pealkirjaga. -->
<script setup>
defineProps({
  title: { type: String, required: true },
  url: { type: String, default: null },
})
</script>

<template>
  <img v-if="url" :src="url" :alt="title" class="poster" />
  <div v-else class="poster placeholder" role="img" :aria-label="title">{{ title }}</div>
</template>
