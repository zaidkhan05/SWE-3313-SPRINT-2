from flask import Flask, request, jsonify
import pandas as pd
import os
from datetime import datetime

app = Flask(__name__)

# Path to the CSVs
data_dir = "data"
USERS_FILE = os.path.join(data_dir, "users.csv")

# Ensure data folder exists
os.makedirs(data_dir, exist_ok=True)

# Load user data
def load_users():
    if os.path.exists(USERS_FILE):
        return pd.read_csv(USERS_FILE)
    else:
        return pd.DataFrame(columns=["username", "password", "role"])

# Save user data
def save_users(df):
    df.to_csv(USERS_FILE, index=False)

@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    users = load_users()
    user = users[(users["username"] == username) & (users["password"] == password)]

    if not user.empty:
        return jsonify({
            "success": True,
            "username": username,
            "role": user.iloc[0]["role"]
        })
    else:
        return jsonify({"success": False, "message": "Invalid credentials"}), 401

@app.route("/api/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    role = data.get("role")

    users = load_users()
    if username in users["username"].values:
        return jsonify({"success": False, "message": "Username already exists"}), 409

    new_user = pd.DataFrame([[username, password, role]], columns=["username", "password", "role"])
    users = pd.concat([users, new_user], ignore_index=True)
    save_users(users)
    return jsonify({"success": True})

if __name__ == "__main__":
    app.run(debug=True)
