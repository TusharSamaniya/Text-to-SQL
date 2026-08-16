# app.py — our web API server
from flask import Flask, jsonify
from flask_cors import CORS

# 1) Create the Flask application
app = Flask(__name__)

# 2) Allow the browser frontend (a different "origin") to call us
CORS(app)


# 3) Define the /api/health endpoint
@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})


# 4) Start the server (only when this file is run directly)
if __name__ == "__main__":
    app.run(debug=True)

