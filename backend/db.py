# db.py — the project's ONLY file that talks to PostgreSQL
import psycopg2
import config


def run_query(sql):
    """Run SQL, return the result rows as a list."""
    with psycopg2.connect(config.DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            return cur.fetchall()


if __name__ == "__main__":
    rows = run_query("SELECT COUNT(*) FROM customers")
    print("Total customers:", rows[0][0])