-- The "check first, then insert" way of booking, without trusting the
-- database constraint. run.sh runs it only after DROPPING the UNIQUE
-- constraint to show what the constraint protects against.
--   1. is the seat free? (SELECT)
--   2. (app_ms) the application does its own work,
--   3. insert booking + seat.
-- Two users can both see "free" in step 1 and both insert in step 3.
\set seat random(:seat_min, :seat_max)
\set user random(:user_min, :user_max)
BEGIN;
SELECT count(*) AS taken FROM broneeritud_kohad WHERE seansi_id = :screening AND istekoha_id = :seat \gset
\if :taken
ROLLBACK;
\else
\sleep :app_ms ms
INSERT INTO broneeringud (kasutaja_id, seansi_id, staatus, kogusumma, loodud)
VALUES (:user, :screening, 'ootel', :price, now())
RETURNING id AS booking_id \gset
INSERT INTO broneeritud_kohad (broneeringu_id, seansi_id, istekoha_id, hind)
VALUES (:booking_id, :screening, :seat, :price);
COMMIT;
\endif
