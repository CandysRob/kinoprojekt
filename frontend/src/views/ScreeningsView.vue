<script setup>
import { computed, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

import { getCinemas, getScreenings } from "../api/cinema";
import DayPicker from "../components/DayPicker.vue";
import FilmPoster from "../components/FilmPoster.vue";
import ShowtimeChip from "../components/ShowtimeChip.vue";
import StateMessage from "../components/StateMessage.vue";
import { useRequest } from "../composables/useRequest";
import { formatDuration, formatLongDate, upcomingDateKeys } from "../utils/format";
import { groupByMovie } from "../utils/screenings";

const route = useRoute();
const router = useRouter();

const days = upcomingDateKeys(7);

// Filtrid on URL-is (?paev=&kino=)
const selectedDay = computed({
  get: () => (days.includes(route.query.paev) ? route.query.paev : days[0]),
  set: (paev) => router.replace({ query: { ...route.query, paev: paev === days[0] ? undefined : paev } }),
});
const selectedCinema = computed({
  get: () => route.query.kino || "",
  set: (kino) => router.replace({ query: { ...route.query, kino: kino || undefined } }),
});

const cinemas = useRequest(getCinemas);
const screenings = useRequest(
  (options) => getScreenings({ date: selectedDay.value, cinema: selectedCinema.value, page_size: 100 }, options),
  { immediate: false },
);

watch([selectedDay, selectedCinema], () => screenings.run(), { immediate: true });

const groups = computed(() => groupByMovie(screenings.data.value?.results ?? []));
const cinemaName = computed(() => cinemas.data.value?.find((c) => String(c.id) === selectedCinema.value)?.name);
</script>

<template>
  <div class="container section">
    <header class="page-header">
      <p class="eyebrow">Kava</p>
      <h1 class="page-title">Seansid</h1>
    </header>

    <div class="filters">
      <DayPicker v-model="selectedDay" :days="days" />
      <label class="cinema-select">
        <span class="visually-hidden">Kino</span>
        <select v-model="selectedCinema" :disabled="!cinemas.data.value">
          <option value="">Kõik kinod</option>
          <option v-for="cinema in cinemas.data.value" :key="cinema.id" :value="String(cinema.id)">
            {{ cinema.name }}, {{ cinema.city }}
          </option>
        </select>
      </label>
    </div>

    <h2 class="day-heading">
      {{ formatLongDate(selectedDay) }}<span v-if="cinemaName" class="muted"> · {{ cinemaName }}</span>
    </h2>

    <div v-if="screenings.loading.value" class="groups" aria-busy="true">
      <div v-for="n in 3" :key="n" class="group skeleton-group" aria-hidden="true"></div>
    </div>

    <StateMessage
      v-else-if="screenings.error.value"
      variant="error"
      title="Seansse ei õnnestunud laadida"
      :message="`${screenings.error.value.message} Kontrolli, kas backend töötab.`"
    >
      <button type="button" class="btn btn-ghost" @click="screenings.run()">Proovi uuesti</button>
    </StateMessage>

    <StateMessage
      v-else-if="!groups.length"
      :title="selectedDay === days[0] ? 'Täna rohkem seansse pole' : 'Sellel päeval seansse pole'"
      :message="
        selectedDay === days[0]
          ? 'Tänased seansid võivad olla juba alanud. Vaata järgmisi päevi.'
          : 'Proovi teist päeva või kino.'
      "
    >
      <button v-if="selectedDay === days[0]" type="button" class="btn btn-ghost" @click="selectedDay = days[1]">
        Vaata homset kava
      </button>
      <button v-if="selectedCinema" type="button" class="btn btn-ghost" @click="selectedCinema = ''">Kõik kinod</button>
    </StateMessage>

    <template v-else>
      <div class="groups">
        <article v-for="group in groups" :key="group.movie.id" class="group">
          <RouterLink :to="`/filmid/${group.movie.id}`" class="group-poster" tabindex="-1" aria-hidden="true">
            <FilmPoster :title="group.movie.title" :url="group.movie.poster_url" size="sm" />
          </RouterLink>
          <div class="group-body">
            <div class="group-head">
              <h3 class="group-title">
                <RouterLink :to="`/filmid/${group.movie.id}`">{{ group.movie.title }}</RouterLink>
              </h3>
              <p class="group-meta muted">
                <span v-if="group.movie.age_rating" class="tag">{{ group.movie.age_rating }}</span>
                {{ formatDuration(group.movie.duration_minutes) }}
              </p>
            </div>
            <div class="showtimes">
              <ShowtimeChip
                v-for="screening in group.screenings"
                :key="screening.id"
                :screening="screening"
                :show-cinema="!selectedCinema"
              />
            </div>
          </div>
        </article>
      </div>
      <p v-if="screenings.data.value?.next" class="muted more-note">
        Näidatud on esimesed 100 seanssi. Vali kino, et nimekirja kitsendada.
      </p>
      <StateMessage
        class="booking-note"
        variant="placeholder"
        title="Piletite broneerimine on veel arendamisel"
        message="Seansiaegu saab praegu ainult vaadata. Kohtade valik ja maksmine lisatakse järgmistes etappides."
      />
    </template>
  </div>
</template>

<style scoped>
.page-header {
  margin-bottom: var(--space-5);
}

.page-title {
  margin-top: var(--space-2);
  font-size: var(--text-2xl);
}

.filters {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-4);
  margin-bottom: var(--space-6);
}

.filters > :first-child {
  min-width: 0;
  max-width: 100%;
}

.cinema-select select {
  min-height: 44px;
  min-width: 220px;
  padding: 0 var(--space-4);
  border: 1px solid var(--color-border-strong);
  border-radius: var(--radius-pill);
  background: var(--color-surface);
}

.day-heading {
  margin-bottom: var(--space-4);
  font-family: var(--font-body);
  font-size: var(--text-lg);
  font-weight: 600;
}

.groups {
  display: grid;
  gap: var(--space-4);
}

.group {
  display: grid;
  grid-template-columns: 88px 1fr;
  gap: var(--space-5);
  padding: var(--space-4);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  background: rgb(24 21 30 / 0.6);
}

.group-poster {
  text-decoration: none;
}

.group-head {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  justify-content: space-between;
  gap: var(--space-2) var(--space-4);
  margin-bottom: var(--space-3);
}

.group-title {
  font-size: var(--text-lg);
}

.group-title a {
  text-decoration: none;
}

.group-title a:hover {
  color: var(--color-accent);
}

.group-meta {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-sm);
}

.showtimes {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: var(--space-3);
}

.skeleton-group {
  height: 150px;
  background: var(--color-surface);
  animation: pulse 1.4s ease-in-out infinite;
}

.more-note {
  margin-top: var(--space-4);
  font-size: var(--text-sm);
}

.booking-note {
  margin-top: var(--space-6);
}

@keyframes pulse {
  50% {
    opacity: 0.5;
  }
}

@media (max-width: 640px) {
  .cinema-select,
  .cinema-select select {
    width: 100%;
  }

  .group {
    grid-template-columns: 56px 1fr;
    gap: var(--space-3);
    padding: var(--space-3);
  }

  .showtimes {
    grid-template-columns: repeat(2, 1fr);
    gap: var(--space-2);
  }
}
</style>
