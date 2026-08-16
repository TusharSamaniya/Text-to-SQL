# prompts.py — the instructions we send to Gemini
import db


def build_sql_prompt(question, examples=""):
    """Assemble the full my capabilities: role + schema + examples + question."""
    return f"""
You are an expert PostgreSQL assistant. Answer ONLY with SQL.

The database schema is:
{db.get_schema()}

Example questions and their SQL:
{examples}

Now write the SQL for this question:
Question: {question}
SQL:
"""