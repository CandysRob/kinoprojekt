from datetime import datetime, timedelta
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Cinema, Genre, Hall, Movie, MovieGenre, Screening


class ApiTestData(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.drama = Genre.objects.create(name="Draama")
        cls.movie = Movie.objects.create(title="Põhjatäht", description="Film tähest.", duration_minutes=110)
        cls.other_movie = Movie.objects.create(title="Aurora", duration_minutes=95)
        MovieGenre.objects.create(movie=cls.movie, genre=cls.drama)

        cls.cinema = Cinema.objects.create(
            name="Kino Täht", street_address="Tänav 1", city="Tallinn", postal_code="10111", country="Eesti"
        )
        cls.hall = Hall.objects.create(cinema=cls.cinema, name="Saal 1", capacity=80)

        def screening(movie, starts_at):
            return Screening.objects.create(
                movie=movie, hall=cls.hall, starts_at=starts_at, ends_at=starts_at + timedelta(hours=2), base_price=Decimal("9.50")
            )

        now = timezone.now()
        cls.screening = screening(cls.movie, now + timedelta(days=1))
        cls.later_screening = screening(cls.other_movie, now + timedelta(days=2))
        cls.past_screening = screening(cls.movie, now - timedelta(days=1))


class MovieApiTests(ApiTestData):
    def test_list_returns_movies_with_genres(self):
        data = self.client.get(reverse("movie-list")).json()
        self.assertEqual([m["title"] for m in data], ["Aurora", "Põhjatäht"])
        self.assertEqual(data[1]["genres"], [{"id": self.drama.id, "name": "Draama"}])

    def test_detail_includes_description(self):
        data = self.client.get(reverse("movie-detail", args=[self.movie.id])).json()
        self.assertEqual(data["description"], "Film tähest.")

    def test_missing_movie_returns_404(self):
        self.assertEqual(self.client.get(reverse("movie-detail", args=[999999])).status_code, 404)


class MovieDateFilterTests(ApiTestData):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        def screening(movie, year, month, day, hour, minute=0):
            # make_aware kasutab settings.TIME_ZONE-i ehk Eesti aega
            starts_at = timezone.make_aware(datetime(year, month, day, hour, minute))
            Screening.objects.create(
                movie=movie, hall=cls.hall, starts_at=starts_at, ends_at=starts_at + timedelta(hours=2), base_price=Decimal("9.50")
            )

        # Põhjatähel on 10. märtsil kaks seanssi
        screening(cls.movie, 2030, 3, 10, 14)
        screening(cls.movie, 2030, 3, 10, 20)
        # Aurora algab 11. märtsil 00:30 Eesti aja järgi (UTC järgi on see veel 10. märts)
        screening(cls.other_movie, 2030, 3, 11, 0, 30)

    def titles(self, date):
        return [m["title"] for m in self.client.get(reverse("movie-list"), {"date": date}).json()]

    def test_movie_with_many_screenings_on_date_appears_once(self):
        self.assertEqual(self.titles("2030-03-10"), ["Põhjatäht"])

    def test_date_is_in_estonian_time(self):
        self.assertEqual(self.titles("2030-03-11"), ["Aurora"])

    def test_date_without_screenings_returns_empty_list(self):
        self.assertEqual(self.titles("2030-03-12"), [])

    def test_without_date_returns_all_movies(self):
        self.titles("2030-03-12")  # filtreeritud nimekiri ei tohi jääda vahemälus ilma filtrita nimekirja asemele
        data = self.client.get(reverse("movie-list")).json()
        self.assertEqual([m["title"] for m in data], ["Aurora", "Põhjatäht"])

    def test_invalid_date_returns_400(self):
        self.assertEqual(self.client.get(reverse("movie-list"), {"date": "homme"}).status_code, 400)
        self.assertEqual(self.client.get(reverse("movie-list"), {"date": "2030-02-30"}).status_code, 400)


class ScreeningApiTests(ApiTestData):
    def test_list_contains_only_upcoming_screenings_in_order(self):
        data = self.client.get(reverse("screening-list")).json()
        self.assertEqual([s["id"] for s in data], [self.screening.id, self.later_screening.id])

    def test_screening_includes_movie_hall_and_cinema(self):
        screening = self.client.get(reverse("screening-list")).json()[0]
        self.assertEqual(screening["movie"]["title"], "Põhjatäht")
        self.assertEqual(screening["hall"]["name"], "Saal 1")
        self.assertEqual(screening["cinema"]["name"], "Kino Täht")

    def test_filter_by_movie(self):
        data = self.client.get(reverse("screening-list"), {"movie": self.other_movie.id}).json()
        self.assertEqual([s["id"] for s in data], [self.later_screening.id])

    def test_invalid_movie_filter_returns_400(self):
        self.assertEqual(self.client.get(reverse("screening-list"), {"movie": "x"}).status_code, 400)


class GenreAndCinemaApiTests(ApiTestData):
    def test_genres_and_cinemas(self):
        self.assertEqual(self.client.get(reverse("genre-list")).json(), [{"id": self.drama.id, "name": "Draama"}])
        cinemas = self.client.get(reverse("cinema-list")).json()
        self.assertEqual(cinemas[0]["halls"][0]["name"], "Saal 1")


class ApiSafetyTests(ApiTestData):
    def test_no_user_booking_or_payment_endpoints(self):
        data = self.client.get(reverse("api-root")).json()
        self.assertEqual(set(data), {"movies", "genres", "cinemas", "screenings"})

    def test_anonymous_users_cannot_write(self):
        self.assertEqual(self.client.post(reverse("movie-list"), {"title": "Uus"}).status_code, 403)
        self.assertEqual(self.client.delete(reverse("movie-detail", args=[self.movie.id])).status_code, 403)
