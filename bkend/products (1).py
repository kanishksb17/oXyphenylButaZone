import sqlite3

# Connect to database (creates if not exists)
conn = sqlite3.connect('eco_finds.db')
cursor = conn.cursor()

# Create table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY,
    title TEXT,
    category TEXT,
    price REAL,
    image TEXT
)
""")

# Insert full dataset (20 products)
full_products = [
    (1, 'Leather Jacket', 'Clothes', 120.0, 'placeholder.jpg'),
    (2, 'Old Textbooks', 'Books', 30.0, 'placeholder.jpg'),
    (3, 'Wireless Earbuds', 'Electronics', 50.0, 'placeholder.jpg'),
    (4, 'Wooden Chair', 'Furniture', 80.0, 'placeholder.jpg'),
    (5, 'Yoga Mat', 'Sports Equipment', 20.0, 'placeholder.jpg'),
    (6, 'Sunglasses', 'Accessories', 25.0, 'placeholder.jpg'),
    (7, 'Face Cream', 'Beauty & Personal Care', 15.0, 'placeholder.jpg'),
    (8, 'Board Game', 'Toys & Games', 40.0, 'placeholder.jpg'),
    (9, 'Cooking Pan', 'Kitchenware', 35.0, 'placeholder.jpg'),
    (10, 'Cushion Cover', 'Home Decor', 10.0, 'placeholder.jpg'),
    (11, 'Jeans', 'Clothes', 50.0, 'placeholder.jpg'),
    (12, 'Laptop', 'Electronics', 450.0, 'placeholder.jpg'),
    (13, 'Office Desk', 'Furniture', 120.0, 'placeholder.jpg'),
    (14, 'Running Shoes', 'Sports Equipment', 60.0, 'placeholder.jpg'),
    (15, 'Necklace', 'Accessories', 40.0, 'placeholder.jpg'),
    (16, 'Shampoo', 'Beauty & Personal Care', 12.0, 'placeholder.jpg'),
    (17, 'Puzzle', 'Toys & Games', 18.0, 'placeholder.jpg'),
    (18, 'Blender', 'Kitchenware', 55.0, 'placeholder.jpg'),
    (19, 'Wall Art', 'Home Decor', 25.0, 'placeholder.jpg'),
    (20, 'T-shirt', 'Clothes', 20.0, 'placeholder.jpg')
]

# Check if table is empty before inserting
cursor.execute("SELECT COUNT(*) FROM products")
if cursor.fetchone()[0] == 0:
    cursor.executemany("INSERT INTO products VALUES (?, ?, ?, ?, ?)", full_products)

conn.commit()
conn.close()
