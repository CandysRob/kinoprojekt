# Kinoprojekti teekaart

Seis: oktoober 2026. Selles failis on kirjas, mis praegu töötab, mis on
teadlikult pooleli ja mis järjekorras on mõistlik edasi teha.

> **Jira:** repos ega kaasasolevates dokumentides ei ole Jira ülesannete
> numbreid ega pealkirju. Allpool on funktsioonid nimetatud sisu järgi ja
> veerg "Jira" on tühi. Lisage sinna oma ülesannete numbrid. Ülesannete
> aktsepteerimistingimused on Jiras, mitte siin.

## Mis praegu töötab

| Osa | Sisu |
| --- | --- |
| Andmebaas | PostgreSQL 16, 13 tabelit `project.sql` järgi, Django migratsioonid (`cinema/migrations/0001_initial.py`) |
| Mudelid | `User`, `Cinema`, `Hall`, `Seat`, `Movie`, `Genre`, `MovieGenre`, `Screening`, `Booking`, `BookedSeat`, `Payment`, `Review`, `News` (`cinema/models.py`) |
| Piirangud | koht saalis kordumatu, koht seansil broneeritav üks kord, seansi lõpp pärast algust, hinne 1–5 |
| Admin-paneel | kõigi tabelite lisamine ja muutmine (`/admin/`) |
| API | filmid, žanrid, kinod, seansid, ainult lugemiseks (`/api/`) |
| Kasutajaliides | avaleht, filmide kataloog, filmi leht, seansside kava (Vue 3) |
| Arendusandmed | `manage.py seed_dev_data` |
| Testid | mudelite piirangud, API, arendusandmete käsk (`cinema/tests.py`, `test_api.py`, `test_seed.py`) |
| Arenduskeskkond | `docker compose`: db, backend, frontend |

## Mis selles etapis lisandus

- Django REST Frameworki API filmide, žanrite, kinode ja seansside jaoks
  (filtrid, lehekülgedeks jagamine, 400/404 vastused).
- Vue 3 + Vite frontend: ühine päis ja jalus, filmikaart, plakat, olekuteated
  (laadimine, tühi, viga, "tulekul"), reageeriv paigutus telefonist arvutini.
- Arendusandmete käsk, mida võib käivitada mitu korda.
- Docker Compose teenused backendi ja frontendi jaoks koos tervisekontrollidega.
- API ja arendusandmete testid.

Andmebaasi skeemi selles etapis ei muudetud, olemasolevad mudelid katsid kõik
vajaliku.

## Teadlikult pooleli

| Funktsioon | Praegune seis | Jira |
| --- | --- | --- |
| Piletite broneerimine | tabelid `broneeringud` ja `broneeritud_kohad` on olemas, API ja kasutajaliides puuduvad; seansi juures on "tulekul" teade | |
| Maksed | tabel `maksed` on olemas, makseteenust ega API-t pole | |
| Kasutaja konto (registreerumine, sisselogimine) | kasutajamudel ja Django autentimine on olemas, avalikku registreerumist ega sisselogimise lehte pole | |
| Arvustused | tabel `arvustused` on olemas, API ja kasutajaliides puuduvad | |
| Uudised | tabel `uudised` on olemas, avalehel on "tulekul" teade | |
| Filmiplakatid | väli `plakati_url` on olemas, arendusandmetes plakateid pole (kuvatakse genereeritud kujundus) | |
| Eriüritused, laiendatud administreerimine | pole alustatud | |
| Toodangukeskkond | ainult arendusseadistus (`runserver`, Vite dev server) | |

## Mida tulevased funktsioonid saavad kasutada

| Funktsioon | Mudelid | Olemasolev API / kood |
| --- | --- | --- |
| Istekohtade valik | `Seat`, `Hall`, `BookedSeat` (`unique_booked_seat_per_screening`) | `GET /api/screenings/{id}/`, `ShowtimeChip.vue` |
| Broneerimine | `Booking`, `BookedSeat`, `Screening.base_price` | `ScreeningSerializer` |
| Maksmine | `Payment` (`paid_at` null = maksmata) | – |
| Kasutaja konto | `User` (`AUTH_USER_MODEL = "cinema.User"`) | API vaikeõigus `IsAuthenticatedOrReadOnly` |
| Arvustused | `Review` (`review_rating_between_1_and_5`) | `FilmDetailView.vue` |
| Uudised | `News` (`cinema` null = kõigile kinodele, `published_at` null = mustand) | `HomeView.vue` uudiste plokk |
| Kinode lehed | `Cinema`, `Hall` | `GET /api/cinemas/{id}/` |

Uus API osa käib `cinema/serializers.py`, `cinema/api_views.py` ja
`cinema/api_urls.py` kaudu. Frontendi päringud on `frontend/src/api/cinema.js`
failis.

## Sõltuvused

```
Kasutaja konto ──┬─> Broneerimine ──> Maksmine
                 └─> Arvustused
Istekohtade valik ─> Broneerimine
Uudised            (sõltumatu)
Kinode lehed       (sõltumatu)
```

- Broneerimine vajab sisselogitud kasutajat (`Booking.user` on kohustuslik) ja
  istekohtade valikut.
- Maksmine vajab broneeringut (`Payment.booking`).
- Arvustus vajab kasutajat (`Review.user`).
- Uudiste ja kinode lehed vajavad ainult olemasolevaid tabeleid ja uut API osa.

## Soovitatud järjekord

1. **Uudised** – väike ja sõltumatu: üks lugemis-API (ainult avaldatud uudised)
   ja avalehe ploki asendamine. Hea esimene ülesanne API laiendamise
   harjutamiseks.
2. **Istekohtade kaart** – seansi saali kohad ja juba broneeritud kohad
   (lugemine). Broneerimise eeldus, mis ei vaja veel sisselogimist.
3. **Kasutaja konto** – registreerumine ja sisselogimine (Django sessioonid
   või token). Vajalik broneerimiseks ja arvustusteks.
4. **Broneerimine** – kohtade valik ja broneeringu loomine. Kasutada
   tehingut (`transaction.atomic`), et kaks inimest ei saaks sama kohta.
   Andmebaasi piirang `unique_booked_seat_per_screening` on juba olemas.
5. **Arvustused** – hinne ja kommentaar filmi lehel.
6. **Maksmine** – makseteenuse liides (alguses testrežiimis).
7. **Eriüritused ja laiendatud administreerimine.**

**Soovitatud järgmine samm:** istekohtade kaart (punkt 2), kui eesmärk on
jõuda kiiresti broneerimiseni; uudised (punkt 1), kui on vaja väikest ja
iseseisvat ülesannet.
