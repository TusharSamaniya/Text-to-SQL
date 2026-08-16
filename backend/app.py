# app.py — our web API server
import uuid

from flask import Flask, jsonify, request
from flask_cors import CORS

import clarifier
import pipeline
import sessions

# 1) Create the Flask application
app = Flask(__name__)

# 2) Allow the browser frontend (a different "origin") to call us
CORS(app)


# 3) Define the /api/health endpoint
@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/api/ask", methods=["POST"])
def ask():
    body = request.json
    session_id = body.get("session_id") or uuid.uuid4().hex
    choice = body.get("choice")

    # --- 1) Is the user answering a pending clarification? ---
    pending_clarification = sessions.get(session_id)
    if choice is not None:
        if not pending_clarification:
            return jsonify({"session_id": session_id, "needs_clarification": False,
                            "error": "No pending clarification for this session."}), 400
        options = pending_clarification["options"]
        if not (0 <= choice < len(options)):
            return jsonify({"session_id": session_id, "needs_clarification": False,
                            "error": "Invalid choice."}), 400
        question = options[choice]       # the picked option IS the new question
        sessions.clear(session_id)
    else:
        sessions.clear(session_id)       # a new question supersedes any pending one
        question = body.get("question", "")

    # --- 2) Ambiguity check (rules + Gemini) ---
    verdict = clarifier.analyze(question)
    if verdict["should_ask"]:
        clarification = clarifier.build_clarification(question)
        sessions.save(session_id, {"original_question": question,
                                   "options": clarification["options"]})
        return jsonify({"session_id": session_id, "needs_clarification": True,
                        "clarification": clarification})

    # --- 3) Clear question -> run the SQL pipeline ---
    try:
        columns, rows = pipeline.ask_question(question)
        rows = [[str(v) for v in row] for row in rows]   # JSON-safe: all strings
        return jsonify({"session_id": session_id, "needs_clarification": False,
                        "question": question, "columns": columns, "rows": rows})
    except Exception as e:
        return jsonify({"session_id": session_id, "needs_clarification": False,
                        "question": question, "columns": [], "rows": [],
                        "error": str(e)}), 500


# 4) Start the server (only when this file is run directly)
if __name__ == "__main__":
    app.run(debug=True)

