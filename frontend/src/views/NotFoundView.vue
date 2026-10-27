<template>
  <section class="container not-found">
    <p class="eyebrow">404</p>
    <h1>Seda lehte ei leitud</h1>
    <p class="muted">Võib-olla on link vale või leht on eemaldatud.</p>
    <RouterLink to="/" class="btn btn-primary">Tagasi avalehele</RouterLink>
  </section>
</template>

<style scoped>
.not-found {
  display: grid;
  justify-items: start;
  gap: var(--space-4);
  padding-block: var(--space-8);
}

.not-found h1 {
  font-size: var(--text-2xl);
}
</style>
