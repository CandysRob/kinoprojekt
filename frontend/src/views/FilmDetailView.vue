<script setup>
import { computed, watch } from "vue";

import { getMovie, getScreenings } from "../api/cinema";
import FilmPoster from "../components/FilmPoster.vue";
import ShowtimeChip from "../components/ShowtimeChip.vue";
import StateMessage from "../components/StateMessage.vue";
import { useRequest } from "../composables/useRequest";
import { formatDuration, formatLongDate } from "../utils/format";
import { groupByDate } from "../utils/screenings";

const props = defineProps({
  id: { type: String, required: true },
});

const film = useRequest((options) => getMovie(props.id, options), { immediate: false });
const screenings = useRequest((options) => getScreenings({ movie: props.id, page_size: 100 }, options), {
  immediate: false,
});

watch(
  () => props.id,
  () => {
    film.run();
    screenings.run();
  },
  { immediate: true },
);

const notFound = computed(() => film.error.value?.status === 404);
const screeningDays = computed(() => groupByDate(screenings.data.value?.results ?? []));

const facts = computed(() => {
  const movie = film.data.value;
  if (!movie) return [];
  return [
    { label: "Kestus", value: formatDuration(movie.duration_minutes) },
    { label: "Esilinastus", value: movie.release_date && new Date(movie.release_date).toLocaleDateString("et-EE") },
    { label: "Keel", value: movie.language },
    { label: "Vanusepiirang", value: movie.age_rating },
  ].filter((fact) => fact.value);
});

watch(
  () => film.data.value?.title,
  (title) => {
    if (title) document.title = `${title} · Kinoprojekt`;
  },
);
</script>

<template>
  <div>
    <div v-if="film.loading.value && !film.data.value" class="container section" aria-busy="true">
      <div class="detail-skeleton">
        <div class="skeleton-block poster-block"></div>
        <div class="skeleton-lines">
          <div class="skeleton-block line-lg"></div>
          <div class="skeleton-block line"></div>
          <div class="skeleton-block line"></div>
        </div>
      </div>
    </div>

    <div v-else-if="notFound" class="container section">
      <StateMessage title="Filmi ei leitud" message="Võib-olla on film eemaldatud või link on vale.">
        <RouterLink to="/filmid" class="btn btn-ghost">Kõik filmid</RouterLink>
      </StateMessage>
    </div>

    <div v-else-if="film.error.value" class="container section">
      <StateMessage variant="error" title="Filmi ei õnnestunud laadida" :message="film.error.value.message">
        <button type="button" class="btn btn-ghost" @click="film.run()">Proovi uuesti</button>
      </StateMessage>
    </div>

    <template v-else-if="film.data.value">
      <section class="hero">
        <div class="hero-backdrop" aria-hidden="true">
          <FilmPoster :title="film.data.value.title" :url="film.data.value.poster_url" size="lg" />
        </div>
        <div class="container hero-inner">
          <div class="hero-poster">
            <FilmPoster :title="film.data.value.title" :url="film.data.value.poster_url" size="lg" />
          </div>
          <div class="hero-info">
            <RouterLink to="/filmid" class="back-link">← Kõik filmid</RouterLink>
            <h1 class="film-title">{{ film.data.value.title }}</h1>
            <ul v-if="film.data.value.genres.length" class="genres" aria-label="Žanrid">
              <li v-for="genre in film.data.value.genres" :key="genre.id">
                <RouterLink :to="{ path: '/filmid', query: { zanr: genre.id } }" class="tag">{{ genre.name }}</RouterLink>
              </li>
            </ul>
            <p v-if="film.data.value.description" class="description">{{ film.data.value.description }}</p>
            <p v-else class="description muted">Kirjeldus on veel lisamata.</p>
            <dl class="facts">
              <div v-for="fact in facts" :key="fact.label">
                <dt>{{ fact.label }}</dt>
                <dd>{{ fact.value }}</dd>
              </div>
            </dl>
            <div class="actions">
              <a href="#seansid" class="btn btn-primary">Vaata seansse</a>
              <a
                v-if="film.data.value.trailer_url"
                :href="film.data.value.trailer_url"
                class="btn btn-ghost"
                target="_blank"
                rel="noopener noreferrer"
              >
                Vaata treilerit
              </a>
            </div>
          </div>
        </div>
      </section>

      <section id="seansid" class="container section">
        <div class="section-header">
          <h2 class="section-title">Seansid</h2>
        </div>

        <p v-if="screenings.loading.value" class="muted">Laadin seansse…</p>
        <StateMessage
          v-else-if="screenings.error.value"
          variant="error"
          title="Seansse ei õnnestunud laadida"
          :message="screenings.error.value.message"
        >
          <button type="button" class="btn btn-ghost" @click="screenings.run()">Proovi uuesti</button>
        </StateMessage>
        <StateMessage
          v-else-if="!screeningDays.length"
          title="Sellel filmil pole praegu seansse"
          message="Uued seansid ilmuvad siia kohe, kui need kavasse lisatakse."
        />
        <template v-else>
          <div class="days">
            <div v-for="day in screeningDays" :key="day.date" class="day">
              <h3 class="day-title">{{ formatLongDate(day.date) }}</h3>
              <div class="showtimes">
                <ShowtimeChip v-for="screening in day.screenings" :key="screening.id" :screening="screening" />
              </div>
            </div>
          </div>
          <StateMessage
            class="booking-note"
            variant="placeholder"
            title="Piletite broneerimine on veel arendamisel"
            message="Seansiaegu saab praegu ainult vaadata. Kohtade valik ja maksmine lisatakse järgmistes etappides."
          />
        </template>
      </section>
    </template>
  </div>
</template>

<style scoped>
.hero {
  position: relative;
  overflow: hidden;
  border-bottom: 1px solid var(--color-border);
}

.hero-backdrop {
  position: absolute;
  inset: -20%;
  filter: blur(60px) saturate(1.2);
  opacity: 0.35;
  pointer-events: none;
}

.hero-backdrop :deep(.poster) {
  width: 100%;
  height: 100%;
  aspect-ratio: auto;
}

.hero::after {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(to bottom, transparent 40%, var(--color-bg));
  pointer-events: none;
}

.hero-inner {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: minmax(200px, 300px) 1fr;
  gap: var(--space-7);
  align-items: start;
  padding-block: var(--space-7);
}

.back-link {
  display: inline-block;
  margin-bottom: var(--space-4);
  font-size: var(--text-sm);
  color: var(--color-text-muted);
  text-decoration: none;
}

.back-link:hover {
  color: var(--color-text);
}

.film-title {
  font-size: var(--text-hero);
}

.genres {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  margin: var(--space-4) 0 0;
  padding: 0;
  list-style: none;
}

.genres .tag {
  text-decoration: none;
}

.genres .tag:hover {
  color: var(--color-text);
  border-color: var(--color-text-muted);
}

.description {
  max-width: 62ch;
  margin-top: var(--space-5);
  font-size: var(--text-lg);
  line-height: 1.5;
}

.facts {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-4) var(--space-6);
  margin: var(--space-5) 0 0;
}

.facts dt {
  font-size: var(--text-xs);
  color: var(--color-text-faint);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.facts dd {
  margin: 0;
  font-weight: 600;
}

.actions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-3);
  margin-top: var(--space-6);
}

.days {
  display: grid;
  gap: var(--space-6);
}

.day-title {
  margin-bottom: var(--space-3);
  font-family: var(--font-body);
  font-size: var(--text-md);
  font-weight: 600;
  color: var(--color-text-muted);
}

.showtimes {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(170px, 1fr));
  gap: var(--space-3);
}

.booking-note {
  margin-top: var(--space-6);
}

.detail-skeleton {
  display: grid;
  grid-template-columns: minmax(200px, 300px) 1fr;
  gap: var(--space-7);
}

.skeleton-block {
  border-radius: var(--radius-md);
  background: var(--color-surface-raised);
  animation: pulse 1.4s ease-in-out infinite;
}

.poster-block {
  aspect-ratio: 2 / 3;
}

.skeleton-lines {
  display: grid;
  gap: var(--space-4);
  align-content: start;
}

.line-lg {
  height: 3rem;
  width: 60%;
}

.line {
  height: 1rem;
  width: 85%;
}

@keyframes pulse {
  50% {
    opacity: 0.5;
  }
}

@media (max-width: 760px) {
  .hero-inner,
  .detail-skeleton {
    grid-template-columns: 1fr;
    gap: var(--space-5);
    padding-block: var(--space-5) var(--space-6);
  }

  .hero-poster,
  .poster-block {
    width: min(180px, 50%);
  }

  .hero-info {
    display: flex;
    flex-direction: column;
  }

  .back-link {
    order: -1;
  }

  .description {
    font-size: var(--text-md);
  }
}

@media (max-width: 420px) {
  .showtimes {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
