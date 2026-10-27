"""
Arendusandmed: žanrid, filmid, kinod, saalid, istekohad ja seansid.

Kõik andmed on väljamõeldud. Käsku võib käivitada mitu korda: olemasolevaid
ridu ei dubleerita, puuduvad lisatakse. Broneeringuid, makseid ega
kasutajaid see käsk ei loo.
"""

import random
from datetime import datetime, time, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from cinema.models import Cinema, Genre, Hall, Movie, MovieGenre, Screening, Seat

GENRES = [
    "Animatsioon",
    "Dokumentaal",
    "Draama",
    "Komöödia",
    "Märul",
    "Perefilm",
    "Põnevus",
    "Romantika",
    "Ulme",
    "Õudus",
]

# (pealkiri, kirjeldus, pikkus minutites, vanusepiirang, keel, žanrid,
#  päevi esilinastuseni (negatiivne = juba linastunud), esiletõstetud)
MOVIES = [
    (
        "Põhjatäht",
        "Noor meremees peab tormisel ööl juhatama laeva koju ainult tähtede järgi.",
        118, "MS-12", "eesti", ["Draama", "Märul"], -20, True,
    ),
    (
        "Viimane tramm",
        "Kaks võõrast jäävad südaööl seisma jäänud trammi ja avastavad, et neid seob rohkem, kui arvasid.",
        96, "MS-6", "eesti", ["Draama", "Romantika"], -35, False,
    ),
    (
        "Orbiit 9",
        "Kosmosejaama meeskond saab signaali, mis ei tohiks olla võimalik.",
        131, "K-12", "inglise", ["Ulme", "Põnevus"], -10, True,
    ),
    (
        "Siili suur seiklus",
        "Uudishimulik siil läheb metsa taha otsima kadunud sõpra.",
        84, "PERE", "eesti", ["Animatsioon", "Perefilm"], -28, False,
    ),
    (
        "Udu rabas",
        "Rabamatkal kaovad matkajad ükshaaval ja keegi ei mäleta, mitu neid alguses oli.",
        102, "K-16", "eesti", ["Õudus", "Põnevus"], -14, False,
    ),
    (
        "Pulm ja pool",
        "Kaks perekonda, üks pulm ja liiga palju sugulasi ühes talus.",
        109, "MS-6", "eesti", ["Komöödia", "Romantika"], -6, True,
    ),
    (
        "Kiirtee",
        "Kuller peab toimetama paki üle piiri enne, kui keegi teada saab, mis selles on.",
        114, "K-14", "inglise", ["Märul", "Põnevus"], -40, False,
    ),
    (
        "Saarte hääl",
        "Dokumentaalfilm saarte inimestest, kes hoiavad elus vanu laule.",
        78, "PERE", "eesti", ["Dokumentaal"], -50, False,
    ),
    (
        "Robotkoer Rex",
        "Tüdruk ehitab vanadest osadest koera, kes otsustab ise maailma päästa.",
        92, "PERE", "inglise", ["Animatsioon", "Perefilm", "Komöödia"], -3, False,
    ),
    (
        "Külm valgus",
        "Uurija naaseb kodulinna, et lahendada juhtum, mille ta kakskümmend aastat tagasi pooleli jättis.",
        124, "K-14", "eesti", ["Draama", "Põnevus"], -18, False,
    ),
    (
        "Tähetolm",
        "Astronoom ja muusik avastavad, et taevas on rohkem kui üks laul.",
        105, "MS-12", "prantsuse", ["Romantika", "Ulme"], 12, False,
    ),
    (
        "Talvemaa",
        "Põhjamaa küla ootab talve, mis seekord ei tahagi lõppeda.",
        99, "MS-6", "eesti", ["Draama", "Perefilm"], 21, False,
    ),
]

# (nimi, aadress, linn, postiindeks, saalid: (nimi, ekraani tüüp, ridu, kohti reas))
CINEMAS = [
    ("Kino Täheke", "Kinotänav 1", "Tallinn", "10111", [("Saal 1", "2D", 10, 14), ("Saal 2", "3D", 8, 12), ("Suur saal", "IMAX", 14, 20)]),
    ("Kino Laine", "Jõe tänav 5", "Tartu", "50101", [("Saal A", "2D", 9, 12), ("Saal B", "2D", 6, 10)]),
    ("Kino Majakas", "Ranna puiestee 12", "Pärnu", "80010", [("Väike saal", "2D", 6, 8), ("Suur saal", "3D", 10, 14)]),
]

BASE_PRICES = {"2D": Decimal("8.50"), "3D": Decimal("10.50"), "IMAX": Decimal("12.50")}
MATINEE_DISCOUNT = Decimal("1.50")  # seansid enne kella 15
ADS_MINUTES = 15  # reklaamid enne filmi
CLEANING_MINUTES = 15  # saali koristus seansside vahel
FIRST_SHOW = time(11, 0)
LAST_SHOW = time(22, 0)


class Command(BaseCommand):
    help = "Loob arenduseks väljamõeldud filmid, kinod, saalid, istekohad ja seansid (korduval käivitamisel ei dubleeri)."

    def add_arguments(self, parser):
        parser.add_argument("--days", type=int, default=7, help="Mitme päeva seansid luua alates tänasest (vaikimisi 7).")

    @transaction.atomic
    def handle(self, *args, days, **options):
        if days < 1:
            self.stderr.write("--days peab olema vähemalt 1.")
            return

        today = timezone.localdate()
        genres = {name: Genre.objects.get_or_create(name=name)[0] for name in GENRES}

        movies = []
        for title, description, minutes, age, language, genre_names, release_in, featured in MOVIES:
            movie, _ = Movie.objects.get_or_create(
                title=title,
                defaults={
                    "description": description,
                    "duration_minutes": minutes,
                    "age_rating": age,
                    "language": language,
                    "release_date": today + timedelta(days=release_in),
                    "is_featured": featured,
                },
            )
            for name in genre_names:
                MovieGenre.objects.get_or_create(movie=movie, genre=genres[name])
            movies.append(movie)

        halls = []
        for name, address, city, postal_code, hall_specs in CINEMAS:
            cinema, _ = Cinema.objects.get_or_create(
                name=name,
                defaults={"street_address": address, "city": city, "postal_code": postal_code, "country": "Eesti"},
            )
            for hall_name, screen_type, rows, per_row in hall_specs:
                hall, _ = Hall.objects.get_or_create(
                    cinema=cinema,
                    name=hall_name,
                    defaults={"screen_type": screen_type, "capacity": rows * per_row},
                )
                row_letters = [chr(ord("A") + i) for i in range(rows)]
                Seat.objects.bulk_create(
                    [Seat(hall=hall, row=row, number=n) for row in row_letters for n in range(1, per_row + 1)],
                    ignore_conflicts=True,  # unique_seat_in_hall jätab olemasolevad kohad vahele
                )
                halls.append(hall)

        created_screenings = 0
        for offset in range(days):
            day = today + timedelta(days=offset)
            showing = [m for m in movies if m.release_date is None or m.release_date <= day]
            if not showing:
                continue
            for hall in halls:
                created_screenings += self.schedule_hall_day(hall, day, showing)

        self.stdout.write(
            self.style.SUCCESS(
                f"Valmis: {Genre.objects.count()} žanrit, {Movie.objects.count()} filmi, "
                f"{Cinema.objects.count()} kino, {Hall.objects.count()} saali, {Seat.objects.count()} istekohta, "
                f"{Screening.objects.count()} seanssi ({created_screenings} uut)."
            )
        )

    def schedule_hall_day(self, hall, day, showing):
        """Täidab saali ühe päeva seanssidega, mis ei kattu. Sama päeva ja saali kava on alati sama."""
        rng = random.Random(f"{hall.cinema.name}/{hall.name}/{day.isoformat()}")
        start = timezone.make_aware(datetime.combine(day, FIRST_SHOW)) + timedelta(minutes=rng.choice([0, 30, 60]))
        last_start = timezone.make_aware(datetime.combine(day, LAST_SHOW))
        created = 0
        while start <= last_start:
            movie = rng.choice(showing)
            end = start + timedelta(minutes=ADS_MINUTES + movie.duration_minutes)
            price = BASE_PRICES.get(hall.screen_type, BASE_PRICES["2D"])
            if timezone.localtime(start).hour < 15:
                price -= MATINEE_DISCOUNT
            _, was_created = Screening.objects.get_or_create(
                hall=hall,
                starts_at=start,
                defaults={
                    "movie": movie,
                    "ends_at": end,
                    "language": movie.language,
                    "subtitles": "eesti, vene" if movie.language != "eesti" else "inglise",
                    "base_price": price,
                },
            )
            created += was_created
            start = self.round_up(end + timedelta(minutes=CLEANING_MINUTES))
        return created

    @staticmethod
    def round_up(moment, minutes=15):
        """Ümardab aja järgmise veerandtunnini, et seansid algaksid ilusatel aegadel."""
        moment = moment.replace(second=0, microsecond=0)
        remainder = moment.minute % minutes
        return moment + timedelta(minutes=minutes - remainder) if remainder else moment
