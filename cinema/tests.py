from datetime import timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import IntegrityError, connection, transaction
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import BookedSeat, Booking, Cinema, Hall, Movie, Review, Screening, Seat, User


class CinemaTestData(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="mari",
            email="mari@example.com",
            password="salajane-parool-123",
            first_name="Mari",
            last_name="Maasikas",
            phone_number="+372 5555 5555",
        )
        cls.cinema = Cinema.objects.create(
            name="Kino", street_address="Tänav 1", city="Tallinn", postal_code="01234", country="Eesti"
        )
        cls.hall = Hall.objects.create(cinema=cls.cinema, name="Saal 1", capacity=100)
        cls.seat = Seat.objects.create(hall=cls.hall, row="A", number=1)
        cls.movie = Movie.objects.create(title="Film", duration_minutes=120)
        start = timezone.now()
        cls.screening = Screening.objects.create(
            movie=cls.movie, hall=cls.hall, starts_at=start, ends_at=start + timedelta(hours=2), base_price=Decimal("8.50")
        )


class UserTests(CinemaTestData):
    def test_password_is_stored_as_hash_in_password_hash_column(self):
        with connection.cursor() as cursor:
            cursor.execute('select password_hash from "user" where id = %s', [self.user.pk])
            (stored,) = cursor.fetchone()
        self.assertNotIn("salajane-parool-123", stored)
        self.assertTrue(self.user.check_password("salajane-parool-123"))


class ConstraintTests(CinemaTestData):
    def test_seat_is_unique_in_hall(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Seat.objects.create(hall=self.hall, row="A", number=1)

    def test_seat_can_be_booked_once_per_screening(self):
        booking = Booking.objects.create(user=self.user, screening=self.screening, total=Decimal("17.00"))
        BookedSeat.objects.create(booking=booking, screening=self.screening, seat=self.seat, price=Decimal("8.50"))
        with self.assertRaises(IntegrityError), transaction.atomic():
            BookedSeat.objects.create(booking=booking, screening=self.screening, seat=self.seat, price=Decimal("8.50"))

    def test_double_booking_fails_validation(self):
        booking = Booking.objects.create(user=self.user, screening=self.screening, total=Decimal("8.50"))
        BookedSeat.objects.create(booking=booking, screening=self.screening, seat=self.seat, price=Decimal("8.50"))
        duplicate = BookedSeat(booking=booking, screening=self.screening, seat=self.seat, price=Decimal("8.50"))
        with self.assertRaisesMessage(ValidationError, "See koht on sellel seansil juba broneeritud."):
            duplicate.full_clean()

    def test_screening_must_end_after_start(self):
        start = timezone.now()
        with self.assertRaises(IntegrityError), transaction.atomic():
            Screening.objects.create(
                movie=self.movie, hall=self.hall, starts_at=start, ends_at=start, base_price=Decimal("8.50")
            )

    def test_review_rating_must_be_between_1_and_5(self):
        for rating in (0, 6):
            with self.subTest(rating=rating), self.assertRaises(IntegrityError), transaction.atomic():
                Review.objects.create(user=self.user, movie=self.movie, rating=rating)

    def test_review_rating_can_be_empty(self):
        review = Review(user=self.user, movie=self.movie, rating=None)
        review.full_clean()
        review.save()

    def test_database_defaults_are_set(self):
        booking = Booking.objects.create(user=self.user, screening=self.screening, total=Decimal("8.50"))
        booking.refresh_from_db()
        self.assertEqual(booking.status, "ootel")
        self.assertIsNotNone(booking.created_at)
        self.assertEqual(self.hall.screen_type, "2D")


class HealthTests(TestCase):
    def test_health_reports_database_ok(self):
        response = self.client.get(reverse("health"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok", "database": "ok"})


class AdminTests(CinemaTestData):
    def test_admin_pages_load(self):
        admin = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="admin-parool-123",
            first_name="Admin",
            last_name="Kasutaja",
            phone_number="+372 5000 0000",
        )
        self.client.force_login(admin)
        for name in ("user", "cinema", "hall", "seat", "movie", "genre", "screening", "booking", "payment", "review", "news"):
            for page in ("changelist", "add"):
                url = reverse(f"admin:cinema_{name}_{page}")
                with self.subTest(url=url):
                    self.assertEqual(self.client.get(url).status_code, 200)
        url = reverse("admin:cinema_user_change", args=[self.user.pk])
        self.assertEqual(self.client.get(url).status_code, 200)
