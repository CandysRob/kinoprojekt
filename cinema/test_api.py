from datetime import datetime, time, timedelta
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Cinema, Genre, Hall, Movie, MovieGenre, Screening


class ApiTestData(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.drama = Genre.objects.create(name="Draama")
        cls.comedy = Genre.objects.create(name="Komöödia")
        cls.movie = Movie.objects.create(
            title="Põhjatäht", description="Film tähest.", duration_minutes=110, age_rating="MS-12", is_featured=True
        )
        cls.other_movie = Movie.objects.create(title="Aurora", duration_minutes=95)
        cls.old_movie = Movie.objects.create(title="Vana film", duration_minutes=90)
        MovieGenre.objects.create(movie=cls.movie, genre=cls.drama)
        MovieGenre.objects.create(movie=cls.other_movie, genre=cls.comedy)

        cls.cinema = Cinema.objects.create(
            name="Kino Täht", street_address="Tänav 1", city="Tallinn", postal_code="10111", country="Eesti"
        )
        cls.other_cinema = Cinema.objects.create(
            name="Kino Laine", street_address="Tänav 2", city="Tartu", postal_code="50101", country="Eesti"
        )
        cls.hall = Hall.objects.create(cinema=cls.cinema, name="Saal 1", capacity=80)
        cls.other_hall = Hall.objects.create(cinema=cls.other_cinema, name="Saal A", capacity=60)

        # Homme kell 18:00 ja ülehomme kell 20:00 Eesti aja järgi
        tomorrow = timezone.localdate() + timedelta(days=1)
        cls.tomorrow = tomorrow
        start = timezone.make_aware(datetime.combine(tomorrow, time(18, 0)))
        later = timezone.make_aware(datetime.combine(tomorrow + timedelta(days=1), time(20, 0)))
        cls.screening = Screening.objects.create(
            movie=cls.movie, hall=cls.hall, starts_at=start, ends_at=start + timedelta(minutes=125), base_price=Decimal("9.50")
        )
        cls.later_screening = Screening.objects.create(
            movie=cls.other_movie, hall=cls.other_hall, starts_at=later, ends_at=later + timedelta(minutes=110), base_price=Decimal("8.00")
        )
        past = timezone.now() - timedelta(days=2)
        cls.past_screening = Screening.objects.create(
            movie=cls.old_movie, hall=cls.hall, starts_at=past, ends_at=past + timedelta(minutes=100), base_price=Decimal("7.00")
        )

    def get_json(self, url, params=None, status=200):
        response = self.client.get(url, params or {})
        self.assertEqual(response.status_code, status, response.content)
        return response.json()


class MovieApiTests(ApiTestData):
    url = reverse("movie-list")

    def test_list_returns_movies_with_genres(self):
        data = self.get_json(self.url)
        self.assertEqual(data["count"], 3)
        titles = [m["title"] for m in data["results"]]
        self.assertEqual(titles, ["Aurora", "Põhjatäht", "Vana film"])
        movie = data["results"][1]
        self.assertEqual(movie["genres"], [{"id": self.drama.id, "name": "Draama"}])
        self.assertNotIn("description", movie)

    def test_filters(self):
        cases = [
            ({"search": "täht"}, ["Põhjatäht"]),
            ({"genre": self.comedy.id}, ["Aurora"]),
            ({"featured": "true"}, ["Põhjatäht"]),
            ({"now_showing": "true"}, ["Aurora", "Põhjatäht"]),
        ]
        for params, expected in cases:
            with self.subTest(params=params):
                data = self.get_json(self.url, params)
                self.assertEqual([m["title"] for m in data["results"]], expected)

    def test_invalid_filters_return_400(self):
        for params in ({"genre": "draama"}, {"featured": "maybe"}):
            with self.subTest(params=params):
                data = self.get_json(self.url, params, status=400)
                self.assertIn(next(iter(params)), data)

    def test_detail_includes_description(self):
        data = self.get_json(reverse("movie-detail", args=[self.movie.id]))
        self.assertEqual(data["title"], "Põhjatäht")
        self.assertEqual(data["description"], "Film tähest.")
        self.assertEqual(data["age_rating"], "MS-12")

    def test_missing_movie_returns_404(self):
        self.get_json(reverse("movie-detail", args=[999999]), status=404)

    def test_list_query_count_does_not_grow_with_movies(self):
        with self.assertNumQueries(3):  # count, filmid, žanrid
            self.client.get(self.url)


class GenreAndCinemaApiTests(ApiTestData):
    def test_genres_are_sorted_by_name(self):
        data = self.get_json(reverse("genre-list"))
        self.assertEqual([g["name"] for g in data], ["Draama", "Komöödia"])

    def test_cinemas_include_halls(self):
        data = self.get_json(reverse("cinema-list"))
        self.assertEqual([c["name"] for c in data], ["Kino Laine", "Kino Täht"])
        self.assertEqual(data[1]["halls"], [{"id": self.hall.id, "name": "Saal 1", "screen_type": "2D", "capacity": 80}])

    def test_missing_cinema_returns_404(self):
        self.get_json(reverse("cinema-detail", args=[999999]), status=404)


class ScreeningApiTests(ApiTestData):
    url = reverse("screening-list")

    def test_list_contains_only_upcoming_screenings_in_order(self):
        data = self.get_json(self.url)
        self.assertEqual([s["id"] for s in data["results"]], [self.screening.id, self.later_screening.id])

    def test_screening_includes_movie_hall_and_cinema(self):
        screening = self.get_json(self.url)["results"][0]
        self.assertEqual(screening["movie"]["title"], "Põhjatäht")
        self.assertEqual(screening["hall"], {"id": self.hall.id, "name": "Saal 1", "screen_type": "2D"})
        self.assertEqual(screening["cinema"], {"id": self.cinema.id, "name": "Kino Täht", "city": "Tallinn"})
        self.assertEqual(screening["base_price"], "9.50")

    def test_filters(self):
        cases = [
            ({"movie": self.other_movie.id}, [self.later_screening.id]),
            ({"cinema": self.cinema.id}, [self.screening.id]),
            ({"date": self.tomorrow.isoformat()}, [self.screening.id]),
            ({"date": (self.tomorrow + timedelta(days=5)).isoformat()}, []),
        ]
        for params, expected in cases:
            with self.subTest(params=params):
                data = self.get_json(self.url, params)
                self.assertEqual([s["id"] for s in data["results"]], expected)

    def test_invalid_filters_return_400(self):
        for params in ({"date": "27.10.2026"}, {"movie": "x"}, {"cinema": "1.5"}):
            with self.subTest(params=params):
                self.get_json(self.url, params, status=400)

    def test_list_query_count_does_not_grow_with_screenings(self):
        with self.assertNumQueries(2):  # count, seansid koos filmi, saali ja kinoga
            self.client.get(self.url)

    def test_past_screening_can_still_be_retrieved(self):
        data = self.get_json(reverse("screening-detail", args=[self.past_screening.id]))
        self.assertEqual(data["movie"]["title"], "Vana film")


class ApiSafetyTests(ApiTestData):
    def test_no_user_booking_or_payment_endpoints(self):
        data = self.get_json(reverse("api-root"))
        self.assertEqual(set(data), {"movies", "genres", "cinemas", "screenings"})

    def test_anonymous_users_cannot_write(self):
        for url in (reverse("movie-list"), reverse("screening-list")):
            with self.subTest(url=url):
                self.assertEqual(self.client.post(url, {"title": "Uus"}).status_code, 403)
        self.assertEqual(self.client.delete(reverse("movie-detail", args=[self.movie.id])).status_code, 403)
        self.assertTrue(Movie.objects.filter(id=self.movie.id).exists())
