<script setup>
import { ref, watch } from "vue";
import { useRoute } from "vue-router";

const links = [
  { to: "/", label: "Avaleht" },
  { to: "/filmid", label: "Filmid" },
  { to: "/seansid", label: "Seansid" },
];

const menuOpen = ref(false);
const route = useRoute();

// Lehe vahetamisel sulgub mobiilimenüü
watch(() => route.path, () => (menuOpen.value = false));
</script>

<template>
  <header class="header">
    <div class="container header-inner">
      <RouterLink to="/" class="brand" aria-label="Kinoprojekt, avaleht">
        <svg class="brand-mark" viewBox="0 0 32 32" aria-hidden="true">
          <rect x="4" y="7" width="24" height="18" rx="3" fill="none" stroke="currentColor" stroke-width="2.5" />
          <path d="M13.5 12l6.5 4-6.5 4z" fill="currentColor" />
        </svg>
        <span>Kinoprojekt</span>
      </RouterLink>

      <button
        class="menu-toggle"
        type="button"
        :aria-expanded="menuOpen"
        aria-controls="main-nav"
        @click="menuOpen = !menuOpen"
      >
        <span class="visually-hidden">{{ menuOpen ? "Sulge menüü" : "Ava menüü" }}</span>
        <span class="menu-icon" :class="{ open: menuOpen }" aria-hidden="true"></span>
      </button>

      <nav id="main-nav" class="nav" :class="{ open: menuOpen }" aria-label="Peamenüü">
        <RouterLink
          v-for="link in links"
          :key="link.to"
          :to="link.to"
          class="nav-link"
          :class="{ active: link.to === '/' ? route.path === '/' : route.path.startsWith(link.to) }"
        >
          {{ link.label }}
        </RouterLink>
      </nav>
    </div>
  </header>
</template>

<style scoped>
.header {
  position: sticky;
  top: 0;
  z-index: 20;
  border-bottom: 1px solid var(--color-border);
  background: rgb(15 13 19 / 0.88);
  backdrop-filter: blur(12px);
}

.header-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: var(--header-height);
}

.brand {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  font-family: var(--font-display);
  font-size: var(--text-lg);
  font-weight: 800;
  text-decoration: none;
}

.brand-mark {
  width: 28px;
  height: 28px;
  color: var(--color-accent);
}

.nav {
  display: flex;
  gap: var(--space-1);
}

.nav-link {
  position: relative;
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-pill);
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-text-muted);
  text-decoration: none;
  transition: color 150ms ease, background-color 150ms ease;
}

.nav-link:hover {
  color: var(--color-text);
}

.nav-link.active {
  color: var(--color-text);
  background: var(--color-surface-raised);
}

.menu-toggle {
  display: none;
  width: 44px;
  height: 44px;
  border: 0;
  background: none;
  cursor: pointer;
}

.menu-icon,
.menu-icon::before,
.menu-icon::after {
  display: block;
  width: 22px;
  height: 2px;
  margin-inline: auto;
  border-radius: 2px;
  background: var(--color-text);
  transition: transform 200ms ease, opacity 150ms ease;
}

.menu-icon {
  position: relative;
}

.menu-icon::before,
.menu-icon::after {
  content: "";
  position: absolute;
  left: 0;
}

.menu-icon::before {
  top: -7px;
}

.menu-icon::after {
  top: 7px;
}

.menu-icon.open {
  background: transparent;
}

.menu-icon.open::before {
  transform: translateY(7px) rotate(45deg);
}

.menu-icon.open::after {
  transform: translateY(-7px) rotate(-45deg);
}

@media (max-width: 640px) {
  .menu-toggle {
    display: block;
  }

  .nav {
    position: absolute;
    top: var(--header-height);
    left: 0;
    right: 0;
    flex-direction: column;
    padding: var(--space-3) var(--gutter) var(--space-5);
    border-bottom: 1px solid var(--color-border);
    background: var(--color-bg);
    visibility: hidden;
    opacity: 0;
    transform: translateY(-8px);
    transition: opacity 150ms ease, transform 150ms ease, visibility 150ms;
  }

  .nav.open {
    visibility: visible;
    opacity: 1;
    transform: none;
  }

  .nav-link {
    padding: var(--space-3) var(--space-4);
    font-size: var(--text-md);
  }
}
</style>
