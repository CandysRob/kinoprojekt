<!-- Seansside leht (/seansid): kõik tulevased seansid ühes tabelis algusaja järgi. -->
<script setup>
import { onMounted, ref } from 'vue'

import { fetchScreenings } from '../api.js'
import AsyncState from '../components/AsyncState.vue'
import { formatDate, formatPrice, formatTime } from '../format.js'

const screenings = ref([])
const loading = ref(true)
const error = ref('')

async function load() {
  loading.value = true
  error.value = ''
  try {
    screenings.value = await fetchScreenings()
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <h1>Seansid</h1>
  <AsyncState
    :loading="loading"
    :error="error"
    :empty="screenings.length === 0"
    empty-text="Tulevasi seansse pole."
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
