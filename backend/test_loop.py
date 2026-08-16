# test_loop.py — prove the self-correction loop: forced cases first (no network),
# then one live question (with a tiny retry, because cloud APIs hiccup - see 503)
import time

import llm
import pipeline

original_ask = llm.ask  # save the real ai so we can swap it back later

print("=== 1. FORCED: a bad first answer, then a good fix ===")
calls = []


def fake_ask(prompt):
    calls.append(1)
    if len(calls) == 1:  # 1st call: Gemini "hallucinates" a wrong column
        return "SELECT customer_id FROM payments"
    # 2nd call: the fixed version, joining through orders
    return ("SELECT c.name, p.amount FROM payments p "
            "JOIN orders o ON o.id = p.order_id "
            "JOIN customers c ON c.id = o.customer_id")


llm.ask = fake_ask
print(pipeline.question_to_sql("payment amounts with customer names"))
llm.ask = original_ask

print("\n=== 2. FORCED: always wrong -> must give up after 2 retries ===")


def always_bad(prompt):
    return "SELECT nobody FROM nowhere"


llm.ask = always_bad
try:
    pipeline.question_to_sql("any question")
    print("NOT blocked (bad!)")
except Exception as e:
    print("Gave up as expected:", type(e).__name__, "-", str(e)[:60])
llm.ask = original_ask

print("\n=== 3. LIVE: one real question (retry up to 3x if the API is busy) ===")
for attempt in range(3):
    try:
        rows = pipeline.question_to_sql(
            "Show payment amounts with the customer's name.")
        print(rows)
        break
    except Exception as e:
        print("API hiccup, retrying...", str(e)[:50])
        time.sleep(3)