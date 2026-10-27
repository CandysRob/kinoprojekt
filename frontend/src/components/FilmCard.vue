<!--
  Üks film filmide nimekirjas. Vanem (FilmsView) annab filmi propsina,
  kaart ainult näitab seda ega muuda midagi.
-->
<script setup>
import { year } from '../format.js'
import FilmPoster from './FilmPoster.vue'

defineProps({
  // Kuju tuleb failist cinema/serializers.py (MovieListSerializer)
  film: { type: Object, required: true },
})
</script>

<template>
  <article class="film-card">
    <RouterLink :to="{ name: 'film', params: { id: film.id } }">
      <FilmPoster :title="film.title" :url="film.poster_url" />
      <h3>{{ film.title }}</h3>
    </RouterLink>
    <p class="muted small">{{ film.genres.map((genre) => genre.name).join(', ') }}</p>
    <p class="muted small">{{ year(film.release_date) }}</p>
  </article>
</template>
