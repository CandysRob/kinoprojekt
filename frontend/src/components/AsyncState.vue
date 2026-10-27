<!--
  Kolm olekut, mis on igal andmeid laadival lehel:

    loading -> "Laen…"      error -> veateade ja "Proovi uuesti" nupp
    empty   -> emptyText     muidu -> lehe enda sisu (slot)

  Kasutamine:
    <AsyncState :loading="loading" :error="error" :empty="films.length === 0" @retry="load">
      ...sisu...
    </AsyncState>
-->
<script setup>
defineProps({
  loading: { type: Boolean, default: false },
  error: { type: String, default: '' },
  empty: { type: Boolean, default: false },
  emptyText: { type: String, default: 'Midagi ei leitud.' },
})

defineEmits(['retry'])
</script>

<template>
  <p v-if="loading" class="state">Laen…</p>
  <div v-else-if="error" class="state error" role="alert">
    <p>{{ error }}</p>
    <button type="button" class="button" @click="$emit('retry')">Proovi uuesti</button>
  </div>
  <p v-else-if="empty" class="state">{{ emptyText }}</p>
  <slot v-else />
</template>
