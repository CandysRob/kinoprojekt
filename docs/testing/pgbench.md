# pgbench: load testing the cinema database

Author: Gerry · Branch: `test/pgbench-german`

## What pgbench is and what it measures

[pgbench](https://www.postgresql.org/docs/16/pgbench.html) is the benchmarking tool that ships with
PostgreSQL. It opens many database connections at once (clients), runs an SQL script in a loop
on each of them, and reports:

- **TPS**: transactions (script runs) per second across all clients;
- **latency**: how long one transaction takes. pgbench prints the average. `bench/run.sh` also
  computes the **p95** from pgbench's per-transaction log, meaning 95% of transactions were faster than this;
- **failed / aborted** transactions, e.g. a client that hit a constraint error.

The scripts can be any SQL plus a few meta commands (`\set` random variables, `\gset` to save a
result, `\if`, `\sleep`). That makes it possible to replay the exact queries our Django code sends
and to simulate many people booking seats at the same moment.

pgbench works **at the database level**: it measures PostgreSQL, not Django, serialization or
HTTP. An API-level tool (k6, Locust) would measure the full request; that is a different
tool for the other team member.

## Safety

Run this only against the **local Docker database**. The `index` and `race` scenarios drop an
index or a constraint for a moment and delete test bookings. Everything runs in a separate
database `kinoprojekt_bench`, so the development data in `kinoprojekt` is not touched.

## Installation

Nothing to install besides Docker Desktop. pgbench comes in the official `postgres:16` image,
which is the same image as our `db` service. `docker-compose.yml` has a service `pgbench` for it:

```yaml
pgbench:
  image: postgres:16
  profiles: ["bench"]          # does not start with "docker compose up"
  entrypoint: ["sh", "/bench/run.sh"]
  environment:
    PGHOST: db
    PGDATABASE: ${BENCH_DB:-kinoprojekt_bench}
    # PGUSER / PGPASSWORD from .env
  volumes:
    - ./bench:/bench:ro
```

## Running

Commands work in bash and PowerShell, from the repository root. A `.env` file is needed
(see README).

```bash
# 1. Database (and Redis, which the backend container expects)
docker compose up -d db redis

# 2. Separate database for the load test, tables and data (once, ~30 s)
docker compose run --rm pgbench createdb
docker compose run --rm -e POSTGRES_DB=kinoprojekt_bench backend uv run python manage.py migrate
docker compose run --rm -e POSTGRES_DB=kinoprojekt_bench backend uv run python manage.py seed_load_data

# 3. All scenarios (~4 minutes), summary table at the end
docker compose run --rm pgbench all
```

Single scenarios: `check`, `explain`, `read`, `index`, `race`. Settings are environment variables:

```bash
docker compose run --rm -e CLIENTS=100 -e DURATION=60 pgbench read
docker compose run --rm -e APP_MS=20 pgbench race
```

| Variable | Default | Meaning |
| --- | --- | --- |
| `CLIENTS` | 50 | simultaneous connections (users) |
| `THREADS` | 4 | pgbench worker threads |
| `DURATION` | 30 | seconds per read test |
| `RACE_TX` | 20 | purchase attempts per client in the race tests |
| `APP_MS` | 1 | simulated application time inside a booking transaction |

pgbench itself, without the runner:

```bash
docker compose run --rm --entrypoint pgbench pgbench -n -c 10 -j 2 -T 10 -f /bench/schedule-date-range.sql
```

Removing the test database:

```bash
docker compose exec db sh -c 'dropdb -U "$POSTGRES_USER" kinoprojekt_bench'
```

## Test data

`seed_dev_data` makes ~500 screenings and no bookings, which is too little for a load test. The new
command `seed_load_data` (`cinema/management/commands/seed_load_data.py`, tests in
`cinema/test_load_seed.py`) builds on it:

| Table | Rows |
| --- | --- |
| `seansid` (screenings, 300 days × 7 halls) | 10 504 |
| `user` (`load_user_00001` …, cannot log in) | 2 000 |
| `broneeringud` (bookings) | 30 946 |
| `broneeritud_kohad` (booked seats / tickets) | 62 710 |

Bookings are 1–4 adjacent seats in one row. Evening and weekend screenings sell more. The data is
the same on every run (`--seed`), and running the command again adds nothing. Options:
`--days`, `--users`, `--seed`. The `race` scenario deletes the bookings of one screening, so
afterwards the counts are a few rows lower. Running `seed_load_data` again refills that screening.

## Scenarios

All scripts are in `bench/`.

| Script | What it is in the app | Question |
| --- | --- | --- |
| `screenings-upcoming.sql` | `GET /api/screenings/` on a cache miss: all future screenings with movie, hall and cinema (exact SQL from the Django ORM) | How expensive is the unlimited list? |
| `schedule-date-cast.sql` | `?date=2026-11-28` filter from branch `feature/kuupaeva-filter`: Django `starts_at__date=day` becomes `(algus_aeg AT TIME ZONE 'Europe/Tallinn')::date = day` | Can the index on `algus_aeg` be used? |
| `schedule-date-range.sql` | The same day written as `algus_aeg >= day 00:00 AND algus_aeg < next day 00:00` | Is the range faster? |
| `index` scenario | `schedule-date-range.sql` with both indexes, only `(filmi_id, algus_aeg)`, and no index on `algus_aeg` | What do the indexes from the index task give? |
| `booking-same-seat.sql` | 50 users click "buy" on **the same seat** at the same moment (plain `INSERT`) | Does the unique constraint let exactly one through? |
| `booking-race.sql` | Premiere rush: 50 users × 20 attempts on random seats of one IMAX screening (280 seats). Booking + seat in one transaction, seat with `ON CONFLICT DO NOTHING`, `ROLLBACK` if the seat was taken | Throughput and correctness with the constraint |
| `booking-race-naive.sql` | Same rush, but "check if free, then insert", with the unique constraint **dropped** | What happens without the constraint? |

The read tests choose a random day out of the next 30 days for every transaction.

## Results

Environment: Windows 11, Docker Desktop 29.9 (12 vCPU, 7.7 GiB for Docker), PostgreSQL 16.15
(`postgres:16`, default settings: `shared_buffers` 128 MB, `max_connections` 100), pgbench 16.15
in its own container on the same Docker network. 50 clients, 4 threads, 30 s per read test.
Measured 25.11.2026, output of `docker compose run --rm pgbench all`:

```text
scenario                                  tps     avg ms     p95 ms  failed  aborted
upcoming (all future, no limit)           169     295.37     546.40       0        0
one day, ::date cast (current)           1084      46.14      94.90       0        0
one day, time range (fix)               10529       4.75      13.11       0        0
range, both indexes                     10332       4.84      13.50       0        0
range, only (filmi_id, algus_aeg)       10778       4.64      12.45       0        0
range, NO index on algus_aeg              681      73.38     135.99       0        0
rush, constraint ON                      5030       9.94      26.43       0        0
rush, check-then-insert, NO constr.      5941       8.42      22.67       0        0
```

Booking correctness (counted from the database after each race):

| Test | Attempts | Tickets sold | Different seats | Seats sold more than once | Empty bookings left |
| --- | --- | --- | --- | --- | --- |
| Same seat × 50, constraint ON | 50 | **1** (49 rejected: `duplicate key value violates unique constraint "unique_booked_seat_per_screening"`) | 1 | 0 | 0 |
| Rush, constraint ON | 1 000 | 277 | 277 | **0** | 0 |
| Rush, check-then-insert, NO constraint | 1 000 | 340 | 275 | **53** | 0 |

An earlier full run on the same data gave the same picture (e.g. cast 1 161 TPS, range 10 577 TPS,
no index 657 TPS, 68 double-sold seats without the constraint), and a third `race` run gave 64
double-sold seats. The 30-second read tests varied by up to ±10% between runs. The 1 000-transaction
race tests take only ~0.2 s, so their TPS varies more. pgbench, the database and the other Docker
containers all share one machine.

EXPLAIN ANALYZE for one day (`docker compose run --rm pgbench explain`, shortened):

```text
schedule-date-cast.sql
  ->  Seq Scan on seansid (actual time=0.073..6.368 rows=35 loops=1)
        Filter: ((algus_aeg >= now()) AND (((algus_aeg AT TIME ZONE 'Europe/Tallinn'))::date = ...))
        Rows Removed by Filter: 10469
        Buffers: shared hit=123
Execution Time: 6.721 ms

schedule-date-range.sql
  ->  Index Scan using screening_starts_at_idx on seansid (actual time=0.019..0.025 rows=35 loops=1)
        Index Cond: ((algus_aeg >= now()) AND (algus_aeg >= ...) AND (algus_aeg < ...))
        Buffers: shared hit=3
Execution Time: 0.224 ms
```

## Conclusions

### 1. The `?date=` filter cannot use the index (about 10× slower). Fix: filter by a time range

`starts_at__date=day` wraps the column in `AT TIME ZONE ...::date`. A B-tree index on
`algus_aeg` stores the raw timestamps, so PostgreSQL cannot search it for a computed date. It reads
all 10 504 screenings, converts each one and throws away 10 469 (123 pages instead of 3).
Under load this is the difference between **1 084 TPS / p95 95 ms** (before) and
**10 529 TPS / p95 13 ms** (after, same result rows). The gap grows with every new day of screenings.

Fix for `ScreeningViewSet` / `MovieViewSet` in `feature/kuupaeva-filter`:

```python
from datetime import datetime, time, timedelta
from django.utils import timezone

day_start = timezone.make_aware(datetime.combine(selected_date, time.min))  # 00:00 Estonian time
queryset = queryset.filter(starts_at__gte=day_start, starts_at__lt=day_start + timedelta(days=1))
```

The alternative would be an expression index on `(algus_aeg AT TIME ZONE 'Europe/Tallinn')::date`.
The range is simpler, uses the index we already have and handles daylight saving time correctly.

### 2. The indexes from the index task work: about 15× under load

With no index on `algus_aeg`, the one-day query drops from **10 332 to 681 TPS** and p95 rises
from **13.5 to 136 ms**. `screening_movie_starts_idx (filmi_id, algus_aeg)` alone was enough here,
because there are only 12 movies: PostgreSQL did 12 small index lookups. That only works with
few movies, so `screening_starts_at_idx` should stay. With hundreds of movies the composite index
would not save this query.

### 3. `GET /api/screenings/` has no limit: 169 TPS, p95 0.55 s on a cache miss

The endpoint returns **every** future screening, which is 10 504 rows with joins in this data set.
With 50 clients asking at once, each query takes ~0.3 s in PostgreSQL alone, before Django even
serializes 10 000 objects.
The 1-minute cache hides this most of the time. But `cinema/signals.py` clears the whole cache when
any movie or screening is saved, so misses come exactly when the schedule is being edited. What
would help: pagination or a default date range (e.g. today + 7 days) on the list, using the range
filter from conclusion 1.

### 4. The unique constraint is what stops double booking

- 50 simultaneous purchases of the same seat: **exactly 1 succeeded**, 49 were rejected by
  `unique_booked_seat_per_screening`.
- Premiere rush with the constraint: 277 tickets for 277 different seats. **0 seats sold twice**, and
  no empty bookings were left (the transaction rolls back when the seat is taken).
- The same rush with "check if the seat is free, then insert" and **no constraint**: 340 tickets
  for 275 seats, so **53 seats were sold more than once** (65 extra tickets). With 1 ms of
  application time between the check and the insert, two users often both see the seat as free.
- Speed is not a reason to skip the constraint. Across three runs the safe version was 0–15% slower
  (5 545 vs 6 063, 5 030 vs 5 941 and 5 846 vs 5 815 TPS). One race takes only ~0.2 s, so that
  spread is mostly noise. A second buyer of the same seat does wait for the first one's
  transaction to end, but the double sales showed up in every run (53, 64 and 68 seats).

For the booking feature (task 7 in `docs/TEAM_WORK_PLAN.md`): create the booking and its seats
in one `transaction.atomic()` block. Rely on the constraint and catch `IntegrityError` (or
`INSERT ... ON CONFLICT DO NOTHING`) and tell the user "seat already taken". A `.exists()`
check before saving is not enough on its own.

## Files

| File | Purpose |
| --- | --- |
| `docker-compose.yml` → service `pgbench` | pgbench in Docker, one command per scenario |
| `bench/run.sh` | runner: scenarios, summary table, p95, index/constraint restore |
| `bench/*.sql` | pgbench scripts (described above) |
| `cinema/management/commands/seed_load_data.py` | large data set for the load test |
| `cinema/test_load_seed.py` | tests for the seeder |
| `.gitattributes` | keeps LF line endings in `bench/` so the scripts run in Linux on Windows checkouts |
