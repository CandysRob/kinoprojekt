from io import StringIO

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from .models import BookedSeat, Booking, Cinema, Genre, Hall, Movie, MovieGenre, Payment, Screening, Seat, User


class SeedDevDataTests(TestCase):
    models = [Genre, Movie, MovieGenre, Cinema, Hall, Seat, Screening]

    def seed(self, days=3):
        call_command("seed_dev_data", days=days, stdout=StringIO())
        return {model.__name__: model.objects.count() for model in self.models}

    def test_creates_data_and_is_repeatable(self):
        first = self.seed()
        self.assertTrue(all(first.values()), first)
        self.assertEqual(self.seed(), first)

    def test_more_days_only_adds_new_screenings(self):
        first = self.seed(days=2)
        second = self.seed(days=3)
        self.assertGreater(second["Screening"], first["Screening"])
        self.assertEqual({k: v for k, v in second.items() if k != "Screening"}, {k: v for k, v in first.items() if k != "Screening"})

    def test_screenings_do_not_overlap_in_a_hall(self):
        self.seed()
        for hall in Hall.objects.all():
            screenings = list(hall.screenings.order_by("starts_at"))
            for previous, current in zip(screenings, screenings[1:]):
                self.assertLessEqual(previous.ends_at, current.starts_at, f"{hall}: {previous} / {current}")

    def test_screenings_only_for_released_movies(self):
        self.seed()
        for screening in Screening.objects.select_related("movie"):
            self.assertLessEqual(screening.movie.release_date, timezone.localdate(screening.starts_at))

    def test_hall_capacity_matches_seats(self):
        self.seed()
        for hall in Hall.objects.all():
            self.assertEqual(hall.capacity, hall.seats.count())

    def test_does_not_create_users_bookings_or_payments(self):
        self.seed()
        for model in (User, Booking, BookedSeat, Payment):
            self.assertEqual(model.objects.count(), 0, model.__name__)
