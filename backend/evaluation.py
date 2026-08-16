# evaluation.py — the test set for Phase 4 scoring.
# Each entry:
#   question      — what the user types
#   category      — which SQL pattern / behaviour it tests
#   should_clarify — True = the system MUST ask before answering
#   expected_sql  — the golden query (verified against the DB).
#                   Only present for clear questions.
#
# Scoring (next subtask) runs expected_sql to get ground-truth rows,
# runs the system, and compares the rows — not the SQL text.

EVAL_QUESTIONS = [
    # --- count ---
    {"question": "How many customers are registered?",
     "category": "count", "should_clarify": False,
     "expected_sql": "SELECT COUNT(*) FROM customers;"},

    {"question": "How many orders are delivered?",
     "category": "count-filter", "should_clarify": False,
     "expected_sql": "SELECT COUNT(*) FROM orders WHERE status = 'delivered';"},

    {"question": "How many orders were cancelled?",
     "category": "count-filter", "should_clarify": False,
     "expected_sql": "SELECT COUNT(*) FROM orders WHERE status = 'cancelled';"},

    # --- basic filters ---
    {"question": "List the names of all customers who live in Mumbai.",
     "category": "filter", "should_clarify": False,
     "expected_sql": "SELECT name FROM customers WHERE city = 'Mumbai';"},

    {"question": "What is the total amount paid by credit card?",
     "category": "filter-sum", "should_clarify": False,
     "expected_sql": "SELECT SUM(amount) FROM payments WHERE method = 'credit_card';"},

    # --- aggregates ---
    {"question": "What is the total revenue from payments?",
     "category": "sum", "should_clarify": False,
     "expected_sql": "SELECT SUM(amount) FROM payments;"},

    {"question": "What is the average order amount?",
     "category": "avg", "should_clarify": False,
     "expected_sql": "SELECT AVG(total_amount) FROM orders;"},

    {"question": "Show the total amount of orders per status.",
     "category": "group-by", "should_clarify": False,
     "expected_sql": "SELECT status, SUM(total_amount) FROM orders GROUP BY status;"},

    {"question": "Show total revenue per month.",
     "category": "group-by-date", "should_clarify": False,
     "expected_sql": "SELECT date_trunc('month', payment_date) AS month, SUM(amount) FROM payments GROUP BY month ORDER BY month;"},

    {"question": "Which city has the most customers?",
     "category": "top-1", "should_clarify": False,
     "expected_sql": "SELECT city, COUNT(*) FROM customers GROUP BY city ORDER BY COUNT(*) DESC LIMIT 1;"},

    # --- sort / limit ---
    {"question": "Show the 5 most recent orders.",
     "category": "sort-limit", "should_clarify": False,
     "expected_sql": "SELECT * FROM orders ORDER BY order_date DESC LIMIT 5;"},

    {"question": "Show the top 5 orders by amount.",
     "category": "sort-limit", "should_clarify": False,
     # KNOWN LIMITATION: our rule list flags "top" and the fast path may
     # ask even though the metric IS specified. We measure, not hide.
     "expected_sql": "SELECT * FROM orders ORDER BY total_amount DESC LIMIT 5;"},

    # --- joins ---
    {"question": "Show order amounts together with customer names.",
     "category": "join", "should_clarify": False,
     "expected_sql": "SELECT o.total_amount, c.name FROM orders o JOIN customers c ON c.id = o.customer_id;"},

    # --- date logic ---
    {"question": "How many new customers signed up last month?",
     "category": "date-window", "should_clarify": False,
     "expected_sql": "SELECT COUNT(*) FROM customers WHERE signup_date >= date_trunc('month', CURRENT_DATE) - INTERVAL '1 month' AND signup_date < date_trunc('month', CURRENT_DATE);"},

    {"question": "How many customers signed up today?",
     "category": "date", "should_clarify": False,
     "expected_sql": "SELECT COUNT(*) FROM customers WHERE signup_date = CURRENT_DATE;"},

    # --- no data found ---
    {"question": "List the customers who live in Antarctica.",
     "category": "no-data", "should_clarify": False,
     "expected_sql": "SELECT * FROM customers WHERE country = 'Antarctica';"},

    # --- must ask: rule-only triggers ---
    {"question": "Show me the best customers.",
     "category": "clarify-rule", "should_clarify": True},

    {"question": "Show me last month's best customers.",
     "category": "clarify-rule", "should_clarify": True},

    {"question": "What is the most popular payment method?",
     "category": "clarify-rule", "should_clarify": True},

    # --- must ask: Gemini-only trigger (no rule word!) ---
    {"question": "Who are our favourite customers?",
     "category": "clarify-gemini", "should_clarify": True},
]