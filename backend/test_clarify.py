# test_clarify.py — generate multiple-choice options (T3.3)
import clarifier

question = "Show me last month's best customers"
result = clarifier.build_clarification(question)

print("LABEL :", result["question"])
print("OPTIONS:")
for i, opt in enumerate(result["options"], 1):
    print(f"  {i}. {opt}")