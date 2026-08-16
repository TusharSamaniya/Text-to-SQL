# test_ambiguity_ai.py — let Gemini judge ambiguity (T3.2)
# The 3rd question uses a word NOT in our rule list ("favourite")
# to show why Gemini is the deep judge.
import clarifier

questions = [
    "Show me last month's best customers",
    "How many customers are in Mumbai?",
    "Who are our favourite customers?",
]

for q in questions:
    result = clarifier.judge_ambiguity(q)
    print(f"Q: {q!r}")
    print(f"   -> ambiguous: {result['ambiguous']}, reason: {result['reason']!r}")