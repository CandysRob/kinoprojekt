#!/bin/sh
# pgbench scenarios for the cinema database (docs/testing/pgbench.md).
# Runs inside the docker-compose service "pgbench":
#
#   docker compose run --rm pgbench <scenario>
#
# Scenarios: createdb | check | explain | read | index | race | all
# Settings (docker compose run -e NAME=value): CLIENTS (50), THREADS (4),
# DURATION seconds per read test (30), RACE_TX purchase attempts per client (20),
# APP_MS simulated application time inside a booking transaction (1).
#
# Connection comes from PGHOST/PGUSER/PGPASSWORD/PGDATABASE (docker-compose.yml).
# Only ever point this at a local Docker database: "index" and "race" change
# the schema for a moment and "race" deletes the bookings of one screening.
set -eu

CLIENTS=${CLIENTS:-50}
THREADS=${THREADS:-4}
DURATION=${DURATION:-30}
RACE_TX=${RACE_TX:-20}
APP_MS=${APP_MS:-1}
BENCH=/bench
LOGS=/tmp/pgbench-logs
SUMMARY=/tmp/pgbench-summary.txt

q() { psql -X -v ON_ERROR_STOP=1 -Atq "$@"; }

header() { printf '\n=== %s\n' "$1"; }

# run_bench <label> <pgbench args...>
# Runs pgbench with a per-transaction log and adds one line to the summary:
# TPS, average latency, p95 latency and the number of failed transactions.
run_bench() {
    label=$1; shift
    rm -rf "$LOGS"; mkdir -p "$LOGS"
    out=$(pgbench -n -c "$CLIENTS" -j "$THREADS" -l --log-prefix="$LOGS/tx" "$@" 2>&1) || true
    printf '%s\n' "$out" | grep -E '^(transaction type|number of (clients|transactions|failed)|latency average|tps)' || true
    tps=$(printf '%s\n' "$out" | sed -n 's/^tps = \([0-9.]*\).*/\1/p' | awk '{printf "%.0f", $1}')
    avg=$(printf '%s\n' "$out" | sed -n 's/^latency average = \([0-9.]*\) ms/\1/p' | awk '{printf "%.2f", $1}')
    failed=$(printf '%s\n' "$out" | sed -n 's/^number of failed transactions: \([0-9]*\).*/\1/p')
    aborted=$(printf '%s\n' "$out" | grep -c 'aborted in command' || true)
    # Log line: client_id tx_no time_us script_no epoch epoch_us; time_us is the 3rd field
    p95=$(cat "$LOGS"/tx* 2>/dev/null | awk '$3 ~ /^[0-9]+$/ {print $3}' | sort -n |
        awk '{v[NR]=$1} END {if (NR) {i=int(NR*0.95); if (i<1) i=1; printf "%.2f", v[i]/1000}}')
    printf '%-36s %8s %10s %10s %7s %8s\n' "$label" "${tps:--}" "${avg:--}" "${p95:--}" "${failed:-0}" "$aborted" >>"$SUMMARY"
    printf '%s\n' "$out" | grep -m 3 'aborted in command' || true
}

summary_start() {
    printf '%-36s %8s %10s %10s %7s %8s\n' scenario tps 'avg ms' 'p95 ms' failed aborted >"$SUMMARY"
}

summary_print() {
    header "Summary (clients=$CLIENTS threads=$THREADS)"
    cat "$SUMMARY"
}

check() {
    header "Data size in database $PGDATABASE"
    q -F ' | ' -c "
        SELECT 'seansid', count(*) FROM seansid
        UNION ALL SELECT 'user', count(*) FROM \"user\"
        UNION ALL SELECT 'broneeringud', count(*) FROM broneeringud
        UNION ALL SELECT 'broneeritud_kohad', count(*) FROM broneeritud_kohad"
    n=$(q -c "SELECT count(*) FROM seansid")
    if [ "$n" -lt 5000 ]; then
        echo "Too little data for a load test ($n screenings). Run seed_load_data first (docs/testing/pgbench.md)." >&2
        exit 1
    fi
    q -c "ANALYZE"
}

# EXPLAIN ANALYZE for one day (day 5) with each schedule query
explain() {
    for f in schedule-date-cast schedule-date-range; do
        header "EXPLAIN ANALYZE $f.sql (day = 5)"
        sed -e '/^\\set/d' -e 's/:day/5/g' "$BENCH/$f.sql" | sed '1,/^SELECT/{/^SELECT/!d}' |
            { printf 'EXPLAIN (ANALYZE, BUFFERS, COSTS OFF)\n'; cat; } | q -f -
    done
}

read_tests() {
    header "Read scenarios: $CLIENTS clients, $DURATION s each"
    run_bench "upcoming (all future, no limit)" -T "$DURATION" -f "$BENCH/screenings-upcoming.sql"
    run_bench "one day, ::date cast (current)" -T "$DURATION" -f "$BENCH/schedule-date-cast.sql"
    run_bench "one day, time range (fix)" -T "$DURATION" -f "$BENCH/schedule-date-range.sql"
}

# Same definitions as migration 0002_search_and_sort_indexes
restore_indexes() {
    q -c "CREATE INDEX IF NOT EXISTS screening_starts_at_idx ON seansid (algus_aeg)" \
      -c "CREATE INDEX IF NOT EXISTS screening_movie_starts_idx ON seansid (filmi_id, algus_aeg)"
}

# Which index serves the one-day query: prints the scan line of the plan
plan_line() {
    sed -e '/^\\set/d' -e 's/:day/5/g' "$BENCH/schedule-date-range.sql" | sed '1,/^SELECT/{/^SELECT/!d}' |
        { printf 'EXPLAIN (COSTS OFF)\n'; cat; } | q -f - | grep 'on seansid' | sed 's/^ *-> */plan: /' || true
}

index_test() {
    header "Index test: schedule-date-range.sql with fewer and fewer indexes on seansid.algus_aeg"
    restore_indexes
    trap restore_indexes EXIT
    plan_line
    run_bench "range, both indexes" -T "$DURATION" -f "$BENCH/schedule-date-range.sql"
    q -c "DROP INDEX screening_starts_at_idx"
    plan_line
    run_bench "range, only (filmi_id, algus_aeg)" -T "$DURATION" -f "$BENCH/schedule-date-range.sql"
    q -c "DROP INDEX screening_movie_starts_idx"
    plan_line
    run_bench "range, NO index on algus_aeg" -T "$DURATION" -f "$BENCH/schedule-date-range.sql"
    restore_indexes
    trap - EXIT
    echo "Indexes restored."
}

restore_constraint() {
    q -c "DELETE FROM broneeritud_kohad WHERE seansi_id = $SCREENING" \
      -c "DELETE FROM broneeringud WHERE seansi_id = $SCREENING"
    q -c "ALTER TABLE broneeritud_kohad ADD CONSTRAINT unique_booked_seat_per_screening UNIQUE (seansi_id, istekoha_id)" 2>/dev/null || true
}

reset_screening() {
    q -c "DELETE FROM broneeritud_kohad WHERE seansi_id = $SCREENING" \
      -c "DELETE FROM broneeringud WHERE seansi_id = $SCREENING"
}

# Prints: tickets | distinct seats | seats sold more than once | bookings without a seat
race_result() {
    q -F ' | ' -c "
        SELECT (SELECT count(*) FROM broneeritud_kohad WHERE seansi_id = $SCREENING),
               (SELECT count(DISTINCT istekoha_id) FROM broneeritud_kohad WHERE seansi_id = $SCREENING),
               (SELECT count(*) FROM (SELECT istekoha_id FROM broneeritud_kohad WHERE seansi_id = $SCREENING
                                       GROUP BY istekoha_id HAVING count(*) > 1) d),
               (SELECT count(*) FROM broneeringud b WHERE b.seansi_id = $SCREENING
                  AND NOT EXISTS (SELECT 1 FROM broneeritud_kohad k WHERE k.broneeringu_id = b.id))"
}

race() {
    # Target: the last screening in the IMAX hall ("premiere night"), all its seats
    set -- $(q -F ' ' -c "
        SELECT s.id, s.alghind, min(i.id), max(i.id), count(i.id)
        FROM seansid s JOIN kinosaalid h ON h.id = s.saali_id JOIN istekohad i ON i.kinosaal_id = h.id
        WHERE h.\"ekraani_tüüp\" = 'IMAX'
        GROUP BY s.id ORDER BY s.algus_aeg DESC LIMIT 1")
    SCREENING=$1 PRICE=$2 SEAT_MIN=$3 SEAT_MAX=$4 SEATS=$5
    set -- $(q -F ' ' -c "SELECT min(id), max(id) FROM \"user\" WHERE \"user\" LIKE 'load_user_%'")
    USER_MIN=$1 USER_MAX=$2
    if [ $((SEAT_MAX - SEAT_MIN + 1)) -ne "$SEATS" ]; then
        echo "Seat ids of the IMAX hall are not consecutive, cannot pick a random seat." >&2
        exit 1
    fi
    vars="-D screening=$SCREENING -D price=$PRICE -D user_min=$USER_MIN -D user_max=$USER_MAX -D app_ms=$APP_MS"
    attempts=$((CLIENTS * RACE_TX))
    header "Booking race on screening $SCREENING (IMAX, $SEATS seats), $CLIENTS clients x $RACE_TX attempts = $attempts"

    trap restore_constraint EXIT

    echo "-- 1) $CLIENTS clients buy the SAME seat at once, plain INSERT (UNIQUE constraint ON)"
    # Not timed: 49 of 50 clients are supposed to fail, so TPS/latency mean nothing here
    reset_screening
    out=$(pgbench -n -c "$CLIENTS" -j "$THREADS" -t 1 -f "$BENCH/booking-same-seat.sql" \
        $vars -D seat_min="$SEAT_MIN" -D seat_max="$SEAT_MIN" 2>&1) || true
    printf '%s\n' "$out" | grep 'actually processed' || true
    rejected=$(printf '%s\n' "$out" | grep -c 'duplicate key value violates unique constraint' || true)
    echo "rejected by unique_booked_seat_per_screening: $rejected"
    echo "tickets | distinct seats | seats sold twice | empty bookings"
    race_result

    echo "-- 2) Premiere rush: random seats, ON CONFLICT DO NOTHING (UNIQUE constraint ON)"
    reset_screening
    run_bench "rush, constraint ON" -t "$RACE_TX" -f "$BENCH/booking-race.sql" \
        $vars -D seat_min="$SEAT_MIN" -D seat_max="$SEAT_MAX"
    echo "tickets | distinct seats | seats sold twice | empty bookings"
    race_result

    echo "-- 3) Same rush, check-then-insert, UNIQUE constraint DROPPED"
    reset_screening
    q -c "ALTER TABLE broneeritud_kohad DROP CONSTRAINT unique_booked_seat_per_screening"
    run_bench "rush, check-then-insert, NO constr." -t "$RACE_TX" -f "$BENCH/booking-race-naive.sql" \
        $vars -D seat_min="$SEAT_MIN" -D seat_max="$SEAT_MAX"
    echo "tickets | distinct seats | seats sold twice | empty bookings"
    race_result

    restore_constraint
    trap - EXIT
    echo "Test bookings deleted and unique_booked_seat_per_screening restored."
}

scenario=${1:-help}
case "$scenario" in
    createdb)
        createdb -h "$PGHOST" -U "$PGUSER" "$PGDATABASE" && echo "Database $PGDATABASE created." ;;
    check) check ;;
    explain) check; explain ;;
    read) check; summary_start; read_tests; summary_print ;;
    index) check; summary_start; index_test; summary_print ;;
    race) check; summary_start; race; summary_print ;;
    all) check; explain; summary_start; read_tests; index_test; race; summary_print ;;
    *)
        echo "Usage: docker compose run --rm pgbench {createdb|check|explain|read|index|race|all}"
        echo "Raw pgbench: docker compose run --rm --entrypoint pgbench pgbench --help"
        [ "$scenario" = help ] ;;
esac
