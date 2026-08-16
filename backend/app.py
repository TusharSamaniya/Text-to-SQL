# app.py — our web API server
from flask import Flask, jsonify, request
from flask_cors import CORS
import pipeline

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
    question = request.json.get("question", "")
    try:
        rows = pipeline.question_to_sql(question)
        rows = [[str(v) for v in row] for row in rows]   # JSON-safe: all strings
        return jsonify({"question": question, "rows": rows})
    except Exception as e:
        return jsonify({"question": question, "rows": [], "error": str(e)}), 500


# 4) Start the server (only when this file is run directly)
if __name__ == "__main__":
    app.run(debug=True)

