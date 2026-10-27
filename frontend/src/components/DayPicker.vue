<script setup>
import { formatDayLabel, formatDayMonth } from "../utils/format";

defineProps({
  days: { type: Array, required: true }, // ["2026-10-27", ...]
  modelValue: { type: String, required: true },
});
defineEmits(["update:modelValue"]);
</script>

<template>
  <div class="days" role="group" aria-label="Vali päev">
    <button
      v-for="day in days"
      :key="day"
      type="button"
      class="day"
      :aria-pressed="day === modelValue"
      @click="$emit('update:modelValue', day)"
    >
      <span class="day-label">{{ formatDayLabel(day) }}</span>
      <span class="day-date">{{ formatDayMonth(day) }}</span>
    </button>
  </div>
</template>

<style scoped>
.days {
  display: flex;
  gap: var(--space-2);
  overflow-x: auto;
  padding-bottom: var(--space-1);
  scrollbar-width: thin;
}

.day {
  flex: none;
  display: grid;
  justify-items: center;
  min-width: 84px;
  padding: var(--space-2) var(--space-3);
  border: 1px solid var(--color-border-strong);
  border-radius: var(--radius-md);
  background: transparent;
  cursor: pointer;
  transition: background-color 150ms ease, border-color 150ms ease;
}

.day:hover {
  border-color: var(--color-text-muted);
}

.day[aria-pressed="true"] {
  border-color: var(--color-accent);
  background: var(--color-accent);
  color: var(--color-accent-ink);
}

.day-label {
  font-weight: 600;
  font-size: var(--text-sm);
}

.day-date {
  font-size: var(--text-xs);
  opacity: 0.75;
}
</style>
