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
MENU_FILE = os.path.join(DATA_DIR, "menu.csv")
ATTEMPTS_FILE = os.path.join(DATA_DIR, "login_attempts.csv")

os.makedirs(DATA_DIR, exist_ok=True)

def load_csv(file, columns):
    if os.path.exists(file):
        return pd.read_csv(file)
    return pd.DataFrame(columns=columns)

def save_csv(df, file):
    df.to_csv(file, index=False)

# ----------------------- AUTH: LOGIN WITH ATTEMPT TRACKING -----------------------
@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    users = load_csv(USERS_FILE, ["username", "password", "role"])
    attempts = load_csv(ATTEMPTS_FILE, ["username", "attempts"])

    if username in attempts["username"].values:
        attempt_row = attempts[attempts["username"] == username]
        if attempt_row.iloc[0]["attempts"] >= 3:
            return jsonify({"success": False, "message": "Account locked. Contact a manager to reset your login."}), 403

    match = users[(users["username"] == username) & (users["password"] == password)]
    if not match.empty:
        attempts = attempts[attempts["username"] != username]
        save_csv(attempts, ATTEMPTS_FILE)
        return jsonify({
            "success": True,
            "username": username,
            "role": match.iloc[0]["role"]
        })
    else:
        if username in attempts["username"].values:
            attempts.loc[attempts["username"] == username, "attempts"] += 1
        else:
            attempts = pd.concat([attempts, pd.DataFrame([[username, 1]], columns=["username", "attempts"])], ignore_index=True)
        save_csv(attempts, ATTEMPTS_FILE)
        return jsonify({"success": False, "message": "Invalid credentials"}), 401

@app.route("/api/reset-attempts", methods=["POST"])
def reset_attempts():
    data = request.json
    manager_user = data.get("manager_username")
    manager_pass = data.get("manager_password")
    target_user = data.get("username")

    users = load_csv(USERS_FILE, ["username", "password", "role"])
    manager = users[(users["username"] == manager_user) & (users["password"] == manager_pass) & (users["role"].str.lower() == "manager")]

    if manager.empty:
        return jsonify({"success": False, "message": "Unauthorized reset attempt."}), 403

    attempts = load_csv(ATTEMPTS_FILE, ["username", "attempts"])
    attempts = attempts[attempts["username"] != target_user]
    save_csv(attempts, ATTEMPTS_FILE)
    return jsonify({"success": True, "message": f"Login attempts reset for {target_user}"})


# ----------------------- WAITER ROUTES -----------------------
@app.route("/api/waiter/orders", methods=["GET"])
def waiter_orders():
    orders = load_csv(ORDERS_FILE, ["table", "item", "quantity", "notes", "status", "timestamp"])
    pending = orders[orders["status"].str.lower() != "ready"]
    return pending.to_dict(orient="records")

@app.route("/api/waiter/clockin", methods=["GET"])
def waiter_clockin_history():
    clock_data = load_csv(CLOCKIN_FILE, ["username", "role", "date", "hours"])
    waiters = clock_data[clock_data["role"].str.lower() == "waiter"]
    return waiters.to_dict(orient="records")

@app.route("/api/menu", methods=["GET"])
def get_menu():
    menu = load_csv(MENU_FILE, ["category", "item", "description", "price"])
    return menu.to_dict(orient="records")

@app.route("/api/orders", methods=["POST"])
def submit_order():
    data = request.json
    order = {
        "table": data.get("table"),
        "item": data.get("item"),
        "quantity": data.get("quantity"),
        "notes": data.get("notes"),
        "status": "Pending",
        "timestamp": datetime.now().isoformat()
    }
    orders = load_csv(ORDERS_FILE, ["table", "item", "quantity", "notes", "status", "timestamp"])
    orders = pd.concat([orders, pd.DataFrame([order])], ignore_index=True)
    save_csv(orders, ORDERS_FILE)
    return jsonify({"success": True})

@app.route("/api/orders", methods=["GET"])
def get_orders():
    orders = load_csv(ORDERS_FILE, ["table", "item", "quantity", "notes", "status", "timestamp"])
    return orders.to_dict(orient="records")


# ----------------------- MANAGER ROUTES -----------------------
@app.route("/api/manager/orders", methods=["GET"])
def manager_get_orders():
    orders = load_csv(ORDERS_FILE, ["table", "item", "quantity", "notes", "status", "timestamp"])
    return orders.to_dict(orient="records")

@app.route("/api/manager/order-history", methods=["GET"])
def manager_order_history():
    orders = load_csv(ORDERS_FILE, ["table", "item", "quantity", "notes", "status", "timestamp"])
    completed = orders[orders["status"].str.lower() == "ready"]
    return completed.to_dict(orient="records")

@app.route("/api/manager/inventory", methods=["GET"])
def manager_inventory():
    inventory = load_csv(INVENTORY_FILE, ["item", "quantity"])
    return inventory.to_dict(orient="records")

@app.route("/api/manager/inventory", methods=["POST"])
def manager_update_inventory():
    data = request.json
    inventory = load_csv(INVENTORY_FILE, ["item", "quantity"])
    existing = inventory[inventory["item"] == data["item"]]
    if not existing.empty:
        inventory.loc[inventory["item"] == data["item"], "quantity"] = data["quantity"]
    else:
        inventory = pd.concat([inventory, pd.DataFrame([data])], ignore_index=True)
    save_csv(inventory, INVENTORY_FILE)
    return jsonify({"success": True})

@app.route("/api/manager/inventory/delete", methods=["POST"])
def manager_delete_inventory():
    data = request.json
    inventory = load_csv(INVENTORY_FILE, ["item", "quantity"])
    inventory = inventory[inventory["item"] != data["item"]]
    save_csv(inventory, INVENTORY_FILE)
    return jsonify({"success": True})

@app.route("/api/manager/employees", methods=["GET"])
def manager_get_employees():
    users = load_csv(USERS_FILE, ["username", "password", "role"])
    return users.to_dict(orient="records")

@app.route("/api/manager/employees", methods=["POST"])
def manager_add_employee():
    data = request.json
    users = load_csv(USERS_FILE, ["username", "password", "role"])
    if data["username"] in users["username"].values:
        return jsonify({"success": False, "message": "Username already exists"}), 409
    new_user = pd.DataFrame([data])
    users = pd.concat([users, new_user], ignore_index=True)
    save_csv(users, USERS_FILE)
    return jsonify({"success": True})

@app.route("/api/manager/employees/delete", methods=["POST"])
def manager_delete_employee():
    data = request.json
    users = load_csv(USERS_FILE, ["username", "password", "role"])
    users = users[users["username"] != data["username"]]
    save_csv(users, USERS_FILE)
    return jsonify({"success": True})

@app.route("/api/manager/clockin", methods=["GET"])
def manager_clockin():
    clock_data = load_csv(CLOCKIN_FILE, ["username", "role", "date", "hours"])
    return clock_data.to_dict(orient="records")

@app.route("/api/manager/analytics", methods=["GET"])
def manager_analytics():
    orders = load_csv(ORDERS_FILE, ["table", "item", "quantity", "notes", "status", "timestamp"])
    total_orders = len(orders)
    top_items = orders["item"].value_counts().head(3).to_dict()
    return {
        "total_orders": total_orders,
        "top_items": top_items
    }

if __name__ == "__main__":
    app.run(debug=True)
