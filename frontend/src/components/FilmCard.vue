<script setup>
import { computed } from "vue";

import { formatDuration, formatYear } from "../utils/format";
import FilmPoster from "./FilmPoster.vue";

const props = defineProps({
  film: { type: Object, required: true },
});

const meta = computed(() =>
  [formatYear(props.film.release_date), formatDuration(props.film.duration_minutes)].filter(Boolean).join(" · "),
);
const genres = computed(() => props.film.genres.map((g) => g.name).join(", "));
</script>

<template>
  <article class="film-card">
    <RouterLink :to="`/filmid/${film.id}`" class="film-link">
      <div class="poster-wrap">
        <FilmPoster :title="film.title" :url="film.poster_url" />
        <span v-if="film.age_rating" class="tag tag-rating">{{ film.age_rating }}</span>
      </div>
      <h3 class="film-title">{{ film.title }}</h3>
    </RouterLink>
    <p v-if="meta" class="film-meta">{{ meta }}</p>
    <p v-if="genres" class="film-genres">{{ genres }}</p>
  </article>
</template>

<style scoped>
.film-card {
  min-width: 0;
}

.film-link {
  display: block;
  text-decoration: none;
}

.poster-wrap {
  position: relative;
  transition: transform 200ms ease;
}

.film-link:hover .poster-wrap {
  transform: translateY(-4px);
}

.film-link:focus-visible {
  outline: none;
}

.film-link:focus-visible .poster-wrap {
  outline: 2px solid var(--color-focus);
  outline-offset: 3px;
  border-radius: var(--radius-md);
}

.tag-rating {
  position: absolute;
  top: var(--space-2);
  left: var(--space-2);
  border-color: transparent;
  background: rgb(15 13 19 / 0.8);
  color: var(--color-text);
  backdrop-filter: blur(4px);
}

.film-title {
  margin-top: var(--space-3);
  font-size: var(--text-md);
  font-weight: 600;
  line-height: 1.25;
}

.film-link:hover .film-title {
  color: var(--color-accent);
}

.film-meta,
.film-genres {
  margin-top: var(--space-1);
  font-size: var(--text-sm);
  color: var(--color-text-muted);
}

.film-genres {
  color: var(--color-text-faint);
}
</style>
