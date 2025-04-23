from flask import Flask, request, jsonify 
from flask_cors import CORS
import pandas as pd
import os
from datetime import datetime
import sys
import webbrowser
from threading import Timer

app = Flask(__name__)
CORS(app)

if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.abspath("backend/")

DATA_DIR = os.path.join(base_path, "data")
USERS_FILE = os.path.join(DATA_DIR, "users.csv")
ORDERS_FILE = os.path.join(DATA_DIR, "orders.csv")
INVENTORY_FILE = os.path.join(DATA_DIR, "inventory.csv")
CLOCKIN_FILE = os.path.join(DATA_DIR, "clockin.csv")
MENU_FILE = os.path.join(DATA_DIR, "menu_items.csv")
ATTEMPTS_FILE = os.path.join(DATA_DIR, "login_attempts.csv")
TABLES_FILE = os.path.join(DATA_DIR, "tables.csv")
ORDER_ITEMS_FILE = os.path.join(DATA_DIR, "order_items.csv")

os.makedirs(DATA_DIR, exist_ok=True)

def load_csv(file, columns):
    if os.path.exists(file):
        return pd.read_csv(file)
    return pd.DataFrame(columns=columns)

def save_csv(df, file):
    df.to_csv(file, index=False)

@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    users = load_csv(USERS_FILE, ["UserName", "Password", "Role"])
    attempts = load_csv(ATTEMPTS_FILE, ["username", "attempts"])

    if username in attempts["username"].values:
        attempt_row = attempts[attempts["username"] == username]
        if attempt_row.iloc[0]["attempts"] >= 3:
            return jsonify({"success": False, "message": "Account locked. Contact a manager to reset your login."}), 403

    match = users[(users["UserName"] == username) & (users["Password"] == password)]
    if not match.empty:
        attempts = attempts[attempts["username"] != username]
        save_csv(attempts, ATTEMPTS_FILE)
        return jsonify({"success": True, "username": username, "role": match.iloc[0]["Role"]})
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

    users = load_csv(USERS_FILE, ["UserName", "Password", "Role"])
    manager = users[(users["UserName"] == manager_user) & (users["Password"] == manager_pass) & (users["Role"].str.lower() == "manager")]

    if manager.empty:
        return jsonify({"success": False, "message": "Unauthorized reset attempt."}), 403

    attempts = load_csv(ATTEMPTS_FILE, ["username", "attempts"])
    attempts = attempts[attempts["username"] != target_user]
    save_csv(attempts, ATTEMPTS_FILE)
    return jsonify({"success": True, "message": f"Login attempts reset for {target_user}"})

@app.route("/api/tables", methods=["GET"])
def get_tables():
    tables = load_csv(TABLES_FILE, ["TableID", "Status", "WaiterID", "BusboyID"])
    return tables.to_dict(orient="records")

@app.route("/api/tables/update", methods=["POST"])
def update_table_status():
    data = request.json
    tables = load_csv(TABLES_FILE, ["TableID", "Status", "WaiterID", "BusboyID"])
    if data["TableID"] in tables["TableID"].values:
        tables.loc[tables["TableID"] == data["TableID"], "Status"] = data["Status"]
        save_csv(tables, TABLES_FILE)
        return jsonify({"success": True})
    return jsonify({"success": False, "message": "Table not found"}), 404

@app.route("/api/menu", methods=["GET"])
def get_full_menu():
    menu = load_csv(MENU_FILE, ["ItemID", "Name", "Category", "Price", "Stock"])
    return menu.to_dict(orient="records")

@app.route("/api/menu/<category>", methods=["GET"])
def get_menu_by_category(category):
    menu = load_csv(MENU_FILE, ["ItemID", "Name", "Category", "Price", "Stock"])
    items = menu[menu["Category"].str.lower() == category.lower()]
    return items.to_dict(orient="records")

@app.route("/api/order-items", methods=["POST"])
def add_order_item():
    data = request.json
    order_items = load_csv(ORDER_ITEMS_FILE, ["OrderID", "ItemID", "Quantity", "Customization"])
    order_items = pd.concat([order_items, pd.DataFrame([data])], ignore_index=True)
    save_csv(order_items, ORDER_ITEMS_FILE)
    return jsonify({"success": True})

@app.route("/api/orders/finalize", methods=["POST"])
def finalize_order():
    data = request.json
    order_id = data.get("OrderID")

    orders = load_csv(ORDERS_FILE, ["OrderID", "Status", "TimeStamp", "WaiterID", "TableID"])
    if order_id not in orders["OrderID"].values:
        new_row = {
            "OrderID": order_id,
            "Status": "Pending",
            "TimeStamp": datetime.now().isoformat(),
            "WaiterID": "EMP101",
            "TableID": "A1"
        }
        orders = pd.concat([orders, pd.DataFrame([new_row])], ignore_index=True)
        save_csv(orders, ORDERS_FILE)

    return jsonify({"success": True, "message": f"Order {order_id} finalized."})

@app.route("/api/order-items/clear", methods=["POST"])
def clear_order_items():
    data = request.json
    order_id = data.get("OrderID")
    order_items = load_csv(ORDER_ITEMS_FILE, ["OrderID", "ItemID", "Quantity", "Customization"])
    order_items = order_items[order_items["OrderID"] != order_id]
    save_csv(order_items, ORDER_ITEMS_FILE)
    return jsonify({"success": True, "message": f"Order {order_id} cleared."})

@app.route("/api/order-items", methods=["GET"])
def get_order_items():
    order_id = request.args.get("order_id")
    order_items = load_csv(ORDER_ITEMS_FILE, ["OrderID", "ItemID", "Quantity", "Customization"])
    filtered = order_items[order_items["OrderID"] == order_id]
    filtered = filtered.fillna("")
    return filtered.to_dict(orient="records")

@app.route("/api/orders/new-id", methods=["GET"])
def get_next_order_id():
    orders = load_csv(ORDERS_FILE, ["OrderID", "Status", "TimeStamp", "WaiterID", "TableID"])

    def extract_number(oid):
        try:
            return int(oid.replace("ORD", ""))
        except:
            return 0

    if not orders.empty:
        used_ids = orders["OrderID"].dropna().apply(extract_number)
        max_id = used_ids.max()
    else:
        max_id = 0

    next_id = f"ORD{str(max_id + 1).zfill(3)}"
    return jsonify({"OrderID": next_id})






@app.route("/api/inventory", methods=["GET"])
def get_inventory():
    inventory = load_csv(INVENTORY_FILE, ["InventoryID", "ItemName", "Category", "CurrentStock", "TimesOrdered"])
    return jsonify(inventory.to_dict(orient="records"))

@app.route("/api/inventory/order", methods=["POST"])
def order_inventory_item():
    data = request.json
    item_name = data.get("ItemName", "").strip().lower()
    inventory = load_csv(INVENTORY_FILE, ["InventoryID", "ItemName", "Category", "CurrentStock", "TimesOrdered"])
    inventory["ItemName_normalized"] = inventory["ItemName"].str.strip().str.lower()
    match = inventory[inventory["ItemName_normalized"] == item_name]

    if match.empty:
        return jsonify({"success": False, "message": f"Item '{item_name}' not found in inventory."}), 404

    index = match.index[0]
    inventory.at[index, "CurrentStock"] += 1
    inventory.at[index, "TimesOrdered"] += 1

    inventory = inventory.drop(columns=["ItemName_normalized"])
    save_csv(inventory, INVENTORY_FILE)

    return jsonify({"success": True, "message": f"{inventory.at[index, 'ItemName']} updated in inventory."})

@app.route("/api/manager/employees", methods=["GET"])
def manager_get_employees():
    users = load_csv(USERS_FILE, ["UserName", "Password", "EmployeeID", "Role", "Clock_In_Time", "Clock_Out_Time"])
    users = users.astype(object).where(pd.notnull(users), None)
    return jsonify(users.to_dict(orient="records"))

@app.route("/api/manager/employees", methods=["POST"])
def manager_add_employee():
    data = request.json
    users = load_csv(USERS_FILE, ["UserName", "Password", "EmployeeID", "Role", "Clock_In_Time", "Clock_Out_Time"])
    if data["UserName"] in users["UserName"].values:
        return jsonify({"success": False, "message": "Username already exists."}), 409

    new_user = pd.DataFrame([{
        "UserName": data["UserName"],
        "Password": data["Password"],
        "EmployeeID": data["EmployeeID"],
        "Role": data["Role"],
        "Clock_In_Time": "",
        "Clock_Out_Time": ""
    }])
    users = pd.concat([users, new_user], ignore_index=True)
    save_csv(users, USERS_FILE)
    return jsonify({"success": True})

@app.route("/api/manager/employees/update", methods=["POST"])
def manager_update_employee():
    data = request.json
    users = load_csv(USERS_FILE, ["UserName", "Password", "EmployeeID", "Role", "Clock_In_Time", "Clock_Out_Time"])
    match = users[users["EmployeeID"] == data["EmployeeID"]]
    if match.empty:
        return jsonify({"success": False, "message": "Employee ID not found."}), 404

    idx = match.index[0]
    for field in ["UserName", "Password", "Role", "EmployeeID"]:
        if field in data:
            users.at[idx, field] = data[field]
    save_csv(users, USERS_FILE)
    return jsonify({"success": True, "message": "User updated successfully."})

@app.route("/api/manager/employees/delete", methods=["POST"])
def manager_delete_employee():
    data = request.json
    users = load_csv(USERS_FILE, ["UserName", "Password", "EmployeeID", "Role", "Clock_In_Time", "Clock_Out_Time"])
    if data["UserName"] not in users["UserName"].values:
        return jsonify({"success": False, "message": "User not found."}), 404
    users = users[users["UserName"] != data["UserName"]]
    save_csv(users, USERS_FILE)
    return jsonify({"success": True, "message": "User removed successfully."})

def open_browser():
    file_path = os.path.abspath("frontend/views/L1.UsernamePassword.html")
    webbrowser.open(f"file:///{file_path}")

if __name__ == "__main__":
    Timer(1, open_browser).start()
    app.run(debug=True)
