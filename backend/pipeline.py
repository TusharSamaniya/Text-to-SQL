# pipeline.py — the main flow: question -> SQL -> results (self-correcting)
import db
import few_shots
import llm
import prompts


def clean_sql(raw):
    """Remove markdown code fences if Gemini wrapped the SQL in ```sql ... ```"""
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw[raw.find("\n") + 1:]                 # drop the ```sql line
        raw = raw[:raw.rfind("```")] if "```" in raw else raw  # drop the close
    return raw.strip()


def ask_question(question):
    """Turn a question into (column_names, rows, sql) so the API can
    SHOW the generated SQL (explainability). Gemini can fix errors 2 times."""
    prompt = prompts.build_sql_prompt(question, few_shots.format_few_shots())
    sql = clean_sql(llm.ask(prompt))

    for attempt in range(3):          # 1st try + up to 2 fixes
        try:
            headers, rows = db.run_query_with_headers(sql)
            return headers, rows, sql
        except Exception as e:
            if attempt == 2:          # out of retries -> fail honestly
                raise
            print("SQL failed -> asking Gemini to fix:", e)
            sql = clean_sql(llm.ask(
                "A PostgreSQL query failed. Fix it and answer ONLY with "
                "the corrected SQL.\n\n"
                f"Original question: {question}\n"
                f"Failed SQL:\n{sql}\n"
                f"Error message:\n{e}\n\n"
                "Corrected SQL:\n"
            ))
    return [], [], sql


def question_to_sql(question):
    """Turn a question into result rows, letting Gemini fix errors 2 times."""
    prompt = prompts.build_sql_prompt(question, few_shots.format_few_shots())
    sql = clean_sql(llm.ask(prompt))

    for attempt in range(3):          # 1st try + up to 2 fixes
        try:
            return db.run_query_safe(sql)
        except Exception as e:
            if attempt == 2:          # out of retries -> fail honestly
                raise
            print("SQL failed -> asking Gemini to fix:", e)
            sql = clean_sql(llm.ask(
                "A PostgreSQL query failed. Fix it and answer ONLY with "
                "the corrected SQL.\n\n"
                f"Original question: {question}\n"
                f"Failed SQL:\n{sql}\n"
                f"Error message:\n{e}\n\n"
                "Corrected SQL:\n"
            ))
    return []