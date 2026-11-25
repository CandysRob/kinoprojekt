-- Premiere rush: many users buy seats for the same screening at once.
-- Variables come from run.sh (-D): screening, price, seat_min, seat_max,
-- user_min, user_max, app_ms.
--
-- One transaction = one purchase attempt of one random seat:
--   1. create the booking,
--   2. (app_ms) the application does its own work, locks are held,
--   3. add the seat. ON CONFLICT relies on the UNIQUE constraint
--      unique_booked_seat_per_screening (seansi_id, istekoha_id): if another
--      user already has the seat, nothing is inserted and won = 0,
--   4. COMMIT if the seat was ours, otherwise ROLLBACK (no empty booking stays).
\set seat random(:seat_min, :seat_max)
\set user random(:user_min, :user_max)
BEGIN;
INSERT INTO broneeringud (kasutaja_id, seansi_id, staatus, kogusumma, loodud)
VALUES (:user, :screening, 'ootel', :price, now())
RETURNING id AS booking_id \gset
\sleep :app_ms ms
WITH ins AS (
    INSERT INTO broneeritud_kohad (broneeringu_id, seansi_id, istekoha_id, hind)
    VALUES (:booking_id, :screening, :seat, :price)
    ON CONFLICT (seansi_id, istekoha_id) DO NOTHING
    RETURNING 1
)
SELECT count(*) AS won FROM ins \gset
\if :won
COMMIT;
\else
ROLLBACK;
\endif
