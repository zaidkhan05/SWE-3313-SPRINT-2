
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
USERS_FILE = os.path.join(DATA_DIR, "users.csv")
ORDERS_FILE = os.path.join(DATA_DIR, "orders.csv")
INVENTORY_FILE = os.path.join(DATA_DIR, "inventory.csv")
CLOCKIN_FILE = os.path.join(DATA_DIR, "clockin.csv")
MENU_FILE = os.path.join(DATA_DIR, "menu_items.csv")
ATTEMPTS_FILE = os.path.join(DATA_DIR, "login_attempts.csv")

os.makedirs(DATA_DIR, exist_ok=True)

def load_csv(file, columns):
    if os.path.exists(file):
        return pd.read_csv(file)
    return pd.DataFrame(columns=columns)

def save_csv(df, file):
    df.to_csv(file, index=False)

# ----------------------- AUTO-INITIALIZE MANAGER -----------------------
@app.before_first_request
def ensure_manager_exists():
    users = load_csv(USERS_FILE, ["UserName", "Password", "EmployeeID", "Role", "Clock_In_Time", "Clock_Out_Time"])
    if users.empty:
        print("\n--- No users found. Please create a manager account using the /api/init-manager endpoint.\n")

# ----------------------- INIT MANAGER -----------------------
@app.route("/api/init-manager", methods=["POST"])
def init_manager():
    data = request.json
    users = load_csv(USERS_FILE, ["UserName", "Password", "EmployeeID", "Role", "Clock_In_Time", "Clock_Out_Time"])
    if not users.empty:
        return jsonify({"success": False, "message": "Manager already exists."}), 400

    new_manager = {
        "UserName": data.get("username"),
        "Password": data.get("password"),
        "EmployeeID": data.get("employee_id", "MGR001"),
        "Role": "Manager",
        "Clock_In_Time": "",
        "Clock_Out_Time": ""
    }
    users = pd.DataFrame([new_manager])
    save_csv(users, USERS_FILE)
    return jsonify({"success": True, "message": "Manager account created."})

# [Insert login, reset, waiter, and manager routes here, same as before...]

if __name__ == "__main__":
    app.run(debug=True)
