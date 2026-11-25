-- Constraint test: every client tries to buy THE SAME seat once (-t 1).
-- A plain INSERT, no ON CONFLICT: the UNIQUE constraint
-- unique_booked_seat_per_screening must let exactly one through. The others
-- get "duplicate key value violates unique constraint" and pgbench reports
-- that client as aborted (this is expected, see run.sh).
\set user random(:user_min, :user_max)
BEGIN;
INSERT INTO broneeringud (kasutaja_id, seansi_id, staatus, kogusumma, loodud)
VALUES (:user, :screening, 'ootel', :price, now())
RETURNING id AS booking_id \gset
INSERT INTO broneeritud_kohad (broneeringu_id, seansi_id, istekoha_id, hind)
VALUES (:booking_id, :screening, :seat_min, :price);
COMMIT;
