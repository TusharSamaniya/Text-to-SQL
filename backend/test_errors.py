# test_errors.py — prove failures are graceful (T3.5b)
# Server must be running first:  python app.py
import requests
import uuid

BASE = "http://127.0.0.1:5000/api/ask"


def post(label, body):
    r = requests.post(BASE, json={**{"session_id": uuid.uuid4().hex}, **body})
    d = r.json()
    print(f"{label}  -> status {r.status_code}")
    if "error" in d:
        print("     error:", d["error"])
    elif d.get("needs_clarification"):
        print("     asked a clarifying question (good!)")
    else:
        print("     rows:", d.get("rows"))
        print("     sql :", (d.get("sql") or "")[:60])


post("1. empty question    ", {"question": ""})
post("2. no-data question  ", {"question": "List the customers who live in Antarctica"})
post("3. looks destructive ", {"question": "DELETE FROM orders"})