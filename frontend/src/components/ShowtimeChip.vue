<script setup>
import { formatPrice, formatTime } from "../utils/format";

// Üks seansiaeg. Broneerimist veel pole, seega see ei ole link ega nupp.
defineProps({
  screening: { type: Object, required: true },
  showCinema: { type: Boolean, default: true },
});
</script>

<template>
  <div class="showtime">
    <div class="showtime-top">
      <time class="showtime-time" :datetime="screening.starts_at">{{ formatTime(screening.starts_at) }}</time>
      <span v-if="screening.hall.screen_type !== '2D'" class="tag tag-accent">{{ screening.hall.screen_type }}</span>
    </div>
    <p class="showtime-place">
      <template v-if="showCinema">{{ screening.cinema.name }} · </template>{{ screening.hall.name }}
    </p>
    <p class="showtime-meta">
      {{ formatPrice(screening.base_price) }}<template v-if="screening.subtitles"> · subt. {{ screening.subtitles }}</template>
    </p>
  </div>
</template>

<style scoped>
.showtime {
  min-width: 0;
  padding: var(--space-3) var(--space-4);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
}

.showtime-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-2);
}

.showtime-time {
  font-family: var(--font-display);
  font-size: var(--text-lg);
  font-weight: 800;
  font-variant-numeric: tabular-nums;
}

.showtime-place,
.showtime-meta {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
}

.showtime-meta {
  color: var(--color-text-faint);
}
</style>
