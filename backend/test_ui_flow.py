# test_ui_flow.py — the FULL loop exactly as the browser does it:
# fresh session id (like React's crypto.randomUUID) -> question
# -> pick option -> refined question -> SQL -> results
# Server must be running first:  python app.py
import requests
import uuid

BASE = "http://127.0.0.1:5000/api/ask"

# The React app generates a fresh session id per page load:
session_id = uuid.uuid4().hex

print("STEP 1 — user asks an ambiguous question")
r = requests.post(BASE, json={"session_id": session_id,
                              "question": "Show me last month's best customers"})
data = r.json()
print("needs_clarification:", data.get("needs_clarification"))
print("label:", data["clarification"]["question"])
for i, opt in enumerate(data["clarification"]["options"], 1):
    print(f"   {i}. {opt}")

print("\nSTEP 2 — user picks option 1")
r = requests.post(BASE, json={"session_id": session_id, "choice": 0})
data = r.json()
print("needs_clarification:", data.get("needs_clarification"))
print("REFINED QUESTION that got answered:")
print("  ", data.get("question"))
print("columns:", data.get("columns"))
print("rows:")
for row in data.get("rows", []):
    print("  ", row)

print("\n=== LOOP COMPLETE: pick -> refined question -> SQL -> results ===")