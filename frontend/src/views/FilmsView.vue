<!--
  Avaleht (/): kõik filmid.

  Kuidas filmid ekraanile jõuavad:
    1. onMounted käivitab load() kohe, kui leht on ekraanil.
    2. fetchMovies() teeb päringu GET /api/movies/ (src/api.js).
    3. Vite suunab päringu Djangole -> MovieViewSet (cinema/api_views.py)
       -> ORM päring PostgreSQL-i tabelisse "filmid" -> JSON.
    4. films.value = [...] ja Vue joonistab kaardid uuesti.

  Kuupäeva filter: kui kasutaja valib kuupäeva, käivitab watch() uuesti load()
  ja päring on GET /api/movies/?date=2026-11-28. Filtreerib backend, mitte Vue.
-->
<script setup>
import { onMounted, ref, watch } from 'vue'

import { fetchMovies } from '../api.js'
import AsyncState from '../components/AsyncState.vue'
import FilmCard from '../components/FilmCard.vue'
import { formatDate } from '../format.js'

// ref() teeb väärtuse reaktiivseks: kui seda muuta, uueneb ka leht
const films = ref([])
const loading = ref(true)
const error = ref('')
// Valitud kuupäev kujul "2026-11-28", tühi = kõik filmid
const selectedDate = ref('')

async function load() {
  loading.value = true
  error.value = ''
  try {
    films.value = await fetchMovies(selectedDate.value)
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

onMounted(load)
// Kuupäeva muutmisel (ka tühjendamisel) laeme filmid uuesti
watch(selectedDate, load)
</script>

<template>
  <h1>Filmid</h1>

  <div class="date-filter">
    <label for="screening-date">Seansi kuupäev</label>
    <input id="screening-date" v-model="selectedDate" type="date" />
    <button v-if="selectedDate" type="button" class="button" @click="selectedDate = ''">Näita kõiki filme</button>
  </div>
  <p v-if="selectedDate" class="muted">Filmid, mille seanss on {{ formatDate(selectedDate) }}</p>

  <AsyncState
    :loading="loading"
    :error="error"
    :empty="films.length === 0"
    :empty-text="
      selectedDate
        ? `${formatDate(selectedDate)} seansse pole. Vali teine kuupäev.`
        : 'Filme veel pole. Käivita arendusandmete käsk seed_dev_data.'
    "
    @retry="load"
  >
    <div class="film-grid">
      <FilmCard v-for="film in films" :key="film.id" :film="film" />
    </div>
  </AsyncState>
</template>
