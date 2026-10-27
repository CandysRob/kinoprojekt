// Abifunktsioonid kuupäevade ja hindade näitamiseks. Aeg on alati Eesti aja järgi.

const timeZone = 'Europe/Tallinn'

// "2026-10-28T18:15:00+02:00" -> "28.10.2026"
export const formatDate = (value) => new Date(value).toLocaleDateString('et-EE', { timeZone })

// "2026-10-28T18:15:00+02:00" -> "18:15"
export const formatTime = (value) =>
  new Date(value).toLocaleTimeString('et-EE', { timeZone, hour: '2-digit', minute: '2-digit' })

// "8.50" -> "8,50 €"
export const formatPrice = (value) => `${Number(value).toFixed(2).replace('.', ',')} €`

// "2026-09-17" -> "2026"
export const year = (date) => (date ? date.slice(0, 4) : '')
