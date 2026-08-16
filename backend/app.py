"""app.py — the web API server (Flask).

Endpoints:
    GET  /api/health  → liveness check
    POST /api/ask     → question → clarification / answer (JSON)

The route is a small state machine: an ambiguous question stores a
pending clarification per session; a subsequent "choice" request
resolves it into the SQL pipeline."""
import uuid

from flask import Flask, jsonify, request
from flask_cors import CORS

import clarifier
import logger
import pipeline
import sessions

# 1) Create the Flask application
app = Flask(__name__)

# 2) Allow the browser frontend (a different "origin") to call us
CORS(app)


def friendly_error(e):
    """Turn any exception into a short, human-readable message."""
    text = str(e).lower()
    if "only select queries are allowed" in text:
        return ("I can only answer read-only questions. Phrase it as a "
                "question, e.g. 'How many customers are in Mumbai?'")
    if any(k in text for k in ("503", "429", "quota", "rate limit")):
        return "The AI service is busy right now. Please wait a moment and try again."
    if any(k in text for k in ("refused", "could not connect", "operationalerror")):
        return "Could not reach the database. Is PostgreSQL running?"
    if "does not exist" in text:
        return "That question led to an invalid query. Please rephrase it."
    return "Something went wrong while answering. Please try rephrasing your question."


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
        if not question.strip():         # nothing to answer -> ask politely
            return jsonify({"session_id": session_id, "needs_clarification": False,
                            "error": "Please type a question first."}), 400

    # --- 2) Ambiguity check (rules + Gemini) ---
    try:
        verdict = clarifier.analyze(question)
        if verdict["should_ask"]:
            clarification = clarifier.build_clarification(question)
            sessions.save(session_id, {"original_question": question,
                                       "options": clarification["options"]})
            logger.log_entry({"type": "clarify", "session_id": session_id,
                              "question": question,
                              "options": clarification["options"]})
            return jsonify({"session_id": session_id,
                            "needs_clarification": True,
                            "clarification": clarification})
    except Exception as e:
        logger.log_entry({"type": "error", "session_id": session_id,
                          "question": question, "error": str(e)})
        return jsonify({"session_id": session_id, "needs_clarification": False,
                        "question": question, "columns": [], "rows": [],
                        "sql": "",
                        "error": friendly_error(e),
                        "detail": str(e)}), 500

    # --- 3) Clear question -> run the SQL pipeline ---
    try:
        columns, rows, sql = pipeline.ask_question(question)
        rows = [[str(v) for v in row] for row in rows]   # JSON-safe: all strings
        logger.log_entry({"type": "answer", "session_id": session_id,
                          "question": question, "sql": sql,
                          "columns": columns, "rows": rows})
        return jsonify({"session_id": session_id, "needs_clarification": False,
                        "question": question, "columns": columns, "rows": rows,
                        "sql": sql})
    except Exception as e:
        logger.log_entry({"type": "error", "session_id": session_id,
                          "question": question, "error": str(e)})
        return jsonify({"session_id": session_id, "needs_clarification": False,
                        "question": question, "columns": [], "rows": [],
                        "sql": "",
                        "error": friendly_error(e),     # human message
                        "detail": str(e)}), 500         # full traceback for devs


# 4) Start the server (only when this file is run directly)
if __name__ == "__main__":
    app.run(debug=True)

