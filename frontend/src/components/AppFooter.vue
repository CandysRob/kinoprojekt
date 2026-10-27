<script setup>
import { getCinemas } from "../api/cinema";
import { useRequest } from "../composables/useRequest";

// Kinode nimekiri tuleb API-st. Vea korral jäetakse see osa lihtsalt ära.
const { data: cinemas } = useRequest(getCinemas);
</script>

<template>
  <footer class="footer">
    <div class="container footer-grid">
      <div>
        <p class="footer-brand">Kinoprojekt</p>
        <p class="muted footer-text">Filmid, seansid ja kinod ühest kohast.</p>
      </div>

      <nav aria-label="Jaluse menüü">
        <p class="footer-heading">Sirvi</p>
        <ul class="footer-list">
          <li><RouterLink to="/filmid">Filmid</RouterLink></li>
          <li><RouterLink to="/seansid">Seansid</RouterLink></li>
        </ul>
      </nav>

      <div v-if="cinemas?.length">
        <p class="footer-heading">Meie kinod</p>
        <ul class="footer-list">
          <li v-for="cinema in cinemas" :key="cinema.id">
            <span>{{ cinema.name }}</span>
            <span class="muted"> · {{ cinema.street_address }}, {{ cinema.city }}</span>
          </li>
        </ul>
      </div>
    </div>
    <div class="container footer-bottom muted">Õppeprojekt. Filmid ja kinod on väljamõeldud arendusandmed.</div>
  </footer>
</template>

<style scoped>
.footer {
  margin-top: var(--space-8);
  border-top: 1px solid var(--color-border);
  background: var(--color-surface);
  font-size: var(--text-sm);
}

.footer-grid {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr 1.5fr;
  gap: var(--space-6);
  padding-block: var(--space-7) var(--space-6);
}

.footer-brand {
  font-family: var(--font-display);
  font-size: var(--text-lg);
  font-weight: 800;
}

.footer-text {
  margin-top: var(--space-2);
  max-width: 28ch;
}

.footer-heading {
  margin-bottom: var(--space-3);
  font-weight: 600;
}

.footer-list {
  display: grid;
  gap: var(--space-2);
  margin: 0;
  padding: 0;
  list-style: none;
}

.footer-list a {
  color: var(--color-text-muted);
  text-decoration: none;
}

.footer-list a:hover {
  color: var(--color-text);
}

.footer-bottom {
  padding-block: var(--space-4);
  border-top: 1px solid var(--color-border);
  font-size: var(--text-xs);
}

@media (max-width: 760px) {
  .footer-grid {
    grid-template-columns: 1fr 1fr;
  }

  .footer-grid > :first-child {
    grid-column: 1 / -1;
  }
}

@media (max-width: 420px) {
  .footer-grid {
    grid-template-columns: 1fr;
  }
}
</style>
