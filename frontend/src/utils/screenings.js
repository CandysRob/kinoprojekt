import { toDateKey } from "./format";

/** Rühmitab seansid päevade kaupa: [{ date: "2026-10-28", screenings: [...] }] */
export function groupByDate(screenings) {
  const groups = new Map();
  for (const screening of screenings) {
    const key = toDateKey(screening.starts_at);
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(screening);
  }
  return [...groups].map(([date, items]) => ({ date, screenings: items }));
}

/** Rühmitab seansid filmide kaupa, säilitades esimese seansi järjekorra. */
export function groupByMovie(screenings) {
  const groups = new Map();
  for (const screening of screenings) {
    const id = screening.movie.id;
    if (!groups.has(id)) groups.set(id, { movie: screening.movie, screenings: [] });
    groups.get(id).screenings.push(screening);
  }
  return [...groups.values()];
}
