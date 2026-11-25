<!--
  Seansside leht (/seansid): kõik tulevased seansid ühes tabelis algusaja järgi.

  Kuupäeva filter: kui kasutaja valib kuupäeva, käivitab watch() uuesti load()
  ja päring on GET /api/screenings/?date=2026-11-28. Filtreerib backend, mitte Vue.
-->
<script setup>
import { onMounted, ref, watch } from 'vue'

import { fetchScreenings } from '../api.js'
import AsyncState from '../components/AsyncState.vue'
import { formatDate, formatPrice, formatTime } from '../format.js'

const screenings = ref([])
const loading = ref(true)
const error = ref('')
// Valitud kuupäev kujul "2026-11-28", tühi = kõik tulevased seansid
const selectedDate = ref('')

async function load() {
  loading.value = true
  error.value = ''
  try {
    screenings.value = await fetchScreenings(null, selectedDate.value)
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

onMounted(load)
// Kuupäeva muutmisel (ka tühjendamisel) laeme seansid uuesti
watch(selectedDate, load)
</script>

<template>
  <h1>Seansid</h1>

  <div class="date-filter">
    <label for="screening-date">Kuupäev</label>
    <input id="screening-date" v-model="selectedDate" type="date" />
    <button v-if="selectedDate" type="button" class="button" @click="selectedDate = ''">Näita kõiki seansse</button>
  </div>
  <p v-if="selectedDate" class="muted">Seansid {{ formatDate(selectedDate) }}</p>

  <AsyncState
    :loading="loading"
    :error="error"
    :empty="screenings.length === 0"
    :empty-text="selectedDate ? `${formatDate(selectedDate)} tulevasi seansse pole. Vali teine kuupäev.` : 'Tulevasi seansse pole.'"
    @retry="load"
  >
    <table class="table">
      <thead>
        <tr>
          <th>Kuupäev</th>
          <th>Kell</th>
          <th>Film</th>
          <th>Kino</th>
          <th class="hide-mobile">Saal</th>
          <th class="hide-mobile">Hind</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="screening in screenings" :key="screening.id">
          <td>{{ formatDate(screening.starts_at) }}</td>
          <td>{{ formatTime(screening.starts_at) }}</td>
          <td>
            <RouterLink :to="{ name: 'film', params: { id: screening.movie.id } }">{{ screening.movie.title }}</RouterLink>
          </td>
          <td>{{ screening.cinema.name }}</td>
          <td class="hide-mobile">{{ screening.hall.name }}</td>
          <td class="hide-mobile">{{ formatPrice(screening.base_price) }}</td>
        </tr>
      </tbody>
    </table>
  </AsyncState>
</template>
