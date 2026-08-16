"""db.py — the project's ONLY file that talks to PostgreSQL.

Holds every database interaction: plain queries, safe read-only
queries with a row cap, schema introspection, and queries that
also return the result column names (for the API)."""
import psycopg2
import config


def run_query(sql):
    """Run SQL, return the result rows as a list."""
    with psycopg2.connect(config.DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            return cur.fetchall()


def run_query_with_headers(sql, max_rows=100):
    """Run SQL read-only (like run_query_safe) and return (headers, rows).
    headers = the column names of the result (from cursor.description),
    so the frontend can label its table."""
    stripped = sql.strip().lower()
    if not (stripped.startswith("select") or stripped.startswith("with")):
        raise ValueError("Only SELECT queries are allowed.")
    safe = f"SELECT * FROM ({sql.rstrip(';')}) AS _q LIMIT {max_rows}"

    with psycopg2.connect(config.DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(safe)
            headers = [d[0] for d in cur.description]
            return headers, cur.fetchall()


def get_schema():
    """Ask the database about itself; return a text description."""
    rows = run_query(
        "SELECT table_name, column_name, data_type "
        "FROM information_schema.columns "
        "WHERE table_schema = 'public' "
        "ORDER BY table_name, ordinal_position"
    )

    schema = ""
    current_table = None
    for table, column, dtype in rows:
        if table != current_table:          # new table? print its header
            schema += f"\nTable: {table}\n"
            current_table = table
        schema += f"  - {column} ({dtype})\n"
    return schema


def run_query_safe(sql, max_rows=100):
    """Execute SQL but never allow writes, and cap the rows returned."""
    stripped = sql.strip().lower()
    if not (stripped.startswith("select") or stripped.startswith("with")):
        raise ValueError("Only SELECT queries are allowed.")

    # Put the query in a box; the box only lets max_rows out.
    safe = f"SELECT * FROM ({sql.rstrip(';')}) AS _q LIMIT {max_rows}"
    return run_query(safe)


if __name__ == "__main__":
    rows = run_query("SELECT COUNT(*) FROM customers")
    print("Total customers:", rows[0][0])