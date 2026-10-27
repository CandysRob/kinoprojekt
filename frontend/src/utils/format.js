// Kuupäevad ja kellaajad näidatakse alati Eesti aja järgi.
const TIME_ZONE = "Europe/Tallinn";

const timeFormat = new Intl.DateTimeFormat("et-EE", { timeZone: TIME_ZONE, hour: "2-digit", minute: "2-digit" });
// Eesti lühike nädalapäev on üks täht (N, R), seega kasutame pikka nime
const weekdayFormat = new Intl.DateTimeFormat("et-EE", { timeZone: TIME_ZONE, weekday: "long" });
const dayMonthFormat = new Intl.DateTimeFormat("et-EE", { timeZone: TIME_ZONE, day: "numeric", month: "short" });
const longDateFormat = new Intl.DateTimeFormat("et-EE", {
  timeZone: TIME_ZONE,
  weekday: "long",
  day: "numeric",
  month: "long",
});
const isoDateFormat = new Intl.DateTimeFormat("en-CA", { timeZone: TIME_ZONE });
const priceFormat = new Intl.NumberFormat("et-EE", { style: "currency", currency: "EUR" });

/** Kuupäev kujul AAAA-KK-PP Eesti aja järgi (API `date` filtri jaoks). */
export function toDateKey(value = new Date()) {
  return isoDateFormat.format(new Date(value));
}

// Võtmest tehtud kuupäev keskpäeval, et ajavöönd ega suveaeg ei nihutaks seda teise päeva.
const fromDateKey = (key) => new Date(`${key}T12:00:00Z`);

const addDays = (key, days) => toDateKey(fromDateKey(key).getTime() + days * 86_400_000);

/** Järgmise `count` päeva võtmed alates tänasest. */
export function upcomingDateKeys(count) {
  const today = toDateKey();
  return Array.from({ length: count }, (_, i) => addDays(today, i));
}

export function formatDayLabel(key) {
  const today = toDateKey();
  if (key === today) return "Täna";
  if (key === addDays(today, 1)) return "Homme";
  const weekday = weekdayFormat.format(fromDateKey(key));
  return weekday.charAt(0).toUpperCase() + weekday.slice(1);
}

export const formatDayMonth = (key) => dayMonthFormat.format(fromDateKey(key));

export function formatLongDate(key) {
  const label = longDateFormat.format(fromDateKey(key));
  return label.charAt(0).toUpperCase() + label.slice(1);
}

export const formatTime = (value) => timeFormat.format(new Date(value));

export const formatPrice = (value) => priceFormat.format(Number(value));

export function formatDuration(minutes) {
  if (!minutes) return null;
  const hours = Math.floor(minutes / 60);
  const rest = minutes % 60;
  if (!hours) return `${rest} min`;
  return rest ? `${hours} t ${rest} min` : `${hours} t`;
}

export const formatYear = (date) => (date ? date.slice(0, 4) : null);
