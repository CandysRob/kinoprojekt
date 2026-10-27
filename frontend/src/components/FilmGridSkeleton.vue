<script setup>
defineProps({
  count: { type: Number, default: 8 },
});
</script>

<template>
  <div class="film-grid" aria-busy="true" aria-label="Filmide laadimine">
    <div v-for="n in count" :key="n" class="skeleton-card" aria-hidden="true">
      <div class="skeleton skeleton-poster"></div>
      <div class="skeleton skeleton-line"></div>
      <div class="skeleton skeleton-line short"></div>
    </div>
  </div>
</template>

<style scoped>
.skeleton {
  border-radius: var(--radius-sm);
  background: linear-gradient(90deg, var(--color-surface) 0%, var(--color-surface-raised) 50%, var(--color-surface) 100%);
  background-size: 200% 100%;
  animation: shimmer 1.4s ease-in-out infinite;
}

.skeleton-poster {
  aspect-ratio: 2 / 3;
  border-radius: var(--radius-md);
}

.skeleton-line {
  height: 0.9rem;
  margin-top: var(--space-3);
  width: 80%;
}

.skeleton-line.short {
  width: 50%;
  margin-top: var(--space-2);
}

@keyframes shimmer {
  from {
    background-position: 100% 0;
  }
  to {
    background-position: -100% 0;
  }
}
</style>
