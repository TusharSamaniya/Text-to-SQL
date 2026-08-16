# test_detect.py — prove the detector works (incl. the "stopped" trap)
import clarifier

questions = [
    "Show me last month's best customers",
    "How many customers are in Mumbai?",
    "What was our top revenue last year?",
    "How many stopped orders do we have?",   # TRAP: contains 'top'
    "List the most recent orders.",
]

for q in questions:
    found = clarifier.detect_ambiguity(q)
    if found:
        print(f"AMBIGUOUS: {q!r}")
        for word, hint in found:
            print(f"   '{word}' -> {hint}")
    else:
        print(f"clear:     {q!r}")