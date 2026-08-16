# test_db.py — smoke test: run a few queries through db.py and print rows
import db

queries = [
    ("Newest customers",
     "SELECT name, city, country, signup_date FROM customers ORDER BY signup_date DESC LIMIT 5"),
    ("Biggest orders (join)",
     "SELECT c.name, o.total_amount, o.status FROM orders o "
     "JOIN customers c ON c.id = o.customer_id ORDER BY o.total_amount DESC LIMIT 5"),
    ("New customers last month",
     "SELECT COUNT(*) FROM customers "
     "WHERE signup_date >= date_trunc('month', CURRENT_DATE) - INTERVAL '1 month' "
     "AND signup_date <  date_trunc('month', CURRENT_DATE)"),
]

for title, sql in queries:
    print(f"=== {title} ===")
    for row in db.run_query(sql):
        print(row)
    print()