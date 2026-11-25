from io import StringIO

from django.core.management import call_command
from django.db.models import Count, F, Sum
from django.test import TestCase

from .models import BookedSeat, Booking, Screening, User


class SeedLoadDataTests(TestCase):
    def seed(self, days=2, users=30):
        call_command("seed_load_data", days=days, users=users, stdout=StringIO())
        return {model.__name__: model.objects.count() for model in (Screening, User, Booking, BookedSeat)}

    def test_creates_users_bookings_and_booked_seats(self):
        counts = self.seed()
        self.assertEqual(counts["User"], 30)
        self.assertGreater(counts["Booking"], 0)
        self.assertGreater(counts["BookedSeat"], counts["Booking"] // 2)

    def test_is_repeatable(self):
        first = self.seed()
        self.assertEqual(self.seed(), first)

    def test_more_days_books_only_the_new_screenings(self):
        first = self.seed(days=2)
        booked_before = set(Booking.objects.values_list("id", flat=True))
        second = self.seed(days=3)
        self.assertGreater(second["BookedSeat"], first["BookedSeat"])
        new = Booking.objects.exclude(id__in=booked_before)
        self.assertFalse(new.filter(screening__in=Booking.objects.filter(id__in=booked_before).values("screening")).exists())

    def test_booked_seats_match_booking_screening_and_hall(self):
        self.seed()
        self.assertFalse(BookedSeat.objects.exclude(screening=F("booking__screening")).exists())
        self.assertFalse(BookedSeat.objects.exclude(seat__hall=F("screening__hall")).exists())

    def test_no_seat_is_sold_twice_and_totals_add_up(self):
        self.seed()
        duplicates = BookedSeat.objects.values("screening", "seat").annotate(n=Count("id")).filter(n__gt=1)
        self.assertFalse(duplicates.exists())
        for booking in Booking.objects.annotate(seat_sum=Sum("seats__price")):
            self.assertEqual(booking.total, booking.seat_sum)
