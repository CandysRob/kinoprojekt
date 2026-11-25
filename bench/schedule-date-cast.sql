-- One day's schedule, written the way Django builds `?date=` today:
--   Screening.objects.select_related("movie", "hall__cinema")
--       .filter(starts_at__gte=now, starts_at__date=day).order_by("starts_at")
-- `starts_at__date` becomes (algus_aeg AT TIME ZONE ...)::date = day. The cast
-- hides the column from the B-tree index on algus_aeg, so the index can only
-- use `>= now()` and every future screening has to be read and filtered.
-- A random day out of the next 30 days, a new one for every transaction.
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
  AND (seansid.algus_aeg AT TIME ZONE 'Europe/Tallinn')::date = (now() AT TIME ZONE 'Europe/Tallinn')::date + :day
ORDER BY seansid.algus_aeg;
