<script setup>
// Ühtne tühja oleku, vea ja "tulekul" teate kast
defineProps({
  variant: { type: String, default: "empty" }, // empty | error | placeholder
  title: { type: String, required: true },
  message: { type: String, default: "" },
});
</script>

<template>
  <div class="state" :class="`state-${variant}`" :role="variant === 'error' ? 'alert' : 'status'">
    <svg v-if="variant === 'error'" class="state-icon" viewBox="0 0 24 24" aria-hidden="true">
      <circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="2" />
      <path d="M12 7.5v5.5M12 16.2v.3" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
    </svg>
    <svg v-else-if="variant === 'placeholder'" class="state-icon" viewBox="0 0 24 24" aria-hidden="true">
      <path d="M4 20h16M6 20V9l6-5 6 5v11" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" />
      <path d="M10 20v-5h4v5" fill="none" stroke="currentColor" stroke-width="2" />
    </svg>
    <svg v-else class="state-icon" viewBox="0 0 24 24" aria-hidden="true">
      <rect x="3" y="6" width="18" height="13" rx="2" fill="none" stroke="currentColor" stroke-width="2" />
      <path d="M3 10h18M8 6l2 4M14 6l2 4" stroke="currentColor" stroke-width="2" />
    </svg>
    <div class="state-body">
      <p class="state-title">{{ title }}</p>
      <p v-if="message" class="state-message">{{ message }}</p>
      <div v-if="$slots.default" class="state-actions"><slot /></div>
    </div>
  </div>
</template>

<style scoped>
.state {
  display: flex;
  gap: var(--space-4);
  align-items: flex-start;
  padding: var(--space-5);
  border: 1px dashed var(--color-border-strong);
  border-radius: var(--radius-lg);
  background: var(--color-surface);
}

.state-error {
  border-style: solid;
  border-color: rgb(255 122 112 / 0.4);
}

.state-placeholder {
  border-style: solid;
  border-color: rgb(242 181 68 / 0.35);
  background: rgb(242 181 68 / 0.06);
}

.state-icon {
  flex: none;
  width: 28px;
  height: 28px;
  color: var(--color-text-faint);
}

.state-error .state-icon {
  color: var(--color-danger);
}

.state-placeholder .state-icon {
  color: var(--color-accent);
}

.state-title {
  font-weight: 600;
}

.state-message {
  margin-top: var(--space-1);
  color: var(--color-text-muted);
  font-size: var(--text-sm);
}

.state-actions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-3);
  margin-top: var(--space-4);
}
</style>
