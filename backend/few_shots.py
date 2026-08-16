# few_shots.py — example question->SQL pairs shown to Gemini
# Each pair teaches ONE SQL pattern, using our REAL column names.

FEW_SHOTS = [
    # 1. Simple count
    ("How many customers do we have?", "SELECT COUNT(*) FROM customers;"),

    # 2. Selecting specific columns
    ("List the name and city of every customer.",
     "SELECT name, city FROM customers;"),

    # 3. Filtering with WHERE
    ("How many orders are delivered?",
     "SELECT COUNT(*) FROM orders WHERE status = 'delivered';"),

    # 4. Sum (money question)
    ("What is the total revenue from payments?",
     "SELECT SUM(amount) FROM payments;"),

    # 5. Average
    ("What is the average order amount?",
     "SELECT AVG(total_amount) FROM orders;"),

    # 6. Grouping: one row per customer
    ("How many orders did each customer place?",
     "SELECT customer_id, COUNT(*) FROM orders GROUP BY customer_id;"),

    # 7. Grouping by a category
    ("Total payments per method.",
     "SELECT method, SUM(amount) FROM payments GROUP BY method;"),

    # 8. Sorting + limiting
    ("Show the 5 most recent orders.",
     "SELECT * FROM orders ORDER BY order_date DESC LIMIT 5;"),

    # 9. JOIN two tables
    ("Show order amounts together with customer names.",
     "SELECT o.total_amount, c.name FROM orders o "
     "JOIN customers c ON c.id = o.customer_id;"),

    # 10. THE date pattern: "last month" (the one Gemini gets wrong
    #     without an example — it wants to guess, we show the logic)
    ("How many new customers signed up last month?",
     "SELECT COUNT(*) FROM customers "
     "WHERE signup_date >= date_trunc('month', CURRENT_DATE) - INTERVAL '1 month' "
     "AND signup_date <  date_trunc('month', CURRENT_DATE);"),

    # 11. Per-month trend (date_trunc + group by)
    ("Show total revenue per month.",
     "SELECT date_trunc('month', payment_date) AS month, SUM(amount) "
     "FROM payments GROUP BY month ORDER BY month;"),
]


def format_few_shots():
    """Turn the list into the text block that goes in the my capabilities."""
    return "\n".join(f"Question: {q}\nSQL: {s}" for q, s in FEW_SHOTS)