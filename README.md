# Kinoprojekt

Selles repos on kinoprojekti veebirakendus (Django + Vue), andmebaasi struktuur
ja backendi valiku võrdlus.

- [`project.sql`](project.sql) – andmebaasi struktuur (PostgreSQL)
- see fail – käivitamine, backendi keel, ORM-id ja raamistikud
- [`docs/ROADMAP.md`](docs/ROADMAP.md) – mis töötab, mis on pooleli ja mis järjekorras edasi teha
- `config/` – Django projekti seaded ja URL-id
- `cinema/` – mudelid, API, admin-paneel, arendusandmete käsk ja testid
- `frontend/` – Vue 3 + Vite kasutajaliides

| Teenus | Aadress |
| --- | --- |
| Kasutajaliides (Vue) | <http://localhost:5173/> |
| API | <http://localhost:8000/api/> |
| Admin-paneel | <http://localhost:8000/admin/> |
| Tervisekontroll | <http://localhost:8000/health/> |

## Käivitamine Dockeriga (soovitatav)

Vaja on ainult Docker Desktopi.

1. Tee seadete fail ja muuda selles `DJANGO_SECRET_KEY` ja `POSTGRES_PASSWORD`:

   ```bash
   cp .env.example .env
   ```

   `.env` on `.gitignore`'is, seda reposse ei panda. Uue võtme saad käsuga, mis
   on kirjas `.env.example` failis.

2. Käivita andmebaas, backend ja frontend:

   ```bash
   docker compose up -d --build
   ```

   Backend käivitub alles siis, kui andmebaas on valmis, ja frontend alles siis,
   kui backend vastab. Olekut näeb käsuga `docker compose ps`.

3. Loo tabelid ja lisa arendusandmed:

   ```bash
   docker compose exec backend uv run python manage.py migrate
   docker compose exec backend uv run python manage.py seed_dev_data
   ```

4. Ava <http://localhost:5173/>. Admin-paneeli jaoks loo kasutaja:

   ```bash
   docker compose exec backend uv run python manage.py createsuperuser
   ```

Koodi muudatused jõuavad konteineritesse kohe (kaust on kaardistatud), Django
ja Vite laevad end ise uuesti. Uue Pythoni või npm-i sõltuvuse järel tee
`docker compose up -d --build`.

Andmebaasi andmed on Dockeri volume'is `pgdata` ja jäävad alles ka pärast
`docker compose down`. Parool määratakse ainult andmebaasi esimesel loomisel.
Kui muudad hiljem `POSTGRES_PASSWORD`-i, tuleb andmed kustutada käsuga
`docker compose down -v` (see kustutab kogu andmebaasi).

## Käivitamine ilma Dockerita

Vaja on [uv](https://docs.astral.sh/uv/), Node.js 20.19+ ja PostgreSQL 16
(näiteks ainult andmebaas Dockerist: `docker compose up -d db`).

```bash
uv sync
uv run python manage.py migrate
uv run python manage.py seed_dev_data
uv run python manage.py runserver
```

Teises terminalis:

```bash
cd frontend
npm install
npm run dev
```

Vite suunab `/api` päringud aadressile `http://127.0.0.1:8000`, seega CORS-i
seadistust pole vaja. Teise aadressi jaoks määra `API_PROXY_TARGET`.

## Arendusandmed

```bash
uv run python manage.py seed_dev_data            # 7 päeva seansse
uv run python manage.py seed_dev_data --days 14  # rohkem päevi
```

Käsk loob väljamõeldud žanrid, filmid, kinod, saalid, istekohad ja seansid.
Seda võib käivitada mitu korda: olemasolevaid ridu ei dubleerita, lisatakse
ainult puuduvad (näiteks uue päeva seansid). Sama päeva ja saali kava on alati
sama ning seansid samas saalis ei kattu. Kasutajaid, broneeringuid ega makseid
käsk ei loo.

## API

API on ainult lugemiseks. Kasutajate, broneeringute ja maksete andmeid see ei
näita.

| Otspunkt | Mida tagastab |
| --- | --- |
| `GET /api/movies/` | kõik filmid koos žanritega |
| `GET /api/movies/{id}/` | üks film koos kirjeldusega |
| `GET /api/genres/` | kõik žanrid |
| `GET /api/cinemas/` | kõik kinod koos saalidega |
| `GET /api/screenings/` | tulevased seansid koos filmi, saali ja kinoga; `?movie={id}` näitab ühe filmi seansse |

Nimekirjad on tavalised JSON-massiivid. Puuduva kirje korral tuleb vastus
`404`, vigase `movie` väärtuse korral `400`.

## Testid ja kontrollid

```bash
uv run python manage.py test                       # backend ja API
uv run python manage.py makemigrations --check     # mudelid ja migratsioonid on kooskõlas
cd frontend && npm run build                       # frontend kompileerub
```

Dockeris: `docker compose exec backend uv run python manage.py test`.

### Mudelid ja `project.sql`

Tabelid luuakse Django migratsioonidega (`cinema/migrations/`), mitte
`project.sql`-ist. Mudelites on ingliskeelsed nimed, andmebaasis jäävad
`db_table` ja `db_column` abil samad eestikeelsed tabelid ja veerud.
Skeemi muutmiseks muuda `cinema/models.py` ja tee uus migratsioon:

```bash
uv run python manage.py makemigrations
uv run python manage.py migrate
```

Erinevused `project.sql`-iga:

- Tabelis `user` on Django sisselogimise jaoks lisaveerud `last_login`,
  `is_active`, `is_staff` ja `is_superuser`, veerg `user` (kasutajanimi) on
  unikaalne ja `password_hash` hoiab Django parooliräsi. Õiguste jaoks tekivad
  ka tabelid `user_groups` ja `user_user_permissions`.
- Kustutamise reegleid (`on delete cascade` jne) täidab Django, mitte
  andmebaas. Django kaudu kustutades on tulemus sama, aga otse SQL-iga
  (nt DataGripis) ei saa rida kustutada, kui sellele viitavad teised read.
- Arvustuse hinde piirang on nimega `review_rating_between_1_and_5`.

## Andmebaasi struktuur

Andmebaasis on järgmised tabelid:

- `user` – kasutajad (sünnikuupäev, mitte vanus, sest vanus muutub iga päev)
- `kino`, `kinosaalid`, `istekohad` – kinod, nende saalid ja saalide kohad
- `filmid`, `žanrid`, `filmid_zanrid` – filmid ja žanrid (mitu-mitmele seos)
- `seansid` – milline film, mis saalis ja mis ajal
- `broneeringud`, `broneeritud_kohad` – kasutaja broneering ja selle kohad
- `maksed` – broneeringu maksed
- `arvustused` – kasutajate hinnangud filmidele (1–5)
- `uudised` – kino teadaanded

Olulisemad piirangud:

- istekoht on saalis kordumatu rea ja numbri järgi;
- sama koht saab ühel seansil olla broneeritud ainult üks kord;
- seansi lõpp peab olema pärast algust;
- arvustuse hinne on vahemikus 1–5.

Väljad, mis võivad olla tühjad (`null`), on näiteks filmi kirjeldus, kasutaja
sünnikuupäev, makse aeg (pole veel makstud) ja uudise avaldamise aeg (mustand).
Backend peab nende puhul arvestama, et väärtust ei pruugi olla.

## Valitud keel: Python

Valisime backendi keeleks Pythoni. Põhjused:

- Python on loetav ja lihtne õppida, nii et mõlemad saame koodist hästi aru.
- Pythonis on mitu küpset veebiraamistikku ja ORM-i, mis toetavad nii
  PostgreSQL-i kui MariaDB/MySQL-i. Kui peaksime andmebaasi vahetama, ei pea
  keelt vahetama.
- Testandmete genereerimiseks on olemas Faker.

Meie andmebaas on PostgreSQL 16. Kõik allpool võrreldud variandid toetavad
nii PostgreSQL-i kui MariaDB/MySQL-i.

## Variandid

### 1. Django + Django ORM

Django on "kõik ühes" raamistik: selles on olemas ORM, migratsioonid,
admin-paneel, kasutajate autentimine, vormide valideerimine ja testimise
tööriistad. Tabelid kirjeldatakse Pythoni klassidena (`models.py`) ja Django
genereerib nende põhjal migratsioonid.

**Plussid meie projekti jaoks**

- Migratsioonid on sisse ehitatud: `makemigrations` ja `migrate`. Kui lisame
  näiteks uue tabeli, piisab mudeli lisamisest.
- Kuna tegime SQL-i enne valmis, on oluline, et ORM saaks olemasoleva skeemiga
  kohaneda. Käsk `inspectdb` loeb olemasolevast andmebaasist mudelid sisse ja
  `db_table` / `db_column` lubavad hoida Pythonis ingliskeelseid nimesid
  (`title`), aga andmebaasis eestikeelseid (`pealkiri`).
- Piirangud, mida kino vajab (koht on seansil broneeritud ainult üks kord,
  seansi lõpp on pärast algust), saab kirjutada otse mudelisse
  (`UniqueConstraint`, `CheckConstraint`).
- Admin-paneel annab kohe võimaluse filme, seansse, saale ja uudiseid käsitsi
  lisada, ilma et peaks selleks eraldi kasutajaliidest tegema.
- Dokumentatsioon on väga põhjalik ja kogukond suur, enamikule vigadele leiab
  vastuse.

**Miinused**

- Raamistik on suur ja sellel on oma kindel viis asjade tegemiseks. Alguses
  tuleb õppida, kuhu mis fail käib.
- JSON API jaoks on vaja lisaks Django REST Frameworki (või käsitsi
  `JsonResponse`), sest Django ise on mõeldud pigem HTML-lehtede jaoks.
- Migratsioonid eeldavad, et skeemi omanik on Django. Kui muudame tabelit
  DataGripis käsitsi, lähevad mudelid ja andmebaas lahku.

### 2. FastAPI + SQLAlchemy + Alembic

FastAPI on kerge ja kiire API-raamistik. Andmebaasiga ise ei tegele, selle
jaoks kasutatakse SQLAlchemy ORM-i ja migratsioonideks Alembicut. Sisend- ja
väljundandmed kirjeldatakse Pydanticu mudelitega ning API dokumentatsioon
(Swagger) tekib automaatselt.

**Plussid meie projekti jaoks**

- Kui frontend vajab ainult JSON API-t, on FastAPI just selleks tehtud.
  Automaatne Swaggeri leht teeb API testimise lihtsaks.
- SQLAlchemy on väga paindlik: keerulisemad päringud, näiteks "vabad kohad
  sellel seansil", saab kirjutada peaaegu nagu SQL-i.
- SQLAlchemy oskab olemasolevat andmebaasi sisse lugeda (automap või
  `sqlacodegen`), mis sobib, kui SQL on enne valmis.

**Miinused**

- Tuleb kokku panna kolm eraldi tööriista (FastAPI, SQLAlchemy, Alembic) ja
  seadistada need ise. Admin-paneeli, autentimist ega kasutajate haldust pole.
- SQLAlchemy õppimise lävi on kõrge, selles on kaks erinevat stiili (Core ja
  ORM) ning dokumentatsioon on mahukas.
- Alembic ei tuvasta kõiki muudatusi automaatselt, migratsioone tuleb
  rohkem käsitsi üle kontrollida.

### 3. Flask + Peewee

Flask on minimaalne raamistik, kus on ainult marsruudid (URL -> funktsioon).
Peewee on väike ja lihtne ORM, mille mudelid näevad välja sarnased Django
omadele.

**Plussid meie projekti jaoks**

- Väga väike ja kiire selgeks saada, sobib väikesele projektile.
- Peewee'l on tööriist `pwiz`, mis loeb olemasolevast andmebaasist mudelid
  sisse, nii et meie valmis SQL-ist saaks kohe koodi.
- Vähe "maagiat": on lihtne aru saada, mis päring andmebaasi läheb.

**Miinused**

- Peewee migratsioonid (`playhouse.migrate`) tuleb kirjutada käsitsi, ei ole
  automaatset `makemigrations` sarnast lahendust. Meie skeem muutub veel
  (näiteks istekohtade ajutine lukustamine broneerimise ajal), nii et see
  oleks palju lisatööd.
- Peewee kogukond on palju väiksem kui Djangol või SQLAlchemyl.
- Autentimise, valideerimise ja admin-paneeli peab ise juurde ehitama või
  eraldi lisadena otsima.

## Võrdlus

| | Django ORM | FastAPI + SQLAlchemy | Flask + Peewee |
| --- | --- | --- | --- |
| PostgreSQL / MariaDB | jah / jah | jah / jah | jah / jah |
| Olemasoleva DB sisselugemine | `inspectdb` | automap, `sqlacodegen` | `pwiz` |
| Migratsioonid | sisse ehitatud, automaatsed | Alembic, osaliselt automaatsed | käsitsi |
| Admin ja autentimine | olemas | pole | pole |
| Õppimise lävi | keskmine | kõrge | madal |
| Kogukond ja dokumentatsioon | väga suur | suur | väike |

## Valik: Django + Django ORM

Valisime Django, sest meie projektis on palju omavahel seotud tabeleid (kinod,
saalid, kohad, seansid, broneeringud, maksed, uudised) ja skeem muutub veel.
Selle juures on kõige suurem abi automaatsetest migratsioonidest, mis on
Djangos sisse ehitatud. Peewee puhul peaksime neid käsitsi kirjutama ja
SQLAlchemy puhul seadistama eraldi tööriista.

Kuna SQL-skeem on enne valmis, on oluline, et ORM ei sunniks tabeleid ümber
nimetama. Djangos saame `inspectdb`-ga olemasolevast andmebaasist mudelid
sisse lugeda ning `db_table` ja `db_column` abil eestikeelsed tabelid ja
veerud alles jätta.

Kinoprojektis on vaja ka kasutajaid, sisselogimist ja võimalust filme,
seansse ja uudiseid lisada. Django annab need kohe kaasa (admin-paneel,
autentimine). FastAPI oleks puhta API jaoks kergem ja kiirem, aga selle
suurusega projekti juures ei ole kiirus probleem ja puuduvate osade ise
ehitamine võtaks rohkem aega kui Django õppimine.
