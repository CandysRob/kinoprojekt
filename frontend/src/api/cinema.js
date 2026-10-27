import { apiGet } from "./client";

// Iga funktsioon vastab ühele Django API otspunktile (cinema/api_urls.py).

export const getMovies = (params, options) => apiGet("movies/", params, options);
export const getMovie = (id, options) => apiGet(`movies/${id}/`, {}, options);
export const getGenres = (options) => apiGet("genres/", {}, options);
export const getCinemas = (options) => apiGet("cinemas/", {}, options);
export const getScreenings = (params, options) => apiGet("screenings/", params, options);
