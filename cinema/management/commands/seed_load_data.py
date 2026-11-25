"""
Load-test data: thousands of screenings, users, bookings and booked seats.

The pgbench scenarios in `bench/` need much more data than `seed_dev_data`
creates (see docs/testing/pgbench.md). Run this against a separate database,
not the development one:

    docker compose run --rm -e POSTGRES_DB=kinoprojekt_bench backend \
        uv run python manage.py seed_load_data

Steps:
1. `seed_dev_data --days N` creates movies, cinemas, halls, seats and the
   screenings (about 35 per day, so the default 300 days gives ~10 000).
2. Users `load_user_00001` ... are added (they cannot log in).
3. Every screening that has no bookings yet gets bookings of 1-4 adjacent
   seats. Evening and weekend screenings sell more seats.

All data is made up and the result is the same on every run with the same
`--seed`. Running the command again does not duplicate anything.
"""

import random
from collections import defaultdict
from datetime import timedelta

from django.contrib.auth.hashers import make_password
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Exists, OuterRef
from django.utils import timezone

from cinema.models import BookedSeat, Booking, Screening, Seat, User

USERNAME_PREFIX = "load_user_"
GROUP_SIZES = (1, 2, 2, 2, 3, 4)  # most people come in pairs
BATCH_SIZE = 5000


class Command(BaseCommand):
    help = "Creates load-test data: screenings for many days, users, bookings and booked seats (repeatable)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--days", type=int, default=300, help="Days of screenings from today (default 300, about 10 000 screenings)."
        )
        parser.add_argument("--users", type=int, default=2000, help="Number of load-test users (default 2000).")
        parser.add_argument("--seed", type=int, default=2026, help="Random seed, the same seed gives the same data.")

    def handle(self, *args, days, users, seed, **options):
        if days < 1 or users < 1:
            raise CommandError("--days and --users must be at least 1.")

        call_command("seed_dev_data", days=days, stdout=self.stdout)

        with transaction.atomic():
            user_ids = self.create_users(users)
            bookings, tickets = self.create_bookings(user_ids, seed)

        self.stdout.write(
            self.style.SUCCESS(
                f"Load data ready: {Screening.objects.count()} screenings, {len(user_ids)} load users, "
                f"{Booking.objects.count()} bookings, {BookedSeat.objects.count()} booked seats "
                f"({bookings} bookings and {tickets} seats added now)."
            )
        )

    def create_users(self, count):
        usernames = [f"{USERNAME_PREFIX}{number:05}" for number in range(1, count + 1)]
        existing = set(User.objects.filter(username__in=usernames).values_list("username", flat=True))
        unusable_password = make_password(None)  # same as set_unusable_password()
        User.objects.bulk_create(
            [
                User(
                    username=username,
                    email=f"{username}@example.com",
                    first_name="Load",
                    last_name=f"User {username[len(USERNAME_PREFIX):]}",
                    phone_number="+372 5000 0000",
                    password=unusable_password,
                )
                for username in usernames
                if username not in existing
            ],
            batch_size=BATCH_SIZE,
        )
        return list(User.objects.filter(username__in=usernames).order_by("id").values_list("id", flat=True))

    def create_bookings(self, user_ids, seed):
        # Seats of every hall grouped by row, in seat number order
        rows_by_hall = defaultdict(lambda: defaultdict(list))
        for seat in Seat.objects.order_by("hall_id", "row", "number"):
            rows_by_hall[seat.hall_id][seat.row].append(seat)

        unbooked = Screening.objects.filter(~Exists(Booking.objects.filter(screening=OuterRef("pk"))))
        now = timezone.now()
        bookings = []
        seats_per_booking = []
        for screening in unbooked.select_related("hall").order_by("id"):
            rng = random.Random(f"{seed}/{screening.pk}")  # each screening on its own: repeatable and independent
            rows = rows_by_hall[screening.hall_id]
            wanted = self.tickets_to_sell(screening, rng)
            for group in self.pick_seat_groups(rows, wanted, rng):
                bookings.append(
                    Booking(
                        user_id=rng.choice(user_ids),
                        screening=screening,
                        status="kinnitatud" if rng.random() < 0.9 else "ootel",
                        total=screening.base_price * len(group),
                        created_at=now - timedelta(minutes=rng.randint(1, 14 * 24 * 60)),
                    )
                )
                seats_per_booking.append(group)

        Booking.objects.bulk_create(bookings, batch_size=BATCH_SIZE)  # PostgreSQL returns the new ids
        tickets = [
            BookedSeat(booking=booking, screening_id=booking.screening_id, seat=seat, price=booking.screening.base_price)
            for booking, group in zip(bookings, seats_per_booking)
            for seat in group
        ]
        BookedSeat.objects.bulk_create(tickets, batch_size=BATCH_SIZE)
        return len(bookings), len(tickets)

    @staticmethod
    def tickets_to_sell(screening, rng):
        """How many seats are sold: a small share by day, more in the evening and at weekends."""
        local = timezone.localtime(screening.starts_at)
        share = 0.02
        if local.hour >= 18:
            share += 0.05
        if local.weekday() >= 5:
            share += 0.03
        return round(screening.hall.capacity * share * rng.uniform(0.2, 1.8))

    @staticmethod
    def pick_seat_groups(rows, wanted, rng):
        """Splits `wanted` seats into groups of adjacent free seats in one row."""
        free = {row: list(seats) for row, seats in rows.items()}
        groups = []
        while wanted > 0:
            size = min(rng.choice(GROUP_SIZES), wanted)
            row_names = list(free)
            rng.shuffle(row_names)
            for row in row_names:
                seats = free[row]
                starts = [
                    i for i in range(len(seats) - size + 1) if seats[i + size - 1].number - seats[i].number == size - 1
                ]
                if starts:
                    i = rng.choice(starts)
                    groups.append(seats[i:i + size])
                    free[row] = seats[:i] + seats[i + size:]
                    break
            else:
                break  # no row has `size` adjacent free seats left
            wanted -= size
        return groups
