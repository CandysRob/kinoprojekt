import { createRouter, createWebHistory } from "vue-router";

import HomeView from "./views/HomeView.vue";

const routes = [
  { path: "/", name: "home", component: HomeView, meta: { title: "Avaleht" } },
  { path: "/:pathMatch(.*)*", name: "not-found", component: () => import("./views/NotFoundView.vue"), meta: { title: "Lehte ei leitud" } },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) return savedPosition;
    // Filtrite muutmisel (sama leht, uus query) jääb kerimisasend paigale
    if (to.path === from.path) return false;
    return { top: 0 };
  },
});

router.afterEach((to) => {
  document.title = to.meta.title ? `${to.meta.title} · Kinoprojekt` : "Kinoprojekt";
});

export default router;
