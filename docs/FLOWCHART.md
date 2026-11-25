# Flowchart: filmi leidmine ja selle seansside vaatamine

Diagramm on failis [FLOWCHART.drawio](FLOWCHART.drawio). Selle saab avada ja muuta aadressil
<https://app.diagrams.net/> (File → Open from → Device).

## Miks me valisime selle protsessi

Kõige loogilisem oleks olnud kujutada piletite ostmist, aga meie kinolehel see veel ei tööta.
Andmebaasis on tabelid broneeringute, istekohtade ja maksete jaoks olemas, kuid API-t ja lehte nende
jaoks pole. Filmi lehel on ka kirjas „Piletite broneerimine pole veel valmis.”

Seepärast valisime protsessi, mis päriselt töötab: **kasutaja leiab filmi ja vaatab, millal seda
kinos näidatakse**. Iga diagrammi samm on rakenduses olemas. Broneerimine on diagrammil eraldi
märkusena, et oleks näha, mis on alles planeeritud.

## Kuidas protsess töötab

1. **Algus:** kasutaja avab kino avalehe.
2. Süsteem laeb filmide nimekirja (`GET /api/movies/`).
3. Kui laadimine ebaõnnestub, näeb kasutaja veateadet ja nuppu „Proovi uuesti”. Nupule vajutades
   proovitakse uuesti.
4. Kasutaja võib valida seansi kuupäeva. Kui ta kuupäeva ei vali, näeb ta kõiki filme.
5. Kui kuupäev on valitud, otsib süsteem ainult need filmid, millel on sel päeval seanss
   (`GET /api/movies/?date=…`). Kui selliseid filme pole, kuvatakse teade „Seansse pole. Vali teine
   kuupäev.” ja kasutaja saab valida uue kuupäeva või filtri tühjendada.
6. Kasutaja klõpsab filmikaardil.
7. Avaneb filmi leht. Süsteem laeb filmi andmed ja selle filmi tulevased seansid
   (`GET /api/movies/{id}/` ja `GET /api/screenings/?movie={id}`).
8. Kui seansse on, näidatakse tabelit, kus on kuupäev, kell, kino, saal ja hind. Kui seansse pole,
   kuvatakse teade „Sellel filmil pole praegu seansse.”
9. **Lõpp:** kasutaja on filmi andmed ja seansid üle vaadanud.

Lihtsuse mõttes ei ole diagrammil filmi lehe laadimise viga. See käitub samamoodi nagu 3. sammus:
kuvatakse veateade ja nupp „Proovi uuesti”.

## Mida harud tähendavad

| Otsus (romb) | Jah | Ei |
| --- | --- | --- |
| Kas filmide laadimine õnnestus? | protsess läheb edasi | veateade, kasutaja proovib uuesti |
| Kas kasutaja valib seansi kuupäeva? | süsteem otsib selle päeva filmid | näidatakse kõiki filme |
| Kas sel päeval on filme? | kasutaja saab filmi valida | teade, kasutaja valib teise kuupäeva |
| Kas filmil on tulevasi seansse? | näidatakse seansside tabelit | teade, et seansse pole |

## Küsimused

### 1. Millal kasutatakse flowcharti?

Flowcharti kasutatakse siis, kui on vaja näidata, mis järjekorras mingi protsess toimub. Näiteks
enne programmi või veebilehe tegemist, et läbi mõelda, mida kasutaja teeb ja mida süsteem vastab.
Seda kasutatakse ka siis, kui tahame protsessi teistele lihtsalt selgitada või leida sealt vigu.

### 2. Milliseid flowcharti sümboleid teate ja mida need tähistavad?

- **Ovaal** – protsessi algus või lõpp.
- **Ristkülik** – tegevus ehk samm, mida kasutaja või süsteem teeb.
- **Romb** – otsus või tingimus. Rombist lähevad välja vähemalt kaks noolt, näiteks „Jah” ja „Ei”.
- **Nool** – näitab, mis suunas protsess liigub ja mis samm tuleb järgmisena.
- **Rööpkülik** – andmete sisestamine või väljastamine (meie diagrammis seda pole).

### 3. Milliseid otsuseid ja võimalikke teekondi teie diagramm näitab?

Diagrammil on neli otsust: kas filmide laadimine õnnestus, kas kasutaja valib kuupäeva, kas sel
päeval on filme ja kas filmil on tulevasi seansse.

Võimalikud teekonnad on näiteks:

- Kasutaja ei vali kuupäeva, klõpsab filmil ja näeb seansside tabelit.
- Kasutaja valib kuupäeva, sel päeval on filme ja ta näeb valitud filmi seansse.
- Kasutaja valib kuupäeva, kus seansse pole, ning peab valima teise kuupäeva.
- Valitud filmil pole tulevasi seansse ja kasutaja näeb vastavat teadet.
- Filmide laadimine ebaõnnestub ja kasutaja proovib uuesti.

### 4. Mis kasu on flowcharti kasutamisest?

Flowchart aitab protsessi kiiresti mõista, ilma et peaks koodi lugema. Sellelt on hästi näha kõik
võimalikud olukorrad, ka need, kus midagi läheb valesti. Nii on lihtsam leida puuduvaid samme ja
vigu juba enne programmeerimist. Lisaks saavad meeskonnaliikmed sama pildi põhjal ühtemoodi aru,
kuidas lehekülg töötab.
