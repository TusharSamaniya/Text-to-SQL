# run_evaluation.py — score the system against the test set (T4.1b).
# Uses Flask's in-process test client: no server window needed.
# NOTE: ~40 Gemini calls -> takes a few minutes; questions are spaced
# 3.5s apart to respect the free-tier per-minute quota.
import time
import uuid

from app import app
import db
import evaluation

client = app.test_client()


def golden_set(sql):
    """Run the golden query and return its rows as a set of string-tuples."""
    rows = db.run_query(sql)
    return {tuple(str(v) for v in row) for row in rows}


passed = 0
total = len(evaluation.EVAL_QUESTIONS)

for i, t in enumerate(evaluation.EVAL_QUESTIONS, 1):
    sid = uuid.uuid4().hex
    print(f"\n[{i}/{total}] {t['category']}: {t['question']}", flush=True)

    try:
        # --- Step 1: ask the question (fresh session) ---
        r = client.post("/api/ask", json={"session_id": sid, "question": t["question"]})
        data = r.get_json()

        if t["should_clarify"]:
            # Correct behaviour: must ask, and an option must resolve.
            asked = bool(data.get("needs_clarification"))
            resolved = False
            if asked:
                r2 = client.post("/api/ask", json={"session_id": sid, "choice": 0})
                d2 = r2.get_json()
                resolved = (d2.get("needs_clarification") is False
                            and not d2.get("error"))
            ok = asked and resolved
            print(f"  -> {'PASS' if ok else 'FAIL'}  (asked={asked}, resolved={resolved})")
        else:
            # Correct behaviour: answer without asking, rows match golden.
            if data.get("needs_clarification"):
                print("  -> FAIL  (asked clarification when it shouldn't)")
                passed_this = False
            elif data.get("error"):
                print(f"  -> FAIL  (error: {data['error'][:60]})")
                passed_this = False
            else:
                actual = {tuple(row) for row in data.get("rows", [])}
                expected = golden_set(t["expected_sql"])
                passed_this = actual == expected
                print(f"  -> {'PASS' if passed_this else 'FAIL'}  "
                      f"(returned {len(actual)} rows vs expected {len(expected)})")
                if not passed_this:
                    print("     returned:", sorted(actual)[:3], "...")
            ok = passed_this

    except Exception as e:
        print(f"  -> ERROR  ({e})")
        ok = False

    passed += ok
    time.sleep(3.5)              # keep under the free-tier per-minute quota

print(f"\n====================")
print(f"SCORE: {passed}/{total} passed")
print(f"====================")