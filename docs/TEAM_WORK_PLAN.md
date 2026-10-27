# Tööjaotus

Projekti teevad kaks inimest: **Rob** ja **Gerry**.

Põhimõte: kumbki ei ole "ainult frontend" ega "ainult backend". Iga
funktsiooni teeb üks inimene läbi kõigi kihtide (andmebaas → Django →
Vue → test) ja teine vaatab selle üle. Järgmise funktsiooni puhul
vahetatakse rollid.

## Kuidas üks ülesanne käib

1. Jira ülesanne → oma haru (`git switch -c filtrid`).
2. Tegija muudab vajalikud kihid: mudel/migratsioon, API, Vue leht, test.
3. Pull request GitHubis. Teine inimene vaatab üle ja käivitab:
   ```bash
   docker compose exec backend uv run python manage.py test
   cd frontend && npm run build
   ```
4. Pärast heakskiitu merge `main` harusse.

Ülevaataja ei kontrolli ainult koodi, vaid avab ka lehe brauseris ja proovib
funktsiooni ise.

## Ülesanded

| # | Ülesanne | Teeb (kõik kihid) | Vaatab üle | Mida see õpetab |
| --- | --- | --- | --- | --- |
| 1 | Žanri filter filmide lehel (`/api/movies/?genre=`) | Gerry | Rob | ORM filter, query parameeter, Vue `select` |
| 2 | Kuupäeva filter seansside lehel (`/api/screenings/?date=`) | Rob | Gerry | kuupäevad ja ajavööndid Djangos ja JS-is |
| 3 | Uudiste API ja leht (`News`) | Rob | Gerry | uus serializer, ViewSet, ruuter, uus leht |
| 4 | Kinode leht (`/api/cinemas/` on juba olemas) | Gerry | Rob | olemasoleva API kasutamine, `v-for` |
| 5 | Saali istekohtade kaart (`Seat`, `BookedSeat`) | Gerry | Rob | seotud tabelid, `select_related`, CSS grid |
| 6 | Registreerumine ja sisselogimine | Rob | Gerry | Django autentimine, vormid, sessioonid |
| 7 | Broneerimine (`Booking`, `BookedSeat`) | koos (paaris) | – | tehingud, andmebaasi piirangud |
| 8 | Arvustused (`Review`) | Gerry | Rob | POST päring, valideerimine (hinne 1–5) |

Iga rida sisaldab andmebaasi- või ORM-tööd, API-d, Vue lehte ja testi, nii et
mõlemad teevad kõiki osi.

## Testid

- Iga uus API otspunkt saab testi failis `cinema/test_api.py`.
- Andmebaasi piirangu muutmisel lisatakse test faili `cinema/tests.py`.
- Ülevaataja kirjutab vähemalt ühe lisatesti (näiteks vigane sisend → `400`).

## Andmebaas

- Mudeli muutmisel teeb tegija migratsiooni (`makemigrations`) ja paneb selle
  samasse commiti.
- Ülevaataja kontrollib `makemigrations --check` ja `seed_dev_data` toimimist
  ning vaatab DataGripis, et tabelid ja veerud on õiged.

## Kui midagi on ebaselge

Kirjuta küsimus Jira ülesande kommentaari või pull requesti, et mõlemad seda
näeksid.
