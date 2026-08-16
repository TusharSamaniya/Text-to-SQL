# test_combine.py — the combined ambiguity decision (T3.2)
# Watch WHICH layer catches each question:
#   "best customers" / "top revenue"  -> fast path (rules)
#   "favourite customers"             -> slow path (Gemini)
#   "How many customers in Mumbai?"   -> neither
import clarifier

questions = [
    "Show me last month's best customers",
    "Who are our favourite customers?",
    "How many customers are in Mumbai?",
    "What was our top revenue last year?",
]

for q in questions:
    result = clarifier.analyze(q)
    print(f"Q: {q!r}")
    print(f"   should_ask: {result['should_ask']}")
    for r in result["reasons"]:
        print(f"      - {r}")