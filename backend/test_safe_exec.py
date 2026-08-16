# test_safe_exec.py — prove the guardrails work
import db

print("--- 1. A normal safe query (Mumbai) ---")
rows = db.run_query_safe("SELECT COUNT(*) FROM customers WHERE city = 'Mumbai'")
print(rows)

print("\n--- 2. Row cap: all customers, capped at 5 ---")
rows = db.run_query_safe("SELECT * FROM customers", max_rows=5)
print("returned", len(rows), "rows (should be 5)")
for r in rows:
    print(r)

print("\n--- 3. A DELETE is rejected by our check ---")
try:
    db.run_query_safe("DELETE FROM customers")
    print("NOT BLOCKED (bad!)")
except ValueError as e:
    print("Rejected as expected:", e)

print("\n--- 4. Sneaky multi-statement 'SELECT 1; DROP TABLE customers' ---")
try:
    db.run_query_safe("SELECT 1; DROP TABLE customers")
    print("NOT BLOCKED (bad!)")
except Exception as e:
    print("Blocked as expected:", type(e).__name__, "-", str(e)[:80])

print("\n--- 5. Safety net: customers table still intact ---")
print(db.run_query("SELECT COUNT(*) FROM customers"))