/**
 * Millise aadressi peal millist lehte näidatakse.
 *
 * Need on FRONTENDI aadressid (lehed). Backendi aadressid (/api/...) on
 * failis cinema/api_urls.py.
 */
import { createRouter, createWebHistory } from 'vue-router'

import FilmDetailView from './views/FilmDetailView.vue'
import FilmsView from './views/FilmsView.vue'
import NotFoundView from './views/NotFoundView.vue'
import ScreeningsView from './views/ScreeningsView.vue'

const routes = [
  { path: '/', name: 'films', component: FilmsView },
  // :id on aadressi osa, props: true annab selle lehele propsina "id"
  { path: '/filmid/:id', name: 'film', component: FilmDetailView, props: true },
  { path: '/seansid', name: 'screenings', component: ScreeningsView },
  // Kõik muud aadressid. Peab olema viimane.
  { path: '/:pathMatch(.*)*', name: 'not-found', component: NotFoundView },
]

export default createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})
