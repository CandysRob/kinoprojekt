<script setup>
import AppFooter from "./components/AppFooter.vue";
import AppHeader from "./components/AppHeader.vue";
</script>

<template>
  <a class="skip-link" href="#main">Liigu sisu juurde</a>
  <AppHeader />
  <main id="main" class="main">
    <RouterView />
  </main>
  <AppFooter />
</template>

<style scoped>
.main {
  min-height: calc(100vh - var(--header-height));
}

.skip-link {
  position: absolute;
  left: var(--space-4);
  top: -100px;
  z-index: 100;
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-sm);
  background: var(--color-accent);
  color: var(--color-accent-ink);
  font-weight: 600;
}

.skip-link:focus {
  top: var(--space-2);
}
</style>
