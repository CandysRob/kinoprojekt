<!--
  Avaleht (/): kõik filmid.

  Kuidas filmid ekraanile jõuavad:
    1. onMounted käivitab load() kohe, kui leht on ekraanil.
    2. fetchMovies() teeb päringu GET /api/movies/ (src/api.js).
    3. Vite suunab päringu Djangole -> MovieViewSet (cinema/api_views.py)
       -> ORM päring PostgreSQL-i tabelisse "filmid" -> JSON.
    4. films.value = [...] ja Vue joonistab kaardid uuesti.
-->
<script setup>
import { onMounted, ref } from 'vue'

import { fetchMovies } from '../api.js'
import AsyncState from '../components/AsyncState.vue'
import FilmCard from '../components/FilmCard.vue'

// ref() teeb väärtuse reaktiivseks: kui seda muuta, uueneb ka leht
const films = ref([])
const loading = ref(true)
const error = ref('')

async function load() {
  loading.value = true
  error.value = ''
  try {
    films.value = await fetchMovies()
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <h1>Filmid</h1>
  <AsyncState
    :loading="loading"
    :error="error"
    :empty="films.length === 0"
    empty-text="Filme veel pole. Käivita arendusandmete käsk seed_dev_data."
    @retry="load"
  >
    <div class="film-grid">
      <FilmCard v-for="film in films" :key="film.id" :film="film" />
    </div>
  </AsyncState>
</template>
