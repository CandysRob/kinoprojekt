from datetime import timedelta
from decimal import Decimal

from django.core.cache import cache
from django.urls import reverse
from django.utils import timezone

from .models import Genre, Movie, Screening
from .test_api import ApiTestData


class ApiCacheTests(ApiTestData):
    def setUp(self):
        cache.clear()

    def test_second_request_comes_from_cache_without_queries(self):
        first = self.client.get(reverse("movie-list")).json()
        with self.assertNumQueries(0):
            second = self.client.get(reverse("movie-list")).json()
        self.assertEqual(first, second)

    def test_new_movie_clears_movie_list(self):
        self.client.get(reverse("movie-list"))
        Movie.objects.create(title="Uus film", duration_minutes=90)
        titles = [m["title"] for m in self.client.get(reverse("movie-list")).json()]
        self.assertIn("Uus film", titles)

    def test_adding_genre_to_movie_clears_movie_list(self):
        comedy = Genre.objects.create(name="Komöödia")
        self.client.get(reverse("movie-list"))
        self.other_movie.genres.add(comedy)  # saadab ainult m2m_changed signaali
        data = self.client.get(reverse("movie-list")).json()
        aurora = next(m for m in data if m["title"] == "Aurora")
        self.assertEqual([g["name"] for g in aurora["genres"]], ["Komöödia"])

    def test_new_screening_clears_screening_lists(self):
        self.client.get(reverse("screening-list"))
        self.client.get(reverse("screening-list"), {"movie": self.movie.id})
        starts_at = timezone.now() + timedelta(days=3)
        new = Screening.objects.create(
            movie=self.movie, hall=self.hall, starts_at=starts_at, ends_at=starts_at + timedelta(hours=2), base_price=Decimal("9.50")
        )
        all_ids = [s["id"] for s in self.client.get(reverse("screening-list")).json()]
        movie_ids = [s["id"] for s in self.client.get(reverse("screening-list"), {"movie": self.movie.id}).json()]
        self.assertIn(new.id, all_ids)
        self.assertIn(new.id, movie_ids)

    def test_each_movie_filter_is_cached_separately(self):
        all_screenings = self.client.get(reverse("screening-list")).json()
        one_movie = self.client.get(reverse("screening-list"), {"movie": self.other_movie.id}).json()
        self.assertEqual(len(all_screenings), 2)
        self.assertEqual([s["id"] for s in one_movie], [self.later_screening.id])

    def test_renamed_hall_shows_in_screenings(self):
        self.client.get(reverse("screening-list"))
        self.hall.name = "Suur saal"
        self.hall.save()
        data = self.client.get(reverse("screening-list")).json()
        self.assertEqual(data[0]["hall"]["name"], "Suur saal")

    def test_invalid_movie_filter_still_returns_400(self):
        response = self.client.get(reverse("screening-list"), {"movie": "abc"})
        self.assertEqual(response.status_code, 400)
