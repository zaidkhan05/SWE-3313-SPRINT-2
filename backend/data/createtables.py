import pandas as pd
import os

# Folder where CSVs will be saved
base_path = ""
os.makedirs(base_path, exist_ok=True)

# Define all CSVs with their structure
csv_data = {
    "users.csv": ["UserName", "Password", "EmployeeID", "Role", "Clock_In_Time", "Clock_Out_Time"],
    "employees.csv": ["EmployeeID", "Name", "JobTitle", "PermissionLevel"],
    "waiters.csv": ["WaiterID", "EmployeeID", "AssignedSection"],
    "chefs.csv": ["ChefID", "EmployeeID", "Specialization"],
    "busboys.csv": ["BusboyID", "EmployeeID"],
    "managers.csv": ["ManagerID", "EmployeeID"],
    "tables.csv": ["TableID", "WaiterID", "BusboyID", "Status"],
    "menu_items.csv": ["ItemID", "Name", "Category", "Price", "Stock"],
    "orders.csv": ["OrderID", "Status", "TimeStamp", "WaiterID", "TableID"],
    "order_items.csv": ["OrderID", "ItemID", "Quantity", "Customization"],
    "payments.csv": ["PaymentID", "OrderID", "PaymentMethod", "Status"],
    "inventory.csv": ["InventoryID", "LastRestockDate", "ReorderLevel", "Name", "Quantity", "Supplier"],
    "inventory_menu_items.csv": ["InventoryID", "ItemID", "QuantityUsed"],
    "reports.csv": ["ReportID", "Type", "Date", "ManagerID", "Date_Generated"]
}

# Create and save all the CSVs with only header rows
created_files = []
for filename, columns in csv_data.items():
    df = pd.DataFrame(columns=columns)
    filepath = os.path.join(base_path, filename)
    df.to_csv(filepath, index=False)
    created_files.append(filepath)

created_files
