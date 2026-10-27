<script setup>
import { computed, ref } from "vue";

const props = defineProps({
  title: { type: String, required: true },
  url: { type: String, default: null },
  size: { type: String, default: "md" }, // sm | md | lg
});

const failed = ref(false);
const showImage = computed(() => props.url && !failed.value);

// Plakatita filmile tehakse pealkirjast püsiv värviline kujundus
const hue = computed(() => {
  let hash = 0;
  for (const char of props.title) hash = (hash * 31 + char.codePointAt(0)) % 360;
  return hash;
});
</script>

<template>
  <div class="poster" :class="`poster-${size}`" :style="{ '--hue': hue }">
    <img v-if="showImage" :src="url" :alt="`${title} plakat`" loading="lazy" @error="failed = true" />
    <div v-else class="poster-fallback" role="img" :aria-label="`${title} (plakat puudub)`">
      <span class="poster-title" aria-hidden="true">{{ title }}</span>
    </div>
  </div>
</template>

<style scoped>
.poster {
  position: relative;
  aspect-ratio: 2 / 3;
  overflow: hidden;
  border-radius: var(--radius-md);
  background: var(--color-surface-raised);
  box-shadow: var(--shadow-card);
}

.poster img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.poster-fallback {
  display: flex;
  align-items: flex-end;
  height: 100%;
  padding: 12%;
  background:
    radial-gradient(120% 70% at 85% 0%, hsl(var(--hue) 70% 55% / 0.55), transparent 60%),
    radial-gradient(90% 60% at 0% 100%, hsl(calc(var(--hue) + 40) 60% 35% / 0.7), transparent 70%),
    linear-gradient(160deg, hsl(var(--hue) 35% 18%), hsl(calc(var(--hue) + 30) 30% 9%));
}

.poster-fallback::before {
  content: "";
  position: absolute;
  inset: 8px;
  border: 1px solid hsl(var(--hue) 80% 85% / 0.18);
  border-radius: calc(var(--radius-md) - 4px);
}

.poster-title {
  font-family: var(--font-display);
  font-weight: 800;
  line-height: 1;
  color: hsl(var(--hue) 40% 94%);
  overflow-wrap: anywhere;
  text-wrap: balance;
}

.poster-sm .poster-title {
  font-size: 0.8rem;
}

.poster-md .poster-title {
  font-size: clamp(1.1rem, 0.9rem + 0.8vw, 1.5rem);
}

.poster-lg .poster-title {
  font-size: clamp(1.6rem, 1.2rem + 1.5vw, 2.4rem);
}

.poster-sm {
  border-radius: var(--radius-sm);
}

.poster-sm .poster-fallback {
  padding: 10%;
}

.poster-sm .poster-fallback::before {
  inset: 4px;
}
</style>
