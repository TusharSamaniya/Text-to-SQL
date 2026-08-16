# test_few_shots.py — see the my capabilities with examples loaded
import few_shots
import prompts

print(prompts.build_sql_prompt("How many customers live in Mumbai?", few_shots.format_few_shots()))