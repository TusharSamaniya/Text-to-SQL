# test_clarify_flow.py — the FULL clarification dialog over HTTP.
# Server must be running first:  python app.py
import requests

BASE = "http://127.0.0.1:5000/api/ask"
s = "test-session-1"

print("STEP 1 — ask an ambiguous question")
r = requests.post(BASE, json={"session_id": s,
                              "question": "Show me last month's best customers"})
data = r.json()
print("needs_clarification:", data.get("needs_clarification"))
print("label:", data["clarification"]["question"])
for i, opt in enumerate(data["clarification"]["options"], 1):
    print(f"   {i}. {opt}")

print("\nSTEP 2 — user picks option 1")
r = requests.post(BASE, json={"session_id": s, "choice": 0})
data = r.json()
print("needs_clarification:", data.get("needs_clarification"))
print("answered question:", data.get("question"))
print("columns:", data.get("columns"))
print("rows:", data.get("rows", [])[:5])

print("\nSTEP 3 — fresh clear question, same session (pending is gone)")
r = requests.post(BASE, json={"session_id": s,
                              "question": "How many customers are in Mumbai?"})
data = r.json()
print("needs_clarification:", data.get("needs_clarification"))
print("rows:", data.get("rows"))