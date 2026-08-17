# migrate_cloud.py — build the cloud database from schema.sql + seed.sql.
# Runs against WHATEVER DATABASE_URL is in .env (so it works for local
# or Neon/Supabase). The seed is deterministic (setseed) -> the cloud
# database gets exactly the same data as local.
import os

import psycopg2

import config
import db

BASE = os.path.dirname(os.path.dirname(__file__))  # project root


def run_sql_file(filename):
    """Execute every statement in a .sql file against the current DB."""
    with open(os.path.join(BASE, "data", filename)) as f:
        statements = f.read().split(";")
    with psycopg2.connect(config.DATABASE_URL) as conn:
        with conn.cursor() as cur:
            for stmt in statements:
                if stmt.strip():
                    cur.execute(stmt)
    print(f"  {filename} executed OK")


print(f"Target database: {config.DATABASE_URL.split('@')[1]}")
print("1) creating tables (schema.sql)")
run_sql_file("schema.sql")
print("2) filling with data (seed.sql)")
run_sql_file("seed.sql")

print("\n3) verification:")
print("   customers:", db.run_query("SELECT COUNT(*) FROM customers"))
print("   orders   :", db.run_query("SELECT COUNT(*) FROM orders"))
print("   payments :", db.run_query("SELECT COUNT(*) FROM payments"))
print("   cities   :", db.run_query("SELECT city, COUNT(*) FROM customers GROUP BY city ORDER BY 2 DESC LIMIT 3"))