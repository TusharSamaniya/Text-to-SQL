"""logger.py — JSONL audit log: one JSON line per API interaction.

Logs every clarify / answer / error with session id, question,
SQL, and rows, so the system's work can be audited and debugged."""
import json
import os
from datetime import datetime

# The log lives next to this file: backend/history.jsonl
LOG_FILE = os.path.join(os.path.dirname(__file__), "history.jsonl")


def log_entry(entry):
    """Stamp the entry with the current time and append it as one JSON line."""
    entry["timestamp"] = datetime.now().isoformat()
    with open(LOG_FILE, "a") as f:          # "a" = append: never overwrites
        f.write(json.dumps(entry) + "\n")