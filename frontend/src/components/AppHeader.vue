<!-- Lehe päis ja menüü. RouterLink vahetab lehte ilma kogu lehte uuesti laadimata. -->
<template>
  <header class="site-header">
    <RouterLink to="/" class="brand">Kinoprojekt</RouterLink>
    <nav class="site-nav" aria-label="Peamenüü">
      <RouterLink to="/">Filmid</RouterLink>
      <RouterLink to="/seansid">Seansid</RouterLink>
    </nav>
  </header>
</template>
