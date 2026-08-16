-- ============================================================
-- SCHEMA: company database for the Text-to-SQL project
-- 3 tables: customers -> orders -> payments
-- Run this FIRST, before seed.sql
-- ============================================================

-- Table 1: customers (the people who buy from us)
CREATE TABLE customers (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    email       VARCHAR(150) UNIQUE NOT NULL,
    city        VARCHAR(100),
    country     VARCHAR(100),
    signup_date DATE NOT NULL
);

-- Table 2: orders (a purchase made by a customer)
CREATE TABLE orders (
    id           SERIAL PRIMARY KEY,
    customer_id  INTEGER NOT NULL REFERENCES customers(id),
    order_date   DATE NOT NULL,
    status       VARCHAR(20) NOT NULL,
    total_amount NUMERIC(10, 2) NOT NULL
);

-- Table 3: payments (money received against an order)
CREATE TABLE payments (
    id           SERIAL PRIMARY KEY,
    order_id     INTEGER NOT NULL REFERENCES orders(id),
    amount       NUMERIC(10, 2) NOT NULL,
    payment_date DATE NOT NULL,
    method       VARCHAR(20) NOT NULL
);