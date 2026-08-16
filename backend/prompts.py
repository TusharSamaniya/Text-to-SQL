"""prompts.py — the instruction templates sent to Gemini.

build_sql_prompt     → role + schema + few-shots + question → SQL
build_ambiguity_prompt   → is the question ambiguous? (JSON)
build_clarification_prompt → multiple-choice options (JSON)"""
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


def build_clarification_prompt(question):
    """Turn an ambiguous question into multiple-choice options (JSON)."""
    return f"""
You are a helpful assistant for a company database.
The user's question is AMBIGUOUS. Generate 3 concrete interpretations.
Each interpretation must be a COMPLETE standalone question, phrased so
our SQL generator can answer it directly against the schema.

Schema:
{db.get_schema()}

Ambiguous question: {question}

Answer with EXACTLY this JSON:
{{"question": "a short label for what is unclear",
  "options": ["complete question 1", "complete question 2", "complete question 3"]}}
"""