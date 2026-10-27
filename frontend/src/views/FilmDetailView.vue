<!--
  Filmi leht (/filmid/:id). Ruuter annab aadressist :id propsina (router.js).
  Leht laeb kaks asja: filmi andmed ja selle filmi tulevased seansid.
-->
<script setup>
import { ref, watch } from 'vue'

import { fetchMovie, fetchScreenings } from '../api.js'
import AsyncState from '../components/AsyncState.vue'
import FilmPoster from '../components/FilmPoster.vue'
import { formatDate, formatPrice, formatTime, year } from '../format.js'

const props = defineProps({
  id: { type: String, required: true },
})

const film = ref(null)
const screenings = ref([])
const loading = ref(true)
const error = ref('')

async function load() {
  loading.value = true
  error.value = ''
  try {
    // Promise.all teeb mõlemad päringud korraga ja ootab, kuni mõlemad on valmis
    const [movie, movieScreenings] = await Promise.all([fetchMovie(props.id), fetchScreenings(props.id)])
    film.value = movie
    screenings.value = movieScreenings
  } catch (err) {
    film.value = null
    error.value = err.status === 404 ? 'Sellist filmi ei leitud.' : err.message
  } finally {
    loading.value = false
  }
}

// immediate: true laeb kohe ja uuesti, kui aadressis olev id muutub
watch(() => props.id, load, { immediate: true })
</script>

<template>
  <p><RouterLink to="/">← Kõik filmid</RouterLink></p>
  <AsyncState :loading="loading" :error="error" @retry="load">
    <article v-if="film" class="film-detail">
      <FilmPoster :title="film.title" :url="film.poster_url" />
      <div>
        <h1>{{ film.title }}</h1>
        <p class="muted">
          {{ film.genres.map((genre) => genre.name).join(', ') }}
          · {{ year(film.release_date) }} · {{ film.duration_minutes }} min
          <template v-if="film.age_rating"> · {{ film.age_rating }}</template>
        </p>
        <p>{{ film.description || 'Kirjeldus puudub.' }}</p>

        <h2>Seansid</h2>
        <p v-if="screenings.length === 0" class="muted">Sellel filmil pole praegu seansse.</p>
        <table v-else class="table">
          <thead>
            <tr>
              <th>Kuupäev</th>
              <th>Kell</th>
              <th>Kino</th>
              <th class="hide-mobile">Saal</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="screening in screenings" :key="screening.id">
              <td>{{ formatDate(screening.starts_at) }}</td>
              <td>{{ formatTime(screening.starts_at) }}</td>
              <td>{{ screening.cinema.name }}</td>
              <td class="hide-mobile">{{ screening.hall.name }} ({{ formatPrice(screening.base_price) }})</td>
            </tr>
          </tbody>
        </table>
        <p class="muted small">Piletite broneerimine pole veel valmis.</p>
      </div>
    </article>
  </AsyncState>
</template>
