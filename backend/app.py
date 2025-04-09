from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os

app = Flask(__name__)
CORS(app)

USERS_FILE = os.path.join(os.path.dirname(__file__), "data", "users.csv")

def load_users():
    if os.path.exists(USERS_FILE):
        return pd.read_csv(USERS_FILE)
    else:
        return pd.DataFrame(columns=["username", "password", "role"])

@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    users = load_users()
    match = users[(users["username"] == data.get("username")) & (users["password"] == data.get("password"))]
    if not match.empty:
        return jsonify({
            "success": True,
            "username": match.iloc[0]["username"],
            "role": match.iloc[0]["role"]
        })
    return jsonify({"success": False, "message": "Invalid credentials"}), 401

if __name__ == "__main__":
    app.run(debug=True)
