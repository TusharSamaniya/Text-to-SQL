# test_sql_gen.py — generate SQL for a question (print only, DON'T execute)
import few_shots
import llm
import prompts

question = "How many customers live in Mumbai?"

# 1) Build the full my capabilities: role + schema + examples + question
prompt = prompts.build_sql_prompt(question, few_shots.format_few_shots())

# 2) Ask Gemini
sql = llm.ask(prompt)

# 3) Show the result (we only print — executing comes in T1.5)
print("QUESTION:", question)
print("GENERATED SQL:")
print(sql)