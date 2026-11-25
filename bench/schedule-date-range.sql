-- The same one-day schedule as schedule-date-cast.sql, but the day is given
-- as a time range: [day 00:00, next day 00:00) in Estonian time. The column
-- is compared as it is, so the index on algus_aeg (screening_starts_at_idx)
-- can jump straight to that day's ~35 rows.
-- In Django: .filter(starts_at__gte=day_start, starts_at__lt=day_start + timedelta(days=1))
\set day random(0, 29)
SELECT seansid.id, seansid.filmi_id, seansid.saali_id, seansid.algus_aeg, seansid.lopu_aeg,
       seansid.keel, seansid.subtiitrid, seansid.alghind,
       filmid.id, filmid.pealkiri, filmid.kirjeldus, filmid.filmi_pikkus, filmid."väljalaskekuupäev",
       filmid.vanusepiirang, filmid.keel, filmid.plakati_url, filmid.treileri_url, filmid."väikeväärtus",
       kinosaalid.id, kinosaalid.kino_id, kinosaalid.name, kinosaalid."ekraani_tüüp", kinosaalid.mahutavus,
       kino.id, kino.kino_nimi, kino."tänava_aadress", kino.linn, kino.postiindeks, kino.riik
FROM seansid
JOIN filmid ON seansid.filmi_id = filmid.id
JOIN kinosaalid ON seansid.saali_id = kinosaalid.id
JOIN kino ON kinosaalid.kino_id = kino.id
WHERE seansid.algus_aeg >= now()
  AND seansid.algus_aeg >= ((now() AT TIME ZONE 'Europe/Tallinn')::date + :day)::timestamp AT TIME ZONE 'Europe/Tallinn'
  AND seansid.algus_aeg < ((now() AT TIME ZONE 'Europe/Tallinn')::date + :day + 1)::timestamp AT TIME ZONE 'Europe/Tallinn'
ORDER BY seansid.algus_aeg;
