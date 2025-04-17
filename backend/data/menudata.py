# Pre-fill menu_items.csv using data extracted from the menu
menu_items_data = [
    # Appetizers
    ("Chicken Nachos", "Appetizer", 8.50, 100),
    ("Pork Nachos", "Appetizer", 8.50, 100),
    ("Pork or Chicken Sliders", "Appetizer", 5.00, 100),
    ("Catfish Bites", "Appetizer", 6.50, 100),
    ("Fried Veggies", "Appetizer", 6.50, 100),

    # Salads
    ("House Salad", "Salad", 7.50, 100),
    ("Wedge Salad", "Salad", 7.50, 100),
    ("Caesar Salad", "Salad", 7.50, 100),
    ("Sweet Potato Chicken Salad", "Salad", 11.50, 100),

    # Entrees
    ("Shrimp & Grits", "Entree", 13.50, 100),
    ("Sweet Tea Fried Chicken", "Entree", 11.50, 100),
    ("Caribbean Chicken", "Entree", 11.50, 100),
    ("Grilled Pork Chops", "Entree", 11.00, 100),
    ("New York Strip Steak", "Entree", 17.00, 100),
    ("Seared Tuna", "Entree", 15.00, 100),
    ("Captain Crunch Chicken Tenders", "Entree", 11.50, 100),
    ("Shock Top Grouper Fingers", "Entree", 11.50, 100),
    ("Mac & Cheese Bar", "Entree", 8.50, 100),

    # Sides
    ("Curly Fries", "Side", 2.50, 200),
    ("Wing Chips", "Side", 2.50, 200),
    ("Sweet Potato Fries", "Side", 2.50, 200),
    ("Creamy Cabbage Slaw", "Side", 2.50, 200),
    ("Adluh Cheese Grits", "Side", 2.50, 200),
    ("Mashed Potatoes", "Side", 2.50, 200),
    ("Mac & Cheese", "Side", 2.50, 200),
    ("Seasonal Vegetables", "Side", 2.50, 200),
    ("Baked Beans", "Side", 2.50, 200),

    # Sandwiches
    ("Grilled Cheese", "Sandwich", 5.50, 100),
    ("Chicken BLT&A", "Sandwich", 10.00, 100),
    ("Philly", "Sandwich", 13.50, 100),
    ("Club", "Sandwich", 10.00, 100),
    ("Meatball Sub", "Sandwich", 10.00, 100),

    # Burgers
    ("Bacon Cheeseburger", "Burger", 11.00, 100),
    ("Carolina Burger", "Burger", 11.00, 100),
    ("Portobello Burger (V)", "Burger", 8.50, 100),
    ("Vegan Boca Burger (V)", "Burger", 10.50, 100),

    # Beverages
    ("Sweet Tea", "Beverage", 2.00, 300),
    ("Unsweetened Tea", "Beverage", 2.00, 300),
    ("Coke", "Beverage", 2.00, 300),
    ("Diet Coke", "Beverage", 2.00, 300),
    ("Sprite", "Beverage", 2.00, 300),
    ("Bottled Water", "Beverage", 2.00, 300),
    ("Lemonade", "Beverage", 2.00, 300),
    ("Orange Juice", "Beverage", 2.00, 300),
]

# Convert to DataFrame and add ItemID
menu_df = pd.DataFrame(menu_items_data, columns=["Name", "Category", "Price", "Stock"])
menu_df.insert(0, "ItemID", range(1, len(menu_df) + 1))

# Save the updated menu_items.csv
menu_csv_path = "menu_items.csv"
menu_df.to_csv(menu_csv_path, index=False)

import ace_tools as tools; tools.display_dataframe_to_user(name="Menu Items", dataframe=menu_df)
