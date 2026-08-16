-- ============================================================
-- SEED: sample company data (customers, orders, payments)
-- Run AFTER schema.sql
--
-- Instead of typing ~850 rows by hand, we GENERATE them using
-- generate_series + random() + ARRAYs.
-- setseed() makes the data identical on every run.
-- ============================================================

-- 1) CLEAN SLATE: wipe all rows and reset the id counters,
--    so re-running this file always starts fresh.
TRUNCATE payments, orders, customers RESTART IDENTITY;

-- 2) FREEZE THE RANDOMNESS: every run now produces the same data.
SELECT setseed(0.42);

-- 3) CUSTOMERS: 50 rows
--    FROM generate_series(1,50) acts as a mini-loop: it makes 50
--    rows, numbered 1..50, which we call "n".
--    The CTE "lists" holds our arrays of names/cities so we can
--    index into them. city at odd index + country at even index
--    = always a matching pair (New York comes with USA).
WITH lists AS (
    SELECT
        ARRAY['Olivia','Liam','Ava','Noah','Emma','Lucas','Mia','Ethan','Sofia','Mason',
              'Isabella','Aiden','Amelia','Carter','Harper','Elijah','Ella','James','Grace','Benjamin'] AS first_names,
        ARRAY['Smith','Johnson','Williams','Brown','Jones','Garcia','Miller','Davis','Rodriguez','Martinez',
              'Wilson','Anderson','Taylor','Thomas','Moore','Jackson','Martin','Lee','Perez','Thompson'] AS last_names,
        ARRAY['New York','USA','London','UK','Berlin','Germany','Tokyo','Japan','Toronto','Canada',
              'Sydney','Australia','Paris','France','Mumbai','India','Sao Paulo','Brazil','Dubai','UAE'] AS city_country
)
INSERT INTO customers (name, email, city, country, signup_date)
SELECT
    first_names[1 + floor(random() * 20)::int]
        || ' ' ||
        last_names[1 + floor(random() * 20)::int]   AS name,
    'customer' || n || '@example.com'               AS email,
    city_country[1 + 2 * place.i]                   AS city,
    city_country[2 + 2 * place.i]                   AS country,
    CURRENT_DATE - (random() * 365)::int            AS signup_date
FROM generate_series(1, 50) AS n,
     -- LATERAL: one roll per customer, reused by BOTH city and
     -- country so pairs always match (New York comes with USA).
     -- Trick: we ADD n so the subquery DEPENDS on the row ->
     -- PostgreSQL can't evaluate it once and share it (it did,
     -- and made everyone live in Mumbai!).
     LATERAL (SELECT (floor(random() * 10)::int + n) % 10 AS i) AS place,
     lists;

-- 4) ORDERS: 400 rows (random customer, random amount, random status)
--    Status trick: the same status repeated in the array makes it
--    MORE likely to be chosen. Delivered appears 4x -> the most
--    common status, cancelled 1x -> the rarest.
INSERT INTO orders (customer_id, order_date, status, total_amount)
SELECT
    1 + floor(random() * 50)::int                   AS customer_id,
    CURRENT_DATE - (random() * 365)::int            AS order_date,
    (ARRAY['pending','shipped','shipped','delivered','delivered','delivered','delivered','cancelled'])
        [1 + floor(random() * 8)::int]              AS status,
    round((10 + random() * 490)::numeric, 2)        AS total_amount
FROM generate_series(1, 400);

-- 5) PAYMENTS: one payment per NON-cancelled order
--    We don't type customer_id/amount by hand here - we SELECT
--    them straight from the orders table. The WHERE skips
--    cancelled orders (a cancelled order shouldn't have payments,
--    otherwise "total revenue" queries would be wrong).
--    o.order_date + N shifts a date forward by N days.
INSERT INTO payments (order_id, amount, payment_date, method)
SELECT
    o.id,
    o.total_amount,
    o.order_date + (1 + floor(random() * 5)::int)   AS payment_date,
    (ARRAY['credit_card','credit_card','paypal','bank_transfer','cash'])
        [1 + floor(random() * 5)::int]              AS method
FROM orders AS o
WHERE o.status <> 'cancelled';