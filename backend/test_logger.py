# test_logger.py — prove the audit log works (T4.2)
import json
import uuid

import logger

# --- 1) Unit check: log_entry appends a parseable line ---
logger.log_entry({"type": "unit-test", "question": "hello"})
with open(logger.LOG_FILE) as f:
    lines = f.readlines()
print("unit entry written:", json.loads(lines[-1]))

# --- 2) Live check: one full question through the API (test client) ---
from app import app

client = app.test_client()
r = client.post("/api/ask", json={"session_id": uuid.uuid4().hex,
                                  "question": "How many customers are in Mumbai?"})
print("status:", r.status_code, "| answer:", r.get_json().get("rows"))

with open(logger.LOG_FILE) as f:
    entries = [json.loads(line) for line in f]

entry = entries[-1]
print("\n--- last logged entry (the audit trail of that question) ---")
print("type     :", entry["type"])
print("question :", entry["question"])
print("sql      :", entry.get("sql"))
print("columns  :", entry.get("columns"))
print("rows     :", entry.get("rows"))
print("timestamp:", entry.get("timestamp"))