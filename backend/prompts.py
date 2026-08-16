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


def build_ambiguity_prompt(question):
    """Ask Gemini to judge if a question is ambiguous (JSON reply)."""
    return f"""
You are a helpful assistant for a company database.
Decide if the user's question is AMBIGUOUS, meaning the SQL
answer would change depending on how we interpret it.
Watch for vague words like "best", "top", "recent", "large".

Answer with EXACTLY this JSON:
{{"ambiguous": true or false, "reason": "one short sentence or leave empty"}}

Question: {question}
"""