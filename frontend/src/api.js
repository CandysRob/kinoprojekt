/**
 * Kõik päringud Django API-sse käivad läbi selle faili.
 *
 * Aadressid on suhtelised (/api/...). Arenduses suunab Vite need edasi
 * Djangole (vaata vite.config.js), seega brauser räägib ainult Vitega.
 */

async function getJson(path) {
  const response = await fetch(`/api/${path}`)
  if (!response.ok) {
    // Viga koos staatuskoodiga, et leht saaks 404 puhul näidata oma teadet
    const error = new Error(`Päring ebaõnnestus (${response.status}). Kas backend töötab?`)
    error.status = response.status
    throw error
  }
  return response.json()
}

// GET /api/movies/ -> kõik filmid
export const fetchMovies = () => getJson('movies/')

// GET /api/movies/5/ -> üks film
export const fetchMovie = (id) => getJson(`movies/${id}/`)

// GET /api/screenings/ -> tulevased seansid, movieId korral ainult selle filmi omad
export const fetchScreenings = (movieId) => getJson(movieId ? `screenings/?movie=${movieId}` : 'screenings/')
