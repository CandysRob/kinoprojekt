# Kinoprojekti teekaart

Seis: oktoober 2026.

> **Jira:** repos ei ole Jira ülesannete numbreid ega pealkirju. Allpool on
> funktsioonid nimetatud sisu järgi ja veerg "Jira" on tühi. Lisage sinna oma
> ülesannete numbrid. Aktsepteerimistingimused on Jiras, mitte siin.

## Mis praegu töötab

| Osa | Sisu |
| --- | --- |
| Andmebaas | PostgreSQL 16, 13 tabelit `project.sql` järgi, Django migratsioonid |
| Mudelid | `cinema/models.py` (kasutajad, kinod, saalid, kohad, filmid, žanrid, seansid, broneeringud, maksed, arvustused, uudised) |
| Admin-paneel | kõigi tabelite lisamine ja muutmine (`/admin/`) |
| API | filmid, žanrid, kinod, seansid, ainult lugemiseks (`/api/`) |
| Lehed | filmide nimekiri, filmi leht koos seanssidega, seansside tabel |
| Arendusandmed | `manage.py seed_dev_data` |
| Testid | mudelite piirangud, API, arendusandmete käsk |
| Docker | `docker compose`: db, backend, frontend |

## Teadlikult tegemata

| Funktsioon | Praegune seis | Jira |
| --- | --- | --- |
| Filmide otsing ja filtrid (žanr, kuupäev, kino) | pole | |
| Piletite broneerimine | tabelid `broneeringud` ja `broneeritud_kohad` on olemas, API ja leht puuduvad | |
| Maksed | tabel `maksed` on olemas | |
| Kasutaja konto (registreerumine, sisselogimine) | kasutajamudel on olemas, lehti pole | |
| Arvustused | tabel `arvustused` on olemas | |
| Uudised | tabel `uudised` on olemas | |
| Filmiplakatid | väli `plakati_url` on olemas, arendusandmetes plakateid pole (näidatakse halli kasti) | |

## Kust edasi minna

| Funktsioon | Mudelid | Mida muuta |
| --- | --- | --- |
| Filtrid | `Movie`, `Genre`, `Screening` | `cinema/api_views.py` `get_queryset`, vastav Vue leht |
| Uudised | `News` | uus serializer + ViewSet, uus leht ja link päises |
| Istekohtade valik | `Seat`, `BookedSeat` | uus API, seansi leht |
| Broneerimine | `Booking`, `BookedSeat` | vajab kasutaja kontot ja istekohtade valikut |
| Arvustused | `Review` | vajab kasutaja kontot, filmi leht |

## Sõltuvused

```
Kasutaja konto ──┬─> Broneerimine ──> Maksmine
                 └─> Arvustused
Istekohtade valik ─> Broneerimine
Filtrid, uudised   (sõltumatud)
```

## Soovitatud järjekord

1. **Filtrid** – žanri valik filmide lehel, kuupäev seansside lehel. Väike ja
   puudutab kõiki kihte (ORM, API, Vue).
2. **Uudised** – esimene täiesti uus API osa ja leht.
3. **Istekohtade kaart** – seansi saali kohad ja juba broneeritud kohad.
4. **Kasutaja konto** – registreerumine ja sisselogimine.
5. **Broneerimine** – kasutada `transaction.atomic`, et kaks inimest ei saaks
   sama kohta (andmebaasi piirang `unique_booked_seat_per_screening` on olemas).
6. **Arvustused**, siis **maksed**.

Tööjaotus on failis [TEAM_WORK_PLAN.md](TEAM_WORK_PLAN.md).
