<script setup>
import { computed, onBeforeUnmount, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

import { getGenres, getMovies } from "../api/cinema";
import FilmCard from "../components/FilmCard.vue";
import FilmGridSkeleton from "../components/FilmGridSkeleton.vue";
import StateMessage from "../components/StateMessage.vue";
import { useRequest } from "../composables/useRequest";

const route = useRoute();
const router = useRouter();

// Filtrid on URL-is (?otsi=&zanr=&kavas=1), et lingiga saaks sama vaate jagada
const filters = computed(() => ({
  search: route.query.otsi || "",
  genre: route.query.zanr || "",
  nowShowing: route.query.kavas === "1",
}));
const hasFilters = computed(() => Boolean(filters.value.search || filters.value.genre || filters.value.nowShowing));

function updateQuery(changes) {
  const query = { ...route.query, ...changes };
  for (const key of Object.keys(query)) if (!query[key]) delete query[key];
  router.replace({ query });
}

// Otsing uuendab URL-i väikese viivitusega, mitte iga klahvivajutuse peale
const searchInput = ref(filters.value.search);
let searchTimer;
watch(searchInput, (value) => {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => updateQuery({ otsi: value.trim() }), 300);
});
watch(
  () => filters.value.search,
  (value) => {
    if (value !== searchInput.value.trim()) searchInput.value = value;
  },
);

const { data: genres } = useRequest(getGenres);

const films = ref([]);
const total = ref(0);
const nextPage = ref(null);
const loading = ref(true);
const loadingMore = ref(false);
const error = ref(null);
let controller;

async function load(page = 1) {
  controller?.abort();
  controller = new AbortController();
  const { signal } = controller;
  if (page === 1) loading.value = true;
  else loadingMore.value = true;
  error.value = null;
  try {
    const data = await getMovies(
      {
        page,
        search: filters.value.search,
        genre: filters.value.genre,
        now_showing: filters.value.nowShowing ? "true" : "",
      },
      { signal },
    );
    films.value = page === 1 ? data.results : [...films.value, ...data.results];
    total.value = data.count;
    nextPage.value = data.next ? page + 1 : null;
  } catch (err) {
    if (err.name !== "AbortError") error.value = err;
  } finally {
    if (!signal.aborted) {
      loading.value = false;
      loadingMore.value = false;
    }
  }
}

watch(filters, () => load(1), { immediate: true });

onBeforeUnmount(() => {
  controller?.abort();
  clearTimeout(searchTimer);
});

function resetFilters() {
  searchInput.value = "";
  router.replace({ query: {} });
}
</script>

<template>
  <div class="container section">
    <header class="page-header">
      <p class="eyebrow">Kataloog</p>
      <h1 class="page-title">Filmid</h1>
    </header>

    <div class="toolbar">
      <label class="search">
        <span class="visually-hidden">Otsi filmi pealkirja järgi</span>
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <circle cx="11" cy="11" r="6.5" fill="none" stroke="currentColor" stroke-width="2" />
          <path d="M16 16l4.5 4.5" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
        </svg>
        <input v-model="searchInput" type="search" placeholder="Otsi pealkirja järgi" autocomplete="off" />
      </label>

      <label class="toggle">
        <input
          type="checkbox"
          :checked="filters.nowShowing"
          @change="updateQuery({ kavas: $event.target.checked ? '1' : '' })"
        />
        <span>Ainult kavas olevad</span>
      </label>
    </div>

    <div v-if="genres?.length" class="chips" role="group" aria-label="Žanr">
      <button
        type="button"
        class="chip"
        :aria-pressed="!filters.genre"
        @click="updateQuery({ zanr: '' })"
      >
        Kõik
      </button>
      <button
        v-for="genre in genres"
        :key="genre.id"
        type="button"
        class="chip"
        :aria-pressed="filters.genre === String(genre.id)"
        @click="updateQuery({ zanr: filters.genre === String(genre.id) ? '' : String(genre.id) })"
      >
        {{ genre.name }}
      </button>
    </div>

    <FilmGridSkeleton v-if="loading" />

    <StateMessage
      v-else-if="error"
      variant="error"
      title="Filme ei õnnestunud laadida"
      :message="`${error.message} Kontrolli, kas backend töötab.`"
    >
      <button type="button" class="btn btn-ghost" @click="load(1)">Proovi uuesti</button>
    </StateMessage>

    <StateMessage
      v-else-if="!films.length"
      :title="hasFilters ? 'Nende filtritega filme ei leitud' : 'Filme veel pole'"
      :message="
        hasFilters
          ? 'Proovi teist otsingut või eemalda filtrid.'
          : 'Lisa filme admin-paneelis või käivita arendusandmete käsk seed_dev_data.'
      "
    >
      <button v-if="hasFilters" type="button" class="btn btn-ghost" @click="resetFilters">Eemalda filtrid</button>
    </StateMessage>

    <template v-else>
      <p class="result-count muted" aria-live="polite">{{ total }} {{ total === 1 ? "film" : "filmi" }}</p>
      <div class="film-grid">
        <FilmCard v-for="film in films" :key="film.id" :film="film" />
      </div>
      <div v-if="nextPage" class="load-more">
        <button type="button" class="btn btn-ghost" :disabled="loadingMore" @click="load(nextPage)">
          {{ loadingMore ? "Laadin…" : "Näita rohkem" }}
        </button>
      </div>
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

.toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-3) var(--space-5);
  margin-bottom: var(--space-4);
}

.search {
  position: relative;
  flex: 1 1 280px;
  max-width: 420px;
}

.search svg {
  position: absolute;
  left: 14px;
  top: 50%;
  width: 18px;
  height: 18px;
  transform: translateY(-50%);
  color: var(--color-text-faint);
  pointer-events: none;
}

.search input {
  width: 100%;
  min-height: 44px;
  padding: 0 var(--space-4) 0 42px;
  border: 1px solid var(--color-border-strong);
  border-radius: var(--radius-pill);
  background: var(--color-surface);
}

.search input::placeholder {
  color: var(--color-text-faint);
}

.search input:focus {
  border-color: var(--color-accent);
  outline: none;
}

.toggle {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  min-height: 44px;
  font-size: var(--text-sm);
  cursor: pointer;
}

.toggle input {
  width: 18px;
  height: 18px;
  accent-color: var(--color-accent);
}

.chips {
  display: flex;
  gap: var(--space-2);
  margin-bottom: var(--space-6);
  padding-bottom: var(--space-1);
  overflow-x: auto;
  scrollbar-width: thin;
}

.chip {
  flex: none;
  min-height: 36px;
  padding: 0 var(--space-4);
  border: 1px solid var(--color-border-strong);
  border-radius: var(--radius-pill);
  background: transparent;
  font-size: var(--text-sm);
  color: var(--color-text-muted);
  cursor: pointer;
  transition: background-color 150ms ease, color 150ms ease, border-color 150ms ease;
}

.chip:hover {
  color: var(--color-text);
  border-color: var(--color-text-muted);
}

.chip[aria-pressed="true"] {
  border-color: var(--color-accent);
  background: var(--color-accent);
  color: var(--color-accent-ink);
  font-weight: 600;
}

.result-count {
  margin-bottom: var(--space-4);
  font-size: var(--text-sm);
}

.load-more {
  display: flex;
  justify-content: center;
  margin-top: var(--space-7);
}
</style>
