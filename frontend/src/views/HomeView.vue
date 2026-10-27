<script setup>
import { computed } from "vue";

import { getMovies, getScreenings } from "../api/cinema";
import FilmCard from "../components/FilmCard.vue";
import FilmGridSkeleton from "../components/FilmGridSkeleton.vue";
import FilmPoster from "../components/FilmPoster.vue";
import StateMessage from "../components/StateMessage.vue";
import { useRequest } from "../composables/useRequest";
import { formatDayLabel, formatDuration, formatTime, toDateKey } from "../utils/format";

const featured = useRequest((options) => getMovies({ featured: "true", now_showing: "true", page_size: 1 }, options));
const nowShowing = useRequest((options) => getMovies({ now_showing: "true", page_size: 10 }, options));
const nextScreenings = useRequest((options) => getScreenings({ page_size: 8 }, options));

const heroFilm = computed(() => featured.data.value?.results[0]);
const heroMeta = computed(() => {
  const film = heroFilm.value;
  if (!film) return "";
  return [film.genres.map((g) => g.name).join(", "), formatDuration(film.duration_minutes)].filter(Boolean).join(" · ");
});
</script>

<template>
  <div>
    <section class="hero">
      <div class="container hero-inner">
        <div class="hero-text">
          <p class="eyebrow">{{ heroFilm ? "Esile tõstetud" : "Tere tulemast" }}</p>
          <h1 class="hero-title">{{ heroFilm ? heroFilm.title : "Filmid, seansid ja kinod ühest kohast" }}</h1>
          <p v-if="heroFilm" class="hero-meta muted">
            <span v-if="heroFilm.age_rating" class="tag">{{ heroFilm.age_rating }}</span>
            {{ heroMeta }}
          </p>
          <p v-else class="hero-meta muted">Vaata, mis on kinos kavas, ja leia endale sobiv seanss.</p>
          <div class="hero-actions">
            <RouterLink v-if="heroFilm" :to="`/filmid/${heroFilm.id}`" class="btn btn-primary">Vaata seansse</RouterLink>
            <RouterLink v-else to="/seansid" class="btn btn-primary">Tänane kava</RouterLink>
            <RouterLink to="/filmid" class="btn btn-ghost">Kõik filmid</RouterLink>
          </div>
        </div>
        <RouterLink v-if="heroFilm" :to="`/filmid/${heroFilm.id}`" class="hero-poster" tabindex="-1" aria-hidden="true">
          <FilmPoster :title="heroFilm.title" :url="heroFilm.poster_url" size="lg" />
        </RouterLink>
      </div>
    </section>

    <section class="container section">
      <div class="section-header">
        <h2 class="section-title">Järgmised seansid</h2>
        <RouterLink to="/seansid" class="link-arrow">Kogu kava →</RouterLink>
      </div>

      <div v-if="nextScreenings.loading.value" class="next-list" aria-busy="true">
        <div v-for="n in 4" :key="n" class="next-item next-skeleton" aria-hidden="true"></div>
      </div>
      <StateMessage
        v-else-if="nextScreenings.error.value"
        variant="error"
        title="Seansse ei õnnestunud laadida"
        :message="nextScreenings.error.value.message"
      >
        <button type="button" class="btn btn-ghost" @click="nextScreenings.run()">Proovi uuesti</button>
      </StateMessage>
      <StateMessage
        v-else-if="!nextScreenings.data.value?.results.length"
        title="Tulevasi seansse pole"
        message="Kava ilmub siia, kui seansid on lisatud."
      />
      <ul v-else class="next-list">
        <li v-for="screening in nextScreenings.data.value.results" :key="screening.id">
          <RouterLink :to="`/filmid/${screening.movie.id}`" class="next-item">
            <span class="next-when">
              <span class="next-day">{{ formatDayLabel(toDateKey(screening.starts_at)) }}</span>
              <time class="next-time" :datetime="screening.starts_at">{{ formatTime(screening.starts_at) }}</time>
            </span>
            <span class="next-info">
              <span class="next-title">{{ screening.movie.title }}</span>
              <span class="next-place muted">{{ screening.cinema.name }} · {{ screening.hall.name }}</span>
            </span>
          </RouterLink>
        </li>
      </ul>
    </section>

    <section class="container section">
      <div class="section-header">
        <h2 class="section-title">Praegu kinos</h2>
        <RouterLink to="/filmid?kavas=1" class="link-arrow">Kõik filmid →</RouterLink>
      </div>

      <FilmGridSkeleton v-if="nowShowing.loading.value" :count="5" />
      <StateMessage
        v-else-if="nowShowing.error.value"
        variant="error"
        title="Filme ei õnnestunud laadida"
        :message="nowShowing.error.value.message"
      >
        <button type="button" class="btn btn-ghost" @click="nowShowing.run()">Proovi uuesti</button>
      </StateMessage>
      <StateMessage
        v-else-if="!nowShowing.data.value?.results.length"
        title="Praegu ei ole ühtegi filmi kavas"
        message="Lisa seansse admin-paneelis või käivita arendusandmete käsk seed_dev_data."
      />
      <div v-else class="film-grid">
        <FilmCard v-for="film in nowShowing.data.value.results" :key="film.id" :film="film" />
      </div>
    </section>

    <section class="container section">
      <div class="section-header">
        <h2 class="section-title">Uudised</h2>
      </div>
      <StateMessage
        variant="placeholder"
        title="Uudised on tulekul"
        message="Uudiste tabel on andmebaasis olemas, kuid uudiste API ja leht on veel tegemata."
      />
    </section>
  </div>
</template>

<style scoped>
.hero {
  position: relative;
  overflow: hidden;
  border-bottom: 1px solid var(--color-border);
  background:
    radial-gradient(60% 80% at 85% 20%, rgb(242 181 68 / 0.16), transparent 70%),
    radial-gradient(50% 70% at 10% 100%, rgb(160 60 90 / 0.18), transparent 70%);
}

.hero-inner {
  display: grid;
  grid-template-columns: 1fr minmax(220px, 300px);
  gap: var(--space-7);
  align-items: center;
  padding-block: var(--space-8);
}

.hero-title {
  margin-top: var(--space-3);
  font-size: var(--text-hero);
}

.hero-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-2);
  margin-top: var(--space-4);
  font-size: var(--text-lg);
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-3);
  margin-top: var(--space-6);
}

.hero-poster {
  text-decoration: none;
  transform: rotate(2deg);
  transition: transform 300ms ease;
}

.hero-poster:hover {
  transform: rotate(0deg) translateY(-4px);
}

.next-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: var(--space-3);
  margin: 0;
  padding: 0;
  list-style: none;
}

.next-item {
  display: flex;
  gap: var(--space-4);
  align-items: center;
  height: 100%;
  padding: var(--space-3) var(--space-4);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  text-decoration: none;
  transition: border-color 150ms ease;
}

.next-item:hover {
  border-color: var(--color-border-strong);
}

.next-item:hover .next-title {
  color: var(--color-accent);
}

.next-skeleton {
  height: 68px;
  animation: pulse 1.4s ease-in-out infinite;
}

.next-when {
  display: grid;
  flex: none;
  min-width: 56px;
}

.next-day {
  font-size: var(--text-xs);
  color: var(--color-text-faint);
}

.next-time {
  font-family: var(--font-display);
  font-size: var(--text-lg);
  font-weight: 800;
  font-variant-numeric: tabular-nums;
}

.next-info {
  display: grid;
  min-width: 0;
}

.next-title {
  font-weight: 600;
}

.next-place {
  font-size: var(--text-sm);
}

@keyframes pulse {
  50% {
    opacity: 0.5;
  }
}

@media (max-width: 760px) {
  .hero-inner {
    grid-template-columns: 1fr;
    padding-block: var(--space-7);
  }

  .hero-poster {
    display: none;
  }
}
</style>
