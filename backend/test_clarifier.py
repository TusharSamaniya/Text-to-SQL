# test_clarifier.py — show the ambiguity rules (T3.1)
import clarifier

print("Ambiguity rules loaded:")
for word, hint in clarifier.AMBIGUOUS_WORDS:
    print(f"  '{word}' -> {hint}")